# -*- coding: utf-8 -*-
"""
save_manager.py —— 存档/读档管理器
4 手动存档位 + 1 自动存档位，JSON 格式读写。
详见 design.md 2.6 / 4.3
"""

import json, os
from datetime import datetime


class SaveManager:
    """存档文件的创建、读取、删除"""

    def __init__(self, save_dir: str = "data/saves"):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def _path(self, slot) -> str:
        return os.path.join(self.save_dir, f"save_{slot}.json")

    def save(self, slot, state_mgr, current_node: str,
             chapter: int, day: int, history: list, flags: dict,
             sound_state: dict = None, items: list = None):
        data = {
            "save_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "current_node": current_node,
            "chapter": chapter,
            "day": day,
            "variables": state_mgr.to_dict(),
            "history": history,
            "flags": flags,
            "sound_state": sound_state or {},
            "items": items or [],
        }
        with open(self._path(slot), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, slot) -> dict:
        path = self._path(slot)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_info(self, slot) -> dict:
        path = self._path(slot)
        if not os.path.exists(path):
            return {"exists": False}
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "exists": True,
            "save_time": data.get("save_time", "未知"),
            "day": data.get("day", 1),
            "chapter": data.get("chapter", 1),
        }
