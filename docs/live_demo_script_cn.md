# 项目现场演示流程

**总时长**: 3-5 分钟  
**准备**: 提前打开终端，cd 到项目目录

---

## Step 1: 展示 GitHub / 项目目录（20 秒）

```bash
cd circuit-layout-optimizer
ls
```

> "这是项目目录。src 下面是 6 个核心模块，data 是测试数据，docs 是技术文档，outputs 是运行结果。README 里有完整的说明。"

打开 `README.md` 快速滚动展示结构。

---

## Step 2: 运行 CLI（40 秒）

```bash
python3 main.py --input data/example_eda_small.json --iter 3000 --temp 800 --use-hpwl --epsilon 1.0
```

> "先用命令行跑一下。这个例子有 15 个模块，4 个固定 IO。模拟退火 3000 轮，可以看到 HPWL 从三千多降到三千出头，降低了约 10%。"

等运行结束，指最后的指标表格。

---

## Step 3: 展示输出图片（30 秒）

```bash
ls -lh outputs/
open outputs/comparison.png
```

> "运行完生成了这些文件。comparison.png 是优化前后对比——左边是随机初始化，模块分散但连线长；右边是优化后，连线明显更紧密。"

依次打开：
- `outputs/comparison.png` — 前后对比
- `outputs/cost_curve.png` — 收敛曲线
- `outputs/congestion_map.png` — 拥塞热力图

> "收敛曲线有 6 个子图——Cost、HPWL、Overlap、Congestion、Density、Temperature——可以看到 SA 收敛过程。拥塞热力图用颜色表示每格电线密度，红色是热点。"

---

## Step 4: 启动 Streamlit Web（60 秒）

```bash
streamlit run app.py
```

浏览器打开 `http://localhost:8501`

> "现在看 Web 版。左边是参数面板——选示例、调权重、调迭代。右边是输入预览——15 个模块的表格。"

### 演示操作：

1. **选择 EDA Medium 示例**：下拉框选 "EDA Medium (24 modules)"
   > "切到 24 模块的例子。可以看到模块表格更新了，有 Macro、Standard Cell、Fixed IO。"

2. **调参数**：滑动 iterations 到 2000，epsilon 到 2.0
   > "参数都可以拖动调节。比如把拥塞权重调大一点。"

3. **点击 Run Optimization**
   > "点运行。等待几秒到十几秒。"

4. **指结果**：
   > "指标卡片出来了——HPWL 降低 12%，Cost 降低 11.6%。"
   > "往下滚——初始和优化布局并排显示。"
   > "收敛曲线、拥塞热力图。"
   > "最下面可以下载 result.json 和 metrics_summary.json。"

---

## Step 5: 总结亮点（20 秒）

> "总结一下——这个项目的亮点：
>
> 1. 完整的 Placement 优化流程——建模、算法、可视化、Web 全覆盖
> 2. HPWL 用的是 EDA 行业标准，不是简单曼哈顿距离
> 3. 拥塞估计和 fixed constraint 让平台更贴近真实 EDA 场景
> 4. CLI + Web 双界面，既能脚本跑也能汇报展示
> 5. 腾讯文档齐全——技术报告、PPT 大纲、面试稿都有"

---

## 备选：如果有时间，演示自定义 JSON

```bash
# 创建一个简单 JSON
cat > /tmp/my_circuit.json << 'EOF'
{
  "chip_width": 150,
  "chip_height": 150,
  "modules": [
    {"id": "CPU", "width": 30, "height": 25, "type": "macro"},
    {"id": "MEM", "width": 25, "height": 20, "type": "macro"},
    {"id": "IO1", "width": 5, "height": 5, "type": "macro", "fixed": true, "x": 0, "y": 0}
  ],
  "nets": [
    {"name": "n1", "pins": ["CPU", "MEM", "IO1"], "weight": 2.0}
  ]
}
EOF

# 用 CLI 跑
python3 main.py --input /tmp/my_circuit.json --iter 1000

# 或在 Web 里上传
```

> "甚至可以现场写一个 JSON 跑——看，HPWL 从原始降到优化后。"

---

## 注意事项

1. **提前准备**：确保 `outputs/` 下已有图片文件，跑过一次 CLI 生成初始图片
2. **网络**：Streamlit 需要本地端口 8501 不被占用
3. **时间控制**：CLI 运行可能需要 10-30 秒不等，Web 运行时间类似，留出缓冲
4. **如果出错**：检查 `pip install -r requirements.txt` 是否完整
