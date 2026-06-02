# 北方集成电路芯片 CAD 实习 — 电路布局优化平台 汇报 PPT

**汇报人**: 王传捷  
**日期**: 2026 年 6 月  
**项目**: Circuit Layout Optimization Platform  

---

## Slide 1 — 项目背景

### IC CAD 中的布局优化问题

- 芯片设计流程：逻辑综合 → **物理设计（Physical Design）** → 制造
- **Placement（布局）** 是物理设计第一步，决定芯片面积、性能、功耗
- 核心挑战：在二维平面上放置电路模块，**连线最短、不重叠、不拥塞**
- 布局质量直接影响：信号延迟、功耗、芯片成本、布线可行性

**建议配图**: 芯片设计流程图（高亮 Placement 阶段），或直接放 `outputs/comparison.png`

**讲稿（30 秒）**:
> "芯片物理设计中，Placement 布局是最关键的一步。我们需要把电路模块放在芯片上，目标是连线最短、不重叠。布局好坏直接决定芯片面积、性能和功耗。这就是我要解决的问题。"

---

## Slide 2 — 项目目标

### 电路布局优化平台做什么

- **输入**: JSON 格式的电路模块 + 连线信息（支持 Macro / Standard Cell / Fixed IO）
- **优化**: 使用 Simulated Annealing 搜索最优布局
- **指标**: HPWL（半周长线长）+ Overlap + Boundary + Density + Congestion
- **输出**: 布局对比图、收敛曲线、拥塞热力图、完整指标
- **界面**: CLI 命令行 + **Streamlit Web 交互平台**

**建议配图**: 平台架构图（输入 → 优化 → 输出）

**讲稿（25 秒）**:
> "我的项目是一个布局优化原型平台。输入是电路模块和连线信息，用模拟退火做优化，以 HPWL 为核心线长指标，输出布局图和评价指标。做了命令行和 Web 两个界面。"

---

## Slide 3 — 系统架构

### 模块化设计：6 个核心模块

```
parser.py → layout.py → cost.py → optimizer.py → visualize.py + metrics.py
```

| 模块 | 职责 |
|------|------|
| `parser.py` | JSON 解析 |
| `layout.py` | Module / Net / Layout 数据结构 |
| `cost.py` | 多目标成本函数 |
| `optimizer.py` | 模拟退火算法 |
| `visualize.py` | 可视化 |
| `metrics.py` | 指标计算 |

**CLI + Web 共用同一套后端，零代码重复**

**建议配图**: 架构图 + 代码结构树

**讲稿（30 秒）**:
> "系统是模块化设计，6 个核心模块分工明确。parser 负责读取 JSON，layout 管数据结构，cost 计算目标函数，optimizer 跑模拟退火，最后 visualize 和 metrics 输出结果。CLI 和 Web 共用同一套后端。"

---

## Slide 4 — 输入数据建模

### Module 类型 + Net 格式

**三种模块类型**:
- **Macro** — 大面积硬核模块（SRAM、CPU Core）
- **Standard Cell** — 小面积标准单元（NAND、Flip-Flop）
- **Fixed IO** — 固定位置模块（芯片边缘 IO Pad）

**Net 支持**:
- 二端 net: `{"source": "A", "target": "B"}`
- 多端 net: `{"pins": ["CPU", "MEM", "IO1"]}`

**建议配图**: `outputs/initial_layout.png`（可以看到 Macro 大矩形 + SC 小矩形 + Fixed IO 在角落）

**讲稿（30 秒）**:
> "输入支持三种模块类型：Macro 是大面积模块，Standard Cell 是小的标准单元，Fixed IO 固定在芯片边缘不动。Net 支持二端和多端格式兼容。这个设计参考了真实 EDA 的 floorplanning 场景。"

---

## Slide 5 — 优化目标函数

### 多目标 Cost Function

```
Total Cost = α × HPWL       ← 连线总长（EDA 标准指标）
           + β × Overlap     ← 模块重叠惩罚
           + γ × Boundary    ← 超出芯片边界
           + δ × Density     ← 模块集中度
           + ε × Congestion  ← 布线拥塞
```

**为什么用 HPWL？**
- EDA 行业标准线长指标（ISPD、ICCAD benchmark）
- 取所有 pin 的 bounding box 半周长
- 比 pairwise 曼哈顿更接近真实 Steiner 树布线
- 计算效率 O(pins) vs O(pins²)

**建议配图**: HPWL 示意图（3-4 个 pin 的 bounding box）

**讲稿（35 秒）**:
> "Cost function 有五个维度。最核心的是 HPWL，这是 EDA placement 的标准指标——取所有 pin 的 bounding box 半周长，比曼哈顿距离更贴近真实布线。其余四个维度惩罚重叠、越界、集中和拥塞。每个权重都可以独立调。"

---

## Slide 6 — 优化算法

### Simulated Annealing（模拟退火）

```
1. 随机初始化 movable 模块位置
2. T = 500（初始温度）
3. 迭代：
   a. 随机选 movable 模块，微调位置
   b. ΔCost ≤ 0 → 接受
      ΔCost > 0 → 以概率 exp(-ΔCost/T) 接受
   c. T = T × 0.995（降温）
4. 输出最优布局
```

**为什么 SA？**
- Cost function 不可导 → 不能用梯度下降
- 概率接受劣解 → 跳出局部最优
- Placement 研究经典 baseline

**建议配图**: `outputs/cost_curve.png`（6 子图收敛曲线）

**讲稿（30 秒）**:
> "我选模拟退火有三个原因。一，布局的 cost 不可导，不能用梯度方法。二，SA 能通过概率接受劣解跳出局部最优。三，它是 placement 研究的经典 baseline。Fixed 模块在优化中不会被移动。"

---

## Slide 7 — 实验结果

### 两个测试用例的结果

**EDA Small (15 模块, 4 Fixed IO)**:
| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| HPWL | 3470.65 | 3115.97 | **-10.2%** |
| Max Congestion | 8 | 7 | -12.5% |
| Overlap | 0 | 0 | ✅ |

**EDA Medium (24 模块, 6 Fixed IO)**:
| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| HPWL | 7326.02 | 6446.72 | **-12.0%** |
| Congested Cells | 19 | 16 | -15.8% |

**建议配图**: `outputs/comparison.png`（优化前后对比）+ `outputs/congestion_map.png`

**讲稿（35 秒）**:
> "两个测试用例分别有 15 和 24 个模块，包含 Macro、Standard Cell 和 Fixed IO。HPWL 分别降低 10% 和 12%，证明 SA 有效。拥塞从热力图可以看到，红色热点区域在优化后有所改善。"

---

## Slide 8 — Web 平台展示

### Streamlit 交互界面

**功能**:
- 📂 选择内置示例 或 上传自定义 JSON
- 🔬 拖动滑块调节所有参数（α/β/γ/δ/ε, 迭代数, 温度）
- 🚀 一键运行优化，实时展示结果
- 📊 指标卡片 + 布局对比 + 收敛曲线 + 拥塞热力图
- 📥 下载 result.json + metrics_summary.json

**启动**: `streamlit run app.py`

**建议配图**: Web 界面截图（或现场演示）

**讲稿（25 秒）**:
> "为了方便展示，我用 Streamlit 做了 Web 界面。可以选示例数据、调参数、一键运行。结果实时显示，包括指标卡片、布局图、收敛曲线和拥塞热力图。也可以下载结果 JSON。"

---

## Slide 9 — 项目亮点与 EDA 关联

### 这个项目和 IC CAD 的关系

**对应的 EDA 概念**:
| 本平台功能 | EDA 对应概念 |
|------------|-------------|
| 模块布局优化 | **Placement** |
| 宏观模块放置 | **Floorplanning / Macro Placement** |
| HPWL 线长 | **Wirelength Optimization** |
| 固定模块约束 | **Fixed Constraints / IO Pad** |
| 拥塞估计 | **Congestion Estimation** |
| 标准单元放置 | **Standard Cell Placement** |

**技术亮点**:
- 从问题建模到平台展示，完整覆盖 Placement 核心要素
- HPWL 采用 EDA 行业标准指标，非简单曼哈顿距离
- 拥塞估计融入优化目标，考虑布线可行性
- CLI + Web 双界面，兼具工程实用性和展示性

**建议配图**: EDA 流程图 + 本平台覆盖的阶段高亮

**讲稿（30 秒）**:
> "这个项目直接对应 IC CAD 里的 Physical Design 和 Placement。HPWL 是 EDA 标准指标，固定约束对应 IO Pad 设计，拥塞估计对应 routability 分析。虽然规模有限，但核心概念和流程和工业 EDA 是一致的。"

---

## Slide 10 — 总结与后续计划

### 已完成 ✅

- ✅ Placement 优化原型平台
- ✅ HPWL + 多目标 cost function
- ✅ Macro / SC / Fixed IO
- ✅ 拥塞估计 + 热力图
- ✅ CLI + Streamlit Web
- ✅ 完整技术文档

### 后续方向 🚀

| 短期 | 中期 | 长期 |
|------|------|------|
| Force-Directed 对比 | Analytical Placement | RL Placement |
| Genetic Algorithm | DEF/LEF 支持 | GNN Placement |
| 更大 benchmark | OpenROAD 集成 | 3D IC |

**建议配图**: roadmap 时间线

**讲稿（30 秒）**:
> "总结一下，这个项目完整展示了 Placement 优化的核心流程。主要局限是规模，SA 不适合大规模设计。后续如果要深入，可以做算法对比、分析性 placement，甚至跟 OpenROAD 对齐。这是我作为 CAD 实习生阶段的项目成果，谢谢。"
