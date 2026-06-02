"""
layout.py — 核心数据结构 (v1.1 EDA 增强版)

Module: 增加 type, fixed, x/y 预设坐标
Net:    增加 pins (多端), name
Layout: 增加 movable_modules / fixed_modules 属性
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Module:
    """
    电路模块。

    Attributes:
        id: 模块唯一标识
        width: 模块宽度
        height: 模块高度
        x: 左下角 x 坐标
        y: 左下角 y 坐标
        type: "macro" | "standard_cell" (默认 macro)
        fixed: 是否为固定模块 (优化中不可移动)
        pins: 所属 net 的 pin 位置 (可选, 默认中心点)
    """
    id: str
    width: float
    height: float
    x: float = 0.0
    y: float = 0.0
    module_type: str = "macro"
    fixed: bool = False

    @property
    def center(self) -> Tuple[float, float]:
        return (self.x + self.width / 2, self.y + self.height / 2)

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def is_macro(self) -> bool:
        return self.module_type == "macro"

    @property
    def is_standard_cell(self) -> bool:
        return self.module_type == "standard_cell"

    def overlaps_with(self, other: "Module") -> bool:
        return not (
            self.x + self.width <= other.x
            or other.x + other.width <= self.x
            or self.y + self.height <= other.y
            or other.y + other.height <= self.y
        )

    def overlap_area(self, other: "Module") -> float:
        if not self.overlaps_with(other):
            return 0.0
        dx = min(self.x + self.width, other.x + other.width) - max(self.x, other.x)
        dy = min(self.y + self.height, other.y + other.height) - max(self.y, other.y)
        return max(0.0, dx) * max(0.0, dy)

    def is_within_chip(self, chip_w: float, chip_h: float) -> bool:
        return (
            self.x >= 0
            and self.y >= 0
            and self.x + self.width <= chip_w
            and self.y + self.height <= chip_h
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "x": round(self.x, 4),
            "y": round(self.y, 4),
            "width": self.width,
            "height": self.height,
            "type": self.module_type,
            "fixed": self.fixed,
        }


@dataclass
class Net:
    """
    电路连线（支持多端 net）。

    Attributes:
        name: net 名称
        pins: 连接的模块 ID 列表
        weight: 连线权重
    """
    name: str
    pins: List[str] = field(default_factory=list)
    weight: float = 1.0

    @property
    def is_multi_pin(self) -> bool:
        return len(self.pins) > 2

    @property
    def pin_count(self) -> int:
        return len(self.pins)


@dataclass
class Layout:
    """
    一次完整布局。

    Attributes:
        chip_width: 芯片宽度
        chip_height: 芯片高度
        modules: 模块列表
        nets: 连线列表
    """
    chip_width: float
    chip_height: float
    modules: List[Module] = field(default_factory=list)
    nets: List[Net] = field(default_factory=list)

    def module_by_id(self, module_id: str) -> Module:
        for mod in self.modules:
            if mod.id == module_id:
                return mod
        raise KeyError(f"模块未找到: {module_id}")

    @property
    def movable_modules(self) -> List[Module]:
        """可移动模块（非 fixed）。"""
        return [m for m in self.modules if not m.fixed]

    @property
    def fixed_modules(self) -> List[Module]:
        """固定模块。"""
        return [m for m in self.modules if m.fixed]

    @property
    def macros(self) -> List[Module]:
        return [m for m in self.modules if m.is_macro]

    @property
    def standard_cells(self) -> List[Module]:
        return [m for m in self.modules if m.is_standard_cell]

    @property
    def total_module_area(self) -> float:
        return sum(m.area for m in self.modules)

    @property
    def chip_area(self) -> float:
        return self.chip_width * self.chip_height

    @property
    def area_utilization(self) -> float:
        return self.total_module_area / self.chip_area

    def randomize_positions(self, seed: int = 42):
        """随机初始化所有非固定模块位置。"""
        import random
        rng = random.Random(seed)
        for mod in self.movable_modules:
            max_x = max(0, self.chip_width - mod.width)
            max_y = max(0, self.chip_height - mod.height)
            mod.x = rng.uniform(0, max_x)
            mod.y = rng.uniform(0, max_y)

    def to_result(self, cost: float, wirelength: float,
                  overlap: float, boundary: float, density: float,
                  hpwl: float = 0.0, congestion: dict = None,
                  max_congestion: int = 0,
                  avg_congestion: float = 0.0) -> dict:
        """输出最终结果字典，包含全部 EDA 指标。"""
        metrics = {
            "total_wirelength": round(wirelength, 4),
            "hpwl": round(hpwl, 4),
            "overlap_penalty": round(overlap, 4),
            "boundary_penalty": round(boundary, 4),
            "density_penalty": round(density, 4),
            "total_cost": round(cost, 4),
            "area_utilization": round(self.area_utilization, 4),
            "num_modules": len(self.modules),
            "num_macros": len(self.macros),
            "num_standard_cells": len(self.standard_cells),
            "num_fixed_modules": len(self.fixed_modules),
            "num_nets": len(self.nets),
            "max_congestion": max_congestion,
            "avg_congestion": round(avg_congestion, 4),
        }
        if congestion:
            metrics["congestion_grid_size"] = congestion.get("grid_size", 0)
            metrics["congestion_std"] = float(congestion.get("congestion_std", 0))
        return {
            "modules": [m.to_dict() for m in self.modules],
            "metrics": metrics,
        }
