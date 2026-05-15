# -*- coding: utf-8 -*-
"""
test_ending_reachability.py —— 全结局可达性验证
覆盖 M6 全结局可达性测试：逐个验证 8 结局的判定条件正确性 + 优先级顺序。
依据 design.md §2.5 结局触发条件表 + story_engine.check_ending() 实现逻辑。
"""
import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from state_manager import StateManager
from story_engine import StoryEngine


class TestEndingReachability(unittest.TestCase):
    """逐个验证 8 结局的变量判定条件"""

    def setUp(self):
        self.sm = StateManager()
        self.st = StoryEngine(self.sm)

    def _reset_flags(self):
        self.st.flags.clear()

    def _set_vars(self, curiosity=None, sanity=None, trust=None,
                   survival_will=None, loyalty=None):
        mappings = {
            "curiosity": curiosity, "sanity": sanity, "trust": trust,
            "survival_will": survival_will, "loyalty": loyalty
        }
        for k, v in mappings.items():
            if v is not None:
                self.sm.change(k, v - self.sm.get(k))

    def _set_flags(self, **kwargs):
        self.st.flags.update(kwargs)

    # ---- 结局 G：荒诞 ----

    def test_ending_G_all_flags(self):
        self._reset_flags()
        self._set_flags(found_diary_page=True,
                        found_wangchao_drawing=True,
                        found_dad_logbook=True)
        self.assertEqual(self.st.check_ending(), "G")

    def test_ending_G_missing_diary(self):
        self._reset_flags()
        self._set_flags(found_wangchao_drawing=True,
                        found_dad_logbook=True)
        self.assertNotEqual(self.st.check_ending(), "G")

    def test_ending_G_missing_drawing(self):
        self._reset_flags()
        self._set_flags(found_diary_page=True,
                        found_dad_logbook=True)
        self.assertNotEqual(self.st.check_ending(), "G")

    def test_ending_G_missing_logbook(self):
        self._reset_flags()
        self._set_flags(found_diary_page=True,
                        found_wangchao_drawing=True)
        self.assertNotEqual(self.st.check_ending(), "G")

    # ---- 结局 F：被背叛 ----

    def test_ending_F_minimal(self):
        self._reset_flags()
        self._set_vars(curiosity=7, sanity=3, trust=3, loyalty=2)
        self.assertEqual(self.st.check_ending(), "F")

    def test_ending_F_extreme(self):
        self._reset_flags()
        self._set_vars(curiosity=10, sanity=0, trust=0, loyalty=0)
        self.assertEqual(self.st.check_ending(), "F")

    def test_ending_F_blocked_by_trust(self):
        self._reset_flags()
        self._set_vars(curiosity=7, sanity=3, trust=4, loyalty=2)
        self.assertNotEqual(self.st.check_ending(), "F")

    def test_ending_F_blocked_by_loyalty(self):
        self._reset_flags()
        self._set_vars(curiosity=7, sanity=3, trust=3, loyalty=3)
        self.assertNotEqual(self.st.check_ending(), "F")

    def test_ending_F_blocked_by_sanity_high(self):
        self._reset_flags()
        self._set_vars(curiosity=7, sanity=4, trust=3, loyalty=2)
        self.assertNotEqual(self.st.check_ending(), "F")

    def test_ending_F_blocked_by_curiosity_low(self):
        self._reset_flags()
        self._set_vars(curiosity=6, sanity=3, trust=3, loyalty=2)
        self.assertNotEqual(self.st.check_ending(), "F")

    # ---- 结局 A：疯狂 ----

    def test_ending_A_with_trust(self):
        self._reset_flags()
        self._set_vars(curiosity=7, sanity=3, trust=5, loyalty=2)
        self.assertEqual(self.st.check_ending(), "A")

    def test_ending_A_with_loyalty(self):
        self._reset_flags()
        self._set_vars(curiosity=7, sanity=3, trust=2, loyalty=3)
        self.assertEqual(self.st.check_ending(), "A")

    def test_ending_A_blocked_by_sanity_high(self):
        self._reset_flags()
        self._set_vars(curiosity=7, sanity=4, trust=5, loyalty=3)
        self.assertNotEqual(self.st.check_ending(), "A")

    def test_ending_A_blocked_by_curiosity_low(self):
        self._reset_flags()
        self._set_vars(curiosity=6, sanity=3, trust=5, loyalty=3)
        self.assertNotEqual(self.st.check_ending(), "A")

    # ---- 结局 E：提前逃离 ----

    def test_ending_E_path_conditions(self):
        """验证 ch05 提前逃离选项的条件判定：sw≥8, s≤4, t≤4"""
        self._reset_flags()
        self._set_vars(survival_will=8, sanity=4, trust=4)
        cond = {"survival_will": {"min": 8}, "sanity": {"max": 4}, "trust": {"max": 4}}
        self.assertTrue(self.sm.check_condition(cond))

    def test_ending_E_path_blocked_by_survival_will(self):
        self._reset_flags()
        self._set_vars(survival_will=7, sanity=4, trust=4)
        cond = {"survival_will": {"min": 8}, "sanity": {"max": 4}, "trust": {"max": 4}}
        self.assertFalse(self.sm.check_condition(cond))

    def test_ending_E_path_blocked_by_sanity(self):
        self._reset_flags()
        self._set_vars(survival_will=8, sanity=5, trust=4)
        cond = {"survival_will": {"min": 8}, "sanity": {"max": 4}, "trust": {"max": 4}}
        self.assertFalse(self.sm.check_condition(cond))

    def test_ending_E_path_blocked_by_trust(self):
        self._reset_flags()
        self._set_vars(survival_will=8, sanity=4, trust=5)
        cond = {"survival_will": {"min": 8}, "sanity": {"max": 4}, "trust": {"max": 4}}
        self.assertFalse(self.sm.check_condition(cond))

    # ---- 结局 B：一起逃离 ----

    def test_ending_B_minimal(self):
        self._reset_flags()
        self._set_vars(curiosity=6, sanity=6, trust=7, loyalty=4)
        self.assertEqual(self.st.check_ending(), "B")

    def test_ending_B_extreme(self):
        self._reset_flags()
        self._set_vars(curiosity=10, sanity=10, trust=10, loyalty=5)
        self.assertEqual(self.st.check_ending(), "B")

    def test_ending_B_blocked_by_trust_low(self):
        self._reset_flags()
        self._set_vars(curiosity=6, sanity=6, trust=6, loyalty=4)
        self.assertNotEqual(self.st.check_ending(), "B")

    def test_ending_B_blocked_by_loyalty_low(self):
        self._reset_flags()
        self._set_vars(curiosity=6, sanity=6, trust=7, loyalty=3)
        self.assertNotEqual(self.st.check_ending(), "B")

    def test_ending_B_blocked_by_curiosity_low(self):
        self._reset_flags()
        self._set_vars(curiosity=5, sanity=6, trust=7, loyalty=4)
        self.assertNotEqual(self.st.check_ending(), "B")

    def test_ending_B_blocked_by_sanity_low(self):
        self._reset_flags()
        self._set_vars(curiosity=6, sanity=5, trust=7, loyalty=4)
        self.assertNotEqual(self.st.check_ending(), "B")

    # ---- 结局 D：被杀 ----

    def test_ending_D_minimal(self):
        self._reset_flags()
        self._set_vars(curiosity=3, sanity=6, trust=3, loyalty=2)
        self.assertEqual(self.st.check_ending(), "D")

    def test_ending_D_extreme(self):
        self._reset_flags()
        self._set_vars(curiosity=0, sanity=10, trust=0, loyalty=0)
        self.assertEqual(self.st.check_ending(), "D")

    def test_ending_D_blocked_by_curiosity_high(self):
        self._reset_flags()
        self._set_vars(curiosity=4, sanity=6, trust=3, loyalty=2)
        self.assertNotEqual(self.st.check_ending(), "D")

    def test_ending_D_blocked_by_trust_high(self):
        self._reset_flags()
        self._set_vars(curiosity=3, sanity=6, trust=4, loyalty=2)
        self.assertNotEqual(self.st.check_ending(), "D")

    # ---- 结局 C：平安离开 ----

    def test_ending_C_minimal(self):
        self._reset_flags()
        self._set_vars(curiosity=3, sanity=6)
        self.assertEqual(self.st.check_ending(), "C")

    def test_ending_C_with_trust(self):
        self._reset_flags()
        self._set_vars(curiosity=3, sanity=6, trust=5, loyalty=4)
        self.assertEqual(self.st.check_ending(), "C")

    def test_ending_C_blocked_by_curiosity_high(self):
        self._reset_flags()
        self._set_vars(curiosity=4, sanity=6)
        self.assertNotEqual(self.st.check_ending(), "C")

    def test_ending_C_blocked_by_sanity_low(self):
        self._reset_flags()
        self._set_vars(curiosity=3, sanity=5)
        self.assertNotEqual(self.st.check_ending(), "C")

    # ---- 优先级测试 ----

    def test_priority_G_overrides_all(self):
        """G（flag三件）优先于任何变量组合"""
        self._reset_flags()
        self._set_flags(found_diary_page=True,
                        found_wangchao_drawing=True,
                        found_dad_logbook=True)
        self._set_vars(curiosity=7, sanity=3, trust=3, loyalty=2)
        self.assertEqual(self.st.check_ending(), "G")

    def test_priority_F_over_A(self):
        """F（t≤3且l≤2）优先于 A"""
        self._reset_flags()
        self._set_vars(curiosity=7, sanity=3, trust=3, loyalty=2)
        self.assertEqual(self.st.check_ending(), "F")

    def test_priority_A_over_B(self):
        """A 优先于 B（sanity≤3 vs sanity≥6）"""
        self._reset_flags()
        self._set_vars(curiosity=7, sanity=3, trust=5, loyalty=3)
        self.assertEqual(self.st.check_ending(), "A")

    def test_priority_D_over_C(self):
        """D（c≤3, s≥6, t≤3, l≤2）优先于 C（c≤3, s≥6）"""
        self._reset_flags()
        self._set_vars(curiosity=3, sanity=6, trust=3, loyalty=2)
        self.assertEqual(self.st.check_ending(), "D")

    def test_no_ending(self):
        """中间状态不触发任何结局"""
        self._reset_flags()
        self._set_vars(curiosity=5, sanity=5, trust=5, loyalty=3)
        self.assertIsNone(self.st.check_ending())

    # ---- 结局节点存在性 ----

    def test_all_ending_nodes_exist(self):
        """8 结局节点均在章节 JSON 中"""
        self.st.load_chapter(6)
        endings = [
            "ch06_ending_G", "ch06_ending_death", "ch06_ending_F",
            "ch06_ending_A", "ch06_ending_B", "ch06_ending_C", "ch06_ending_D"
        ]
        for eid in endings:
            self.assertIn(eid, self.st.nodes, f"结局节点 {eid} 应存在于 ch06")

    def test_ending_E_nodes_exist(self):
        """E 结局链在 ch05 中"""
        self.st.load_chapter(5)
        for eid in ["ch05_ending_e", "ch05_ending_e_02", "ch05_ending_e_03"]:
            self.assertIn(eid, self.st.nodes, f"结局节点 {eid} 应存在于 ch05")

    def test_ending_chains_have_flag(self):
        """所有结局链节点标记 is_ending_chain: true（ch06_ending_check 是路由节点，非链节点）"""
        self.st.load_chapter(6)
        ending_nodes = [n for nid, n in self.st.nodes.items()
                        if nid.startswith("ch06_ending_") and nid != "ch06_ending_check"]
        self.assertGreater(len(ending_nodes), 0, "应有结局链节点")
        for n in ending_nodes:
            self.assertTrue(n.get("is_ending_chain"),
                            f"{n['node_id']} 应标记 is_ending_chain: true")


if __name__ == "__main__":
    unittest.main()
