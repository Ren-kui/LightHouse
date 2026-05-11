# -*- coding: utf-8 -*-
"""
test_save_manager.py —— 存档系统单元测试
覆盖：存档/读档往返 / 存档信息 / 空存档处理
使用临时 JSON 文件，不影响实际存档数据。
"""

import os
import sys
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from state_manager import StateManager
from save_manager import SaveManager


class TestSaveManager(unittest.TestCase):

    def setUp(self):
        tmpdir = tempfile.mkdtemp()
        self._tmpdir = tmpdir
        save_dir = os.path.join(tmpdir, "saves")
        os.makedirs(save_dir, exist_ok=True)
        self.mgr = SaveManager(save_dir=save_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def _make_state(self):
        sm = StateManager()
        sm.change("curiosity", 3)   # 0 + 3 = 3
        sm.change("sanity", -2)     # 10 - 2 = 8
        return sm

    # ---- 存档 / 读档 ----

    def test_save_and_load_roundtrip(self):
        sm = self._make_state()
        self.mgr.save("1", sm, "ch01_start", 1, 1, ["n1"], {"found_diary": True})

        data = self.mgr.load("1")
        self.assertIsNotNone(data)
        self.assertEqual(data["current_node"], "ch01_start")
        self.assertEqual(data["chapter"], 1)
        self.assertEqual(data["day"], 1)
        self.assertEqual(data["history"], ["n1"])
        self.assertTrue(data["flags"]["found_diary"])
        self.assertEqual(data["variables"]["curiosity"], 3)
        self.assertEqual(data["variables"]["sanity"], 8)

    def test_save_overwrites(self):
        sm = self._make_state()
        self.mgr.save("1", sm, "n1", 1, 1, [], {})
        self.mgr.save("1", sm, "n2", 2, 3, [], {})
        data = self.mgr.load("1")
        self.assertEqual(data["current_node"], "n2")
        self.assertEqual(data["day"], 3)

    # ---- 空存档 / 不存在 ----

    def test_load_nonexistent_returns_none(self):
        data = self.mgr.load("999")
        self.assertIsNone(data)

    def test_get_info_empty_slot(self):
        info = self.mgr.get_info("1")
        self.assertFalse(info["exists"])

    def test_get_info_existing_slot(self):
        sm = self._make_state()
        self.mgr.save("1", sm, "ch01_start", 1, 1, [], {})
        info = self.mgr.get_info("1")
        self.assertTrue(info["exists"])
        self.assertIn("save_time", info)
        self.assertEqual(info["day"], 1)

    # ---- 自动存档位 ----

    def test_save_to_auto(self):
        sm = self._make_state()
        self.mgr.save("auto", sm, "ch02_d3_whisper", 2, 3, [], {})
        data = self.mgr.load("auto")
        self.assertIsNotNone(data)
        self.assertEqual(data["chapter"], 2)
        self.assertEqual(data["day"], 3)

    def test_save_to_string_slot(self):
        sm = self._make_state()
        self.mgr.save("2", sm, "n", 1, 1, [], {})
        data = self.mgr.load("2")
        self.assertIsNotNone(data)

    # ---- 存档信息列表 ----

    def test_get_info_all_slots(self):
        sm = self._make_state()
        for slot in ["1", "2", "3", "auto"]:
            self.mgr.save(str(slot), sm, "n", 1, 1, [], {})
            info = self.mgr.get_info(str(slot))
            self.assertTrue(info["exists"])


if __name__ == "__main__":
    unittest.main()
