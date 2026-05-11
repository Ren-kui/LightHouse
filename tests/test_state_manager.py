# -*- coding: utf-8 -*-
"""
test_state_manager.py —— 变量管理器单元测试
覆盖：初始化 / 边界 / CRUD / 条件判定 / 描述 / 序列化
纯标准库 unittest，零外部依赖。
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from state_manager import StateManager


class TestStateManager(unittest.TestCase):

    def setUp(self):
        self.sm = StateManager()

    # ---- 初始化 ----

    def test_default_values(self):
        self.assertEqual(self.sm.get("curiosity"), 0)
        self.assertEqual(self.sm.get("sanity"), 10)
        self.assertEqual(self.sm.get("trust"), 5)
        self.assertEqual(self.sm.get("survival_will"), 7)
        self.assertEqual(self.sm.get("loyalty"), 3)

    def test_all_vars_present(self):
        data = self.sm.get_all()
        self.assertSetEqual(set(data.keys()), set(StateManager.SPEC.keys()))

    # ---- 边界保护 ----

    def test_change_clamp_min(self):
        self.sm.change("curiosity", -5)
        self.assertEqual(self.sm.get("curiosity"), 0)

    def test_change_clamp_max(self):
        self.sm.change("sanity", 100)
        self.assertEqual(self.sm.get("sanity"), 10)

    def test_change_normal(self):
        self.sm.change("trust", 2)
        self.assertEqual(self.sm.get("trust"), 7)

    def test_change_returns_new_value(self):
        result = self.sm.change("loyalty", 1)
        self.assertEqual(result, 4)

    # ---- apply_effects ----

    def test_apply_effects_batch(self):
        effects = {"curiosity": 3, "sanity": -2, "trust": 1}
        self.sm.apply_effects(effects)
        self.assertEqual(self.sm.get("curiosity"), 3)
        self.assertEqual(self.sm.get("sanity"), 8)
        self.assertEqual(self.sm.get("trust"), 6)

    def test_apply_effects_skip_zero(self):
        effects = {"curiosity": 0, "trust": 1}
        self.sm.apply_effects(effects)
        self.assertEqual(self.sm.get("curiosity"), 0)
        self.assertEqual(self.sm.get("trust"), 6)

    def test_apply_effects_none(self):
        self.sm.apply_effects(None)
        self.assertEqual(self.sm.get("curiosity"), 0)

    # ---- 条件判定 ----

    def test_condition_none_true(self):
        self.assertTrue(self.sm.check_condition(None))

    def test_condition_min_pass(self):
        self.sm.change("curiosity", 5)
        self.assertTrue(self.sm.check_condition({"curiosity": {"min": 3}}))

    def test_condition_min_fail(self):
        self.assertFalse(self.sm.check_condition({"curiosity": {"min": 3}}))

    def test_condition_max_pass(self):
        self.sm.change("sanity", -5)  # sanity 10 → 5 <= 8
        self.assertTrue(self.sm.check_condition({"sanity": {"max": 8}}))

    def test_condition_eq_pass(self):
        self.sm.change("trust", 0)  # trust stays at default 5
        self.assertTrue(self.sm.check_condition({"trust": {"eq": 5}}))

    def test_condition_eq_fail(self):
        self.assertFalse(self.sm.check_condition({"trust": {"eq": 10}}))

    def test_condition_multi_all_pass(self):
        self.sm.change("curiosity", 5)  # 0 → 5 >= 3
        self.sm.change("sanity", -5)    # 10 → 5 <= 8
        self.assertTrue(self.sm.check_condition({
            "curiosity": {"min": 3},
            "sanity": {"max": 8},
        }))

    def test_condition_multi_one_fail(self):
        self.sm.change("curiosity", 1)
        self.assertFalse(self.sm.check_condition({
            "curiosity": {"min": 3},
            "sanity": {"max": 8},
        }))

    # ---- 描述 ----

    def test_describe_unknown_key(self):
        self.assertEqual(self.sm.describe("nope"), "——")

    def test_describe_curiosity_band(self):
        self.assertEqual(self.sm.describe("curiosity"), "我对这里发生的事没太大兴趣。")
        self.sm.change("curiosity", 5)
        self.assertIn("这里肯定有什么", self.sm.describe("curiosity"))

    def test_describe_sanity_band(self):
        self.assertEqual(self.sm.describe("sanity"), "我没事。真的。")

    def test_describe_trust_band(self):
        self.assertEqual(self.sm.describe("trust"), "他沉默，但他不会害我。至少现在不会。")

    # ---- 显隐分离 ----

    def test_get_visible_excludes_hidden(self):
        visible = self.sm.get_visible()
        self.assertIn("curiosity", visible)
        self.assertIn("sanity", visible)
        self.assertIn("trust", visible)
        self.assertNotIn("survival_will", visible)
        self.assertNotIn("loyalty", visible)

    # ---- 序列化 ----

    def test_to_dict_from_dict_roundtrip(self):
        self.sm.change("curiosity", 7)   # 0 + 7 = 7
        self.sm.change("trust", -3)      # 5 - 3 = 2
        data = self.sm.to_dict()
        sm2 = StateManager()
        sm2.from_dict(data)
        self.assertEqual(sm2.get("curiosity"), 7)
        self.assertEqual(sm2.get("trust"), 2)
        self.assertEqual(sm2.get("sanity"), 10)

    def test_from_dict_partial(self):
        sm2 = StateManager()
        sm2.from_dict({"curiosity": 5})
        self.assertEqual(sm2.get("curiosity"), 5)
        self.assertEqual(sm2.get("sanity"), 10)  # 未传入，保持默认

    # ---- 重置 ----

    def test_reset(self):
        self.sm.change("curiosity", 8)
        self.sm.change("sanity", 1)
        self.sm.reset()
        self.assertEqual(self.sm.get("curiosity"), 0)
        self.assertEqual(self.sm.get("sanity"), 10)


if __name__ == "__main__":
    unittest.main()
