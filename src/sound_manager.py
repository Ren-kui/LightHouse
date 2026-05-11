# -*- coding: utf-8 -*-
"""
sound_manager.py —— 音效管理器
纯代码合成音频（wave + struct + math），零外部依赖/零素材文件。
SD 维护，FD 通过 API 调用。

架构：
  - 预生成策略：所有音效在 __init__ 时一次性合成到 data/sounds/ 缓存
  - 异步播放：不阻塞 Tkinter 主线程
  - 静默规则：章节过渡/面板打开/选项出现时自动淡出
"""

import os
import struct
import math
import wave
import threading


class SoundManager:
    """音效引擎。M4 阶段：空壳 API，不实际发声。"""

    REGISTRY = {
        "hum_low":       {"freq": 40,  "duration": 3.0, "waveform": "sine",   "loop": True},
        "heartbeat":     {"freq": 60,  "duration": 0.5, "waveform": "pulse",  "loop": True},
        "metal_creak":   {"freq": 800, "duration": 0.3, "waveform": "square", "loop": False},
        "water_drone":   {"freq": 30,  "duration": 3.0, "waveform": "noise",  "loop": True},
        "silence_fade":  {"freq": 0,   "duration": 0.5, "waveform": "fade",   "loop": False},
    }

    SAMPLE_RATE = 44100
    SAMPLE_WIDTH = 2
    CHANNELS = 1

    def __init__(self, data_dir: str = "data"):
        self._data_dir = data_dir
        self._sound_dir = os.path.join(data_dir, "sounds")
        os.makedirs(self._sound_dir, exist_ok=True)
        self._volume = 0.8
        self._muted = False
        self._active = None
        self._lock = threading.Lock()

    # ========== 公共 API ==========

    def play(self, name: str):
        """播放命名音效（M5 前不实际发声）"""
        if name not in self.REGISTRY:
            raise ValueError("未知音效: {}".format(name))
        # M5: 实际合成 + 播放

    def stop(self, name: str):
        """停止指定音效"""
        # M5: 实际停止
        pass

    def stop_all(self):
        """静默全部音效"""
        # M5: 实际停止全部
        pass

    def set_volume(self, volume: float):
        """设置全局音量 0.0 ~ 1.0"""
        if not 0.0 <= volume <= 1.0:
            raise ValueError("音量必须在 0.0 ~ 1.0 之间，收到: {}".format(volume))
        self._volume = volume

    def mute(self):
        """静音"""
        self._muted = True

    def unmute(self):
        """取消静音"""
        self._muted = False

    @property
    def is_muted(self) -> bool:
        return self._muted

    @property
    def volume(self) -> float:
        return self._volume

    # ========== 存档序列化 ==========

    def to_dict(self) -> dict:
        """序列化音效状态（存档用）"""
        return {
            "active": self._active,
            "volume": self._volume,
            "muted": self._muted,
        }

    def from_dict(self, data: dict):
        """从存档恢复音效状态"""
        if data:
            self._active = data.get("active")
            self._volume = data.get("volume", 0.8)
            self._muted = data.get("muted", False)

    # ========== 内部合成（M5 实现） ==========

    def _generate_tone(self, freq: float, duration: float, waveform: str) -> str:
        """预生成音效文件到 data/sounds/。
        返回缓存文件路径。M5 实现实际 PCM 采样合成。
        """
        # M5: 根据 waveform 类型生成正弦波/方波/脉冲/噪声/fade
        pass
