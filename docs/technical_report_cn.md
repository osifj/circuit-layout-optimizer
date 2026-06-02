# 电路布局优化平台 — 技术报告

## 1. 摘要

本报告描述了一个面向 IC CAD Physical Design 的 Placement Optimization 原型系统。系统使用 Python 实现，读入电路模块和连线信息（JSON 格式），使用模拟退火（Simulated Annealing）算法在二维芯片平面上搜索较优的模块布局方案，以 HPWL（Half-Perimeter Wirelength）为核心线长指标，结合重叠、边界、密度和拥塞估计构成多目标成本函数。系统提供 CLI 命令行和 Streamlit Web 双界面，输出优化后的模块坐标、布局对比图、收敛曲线、拥塞热力图和完整的评价指标体系。

---

## 2. 背景介绍

集成电路设计流程通常分为逻辑设计（Logic Design）和物理设计（Physical Design）两大阶段。物理设计的核心任务之一是将逻辑综合产生的网表（netlist）转化为芯片上的物理版图（layout）。

布局（Placement）是物理设计的第一步：在芯片二维平面上为所有电路模块分配坐标。布局的质量直接决定后续布线（Routing）的可行性和芯片的最终性能。一个不好的布局会导致：
- 连线过长，信号延迟增大
- 局部拥塞过高，布线失败
- 面积利用率低，芯片成本上升

工业界 EDA 工具（如 Synopsys IC Compiler II、Cadence Innovus）的 Placement 引擎极其复杂，通常包含 Global Placement（分析性方法）→ Legalization → Detailed Placement 三个阶段，处理百万级标准单元。学术界开源项目 OpenROAD 也实现了完整的 Placement flow。

本项目的定位是 **原型系统**（prototype），目标不是达到工业级规模和精度，而是完整展示 Placement 优化的核心建模、算法实现和平台化流程。

---

## 3. 相关概念

### 3.1 IC CAD

IC CAD（Integrated Circuit Computer-Aided Design）即集成电路计算机辅助设计，俗称 EDA（Electronic Design Automation）。包括从 RTL 设计、逻辑综合、物理设计到签核（signoff）的全流程工具链。

### 3.2 Physical Design

物理设计是将逻辑网表转化为物理版图的过程，主要步骤：
1. **Floorplanning**：确定宏观模块（macro）的大致位置
2. **Placement**：为所有模块分配精确坐标
3. **CTS（Clock Tree Synthesis）**：构建时钟树
4. **Routing**：完成所有连线
5. **Signoff**：时序、功耗、DRC 验证

### 3.3 Placement

Placement 是物理设计中最关键也最耗时的步骤之一。其核心挑战在于：
- 模块数量大（百万级标准单元）
- 约束复杂（不重叠、边界、时序、拥塞）
- 目标多维（线长、时序、功耗、可布线性）

### 3.4 HPWL（Half-Perimeter Wirelength）

HPWL 是 EDA Placement 研究中最广泛使用的线长估计指标。对于包含 n 个 pin 的 net：

```
HPWL = (max(x_i) - min(x_i)) + (max(y_i) - min(y_i))
```

即所有 pin 的 bounding box 半周长。HPWL 的优点：
- 计算复杂度 O(n)，远优于 pairwise O(n²)
- 是 Steiner 树线长的紧致下界
- ISPD、ICCAD 等 Placement benchmark 的标准指标

### 3.5 Congestion（拥塞）

拥塞衡量芯片各区域的布线密度。即使总 HPWL 小，如果所有连线集中在同一区域，布线器（Router）仍无法完成走线。拥塞估计通常使用网格法：将芯片划分为均匀网格，统计每个格点经过的连线数量。

### 3.6 Fixed Constraints（固定约束）

在真实设计中，部分模块的位置是预先确定的：
- **IO Pad**：固定在芯片边缘
- **Hard Macro**：第三方 IP 核（如 PLL、ADC）可能要求特定位置
- **Pre-placed SRAM**：由 floorplan 阶段确定

优化算法必须尊重这些固定约束，不改变固定模块的坐标。

---

## 4. 系统设计

### 4.1 总体架构

```
输入层（parser.py）
    ↓
数据层（layout.py）
    ↓
成本层（cost.py） ← 多目标 cost function
    ↓
优化层（optimizer.py） ← Simulated Annealing
    ↓
输出层（metrics.py + visualize.py）
    ↓
界面层（main.py CLI + app.py Web）
```

### 4.2 模块职责

| 模块 | 职责 |
|------|------|
| `parser.py` | JSON 输入解析、格式验证、新旧 net 格式兼容 |
| `layout.py` | Module / Net / Layout 数据类，movable/fixed 模块管理 |
| `cost.py` | HPWL、overlap、boundary、density、congestion 计算 |
| `optimizer.py` | SA 算法，fixed 模块跳过，迭代历史记录 |
| `metrics.py` | 指标计算、打印、JSON 输出 |
| `visualize.py` | matplotlib 图表生成（布局图/对比图/收敛曲线/热力图） |
| `main.py` | CLI 入口，argparse 参数管理 |
| `app.py` | Streamlit Web 入口 |

---

## 5. 数据结构设计

### Module

```python
@dataclass
class Module:
    id: str           # 唯一标识
    width: float      # 宽度
    height: float     # 高度
    x: float = 0.0    # 左下角 x（布局变量）
    y: float = 0.0    # 左下角 y（布局变量）
    module_type: str = "macro"    # macro | standard_cell
    fixed: bool = False           # 是否固定
```

### Net

```python
@dataclass
class Net:
    name: str             # 名称
    pins: List[str]       # 连接模块 ID 列表
    weight: float = 1.0   # 权重
```

### Layout

```python
@dataclass
class Layout:
    chip_width: float
    chip_height: float
    modules: List[Module]
    nets: List[Net]

    # 属性
    movable_modules: List[Module]  # 非 fixed
    fixed_modules: List[Module]    # fixed
    macros: List[Module]           # macro 类型
    standard_cells: List[Module]   # standard_cell 类型
```

---

## 6. Cost Function 设计

```
Total Cost = α × HPWL
           + β × Overlap Penalty
           + γ × Boundary Penalty
           + δ × Density Penalty
           + ε × Congestion Penalty
```

### 6.1 HPWL（α × HPWL）

默认使用 HPWL 作为线长指标。可切换到 pairwise wirelength（`--no-hpwl`）。

### 6.2 Overlap Penalty（β × 重叠面积）

计算所有模块对的矩形重叠面积之和。重叠面积越大惩罚越大，SA 优化过程中自然驱动模块分离开。

### 6.3 Boundary Penalty（γ × 超出距离）

计算模块超出芯片边界的距离。γ 设为高位（默认 100）确保模块始终在芯片内。

### 6.4 Density Penalty（δ × 集中度）

计算所有模块中心点 x/y 坐标的归一化方差。方差越小 → 模块越集中 → 惩罚越大。鼓励模块分散布局。

### 6.5 Congestion Penalty（ε × 最大拥塞）

将芯片划分为 G×G 网格。每条 net 的 L 形曼哈顿路径经过的格点计数 +1。最大拥塞值作为惩罚项。ε 控制拥塞在优化中的权重。

---

## 7. 模拟退火算法

### 7.1 算法描述

模拟退火（Simulated Annealing, SA）受物理退火过程启发，是一种随机全局优化算法。

**核心思想**：
- 高温时：接受劣解概率大 → 广泛探索
- 低温时：接受劣解概率小 → 精细收敛

**算法步骤**：
```
1. 随机初始化模块位置（只初始化 movable 模块）
2. T = T0（初始温度，默认 500）
3. for iter = 1 to max_iter:
   a. 随机选择一个 movable 模块
   b. 随机微调位置（步长 ∝ T/T0 × move_scale）
   c. 计算 ΔCost = Cost_new - Cost_current
   d. if ΔCost ≤ 0: 接受新布局
      else: 以概率 exp(-ΔCost/T) 接受
   e. 如果当前布局优于历史最优 → 更新最优
   f. T = T × cooling_rate（默认 0.995）
4. 返回历史最优布局
```

### 7.2 关键参数

| 参数 | 含义 | 默认值 | 建议范围 |
|------|------|--------|----------|
| T0 | 初始温度 | 500 | 300-1000 |
| cooling_rate | 降温系数 | 0.995 | 0.990-0.999 |
| max_iter | 最大迭代 | 2000 | 1000-10000 |
| move_scale | 移动步长比例 | 0.2 | 0.1-0.5 |

### 7.3 选择 SA 的理由

1. **代价函数不可导**：Placement 的 cost function 无法求梯度，不能用梯度下降
2. **跳出局部最优**：概率接受劣解的机制天然适合非凸优化
3. **实现简单**：不需要复杂的数学模型
4. **学术界验证**：SA 是 Placement 研究中的经典 baseline（如 TimberWolf）

### 7.4 固定模块处理

SA 在每次扰动时只从 `movable_modules` 中选择模块，`fixed_modules` 坐标始终保持不变。

---

## 8. Web 平台设计

### 8.1 技术选型

**Streamlit**：Python 原生的 Web 框架，适合数据科学和算法 Demo 快速搭建。选择理由：
- 无需前端代码（HTML/JS/CSS）
- 可直接调用项目中已有的 Python 模块
- 丰富的交互组件（slider、file uploader、chart display）

### 8.2 界面布局

```
┌─ Sidebar ──────────┬─ Main Area ───────────────────┐
│ 📂 Input Selection  │ 📖 Project Intro (折叠)       │
│ 🔬 SA Parameters    │ 📂 Input Data Preview         │
│ 📐 Cost Weights     │   - 6 metric cards            │
│ 🚀 Run Button       │   - Modules table             │
│                     │   - Nets table                │
│                     │ 📊 Results                    │
│                     │   - Key metrics cards         │
│                     │   - Layout images             │
│                     │   - Cost curve                │
│                     │   - Congestion map            │
│                     │ 📥 Downloads                  │
│                     │   - result.json               │
│                     │   - metrics_summary.json      │
└─────────────────────┴───────────────────────────────┘
```

---

## 9. 实验结果

### 9.1 EDA Small（200×200, 15 模块）

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| HPWL | 3470.65 | 3115.97 | **-10.2%** |
| Total Cost | 3521.50 | 3217.34 | -8.6% |
| Max Congestion | 8 | 8 | 持平 |
| Avg Congestion | 1.67 | 1.60 | -4.2% |
| Overlap | 0 | 0 | ✅ 无 |

### 9.2 EDA Medium（300×300, 24 模块）

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| HPWL | 7326.02 | 6446.72 | **-12.0%** |
| Total Cost | 7386.64 | 6527.96 | -11.6% |
| Max Congestion | 11 | 11 | 持平 |
| Congested Cells | 19 | 16 | -15.8% |
| Avg Congestion | 2.79 | 2.63 | -5.7% |

### 9.3 分析

- HPWL 在两个测试用例上分别降低 10.2% 和 12.0%，验证了 SA 的有效性
- 重叠在足够迭代后趋于零，说明 SA 能够满足不重叠约束
- 拥塞最大值的改善有限（固定模块的 congestion 贡献不可优化），但拥塞格点数和平均拥塞均有下降
- 面积利用率低（~8%）是测试用例的特征（模块总面积远小于芯片面积），实际芯片中会更高

---

## 10. 局限性

1. **规模限制**：SA 算法在数百模块以上收敛速度显著变慢。工业级 Placement 处理百万级单元，使用分析性方法
2. **简单路由模型**：L 形曼哈顿路径与实际 Global Router 差距大
3. **无时序感知**：未引入 timing-driven cost（slack-based weighting）
4. **无合法化**：Standard Cell 没有 row-based legalization
5. **JSON-only**：不支持 DEF/LEF/LIB/SDC 等工业格式
6. **单算法**：只实现了 SA，未做算法对比
7. **无并行化**：SA 是串行算法，未利用多核

---

## 11. 后续工作

### 短期
- **算法对比**：实现 Force-Directed Placement 和 Genetic Algorithm，比较收敛速度和结果质量
- **更大 benchmark**：50-100+ 模块的测试用例
- **Congestion-aware routing**：使用 FLUTE 或 Steiner Tree 近似代替 L 形路由

### 中期
- **Analytical Placement**：实现基于二次规划的全局布局（如 ePlace、RePlAce 的思路）
- **Legalization**：实现 Tetris 或 Abacus 合法化算法
- **DEF/LEF 支持**：解析工业标准格式

### 长期
- **OpenROAD 集成**：作为 OpenROAD flow 的一个 placement 实验模块
- **RL-based Placement**：使用强化学习做 macro placement（如 Google 的论文）
- **GNN-based Placement**：图神经网络预测 congestion / wirelength

---

## 12. 总结

本项目实现了一个完整的 Placement Optimization 原型系统，覆盖了从问题建模到算法实现到平台展示的全流程。系统以 HPWL 为核心线长指标，实现了多目标成本函数和模拟退火优化，支持 Macro / Standard Cell / Fixed IO 三种模块类型，提供 CLI 和 Streamlit Web 双界面。

项目展示了以下工程能力：
- IC CAD / EDA 领域概念的理解和落地
- 多目标优化问题的数学建模
- 模拟退火算法的实现
- Python 模块化系统设计
- Web 平台搭建（Streamlit）
- 可视化分析能力

虽然离工业级 EDA 工具有较大差距，但作为实习项目原型，完整展示了 Placement Optimization 的核心要素和工程实现思路。
