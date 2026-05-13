# -*- coding: utf-8 -*-
"""
sound_manager.py —— 音效管理器
纯代码合成音频（wave + struct + math），零外部依赖/零素材文件。
SD 维护，FD 通过 API 调用。

架构：
  - 预生成策略：所有音效在 __init__ 时一次性合成到 data/sounds/ 缓存
  - 异步播放：使用 winsound SND_ASYNC，不阻塞 Tkinter 主线程
  - 静默规则：章节过渡/面板打开/选项出现时自动淡出
"""

import os
import struct
import math
import wave
import threading
import random
from array import array


class SoundManager:
    """音效引擎。M5：完整 PCM 合成 + winsound 播放。"""

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
    MAX_AMPLITUDE = 32767

    def __init__(self, data_dir: str = "data"):
        self._data_dir = data_dir
        self._sound_dir = os.path.join(data_dir, "sounds")
        os.makedirs(self._sound_dir, exist_ok=True)
        self._volume = 0.8
        self._muted = False
        self._active = None
        self._loop_active = None
        self._lock = threading.Lock()
        self._play_thread = None

        # 预生成全部音效文件
        self._generate_all()

    # ========== 公共 API ==========

    def play(self, name: str):
        """播放命名音效。使用 winsound 异步回放（不阻塞主线程）。"""
        if name not in self.REGISTRY:
            raise ValueError("未知音效: {}".format(name))

        info = self.REGISTRY[name]
        path = self._get_cache_path(name)

        if not os.path.exists(path):
            return

        with self._lock:
            # silence_fade 先停止当前全部音效再播放淡出音
            if name == "silence_fade":
                self._stop_inner()

            if self._muted:
                return

            self._active = name
            if info["loop"]:
                self._loop_active = name

        # 在独立线程中调用 winsound（winsound 的 SND_ASYNC 本身不阻塞，
        # 但 PlaySound 调用期间会短暂持有 GIL，用线程隔离避免影响逐字动画）
        self._play_thread = threading.Thread(
            target=self._play_winsound,
            args=(path, info["loop"]),
            daemon=True)
        self._play_thread.start()

    def stop(self, name: str):
        """停止指定音效"""
        with self._lock:
            if self._active == name:
                self._stop_inner()

    def stop_all(self):
        """静默全部音效"""
        with self._lock:
            self._stop_inner()

    def set_volume(self, volume: float):
        """设置全局音量 0.0 ~ 1.0"""
        if not 0.0 <= volume <= 1.0:
            raise ValueError("音量必须在 0.0 ~ 1.0 之间，收到: {}".format(volume))
        self._volume = volume

    def mute(self):
        """静音"""
        self._muted = True
        self._stop_inner()

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
        with self._lock:
            return {
                "active": self._active,
                "volume": self._volume,
                "muted": self._muted,
            }

    def from_dict(self, data: dict):
        """从存档恢复音效状态"""
        if data:
            self._volume = data.get("volume", 0.8)
            self._muted = data.get("muted", False)

    # ========== 内部合成 ==========

    def _get_cache_path(self, name: str) -> str:
        return os.path.join(self._sound_dir, "{}.wav".format(name))

    def _generate_all(self):
        """预生成全部注册音效到 data/sounds/ 目录。
        若缓存文件已存在（且来源本引擎），跳过生成，避免重复 I/O。
        """
        for name in self.REGISTRY:
            path = self._get_cache_path(name)
            if os.path.exists(path):
                continue
            self._generate_tone(name)

    def _generate_tone(self, name: str):
        """预生成单个音效文件到 data/sounds/。
        根据 waveform 类型生成正弦波/方波/脉冲/噪声/淡出。
        """
        info = self.REGISTRY[name]
        freq = info["freq"]
        duration = info["duration"]
        waveform = info["waveform"]
        path = self._get_cache_path(name)

        if waveform == "sine":
            samples = self._gen_sine(freq, duration)
        elif waveform == "square":
            samples = self._gen_square(freq, duration)
        elif waveform == "pulse":
            samples = self._gen_pulse(freq, duration)
        elif waveform == "noise":
            samples = self._gen_noise(freq, duration)
        elif waveform == "fade":
            samples = self._gen_fade(freq, duration)
        else:
            raise ValueError("未知波形类型: {}".format(waveform))

        self._write_wav(path, samples)

    def _gen_sine(self, freq: float, duration: float) -> array:
        """生成正弦波采样"""
        n = int(self.SAMPLE_RATE * duration)
        buf = array('h', [0] * n)
        amp = self.MAX_AMPLITUDE
        for i in range(n):
            buf[i] = int(amp * math.sin(2 * math.pi * freq * i / self.SAMPLE_RATE))
        return buf

    def _gen_square(self, freq: float, duration: float) -> array:
        """生成方波采样（金属嘎吱感）"""
        n = int(self.SAMPLE_RATE * duration)
        buf = array('h', [0] * n)
        amp = int(self.MAX_AMPLITUDE * 0.6)
        period = self.SAMPLE_RATE / freq if freq > 0 else self.SAMPLE_RATE
        for i in range(n):
            # 方波 + 轻微频率调制模拟金属嘎吱
            t = i / self.SAMPLE_RATE
            mod = 1.0 + 0.15 * math.sin(2 * math.pi * 3.7 * t)
            sample_val = 1 if (i % int(period * mod)) < int(period * mod / 2) else -1
            buf[i] = int(sample_val * amp * math.exp(-3 * t / duration))
        return buf

    def _gen_pulse(self, freq: float, duration: float) -> array:
        """生成双脉冲采样（心跳 lub-dub）"""
        n = int(self.SAMPLE_RATE * duration)
        buf = array('h', [0] * n)
        pulse_width = int(self.SAMPLE_RATE * 0.05)
        pulse_gap = int(self.SAMPLE_RATE * 0.15)
        amp1 = int(self.MAX_AMPLITUDE * 0.7)
        amp2 = int(self.MAX_AMPLITUDE * 0.55)
        # 第一脉冲 (lub)
        for i in range(pulse_width):
            if i < n:
                buf[i] = int(amp1 * math.sin(2 * math.pi * freq * i / self.SAMPLE_RATE))
        # 第二脉冲 (dub)
        offset = pulse_width + pulse_gap
        for i in range(pulse_width):
            idx = offset + i
            if idx < n:
                buf[idx] = int(amp2 * math.sin(2 * math.pi * freq * i / self.SAMPLE_RATE))
        return buf

    def _gen_noise(self, freq: float, duration: float) -> array:
        """生成低通滤波白噪声采样（水下底噪）"""
        n = int(self.SAMPLE_RATE * duration)
        buf = array('h', [0] * n)
        amp = int(self.MAX_AMPLITUDE * 0.25)
        # 简单移动平均低通滤波
        window = int(self.SAMPLE_RATE / (freq * 8)) if freq > 0 else 100
        window = max(1, min(window, n // 4))
        for i in range(n):
            noise_val = random.uniform(-1.0, 1.0)
            buf[i] = int(noise_val * amp)
        # 低通滤波
        filtered = array('h', [0] * n)
        for i in range(n):
            total = 0
            count = 0
            for j in range(max(0, i - window + 1), i + 1):
                total += buf[j]
                count += 1
            filtered[i] = int(total / count) if count > 0 else 0
        return filtered

    def _gen_fade(self, freq: float, duration: float) -> array:
        """生成淡出采样（过渡用）
        固定 440Hz 正弦波从满幅线性衰减至零。
        """
        n = int(self.SAMPLE_RATE * duration)
        buf = array('h', [0] * n)
        tone_freq = 440.0
        for i in range(n):
            envelope = 1.0 - (i / n)
            sample = int(self.MAX_AMPLITUDE * 0.3 * envelope *
                         math.sin(2 * math.pi * tone_freq * i / self.SAMPLE_RATE))
            buf[i] = sample
        return buf

    def _write_wav(self, path: str, samples: array):
        """将采样数据写入 WAV 文件"""
        with wave.open(path, 'w') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.SAMPLE_WIDTH)
            wf.setframerate(self.SAMPLE_RATE)
            wf.writeframes(samples.tobytes())

    # ========== 内部播放 ==========

    def _play_winsound(self, path: str, loop: bool):
        """在独立线程中调用 winsound 播放"""
        try:
            import winsound
            flags = winsound.SND_FILENAME | winsound.SND_ASYNC
            if loop:
                flags |= winsound.SND_LOOP
            winsound.PlaySound(path, flags)
        except ImportError:
            # 非 Windows 平台静默跳过（winsound 不可用）
            pass

    def _stop_inner(self):
        """内部停止全部播放（不持锁时需外部加锁调用）"""
        try:
            import winsound
            winsound.PlaySound(None, winsound.SND_PURGE)
        except ImportError:
            pass
        self._active = None
        self._loop_active = None
