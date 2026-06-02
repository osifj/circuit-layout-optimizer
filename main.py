#!/usr/bin/env python3
"""
main.py — 电路布局优化平台 v1.1 EDA 增强版

用法:
    python3 main.py --input data/example_eda_small.json --use-hpwl --epsilon 1.0
    python3 main.py --input data/example_eda_medium.json --iter 5000 --temp 1000 --grid-size 10

新增参数:
    --use-hpwl     使用 HPWL 作为线长指标 (默认开启)
    --epsilon      拥塞惩罚权重 (默认 1.0)
    --grid-size    拥塞估计网格大小 (默认 10)
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.parser import parse_input
from src.layout import Layout, Module, Net
from src.cost import CostFunction
from src.optimizer import SimulatedAnnealing
from src.metrics import compute_metrics, print_metrics, save_metrics
from src.visualize import (
    draw_layout, draw_comparison, draw_cost_curve, draw_congestion_heatmap
)


def build_layout(data: dict) -> Layout:
    """从解析后的 JSON 构建 Layout 对象。"""
    modules = [
        Module(
            id=m["id"], width=m["width"], height=m["height"],
            x=m.get("x", 0.0), y=m.get("y", 0.0),
            module_type=m.get("type", "macro"),
            fixed=m.get("fixed", False),
        )
        for m in data["modules"]
    ]
    nets = [
        Net(
            name=n.get("name", f"net_{i}"),
            pins=n["pins"],
            weight=n.get("weight", 1.0),
        )
        for i, n in enumerate(data.get("nets", []))
    ]
    return Layout(
        chip_width=data["chip_width"],
        chip_height=data["chip_height"],
        modules=modules,
        nets=nets,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Circuit Layout Optimization Platform v1.1 — 电路布局优化平台 EDA 版"
    )
    parser.add_argument("--input", "-i", default="data/example_small.json",
                        help="输入 JSON 文件路径")
    parser.add_argument("--output", "-o", default="outputs/result.json",
                        help="输出结果 JSON 路径")
    parser.add_argument("--alpha", type=float, default=1.0,
                        help="HPWL 权重 (默认 1.0)")
    parser.add_argument("--beta", type=float, default=10.0,
                        help="重叠惩罚权重 (默认 10.0)")
    parser.add_argument("--gamma", type=float, default=100.0,
                        help="边界惩罚权重 (默认 100.0)")
    parser.add_argument("--delta", type=float, default=5.0,
                        help="密度惩罚权重 (默认 5.0)")
    parser.add_argument("--epsilon", type=float, default=1.0,
                        help="拥塞惩罚权重 (默认 1.0)")
    parser.add_argument("--use-hpwl", action="store_true", default=True,
                        help="使用 HPWL 作为线长指标 (默认)")
    parser.add_argument("--no-hpwl", action="store_true",
                        help="禁用 HPWL，使用 pairwise wirelength")
    parser.add_argument("--grid-size", type=int, default=10,
                        help="拥塞估计网格大小 (默认 10)")
    parser.add_argument("--iter", type=int, default=2000, dest="max_iter",
                        help="模拟退火最大迭代次数")
    parser.add_argument("--temp", type=float, default=500.0,
                        dest="initial_temp", help="初始温度")
    parser.add_argument("--cooling", type=float, default=0.995,
                        dest="cooling_rate", help="降温系数")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    parser.add_argument("--summary", default="outputs/metrics_summary.json",
                        help="指标汇总 JSON 路径")

    args = parser.parse_args()

    use_hpwl = args.use_hpwl and not args.no_hpwl

    print("=" * 65)
    print(" 🧬 Circuit Layout Optimization Platform v1.1")
    print("    电路布局优化平台 EDA 增强版")
    print("=" * 65)

    # Step 1: 解析
    print("\n📂 Step 1: 加载输入文件...")
    data = parse_input(args.input)

    # Step 2: 构建
    print("\n🔧 Step 2: 构建布局数据结构...")
    layout = build_layout(data)
    print(f"   模块: {len(layout.modules)} "
          f"(macro={len(layout.macros)}, SC={len(layout.standard_cells)}, "
          f"fixed={len(layout.fixed_modules)})")
    print(f"   连线: {len(layout.nets)} "
          f"(多端 net={sum(1 for n in layout.nets if n.is_multi_pin)})")
    print(f"   面积利用率: {layout.area_utilization:.1%}")

    # Step 3: 随机初始化
    print("\n🎲 Step 3: 随机初始化 + 初始评估...")
    layout.randomize_positions(seed=args.seed)

    cost_fn = CostFunction(
        alpha=args.alpha, beta=args.beta, gamma=args.gamma,
        delta=args.delta, epsilon=args.epsilon,
        use_hpwl=use_hpwl,
    )
    initial_cost, initial_components = cost_fn.total_cost(layout, args.grid_size)
    print(f"   初始 cost = {initial_cost:.2f}  "
          f"HPWL={initial_components[0]:.2f}  重叠={initial_components[1]:.2f}  "
          f"拥塞={initial_components[4]:.0f}")

    draw_layout(layout, title="Initial Layout (Random)",
                output_path="outputs/initial_layout.png")

    # Step 4: SA 优化
    print("\n🔬 Step 4: 模拟退火优化...")
    sa = SimulatedAnnealing(
        cost_fn=cost_fn,
        initial_temp=args.initial_temp,
        cooling_rate=args.cooling_rate,
        max_iter=args.max_iter,
        grid_size=args.grid_size,
        seed=args.seed,
    )
    optimized = sa.optimize(layout, verbose=True)

    # Step 5: 评测
    print("\n📊 Step 5: 最终评价...")
    initial_metrics = compute_metrics(layout, cost_fn, args.grid_size)
    optimized_metrics = compute_metrics(optimized, cost_fn, args.grid_size)

    print_metrics(initial_metrics, optimized_metrics)

    # 拥塞
    init_cong = cost_fn.congestion_estimate(layout, args.grid_size)
    opt_cong = cost_fn.congestion_estimate(optimized, args.grid_size)
    print(f"\n   拥塞对比: max {init_cong['max_congestion']}→{opt_cong['max_congestion']}"
          f"  avg {init_cong['avg_congestion']:.2f}→{opt_cong['avg_congestion']:.2f}"
          f"  congested_cells {init_cong['congested_cells_count']}→{opt_cong['congested_cells_count']}")

    # 保存结果
    result = optimized.to_result(
        cost=optimized_metrics["total_cost"],
        wirelength=optimized_metrics["total_wirelength"],
        overlap=optimized_metrics["overlap_penalty"],
        boundary=optimized_metrics["boundary_penalty"],
        density=optimized_metrics["density_penalty"],
        hpwl=optimized_metrics["hpwl"],
        max_congestion=opt_cong["max_congestion"],
        avg_congestion=opt_cong["avg_congestion"],
        congestion=opt_cong,
    )
    save_metrics(result, args.output)

    # 指标汇总
    summary = {
        "initial": {k: v for k, v in initial_metrics.items()
                     if k != "congestion_grid"},
        "optimized": {k: v for k, v in optimized_metrics.items()
                       if k != "congestion_grid"},
        "hpwl_reduction_pct": (
            round((1 - optimized_metrics["hpwl"] / max(initial_metrics["hpwl"], 1e-6)) * 100, 2)
        ),
        "congestion_max_change": (
            opt_cong["max_congestion"] - init_cong["max_congestion"]
        ),
    }
    print(f"\n📊 指标汇总已保存: {args.summary}")
    Path(args.summary).parent.mkdir(parents=True, exist_ok=True)
    with open(args.summary, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False,
                  default=lambda o: int(o) if hasattr(o, "item") else str(o))

    # Step 6: 可视化
    print("\n🎨 Step 6: 生成可视化图表...")
    draw_layout(optimized, title="Optimized Layout",
                output_path="outputs/optimized_layout.png")
    draw_comparison(layout, optimized)
    draw_cost_curve(sa.history)
    draw_congestion_heatmap(
        optimized, opt_cong["grid"], opt_cong["grid_size"],
        output_path="outputs/congestion_map.png",
    )

    print("\n" + "=" * 65)
    print(" ✅ 全部完成！")
    print("=" * 65)
    print(f"  📁 results:        {args.output}")
    print(f"  📊 metrics summary: {args.summary}")
    print(f"  📊 comparison:      outputs/comparison.png")
    print(f"  📈 cost curve:      outputs/cost_curve.png")
    print(f"  📊 congestion map:  outputs/congestion_map.png")
    print(f"  📐 initial layout:  outputs/initial_layout.png")
    print(f"  📐 optimized layout:outputs/optimized_layout.png")


if __name__ == "__main__":
    main()
