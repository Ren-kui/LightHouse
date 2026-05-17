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
        self._running = False
        self._on_stop()
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.destroy()
        self.canvas = None

    # ---- 子类覆写 ----

    def _on_start(self):
        pass

    def _on_stop(self):
        pass

    def _complete(self, success: bool):
        """小游戏结束，延迟回调防止在 _loop 调用栈内销毁 canvas"""
        if self._running:
            self._running = False
        if self._complete_callback and self.canvas and self.canvas.winfo_exists():
            self.canvas.after(10, self._complete_callback, success)


# ============================================================
# MG1 · 配电连线（第2天）—— B2 重写：6对端子+6中继点+亮灭灯
# ============================================================

class MG1_PowerConnect(MinigameBase):
    """配电连线：左端子→中继点→右端子，亮灭灯循环干扰。"""

    PAIRS = [
        ("主线路 A", "#cc0000"),
        ("备用线路 B", "#cc6600"),
        ("地线 GND",  "#888888"),
        ("信号线 SIG", "#4488cc"),
        ("照明线路 L", "#ccaa00"),
        ("应急线路 E", "#aa44cc"),
    ]
    TIME_LIMIT = 36
    LIGHT_DURATION = 1500   # 亮灯持续 ms
    DARK_DURATION = 2500    # 灭灯持续 ms

    def __init__(self, parent: tk.Frame, pre_connect: int = 0):
        super().__init__(parent)

        self.pre_connect = pre_connect  # 预完成连接数（教学用）
        self._left_terminals = []   # 左侧端子
        self._right_terminals = []  # 右侧端子（乱序）
        self._relays = []           # 中继点
        self._selected_left = None  # 当前选中的左端子 index
        self._selected_relay = None # 当前选中的中继点 index
        self._connections = []      # 连线列表（含半程线）
        self._half_lines = []       # 半程连线（左→中继，未完成）
        self._matched_left = set()
        self._matched_right = set()
        self._matched_relays = set()
        self._phase = "light"       # "light" / "dark"
        self._cycle_job = None
        self._time_left = self.TIME_LIMIT
        self._timer_id = None
        self._wrong_flash_id = None
        self._hint_id = None
        self._timer_text = None

    def _on_start(self):
        self._draw_ui()
        self.canvas.bind("<Button-1>", self._on_click)
        self._start_timer()
        self._start_light_cycle()

    def _on_stop(self):
        if self._timer_id:
            self.canvas.after_cancel(self._timer_id)
        if self._wrong_flash_id:
            self.canvas.after_cancel(self._wrong_flash_id)
        if self._cycle_job:
            self.canvas.after_cancel(self._cycle_job)
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.unbind("<Button-1>")

    # ===== 亮灭灯循环 =====

    def _start_light_cycle(self):
        if not self._running:
            return
        self._phase = "light"
        self._apply_light_phase()
        self._cycle_job = self.canvas.after(
            self.LIGHT_DURATION, self._start_dark_cycle)

    def _start_dark_cycle(self):
        if not self._running:
            return
        self._phase = "dark"
        self._apply_dark_phase()
        self._cycle_job = self.canvas.after(
            self.DARK_DURATION, self._start_light_cycle)

    def _apply_light_phase(self):
        """亮灯：恢复所有未匹配端子和中继的正常颜色和文字，保留已选高亮"""
        for i, (label, color, _, _, lid, ltxt, _, _, _, _) in enumerate(self._left_terminals):
            if i not in self._matched_left:
                self.canvas.itemconfig(lid, fill="#111111", outline=color)
                self.canvas.itemconfig(ltxt, text=label, fill="#e8e8e8")
        for i, (rlabel, rcolor, _, _, rid, rtxt, _, _, _, _) in enumerate(self._right_terminals):
            if i not in self._matched_right:
                self.canvas.itemconfig(rid, fill="#111111", outline=rcolor)
                self.canvas.itemconfig(rtxt, text=rlabel, fill="#e8e8e8")
        for i, (color, _, _, rid) in enumerate(self._relays):
            if i not in self._matched_relays:
                self.canvas.itemconfig(rid, fill="#111111", outline=color, width=4)
        # 恢复已选高亮
        if self._selected_left is not None:
            self._highlight_left(self._selected_left)
        if self._selected_relay is not None:
            self._highlight_relay(self._selected_relay)

    def _apply_dark_phase(self):
        """灭灯：所有未匹配端子显示'故障'、灰色框；中继点颜色消失"""
        for i, (label, color, _, _, lid, ltxt, _, _, _, _) in enumerate(self._left_terminals):
            if i not in self._matched_left:
                self.canvas.itemconfig(lid, fill="#0a0a0a", outline="#333333")
                self.canvas.itemconfig(ltxt, text="故障", fill="#555555")
        for i, (rlabel, rcolor, _, _, rid, rtxt, _, _, _, _) in enumerate(self._right_terminals):
            if i not in self._matched_right:
                self.canvas.itemconfig(rid, fill="#0a0a0a", outline="#333333")
                self.canvas.itemconfig(rtxt, text="故障", fill="#555555")
        for i, (color, _, _, rid) in enumerate(self._relays):
            if i not in self._matched_relays:
                self.canvas.itemconfig(rid, fill="#0a0a0a", outline="#1a1a1a", width=4)

    def _stop_cycle(self):
        if self._cycle_job:
            self.canvas.after_cancel(self._cycle_job)
            self._cycle_job = None
        self._phase = "light"
        self._apply_light_phase()

    # ===== 绘制 =====

    def _draw_ui(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() if self.canvas.winfo_width() >= 50 else 688
        h = self.canvas.winfo_height() if self.canvas.winfo_height() >= 50 else 538

        self.canvas.create_text(w // 2, 22,
                                text="配电设备连线",
                                fill="#e8e8e8",
                                font=("Microsoft YaHei", 13, "bold"))
        self.canvas.create_text(w // 2, 44,
                                text="左端子 → 中继点 → 右端子  灭灯时靠记忆",
                                fill="#666666",
                                font=("Microsoft YaHei", 8))

        self._timer_text = self.canvas.create_text(
            w // 2, h - 18,
            text="剩余: {}秒".format(self._time_left),
            fill="#cc6600",
            font=("Microsoft YaHei", 9, "bold"))
        self._hint_id = self.canvas.create_text(
            w // 2, 56,
            text="",
            fill="#aaaaaa",
            font=("Microsoft YaHei", 8))

        # 三列布局
        left_x = w // 6 + 20
        relay_x = w // 2
        right_x = w * 5 // 6 - 20
        start_y = 74
        spacing = max(38, (h - start_y - 60) // len(self.PAIRS))

        right_labels = list(self.PAIRS)
        random.shuffle(right_labels)
        # 中继点 Y 顺序也打乱（与左右端子位置错开，增加难度）
        relay_ys = [start_y + i * spacing for i in range(len(self.PAIRS))]
        random.shuffle(relay_ys)

        self._left_terminals = []
        self._right_terminals = []
        self._relays = []
        self._matched_left = set()
        self._matched_right = set()
        self._matched_relays = set()
        self._selected_left = None
        self._selected_relay = None
        self._connections = []

        for i, (label, color) in enumerate(self.PAIRS):
            y = start_y + i * spacing
            bw, bh = 36, 11  # 端子半宽半高

            # 左侧端子
            lx1, ly1 = left_x - bw, y - bh
            lx2, ly2 = left_x + bw, y + bh
            lid = self.canvas.create_rectangle(
                lx1, ly1, lx2, ly2,
                fill="#111111", outline=color, width=2)
            ltxt = self.canvas.create_text(
                left_x, y, text=label, fill="#e8e8e8",
                font=("Microsoft YaHei", 9, "bold"))
            self._left_terminals.append((label, color, left_x, y, lid, ltxt, lx1, ly1, lx2, ly2))

            # 中继点（无标签，仅颜色环），X 居中，Y 顺序与左端子不同
            ry = relay_ys[i]
            rid = self.canvas.create_oval(
                relay_x - 8, ry - 8, relay_x + 8, ry + 8,
                fill="#111111", outline=color, width=4)
            self._relays.append((color, relay_x, ry, rid))

            # 右侧端子（乱序）
            rlabel, rcolor = right_labels[i]
            rx1, ry1 = right_x - bw, y - bh
            rx2, ry2 = right_x + bw, y + bh
            r_rid = self.canvas.create_rectangle(
                rx1, ry1, rx2, ry2,
                fill="#111111", outline=rcolor, width=2)
            rtxt = self.canvas.create_text(
                right_x, y, text=rlabel, fill="#e8e8e8",
                font=("Microsoft YaHei", 9, "bold"))
            self._right_terminals.append((rlabel, rcolor, right_x, y, r_rid, rtxt, rx1, ry1, rx2, ry2))

        # 区隔标签
        self.canvas.create_text(left_x, start_y - 22, text="端子",
                                fill="#444444", font=("Microsoft YaHei", 7))
        self.canvas.create_text(relay_x, start_y - 22, text="中继",
                                fill="#444444", font=("Microsoft YaHei", 7))
        self.canvas.create_text(right_x, start_y - 22, text="端子",
                                fill="#444444", font=("Microsoft YaHei", 7))

        # 预连接教学：首次 MG1 时预先完成一对连线，向玩家展示规则
        for n in range(min(self.pre_connect, len(self.PAIRS))):
            self._pre_connect_pair(n)

    def _pre_connect_pair(self, n):
        target_label, color = self.PAIRS[n]
        left_idx = None
        relay_idx = None
        right_idx = None
        for i, (lbl, clr, _, _, _, _, _, _, _, _) in enumerate(self._left_terminals):
            if lbl == target_label and clr == color:
                left_idx = i; break
        for i, (clr, _, _, _) in enumerate(self._relays):
            if clr == color:
                relay_idx = i; break
        for i, (rlbl, rclr, _, _, _, _, _, _, _, _) in enumerate(self._right_terminals):
            if rlbl == target_label and rclr == color:
                right_idx = i; break
        if left_idx is not None and relay_idx is not None and right_idx is not None:
            self._matched_left.add(left_idx)
            self._matched_relays.add(relay_idx)
            self._matched_right.add(right_idx)
            lx = self._left_terminals[left_idx][2] + 36
            ly = self._left_terminals[left_idx][3]
            rx = self._relays[relay_idx][1]
            ry = self._relays[relay_idx][2]
            ln1 = self.canvas.create_line(lx, ly, rx, ry, fill=color, width=2)
            ln2 = self.canvas.create_line(rx, ry,
                                          self._right_terminals[right_idx][2] - 36,
                                          self._right_terminals[right_idx][3],
                                          fill=color, width=2)
            self._connections.append(ln1)
            self._connections.append(ln2)
            lrect = self._left_terminals[left_idx][4]
            rrect = self._right_terminals[right_idx][4]
            r_relay = self._relays[relay_idx][3]
            self.canvas.itemconfig(lrect, fill="#002200", outline="#00aa00")
            self.canvas.itemconfig(r_relay, fill="#002200", outline="#00aa00")
            self.canvas.itemconfig(rrect, fill="#002200", outline="#00aa00")
            if n == 0:
                self.canvas.itemconfig(self._hint_id,
                    text="左端子 → 中继点 → 右端子（同色配对）")

    # ===== 点击交互 =====

    def _on_click(self, event):
        if not self._running:
            return
        cx, cy = event.x, event.y

        # 灭灯期间仍可操作（靠记忆），高亮颜色加亮以穿透暗色
        dark = self._phase == "dark"

        # 检查中继点
        for i, (color, rx, ry, rid) in enumerate(self._relays):
            if i in self._matched_relays:
                continue
            if (cx - rx) ** 2 + (cy - ry) ** 2 <= 16 ** 2:
                if self._selected_left is not None:
                    left_color = self._left_terminals[self._selected_left][1]
                    if left_color == color:
                        self._selected_relay = i
                        self._highlight_relay(i)
                        # 画半程连线：左端子 → 中继点
                        self._clear_half_lines()
                        lx2 = self._left_terminals[self._selected_left][8]  # x2
                        ly = self._left_terminals[self._selected_left][3]
                        half = self.canvas.create_line(
                            lx2, ly, rx, ry, fill=left_color, width=2, dash=(4, 4))
                        self._half_lines.append(half)
                        self.canvas.itemconfig(self._hint_id, text="中继点正确！　点右侧端子...")
                        return
                    else:
                        self.canvas.itemconfig(self._hint_id, text="中继点颜色不匹配")
                        self._flash_relay_wrong(i)
                        return
                else:
                    self.canvas.itemconfig(self._hint_id, text="请先点击左侧端子")
                    return

        # 检查右侧端子
        for i, (rlabel, rcolor, tx, ty, rid, rtxt, x1, y1, x2, y2) in enumerate(self._right_terminals):
            if i in self._matched_right:
                continue
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                if self._selected_left is not None and self._selected_relay is not None:
                    left_label = self._left_terminals[self._selected_left][0]
                    relay_color = self._relays[self._selected_relay][0]
                    if left_label == rlabel and relay_color == rcolor:
                        self._clear_half_lines()
                        self._try_connect(self._selected_left, self._selected_relay, i)
                    else:
                        self._flash_wrong_pair()
                    self._selected_left = None
                    self._selected_relay = None
                    self._clear_all_highlights()
                    return
                elif self._selected_left is None:
                    self.canvas.itemconfig(self._hint_id, text="请先点击左侧端子")
                    return
                elif self._selected_relay is None:
                    self.canvas.itemconfig(self._hint_id, text="请先点击中继点")
                    return

        # 检查左侧端子
        for i, (label, color, tx, ty, lid, ltxt, x1, y1, x2, y2) in enumerate(self._left_terminals):
            if i in self._matched_left:
                continue
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                self._selected_left = i
                self._selected_relay = None
                self._highlight_left(i)
                self.canvas.itemconfig(self._hint_id, text="已选左端子　→　点中继点")
                return

        # 点击空白取消
        self._selected_left = None
        self._selected_relay = None
        self._clear_all_highlights()
        self.canvas.itemconfig(self._hint_id, text="")

    # ===== 高亮 =====

    def _highlight_left(self, idx):
        self._clear_all_highlights()
        _, color, _, _, lid, _, _, _, _, _ = self._left_terminals[idx]
        self.canvas.itemconfig(lid, fill="#1a0000", outline=self._brighten(color))

    def _highlight_relay(self, idx):
        color, _, _, rid = self._relays[idx]
        if self._phase == "dark":
            self.canvas.itemconfig(rid, fill="#332200", outline="#cc6600", width=4)
        else:
            self.canvas.itemconfig(rid, fill="#1a1a00", outline=self._brighten(color))

    def _clear_all_highlights(self):
        self._clear_half_lines()
        for _, color, _, _, lid, _, _, _, _, _ in self._left_terminals:
            self.canvas.itemconfig(lid, fill="#111111", outline=color)
        # 重置全部中继点（灭灯时保持暗色）
        for color, _, _, rid in self._relays:
            if self._phase == "dark":
                self.canvas.itemconfig(rid, fill="#0a0a0a", outline="#1a1a1a", width=4)
            else:
                self.canvas.itemconfig(rid, fill="#111111", outline=color, width=4)

    def _clear_half_lines(self):
        for lid in self._half_lines:
            if self.canvas and self.canvas.winfo_exists():
                self.canvas.delete(lid)
        self._half_lines.clear()

    def _brighten(self, hex_color):
        r = min(255, int(hex_color[1:3], 16) + 60)
        g = min(255, int(hex_color[3:5], 16) + 60)
        b = min(255, int(hex_color[5:7], 16) + 60)
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    # ===== 连接 =====

    def _try_connect(self, left_idx, relay_idx, right_idx):
        left_label = self._left_terminals[left_idx][0]
        right_label = self._right_terminals[right_idx][0]
        if left_label != right_label:
            self._flash_wrong_pair()
            return

        self._matched_left.add(left_idx)
        self._matched_relays.add(relay_idx)
        self._matched_right.add(right_idx)

        # 画连线：左→中继→右
        lx = self._left_terminals[left_idx][2] + 36
        ly = self._left_terminals[left_idx][3]
        rx = self._relays[relay_idx][1]
        ry = self._relays[relay_idx][2]
        color = self._left_terminals[left_idx][1]

        ln1 = self.canvas.create_line(lx, ly, rx, ry, fill=color, width=2)
        ln2 = self.canvas.create_line(rx, ry,
                                      self._right_terminals[right_idx][2] - 36,
                                      self._right_terminals[right_idx][3],
                                      fill=color, width=2)
        self._connections.append(ln1)
        self._connections.append(ln2)

        # 标记完成
        lrect = self._left_terminals[left_idx][4]
        rrect = self._right_terminals[right_idx][4]
        r_relay = self._relays[relay_idx][3]
        self.canvas.itemconfig(lrect, fill="#002200", outline="#00aa00")
        self.canvas.itemconfig(r_relay, fill="#002200", outline="#00aa00")
        self.canvas.itemconfig(rrect, fill="#002200", outline="#00aa00")
        self.canvas.itemconfig(self._hint_id, text="配对成功！")

        if len(self._matched_left) == len(self.PAIRS):
            self._stop_cycle()
            self.canvas.itemconfig(self._hint_id,
                                   text="全部配对完成！设备供电正常。")
            self.canvas.after(800, lambda: self._complete(True))

    def _flash_wrong_pair(self):
        self.canvas.itemconfig(self._hint_id, text="配对错误，请重试。")

    def _flash_relay_wrong(self, idx):
        color, _, _, rid = self._relays[idx]
        self.canvas.itemconfig(rid, fill="#330000", outline="#ff0000")
        def reset():
            if self.canvas and self.canvas.winfo_exists():
                self.canvas.itemconfig(rid, fill="#111111", outline=color, width=4)
        self._wrong_flash_id = self.canvas.after(400, reset)

    # ===== 计时器 =====

    def _start_timer(self):
        if not self._running:
            return
        self._time_left -= 1
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.itemconfig(self._timer_text,
                                   text="剩余: {}秒".format(self._time_left))
        if self._time_left <= 0:
            self._stop_cycle()
            self.canvas.itemconfig(self._hint_id,
                                   text="时间耗尽。设备未能完成连线。")
            self.canvas.after(800, lambda: self._complete(False))
            return
        if self._time_left <= 10:
            self.canvas.itemconfig(self._timer_text, fill="#cc0000")
        self._timer_id = self.canvas.after(1000, self._start_timer)


# ============================================================
# MG2 · 太阳能反应测试（第2天）—— B3 重写：缩小+蓝干扰+移动+双点
# ============================================================

class MG2_SolarReaction(MinigameBase):
    """太阳能反应测试：黄点命中/蓝点避开，光点缩小+移动。"""

    TARGET_HITS = 6     # B3降档
    TOTAL_FLASHES = 12  # B3降档
    FLASH_DURATION = 900   # 光点存活 ms
    FLASH_INTERVAL = 1200  # 闪烁间隔 ms

    def __init__(self, parent: tk.Frame):
        super().__init__(parent)

        self._hits = 0
        self._flash_count = 0
        self._dots = []            # 当前活跃的光点列表
        self._dots_alive = False   # 是否有活跃光点
        self._flash_timer = None   # 消失计时器
        self._spawn_timer = None   # 生成计时器
        self._shrink_job = None    # 缩小计时器
        self._move_job = None      # 移动计时器

        self._score_text_id = None
        self._hint_id = None
        self._warning_text_id = None  # 蓝色干扰提示

    def _on_start(self):
        self._draw_ui()
        self.canvas.bind("<Button-1>", self._on_click)
        self.parent.winfo_toplevel().bind("<space>", self._on_space)
        self._spawn_flash()

    def _on_stop(self):
        for job in [self._flash_timer, self._spawn_timer, self._shrink_job, self._move_job]:
            if job:
                self.canvas.after_cancel(job)
        self._flash_timer = self._spawn_timer = self._shrink_job = self._move_job = None
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.unbind("<Button-1>")
        self.parent.winfo_toplevel().unbind("<space>")

    # ===== 绘制 =====

    def _draw_ui(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() if self.canvas.winfo_width() >= 50 else 688
        h = self.canvas.winfo_height() if self.canvas.winfo_height() >= 50 else 538

        self.canvas.create_text(w // 2, 26,
                                text="太阳能板反应测试",
                                fill="#e8e8e8",
                                font=("Microsoft YaHei", 13, "bold"))
        self.canvas.create_text(w // 2, 50,
                                text="点击黄色光点 — 避开蓝色光点！",
                                fill="#666666",
                                font=("Microsoft YaHei", 8))
        self._hint_id = self.canvas.create_text(
            w // 2, h - 28,
            text="准备就绪...",
            fill="#aaaaaa",
            font=("Microsoft YaHei", 9))

        # 太阳能板背景网格
        px, py = w // 2 - 184, 64
        pw, ph = 368, h - 64 - 64
        self.canvas.create_rectangle(
            px, py, px + pw, py + ph,
            fill="#0a0a12", outline="#1a1a2e", width=2, dash=(4, 4))
        for gx in range(px, px + pw + 1, 60):
            self.canvas.create_line(gx, py, gx, py + ph, fill="#111122")

        self._score_text_id = self.canvas.create_text(
            w // 2, h - 52,
            text="已捕获: 0 / {}".format(self.TARGET_HITS),
            fill="#cc6600",
            font=("Microsoft YaHei", 10, "bold"))
        self._warning_text_id = self.canvas.create_text(
            w // 2, h - 72,
            text="",
            fill="#4488cc",
            font=("Microsoft YaHei", 8))

    # ===== 点击 =====

    def _on_click(self, event):
        if not self._running or not self._dots_alive:
            return
        cx, cy = event.x, event.y
        for d in self._dots[:]:
            dx, dy = cx - d["x"], cy - d["y"]
            if math.sqrt(dx * dx + dy * dy) <= d["r"] + 12:
                if d["type"] == "blue":
                    self._hit_blue(d)
                else:
                    self._hit_yellow(d)
                return

    def _on_space(self, event=None):
        if not self._running or not self._dots_alive:
            return
        # 空格命中所有当前黄点（不处罚）
        for d in self._dots[:]:
            if d["type"] == "yellow":
                self._hit_yellow(d)
                return

    def _hit_yellow(self, d):
        self._hits += 1
        self.canvas.itemconfig(d["inner_id"], fill="#00cc00", outline="#00ff00")
        self.canvas.itemconfig(d["outer_id"], outline="#00cc00")
        self.canvas.itemconfig(self._hint_id, text="捕获成功！")
        self.canvas.itemconfig(self._score_text_id,
                               text="已捕获: {} / {}".format(self._hits, self.TARGET_HITS))
        self._clear_dot(d)
        if self._hits >= self.TARGET_HITS:
            self._finish_all(True)

    def _hit_blue(self, d):
        self._hits = max(0, self._hits - 1)
        self.canvas.itemconfig(d["inner_id"], fill="#ff0000", outline="#ff3333")
        self._clear_dot(d)
        self.canvas.itemconfig(self._hint_id, text="那是蓝色光点！读数-1")
        self.canvas.itemconfig(self._score_text_id,
                               text="已捕获: {} / {}".format(self._hits, self.TARGET_HITS))
        self.canvas.itemconfig(self._warning_text_id, text="")

    # ===== 生成光点 =====

    def _spawn_flash(self):
        if not self._running:
            return
        self._flash_count += 1
        if self._flash_count > self.TOTAL_FLASHES:
            self._finish_all(self._hits >= self.TARGET_HITS)
            return

        w = self.canvas.winfo_width() if self.canvas.winfo_width() >= 50 else 688
        h = self.canvas.winfo_height() if self.canvas.winfo_height() >= 50 else 538
        px, py = w // 2 - 184, 64
        pw, ph = 368, h - 64 - 64
        margin = 30

        self._dots = []
        self._dots_alive = True

        # C: 15% 概率双黄点
        yellow_count = 2 if random.random() <= 0.15 else 1
        for _ in range(yellow_count):
            x = random.randint(px + margin, px + pw - margin)
            y = random.randint(py + margin, py + ph - margin)
            r = random.randint(18, 30)
            # C: 每帧移动速度
            vx = random.uniform(-1.0, 1.0)
            vy = random.uniform(-1.0, 1.0)
            outer_id = self.canvas.create_oval(
                x - r - 6, y - r - 6, x + r + 6, y + r + 6,
                fill="", outline="#cc8800", width=3)
            inner_id = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill="#cc6600", outline="#ffaa00", width=2)
            self._dots.append({
                "type": "yellow", "x": x, "y": y,
                "r": float(r), "max_r": float(r),
                "inner_id": inner_id, "outer_id": outer_id,
                "vx": vx, "vy": vy,
            })

        # B: 0-2 个蓝色干扰点
        blue_count = random.randint(0, 2)
        if blue_count > 0:
            self.canvas.itemconfig(self._warning_text_id, text="避开蓝色光点！")
        for _ in range(blue_count):
            x = random.randint(px + margin, px + pw - margin)
            y = random.randint(py + margin, py + ph - margin)
            r = random.randint(14, 22)
            inner_id = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill="#3366aa", outline="#4488cc", width=2)
            outer_id = self.canvas.create_oval(
                x - r - 4, y - r - 4, x + r + 4, y + r + 4,
                fill="", outline="#3366aa", width=2)
            self._dots.append({
                "type": "blue", "x": x, "y": y,
                "r": float(r), "max_r": float(r),
                "inner_id": inner_id, "outer_id": outer_id,
                "vx": 0, "vy": 0,
            })

        self.canvas.itemconfig(self._hint_id, text="快点击黄点！")
        self._flash_timer = self.canvas.after(self.FLASH_DURATION, self._miss_all)
        self._start_shrink()   # A
        self._start_move()     # C

    def _start_shrink(self):
        """A: 光点线性缩小至 50%，每 50ms 一帧"""
        if self._shrink_job:
            self.canvas.after_cancel(self._shrink_job)
        total_steps = self.FLASH_DURATION // 50
        step = 0
        def _tick():
            nonlocal step
            if not self._running or not self._dots_alive:
                return
            step += 1
            ratio = 1.0 - 0.5 * min(step / total_steps, 1.0)  # 100% → 50%
            for d in self._dots:
                cr = d["max_r"] * ratio
                if cr < 3:
                    cr = 3
                d["r"] = cr
                self.canvas.coords(d["inner_id"],
                    d["x"] - cr, d["y"] - cr,
                    d["x"] + cr, d["y"] + cr)
                if d["type"] == "yellow":
                    self.canvas.coords(d["outer_id"],
                        d["x"] - cr - 6, d["y"] - cr - 6,
                        d["x"] + cr + 6, d["y"] + cr + 6)
                else:
                    self.canvas.coords(d["outer_id"],
                        d["x"] - cr - 4, d["y"] - cr - 4,
                        d["x"] + cr + 4, d["y"] + cr + 4)
            if step < total_steps:
                self._shrink_job = self.canvas.after(50, _tick)
        _tick()

    def _start_move(self):
        """C: 黄点缓慢移动，每 50ms 一帧"""
        if self._move_job:
            self.canvas.after_cancel(self._move_job)
        def _tick():
            if not self._running or not self._dots_alive:
                return
            w = self.canvas.winfo_width() if self.canvas.winfo_width() >= 50 else 688
            h = self.canvas.winfo_height() if self.canvas.winfo_height() >= 50 else 538
            px, py = w // 2 - 184 + 20, 64 + 20
            pw, ph = 368 - 40, h - 64 - 64 - 40
            for d in self._dots:
                if d["type"] != "yellow":
                    continue
                d["x"] += d["vx"]
                d["y"] += d["vy"]
                # 边界反弹
                if d["x"] - d["r"] < px or d["x"] + d["r"] > px + pw:
                    d["vx"] *= -1
                    d["x"] += d["vx"]
                if d["y"] - d["r"] < py or d["y"] + d["r"] > py + ph:
                    d["vy"] *= -1
                    d["y"] += d["vy"]
                cr = d["r"]
                self.canvas.coords(d["inner_id"],
                    d["x"] - cr, d["y"] - cr,
                    d["x"] + cr, d["y"] + cr)
                self.canvas.coords(d["outer_id"],
                    d["x"] - cr - 6, d["y"] - cr - 6,
                    d["x"] + cr + 6, d["y"] + cr + 6)
            self._move_job = self.canvas.after(50, _tick)
        _tick()

    # ===== 光点消失 =====

    def _clear_dot(self, d):
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.delete(d["inner_id"])
            self.canvas.delete(d["outer_id"])
        self._dots = [x for x in self._dots if x is not d]
        if not self._dots:
            self._dots_alive = False
            self._cancel_timers()
            self._schedule_next()

    def _miss_all(self):
        if not self._dots_alive:
            return
        self._flash_timer = None
        for d in self._dots[:]:
            if self.canvas and self.canvas.winfo_exists():
                self.canvas.delete(d["inner_id"])
                self.canvas.delete(d["outer_id"])
        self._dots = []
        self._dots_alive = False
        self.canvas.itemconfig(self._hint_id, text="漏掉了...")
        self._cancel_timers()
        self._schedule_next()

    def _cancel_timers(self):
        for attr in ['_shrink_job', '_move_job', '_flash_timer']:
            j = getattr(self, attr, None)
            if j:
                self.canvas.after_cancel(j)
                setattr(self, attr, None)

    def _schedule_next(self):
        if self._spawn_timer:
            self.canvas.after_cancel(self._spawn_timer)
            self._spawn_timer = None
        self._spawn_timer = self.canvas.after(self.FLASH_INTERVAL, self._spawn_flash)

    def _finish_all(self, success: bool):
        self._dots_alive = False
        self._cancel_timers()
        for d in self._dots[:]:
            if self.canvas and self.canvas.winfo_exists():
                self.canvas.delete(d["inner_id"])
                self.canvas.delete(d["outer_id"])
        self._dots = []
        if self._spawn_timer:
            self.canvas.after_cancel(self._spawn_timer)
            self._spawn_timer = None
        if success:
            self.canvas.itemconfig(self._hint_id, text="测试完成：效率评级良好。")
        else:
            self.canvas.itemconfig(self._hint_id, text="测试完成：捕获不足，效率评级偏低。")
        self.canvas.after(800, lambda: self._complete(success))


# ============================================================
# MG3 · 直升机平台平衡测试（第4天）
# ============================================================

class MG3_PlatformBalance(MinigameBase):
    """持续点击保持光标稳定在中心区域。B+C难度：随机阵风+收缩安全区。"""

    SURVIVAL_TIME = 20
    DRIFT_SPEED = 2.0        # 基础漂移速度
    ZONE_RADIUS_START = 100  # 安全区初始半径
    ZONE_RADIUS_MIN = 80     # 安全区最小半径
    GUST_MIN_INTERVAL = 3.5  # 阵风最短间隔（秒）
    GUST_MAX_INTERVAL = 7.0  # 阵风最长间隔（秒）

    def __init__(self, parent: tk.Frame):
        super().__init__(parent)
        self.canvas.config(width=680, height=520)

        self._elapsed = 0.0
        self._marker_x = 0
        self._marker_y = 0
        self._drift_x = 0.0
        self._drift_y = 0.0
        self._marker_id = None
        self._zone_id = None
        self._timer_id = None
        self._gust_job = None
        self._gust_warn_id = None
        self._gust_dir_x = 0
        self._gust_dir_y = 0
        self._current_radius = self.ZONE_RADIUS_START

    def _on_start(self):
        self._draw_ui()
        self.canvas.bind("<Button-1>", self._on_click)
        self.parent.winfo_toplevel().bind("<space>", self._on_space)
        # 鼠标归正到中心
        try:
            import ctypes
            cx_scr = self.canvas.winfo_rootx() + self._cx
            cy_scr = self.canvas.winfo_rooty() + self._cy
            ctypes.windll.user32.SetCursorPos(cx_scr, cy_scr)
        except Exception:
            pass
        self._schedule_gust()
        self._tick()

    def _on_stop(self):
        if self._timer_id:
            self.canvas.after_cancel(self._timer_id)
        if self._gust_job:
            self.canvas.after_cancel(self._gust_job)
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.unbind("<Button-1>")
        self.parent.winfo_toplevel().unbind("<space>")

    def _draw_ui(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50: w = 680
        if h < 50: h = 520

        self.canvas.create_text(w // 2, 24,
                                text="直升机平台平衡测试",
                                fill="#e8e8e8",
                                font=("Microsoft YaHei", 14, "bold"))
        self.canvas.create_text(w // 2, 52,
                                text="连续点击 / 空格键保持光标在中心区域内",
                                fill="#666666",
                                font=("Microsoft YaHei", 9))

        self._cx = w // 2
        self._cy = h // 2 + 16

        # 安全区（初始半径100）
        rz = self._current_radius
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

        # 光标（放大到 24×24）
        self._marker_x = self._cx
        self._marker_y = self._cy
        self._marker_id = self.canvas.create_rectangle(
            self._marker_x - 12, self._marker_y - 12,
            self._marker_x + 12, self._marker_y + 12,
            fill="#cc6600", outline="#ff8800", width=3)

        # 状态文字
        self._status_id = self.canvas.create_text(
            w // 2, h - 22,
            text="坚持 {} 秒 | 已过 0.0 秒".format(self.SURVIVAL_TIME),
            fill="#aaaaaa",
            font=("Microsoft YaHei", 10))

        # 阵风方向箭头（初始隐藏）
        self._gust_warn_id = self.canvas.create_text(
            w // 2, self._cy - rz - 20,
            text="", fill="#cc0000",
            font=("Microsoft YaHei", 11, "bold"))

        # 随机初始漂移
        angle = random.uniform(0, 2 * math.pi)
        self._drift_x = math.cos(angle) * self.DRIFT_SPEED
        self._drift_y = math.sin(angle) * self.DRIFT_SPEED

    # ===== 阵风系统 =====

    def _schedule_gust(self):
        if not self._running:
            return
        interval = random.uniform(self.GUST_MIN_INTERVAL, self.GUST_MAX_INTERVAL)
        self._gust_job = self.canvas.after(int(interval * 1000), self._trigger_gust)

    def _trigger_gust(self):
        if not self._running:
            return
        # 随机风向
        angle = random.uniform(0, 2 * math.pi)
        strength = random.uniform(22, 38)
        self._gust_dir_x = math.cos(angle) * strength
        self._gust_dir_y = math.sin(angle) * strength
        # 显示风向提示（0.6秒）
        dir_chars = ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"]
        idx = int((angle + math.pi / 8) / (math.pi / 4)) % 8
        self.canvas.itemconfig(self._gust_warn_id, text="◈ 强风 {} ◈".format(dir_chars[idx]))
        self.canvas.after(600, lambda: self._clear_gust_warn())
        # 阵风推力
        self._marker_x += self._gust_dir_x
        self._marker_y += self._gust_dir_y
        self._gust_dir_x = 0
        self._gust_dir_y = 0
        self._schedule_gust()

    def _clear_gust_warn(self):
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.itemconfig(self._gust_warn_id, text="")

    # ===== 点击 =====

    def _on_click(self, event):
        if not self._running:
            return
        self._push_toward_center()

    def _on_space(self, event=None):
        if not self._running:
            return
        self._push_toward_center()

    def _push_toward_center(self):
        push_strength = 14
        dx = self._cx - self._marker_x
        dy = self._cy - self._marker_y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            self._marker_x += (dx / dist) * push_strength
            self._marker_y += (dy / dist) * push_strength
        # 微调漂移方向
        self._drift_x += random.uniform(-0.8, 0.8)
        self._drift_y += random.uniform(-0.8, 0.8)

    # ===== 主循环 =====

    def _tick(self):
        if not self._running:
            return
        self._elapsed += 0.05

        # 漂移
        self._marker_x += self._drift_x
        self._marker_y += self._drift_y

        # 更新光标位置
        self.canvas.coords(self._marker_id,
                           self._marker_x - 12, self._marker_y - 12,
                           self._marker_x + 12, self._marker_y + 12)

        # 收缩安全区（最后8秒加速收缩100→80）
        progress = self._elapsed / self.SURVIVAL_TIME
        if progress > 0.6:
            shrink_progress = (progress - 0.6) / 0.4
            self._current_radius = int(self.ZONE_RADIUS_START
                - (self.ZONE_RADIUS_START - self.ZONE_RADIUS_MIN) * shrink_progress)
            self.canvas.coords(self._zone_id,
                               self._cx - self._current_radius, self._cy - self._current_radius,
                               self._cx + self._current_radius, self._cy + self._current_radius)

        # 状态文字
        self.canvas.itemconfig(self._status_id,
                               text="坚持 {} 秒 | 已过 {:.1f} 秒".format(
                                   self.SURVIVAL_TIME, self._elapsed))

        # 出界判定（用当前半径）
        dx = self._marker_x - self._cx
        dy = self._marker_y - self._cy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > self._current_radius:
            self._marker_out()
            return

        # 完成
        if self._elapsed >= self.SURVIVAL_TIME:
            self._marker_success()
            return

        # 最后5秒状态变红
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
# MG4-A · 海鸟躲避（第4章 D9）—— B4 重写：25s计时+红鸟+归正+头骨
# ============================================================
class MG4A_SeabirdDodge(MinigameBase):
    SURVIVAL_TIME = 25     # B4: 坚持 25 秒
    MAX_HITS = 4           # B4: 被击中 ≤4 次即胜利
    BIRD_COUNT = 8         # 场上最大鸟数
    RED_PROB = 1.0 / 15.0  # B4: 红鸟概率
    LOOP_INTERVAL = 50     # 循环间隔 ms（原100ms太快，改为50ms更流畅）

    def __init__(self, parent):
        super().__init__(parent)
        self._elapsed = 0.0
        self._hits = 0
        self._birds = []
        self._timer = None
        self._score_id = None
        self._status_id = None
        self._started = False
        self._build_ui()

    def _build_ui(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50: w = 688
        if h < 50: h = 538
        self.canvas.create_text(w // 2, 24, text="躲避海鸟",
                                fill="#cc6600", font=("Microsoft YaHei", 13, "bold"))
        self.canvas.create_text(w // 2, 44, text="移动鼠标闪避 — 灰色慢/红色快 — 坚持25秒",
                                fill="#666666", font=("Microsoft YaHei", 8))
        self._score_id = self.canvas.create_text(w // 2, h - 48,
            text="时间: 0.0 / {}s | 被击中: 0 / {}".format(self.SURVIVAL_TIME, self.MAX_HITS),
            fill="#cc6600", font=("Microsoft YaHei", 10, "bold"))
        self._status_id = self.canvas.create_text(w // 2, h - 26,
            text="",
            fill="#aaaaaa", font=("Microsoft YaHei", 8))
        self._px, self._py = w // 2, h // 2
        r = 12
        self._player_id = self.canvas.create_oval(
            self._px - r, self._py - r, self._px + r, self._py + r,
            fill="#e8e8e8", outline="#cc6600", width=2)
        self.canvas.bind("<Motion>", self._on_move)
        self.canvas.focus_set()

    def start(self):
        super().start()
        if self._running:
            # B4: 鼠标归正到游戏界面中心
            self.canvas.event_generate('<Motion>', x=self._px, y=self._py, warp=True)
            self._started = True
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
        self._elapsed += self.LOOP_INTERVAL / 1000.0
        if len(self._birds) < self.BIRD_COUNT:
            self._spawn()
        self._move_all()
        self._check_hits()
        # 更新状态
        self.canvas.itemconfig(self._score_id,
            text="时间: {:.1f} / {}s | 被击中: {} / {}".format(
                self._elapsed, self.SURVIVAL_TIME, self._hits, self.MAX_HITS))
        if self._hits > self.MAX_HITS:
            self.canvas.itemconfig(self._status_id, text="被击落...", fill="#cc0000")
            self.canvas.after(400, lambda: self._complete(False))
            return
        if self._elapsed >= self.SURVIVAL_TIME:
            self.canvas.itemconfig(self._status_id, text="撑过去了！", fill="#00cc00")
            self.canvas.after(400, lambda: self._complete(True))
            return
        if self._elapsed >= self.SURVIVAL_TIME - 5:
            self.canvas.itemconfig(self._score_id, fill="#cc0000")
        if not self.canvas or not self.canvas.winfo_exists():
            return
        self._timer = self.canvas.after(self.LOOP_INTERVAL, self._loop)

    def _spawn(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50 or h < 50: return
        side = random.randint(0, 3)
        if side == 0:    x, y = random.randint(0, w), -10
        elif side == 1:  x, y = w + 10, random.randint(0, h)
        elif side == 2:  x, y = random.randint(0, w), h + 10
        else:            x, y = -10, random.randint(0, h)

        # B4: 15分之1概率生成红鸟
        is_red = random.random() < self.RED_PROB
        if is_red:
            r, fill_c, outline_c, speed_mul = 10, "#cc2200", "#ff4444", 2.5
        else:
            r, fill_c, outline_c, speed_mul = 8, "#444444", "#888888", 1.0

        dx = (self._px - x) / 30 * speed_mul
        dy = (self._py - y) / 30 * speed_mul
        bid = self.canvas.create_oval(x - r, y - r, x + r, y + r,
            fill=fill_c, outline=outline_c, width=1 if not is_red else 2)
        self._birds.append({"id": bid, "x": x, "y": y, "dx": dx, "dy": dy, "r": r, "red": is_red})

    def _move_all(self):
        if not self.canvas or not self.canvas.winfo_exists():
            return
        w = self.canvas.winfo_width(); h = self.canvas.winfo_height()
        for b in self._birds[:]:
            b["x"] += b["dx"]; b["y"] += b["dy"]
            r = b["r"]
            self.canvas.coords(b["id"], b["x"] - r, b["y"] - r, b["x"] + r, b["y"] + r)
            if b["x"] < -30 or b["x"] > w + 30 or b["y"] < -30 or b["y"] > h + 30:
                self.canvas.delete(b["id"]); self._birds.remove(b)

    def _check_hits(self):
        for b in self._birds[:]:
            r = b["r"] + 12  # 鸟半径 + 玩家半径 = 碰撞检测
            dx = b["x"] - self._px; dy = b["y"] - self._py
            if (dx * dx + dy * dy) < r * r:
                self._hits += 1
                self.canvas.delete(b["id"]); self._birds.remove(b)
                if self._hits > self.MAX_HITS:
                    return

    def _on_stop(self):
        if self._timer and self.canvas and self.canvas.winfo_exists():
            self.canvas.after_cancel(self._timer)
            self._timer = None
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.unbind("<Motion>")


# ============================================================
# MG4B/MG5 · 黑暗收缩复合游戏（B5：暗红+分屏+能量条过热）
# ============================================================

class MG4B5_DarkCircuit(MinigameBase):
    """复合小游戏：上屏配电连线 + 下屏暗红收缩能量条。两屏皆胜→整体通关。"""

    # — 配电部分 —
    PAIRS = [
        ("主线路 A", "#cc0000"),
        ("备用线路 B", "#cc6600"),
        ("照明线路 L", "#ccaa00"),
        ("应急线路 E", "#aa44cc"),
        ("地线 GND",  "#888888"),
        ("信号线 SIG", "#4488cc"),
    ]
    LIGHT_DURATION = 1500
    DARK_DURATION = 2500

    # — 能量条部分 —
    ENERGY_MAX = 30
    ENERGY_DECAY_S = 2     # 每2秒消退1格
    OVERHEAT_THRESHOLD = 10  # 连续点击≥10次触发过热
    OVERHEAT_COOLDOWN = 4   # 过热冷却秒数
    SHRINK_BASE = 0.0068     # 基础收缩速度/帧（0.008×0.85），能量归零时×3

    TIME_LIMIT = 50

    def __init__(self, parent: tk.Frame):
        super().__init__(parent)

        # 配电
        self._left_terminals = []
        self._right_terminals = []
        self._relays = []
        self._matched_left = set()
        self._matched_right = set()
        self._matched_relays = set()
        self._selected_left = None
        self._selected_relay = None
        self._phase = "light"
        self._cycle_job = None

        # 能量条
        self._energy = 5  # 起始5格
        self._click_streak = 0
        self._overheated = False
        self._overheat_job = None

        # 能量条闪烁
        self._blink_state = False
        self._blink_job = None

        # 暗红收缩
        self._shrink = 0.0      # 0=全开, 1=死亡
        self._shrink_job = None

        # 计时
        self._time_left = self.TIME_LIMIT
        self._timer_id = None

        # 双胜利跟踪
        self._top_won = False
        self._bot_won = False

        self._mid_y = 0  # 分屏线
        self._hint_id = None
        self._energy_bar_id = None
        self._energy_text_id = None
        self._overheat_text_id = None
        self._timer_text = None
        self._dark_rect_id = None    # 暗红矩形框
        self._safe_rect_id = None    # 安全区（内层亮区）
        self._shrink_text_id = None

    # ===== 启动 =====

    def _on_start(self):
        self._draw_ui()
        self.canvas.bind("<Button-1>", self._on_click)
        self._start_timer()
        self._start_light_cycle()

    def _on_stop(self):
        if self._timer_id:
            self.canvas.after_cancel(self._timer_id)
        if self._cycle_job:
            self.canvas.after_cancel(self._cycle_job)
        if self._overheat_job:
            self.canvas.after_cancel(self._overheat_job)
        if self._shrink_job:
            self.canvas.after_cancel(self._shrink_job)
        if self._blink_job:
            self.canvas.after_cancel(self._blink_job)
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.unbind("<Button-1>")

    # ===== 亮灭灯 =====

    def _start_light_cycle(self):
        if not self._running: return
        self._phase = "light"
        self._apply_light_phase()
        self._cycle_job = self.canvas.after(self.LIGHT_DURATION, self._start_dark_cycle)

    def _start_dark_cycle(self):
        if not self._running: return
        self._phase = "dark"
        self._apply_dark_phase()
        self._cycle_job = self.canvas.after(self.DARK_DURATION, self._start_light_cycle)

    def _apply_light_phase(self):
        for i, (label, color, _, _, lid, ltxt, _, _, _, _) in enumerate(self._left_terminals):
            if i not in self._matched_left:
                self.canvas.itemconfig(lid, fill="#111111", outline=color)
                self.canvas.itemconfig(ltxt, text=label, fill="#e8e8e8")
        for i, (rlabel, rcolor, _, _, rid, rtxt, _, _, _, _) in enumerate(self._right_terminals):
            if i not in self._matched_right:
                self.canvas.itemconfig(rid, fill="#111111", outline=rcolor)
                self.canvas.itemconfig(rtxt, text=rlabel, fill="#e8e8e8")
        for i, (color, _, _, rid) in enumerate(self._relays):
            if i not in self._matched_relays:
                self.canvas.itemconfig(rid, fill="#111111", outline=color, width=3)
        if self._selected_left is not None:
            self._highlight_left(self._selected_left)
        if self._selected_relay is not None:
            self._highlight_relay(self._selected_relay)

    def _apply_dark_phase(self):
        for i, (label, color, _, _, lid, ltxt, _, _, _, _) in enumerate(self._left_terminals):
            if i not in self._matched_left:
                self.canvas.itemconfig(lid, fill="#0a0a0a", outline="#333333")
                self.canvas.itemconfig(ltxt, text="故障", fill="#555555")
        for i, (rlabel, rcolor, _, _, rid, rtxt, _, _, _, _) in enumerate(self._right_terminals):
            if i not in self._matched_right:
                self.canvas.itemconfig(rid, fill="#0a0a0a", outline="#333333")
                self.canvas.itemconfig(rtxt, text="故障", fill="#555555")
        for i, (color, _, _, rid) in enumerate(self._relays):
            if i not in self._matched_relays:
                self.canvas.itemconfig(rid, fill="#0a0a0a", outline="#1a1a1a", width=3)

    def _stop_cycle(self):
        if self._cycle_job:
            self.canvas.after_cancel(self._cycle_job)
            self._cycle_job = None
        self._phase = "light"
        self._apply_light_phase()

    # ===== 绘制 =====

    def _draw_ui(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50: w = 688
        if h < 50: h = 538
        self._mid_y = h // 2

        # —— 顶部：配电连线 ——
        self.canvas.create_text(w // 2, 12,
            text="配电连线（上）",
            fill="#666666", font=("Microsoft YaHei", 8, "bold"))

        left_x = w // 5
        relay_x = w // 2
        right_x = w * 4 // 5
        start_y = 30
        spacing = max(22, (self._mid_y - 20 - start_y) // len(self.PAIRS))

        right_labels = list(self.PAIRS)
        random.shuffle(right_labels)
        relay_ys = [start_y + i * spacing for i in range(len(self.PAIRS))]
        random.shuffle(relay_ys)

        self._left_terminals = []
        self._right_terminals = []
        self._relays = []
        self._matched_left = set()
        self._matched_right = set()
        self._matched_relays = set()
        self._selected_left = None
        self._selected_relay = None

        for i, (label, color) in enumerate(self.PAIRS):
            y = start_y + i * spacing
            bw, bh = 30, 9
            # 左
            lx1, ly1 = left_x - bw, y - bh
            lx2, ly2 = left_x + bw, y + bh
            lid = self.canvas.create_rectangle(lx1, ly1, lx2, ly2,
                fill="#111111", outline=color, width=2)
            ltxt = self.canvas.create_text(left_x, y, text=label,
                fill="#e8e8e8", font=("Microsoft YaHei", 8, "bold"))
            self._left_terminals.append((label, color, left_x, y, lid, ltxt, lx1, ly1, lx2, ly2))
            # 中继
            ry = relay_ys[i]
            rid = self.canvas.create_oval(relay_x - 7, ry - 7, relay_x + 7, ry + 7,
                fill="#111111", outline=color, width=3)
            self._relays.append((color, relay_x, ry, rid))
            # 右
            rlabel, rcolor = right_labels[i]
            rx1, ry1 = right_x - bw, y - bh
            rx2, ry2 = right_x + bw, y + bh
            r_rid = self.canvas.create_rectangle(rx1, ry1, rx2, ry2,
                fill="#111111", outline=rcolor, width=2)
            rtxt = self.canvas.create_text(right_x, y, text=rlabel,
                fill="#e8e8e8", font=("Microsoft YaHei", 8, "bold"))
            self._right_terminals.append((rlabel, rcolor, right_x, y, r_rid, rtxt, rx1, ry1, rx2, ry2))

        # —— 分屏线 ——
        self.canvas.create_line(0, self._mid_y, w, self._mid_y, fill="#333333", dash=(4, 4))

        # —— 底部：暗红收缩 + 能量条 ——
        dm = 6
        self._dark_rect_id = self.canvas.create_rectangle(
            dm, self._mid_y + 6, w - dm, h - 48,
            fill="", outline="#330000", width=2)
        self._safe_rect_id = self.canvas.create_rectangle(
            dm, self._mid_y + 6, w - dm, h - 48,
            fill="#0a0505", outline="#aa0000", width=2)
        self._shrink_text_id = self.canvas.create_text(
            w // 2, (self._mid_y + h - 50) // 2,
            text="",
            fill="#cc0000", font=("Microsoft YaHei", 22, "bold"))

        # 能量条
        bar_x = w // 4
        bar_w = w // 2
        bar_y = h - 42
        bar_h = 12
        self._energy_bar_bg = self.canvas.create_rectangle(
            bar_x, bar_y, bar_x + bar_w, bar_y + bar_h,
            fill="#1a1a1a", outline="#444444")
        self._energy_bar_id = self.canvas.create_rectangle(
            bar_x, bar_y, bar_x + bar_w * self._energy / self.ENERGY_MAX, bar_y + bar_h,
            fill="#cc6600", outline="")
        self._energy_text_id = self.canvas.create_text(
            w // 2, bar_y + bar_h // 2,
            text="{}/{}".format(self._energy, self.ENERGY_MAX),
            fill="#e8e8e8", font=("Microsoft YaHei", 8, "bold"))

        # 过热提示
        self._overheat_text_id = self.canvas.create_text(
            w // 2, h - 24,
            text="",
            fill="#cc0000", font=("Microsoft YaHei", 9, "bold"))

        # 说明 + 死亡警告（分两行错开）
        self._warn_id = self.canvas.create_text(
            w // 2, self._mid_y + 16,
            text="点击区域充能抵抗 — 收缩完毕你会死",
            fill="#cc6600", font=("Microsoft YaHei", 9, "bold"))

        # 计时器
        self._timer_text = self.canvas.create_text(
            w // 2, h - 8,
            text="剩余: {}秒".format(self._time_left),
            fill="#cc6600", font=("Microsoft YaHei", 8, "bold"))

        # 通用提示
        self._hint_id = self.canvas.create_text(
            w // 2, self._mid_y + 30,
            text="",
            fill="#aaaaaa", font=("Microsoft YaHei", 7))

    # ===== 点击 =====

    def _on_click(self, event):
        if not self._running: return
        cx, cy = event.x, event.y

        # 上半区：配电
        if cy < self._mid_y:
            self._on_top_click(cx, cy)
        else:
            self._on_bot_click(cx, cy)

    # — 上半配电 —

    def _on_top_click(self, cx, cy):
        if self._phase == "dark":
            pass  # 灭灯仍可操作
        # 中继点
        for i, (color, rx, ry, rid) in enumerate(self._relays):
            if i in self._matched_relays: continue
            if (cx - rx) ** 2 + (cy - ry) ** 2 <= 14 ** 2:
                if self._selected_left is not None:
                    if self._left_terminals[self._selected_left][1] == color:
                        self._selected_relay = i
                        self._highlight_relay(i)
                        return
                    else:
                        self._flash_relay_wrong(i)
                        return
                return

        # 右侧端子
        for i, (rlabel, rcolor, tx, ty, rid, rtxt, x1, y1, x2, y2) in enumerate(self._right_terminals):
            if i in self._matched_right: continue
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                if self._selected_left is not None and self._selected_relay is not None:
                    if self._left_terminals[self._selected_left][0] == rlabel and \
                       self._relays[self._selected_relay][0] == rcolor:
                        self._connect_top(self._selected_left, self._selected_relay, i)
                    self._selected_left = None
                    self._selected_relay = None
                    self._clear_all_highlights()
                    return
                return

        # 左侧端子
        for i, (label, color, tx, ty, lid, ltxt, x1, y1, x2, y2) in enumerate(self._left_terminals):
            if i in self._matched_left: continue
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                self._selected_left = i
                self._selected_relay = None
                self._highlight_left(i)
                return

        # 空白取消
        self._selected_left = None
        self._selected_relay = None
        self._clear_all_highlights()

    def _connect_top(self, li, ri_idx, r_idx):
        self._matched_left.add(li)
        self._matched_relays.add(ri_idx)
        self._matched_right.add(r_idx)
        lrect = self._left_terminals[li][4]
        rrect = self._right_terminals[r_idx][4]
        r_relay = self._relays[ri_idx][3]
        self.canvas.itemconfig(lrect, fill="#002200", outline="#00aa00")
        self.canvas.itemconfig(r_relay, fill="#002200", outline="#00aa00")
        self.canvas.itemconfig(rrect, fill="#002200", outline="#00aa00")
        if len(self._matched_left) == len(self.PAIRS):
            self._top_won = True
            self._stop_cycle()
            self.canvas.itemconfig(self._hint_id, text="配线完成！")
            self._check_double_win()

    def _highlight_left(self, idx):
        self._clear_all_highlights()
        _, color, _, _, lid, _, _, _, _, _ = self._left_terminals[idx]
        self.canvas.itemconfig(lid, fill="#1a0000", outline=self._brighten(color))

    def _highlight_relay(self, idx):
        color, _, _, rid = self._relays[idx]
        if self._phase == "dark":
            self.canvas.itemconfig(rid, fill="#332200", outline="#cc6600", width=3)
        else:
            self.canvas.itemconfig(rid, fill="#1a1a00", outline=self._brighten(color))

    def _clear_all_highlights(self):
        for _, color, _, _, lid, _, _, _, _, _ in self._left_terminals:
            self.canvas.itemconfig(lid, fill="#111111", outline=color)
        for color, _, _, rid in self._relays:
            if self._phase == "dark":
                self.canvas.itemconfig(rid, fill="#0a0a0a", outline="#1a1a1a", width=3)
            else:
                self.canvas.itemconfig(rid, fill="#111111", outline=color, width=3)

    def _brighten(self, hex_color):
        r = min(255, int(hex_color[1:3], 16) + 60)
        g = min(255, int(hex_color[3:5], 16) + 60)
        b = min(255, int(hex_color[5:7], 16) + 60)
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    def _flash_relay_wrong(self, idx):
        color, _, _, rid = self._relays[idx]
        self.canvas.itemconfig(rid, fill="#330000", outline="#ff0000")
        def reset():
            if self.canvas and self.canvas.winfo_exists():
                if self._phase == "dark":
                    self.canvas.itemconfig(rid, fill="#0a0a0a", outline="#1a1a1a", width=3)
                else:
                    self.canvas.itemconfig(rid, fill="#111111", outline=color, width=3)
        self.canvas.after(400, reset)

    # — 下半 能量 + 暗红收缩 —

    def _on_bot_click(self, cx, cy):
        if self._bot_won: return
        if self._overheated: return

        self._click_streak += 1
        def _reset(cs):
            if self._click_streak == cs:
                self._click_streak = 0
        self.canvas.after(500, lambda cs=self._click_streak: _reset(cs))

        if self._click_streak >= self.OVERHEAT_THRESHOLD:
            self._trigger_overheat()
            return

        self._energy = min(self.ENERGY_MAX, self._energy + 1)
        self._shrink = max(0.0, self._shrink - 0.03)  # 点击击退收缩
        self._update_energy_bar()
        self._draw_shrink()

    def _trigger_overheat(self):
        self._overheated = True
        self._click_streak = 0
        self.canvas.itemconfig(self._overheat_text_id, text="过热！冷却中...")
        def _cool():
            self._overheated = False
            if self.canvas and self.canvas.winfo_exists():
                self.canvas.itemconfig(self._overheat_text_id, text="")
        self._overheat_job = self.canvas.after(self.OVERHEAT_COOLDOWN * 1000, _cool)

    def _start_shrink_loop(self):
        """50ms 帧循环：暗红收缩动画"""
        if not self._running or self._bot_won: return
        if self._shrink >= 1.0:
            self._do_shrink_death()
            return

        speed = self.SHRINK_BASE
        if self._energy <= 0:
            speed *= 3  # 归零三倍速
        self._shrink += speed

        if self._energy > 0:
            self._shrink = max(0.0, self._shrink - 0.004 * self._energy / self.ENERGY_MAX)

        self._draw_shrink()

        if self._shrink >= 1.0:
            self._do_shrink_death()
            return

        self._shrink_job = self.canvas.after(50, self._start_shrink_loop)

    def _draw_shrink(self):
        """根据 shrink 值绘制暗红收缩框，独立计算 X/Y 收缩"""
        if not self.canvas or not self.canvas.winfo_exists(): return
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50: w = 688
        dm = 6
        area_w = w - 2 * dm
        area_h = h - 48 - self._mid_y - 6

        # X / Y 分别收缩
        mx = area_w // 2 * self._shrink
        my = area_h // 2 * self._shrink if area_h > 0 else 0

        sx1 = dm + mx
        sy1 = self._mid_y + 6 + my
        sx2 = w - dm - mx
        sy2 = h - 48 - my

        if sx2 - sx1 < 2 or sy2 - sy1 < 2:
            # 收缩到极限
            cx = (w) // 2; cy = (self._mid_y + 6 + h - 48) // 2
            self.canvas.coords(self._safe_rect_id, cx, cy, cx + 1, cy + 1)
        else:
            self.canvas.coords(self._safe_rect_id, sx1, sy1, sx2, sy2)

        rv = int(30 + min(1.0, self._shrink) * 160)
        outline = "#{:02x}0000".format(min(255, rv))
        self.canvas.itemconfig(self._safe_rect_id, outline=outline,
                               fill="#{:02x}0505".format(int(10 + min(1.0, self._shrink) * 40)))
        if self._shrink > 0.6:
            self.canvas.itemconfig(self._shrink_text_id, text="黑暗逼近！",
                                   fill="#{:02x}0000".format(min(255, int(100 + min(1.0, self._shrink) * 155))))

    def _do_shrink_death(self):
        self._bot_won = True  # 标记结束
        self.canvas.coords(self._safe_rect_id, 0, 0, 0, 0)
        self.canvas.itemconfig(self._shrink_text_id, text="", fill="#000000")
        # 1.5s 留白
        self.canvas.after(1500, lambda: self._complete(False))

    def _update_energy_bar(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50: w = 688
        bar_w = w // 2
        bar_x = w // 4
        bar_y = h - 42
        bar_h = 12
        self.canvas.coords(self._energy_bar_id,
            bar_x, bar_y,
            bar_x + bar_w * max(0, self._energy) / self.ENERGY_MAX, bar_y + bar_h)
        self.canvas.itemconfig(self._energy_text_id,
            text="{}/{}".format(self._energy, self.ENERGY_MAX))
        if self._energy <= 5:
            self.canvas.itemconfig(self._energy_bar_id, fill="#cc0000")
        elif self._energy <= 10:
            self.canvas.itemconfig(self._energy_bar_id, fill="#cc6600")
        else:
            self.canvas.itemconfig(self._energy_bar_id, fill="#cc6600")
        self._start_blink()

    def _start_blink(self):
        """能量条边框闪烁提醒玩家点击"""
        if self._blink_job:
            self.canvas.after_cancel(self._blink_job)
        def _tick():
            if not self._running or self._bot_won: return
            self._blink_state = not self._blink_state
            color = "#cc6600" if self._blink_state else "#333333"
            self.canvas.itemconfig(self._energy_bar_bg, outline=color)
            self._blink_job = self.canvas.after(400, _tick)
        _tick()

    # 能量自然消退 + 启动收缩
    def _start_energy_decay(self):
        self._start_shrink_loop()
        self._energy_tick()

    def _energy_tick(self):
        if not self._running or self._bot_won: return
        self._energy = max(0, self._energy - 1)
        self._update_energy_bar()
        # 能量归零时收缩加速已在 _start_shrink_loop 处理
        self.canvas.after(self.ENERGY_DECAY_S * 1000, self._energy_tick)

    # ===== 双胜利检查 =====

    def _check_double_win(self):
        if self._top_won and not self._bot_won:
            self._bot_won = True
            self.canvas.itemconfig(self._hint_id, text="配线完成！撑住了！")
            self.canvas.after(800, lambda: self._complete(True))

    # ===== 计时 =====

    def _start_timer(self):
        self._start_energy_decay()  # 启动消退
        self._tick_timer()

    def _tick_timer(self):
        if not self._running: return
        self._time_left -= 1
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.itemconfig(self._timer_text,
                text="剩余: {}秒".format(self._time_left))
        if self._time_left <= 0:
            if not self._top_won and not self._bot_won:
                self.canvas.itemconfig(self._hint_id, text="时间耗尽...")
            self.canvas.after(800, lambda: self._complete(False))
            return
        if self._time_left <= 10:
            self.canvas.itemconfig(self._timer_text, fill="#cc0000")
        self._timer_id = self.canvas.after(1000, self._tick_timer)
