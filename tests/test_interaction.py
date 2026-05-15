# -*- coding: utf-8 -*-
"""
test_interaction.py —— 交互状态机交叉测试
覆盖跨模块交互盲区：面板 × 暂停计时 / 面板 × 逐字打印 / 光点 tuple 一致性。

这些测试不操作 GUI，只验证内部状态机在交叉条件下的行为正确性。
对应 fd_selfcheck.md 的交互矩阵（X1~X6）。
"""

import os
import sys
import tkinter as tk
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from main_window import MainWindow
from minigame_base import MG2_SolarReaction


class TestInteractionPanelPause(unittest.TestCase):
    """面板 + 暂停计时 交叉场景（X2/X3）"""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.win = MainWindow(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_show_panel_cancels_pause_job(self):
        """X2: 暂停倒计时中按 Tab → 计时器取消"""
        self.win._is_pausing = True
        self.win._pause_job = "fake_timer_id"
        self.win._show_panel()
        self.assertIsNone(self.win._pause_job,
            "面板打开后 _pause_job 应为 None（计时器已取消）")

    def test_finish_pause_blocked_when_panel_open(self):
        """X3: 面板打开时暂停计时到期 → 文本不推进"""
        self.win._panel_open = True
        self.win._chunks = ["块1", "块2"]
        self.win._chunk_idx = 0
        self.win._is_pausing = True
        self.win._pause_job = None
        self.win._finish_pause()
        self.assertEqual(self.win._chunk_idx, 0,
            "面板打开时 _finish_pause 不应推进 chunk_idx")

    def test_show_panel_pauses_typewriter(self):
        """X1: 逐字打印中按 Tab → 打字暂停"""
        self.win._is_typing = True
        self.win._typewriter_job = "fake_timer_id"
        self.win._show_panel()
        self.assertIsNone(self.win._typewriter_job,
            "面板打开后 _typewriter_job 应为 None（打字已暂停）")

    def test_text_advance_blocked_when_panel_open(self):
        """X1: 面板打开时按键 → 文本不推进"""
        self.win._panel_open = True
        self.win._chunks = ["块1", "块2"]
        self.win._chunk_idx = 0
        result = self.win._on_text_advance()
        self.assertEqual(result, "break",
            "面板打开时 _on_text_advance 应返回 'break'")
        self.assertEqual(self.win._chunk_idx, 0,
            "面板打开时不应推进 chunk_idx")

    def test_pause_blocked_by_panel_in_on_text_advance(self):
        """X2: 暂停中且面板打开时按键 → 不应双重推进"""
        self.win._panel_open = True
        self.win._is_pausing = True
        self.win._pause_job = "fake"
        self.win._chunks = ["块1", "块2"]
        self.win._chunk_idx = 0
        # 面板打开时 space 事件被第一行 _panel_open 拦截
        result = self.win._on_text_advance()
        self.assertEqual(result, "break")
        # 不应进入 _is_pausing 分支（因为 _panel_open 先拦截）
        self.assertTrue(self.win._is_pausing or self.win._chunk_idx == 0)


class TestInteractionMinigameDot(unittest.TestCase):
    """MG2 光点 tuple 一致性验证（X4 场景）"""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        frame = tk.Frame(self.root)
        frame.pack()
        self.mg = MG2_SolarReaction(frame)
        self.mg._running = True

    def tearDown(self):
        self.mg.destroy()
        self.root.destroy()

    def test_click_with_yellow_dot(self):
        """B3: _on_click 命中黄点不崩溃"""
        self.mg._dots = [{"type": "yellow", "x": 100, "y": 100, "r": 20, "max_r": 20,
                           "inner_id": "i1", "outer_id": "o1", "vx": 0, "vy": 0}]
        self.mg._dots_alive = True
        class MockEvent:
            x = 105
            y = 105
        try:
            self.mg._on_click(MockEvent())
        except Exception as e:
            self.fail("_on_click 失败: {}".format(e))

    def test_hit_yellow_unpack(self):
        """B3: _hit_yellow 正确操作 dot dict"""
        d = {"type": "yellow", "x": 100, "y": 100, "r": 20, "max_r": 20,
             "inner_id": "i1", "outer_id": "o1", "vx": 0, "vy": 0}
        self.mg._dots = [d]
        self.mg._dots_alive = True
        try:
            self.mg._hit_yellow(d)
        except Exception as e:
            self.fail("_hit_yellow 失败: {}".format(e))

    def test_hit_blue_unpack(self):
        """B3: _hit_blue 正确操作 dot dict"""
        d = {"type": "blue", "x": 100, "y": 100, "r": 20, "max_r": 20,
             "inner_id": "i1", "outer_id": "o1", "vx": 0, "vy": 0}
        self.mg._dots = [d]
        self.mg._dots_alive = True
        try:
            self.mg._hit_blue(d)
        except Exception as e:
            self.fail("_hit_blue 失败: {}".format(e))

    def test_no_crash_on_click_without_dot(self):
        """B3: _on_click 在当前无光点时不应崩溃"""
        self.mg._dots = []
        self.mg._dots_alive = False
        class MockEvent:
            x = 0
            y = 0
        try:
            self.mg._on_click(MockEvent())
        except Exception as e:
            self.fail("无光点状态下 _on_click 不应崩溃: {}".format(e))


if __name__ == "__main__":
    unittest.main()
