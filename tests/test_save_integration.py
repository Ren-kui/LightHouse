# -*- coding: utf-8 -*-
"""
test_save_integration.py —— 存档/读档链路集成测试（QA）
覆盖：完整往返 / sound_state / 存档数据格式 / 多存档位 / 保存后读取的一致性
M4 QA 通过后移入 test_report.md。
"""

import os
import sys
import json
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from state_manager import StateManager
from save_manager import SaveManager
from sound_manager import SoundManager


class TestSaveIntegration(unittest.TestCase):
    """存档/读档完整链路集成测试"""

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
        sm.change("curiosity", 5)
        sm.change("sanity", -3)
        sm.change("trust", 2)
        sm.change("survival_will", -1)
        sm.change("loyalty", 1)
        return sm

    # ========== 完整字段往返 ==========

    def test_full_roundtrip_all_fields(self):
        """SA-01: 存档→读档 全字段往返（含 sound_state）"""
        sm = self._make_state()
        history = ["ch01_start", "ch01_evening", "ch02_mg1"]
        flags = {"found_diary": True, "mg1_complete": False}
        sound = {"active": "hum_low", "volume": 0.6, "muted": False}

        self.mgr.save(1, sm, "ch02_d3_whisper", 2, 3,
                      history, flags, sound_state=sound)

        data = self.mgr.load(1)
        self.assertIsNotNone(data, "读档不应为 None")
        self.assertEqual(data["current_node"], "ch02_d3_whisper")
        self.assertEqual(data["chapter"], 2)
        self.assertEqual(data["day"], 3)
        self.assertEqual(data["history"], history)
        self.assertEqual(data["flags"], flags)
        self.assertEqual(data["variables"]["curiosity"], 5)
        self.assertEqual(data["variables"]["sanity"], 7)   # 10-3
        self.assertEqual(data["variables"]["trust"], 6)     # 4+2
        self.assertEqual(data["variables"]["survival_will"], 5)  # 6-1
        self.assertEqual(data["variables"]["loyalty"], 4)   # 3+1
        self.assertEqual(data["sound_state"], sound)
        self.assertIn("save_time", data)

    def test_sound_state_roundtrip_variants(self):
        """SA-02: sound_state 各种取值往返"""
        sm = self._make_state()

        # 静音状态
        sound_muted = {"active": "water_drone", "volume": 0.3, "muted": True}
        self.mgr.save(1, sm, "n", 1, 1, [], {}, sound_state=sound_muted)
        self.assertEqual(self.mgr.load(1)["sound_state"], sound_muted)

        # 无活跃音效
        sound_none = {"active": None, "volume": 0.8, "muted": False}
        self.mgr.save(2, sm, "n", 1, 1, [], {}, sound_state=sound_none)
        self.assertIsNone(self.mgr.load(2)["sound_state"]["active"])

        # 空 sound_state
        self.mgr.save(3, sm, "n", 1, 1, [], {}, sound_state={})
        self.assertEqual(self.mgr.load(3)["sound_state"], {})

    # ========== 存档数据格式 ==========

    def test_save_data_has_all_required_keys(self):
        """SA-03: 存档文件包含全部必须键"""
        sm = self._make_state()
        self.mgr.save(1, sm, "ch01_start", 1, 1, [], {},
                      sound_state={"active": "hum_low", "volume": 0.5, "muted": False})

        # 直接读取 JSON 文件检查键
        raw_path = os.path.join(self.mgr.save_dir, "save_1.json")
        with open(raw_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        required = ["save_time", "current_node", "chapter", "day",
                    "variables", "history", "flags", "sound_state", "items"]
        for key in required:
            self.assertIn(key, raw,
                          "存档必须包含键 '{}'，当前键: {}".format(key, list(raw.keys())))

        # 变量子键检查
        var_keys = ["curiosity", "sanity", "trust", "survival_will", "loyalty"]
        for vk in var_keys:
            self.assertIn(vk, raw["variables"])

    # ========== 多次存取 ==========

    def test_multi_cycle_save_load(self):
        """SA-04: 多轮 存档→修改→存→读 循环"""
        sm = self._make_state()
        self.mgr.save(1, sm, "n1", 1, 1, [], {})
        self.assertEqual(self.mgr.load(1)["current_node"], "n1")

        sm.change("curiosity", 2)  # 5+2=7
        self.mgr.save(1, sm, "n2", 2, 4, ["n1"], {"a": 1})
        self.assertEqual(self.mgr.load(1)["current_node"], "n2")
        self.assertEqual(self.mgr.load(1)["day"], 4)
        self.assertEqual(self.mgr.load(1)["variables"]["curiosity"], 7)

    def test_multiple_slots_independent(self):
        """SA-05: 多个存档位互不干扰"""
        sm = self._make_state()
        self.mgr.save(1, sm, "node_a", 1, 2, ["h1"], {})
        self.mgr.save(2, sm, "node_b", 2, 5, ["h2"], {"k": "v"})
        self.mgr.save(3, sm, "node_c", 3, 7, ["h3"], {})

        self.assertEqual(self.mgr.load(1)["current_node"], "node_a")
        self.assertEqual(self.mgr.load(2)["current_node"], "node_b")
        self.assertEqual(self.mgr.load(3)["current_node"], "node_c")

    # ========== 存档信息接口 ==========

    def test_get_info_fields_complete(self):
        """SA-06: get_info 返回完整字段"""
        sm = self._make_state()
        self.mgr.save(1, sm, "ch02_d3_evening", 2, 3, [], {})

        info = self.mgr.get_info(1)
        self.assertTrue(info["exists"])
        self.assertIn("save_time", info)
        self.assertEqual(info["day"], 3)
        self.assertEqual(info["chapter"], 2)

    def test_get_info_auto_slot(self):
        """SA-07: 自动存档位 info 正确"""
        sm = self._make_state()
        self.mgr.save("auto", sm, "ch03_basement", 3, 5, [], {})

        info = self.mgr.get_info("auto")
        self.assertTrue(info["exists"])
        self.assertEqual(info["chapter"], 3)

    # ========== 边界情况 ==========

    def test_save_then_load_corrupt_dir(self):
        """SA-08: 不存在的槽位返回 None"""
        self.assertIsNone(self.mgr.load("nonexistent"))
        self.assertIsNone(self.mgr.load(999))

    def test_save_overwrite_preserves_format(self):
        """SA-09: 覆写存档保持数据格式一致"""
        sm = self._make_state()
        self.mgr.save(1, sm, "first", 1, 1, [], {"f1": True})
        self.mgr.save(1, sm, "second", 2, 2, ["first"], {})

        data = self.mgr.load(1)
        self.assertEqual(data["current_node"], "second")
        self.assertNotIn("f1", data["flags"])

    def test_save_with_none_sound_state(self):
        """SA-10: sound_state=None 时填入空字典"""
        sm = self._make_state()
        self.mgr.save(1, sm, "n", 1, 1, [], {}, sound_state=None)
        data = self.mgr.load(1)
        self.assertEqual(data["sound_state"], {})

    def test_sound_manager_to_from_dict(self):
        """SA-11: SoundManager to_dict/from_dict 序列化往返"""
        snd = SoundManager()
        snd.set_volume(0.5)
        snd.mute()
        d = snd.to_dict()
        self.assertEqual(d["volume"], 0.5)
        self.assertTrue(d["muted"])
        self.assertIsNone(d["active"])

        snd2 = SoundManager()
        snd2.from_dict(d)
        self.assertEqual(snd2.volume, 0.5)
        self.assertTrue(snd2.is_muted)

        # 空 dict 不应改变已有状态（旧存档无 sound_state 时的行为）
        snd3 = SoundManager()
        snd3.set_volume(0.3)
        snd3.from_dict({})
        self.assertEqual(snd3.volume, 0.3)  # 保持原值
        self.assertFalse(snd3.is_muted)     # 保持默认


if __name__ == "__main__":
    unittest.main()
