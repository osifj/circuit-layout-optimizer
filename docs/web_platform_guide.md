# Web 平台使用指南

Circuit Layout Optimization Platform — Streamlit Web 界面操作手册

---

## 1. 启动平台

```bash
cd circuit-layout-optimizer
streamlit run app.py
```

浏览器打开 `http://localhost:8501`

---

## 2. 页面结构

```
┌────────────────────────────────────────────────────────┐
│  🧬 Circuit Layout Optimization Platform              │
│  电路布局优化平台 — EDA / IC CAD Placement Demo        │
├──────────────┬─────────────────────────────────────────┤
│  SIDEBAR     │  MAIN AREA                              │
│              │  ┌─ About This Platform ────────────┐   │
│  📂 Input    │  │  (可折叠的介绍区)               │   │
│  - Example   │  └──────────────────────────────────┘   │
│  - Upload    │  ┌─ Input Data Preview ─────────────┐   │
│              │  │  6 metrics + modules/nets tables  │   │
│  🔬 SA Params│  └──────────────────────────────────┘   │
│  - Iterations│  ┌─ After RUN: ──────────────────────┐   │
│  - Temp      │  │  Key Metrics Cards                │   │
│  - Cooling   │  │  Layout Images                    │   │
│              │  │  Cost Curve / Congestion Map      │   │
│  📐 Weights  │  │  Downloads + JSON Preview         │   │
│  - α β γ δ ε │  └──────────────────────────────────┘   │
│              │                                          │
│  🚀 RUN      │                                          │
└──────────────┴─────────────────────────────────────────┘
```

---

## 3. 参数含义

### Simulated Annealing 参数

| 参数 | 含义 | 建议值 |
|------|------|--------|
| Iterations | SA 最大迭代轮数 | 2000-5000 |
| Initial Temp | 初始温度（高→探索性强） | 500-1000 |
| Cooling Rate | 降温系数（接近 1→慢冷却→精细） | 0.990-0.999 |

### Cost Function 权重

| 参数 | 含义 | 默认值 | 调节建议 |
|------|------|--------|----------|
| α | HPWL 权重 | 1.0 | 线长最重要，保持 1.0 |
| β | 重叠惩罚 | 10.0 | 有重叠 → 调高 β |
| γ | 边界惩罚 | 100.0 | 保持高位 |
| δ | 密度惩罚 | 5.0 | 模块太集中 → 调高 δ |
| ε | 拥塞惩罚 | 1.0 | 拥塞高 → 调高 ε |

---

## 4. 如何运行优化

1. **选择输入**：Sidebar 选内置示例 或 上传自定义 JSON
2. **调参**：滑动条调整 SA 参数和 cost weights
3. **点击 🚀 Run Optimization**
4. **等待**：进度条旋转 + "Running" 提示
5. **查看结果**：指标卡片 → 布局图 → 收敛曲线 → 拥塞热力图

---

## 5. 如何解读 HPWL Reduction

**HPWL Reduction = (初始 HPWL - 优化后 HPWL) / 初始 HPWL × 100%**

- 正值（如 +12%）：HPWL 降低，优化有效 ✅
- 负值：HPWL 增加，权重或参数需调整 ⚠️
- 一般小规模（15 modules）预期降低 10-20%
- 中规模（25 modules）预期降低 8-15%

---

## 6. 如何解读 Congestion Map

热力图颜色含义：

| 颜色 | 含义 |
|------|------|
| 浅黄 | 低拥塞（< 3 nets） — 布线空间充裕 |
| 橙 | 中拥塞（3-6 nets） — 需关注 |
| 深红 | 高拥塞（> 6 nets） — 布线热点，可能要调 ε |

网格数 = Grid Size × Grid Size（默认 10×10=100 格）

---

## 7. 用于实习汇报展示

### 展示流程建议

1. **开场**：展示平台首页 + 简介 "About This Platform"
2. **输入**：选 EDA Medium 示例，展示模块/Nets 表格
3. **运行**：点 Run，等待 10-30 秒
4. **指标**：重点展示 HPWL 降低%、Cost 降低%
5. **布局图**：对比 initial vs optimized，说明模块从随机→优化分布
6. **收敛曲线**：展示 Cost 持续下降，验证 SA 算法收敛
7. **拥塞热力图**：解释颜色含义，说明为什么 EDA 要关注 congestion
8. **下载**：展示 result.json / metrics_summary.json 可导出

### 需要强调的技术点

- HPWL 是 IC placement 行业标准线长指标
- Simulated Annealing 是经典的 EDA 优化算法
- Multi-objective cost function 覆盖线长、重叠、边界、密度、拥塞五个维度
- Fixed IO 约束体现真实设计中的 floorplan 约束
- Macro / Standard Cell 区分体现模块级别的 placement 概念

---

## 8. 常见问题

### Q: 优化后仍有 Overlap？
**A:** 增大 β 或增加 Iterations。SA 需要足够迭代才能完全消除重叠。

### Q: HPWL 降低不多？
**A:** 如果初始随机布局恰好不错，降低空间小。可增加 Iterations 并降低 cooling rate。

### Q: Congestion 不变？
**A:** 增大 ε 让 SA 更重视拥塞优化。默认 ε=1.0 对 congestion 敏感度低。

### Q: 如何用自定义数据？
**A:** 上传 JSON 文件。格式参考 `data/example_eda_small.json`。支持二端 net (source/target) 和多端 net (pins)。
