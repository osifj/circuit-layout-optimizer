"""
optimizer.py — 模拟退火优化器 (v1.1 EDA 增强版)

核心改进:
- 跳过 fixed 模块（不移动固定 IO/macro）
- 记录 hpwl + congestion 到迭代历史
- 支持 grid_size 参数
"""

import random
import math
import copy
from typing import List, Dict, Any
from .layout import Layout
from .cost import CostFunction


class SimulatedAnnealing:
    """
    模拟退火优化器 (EDA 版)。

    Attributes:
        cost_fn: 成本函数
        initial_temp: 初始温度
        cooling_rate: 降温系数
        max_iter: 最大迭代次数
        min_temp: 最低温度
        move_scale: 移动步长比例
        grid_size: 拥塞估计网格大小
        seed: 随机种子
    """

    def __init__(
        self,
        cost_fn: CostFunction,
        initial_temp: float = 500.0,
        cooling_rate: float = 0.995,
        max_iter: int = 2000,
        min_temp: float = 0.01,
        move_scale: float = 0.2,
        grid_size: int = 10,
        seed: int = 42,
    ):
        self.cost_fn = cost_fn
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.max_iter = max_iter
        self.min_temp = min_temp
        self.move_scale = move_scale
        self.grid_size = grid_size
        self.seed = seed
        self.history: List[Dict[str, Any]] = []

    def optimize(self, layout: Layout, verbose: bool = True) -> Layout:
        """
        模拟退火优化。只移动 movable_modules。
        """
        rng = random.Random(self.seed)

        current = copy.deepcopy(layout)
        current_cost, current_components = self.cost_fn.total_cost(
            current, self.grid_size
        )
        best = copy.deepcopy(current)
        best_cost = current_cost
        best_components = current_components

        temperature = self.initial_temp
        self.history = []

        if not layout.movable_modules:
            print("⚠️ 没有可移动模块 (全部 fixed)，跳过优化")
            return best

        if verbose:
            print(f"\n🔥 模拟退火开始 (T₀={self.initial_temp}, "
                  f"cooldown={self.cooling_rate}, max_iter={self.max_iter})")
            print(f"   初始 cost = {current_cost:.2f}  "
                  f"HPWL={current_components[0]:.2f}  "
                  f"重叠={current_components[1]:.2f}  "
                  f"拥塞={current_components[4]:.0f}")

        for iteration in range(self.max_iter):
            if temperature < self.min_temp:
                if verbose:
                    print(f"   温度降至 {temperature:.4f}，停止")
                break

            # Step 1: 只扰动 movable 模块
            candidate = copy.deepcopy(current)
            movable = candidate.movable_modules
            if not movable:
                break

            mod_idx = rng.randint(0, len(movable) - 1)
            mod = movable[mod_idx]

            max_move = max(candidate.chip_width, candidate.chip_height) * self.move_scale
            move_range = max_move * (temperature / self.initial_temp)
            dx = rng.uniform(-move_range, move_range)
            dy = rng.uniform(-move_range, move_range)
            mod.x += dx
            mod.y += dy

            # Step 2: 计算新 cost
            new_cost, new_components = self.cost_fn.total_cost(
                candidate, self.grid_size
            )

            # Step 3: 接受判断
            delta = new_cost - current_cost
            accepted = False
            if delta <= 0:
                accepted = True
            else:
                prob = math.exp(-delta / temperature)
                if rng.random() < prob:
                    accepted = True

            if accepted:
                current = candidate
                current_cost = new_cost
                current_components = new_components
                if current_cost < best_cost:
                    best = copy.deepcopy(current)
                    best_cost = current_cost
                    best_components = current_components

            # 记录
            current_hpwl = self.cost_fn.hpwl(current)
            cong = self.cost_fn.congestion_estimate(current, self.grid_size)

            self.history.append({
                "iteration": iteration,
                "temperature": round(temperature, 4),
                "current_cost": round(current_cost, 4),
                "best_cost": round(best_cost, 4),
                "wirelength": round(current_components[0], 4),
                "hpwl": round(current_hpwl, 4),
                "overlap": round(current_components[1], 4),
                "boundary": round(current_components[2], 4),
                "density": round(current_components[3], 4),
                "congestion": int(current_components[4]),
                "accepted": accepted,
            })

            temperature *= self.cooling_rate

            if verbose and iteration % max(1, self.max_iter // 5) == 0:
                print(f"   iter {iteration:5d}  T={temperature:.2f}  "
                      f"cost={current_cost:.2f}  best={best_cost:.2f}  "
                      f"acc={'✓' if accepted else '✗'}")

        if verbose:
            print(f"\n✅ 优化完成: best_cost = {best_cost:.2f}")
            print(f"   HPWL={best_components[0]:.2f}  重叠={best_components[1]:.2f}  "
                  f"边界={best_components[2]:.2f}  拥塞={best_components[4]:.0f}")

        return best
