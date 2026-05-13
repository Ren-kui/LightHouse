# -*- coding: utf-8 -*-
"""
test_sound_manager.py —— SD 音效模块验收测试（SD-01~04）
覆盖：实例化 / API 签名 / 边界保护 / 不阻塞

QA 按 sound_spec.md §1-§7 逐项验证。
"""

import os
import sys
import time
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from sound_manager import SoundManager


class TestSoundManagerAcceptance(unittest.TestCase):
    """SD-01~04 音效模块基础验收"""

    def setUp(self):
        tmpdir = tempfile.mkdtemp()
        self._tmpdir = tmpdir
        self.snd = SoundManager(data_dir=tmpdir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    # ========== SD-01 · 实例化 ==========

    def test_sd01_instantiation_ok(self):
        """SD-01a: SoundManager 实例化不报错"""
        self.assertIsInstance(self.snd, SoundManager)

    def test_sd01_registry_complete(self):
        """SD-01b: 注册表包含全部 5 个音效"""
        required = ["hum_low", "heartbeat", "metal_creak", "water_drone", "silence_fade"]
        for name in required:
            self.assertIn(name, SoundManager.REGISTRY,
                          "注册表缺少音效: {}".format(name))

    def test_sd01_registry_fields_complete(self):
        """SD-01c: 每个注册音效含全部必要字段"""
        required_fields = {"freq", "duration", "waveform", "loop"}
        for name, spec in SoundManager.REGISTRY.items():
            missing = required_fields - set(spec.keys())
            self.assertEqual(missing, set(),
                "音效 '{}' 缺字段: {}".format(name, missing))

    def test_sd01_sound_dir_created(self):
        """SD-01d: data/sounds/ 目录自动创建"""
        self.assertTrue(os.path.isdir(self.snd._sound_dir))

    # ========== SD-02 · API 签名 ==========

    def test_sd02_api_play_exists(self):
        """SD-02a: play(name) 方法存在且可调用"""
        self.assertTrue(callable(self.snd.play))
        # M4 空壳，调用不报错
        self.snd.play("hum_low")

    def test_sd02_api_stop_exists(self):
        """SD-02b: stop(name) 方法存在"""
        self.assertTrue(callable(self.snd.stop))
        self.snd.stop("hum_low")

    def test_sd02_api_stop_all_exists(self):
        """SD-02c: stop_all() 方法存在"""
        self.assertTrue(callable(self.snd.stop_all))
        self.snd.stop_all()

    def test_sd02_api_set_volume_exists(self):
        """SD-02d: set_volume(f) 方法存在"""
        self.assertTrue(callable(self.snd.set_volume))
        self.snd.set_volume(0.5)

    def test_sd02_api_mute_unmute_exists(self):
        """SD-02e: mute() / unmute() 方法存在"""
        self.assertTrue(callable(self.snd.mute))
        self.assertTrue(callable(self.snd.unmute))

    def test_sd02_api_to_dict_exists(self):
        """SD-02f: to_dict() 返回 dict"""
        d = self.snd.to_dict()
        self.assertIsInstance(d, dict)
        self.assertIn("active", d)
        self.assertIn("volume", d)
        self.assertIn("muted", d)

    def test_sd02_api_from_dict_exists(self):
        """SD-02g: from_dict(dict) 方法存在且可调用"""
        self.assertTrue(callable(self.snd.from_dict))
        self.snd.from_dict({"active": "hum_low", "volume": 0.3, "muted": True})
        self.assertTrue(self.snd.is_muted)
        self.assertEqual(self.snd.volume, 0.3)

    def test_sd02_api_properties(self):
        """SD-02h: volume / is_muted 属性可读"""
        self.assertIsInstance(self.snd.volume, float)
        self.assertIsInstance(self.snd.is_muted, bool)

    # ========== SD-03 · 边界保护 ==========

    def test_sd03_play_unknown_raises(self):
        """SD-03a: play(不存在的音效名) 抛 ValueError"""
        with self.assertRaises(ValueError):
            self.snd.play("nonexistent_sound")

    def test_sd03_volume_negative_raises(self):
        """SD-03b: set_volume(-0.1) 抛 ValueError"""
        with self.assertRaises(ValueError):
            self.snd.set_volume(-0.1)

    def test_sd03_volume_above_1_raises(self):
        """SD-03c: set_volume(1.5) 抛 ValueError"""
        with self.assertRaises(ValueError):
            self.snd.set_volume(1.5)

    def test_sd03_volume_boundary_0_ok(self):
        """SD-03d: set_volume(0.0) 不抛异常"""
        self.snd.set_volume(0.0)
        self.assertEqual(self.snd.volume, 0.0)

    def test_sd03_volume_boundary_1_ok(self):
        """SD-03e: set_volume(1.0) 不抛异常"""
        self.snd.set_volume(1.0)
        self.assertEqual(self.snd.volume, 1.0)

    def test_sd03_mute_toggle(self):
        """SD-03f: mute()/unmute() 状态正确翻转"""
        self.assertFalse(self.snd.is_muted)
        self.snd.mute()
        self.assertTrue(self.snd.is_muted)
        self.snd.unmute()
        self.assertFalse(self.snd.is_muted)

    # ========== SD-04 · 不阻塞 ==========

    def test_sd04_init_under_100ms(self):
        """SD-04a: __init__ 在 2s 内完成（M5 含 PCM 合成 + 磁盘写入）"""
        t0 = time.perf_counter()
        s = SoundManager(data_dir=self._tmpdir + "_sd04a")
        elapsed = time.perf_counter() - t0
        self.assertLess(elapsed, 2.0,
            "__init__ 耗时 {:.4f}s，超过 2s".format(elapsed))
        # 清理临时目录
        import shutil
        shutil.rmtree(s._sound_dir, ignore_errors=True)

    def test_sd04_play_returns_quickly(self):
        """SD-04b: play() 立即返回（M5 异步线程播放，play 本身不阻塞）"""
        t0 = time.perf_counter()
        for _ in range(10):
            self.snd.play("hum_low")
        elapsed = time.perf_counter() - t0
        self.assertLess(elapsed, 0.5,
            "play() 10 次耗时 {:.4f}s，可能阻塞主线程".format(elapsed))

    def test_sd04_stop_all_no_delay(self):
        """SD-04c: stop_all() 立即返回"""
        t0 = time.perf_counter()
        self.snd.stop_all()
        elapsed = time.perf_counter() - t0
        self.assertLess(elapsed, 0.05,
            "stop_all() 耗时 {:.4f}s".format(elapsed))


if __name__ == "__main__":
    unittest.main()
