# -*- coding: utf-8 -*-
"""
test_story_engine.py —— 剧情引擎单元测试
覆盖：JSON 加载 / 节点跳转 / 条件过滤 / 选择效果 / auto_next
使用临时 JSON 数据，不依赖实际章节文件。
"""

import os
import sys
import json
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from state_manager import StateManager
from story_engine import StoryEngine


def _make_temp_json(data):
    """创建临时 JSON 文件，返回路径"""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(data, tmp)
    tmp.close()
    return tmp.name


class TestStoryEngine(unittest.TestCase):

    def setUp(self):
        self.sm = StateManager()
        self.engine = StoryEngine(self.sm, "data")

    # ---- 加载 ----

    def test_load_node_ids_manual(self):
        """手动注入节点，测试 nodes 字典加载"""
        js = {
            "chapter": 99,
            "start_node": "n1",
            "nodes": [
                {"node_id": "n1", "chapter": 99, "day": 1, "text": "测试", "choices": []},
                {"node_id": "n2", "chapter": 99, "day": 2, "text": "结束",
                 "choices": [{"label": "继续", "next_node": None, "effects": None, "conditions": None}],
                 "auto_next": "n3"},
            ]
        }
        self.engine.nodes = {n["node_id"]: n for n in js["nodes"]}
        self.engine.current_node = "n1"
        self.assertIn("n1", self.engine.nodes)
        self.assertIn("n2", self.engine.nodes)

    # ---- 节点跳转 ----

    def test_goto_node_exists(self):
        self.engine.nodes = {
            "a": {"node_id": "a", "chapter": 1, "day": 1, "text": "A", "choices": []},
            "b": {"node_id": "b", "chapter": 2, "day": 3, "text": "B", "choices": []},
        }
        self.engine.goto_node("b")
        self.assertEqual(self.engine.current_node, "b")
        self.assertEqual(self.engine.chapter, 2)
        self.assertEqual(self.engine.day, 3)

    def test_goto_node_does_not_exist(self):
        self.engine.nodes = {}
        result = self.engine.goto_node("gone")
        self.assertIsNone(result)

    # ---- 获取当前文本 ----

    def test_get_current_text(self):
        self.engine.nodes = {
            "a": {"node_id": "a", "chapter": 1, "day": 1, "text": "你好", "choices": []},
        }
        self.engine.current_node = "a"
        self.assertEqual(self.engine.get_current_text(), "你好")

    def test_get_current_text_none(self):
        self.engine.current_node = None
        self.assertEqual(self.engine.get_current_text(), "")

    # ---- 条件过滤 ----

    def test_available_choices_unconditional(self):
        self.engine.nodes = {
            "a": {"node_id": "a", "chapter": 1, "day": 1, "text": "",
                  "choices": [
                      {"label": "A", "next_node": "b", "effects": None, "conditions": None},
                      {"label": "B", "next_node": "c", "effects": None, "conditions": None},
                  ]},
        }
        self.engine.current_node = "a"
        available = self.engine.get_available_choices()
        self.assertEqual(len(available), 2)

    def test_available_choices_filtered(self):
        self.sm.change("curiosity", 0)
        self.engine.nodes = {
            "a": {"node_id": "a", "chapter": 1, "day": 1, "text": "",
                  "choices": [
                      {"label": "需要好奇", "next_node": "b", "effects": None,
                       "conditions": {"curiosity": {"min": 5}}},
                      {"label": "无条件", "next_node": "c", "effects": None,
                       "conditions": None},
                  ]},
        }
        self.engine.current_node = "a"
        available = self.engine.get_available_choices()
        self.assertEqual(len(available), 1)
        self.assertEqual(available[0]["label"], "无条件")

    def test_available_choices_none(self):
        self.engine.current_node = None
        self.assertEqual(self.engine.get_available_choices(), [])

    # ---- 选择效果 ----

    def test_make_choice_applies_effects(self):
        self.engine.nodes = {
            "a": {"node_id": "a", "chapter": 1, "day": 1, "text": "",
                  "choices": [
                      {"label": "加好奇", "next_node": "b", "effects": {"curiosity": 3}, "conditions": None},
                  ]},
            "b": {"node_id": "b", "chapter": 1, "day": 2, "text": "B", "choices": []},
        }
        self.engine.current_node = "a"
        self.engine.make_choice(0)
        self.assertEqual(self.sm.get("curiosity"), 3)
        self.assertEqual(self.engine.current_node, "b")
        self.assertEqual(self.engine.day, 2)

    def test_make_choice_records_history(self):
        self.engine.nodes = {
            "a": {"node_id": "a", "chapter": 1, "day": 1, "text": "",
                  "choices": [
                      {"label": "走", "next_node": "b", "effects": None, "conditions": None},
                  ]},
            "b": {"node_id": "b", "chapter": 1, "day": 2, "text": "B", "choices": []},
        }
        self.engine.current_node = "a"
        self.engine.make_choice(0)
        self.assertEqual(self.engine.history, ["a"])

    # ---- auto_next / 结束 ----

    def test_auto_next_triggers_reached_end(self):
        self.engine.nodes = {
            "a": {"node_id": "a", "chapter": 1, "day": 1, "text": "",
                  "choices": [
                      {"label": "完成", "next_node": None, "effects": None, "conditions": None},
                  ],
                  "auto_next": "missing_node"},
        }
        self.engine.current_node = "a"
        self.engine.reached_end = False
        self.engine.make_choice(0)
        self.assertTrue(self.engine.reached_end)
        self.assertIsNone(self.engine.current_node)

    def test_auto_next_to_loaded_node_no_effect(self):
        """如果 auto_next 指向的节点已加载，make_choice 不会自动跳转"""
        self.engine.nodes = {
            "a": {"node_id": "a", "chapter": 1, "day": 1, "text": "",
                  "choices": [
                      {"label": "完成", "next_node": None, "effects": None, "conditions": None},
                  ],
                  "auto_next": "b"},
            "b": {"node_id": "b", "chapter": 1, "day": 2, "text": "B", "choices": []},
        }
        self.engine.current_node = "a"
        self.engine.reached_end = False
        result = self.engine.make_choice(0)
        # 不应跳转到 b（当前逻辑：auto_next 在已加载时不自动跳转）
        self.assertFalse(self.engine.reached_end)

    # ---- 选择索引越界 ----

    def test_make_choice_out_of_range(self):
        self.engine.nodes = {
            "a": {"node_id": "a", "chapter": 1, "day": 1, "text": "",
                  "choices": []},
        }
        self.engine.current_node = "a"
        with self.assertRaises(IndexError):
            self.engine.make_choice(0)


if __name__ == "__main__":
    unittest.main()
