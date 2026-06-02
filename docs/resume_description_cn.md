# 简历项目描述（中文）

## 一句话概括

开发了一个电路布局优化原型平台，使用模拟退火算法实现芯片模块的自动化布局，支持 HPWL 线长估计、拥塞分析和 Streamlit Web 可视化。

---

## 3 条简历 Bullet Point

- 使用 **Python** 实现了**模拟退火（Simulated Annealing）** 算法，对电路模块布局进行多目标优化（HPWL 线长、重叠、边界、密度、拥塞），在测试用例上实现 HPWL 降低 10-12%
- 引入 **EDA 行业标准指标 HPWL**、网格拥塞估计、Macro/Standard Cell/Fixed IO 约束，使原型更接近真实 IC CAD Placement 场景
- 基于 **Streamlit** 构建交互式 Web 平台，支持 JSON 数据上传、参数实时调节、优化结果可视化展示和指标下载

---

## 5 条详细 Bullet Point

1. 独立设计并实现了**电路布局优化平台**，覆盖 IC CAD Physical Design 中 Placement 问题的完整流程：JSON 输入解析 → 数据结构建模 → 多目标成本函数 → 模拟退火优化 → 可视化分析
2. 实现了以 **HPWL（Half-Perimeter Wirelength）** 为核心线长指标的**五维成本函数**，各维度权重可独立调节，支持算法效果的 trade-off 分析
3. 支持 **Macro / Standard Cell / Fixed IO** 三种模块类型和**多端 Net** 格式，Fixed 模块在优化过程中位置保持不变，更贴近真实 Floorplanning 约束
4. 实现了基于网格法的**拥塞估计（Congestion Estimation）**，生成拥塞热力图并将拥塞值纳入成本函数，使优化结果考虑布线可行性
5. 构建了 **CLI 命令行 + Streamlit Web 双界面**，Web 平台支持文件上传、参数拖动调节、实时结果查看和 JSON 结果下载，适合技术展示和汇报

---

## 技术栈

Python · NumPy · Matplotlib · Streamlit · Simulated Annealing · HPWL · Congestion Estimation

---

## 可替换关键词版本

根据投递岗位可以替换关键词组合：

**偏 EDA 方向**：
> IC CAD · Physical Design · Placement Optimization · HPWL · Macro Placement · Standard Cell · Fixed Constraints · Congestion Estimation · Floorplanning

**偏 AI/算法方向**：
> Combinatorial Optimization · Simulated Annealing · Multi-objective Optimization · Cost Function Design · Heuristic Search · Convergence Analysis

**偏全栈/平台方向**：
> Python · Streamlit · Data Visualization · CLI Development · Modular Architecture · Interactive Dashboard
