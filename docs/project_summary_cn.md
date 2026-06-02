# 电路布局优化平台 — 项目总结

## 项目名称

**Circuit Layout Optimization Platform（电路布局优化平台）**

—— 面向 IC CAD Physical Design 的 Placement Optimization 原型系统

---

## 项目背景

在集成电路（IC）设计流程中，**物理设计（Physical Design）** 是将逻辑网表转化为芯片物理版图的关键阶段。其中 **布局（Placement）** 问题是 EDA 工具链的核心环节：在芯片二维平面上为电路模块分配坐标位置，同时最小化连线总长、避免模块重叠、满足边界约束和拥塞约束。

布局优化的质量直接影响芯片面积、时序、功耗和可制造性。工业界 EDA 工具（Synopsys IC Compiler、Cadence Innovus）和开源工具（OpenROAD）都投入了大量工程资源解决 Placement 问题。

本项目在 **北方集成电路芯片 CAD 实习** 期间开发，目标不是做工业级 EDA 工具，而是建立一个完整的 Placement Optimization 原型平台，展示对该领域核心概念、建模方法和算法实现的理解。

---

## 为什么电路布局优化是芯片 CAD / EDA 的核心问题

1. **连线长度（Wirelength）** 直接影响信号延迟和功耗。放置不当 → 连线过长 → 性能下降
2. **模块重叠（Overlap）** 在物理上不可行，两个模块不能占据同一块硅片面积
3. **拥塞（Congestion）** 导致布线失败。即使连线总长短，所有线集中在同一区域，布线器无法走通
4. **面积利用率（Utilization）** 影响芯片成本。布局越紧凑，芯片面积越小
5. **固定约束（Fixed Constraints）** 在真实设计中普遍存在，如 IO Pad 在芯片边缘、SRAM 位置预先指定

这些问题相互耦合，构成了 Placement 领域的核心挑战。

---

## 项目目标

开发一个用于电路模块布局优化的原型系统：

1. 支持输入电路模块、连接关系和布局约束（JSON 格式）
2. 使用模拟退火（Simulated Annealing）优化布局
3. 以 **HPWL（Half-Perimeter Wirelength）** 为 EDA 标准线长指标
4. 实现多目标成本函数：线长 + 重叠 + 边界 + 密度 + 拥塞
5. 支持 **Macro / Standard Cell / Fixed IO** 三种模块类型
6. 完整的可视化和评价指标输出
7. **CLI（命令行）+ Streamlit Web** 双界面

---

## 系统输入

### JSON 格式

```json
{
  "chip_width": 200,
  "chip_height": 200,
  "modules": [
    {"id": "CPU", "width": 40, "height": 35, "type": "macro"},
    {"id": "IO1", "width": 5, "height": 5, "type": "macro", "fixed": true, "x": 0, "y": 0},
    {"id": "U1", "width": 3, "height": 2, "type": "standard_cell"}
  ],
  "nets": [
    {"name": "net1", "pins": ["CPU", "IO1", "U1"], "weight": 2.0},
    {"source": "A", "target": "B", "weight": 1.0}
  ]
}
```

支持旧格式（source/target 二端 net）和新格式（pins 多端 net）兼容。

---

## 系统输出

| 输出文件 | 内容 |
|----------|------|
| `outputs/result.json` | 优化后模块坐标 + 全部评价指标 |
| `outputs/metrics_summary.json` | 优化前后指标对比汇总 |
| `outputs/initial_layout.png` | 随机初始布局图 |
| `outputs/optimized_layout.png` | SA 优化后布局图 |
| `outputs/comparison.png` | 优化前后并排对比 |
| `outputs/cost_curve.png` | 6 子图收敛曲线 |
| `outputs/congestion_map.png` | 布线拥塞热力图 |

---

## 算法流程

```
1. 解析 JSON 输入 → 构建 Module / Net / Layout 数据结构
2. 随机初始化 movable 模块坐标
3. 计算初始 Cost（HPWL + Overlap + Boundary + Density + Congestion）
4. 模拟退火迭代：
   a. 随机选择一个 movable 模块
   b. 微调其位置（步长 ∝ 当前温度）
   c. 计算新 Cost
   d. ΔCost ≤ 0 → 接受
      ΔCost > 0 → 以概率 exp(-ΔCost/T) 接受
   e. T = T × cooling_rate
5. 输出最优布局 + 完整可视化
```

## 核心技术点

### 1. HPWL（Half-Perimeter Wirelength）

EDA 行业标准线长估算。对每条 net 取所有 pin 的 bounding box：

```
HPWL_net = (max_x - min_x) + (max_y - min_y)
```

比 pairwise 曼哈顿距离更接近真实 Steiner 树布线结果。

### 2. 多目标 Cost Function

```
Total Cost = α × HPWL + β × Overlap + γ × Boundary + δ × Density + ε × Congestion
```

五个维度可独立调节权重，针对不同优化目标进行 trade-off。

### 3. Macro / Standard Cell 区分

- **Macro**：大面积模块（如 SRAM、CPU Core），布局自由度受限
- **Standard Cell**：小面积标准单元，可视化中缩小显示
- **Fixed IO**：固定位置模块，SA 跳过不移动

### 4. 拥塞估计

网格法：划分 G×G 网格 → 每条 net 的 L 形曼哈顿路由经过的格点计数 → 统计最大/平均拥塞 → 可视化热力图

### 5. Simulated Annealing

经典随机全局优化算法，在 Placement 研究中广泛使用。高温阶段探索全局空间，低温阶段精调局部最优。

---

## 当前实现功能

- [x] JSON 输入解析（兼容新旧 net 格式）
- [x] 多端 net 支持
- [x] Macro / Standard Cell / Fixed IO 模块类型
- [x] HPWL 计算（EDA 标准）
- [x] Pairwise Wirelength（对比参考）
- [x] 重叠惩罚
- [x] 边界惩罚
- [x] 密度惩罚
- [x] 网格拥塞估计 + 拥塞惩罚
- [x] 模拟退火优化（跳过 fixed 模块）
- [x] 6 子图收敛曲线（Cost/HPWL/Overlap/Congestion/Density/Temperature）
- [x] 拥塞热力图
- [x] CLI 命令行接口（参数可调）
- [x] Streamlit Web 平台（上传 JSON、调参、实时展示、下载结果）

---

## 实验结果

### EDA Small（200×200, 15 模块, 4 fixed IO, 8 nets）

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| HPWL | 3470.65 | 3115.97 | **-10.2%** |
| Max Congestion | 8 | 7 | -12.5% |
| Avg Congestion | 1.67 | 1.57 | -6.0% |

### EDA Medium（300×300, 24 模块, 6 fixed IO, 15 nets）

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| HPWL | 7326.02 | 6446.72 | **-12.0%** |
| Congested Cells | 19 | 16 | -15.8% |
| Avg Congestion | 2.79 | 2.63 | -5.7% |

---

## Web 平台展示功能

基于 Streamlit 的双栏交互界面：

- **左侧 Sidebar**：选择示例/上传 JSON、调节所有参数、一键运行
- **右侧主区域**：输入预览表格、指标卡片、4 种可视化图、JSON 下载

启动命令：`streamlit run app.py`

---

## 项目亮点

1. **从问题建模到完整实现**：Problem formulation → Data structure → Cost function → Algorithm → Visualization → Web platform，全链路覆盖
2. **EDA 专业概念落地**：HPWL、Congestion、Macro/SC、Fixed Constraints 均有实现和解释
3. **多目标联合优化**：5 维 cost function 可独立调节
4. **CLI + Web 双界面**：既能脚本调用，也能汇报展示
5. **代码结构清晰**：模块化设计，src/ 目录职责明确
6. **完整的汇报材料**：项目总结、技术报告、PPT 大纲、面试稿、简历描述

---

## 当前局限性

1. **规模受限**：SA 在数百模块以上收敛变慢，不适合大规模 benchmark
2. **简单路由模型**：L 形曼哈顿 vs 实际 Global Router
3. **无时序感知**：未引入 timing-driven cost
4. **无合法化**：Standard Cell 未做 row-based legalization
5. **JSON 格式**：不支持 DEF/LEF 工业格式
6. **单算法**：仅 SA，未对比 Force-Directed / Analytical / RL 等方法

---

## 后续优化方向

### 短期（v1.3）
- 算法对比：Force-Directed Placement、Genetic Algorithm
- 更大规模测试（50-100 modules）
- 更多指标：HPWL over Iteration、Wirelength Distribution

### 中期（v2.0）
- Analytical Placement + Legalization
- DEF/LEF 格式支持
- 与 OpenROAD 结果对比

### 长期
- Reinforcement Learning Placement
- Timing / Power-Aware Optimization
- 多芯片/3D IC 布局
