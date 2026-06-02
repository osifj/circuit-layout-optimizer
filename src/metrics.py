"""
metrics.py — EDA 评价指标 (v1.1 增强版)

输出:
- pairwise_wirelength / HPWL / HPWL 降低%
- overlap (has_overlap)
- boundary / density
- congestion (max / avg / std / congested_cells)
- area_utilization / module type 统计
"""

import json
from pathlib import Path
from typing import Dict, Any
from .layout import Layout
from .cost import CostFunction


def compute_metrics(
    layout: Layout, cost_fn: CostFunction, grid_size: int = 10
) -> Dict[str, Any]:
    """
    计算布局的全部 EDA 评价指标。
    """
    total_cost, (wl, ov, bd, dn, cn) = cost_fn.total_cost(layout, grid_size)
    hpwl_val = cost_fn.hpwl(layout)
    pairwise_val = cost_fn.pairwise_wirelength(layout)
    cong = cost_fn.congestion_estimate(layout, grid_size)

    return {
        "total_wirelength": round(wl, 4),
        "pairwise_wirelength": round(pairwise_val, 4),
        "hpwl": round(hpwl_val, 4),
        "overlap_penalty": round(ov, 4),
        "has_overlap": ov > 1e-6,
        "boundary_penalty": round(bd, 4),
        "density_penalty": round(dn, 4),
        "congestion_penalty": int(cn),
        "total_cost": round(total_cost, 4),
        "area_utilization": round(layout.area_utilization, 4),
        "chip_area": layout.chip_area,
        "total_module_area": layout.total_module_area,
        "num_modules": len(layout.modules),
        "num_macros": len(layout.macros),
        "num_standard_cells": len(layout.standard_cells),
        "num_fixed_modules": len(layout.fixed_modules),
        "num_movable_modules": len(layout.movable_modules),
        "num_nets": len(layout.nets),
        "num_multi_pin_nets": sum(1 for n in layout.nets if n.is_multi_pin),
        "max_congestion": cong["max_congestion"],
        "avg_congestion": cong["avg_congestion"],
        "congestion_std": cong["congestion_std"],
        "congested_cells_count": cong["congested_cells_count"],
        "congestion_grid_size": cong["grid_size"],
        "congestion_grid": cong["grid"],
    }


def print_metrics(initial_metrics: dict, optimized_metrics: dict):
    """打印优化前后对比表格。"""
    print("\n" + "=" * 75)
    print(" 📊 布局优化评价指标 (EDA v1.1)")
    print("=" * 75)
    print(f"{'指标':<30} {'优化前':>18} {'优化后':>18}")
    print("-" * 66)

    keys_display = [
        ("hpwl", "HPWL (半周长线长)"),
        ("pairwise_wirelength", "Pairwise Wirelength"),
        ("overlap_penalty", "重叠惩罚"),
        ("boundary_penalty", "边界惩罚"),
        ("density_penalty", "密度惩罚"),
        ("congestion_penalty", "拥塞惩罚 (max)"),
        ("total_cost", "总成本"),
        ("area_utilization", "面积利用率"),
        ("max_congestion", "最大拥塞 (nets/cell)"),
        ("avg_congestion", "平均拥塞 (nets/cell)"),
        ("congested_cells_count", "拥塞格点数"),
    ]

    for key, label in keys_display:
        before = initial_metrics.get(key, "N/A")
        after = optimized_metrics.get(key, "N/A")
        b_str = f"{before:.4f}" if isinstance(before, float) else str(before)
        a_str = f"{after:.4f}" if isinstance(after, float) else str(after)
        print(f"{label:<30} {b_str:>18} {a_str:>18}")

    print("-" * 66)
    print(f"{'模块统计':<30} {'':>18} {'':>18}")
    for key, label in [
        ("num_modules", "总模块数"),
        ("num_macros", "Macro 数"),
        ("num_standard_cells", "Standard Cell 数"),
        ("num_fixed_modules", "Fixed 模块数"),
        ("num_movable_modules", "Movable 模块数"),
        ("num_nets", "连线数"),
        ("num_multi_pin_nets", "多端 Net 数"),
    ]:
        b = initial_metrics.get(key, "N/A")
        a = optimized_metrics.get(key, "N/A")
        print(f"  {label:<28} {str(b):>18} {str(a):>18}")

    # HPWL 降低百分比
    init_hpwl = initial_metrics.get("hpwl", 0)
    opt_hpwl = optimized_metrics.get("hpwl", 0)
    if isinstance(init_hpwl, (int, float)) and init_hpwl > 0:
        reduction = (1 - opt_hpwl / init_hpwl) * 100
        print(f"\n   📉 HPWL 降低: {reduction:+.1f}%")

    # Overlap
    opt_ov = optimized_metrics.get("has_overlap", False)
    print(f"   {'⚠️ 仍有重叠' if opt_ov else '✅ 无重叠'}")

    print("=" * 75)


def save_metrics(metrics: dict, output_path: str):
    """保存指标到 JSON (去除 numpy array)。"""
    # 深拷贝并清理 numpy 类型
    clean = {}
    for k, v in metrics.items():
        if k == "congestion_grid":
            continue  # numpy array, 不存 JSON
        if hasattr(v, "tolist"):
            clean[k] = v.tolist()
        elif isinstance(v, (int, float, str, bool, list, dict)):
            clean[k] = v
        else:
            clean[k] = str(v)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2, ensure_ascii=False)
    print(f"📊 指标已保存: {output_path}")
