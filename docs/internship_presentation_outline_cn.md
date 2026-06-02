# 实习汇报 PPT 大纲（中文）

**汇报人**：王传捷  
**项目**：电路布局优化平台 — Circuit Layout Optimization Platform  
**汇报时长**：8-10 分钟

---

## Slide 1 — 封面

**标题**：电路布局优化平台 — EDA Placement Optimization 原型系统

**副标题**：北方集成电路芯片 CAD 实习生项目汇报

**内容**：
- 你的名字
- 实习单位和岗位
- 项目名称
- 日期

---

## Slide 2 — 项目背景：芯片设计中的布局问题

**要讲的内容**：
> "在芯片设计流程中，物理设计是关键阶段。其中布局（Placement）问题决定了芯片面积、性能、功耗。简单来说就是：给你几十上百个电路模块，你要把它们放在芯片上，让连线最短、不重叠、不拥塞。"

**放什么图**：
- IC 设计流程图（逻辑综合 → 物理设计 → 制造），高亮 Placement 阶段
- 或直接放项目中的布局对比图

**怎么说**：
> "布局之所以难，是因为这些目标是相互冲突的。连线短了可能模块会重叠，分散开了连线又长了。这就是 Placement Optimization 要解决的问题。"

---

## Slide 3 — 问题定义

**标题**：Placement Optimization — 数学建模

**内容**：

```
输入：芯片边界 (W,H) + N 个模块 + K 条连线
目标：为每个模块分配坐标 (x_i, y_i)，最小化：

Total Cost = α × HPWL     (连线总长)
           + β × Overlap   (重叠)
           + γ × Boundary  (边界)
           + δ × Density   (密度)
           + ε × Congestion(拥塞)
```

**放什么图**：
- 一个简单的布局示意图：3-4 个矩形在芯片内，连线标注

**怎么说**：
> "我把布局优化抽象成一个多目标优化问题。目标函数有 5 个分量：线长、重叠、边界、密度、拥塞。每个分量有独立权重，可以根据需求调整。"

---

## Slide 4 — 系统架构

**标题**：系统总体架构

**内容**：
```
输入 JSON → parser → layout → cost function
                                ↓
                          Simulated Annealing
                                ↓
                    可视化 ← metrics ← result.json
```

**模块说明**：
| 模块 | 职责 |
|------|------|
| parser.py | JSON 解析 |
| layout.py | 数据结构 |
| cost.py | Cost function |
| optimizer.py | SA 算法 |
| visualize.py | matplotlib 可视化 |
| app.py | Streamlit Web |

**怎么说**：
> "系统采用模块化设计，6 个核心模块各司其职。CLI 和 Web 共用同一套底层代码，不重复。"

---

## Slide 5 — HPWL 与多目标 Cost Function

**标题**：EDA 标准指标：HPWL

**内容**：
- **HPWL = Half-Perimeter Wirelength**
- 对每条 net，取所有 pin 的 bounding box 半周长
- 比 pairwise 曼哈顿更接近真实布线结果
- ISPD / ICCAD placement benchmark 标准

**对比**：
| 方法 | 2端 net | 多端 net | EDA 标准 |
|------|---------|----------|----------|
| Pairwise | |x1-x2|+|y1-y2| | O(pins²) | ❌ |
| HPWL | |x1-x2|+|y1-y2| | O(pins) | ✅ |

**怎么说**：
> "为什么用 HPWL 而不是简单曼哈顿距离？因为 EDA 行业都用 HPWL。对多端 net，HPWL 计算所有 pin 的 bounding box 半周长，更接近真实 Steiner 树路由。这也是 ISPD 和 ICCAD placement benchmark 的标准指标。"

---

## Slide 6 — 模拟退火算法

**标题**：优化算法 — Simulated Annealing

**内容**：
```
1. 随机初始化模块位置
2. T = T0（初始温度）
3. 循环：
   a. 随机选 movable 模块，微调位置
   b. ΔCost ≤ 0 → 接受
      ΔCost > 0 → 以概率 exp(-ΔCost/T) 接受
   c. T = T × 0.995（降温）
4. 输出最优布局
```

**放什么图**：
- Cost 收敛曲线（6 子图）

**为什么用 SA**：
- 实现简单，不需要梯度
- 能跳出局部最优（概率接受劣解）
- 学术界 Placement 研究常用基线

**怎么说**：
> "我选择模拟退火有几个原因。第一，布局问题的 cost function 不可导，不能用梯度下降。第二，SA 有概率接受劣解的机制，能跳出局部最优。第三，它是学术界 placement 研究的经典 baseline。"

---

## Slide 7 — EDA 专业增强

**标题**：接近真实 EDA 场景的功能

**内容**：
| 功能 | 实现 |
|------|------|
| Macro Placement | 大面积模块，SA 布局 |
| Standard Cell | 小模块，可视化区分 |
| Fixed IO Constraints | SA 跳过，不可移动 |
| Multi-Pin Nets | HPWL bounding box |
| Congestion Estimation | 10×10 网格 + 热力图 |

**怎么说**：
> "除了基本优化，我还加了几个贴近实际 EDA 场景的功能。Fixed IO 是真实设计中常见的——IO Pad 固定在芯片边缘，优化不能动。Congestion 估计也很重要，因为线长短不等于能布线成功，还得看拥塞。"

---

## Slide 8 — Web 平台演示

**标题**：Streamlit Web 交互平台

**放什么**：
- 截图或现场演示

**功能展示**：
1. 选择示例数据 → 预览表格
2. 调参（α/β/γ/δ/ε, iterations, temperature）
3. 运行 → 指标卡片实时更新
4. 4 种可视化图
5. 下载 result.json + metrics_summary.json

**怎么说**：
> "为了方便展示，我用 Streamlit 做了一个 Web 界面。可以选示例数据、调参数、一键运行，结果实时显示。这个可以在汇报时直接打开演示。"

---

## Slide 9 — 实验结果

**标题**：实验结果

**EDA Small (15 modules, 4 fixed IO)**：
| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| HPWL | 3470.65 | 3115.97 | **-10.2%** |
| Max Congestion | 8 | 7 | -12.5% |

**EDA Medium (24 modules, 6 fixed IO)**：
| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| HPWL | 7326.02 | 6446.72 | **-12.0%** |
| Congested Cells | 19 | 16 | -15.8% |

**放什么图**：
- 优化前后对比图（comparison.png）
- Cost 收敛曲线（cost_curve.png）
- 拥塞热力图（congestion_map.png）

**怎么说**：
> "两个测试用例分别有 15 和 24 个模块，包含 macro、standard cell、fixed IO 和多端 net。HPWL 分别降低了 10% 和 12%，拥塞也有改善。"

---

## Slide 10 — 总结与后续工作

**标题**：总结

**已完成**：
- ✅ Placement Optimization 原型平台
- ✅ HPWL + 多目标 cost function
- ✅ Macro / SC / Fixed IO 支持
- ✅ 拥塞估计 + 热力图
- ✅ CLI + Streamlit Web 双界面
- ✅ 完整汇报材料

**局限性**：
- 规模有限（SA 不适合大规模）
- 无时序感知
- 不支持 DEF/LEF 格式

**后续方向**：
- 算法对比（Force-Directed、GA）
- 更大规模 benchmark
- Analytical placement + legalization
- OpenROAD 集成 / 对比
- RL-based placement

**怎么说**：
> "总结一下，这个项目是一个 placement 原型系统，展示了从问题建模到算法实现到平台展示的完整流程。它的局限性主要是规模——SA 不适合大规模。后续如果要继续深入，可以考虑和分析性 placement 方法对比，或者和 OpenROAD 的结果做比较。"
