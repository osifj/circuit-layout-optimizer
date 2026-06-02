# Circuit Layout Optimization Platform v1.2

**电路布局优化平台** — EDA Placement Optimization 原型系统

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28%2B-red)](https://streamlit.io/)

---

## Project Overview

A complete **Placement Optimization** prototype for IC CAD Physical Design. Reads circuit modules and netlists in JSON, optimizes 2D module placement using **Simulated Annealing** with a multi-objective cost function (HPWL + Overlap + Boundary + Density + Congestion), and provides full visualization and evaluation.

**Interfaces**: CLI (command line) + Streamlit Web platform

---

## Features

- [x] **HPWL** (Half-Perimeter Wirelength) — EDA industry standard wirelength metric
- [x] **Multi-objective cost function**: 5 tunable dimensions (α/β/γ/δ/ε)
- [x] **Macro / Standard Cell / Fixed IO** module types with visual distinction
- [x] **Multi-pin net** support (backward-compatible with 2-pin source/target format)
- [x] **Congestion estimation**: grid-based routing density analysis with heatmap
- [x] **Simulated Annealing** optimizer with fixed module constraints
- [x] **6-panel convergence plots**: Cost / HPWL / Overlap / Congestion / Density / Temperature
- [x] **Streamlit Web** platform: upload JSON, tune parameters, run, download results
- [x] **Complete documentation**: technical report, presentation outline, interview script, resume bullets

---

## 项目背景

在集成电路设计流程中，**Placement（布局）** 是 Physical Design 的第一步：将成百上千个电路模块放置到芯片二维平面上，在满足面积、不重叠、拥塞等约束的前提下，最小化连线总长。

本平台从数学建模 → 算法实现 → 可视化分析，完整覆盖 Placement 优化问题的核心要素。

---

## 为什么 HPWL 更接近 IC CAD Placement

**HPWL (Half-Perimeter Wirelength)** 是 IC Placement 研究中的标准线长指标：

```
HPWL_net = (max_x - min_x) + (max_y - min_y)
```

取一条 net 所有 pin 的 bounding box 半周长。相比 pairwise 曼哈顿距离：
- **更贴近真实布线**：实际 router 会在 bounding box 内完成 Steiner Tree 路由，HPWL 是该 tree 的紧致下界
- **计算高效**：O(pins) vs O(pins²)
- **业界标准**：所有 Placement benchmark (ISPD, ICCAD) 和工业工具都以 HPWL 为核心指标

---

## Macro Placement 是什么

**Macro**（宏模块）是大面积、功能完整的硬核模块，如 SRAM、CPU Core、DSP。Macro Placement 是 Floorplanning 的核心：
- 面积大（占芯片 10-50%）
- 位置自由度受限
- 对整体布局和拥塞影响巨大

## Standard Cell Placement 是什么

**Standard Cell**（标准单元）是面积小的基本逻辑单元（如 NAND、Flip-Flop）。Standard Cell Placement 通常是 Analytical Placement + Legalization：
- 数量多（万-百万级）
- 高度统一（Row-based）
- 需要 detail placement 做合法化

本项目在 prototype 层面将两种模块类型区分渲染和分析，理解其本质差异。

---

## Fixed IO / Fixed Macro 约束

真实设计中：
- **IO Pad**（输入输出引脚）固定在芯片边缘
- **Fixed Macro**（如第三方 IP 核）预先指定坐标
- 优化算法必须绕过固定模块，不改变其位置

本项目 SA optimizer 自动跳过 `fixed: true` 的模块，可视化中用特殊样式标注。

---

## Congestion Estimation 在 Physical Design 中的意义

**Congestion（拥塞）** 衡量芯片某个区域的布线密度。即使 HPWL 很小，如果所有连线都在同一个狭窄区域穿过，布线器（Router）也无法完成走线。

本项目用网格法估计拥塞：
1. 划分 G×G 网格
2. 每条 net 的 L 形曼哈顿路径经过的格点 +1
3. 统计最大/平均拥塞、拥塞格点数

拥塞估计被纳入 cost function（ε × Congestion Penalty），SA 会主动避免高拥塞区域。

---

## 与 OpenROAD / Commercial EDA 的关系

| 维度 | 本项目 | OpenROAD | Commercial EDA |
|------|--------|----------|----------------|
| **Phase** | Prototype | Open-source Production | Licensed Production |
| **Scale** | 10-100 modules | Million cells | 10M+ cells |
| **Algorithm** | Simulated Annealing | Analytical + Legalization | Multi-stage hybrid |
| **Metrics** | HPWL + Congestion | HPWL + Timing + Power | Full signoff |
| **Format** | JSON | DEF/LEF/LIB/SDC | Industry standard |
| **Use Case** | Learning / Prototyping | Research / Tapeout | Mass production |

本项目建立的建模思路和优化流程与工业 Placement 一致，是理解 EDA Physical Design 的绝佳入口。

---

## 当前局限性

1. **规模受限**：SA 算法在数百模块以上收敛变慢
2. **简单路由模型**：L 形曼哈顿 vs 实际 Steiner / Global Router
3. **无时序感知**：未引入 timing-driven placement
4. **无合法化**：Standard cell rows 未做 legalization
5. **JSON 格式**：不支持 DEF/LEF 工业格式
6. **单目标权重**：α/β/γ/δ/ε 需手动调节

---

## 优化目标函数

```
Total Cost = α × HPWL
           + β × Overlap Penalty
           + γ × Boundary Penalty
           + δ × Density Penalty
           + ε × Congestion Penalty
```

| 参数 | 含义 | 默认值 | 命令行 |
|------|------|--------|--------|
| α | HPWL 权重 | 1.0 | `--alpha` |
| β | 重叠惩罚 | 10.0 | `--beta` |
| γ | 边界惩罚 | 100.0 | `--gamma` |
| δ | 密度惩罚 | 5.0 | `--delta` |
| ε | 拥塞惩罚 | 1.0 | `--epsilon` |

---

## 模拟退火算法

```
1. 随机初始化 movable 模块位置
2. T = T0 (初始温度)
3. for each iteration:
   a. 随机选一个 movable 模块，微调位置
   b. 计算 Δcost
   c. Δcost ≤ 0 → 接受；否则以概率 exp(-Δcost/T) 接受
   d. T = T × cooling_rate
4. 输出最优布局
```

---

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行 EDA 小规模示例
python3 main.py --input data/example_eda_small.json \
  --iter 3000 --temp 800 --use-hpwl --epsilon 1.0

# 运行 EDA 中规模示例
python3 main.py --input data/example_eda_medium.json \
  --iter 5000 --temp 1000 --use-hpwl --epsilon 1.0 --grid-size 10

# 兼容旧格式
python3 main.py --input data/example_small.json
```

---

## 输入格式

### 模块（支持扩展字段）
```json
{
  "id": "CPU_CORE", "width": 40, "height": 35,
  "type": "macro",
  "fixed": false
}
```

### Net（兼容二端 + 多端）
```json
// 新格式 — 多端
{"name": "n_bus", "pins": ["CPU", "MEM", "IO1", "IO2"], "weight": 2.0}

// 旧格式 — 二端 (自动转换)
{"source": "A", "target": "B", "weight": 1.0}
```

---

## 输出文件

| 文件 | 内容 |
|------|------|
| `outputs/result.json` | 优化后模块坐标 + 全部指标 |
| `outputs/metrics_summary.json` | 优化前后指标对比汇总 |
| `outputs/initial_layout.png` | 随机初始布局 |
| `outputs/optimized_layout.png` | SA 优化后布局 |
| `outputs/comparison.png` | 前后并排对比 |
| `outputs/cost_curve.png` | 收敛曲线（6 子图，含 HPWL + Congestion） |
| `outputs/congestion_map.png` | 拥塞热力图 |

---

## 项目结构

```
circuit-layout-optimizer/
├── data/
│   ├── example_small.json           # 旧格式兼容
│   ├── example_medium.json          # 旧格式兼容
│   ├── example_eda_small.json       # EDA 格式 (macro+SC+fixed+multi-pin)
│   └── example_eda_medium.json      # EDA 格式 (大)
├── src/
│   ├── __init__.py
│   ├── parser.py                    # JSON 解析 (兼容新旧格式)
│   ├── layout.py                    # Module/Net/Layout 数据结构
│   ├── cost.py                      # HPWL + 多目标 cost function
│   ├── optimizer.py                 # SA 优化 (跳过 fixed 模块)
│   ├── visualize.py                 # 可视化 (macro/SC/fixed 区分)
│   └── metrics.py                   # EDA 指标计算和输出
├── docs/
│   ├── internship_report_outline.md # 实习汇报提纲
│   └── web_platform_guide.md        # Web 平台使用指南
├── outputs/                         # 输出目录
├── app.py                           # Streamlit Web 界面
├── main.py                          # CLI 主入口
├── requirements.txt
└── README.md
```

---

## Streamlit Web Platform

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动 Web 平台

```bash
cd circuit-layout-optimizer
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`。

### 页面功能

| 区域 | 功能 |
|------|------|
| **Sidebar** | 选择内置示例 或 上传自定义 JSON，调节 SA 参数和 cost weights |
| **Input Preview** | 显示 chip 尺寸、模块/Nets 数量统计、模块表格、Net 表格 |
| **Metrics Cards** | HPWL 降低%、Cost 降低%、Congestion 变化、Overlap 状态 |
| **Layout Viz** | 初始/优化布局并排，前后对比，收敛曲线（6 子图），拥塞热力图 |
| **Downloads** | 下载 `result.json` 和 `metrics_summary.json` |

### 上传自定义 JSON

在左侧 Sidebar 点击 "Upload your own JSON file"，上传符合格式的 `.json` 文件即可。支持：

- 旧格式: `{"source": "A", "target": "B", "weight": 1.0}`
- 新格式: `{"name": "net1", "pins": ["A","B","C"], "weight": 1.0}`
- 模块扩展: `type`, `fixed`, `x`, `y`

### 如何解释输出结果

1. **HPWL 降低 %** → 越高越好，表示布局优化后连线总长显著缩短
2. **Overlap = 0** → 无模块重叠，布局合法
3. **Max Congestion** → 越小越好，表示布线密度均匀
4. **Cost Curve** → 看 SA 收敛趋势（Cost 持续下降 → 算法有效）
5. **Congestion Map** → 红色区域是布线热点，需关注

---

## 技术栈

- Python 3.10+
- NumPy — 数值计算
- Matplotlib — 可视化
- Streamlit — Web 界面
- Pandas — 数据展示
- Simulated Annealing — 优化算法

---

## Example Results

### EDA Small (200×200, 15 modules, 4 fixed IO)

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| HPWL | 3470.65 | 3115.97 | **-10.2%** |
| Total Cost | 3521.50 | 3217.34 | -8.6% |
| Max Congestion | 8 | 7 | -12.5% |
| Overlap | 0 | 0 | ✅ |

### EDA Medium (300×300, 24 modules, 6 fixed IO)

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| HPWL | 7326.02 | 6446.72 | **-12.0%** |
| Total Cost | 7386.64 | 6527.96 | -11.6% |
| Congested Cells | 19 | 16 | -15.8% |
| Avg Congestion | 2.79 | 2.63 | -5.7% |

---

## Documentation

| Document | Description |
|----------|-------------|
| [Project Summary (CN)](docs/project_summary_cn.md) | 中文项目总结 |
| [Project Summary (EN)](docs/project_summary_en.md) | English project summary |
| [Presentation Outline (CN)](docs/internship_presentation_outline_cn.md) | 中文 PPT 大纲 (10 slides) |
| [Presentation Outline (EN)](docs/internship_presentation_outline_en.md) | English PPT outline |
| [Technical Report (CN)](docs/technical_report_cn.md) | 正式技术报告 |
| [Interview Script (CN)](docs/interview_explanation_cn.md) | 面试/答辩讲解稿 |
| [Resume Description (CN)](docs/resume_description_cn.md) | 中文简历描述 |
| [Resume Description (EN)](docs/resume_description_en.md) | English resume bullets |
| [Web Platform Guide](docs/web_platform_guide.md) | Web 平台使用指南 |

---

## Future Work

- [ ] Algorithm comparison: Force-Directed, Genetic Algorithm
- [ ] Larger benchmarks (50-100+ modules)
- [ ] Analytical Placement + Legalization
- [ ] DEF/LEF format support
- [ ] Timing-driven placement
- [ ] OpenROAD integration
- [ ] RL-based / GNN-based placement

---

## License

MIT
