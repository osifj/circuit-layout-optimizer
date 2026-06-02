"""
visualize.py — 可视化模块 (v1.1 EDA 增强版)

功能:
- 区分 macro / standard_cell / fixed 模块渲染
- 布局图 + 对比图 + 收敛曲线 + 拥塞热力图
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from .layout import Layout


MACRO_COLORS = [
    "#4ECDC4", "#FF6B6B", "#FFE66D", "#45B7D1",
    "#96CEB4", "#DDA0DD", "#98D8C8", "#F7DC6F",
    "#BB8FCE", "#85C1E9", "#F8C471", "#82E0AA",
    "#F1948A", "#AED6F1", "#D2B4DE", "#A3E4D7",
]

SC_COLORS = [
    "#3498DB", "#E74C3C", "#2ECC71", "#F39C12",
    "#9B59B6", "#1ABC9C", "#E67E22", "#16A085",
]

FIXED_COLOR = "#555555"
FIXED_HATCH = "////"


def _module_style(mod):
    """返回模块的颜色、hatch、边框样式。"""
    if mod.fixed:
        return FIXED_COLOR, FIXED_HATCH, "#333333", 2.5
    if mod.is_standard_cell:
        idx = hash(mod.id) % len(SC_COLORS)
        return SC_COLORS[idx], None, "#222222", 1.0
    idx = hash(mod.id) % len(MACRO_COLORS)
    return MACRO_COLORS[idx], None, "#222222", 1.5


def draw_layout(
    layout: Layout,
    title: str = "Layout",
    output_path: Optional[str] = None,
    show_nets: bool = True,
) -> str:
    """绘制单个布局图。区分 macro/SC/fixed 样式。"""
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-5, layout.chip_width + 5)
    ax.set_ylim(-5, layout.chip_height + 5)

    # 芯片边界
    chip = patches.Rectangle(
        (0, 0), layout.chip_width, layout.chip_height,
        linewidth=2, edgecolor="#333333", facecolor="#FAFAFA", zorder=0
    )
    ax.add_patch(chip)

    # 连线
    if show_nets:
        for net in layout.nets:
            centers = []
            for pid in net.pins:
                try:
                    m = layout.module_by_id(pid)
                    centers.append(m.center)
                except KeyError:
                    continue
            if len(centers) < 2:
                continue
            for i in range(len(centers) - 1):
                alpha = min(1.0, max(0.12, net.weight / 3.0))
                ax.plot(
                    [centers[i][0], centers[i+1][0]],
                    [centers[i][1], centers[i+1][1]],
                    color="#AAAAAA", linewidth=net.weight * 1.2,
                    alpha=alpha, zorder=1
                )

    # 模块
    for mod in layout.modules:
        color, hatch, edge_color, lw = _module_style(mod)
        rect = patches.Rectangle(
            (mod.x, mod.y), mod.width, mod.height,
            linewidth=lw, edgecolor=edge_color, facecolor=color,
            alpha=0.85 if mod.fixed else 0.75,
            hatch=hatch,
            zorder=2
        )
        ax.add_patch(rect)
        cx, cy = mod.center
        label = mod.id if mod.width > 3 else ""
        if label:
            ax.text(cx, cy, label, ha="center", va="center",
                    fontsize=7 if mod.is_standard_cell else 9,
                    fontweight="bold", color="#111111", zorder=3)
        # fixed 标记
        if mod.fixed:
            ax.text(cx, mod.y - 2, "[FIXED]", ha="center", va="top",
                    fontsize=5, color="#888888", zorder=3)

    # 图例
    from matplotlib.lines import Line2D
    legend_items = []
    if layout.macros:
        legend_items.append(patches.Patch(facecolor=MACRO_COLORS[0], alpha=0.75,
                                          label=f"Macro ({len(layout.macros)})"))
    if layout.standard_cells:
        legend_items.append(patches.Patch(facecolor=SC_COLORS[0], alpha=0.75,
                                          label=f"StdCell ({len(layout.standard_cells)})"))
    if layout.fixed_modules:
        legend_items.append(patches.Patch(facecolor=FIXED_COLOR, alpha=0.85,
                                          hatch=FIXED_HATCH,
                                          label=f"Fixed ({len(layout.fixed_modules)})"))
    if legend_items:
        ax.legend(handles=legend_items, loc="upper right", fontsize=8)

    ax.set_aspect("equal")
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("X"); ax.set_ylabel("Y")
    ax.grid(True, alpha=0.3, linestyle="--")

    if output_path is None:
        output_path = f"outputs/{title.lower().replace(' ', '_')}.png"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"📊 布局图已保存: {output_path}")
    return output_path


def draw_comparison(
    initial: Layout, optimized: Layout,
    output_path: str = "outputs/comparison.png",
):
    """并排对比优化前后布局。"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    for ax, layout, title in [
        (ax1, initial, "Initial Layout (Random)"),
        (ax2, optimized, "Optimized Layout (Simulated Annealing)")
    ]:
        ax.set_xlim(-5, layout.chip_width + 5)
        ax.set_ylim(-5, layout.chip_height + 5)
        chip = patches.Rectangle(
            (0, 0), layout.chip_width, layout.chip_height,
            linewidth=2, edgecolor="#333333", facecolor="#FAFAFA", zorder=0
        )
        ax.add_patch(chip)

        for net in layout.nets:
            centers = []
            for pid in net.pins:
                try:
                    m = layout.module_by_id(pid)
                    centers.append(m.center)
                except KeyError:
                    continue
            for i in range(len(centers) - 1):
                ax.plot(
                    [centers[i][0], centers[i+1][0]],
                    [centers[i][1], centers[i+1][1]],
                    color="#CCCCCC", linewidth=0.8, alpha=0.5, zorder=1
                )

        for mod in layout.modules:
            color, hatch, edge_color, lw = _module_style(mod)
            rect = patches.Rectangle(
                (mod.x, mod.y), mod.width, mod.height,
                linewidth=lw, edgecolor=edge_color, facecolor=color,
                alpha=0.85 if mod.fixed else 0.75,
                hatch=hatch, zorder=2
            )
            ax.add_patch(rect)
            cx, cy = mod.center
            if mod.width > 3:
                ax.text(cx, cy, mod.id, ha="center", va="center",
                        fontsize=7 if mod.is_standard_cell else 9,
                        fontweight="bold", zorder=3)

        ax.set_aspect("equal")
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.grid(True, alpha=0.3, linestyle="--")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"📊 对比图已保存: {output_path}")
    return output_path


def draw_cost_curve(
    history: List[Dict[str, Any]],
    output_path: str = "outputs/cost_curve.png",
):
    """绘制收敛曲线 (含 HPWL + congestion)。"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    iters = [h["iteration"] for h in history]

    # Total Cost
    ax = axes[0, 0]
    ax.plot(iters, [h["current_cost"] for h in history],
            alpha=0.35, color="#FF6B6B", linewidth=0.5, label="Current")
    ax.plot(iters, [h["best_cost"] for h in history],
            color="#2ECC71", linewidth=2, label="Best")
    ax.set_xlabel("Iter"); ax.set_ylabel("Cost")
    ax.set_title("Total Cost"); ax.legend(); ax.grid(True, alpha=0.3)

    # HPWL
    ax = axes[0, 1]
    ax.plot(iters, [h["hpwl"] for h in history], color="#3498DB", linewidth=1)
    ax.set_xlabel("Iter"); ax.set_ylabel("HPWL")
    ax.set_title("HPWL"); ax.grid(True, alpha=0.3)

    # Overlap
    ax = axes[0, 2]
    ax.plot(iters, [h["overlap"] for h in history], color="#E74C3C", linewidth=1)
    ax.set_xlabel("Iter"); ax.set_ylabel("Overlap")
    ax.set_title("Overlap Penalty"); ax.grid(True, alpha=0.3)

    # Congestion
    ax = axes[1, 0]
    ax.plot(iters, [h["congestion"] for h in history], color="#E67E22", linewidth=1)
    ax.set_xlabel("Iter"); ax.set_ylabel("Max Congestion")
    ax.set_title("Congestion"); ax.grid(True, alpha=0.3)

    # Density
    ax = axes[1, 1]
    ax.plot(iters, [h["density"] for h in history], color="#9B59B6", linewidth=1)
    ax.set_xlabel("Iter"); ax.set_ylabel("Density")
    ax.set_title("Density Penalty"); ax.grid(True, alpha=0.3)

    # Temperature
    ax = axes[1, 2]
    ax.plot(iters, [h["temperature"] for h in history], color="#1ABC9C", linewidth=1.5)
    ax.set_xlabel("Iter"); ax.set_ylabel("T")
    ax.set_title("Temperature Decay"); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"📊 收敛曲线已保存: {output_path}")
    return output_path


def draw_congestion_heatmap(
    layout: Layout,
    congestion_grid: np.ndarray,
    grid_size: int,
    output_path: str = "outputs/congestion_map.png",
):
    """绘制布线拥塞热力图。"""
    fig, ax = plt.subplots(figsize=(9, 8))
    cell_w = layout.chip_width / grid_size
    cell_h = layout.chip_height / grid_size

    extent = [0, layout.chip_width, 0, layout.chip_height]
    im = ax.imshow(
        congestion_grid, origin="lower", extent=extent,
        cmap="YlOrRd", aspect="auto", alpha=0.85, interpolation="nearest",
    )
    cbar = plt.colorbar(im, ax=ax, shrink=0.85)
    cbar.set_label("Number of Nets", fontsize=10)

    # 芯片边界
    chip = patches.Rectangle(
        (0, 0), layout.chip_width, layout.chip_height,
        linewidth=2, edgecolor="#333333", facecolor="none", zorder=3
    )
    ax.add_patch(chip)

    # 模块轮廓
    for mod in layout.modules:
        color, _, edge_color, lw = _module_style(mod)
        rect = patches.Rectangle(
            (mod.x, mod.y), mod.width, mod.height,
            linewidth=lw * 0.8, edgecolor=edge_color, facecolor="none",
            alpha=0.6, zorder=4
        )
        ax.add_patch(rect)
        if mod.width > 3:
            cx, cy = mod.center
            ax.text(cx, cy, mod.id, ha="center", va="center",
                    fontsize=6, fontweight="bold", color="#111111",
                    zorder=5)

    # 网格线
    for i in range(grid_size + 1):
        ax.axvline(i * cell_w, color="#999999", linewidth=0.3, alpha=0.4)
        ax.axhline(i * cell_h, color="#999999", linewidth=0.3, alpha=0.4)

    ax.set_xlim(-2, layout.chip_width + 2)
    ax.set_ylim(-2, layout.chip_height + 2)
    ax.set_aspect("equal")
    ax.set_title(
        f"Routing Congestion Map ({grid_size}×{grid_size})\n"
        f"Max={congestion_grid.max():.0f}  Avg={congestion_grid.mean():.2f}",
        fontsize=13, fontweight="bold"
    )
    ax.set_xlabel("X"); ax.set_ylabel("Y")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"📊 拥塞热力图已保存: {output_path}")
    return output_path
