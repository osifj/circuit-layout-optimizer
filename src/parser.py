"""
parser.py — JSON 输入解析模块 (v1.1 EDA 增强版)

支持:
- 旧 net 格式: {"source": "A", "target": "B", "weight": 1.0}
- 新 net 格式: {"name": "net1", "pins": ["A","B","C"], "weight": 1.0}
- module 扩展: type (macro|standard_cell), fixed (bool), x/y 预设坐标
"""

import json
from pathlib import Path
from typing import Dict, Any


def parse_input(filepath: str) -> Dict[str, Any]:
    """
    读取并解析 JSON 输入文件。

    兼容 net 格式:
      - 旧: {"source": "A", "target": "B", "weight": 1.0}
      - 新: {"name": "net1", "pins": ["A","B","C"], "weight": 1.0}

    模块可选扩展字段:
      - type: "macro" | "standard_cell" (默认 "macro")
      - fixed: true | false (默认 false)
      - x, y: 固定模块预设坐标
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"输入文件不存在: {filepath}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    required = ["chip_width", "chip_height", "modules", "nets"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"缺少必要字段: {missing}")

    if not isinstance(data["modules"], list) or len(data["modules"]) == 0:
        raise ValueError("modules 必须是非空列表")

    macro_count = 0
    sc_count = 0
    fixed_count = 0
    for i, mod in enumerate(data["modules"]):
        for field in ["id", "width", "height"]:
            if field not in mod:
                raise ValueError(f"modules[{i}] 缺少字段: {field}")
        # 补全默认值
        mod.setdefault("type", "macro")
        mod.setdefault("fixed", False)
        mod.setdefault("x", 0.0)
        mod.setdefault("y", 0.0)
        if mod["type"] == "macro":
            macro_count += 1
        elif mod["type"] == "standard_cell":
            sc_count += 1
        if mod["fixed"]:
            fixed_count += 1

    # 标准化 nets
    if "nets" not in data:
        data["nets"] = []

    normalized_nets = []
    pin_net_count = 0
    for i, net in enumerate(data["nets"]):
        if "pins" in net:
            normalized_nets.append({
                "pins": net["pins"],
                "weight": net.get("weight", 1.0),
                "name": net.get("name", f"net_{i}"),
            })
            if len(net["pins"]) > 2:
                pin_net_count += 1
        elif "source" in net and "target" in net:
            normalized_nets.append({
                "pins": [net["source"], net["target"]],
                "weight": net.get("weight", 1.0),
                "name": net.get("name", f"net_{i}"),
            })
        else:
            raise ValueError(
                f"nets[{i}] 格式错误: 需要 'pins' 或 'source'+'target'"
            )

    data["nets"] = normalized_nets

    parts = [f"{len(data['modules'])} 个模块"]
    if macro_count > 0:
        parts.append(f"{macro_count} macro")
    if sc_count > 0:
        parts.append(f"{sc_count} standard_cell")
    if fixed_count > 0:
        parts.append(f"{fixed_count} fixed")
    parts.append(f"{len(normalized_nets)} 条连线")
    if pin_net_count > 0:
        parts.append(f"(含 {pin_net_count} 条多端 net)")

    print(f"✅ 成功加载: {', '.join(parts)}")
    print(f"   芯片尺寸: {data['chip_width']} × {data['chip_height']}")

    return data
