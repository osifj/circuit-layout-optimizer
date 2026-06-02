# 实习汇报提纲 — 电路布局优化平台

## 1. 项目背景

集成电路（IC）设计流程中，**物理设计（Physical Design）** 是将逻辑网表转化为芯片物理版图的关键阶段。其中 **布局（Placement）** 问题直接决定芯片面积、时序、功耗和可制造性，是 EDA 工具链的核心环节。

布局优化的本质是一个大规模组合优化问题：在二维芯片平面上为成百上千个电路模块（macro block / standard cell）分配坐标位置，同时最小化连线总长、避免模块重叠、满足边界和拥塞约束。

本项目实现了一个完整的电路布局优化原型平台，从数学建模到算法实现到可视化分析，覆盖 Placement 问题的核心要素。

---

## 2. 为什么布局优化是芯片 CAD 的关键问题

1. **连线长度（Wirelength）** 直接影响信号延迟和功耗。布局不合理 → 线太长 → 芯片性能下降。
2. **拥塞（Congestion）** 导致布线失败。即使连线总长短，如果所有线集中在某个区域，布线器（Router）无法完成走线。
3. **模块重叠（Overlap）** 违反设计规则。物理上两个模块不能占据同一块硅片面积。
4. **面积利用率（Area Utilization）** 影响芯片成本。布局越紧凑，芯片面积越小，成本越低。
5. **宏观模块固定约束（Fixed Macro / IO Pad）** 在真实设计中普遍存在（如 SRAM 固定位置、IO Pad 在芯片边缘），优化算法必须遵守。

---

## 3. 数学建模

### 问题定义

给定：
- 芯片边界 (W, H)
- N 个电路模块 {M_i}，每个模块有 (w_i, h_i)
- K 条连线（Net）{N_k}，每条连接多个模块

求：每个模块的坐标 (x_i, y_i)，使得目标函数最小。

### 约束条件
1. 模块在芯片内：0 ≤ x_i ≤ W-w_i, 0 ≤ y_i ≤ H-h_i
2. 模块不重叠：∀i≠j, M_i ∩ M_j = ∅
3. Fixed 模块坐标不可变

### 目标函数

```
Total Cost = α × HPWL
           + β × Overlap Penalty
           + γ × Boundary Penalty
           + δ × Density Penalty
           + ε × Congestion Penalty
```

---

## 4. 优化目标函数详解

### HPWL — Half-Perimeter Wirelength

EA 行业标准线长估计。对每条 net 取所有 pin 的 bounding box：

```
HPWL_net = (max_x - min_x) + (max_y - min_y)
```

相比 pairwise 曼哈顿距离，HPWL 更接近真实 Steiner 树布线结果，计算效率高，是 Placement 研究的标准指标。

### Overlap Penalty

重叠面积直接作为惩罚项，SA 会自然驱动模块分开。

### Boundary Penalty

超出芯片边界的距离惩罚，权重 γ 设为较高值（如 100）以确保模块始终在芯片内。

### Density Penalty

模块中心分布的方差过小时惩罚，防止所有模块挤在一个小区域。

### Congestion Penalty

网格拥塞估计：划分 10×10 或更细网格，用 L 形曼哈顿路由模拟每条 net 的走线，统计每格经过的 net 数。最大拥塞值作为惩罚项加入总成本。

---

## 5. 模拟退火优化算法

**Simulated Annealing (SA)** 是一种随机全局优化算法，模拟物理退火过程。

### 算法流程

```
1. 初始化模块位置（随机）
2. 初始温度 T = T0
3. for iter = 1 to max_iter:
   a. 随机选择一个 movable 模块
   b. 随机微调其位置（移动范围 ∝ T）
   c. 计算新 cost
   d. if Δcost ≤ 0: 接受
      else: 以概率 exp(-Δcost/T) 接受
   e. T = T × cooling_rate
4. 输出历史最优布局
```

### SA 对 Placement 问题的优势

- 跳出局部最优：升温接受劣解，降温逐步收敛
- 实现简单，不需要梯度信息（布局问题 cost 不可导）
- 效果稳定，学术界 Placement 研究中广泛使用

---

## 6. 实验结果

### 测试用例 1: EDA Small (200×200, 15 modules, 4 fixed IO, 8 nets)

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| HPWL | 3470.65 | 3115.97 | **-10.2%** |
| Max Congestion | 8 | 7 | **-12.5%** |
| Overlap | 0 | 3.99 | ⚠️ 轻微 |
| Avg Congestion | 1.67 | 1.57 | -6.0% |

### 测试用例 2: EDA Medium (300×300, 24 modules, 6 fixed IO, 15 nets)

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| HPWL | 7326.02 | 6446.72 | **-12.0%** |
| Max Congestion | 11 | 11 | 持平 |
| Congested Cells | 19 | 16 | **-15.8%** |
| Avg Congestion | 2.79 | 2.63 | -5.7% |

---

## 7. 技术亮点

1. **多目标优化建模**：HPWL、重叠、边界、密度、拥塞五维联合优化
2. **EDA 标准指标**：HPWL 替代简单曼哈顿距离，拥塞估计融入 cost function
3. **Fixed 模块支持**：IO Pad / Fixed Macro 约束，接近真实设计场景
4. **Macro + Standard Cell 混合放置**：两种模块类型区分渲染和分析
5. **多端 Net 支持**：兼容多端布线（如 clock tree）
6. **完整可视化**：布局图、对比图、收敛曲线、拥塞热力图
7. **可扩展架构**：模块化设计，cost function 可插拔

---

## 8. 后续扩展方向

### 短期（v1.2）
- Force-Directed Placement 算法对比
- 更大规模测试用例（100+ modules）
- 更多拥塞路由模型（如 Steiner Tree approximation）

### 中期（v2.0）
- Web 平台化（Streamlit / FastAPI）
- 交互式调参（α/β/γ/δ/ε 滑块）
- 与 EDA 开源工具对比（OpenROAD）

### 长期（研究级）
- Reinforcement Learning Placement (RL-based)
- Graph Neural Network Placement (GNN-based)
- 与 OpenROAD flow 集成
- Timing / Power / Area 联合优化
- 支持 DEF/LEF 格式输入输出

---

## 9. 与工业 EDA 的关系

本项目是一个**原型系统**，展示了 Placement 优化的核心概念和算法。在工业 EDA 工具（如 Synopsys IC Compiler、Cadence Innovus）或开源工具（如 OpenROAD）中，Placement 远比本项目复杂：

| 维度 | 本项目 | 工业 EDA |
|------|--------|----------|
| 规模 | 10-100 modules | 百万级 cells |
| 算法 | SA | Analytical + Legalization + Detailed |
| 指标 | HPWL + Congestion | HPWL + Timing + Power + Routability |
| 格式 | JSON | DEF/LEF/LIB/SDC |
| 约束 | Fixed IO | Complex floorplan constraints |

但本项目建立的**数学建模思路、cost function 设计、SA 优化流程**与工业 Placement 的核心思想一致，是理解 EDA Physical Design 的绝佳起点。
