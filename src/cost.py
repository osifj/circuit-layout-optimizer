"""
cost.py — 多目标成本函数 (v1.1 EDA 增强版)

实现:
1. pairwise wirelength — 加权曼哈顿距离 (所有 pin pair)
2. HPWL — Half-Perimeter Wirelength (EDA 标准)
3. overlap penalty — 重叠面积惩罚
4. boundary penalty — 超出芯片边界惩罚
5. density penalty — 局部密度惩罚
6. congestion estimation + penalty — 网格拥塞估计与惩罚

Total Cost = α × HPWL + β × Overlap + γ × Boundary + δ × Density + ε × Congestion
"""

import numpy as np
from typing import Tuple, List
from .layout import Layout


class CostFunction:
    """
    多目标成本函数 (EDA 专业版)。

    Attributes:
        alpha: HPWL 权重
        beta: 重叠惩罚权重
        gamma: 边界惩罚权重
        delta: 密度惩罚权重
        epsilon: 拥塞惩罚权重
        use_hpwl: True=使用 HPWL, False=使用 pairwise wirelength
    """

    def __init__(
        self,
        alpha: float = 1.0,
        beta: float = 10.0,
        gamma: float = 100.0,
        delta: float = 5.0,
        epsilon: float = 1.0,
        use_hpwl: bool = True,
    ):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.epsilon = epsilon
        self.use_hpwl = use_hpwl

    # ── Wirelength ──────────────────────────────────────────

    def pairwise_wirelength(self, layout: Layout) -> float:
        """
        计算所有 pin pair 的加权曼哈顿距离之和。

        对于多端 net (pins: [A,B,C])：
            遍历所有 pair (A,B), (A,C), (B,C) 并乘以 weight。
        """
        total = 0.0
        for net in layout.nets:
            # 获取所有有效模块的中心点
            centers = []
            for pid in net.pins:
                try:
                    m = layout.module_by_id(pid)
                    centers.append(m.center)
                except KeyError:
                    continue
            if len(centers) < 2:
                continue
            # 全 pair 遍历
            for i in range(len(centers)):
                for j in range(i + 1, len(centers)):
                    dist = abs(centers[i][0] - centers[j][0]) + abs(centers[i][1] - centers[j][1])
                    total += net.weight * dist
        return total

    def hpwl(self, layout: Layout) -> float:
        """
        计算 Half-Perimeter Wirelength (HPWL)。

        对每条 net，取所有 pin (模块中心) 的 bounding box:
            HPWL_net = (max_x - min_x) + (max_y - min_y)

        这是 IC placement 行业标准线长估算。
        """
        total = 0.0
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
            xs = [c[0] for c in centers]
            ys = [c[1] for c in centers]
            hpwl_net = (max(xs) - min(xs)) + (max(ys) - min(ys))
            total += net.weight * hpwl_net
        return total

    def wirelength_cost(self, layout: Layout) -> float:
        """根据 use_hpwl 标志返回对应的线长指标。"""
        if self.use_hpwl:
            return self.hpwl(layout)
        return self.pairwise_wirelength(layout)

    # ── Overlap ─────────────────────────────────────────────

    def overlap_penalty(self, layout: Layout) -> float:
        """模块间重叠面积惩罚。"""
        penalty = 0.0
        mods = layout.modules
        for i in range(len(mods)):
            for j in range(i + 1, len(mods)):
                penalty += mods[i].overlap_area(mods[j])
        return penalty

    # ── Boundary ────────────────────────────────────────────

    def boundary_penalty(self, layout: Layout) -> float:
        """模块超出芯片边界的距离惩罚。"""
        penalty = 0.0
        w, h = layout.chip_width, layout.chip_height
        for mod in layout.modules:
            if mod.x < 0:
                penalty += abs(mod.x)
            if mod.x + mod.width > w:
                penalty += (mod.x + mod.width - w)
            if mod.y < 0:
                penalty += abs(mod.y)
            if mod.y + mod.height > h:
                penalty += (mod.y + mod.height - h)
        return penalty

    # ── Density ─────────────────────────────────────────────

    def density_penalty(self, layout: Layout) -> float:
        """模块集中度惩罚 → 鼓励分散布局。"""
        if len(layout.modules) <= 1:
            return 0.0
        centers = np.array([m.center for m in layout.modules])
        var_x = np.var(centers[:, 0]) / (layout.chip_width ** 2)
        var_y = np.var(centers[:, 1]) / (layout.chip_height ** 2)
        avg_var = (var_x + var_y) / 2
        return 1.0 / (avg_var + 1e-6)

    # ── Congestion ──────────────────────────────────────────

    def congestion_estimate(
        self, layout: Layout, grid_size: int = 10
    ) -> dict:
        """
        网格布线拥塞估计。

        划分 grid_size×grid_size 网格，对每条 net 用 L 形
        曼哈顿路由追踪经过的格点，统计每格 net 数。

        Returns:
            dict: {grid_size, grid, max_congestion, avg_congestion,
                   congestion_std, congested_cells_count}
        """
        grid = np.zeros((grid_size, grid_size), dtype=int)
        cell_w = layout.chip_width / grid_size
        cell_h = layout.chip_height / grid_size

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

            # 对多端 net：从第一个 pin 出发，依次 L 形路由到每个后续 pin
            for i in range(len(centers) - 1):
                cx1, cy1 = centers[i]
                cx2, cy2 = centers[i + 1]
                gx1 = min(grid_size - 1, max(0, int(cx1 / cell_w)))
                gy1 = min(grid_size - 1, max(0, int(cy1 / cell_h)))
                gx2 = min(grid_size - 1, max(0, int(cx2 / cell_w)))
                gy2 = min(grid_size - 1, max(0, int(cy2 / cell_h)))
                # L 形路由
                for gx in range(min(gx1, gx2), max(gx1, gx2) + 1):
                    grid[gy1, gx] += 1
                for gy in range(min(gy1, gy2), max(gy1, gy2) + 1):
                    grid[gy, gx2] += 1

        congested_threshold = max(1, grid.max() // 2)
        congested_cells = int((grid >= congested_threshold).sum())

        return {
            "grid_size": grid_size,
            "grid": grid,
            "max_congestion": int(grid.max()),
            "avg_congestion": round(float(grid.mean()), 4),
            "congestion_std": round(float(grid.std()), 4),
            "congested_cells_count": congested_cells,
        }

    def congestion_penalty(
        self, layout: Layout, grid_size: int = 10
    ) -> float:
        """
        拥塞惩罚 — 最大拥塞值作为惩罚项。

        拥塞越高 → 布线越困难 → 惩罚越大。
        """
        cong = self.congestion_estimate(layout, grid_size)
        return float(cong["max_congestion"])

    # ── Total Cost ──────────────────────────────────────────

    def total_cost(
        self, layout: Layout, grid_size: int = 10
    ) -> Tuple[float, tuple]:
        """
        计算总成本。

        Total = α × HPWL + β × Overlap + γ × Boundary
              + δ × Density + ε × Congestion

        Returns:
            total_cost: 总成本
            components: (wirelength, overlap, boundary, density, congestion_max)
        """
        wl = self.wirelength_cost(layout)
        ov = self.overlap_penalty(layout)
        bd = self.boundary_penalty(layout)
        dn = self.density_penalty(layout)
        cn = self.congestion_penalty(layout, grid_size)

        total = (self.alpha * wl +
                 self.beta * ov +
                 self.gamma * bd +
                 self.delta * dn +
                 self.epsilon * cn)

        return total, (wl, ov, bd, dn, cn)
