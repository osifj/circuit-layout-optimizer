# 1 分钟面试版项目介绍

**使用场景**: 面试官问"你这个项目主要做了什么？"  

---

## 1 分钟版（134 字，约 60 秒）

> "我在 CAD 实习期间做了一个电路布局优化平台。这个问题对应 IC CAD 里的 Placement——就是给定一堆电路模块和连线关系，在芯片二维平面上给每个模块分配坐标，目标是连线最短、模块不重叠。
>
> 我用了 EDA 行业标准的 HPWL 作为线长指标，就是取所有 pin 的 bounding box 半周长，比简单曼哈顿距离更贴近真实布线。然后构建了五维成本函数——线长、重叠、边界、密度、还有拥塞估计——用模拟退火做全局优化。
>
> 还支持 Fixed IO 约束、Macro 和 Standard Cell 区分、多端 net，这些是真实 EDA floorplanning 里会遇到的场景。
>
> 最后用 Streamlit 搭了一个 Web 平台，可以直接上传 JSON、调参数、看结果。跟芯片 CAD 实习的关联就是——它覆盖了 Physical Design 里 Placement 问题的核心要素，从数学建模到算法实现到平台展示都自己做了一遍。"

---

## 30 秒版（如果时间紧）

> "我做了一个电路布局优化平台，用模拟退火算法在芯片上自动放置模块。用了 EDA 行业标准的 HPWL 指标做线长估计，加上重叠、边界、密度、拥塞五个维度做多目标优化。支持 Fixed IO 约束和多端 net。做了 CLI 和 Streamlit Web 双界面。HPWL 在测试用例上降低了 10-12%。"

---

## 关键词提醒

说的时候自然带出这些词：
- IC CAD / EDA
- Physical Design
- Placement Optimization
- HPWL（Half-Perimeter Wirelength）
- Simulated Annealing
- Multi-objective Cost Function
- Congestion Estimation
- Fixed Constraints
- Streamlit Web Platform
