# -*- coding: utf-8 -*-
"""
state_manager.py —— 变量管理器
管理 5 个核心状态变量：curiosity / sanity / trust / survival_will / loyalty
详见 design.md 2.3
"""

class StateManager:
    """变量增删改查 + 条件判定 + 隐晦描述"""

    # (中文名, 显隐, 最小值, 最大值, 初始值)
    SPEC = {
        "curiosity":     ("好奇心",   True,  0, 10, 0),
        "sanity":        ("理智",     True,  0, 10, 10),
        "trust":         ("信任",     True,  0, 10, 4),
        "survival_will": ("生存意愿", False, 0, 10, 6),
        "loyalty":       ("忠诚",     False, 0, 5,  3),
    }

    def __init__(self):
        self._data = {}
        self.reset()

    def reset(self):
        for k, (_, _, _, _, default) in self.SPEC.items():
            self._data[k] = default

    # ---- CRUD ----

    def get(self, key: str) -> int:
        return self._data.get(key, 0)

    def get_all(self) -> dict:
        return dict(self._data)

    def get_visible(self) -> dict:
        return {k: v for k, v in self._data.items() if self.SPEC[k][1]}

    def change(self, key: str, delta: int) -> int:
        _, _, lo, hi, _ = self.SPEC[key]
        v = max(lo, min(hi, self._data[key] + delta))
        self._data[key] = v
        return v

    def apply_effects(self, effects: dict):
        if effects:
            for k, d in effects.items():
                if d != 0:
                    self.change(k, d)

    def to_dict(self) -> dict:
        return dict(self._data)

    def from_dict(self, data: dict):
        for k in self.SPEC:
            if k in data:
                self._data[k] = data[k]

    # ---- 条件判定 ----

    def check_condition(self, conditions) -> bool:
        if conditions is None:
            return True
        for key, constraint in conditions.items():
            cur = self._data.get(key, 0)
            if "min" in constraint and cur < constraint["min"]:
                return False
            if "max" in constraint and cur > constraint["max"]:
                return False
            if "eq"  in constraint and cur != constraint["eq"]:
                return False
        return True

    # ---- 隐晦描述（按 day 分段，避免早期天出现预知性文本） ----

    def describe(self, key: str, day: int = None) -> str:
        v = self._data.get(key)
        if v is None:
            return "——"
        if day is None:
            day = 99  # 未传天数时用最成熟的描述

        if key == "curiosity":
            if v <= 2: return "我对这里发生的事没太大兴趣。"
            if v <= 4: return "我开始留意一些细节了。"
            if v <= 6: return "这里肯定有什么。我必须弄清楚。"
            if v <= 8: return "我已经没法不去想了。"
            if day <= 6: return "有些答案不重要了。但问题还在。"
            return "我不需要答案。我就是答案的一部分。"

        if key == "sanity":
            if v <= 2: return "我握笔的手在发抖。这不是冷的。" if day <= 5 else "我已经分不清了。但分不清好像也没那么糟。"
            if v <= 4: return "还能思考。还能克制。"
            if v <= 6: return "大体上我还能正常工作。"
            if v <= 8: return "我没事。真的。"
            return "我没事。真的。"

        if key == "trust":
            if v <= 2: return "我们只是同事。"
            if v <= 4: return "他只是个称职的守塔人。仅此而已。" if day <= 6 else "不能相信他。他在隐瞒什么。"
            if v <= 6: return "他还是一样地沉默。" if day <= 3 else "他沉默，但至少现在——他不会害我。"
            if v <= 8: return "这个人在我身边让我觉得安心。"
            return "他是我在这里唯一的锚。"

        return "——"
