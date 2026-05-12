# -*- coding: utf-8 -*-
"""
darkness_overlay.py —— 黑暗收缩覆盖层
V1：单一矩形边框向内收缩，规整流畅（100ms 帧动画）。
后续可升级 V2（独立速度）/ V3（啃咬吞噬）/ V4（PNG 遮罩）。
详见 design.md 1.4 / decisions.md D015-D016

用法：
    overlay = DarknessOverlay(parent_frame)
    overlay.set_complete_callback(on_done)
    overlay.start(duration_seconds=50)
"""
import tkinter as tk


class DarknessOverlay:
    """黑暗收缩覆盖层——V1 矩形收缩"""

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
        self._start_margin = 0    # 初始边距（0 = 无黑暗）
        self._end_margin = 0      # 终点边距

    def set_complete_callback(self, callback):
        """设置收缩完成回调（失败 → player 死亡）"""
        self._on_complete = callback

    def start(self, duration_seconds: int = 50):
        """启动黑暗收缩动画"""
        self._duration = duration_seconds
        self._total_steps = int(duration_seconds * 1000 / self._frame_interval)
        self._current_step = 0

        w = self.parent.winfo_width()
        h = self.parent.winfo_height()

        if w < 10 or h < 10:
            w, h = 860, 640  # 默认窗口尺寸

        self._end_margin = max(w, h) // 2  # 收缩到中心点

        # 创建全尺寸 Canvas
        self.canvas = tk.Canvas(
            self.parent, width=w, height=h,
            bg="#000000", highlightthickness=0, bd=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.canvas.lift()

        self._running = True
        self._draw_frame()

    def _draw_frame(self):
        """绘制一帧黑暗收缩"""
        if not self._running:
            return

        w = self.parent.winfo_width()
        h = self.parent.winfo_height()

        if w < 10 or h < 10:
            w, h = 860, 640

        progress = min(self._current_step / self._total_steps, 1.0)
        margin = int(progress * self._end_margin)

        self.canvas.delete("all")

        if margin >= max(w, h) // 2:
            # 完全黑屏
            self.canvas.create_rectangle(0, 0, w, h,
                                         fill="#000000", outline="")
        elif progress >= 1.0:
            self.canvas.create_rectangle(0, 0, w, h,
                                         fill="#000000", outline="")
            self._on_complete_inner()
            return
        else:
            # 绘制四个边缘黑色条带，中心透出
            # 顶部条
            self.canvas.create_rectangle(0, 0, w, margin,
                                         fill="#000000", outline="")
            # 底部条
            self.canvas.create_rectangle(0, h - margin, w, h,
                                         fill="#000000", outline="")
            # 左侧条
            self.canvas.create_rectangle(0, margin, margin, h - margin,
                                         fill="#000000", outline="")
            # 右侧条
            self.canvas.create_rectangle(w - margin, margin, w, h - margin,
                                         fill="#000000", outline="")

        self._current_step += 1
        if self._current_step >= self._total_steps:
            self._on_complete_inner()
        else:
            self._after_id = self.canvas.after(
                self._frame_interval, self._draw_frame)

    def _on_complete_inner(self):
        """收缩完成，触发回调"""
        self._running = False
        if self._after_id:
            self.canvas.after_cancel(self._after_id)
            self._after_id = None
        # 确保全黑
        if self.canvas and self.canvas.winfo_exists():
            w = self.parent.winfo_width() or 860
            h = self.parent.winfo_height() or 640
            self.canvas.delete("all")
            self.canvas.create_rectangle(0, 0, w, h,
                                         fill="#000000", outline="")
        if self._on_complete:
            self._on_complete()

    def stop(self):
        """手动停止收缩"""
        self._running = False
        if self._after_id:
            self.canvas.after_cancel(self._after_id)
            self._after_id = None

    def destroy(self):
        """清理覆盖层"""
        self.stop()
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.place_forget()
            self.canvas.destroy()
            self.canvas = None
