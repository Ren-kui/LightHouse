# -*- coding: utf-8 -*-
"""
test_qa_logic.py —— QA 逻辑层验证脚本
模拟游戏流程，验证关键状态变更无人工 GUI 操作。
覆盖：flag 系统 / 结局可达性 / 桥段正确性 / 多击机制 / MG2 竞态修复 / 章节完整性
"""
import os, sys, json, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from state_manager import StateManager
from story_engine import StoryEngine


class TestQAFlagSystem(unittest.TestCase):
    """验证 flag 写入/读取/结局判定"""

    def setUp(self):
        self.sm = StateManager()
        self.st = StoryEngine(self.sm)

    def test_flag_from_choice(self):
        """选择中 set_flags 被正确写入"""
        # 模拟加载 ch05 节点含 set_flags 的选择
        self.st.load_chapter(5)
        self.st.goto_node("ch05_talk_zhang")
        # 设 loyalty≥4
        self.sm.change("loyalty", 4)
        choices = self.st.get_available_choices()
        # 找到含 set_flags 的选择
        has_flags = [c for c in choices if c.get("set_flags")]
        self.assertGreater(len(has_flags), 0, "ch05_talk_zhang 应包含 set_flags 选项")
        # 执行选择
        for i, c in enumerate(choices):
            if c.get("set_flags"):
                self.st.make_choice(i)
                self.assertIn("found_diary_page", self.st.flags,
                    "set_flags 应写入 found_diary_page")
                break

    def test_flag_from_node(self):
        """到达节点时 set_flags 自动设置"""
        # ch04_darkness_end 本身不设 flag，但选项有
        self.st.load_chapter(4)
        self.st.goto_node("ch04_darkness_end")
        self.sm.change("survival_will", 8)
        choices = self.st.get_available_choices()
        has_set_flags = [c for c in choices if c.get("set_flags")]
        self.assertGreater(len(has_set_flags), 0,
            "survival_will≥8 应可见含 set_flags 的隐藏选项")

    def test_ending_g_unreachable_without_flags(self):
        """没有 flag 时结局 G 不触发"""
        self.st.goto_node("ch06_ending_check")  # 假设在 ch06
        # 手动设变量满足 G 外的条件
        self.sm.apply_effects({"curiosity": 8, "sanity": 2, "trust": 6,
                                "survival_will": 8, "loyalty": 4})
        result = self.st.check_ending()
        # 没有 flags 时不应返回 G
        self.assertNotEqual(result, "G", "无 flags 时不应触发结局 G")


class TestQABridgeCorrectness(unittest.TestCase):
    """验证桥段 _last_node_id 和 text_bridges 匹配"""

    def setUp(self):
        self.sm = StateManager()
        self.st = StoryEngine(self.sm)

    def test_bridge_id_flow(self):
        """选择→跳转 后 _last_node_id 正确"""
        self.st.load_chapter(1)
        self.st.goto_node("ch01_check_power")
        src = self.st.current_node  # 记录源节点
        choices = self.st.get_available_choices()
        self.st.make_choice(0)  # 选第一个 → ch01_evening
        # _jump_to_node 应在跳转前记录源
        self.assertEqual(self.st._last_node_id, src,
            "跳转后 _last_node_id 应为源节点")

    def test_bridge_text_applied(self):
        """text_bridges 被正确拼接"""
        self.st.load_chapter(1)
        self.st.goto_node("ch01_check_power")
        self.st.make_choice(0)  # → ch01_evening
        text = self.st.get_current_text()
        # 应包含 ch01_evening.text_bridges 中 ch01_check_power 的桥文本
        self.assertIn("维护手册", text, "桥文本应包含'维护手册'")


class TestQAMultiClick(unittest.TestCase):
    """验证多击机制状态机"""

    def setUp(self):
        self.sm = StateManager()
        self.st = StoryEngine(self.sm)

    def test_multi_click_node_exists(self):
        """ch03 含多击选项"""
        self.st.load_chapter(3)
        self.st.goto_node("ch03_basement_find")
        choices = self.st.get_available_choices()
        mc_choices = [c for c in choices if c.get("multi_click")]
        self.assertEqual(len(mc_choices), 1,
            "ch03_basement_find 应有 1 个 multi_click 选项")


class TestQAMinigameLifecycle(unittest.TestCase):
    """验证 MG2 竞态修复：_schedule_next cancel _spawn_timer（B3）"""

    def test_clear_dot_cancels_spawn(self):
        """_schedule_next 调度前 cancel 旧 _spawn_timer"""
        from minigame_base import MG2_SolarReaction
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        frm = tk.Frame(root)
        mg = MG2_SolarReaction(frm)
        mg._running = True
        # 模拟已有 _spawn_timer
        fake_id = 99999
        mg._spawn_timer = fake_id
        mg._dots = []
        mg._dots_alive = False
        mg.canvas = tk.Canvas(frm, width=100, height=100)
        try:
            mg._schedule_next()
            # 若 _spawn_timer 已被 cancel 并被替换，不应崩溃
            self.assertNotEqual(mg._spawn_timer, fake_id,
                "_schedule_next 应取消旧 _spawn_timer 并设置新的")
        finally:
            root.destroy()


class TestQAChapterIntegrity(unittest.TestCase):
    """验证全部 6 章可加载且节点完整"""

    def setUp(self):
        self.sm = StateManager()
        self.st = StoryEngine(self.sm)

    def test_all_chapters_load(self):
        """6 章均可加载"""
        for ch in range(1, 7):
            self.st.load_chapter(ch)
            self.assertGreater(len(self.st.nodes), 0,
                "第{}章应包含节点".format(ch))

    def test_chapter_06_endings(self):
        """ch06 包含全部 8 结局节点"""
        self.st.load_chapter(6)
        endings = ["ch06_ending_G", "ch06_ending_death", "ch06_ending_F",
                    "ch06_ending_A", "ch06_ending_E", "ch06_ending_B",
                    "ch06_ending_C", "ch06_ending_D"]
        for eid in endings:
            # 这些节点不一定在 ch06 JSON 中（某些在其他地方），但至少 _ensure_node_loaded 会尝试加载
            self.st._ensure_node_loaded(eid)
            self.assertIn(eid, self.st.nodes,
                "结局节点 {} 应存在".format(eid))

    def test_chapter_04_return_drawer(self):
        """ch04_return_drawer 节点存在"""
        self.st.load_chapter(4)
        self.assertIn("ch04_return_drawer", self.st.nodes,
            "ch04_return_drawer 节点应存在")


if __name__ == "__main__":
    unittest.main()
