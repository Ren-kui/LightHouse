# -*- coding: utf-8 -*-
"""
darkness_overlay.py —— 黑暗收缩覆盖层
V1：单一矩形边框向内收缩，规整流畅（100ms 帧动画）。
玩家需在 50 秒内连续点击中心区域加速"重启"——点击不足则黑暗完全收缩 = 失败。
后续可升级 V2（独立速度）/ V3（啃咬吞噬）/ V4（PNG 遮罩）。
详见 design.md 1.4 / decisions.md D015-D016

用法：
    overlay = DarknessOverlay(parent_frame)
    overlay.set_complete_callback(on_done)  # on_done(success: bool)
    overlay.start(duration_seconds=50)
"""
import tkinter as tk


class DarknessOverlay:
    """黑暗收缩覆盖层——V1 矩形收缩 + 点击重启交互"""

    CLICK_TARGET = 30   # 需要点击次数（代表"跑上楼重启"）
    CLICK_AREA = 200    # 中央可点击区域边长

    def __init__(self, parent: tk.Frame):
        self.parent = parent
        self.canvas = None
        self._running = False
        self._on_complete = None
        self._after_id = None

        # 收缩参数
        self._duration = 50       # 总秒数
        self._frame_interval = 100  # 每帧 ms
        self._total_steps = 0
        self._current_step = 0
        self._end_margin = 0
        self._version = 1          # V1=均匀, V2=不对称
        # V2 不对称参数：各边独立收缩速度（1.0=正常速度, <1=慢, >1=快）
        self._v2_speeds = {"top": 1.0, "left": 1.0, "bottom": 1.0, "right": 1.0}
        self._v2_margins = {"top": 0, "left": 0, "bottom": 0, "right": 0}

        # 交互状态
        self._clicks = 0
        self._success = False
        self._timer_text = None
        self._click_text = None
        self._inst_text = None
        self._click_rect = None

    def set_complete_callback(self, callback):
        self._on_complete = callback

    def start(self, duration_seconds: int = 50, version: int = 1):
        self._duration = duration_seconds
        self._version = version
        self._total_steps = int(duration_seconds * 1000 / self._frame_interval)
        self._current_step = 0
        self._clicks = 0
        self._success = False

        # V2：随机化各边速度（0.6~1.4x 偏差）
        if version >= 2:
            import random
            self._v2_speeds = {
                "top": random.uniform(0.6, 1.4),
                "left": random.uniform(0.6, 1.4),
                "bottom": random.uniform(0.6, 1.4),
                "right": random.uniform(0.6, 1.4),
            }
            self._v2_margins = {"top": 0, "left": 0, "bottom": 0, "right": 0}

        w = self.parent.winfo_width()
        h = self.parent.winfo_height()
        if w < 50 or h < 50:
            w, h = 860, 640

        self._end_margin = max(w, h) // 2

        self.canvas = tk.Canvas(
            self.parent, width=w, height=h,
            bg="#000000", highlightthickness=0, bd=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # 文字层（上层：指引 + 倒计时 + 进度）
        cx, cy = w // 2, h // 2
        self._inst_text = self.canvas.create_text(
            cx, cy - 60,
            text="黑暗在收缩——\n点击中央区域重启总开关！",
            fill="#cc0000", font=("Microsoft YaHei", 14, "bold"),
            justify=tk.CENTER)
        self._timer_text = self.canvas.create_text(
            cx, cy + 20,
            text="剩余: {} 秒 | 重启进度: 0/{}".format(self._duration, self.CLICK_TARGET),
            fill="#888888", font=("Microsoft YaHei", 11))
        self._click_text = self.canvas.create_text(
            cx, cy + 90,
            text="",
            fill="#cc6600", font=("Microsoft YaHei", 10))

        # 屏幕中央半透明可点击区域
        r = self.CLICK_AREA // 2
        self._click_rect = self.canvas.create_rectangle(
            cx - r, cy - 80, cx + r, cy + 120,
            fill="", outline="#cc0000", dash=(6, 3))
        self.canvas.tag_bind(self._click_rect, "<Button-1>", self._on_click_action)
        # 整个 canvas 也能点
        self.canvas.bind("<Button-1>", self._on_click_action)

        self._running = True
        self._draw_frame()

    def _on_click_action(self, event=None):
        if not self._running or self._success:
            return
        self._clicks += 1
        remaining = self.CLICK_TARGET - self._clicks
        if self._canvas_alive():
            self.canvas.itemconfig(self._click_text,
                text="⚡ 重启中... {}".format("█" * min(self._clicks * 2, 20)))
        if self._clicks >= self.CLICK_TARGET:
            self._success = True
            self._clicks = self.CLICK_TARGET
            self._finish()

    def _canvas_alive(self):
        return self.canvas and self.canvas.winfo_exists()

    def _draw_frame(self):
        if not self._running or not self._canvas_alive():
            return

        w = self.parent.winfo_width()
        h = self.parent.winfo_height()
        if w < 50 or h < 50:
            w, h = 860, 640

        progress = min(self._current_step / self._total_steps, 1.0)
        margin = int(progress * self._end_margin)

        self.canvas.delete("dark")

        if self._version >= 2:
            # V2 不对称：各边独立速度
            for side in ("top", "left", "bottom", "right"):
                spd = self._v2_speeds[side]
                self._v2_margins[side] = int(progress * self._end_margin * spd)
            t = self._v2_margins["top"]
            l = self._v2_margins["left"]
            b = self._v2_margins["bottom"]
            r = self._v2_margins["right"]
            # 检查是否完全收缩（任何一边到达中心）
            max_margin = max(t, l, b, r)
            if max_margin >= max(w, h) // 2:
                self.canvas.create_rectangle(0, 0, w, h,
                    fill="#000000", outline="", tags="dark")
                self._finish()
                return
            if progress >= 1.0:
                self._finish()
                return
            # 四边独立条带
            if t > 0:
                self.canvas.create_rectangle(0, 0, w, t,
                    fill="#000000", outline="", tags="dark")
            if b > 0:
                self.canvas.create_rectangle(0, h - b, w, h,
                    fill="#000000", outline="", tags="dark")
            if l > 0:
                self.canvas.create_rectangle(0, t, l, h - b,
                    fill="#000000", outline="", tags="dark")
            if r > 0:
                self.canvas.create_rectangle(w - r, t, w, h - b,
                    fill="#000000", outline="", tags="dark")
        else:
            # V1 均匀收缩
            if margin >= max(w, h) // 2 or progress >= 1.0:
                self.canvas.create_rectangle(0, 0, w, h,
                    fill="#000000", outline="", tags="dark")
                self._finish()
                return
            self.canvas.create_rectangle(0, 0, w, margin,
                fill="#000000", outline="", tags="dark")
            self.canvas.create_rectangle(0, h - margin, w, h,
                fill="#000000", outline="", tags="dark")
            self.canvas.create_rectangle(0, margin, margin, h - margin,
                fill="#000000", outline="", tags="dark")
            self.canvas.create_rectangle(w - margin, margin, w, h - margin,
                fill="#000000", outline="", tags="dark")

        # 更新倒计时
        remaining = max(0, int(self._duration * (1 - progress)))
        if self._canvas_alive():
            self.canvas.itemconfig(self._timer_text,
                text="剩余: {} 秒 | 重启进度: {}/{}".format(
                    remaining, self._clicks, self.CLICK_TARGET))

        self._current_step += 1
        if self._current_step >= self._total_steps:
            self._finish()
        else:
            self._after_id = self.canvas.after(
                self._frame_interval, self._draw_frame)

    def _finish(self):
        if not self._running:
            return
        self._running = False
        if self._after_id and self._canvas_alive():
            self.canvas.after_cancel(self._after_id)
            self._after_id = None

        if self._canvas_alive():
            self.canvas.delete("all")
            w = self.parent.winfo_width()
            h = self.parent.winfo_height()
            if w < 50 or h < 50:
                w, h = 860, 640
            if self._success:
                self.canvas.create_rectangle(0, 0, w, h,
                    fill="#0a0a0a", outline="")
                self.canvas.create_text(w // 2, h // 2,
                    text="总开关重启成功。\n灯亮了。",
                    fill="#00cc00", font=("Microsoft YaHei", 16, "bold"),
                    justify=tk.CENTER)
                self.canvas.after(1500, lambda: self._trigger_complete(True))
            else:
                self.canvas.create_rectangle(0, 0, w, h,
                    fill="#000000", outline="")
                self.canvas.create_text(w // 2, h // 2,
                    text="黑暗吞没了一切。",
                    fill="#cc0000", font=("Microsoft YaHei", 16, "bold"),
                    justify=tk.CENTER)
                self.canvas.after(1500, lambda: self._trigger_complete(False))

    def _trigger_complete(self, success: bool):
        if self._on_complete:
            self._on_complete(success)

    def stop(self):
        self._running = False
        if self._after_id and self._canvas_alive():
            self.canvas.after_cancel(self._after_id)
            self._after_id = None

    def destroy(self):
        self.stop()
        if self._canvas_alive():
            self.canvas.place_forget()
            self.canvas.destroy()
            self.canvas = None
