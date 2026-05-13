# -*- coding: utf-8 -*-
"""
minigame_base.py —— 小游戏基类 + 三个小游戏实现
详见 design.md 2.4 / D010 / D015
"""

import tkinter as tk
import random
import math


class MinigameBase:
    """小游戏抽象基类。每个小游戏拥有独立的 Canvas。"""

    def __init__(self, parent: tk.Frame):
        self.parent = parent
        self.canvas = tk.Canvas(
            parent,
            bg="#000000",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self._running = False
        self._complete_callback = None

    def set_complete_callback(self, cb):
        """cb(success: bool) —— 小游戏结束时调用"""
        self._complete_callback = cb

    def start(self):
        self._running = True
        self._on_start()

    def stop(self):
        self._running = False
        self._on_stop()

    def destroy(self):
        """销毁小游戏实例，先解绑后清理组件"""
        if self._running:
            self._running = False
            self._on_stop()
        self.canvas.destroy()
        self.canvas = None

    # ---- 子类覆写 ----

    def _on_start(self):
        pass

    def _on_stop(self):
        pass

    def _complete(self, success: bool):
        """小游戏结束，回调后安全停止"""
        if self._complete_callback:
            self._complete_callback(success)
        if self._running:
            self.stop()


# ============================================================
# MG1 · 配电连线（第2天）
# ============================================================

class MG1_PowerConnect(MinigameBase):
    """匹配接线端子，全部正确配对完成。"""

    PAIRS = [
        ("主线路 A", "#cc0000"),
        ("备用线路 B", "#cc6600"),
        ("地线 GND",  "#888888"),
        ("信号线 SIG", "#4488cc"),
    ]
    TIME_LIMIT = 60  # 秒

    def __init__(self, parent: tk.Frame):
        super().__init__(parent)
        self.canvas.config(width=600, height=400)

        self._left_terminals = []   # [(label, color, x, y, id)]
        self._right_terminals = []  # [(label, color, x, y, id)]
        self._selected_left = None  # 当前选中的左侧端子 (index)
        self._connections = []      # [(left_idx, right_idx, line_id)]
        self._matched_left = set()
        self._matched_right = set()

        self._time_left = self.TIME_LIMIT
        self._timer_id = None
        self._wrong_flash_id = None

        # 提示文字
        self._hint_id = None

    def _on_start(self):
        self._draw_ui()
        self.canvas.bind("<Button-1>", self._on_click)
        self._start_timer()

    def _on_stop(self):
        if self._timer_id:
            self.canvas.after_cancel(self._timer_id)
        if self._wrong_flash_id:
            self.canvas.after_cancel(self._wrong_flash_id)
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.unbind("<Button-1>")

    def _draw_ui(self):
        self.canvas.delete("all")
        w = int(self.canvas["width"])
        h = int(self.canvas["height"])

        # 标题
        self.canvas.create_text(w // 2, 30,
                                text="配电设备连线",
                                fill="#e8e8e8",
                                font=("Microsoft YaHei", 14, "bold"))

        # 说明
        self.canvas.create_text(w // 2, 60,
                                text="点击左侧端子，再点击右侧对应端子完成配对",
                                fill="#666666",
                                font=("Microsoft YaHei", 9))

        # 计时器
        self._timer_text = self.canvas.create_text(
            w // 2, h - 24,
            text="剩余: {}秒".format(self._time_left),
            fill="#cc6600",
            font=("Microsoft YaHei", 10, "bold"))

        # 提示区
        self._hint_id = self.canvas.create_text(
            w // 2, h - 48,
            text="",
            fill="#aaaaaa",
            font=("Microsoft YaHei", 9))

        # 画左右端子
        left_x = w // 4
        right_x = w * 3 // 4
        start_y = 100
        spacing = 50

        # 打乱右侧顺序
        right_labels = list(self.PAIRS)
        random.shuffle(right_labels)

        self._left_terminals = []
        self._right_terminals = []
        self._selected_left = None
        self._connections = []
        self._matched_left = set()
        self._matched_right = set()

        for i, (label, color) in enumerate(self.PAIRS):
            y = start_y + i * spacing
            # 左侧端子
            x1, y1 = left_x - 40, y - 12
            x2, y2 = left_x + 40, y + 12
            lid = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="#111111", outline=color, width=2)
            ltxt = self.canvas.create_text(
                left_x, y, text=label, fill="#e8e8e8",
                font=("Microsoft YaHei", 10, "bold"))
            self._left_terminals.append((label, color, left_x, y, lid, ltxt, x1, y1, x2, y2))

            # 右侧端子（乱序）
            rlabel, rcolor = right_labels[i]
            rx1, ry1 = right_x - 40, y - 12
            rx2, ry2 = right_x + 40, y + 12
            rid = self.canvas.create_rectangle(
                rx1, ry1, rx2, ry2,
                fill="#111111", outline=rcolor, width=2)
            rtxt = self.canvas.create_text(
                right_x, y, text=rlabel, fill="#e8e8e8",
                font=("Microsoft YaHei", 10, "bold"))
            self._right_terminals.append((rlabel, rcolor, right_x, y, rid, rtxt, rx1, ry1, rx2, ry2))

    def _on_click(self, event):
        if not self._running:
            return
        cx, cy = event.x, event.y

        # 检查是否点击了右侧端子
        for i, (label, color, tx, ty, rid, ttxt, x1, y1, x2, y2) in enumerate(self._right_terminals):
            if i in self._matched_right:
                continue
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                if self._selected_left is not None:
                    self._try_connect(self._selected_left, i)
                    self._selected_left = None
                    self._clear_highlight()
                return

        # 检查是否点击了左侧端子
        for i, (label, color, tx, ty, lid, ltxt, x1, y1, x2, y2) in enumerate(self._left_terminals):
            if i in self._matched_left:
                continue
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                self._selected_left = i
                self._highlight_left(i)
                return

        # 点击空白取消选择
        self._selected_left = None
        self._clear_highlight()

    def _highlight_left(self, idx):
        self._clear_highlight()
        _, color, _, _, lid, _, _, _, _, _ = self._left_terminals[idx]
        self.canvas.itemconfig(lid, fill="#1a0000", outline=self._brighten(color))

    def _clear_highlight(self):
        for _, color, _, _, lid, _, _, _, _, _ in self._left_terminals:
            self.canvas.itemconfig(lid, fill="#111111", outline=color)

    def _brighten(self, hex_color):
        r = min(255, int(hex_color[1:3], 16) + 60)
        g = min(255, int(hex_color[3:5], 16) + 60)
        b = min(255, int(hex_color[5:7], 16) + 60)
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    def _try_connect(self, left_idx, right_idx):
        left_label = self._left_terminals[left_idx][0]
        right_label = self._right_terminals[right_idx][0]

        if left_label == right_label:
            # 正确
            self._matched_left.add(left_idx)
            self._matched_right.add(right_idx)

            lx = self._left_terminals[left_idx][2] + 40
            ly = self._left_terminals[left_idx][3]
            rx = self._right_terminals[right_idx][2] - 40
            ry = self._right_terminals[right_idx][3]

            lid = self.canvas.create_line(
                lx, ly, rx, ry,
                fill=self._left_terminals[left_idx][1], width=2)
            self._connections.append((left_idx, right_idx, lid))

            # 标记为已完成
            lrect = self._left_terminals[left_idx][4]
            rrect = self._right_terminals[right_idx][4]
            self.canvas.itemconfig(lrect, fill="#002200", outline="#00aa00")
            self.canvas.itemconfig(rrect, fill="#002200", outline="#00aa00")

            self.canvas.itemconfig(self._hint_id, text="配对成功！")

            # 检查是否全部完成
            if len(self._matched_left) == len(self.PAIRS):
                self.canvas.itemconfig(self._hint_id,
                                       text="全部配对完成！设备供电正常。")
                self.canvas.after(800, lambda: self._complete(True))
        else:
            # 错误
            self._flash_wrong(left_idx, right_idx)

    def _flash_wrong(self, left_idx, right_idx):
        lrect = self._left_terminals[left_idx][4]
        rrect = self._right_terminals[right_idx][4]
        orig_l = self._left_terminals[left_idx][1]
        orig_r = self._right_terminals[right_idx][1]

        self.canvas.itemconfig(lrect, fill="#330000", outline="#ff0000")
        self.canvas.itemconfig(rrect, fill="#330000", outline="#ff0000")
        self.canvas.itemconfig(self._hint_id, text="配对错误，请重试。")

        def reset():
            self.canvas.itemconfig(lrect, fill="#111111", outline=orig_l)
            self.canvas.itemconfig(rrect, fill="#111111", outline=orig_r)

        self._wrong_flash_id = self.canvas.after(500, reset)

    def _start_timer(self):
        if not self._running:
            return
        self._time_left -= 1
        self.canvas.itemconfig(self._timer_text,
                               text="剩余: {}秒".format(self._time_left))
        if self._time_left <= 0:
            self.canvas.itemconfig(self._hint_id,
                                   text="时间耗尽。设备未能完成连线。")
            self.canvas.after(800, lambda: self._complete(False))
            return
        if self._time_left <= 10:
            self.canvas.itemconfig(self._timer_text, fill="#cc0000")
        self._timer_id = self.canvas.after(1000, self._start_timer)


# ============================================================
# MG2 · 太阳能反应测试（第2天）
# ============================================================

class MG2_SolarReaction(MinigameBase):
    """点击或空格键响应闪烁光点，漏掉影响效率评价。"""

    TARGET_HITS = 8    # 需要命中
    TOTAL_FLASHES = 14 # 总闪烁次数
    FLASH_DURATION = 900  # 每次闪烁持续 ms
    FLASH_INTERVAL = 1200 # 闪烁间隔 ms

    def __init__(self, parent: tk.Frame):
        super().__init__(parent)
        self.canvas.config(width=600, height=400)

        self._hits = 0
        self._misses = 0
        self._flash_count = 0
        self._current_dot = None   # 当前光点 (x, y, r, dot_inner, dot_outer)
        self._flash_timer = None
        self._spawn_timer = None

        self._score_text_id = None
        self._hint_id = None

    def _on_start(self):
        self._draw_ui()
        self.canvas.bind("<Button-1>", self._on_click)
        self.parent.winfo_toplevel().bind("<space>", self._on_space)
        self._spawn_flash()

    def _on_stop(self):
        if self._flash_timer:
            self.canvas.after_cancel(self._flash_timer)
        if self._spawn_timer:
            self.canvas.after_cancel(self._spawn_timer)
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.unbind("<Button-1>")
        self.parent.winfo_toplevel().unbind("<space>")

    def _draw_ui(self):
        self.canvas.delete("all")
        w = int(self.canvas["width"])
        h = int(self.canvas["height"])

        self.canvas.create_text(w // 2, 30,
                                text="太阳能板反应测试",
                                fill="#e8e8e8",
                                font=("Microsoft YaHei", 14, "bold"))
        self.canvas.create_text(w // 2, 58,
                                text="点击闪烁的光点来捕获读数——漏掉太多会影响效率评级",
                                fill="#666666",
                                font=("Microsoft YaHei", 9))

        # 状态提示
        self._hint_id = self.canvas.create_text(
            w // 2, h - 30,
            text="准备就绪...",
            fill="#aaaaaa",
            font=("Microsoft YaHei", 10))

        # 太阳能板示意背景
        self.canvas.create_rectangle(
            w // 2 - 180, 90, w // 2 + 180, h - 70,
            fill="#0a0a12", outline="#1a1a2e", width=2,
            dash=(4, 4))
        # 网格线
        for gx in range(w // 2 - 180, w // 2 + 181, 60):
            self.canvas.create_line(gx, 90, gx, h - 70,
                                    fill="#111122")

        self._score_text_id = self.canvas.create_text(
            w // 2, h - 56,
            text="已捕获: 0 / {}".format(self.TARGET_HITS),
            fill="#cc6600",
            font=("Microsoft YaHei", 10, "bold"))

    def _on_click(self, event):
        if not self._running:
            return
        if self._current_dot:
            x, y, r, dot_inner, dot_outer = self._current_dot
            dx = event.x - x
            dy = event.y - y
            if math.sqrt(dx * dx + dy * dy) <= r + 10:
                self._hit_dot()

    def _on_space(self, event=None):
        if not self._running:
            return
        if self._current_dot:
            self._hit_dot()

    def _spawn_flash(self):
        if not self._running:
            return
        self._flash_count += 1
        if self._flash_count > self.TOTAL_FLASHES:
            self._finish()
            return

        w = int(self.canvas["width"])
        h = int(self.canvas["height"])

        # 在面板区域内随机位置
        margin = 30
        x = random.randint(w // 2 - 180 + margin, w // 2 + 180 - margin)
        y = random.randint(90 + margin, h - 70 - margin)
        r = random.randint(16, 26)

        # 光点（外圈光晕 + 内核）
        dot_outer = self.canvas.create_oval(
            x - r - 6, y - r - 6, x + r + 6, y + r + 6,
            fill="", outline="#cc8800", width=3)
        dot_inner = self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill="#cc6600", outline="#ffaa00", width=2)

        self._current_dot = (x, y, r, dot_inner, dot_outer)
        self.canvas.itemconfig(self._hint_id, text="快点击！")

        # 闪烁自动消失
        self._flash_timer = self.canvas.after(
            self.FLASH_DURATION, self._miss_dot)

    def _hit_dot(self):
        """命中光点"""
        if not self._current_dot:
            return
        x, y, r, dot_inner, dot_outer = self._current_dot

        # 命中效果：绿闪
        self.canvas.itemconfig(dot_inner, fill="#00cc00", outline="#00ff00")
        self.canvas.itemconfig(dot_outer, outline="#00cc00")
        self.canvas.itemconfig(self._hint_id, text="捕获成功！")

        self._hits += 1
        self.canvas.itemconfig(self._score_text_id,
                               text="已捕获: {} / {}".format(self._hits, self.TARGET_HITS))

        # 取消消失定时器（防止已触发时 after_cancel 操作失效的 id）
        if self._flash_timer:
            self.canvas.after_cancel(self._flash_timer)
        self._flash_timer = None

        # 清除光点
        self.canvas.after(200, self._clear_dot_and_next)

    def _miss_dot(self):
        """未命中，光点消失"""
        if not self._current_dot:
            return
        self._misses += 1
        self._flash_timer = None  # 定时器已触发，标记失效
        x, y, r, dot_inner, dot_outer = self._current_dot
        if self.canvas.winfo_exists():
            self.canvas.itemconfig(self._hint_id, text="漏掉了...")
        self.canvas.after(200, self._clear_dot_and_next)

    def _clear_dot_and_next(self):
        if not self._running:
            return
        if self._current_dot:
            _, _, _, dot_inner, dot_outer = self._current_dot
            if self.canvas.winfo_exists():
                self.canvas.delete(dot_inner)
                self.canvas.delete(dot_outer)
        self._current_dot = None
        self._flash_timer = None

        # 取消已排队的下一次刷新定时器，防止 _hit_dot 和 _miss_dot
        # 同时调度 _clear_dot_and_next 导致重复召唤 _spawn_flash（MG2 光点叠层 bug）
        if self._spawn_timer:
            self.canvas.after_cancel(self._spawn_timer)
            self._spawn_timer = None

        # 下一个闪烁
        self._spawn_timer = self.canvas.after(
            self.FLASH_INTERVAL, self._spawn_flash)

    def _finish(self):
        if self._current_dot:
            _, _, _, dot_inner, dot_outer = self._current_dot
            self.canvas.delete(dot_inner)
            self.canvas.delete(dot_outer)
        self._current_dot = None

        success = self._hits >= self.TARGET_HITS
        if success:
            self.canvas.itemconfig(self._hint_id,
                                   text="测试完成：效率评级良好。")
        else:
            self.canvas.itemconfig(self._hint_id,
                                   text="测试完成：捕获不足，效率评级偏低。")
        self.canvas.after(1000, lambda: self._complete(success))


# ============================================================
# MG3 · 直升机平台平衡测试（第4天）
# ============================================================

class MG3_PlatformBalance(MinigameBase):
    """持续点击保持光标稳定在中心区域。"""

    SURVIVAL_TIME = 20  # 需要坚持的秒数
    DRIFT_SPEED = 1.5   # 每帧漂移像素
    ZONE_RADIUS = 60    # 安全区半径

    def __init__(self, parent: tk.Frame):
        super().__init__(parent)
        self.canvas.config(width=600, height=400)

        self._elapsed = 0.0
        self._marker_x = 0
        self._marker_y = 0
        self._drift_x = 0.0
        self._drift_y = 0.0
        self._marker_id = None
        self._zone_id = None
        self._timer_id = None

    def _on_start(self):
        self._draw_ui()
        self.canvas.bind("<Button-1>", self._on_click)
        self.parent.winfo_toplevel().bind("<space>", self._on_space)
        self._tick()

    def _on_stop(self):
        if self._timer_id:
            self.canvas.after_cancel(self._timer_id)
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.unbind("<Button-1>")
        self.parent.winfo_toplevel().unbind("<space>")

    def _draw_ui(self):
        self.canvas.delete("all")
        w = int(self.canvas["width"])
        h = int(self.canvas["height"])

        self.canvas.create_text(w // 2, 30,
                                text="直升机平台平衡测试",
                                fill="#e8e8e8",
                                font=("Microsoft YaHei", 14, "bold"))
        self.canvas.create_text(w // 2, 58,
                                text="连续点击 / 空格键保持光标在中心区域内",
                                fill="#666666",
                                font=("Microsoft YaHei", 9))

        self._cx = w // 2
        self._cy = h // 2 + 20

        # 安全区
        rz = self.ZONE_RADIUS
        self._zone_id = self.canvas.create_oval(
            self._cx - rz, self._cy - rz,
            self._cx + rz, self._cy + rz,
            fill="#0a1a0a", outline="#225522", width=2, dash=(4, 4))

        # 十字准心
        self.canvas.create_line(
            self._cx, self._cy - rz, self._cx, self._cy + rz,
            fill="#1a1a1a")
        self.canvas.create_line(
            self._cx - rz, self._cy, self._cx + rz, self._cy,
            fill="#1a1a1a")

        # 标记（玩家控制的光标）
        self._marker_x = self._cx
        self._marker_y = self._cy
        self._marker_id = self.canvas.create_rectangle(
            self._cx - 8, self._cy - 8,
            self._cx + 8, self._cy + 8,
            fill="#cc6600", outline="#ff8800", width=2)

        # 状态文字
        self._status_id = self.canvas.create_text(
            w // 2, h - 30,
            text="坚持 {} 秒 | 已过 0.0 秒".format(self.SURVIVAL_TIME),
            fill="#aaaaaa",
            font=("Microsoft YaHei", 10))

        # 随机初始漂移方向
        angle = random.uniform(0, 2 * math.pi)
        self._drift_x = math.cos(angle) * self.DRIFT_SPEED
        self._drift_y = math.sin(angle) * self.DRIFT_SPEED

    def _on_click(self, event):
        if not self._running:
            return
        self._push_toward_center()

    def _on_space(self, event=None):
        if not self._running:
            return
        self._push_toward_center()

    def _push_toward_center(self):
        push_strength = 12
        dx = self._cx - self._marker_x
        dy = self._cy - self._marker_y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            self._marker_x += (dx / dist) * push_strength
            self._marker_y += (dy / dist) * push_strength
        # 随机偏移漂移方向
        self._drift_x = random.uniform(-1.5, 1.5)
        self._drift_y = random.uniform(-1.5, 1.5)

    def _tick(self):
        if not self._running:
            return
        self._elapsed += 0.05

        # 漂移
        self._marker_x += self._drift_x
        self._marker_y += self._drift_y

        # 更新标记位置
        self.canvas.coords(self._marker_id,
                           self._marker_x - 8, self._marker_y - 8,
                           self._marker_x + 8, self._marker_y + 8)

        # 更新状态文字
        self.canvas.itemconfig(self._status_id,
                               text="坚持 {} 秒 | 已过 {:.1f} 秒".format(
                                   self.SURVIVAL_TIME, self._elapsed))

        # 检查是否出界
        dx = self._marker_x - self._cx
        dy = self._marker_y - self._cy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > self.ZONE_RADIUS:
            self._marker_out()
            return

        # 检查是否完成
        if self._elapsed >= self.SURVIVAL_TIME:
            self._marker_success()
            return

        # 倒计时变红
        if self._elapsed >= self.SURVIVAL_TIME - 5:
            self.canvas.itemconfig(self._status_id, fill="#cc0000")

        self._timer_id = self.canvas.after(50, self._tick)

    def _marker_out(self):
        self.canvas.itemconfig(self._marker_id, fill="#cc0000", outline="#ff0000")
        self.canvas.itemconfig(self._status_id,
                               text="平台失衡！",
                               fill="#cc0000")
        self.canvas.after(800, lambda: self._complete(False))

    def _marker_success(self):
        self.canvas.itemconfig(self._marker_id, fill="#00cc00", outline="#00ff00")
        self.canvas.itemconfig(self._status_id,
                               text="稳定测试通过！",
                               fill="#00cc00")
        self.canvas.after(800, lambda: self._complete(True))

# ============================================================
# MG4-A · 海鸟躲避（第4章 D9）
# ============================================================
class MG4A_SeabirdDodge(MinigameBase):
    TARGET_DODGES = 5
    BIRD_COUNT = 8

    def __init__(self, parent):
        import tkinter as tk
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        import tkinter as tk
        w = int(self.canvas["width"])
        h = int(self.canvas["height"])
        self.canvas.create_text(w // 2, 40, text="移动鼠标躲避海鸟",
                                fill="#cc6600", font=("Microsoft YaHei", 12, "bold"))
        self._score_id = self.canvas.create_text(w // 2, h - 56,
            text=f"已躲避: 0 / {self.TARGET_DODGES}",
            fill="#cc6600", font=("Microsoft YaHei", 10, "bold"))
        self._px, self._py = w // 2, h // 2
        r = 12
        self._player_id = self.canvas.create_oval(
            self._px - r, self._py - r, self._px + r, self._py + r,
            fill="#e8e8e8", outline="#cc6600", width=2)
        self.canvas.bind("<Motion>", self._on_move)
        self.canvas.focus_set()
        self._dodges = 0
        self._hits = 0
        self._birds = []
        self._timer = None

    def start(self):
        super().start()
        if self._running:
            self._loop()

    def _on_move(self, event):
        if not self._running: return
        self._px = event.x; self._py = event.y
        r = 12
        self.canvas.coords(self._player_id, self._px - r, self._py - r, self._px + r, self._py + r)

    def _loop(self):
        if not self._running: return
        if not self.canvas or not self.canvas.winfo_exists():
            return
        if len(self._birds) < self.BIRD_COUNT: self._spawn()
        self._move_all(); self._check_hits()
        if not self.canvas or not self.canvas.winfo_exists():
            return
        self._timer = self.canvas.after(100, self._loop)

    def _spawn(self):
        import random
        w = int(self.canvas["width"]); h = int(self.canvas["height"])
        side = random.randint(0, 3)
        if side == 0:    x, y = random.randint(0, w), -10
        elif side == 1:  x, y = w + 10, random.randint(0, h)
        elif side == 2:  x, y = random.randint(0, w), h + 10
        else:            x, y = -10, random.randint(0, h)
        r = 8
        bid = self.canvas.create_oval(x - r, y - r, x + r, y + r,
            fill="#444444", outline="#888888", width=1)
        self._birds.append({"id": bid, "x": x, "y": y, "dx": (self._px - x) / 15, "dy": (self._py - y) / 15})

    def _move_all(self):
        if not self.canvas or not self.canvas.winfo_exists():
            return
        w = int(self.canvas["width"]); h = int(self.canvas["height"])
        for b in self._birds[:]:
            b["x"] += b["dx"]; b["y"] += b["dy"]
            r = 8
            self.canvas.coords(b["id"], b["x"] - r, b["y"] - r, b["x"] + r, b["y"] + r)
            if b["x"] < -20 or b["x"] > w + 20 or b["y"] < -20 or b["y"] > h + 20:
                self.canvas.delete(b["id"]); self._birds.remove(b)
                self._dodges += 1
                self.canvas.itemconfig(self._score_id,
                    text=f"已躲避: {self._dodges} / {self.TARGET_DODGES}")
                if self._dodges >= self.TARGET_DODGES:
                    self._complete(True)

    def _check_hits(self):
        r = 20
        for b in self._birds[:]:
            dx = b["x"] - self._px; dy = b["y"] - self._py
            if (dx * dx + dy * dy) < r * r:
                self._hits += 1
                self.canvas.delete(b["id"]); self._birds.remove(b)
                if self._hits >= 3:
                    self._complete(False)

    def _on_stop(self, running=True):
        if running: return
        if self._timer and self.canvas.winfo_exists():
            self.canvas.after_cancel(self._timer); self._timer = None
        self.canvas.unbind("<Motion>")
