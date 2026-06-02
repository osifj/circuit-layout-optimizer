# 面试/答辩讲解稿 — 电路布局优化平台

---

## 1. 30 秒版（一句话）

> "我在实习期间做了一个电路布局优化平台，用模拟退火算法在芯片上自动放置电路模块，目标是让连线最短、不重叠、不拥塞。做了 CLI 命令行和 Streamlit Web 两个界面。"

---

## 2. 1 分钟版（电梯演讲）

> "我实习期间独立开发了一个电路布局优化原型平台。它的输入是 JSON 格式的电路模块和连线信息，包含 macro、standard cell、fixed IO 等类型。我使用模拟退火（Simulated Annealing）算法进行优化，cost function 包含五个维度：HPWL 线长、重叠、边界、密度和拥塞。HPWL 是 EDA 行业标准的线长指标，比简单曼哈顿距离更贴近真实布线。系统还做了拥塞估计——用网格法统计每个区域经过的连线数，生成热力图。最后用 Streamlit 做了一个 Web 界面，可以上传数据、调参数、实时看结果，适合实习汇报展示。HPWL 在两个测试用例上降低了 10-12%。"

---

## 3. 3 分钟版（面试详细版）

> "我做的项目是电路布局优化平台，定位是 IC CAD Physical Design 中 Placement 问题的原型系统。
>
> **背景**：芯片设计流程中，Physical Design 是把逻辑网表变成物理版图的过程。Placement 是第一步，也是最关键的一步——决定了芯片面积、时序、功耗。简单说就是在芯片上摆放模块，要连线最短、不重叠。
>
> **做了什么**：我建了一个 Python 项目，模块化设计，6 个核心模块。输入是 JSON，支持 macro、standard cell、fixed IO 三种模块类型，支持二端和多端 net。用模拟退火做优化，cost function 是五维的：HPWL、overlap、boundary、density、congestion，每个维度有独立权重可以调。
>
> **HPWL** 是 EDA 行业标准指标，对每条 net 取所有 pin 的 bounding box 半周长。为什么不用简单曼哈顿距离？因为 HPWL 更接近真实的 Steiner 树布线结果，而且 ISPD 和 ICCAD 的 placement benchmark 都用 HPWL。
>
> **拥塞估计**：即使线长短，如果所有线挤在一起，布线器也走不通。我用网格法，把芯片分成 10×10 格，每条 net 的 L 形路由经过的格点计数，然后画热力图。
>
> **结果**：两个测试用例（15 和 24 个模块）HPWL 分别降低 10.2% 和 12.0%。做了 CLI 和 Streamlit Web 双界面，Web 可以上传 JSON、调参、实时展示。项目有完整的文档：技术报告、PPT 大纲、面试稿、简历描述。
>
> **最大的收获**：第一是理解了 Placement 在 EDA 里的位置和核心问题，第二是学会了怎么把一个学术问题落地成实际可运行的代码，第三是多目标优化中 trade-off 的思维方式。"

---

## 4. "你这个和真实 EDA 工具有多大差距？"

> "差距非常大，我是有清醒认识的。
>
> **规模上**：我这个只能处理几十个模块，真实 EDA 工具处理百万级标准单元。我的 SA 算法在这个规模上完全不行——工业界用的是 Analytical Placement（基于二次规划），然后 Legalization，最后 Detailed Placement 三步走。
>
> **功能上**：我没有时序感知，没有 legalization，不支持 DEF/LEF 格式，路由模型也极其简化。
>
> **但**：我的 cost function 设计、HPWL 的计算方式、固定约束的处理逻辑——这些和学术界的 Placement 论文思路是一致的。所以你可以把它理解为一个教学/原型版本，用来展示 Placement 的核心概念，而不是工业级工具。
>
> 如果我继续做，下一步会去看 Analytical Placement 的方法，比如 ePlace 或 RePlAce 的论文，理解它们的数学模型，然后试着实现。"

---

## 5. "为什么用模拟退火？"

> "三个原因。
>
> **第一**，Placement 的 cost function 不可导——模块重叠的判断是离散的，不能用梯度下降。
>
> **第二**，SA 能跳出局部最优。它通过概率接受劣解的机制，高温时能探索全局空间，低温时收敛到局部最优。这个特性对组合优化问题很关键。
>
> **第三**，SA 在 Placement 领域有学术传统。1980 年代的 TimberWolf 就用 SA 做 placement，后来很多论文都用 SA 作为 baseline。我不是凭空选的。
>
> **当然 SA 也有局限**：收敛慢，对参数敏感，不适合大规模。工业界早已不用 SA 做 placement了——现在主流是分析性方法。但在原型验证和学术界 baseline 层面，SA 仍然是合理的选择。"

---

## 6. "HPWL 是什么？"

> "HPWL 是 Half-Perimeter Wirelength 的缩写，翻译过来是'半周长线长'。
>
> 具体来说，对一条 net 有 n 个 pin，每个 pin 有一个坐标 (x_i, y_i)，那么：
>
> ```
> HPWL = (max_x - min_x) + (max_y - min_y)
> ```
>
> 就是所有 pin 的 bounding box 的半周长。
>
> **为什么用它？** 因为真实的布线是在这个 bounding box 内部完成的 Steiner 树路由，HPWL 是这个树长度的紧致下界——数学上可以证明 Steiner 树长度 ≥ HPWL。而且 HPWL 计算是 O(n)，比两两之间算曼哈顿距离（O(n²)）快。
>
> **在 EDA 中的地位**：ISPD、ICCAD 等 placement benchmark 几乎都用 HPWL 作为线长指标。工业界 tool 内部可能用更复杂的模型，但 HPWL 是学术界和 benchmark 的标准。"

---

## 7. "拥塞估计怎么做的？"

> "我用的是网格法，这是学术界最常见的拥塞估计方法。
>
> **步骤**：
> 1. 把芯片分成 G×G 的均匀网格（默认 10×10 = 100 格）
> 2. 对每条 net，从第一个 pin 到最后一个 pin，走 L 形曼哈顿路径（先水平再垂直）
> 3. 路过的每个格点计数 +1
> 4. 最后得到一个二维矩阵，每个格点上的数字就是经过的 net 数量
> 5. 输出 max congestion、avg congestion 和 heatmap
>
> **局限性**：我用的是 L 形路由，真实 router 会用更智能的算法（如迷宫路由、模式路由），所以我的拥塞估计是上界——实际拥塞可能更低。另外我没有考虑 net 的宽度和 spacing rule。
>
> **怎么融入优化**：我把 max congestion 作为 cost function 的一个分量（ε × MaxCongestion），SA 在优化时会尝试减少高拥塞区域的 net 数量。"

---

## 8. "后续怎么接近工业级？"

> "说实话，从我现在这个原型到工业级 placement 工具，中间还有很长的路。但如果要做，我的思路是这样：
>
> **第一步**：把算法从 SA 换成 Analytical Placement。核心思想是把 placement 转化成数学优化问题——用二次规划（QP）或非线性规划（NLP）求解。经典的论文是 ePlace 和 RePlAce，我读过一些。
>
> **第二步**：加 Legalization。Analytical placement 的结果模块有重叠，需要合法化——把 standard cell 塞进 row 里。经典算法是 Tetris 和 Abacus。
>
> **第三步**：支持 DEF/LEF 格式。这是工业标准，也是 OpenROAD 的输入。解析 DEF/LEF 后就能跑真实 benchmark（如 ISPD 2015/2016）。
>
> **第四步**：加时序感知。通过 STA（静态时序分析）得到每个 net 的 slack，在 cost function 里加权——时序紧张的 net 权重更高。
>
> **更长期**：可以考虑强化学习做 macro placement。Google 2021 年的论文展示了用 RL 做 macro placement 效果很好。
>
> 目前这个原型最大的价值是让我理解了 Placement 问题的本质和 EDA 工具链的架构。如果以后真做 EDA 方向，这些基础概念会很有用。"
