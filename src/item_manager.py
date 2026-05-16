# -*- coding: utf-8 -*-
"""
item_manager.py —— 物品管理器
管理玩家随身物品：获取/移除/检查/携带效果/消耗/销毁。
详见 design.md §2.7
"""

import json, os


class ItemManager:
    """物品增删改查 + 携带效果叠加"""

    def __init__(self, data_path: str = "data/items.json"):
        self._data_path = data_path
        self._defs = {}       # item_id → {name, desc, carry_effects, ...}
        self._inventory = {}  # item_id → True
        self._load_defs()

    def _load_defs(self):
        if not os.path.exists(self._data_path):
            return
        with open(self._data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item_id, info in data.items():
            self._defs[item_id] = info
        # 写入后验证
        with open(self._data_path, "r", encoding="utf-8") as f:
            json.load(f)

    def acquire(self, item_id: str) -> bool:
        """获得物品。已存在返回 False，新获得返回 True。"""
        if item_id not in self._defs:
            return False
        if item_id in self._inventory:
            return False
        self._inventory[item_id] = True
        return True

    def remove(self, item_id: str) -> bool:
        """移除物品。"""
        if item_id in self._inventory:
            del self._inventory[item_id]
            return True
        return False

    def has(self, item_id: str) -> bool:
        return item_id in self._inventory

    def get_carry_effects(self) -> dict:
        """汇总所有携带物品的变量效果（name → delta）。"""
        result = {}
        for item_id in self._inventory:
            info = self._defs.get(item_id, {})
            effects = info.get("carry_effects")
            if effects:
                for var_name, delta in effects.items():
                    result[var_name] = result.get(var_name, 0) + delta
        return result

    def get_info(self, item_id: str) -> dict:
        """获取物品定义信息。"""
        return self._defs.get(item_id, {})

    def get_all_items(self) -> list:
        """返回当前持有的所有物品的展示列表。"""
        result = []
        for item_id in self._inventory:
            info = self._defs.get(item_id, {})
            effects = info.get("carry_effects", {})
            eff_parts = []
            for k, v in effects.items():
                sign = "+" if v > 0 else ""
                eff_parts.append(f"{k}{sign}{v}")
            desc = info.get("desc", "")
            if eff_parts:
                desc = desc + f"（{'，'.join(eff_parts)}）"
            result.append({"id": item_id, "name": info.get("name", item_id), "desc": desc})
        return result

    def consume(self, item_id: str):
        """消耗物品（销毁+触发临时任务回调）。返回 destroy_quest id 或 None。"""
        info = self._defs.get(item_id, {})
        quest = info.get("destroy_quest")
        self._inventory.pop(item_id, None)
        return quest

    def destroy(self, item_id: str) -> bool:
        """直接销毁物品。"""
        return self.remove(item_id)

    def to_dict(self) -> dict:
        return list(self._inventory.keys())

    def from_dict(self, data):
        self._inventory.clear()
        if isinstance(data, list):
            for item_id in data:
                if item_id in self._defs:
                    self._inventory[item_id] = True
        elif isinstance(data, dict):
            for item_id, v in data.items():
                if v and item_id in self._defs:
                    self._inventory[item_id] = True

    def reset(self):
        self._inventory.clear()
