# -*- coding: utf-8 -*-
"""
main_window.py —— 游戏主窗口（Undertale 风格）
负责全部 UI 渲染，不包含业务逻辑。
所有状态变更通过回调通知 Game 类。

配色来源：design.md 1.3
"""

import tkinter as tk


class MainWindow:
    """纯 UI 层。5 个界面：标题/文本/选项/面板/存档。"""

    # design.md 1.3 配色字典
    COLORS = {
        "bg": "#000000",
        "text": "#e8e8e8",
        "emphasis": "#cc0000",
        "dim": "#666666",
        "arrow": "#666666",
        "arrow_hover": "#e8e8e8",
        "accent": "#cc6600",
        "status_bg": "#0a0a0a",
        "panel_bg": "#0a0a0a",
    }

    FONT = ("Microsoft YaHei", 13)
    FONT_BIG = ("Microsoft YaHei", 22, "bold")
    FONT_SMALL = ("Microsoft YaHei", 9)
    FONT_MENU = ("Microsoft YaHei", 12)

    # mood → 逐字打印速度（ms/字）
    MOOD_SPEEDS = {
        "quiet": 30,
        "tension": 22,
        "dread": 35,
        "loss": 40,
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("灯塔")
        self.root.geometry("860x640")
        self.root.minsize(640, 480)
        self.root.configure(bg=self.COLORS["bg"])
        self._center_window()

        # 公开回调（由 Game 类绑定）
        self.on_menu_new_game = None
        self.on_menu_continue = None
        self.on_menu_collection = None
        self.on_gm_unlock_collection = None
        self.on_choice_made = None
        self.on_text_complete = None
        self.on_toggle_panel = None
        self.on_save_clicked = None
        self.on_load_clicked = None
        self.on_auto_advance = None
        self.on_gm_jump = None
        self.on_gm_set_var = None
        self.on_gm_preset = None
        self.on_gm_open = None
        self.on_gm_load_chapter = None

        # GM 调试栏（需 --gm 启动参数开启）
        self.gm_enabled = False
        self._gm_open = False
        self._gm_frame = None
        self._gm_dim_layer = None

        # UI 组件
        self._build()

        # 逐字打印状态
        self._chunks = []          # 文本块列表
        self._chunk_idx = 0        # 当前块索引
        self._is_typing = False    # 正在逐字打印
        self._in_key_mode = False   # 正在打印 [key] 标记内的文字
        self._typewriter_job = None  # after 定时器 ID
        self._typewrite_delay = 30   # 逐字延迟（ms），由 node mood 动态调整
        self._pause_after = {}     # 块索引 -> 暂停秒数
        self._is_pausing = False   # 正在暂停等待
        self._pause_job = None     # 暂停 after 定时器
        self._prompt_blink_job = None  # 提示符闪烁 after
        self._choice_labels = []   # 选项 Label 引用（multi_click 用）
        self._sound_events = []    # 当前块的音效事件列表
        self._sound_mgr = None     # 由 Game 注入

        # 面板数据缓存（面板关闭期间保持数据不丢失）
        self._cached_notes = ""
        self._cached_status = {}
        self._cached_items = []
        self._seen_item_ids = set()   # 已查看过详情的物品 ID

        # 日记缓存（多天翻阅）
        self._diary_cache = {}
        self._diary_view_day = 0
        self._diary_latest_day = 0

    def set_sound_manager(self, sound_mgr):
        """由 Game.__init__ 注入 SoundManager 实例（M5 音效集成）"""
        self._sound_mgr = sound_mgr

    # ========== 布局 ==========

    def _center_window(self):
        self.root.update_idletasks()
        w, h = 860, 640
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        """构建基础骨架：文本区 + 选项区 + 状态栏"""
        # — 底部状态栏（先创建，保证choice_frame可引用） —
        self.status_bar = tk.Frame(self.root, bg=self.COLORS["status_bg"], height=32)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        self._build_status_bar()

        # — 选项区（状态栏上方，固定高度不伸缩，始终在视野内，OPT-05） —
        self.choice_frame = tk.Frame(self.root, bg=self.COLORS["bg"],
                                     height=180)
        self.choice_frame.pack(side=tk.BOTTOM, fill=tk.X,
                               padx=60, pady=(8, 4), before=self.status_bar)
        self.choice_frame.pack_propagate(False)  # 固定高度
        self._choice_rows = []

        # — 文本显示区（填充剩余空间） —
        text_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(36, 0))

        self.text_area = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=self.FONT,
            bg=self.COLORS["bg"],
            fg=self.COLORS["text"],
            insertbackground=self.COLORS["text"],
            selectbackground="#222222",
            borderwidth=0,
            highlightthickness=0,
            relief=tk.FLAT,
            padx=20,
            pady=16,
            spacing2=6,
            state=tk.DISABLED,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # 空格/回车/点击 → 推进文本
        self.text_area.bind("<space>", self._on_text_advance)
        self.text_area.bind("<Return>", self._on_text_advance)
        self.text_area.bind("<Button-1>", self._on_text_advance)

        # Tab 键切换状态面板（widget 级绑定抢在 Text 类绑定之前拦截）
        self.text_area.bind("<Tab>", lambda e: self.toggle_panel() or "break")
        self.root.bind("<Tab>", lambda e: self.toggle_panel())

        # — 小游戏覆盖层（默认隐藏） —
        self._build_minigame_area()

        # 文本 tag 配置
        self.text_area.tag_configure("dim", foreground=self.COLORS["dim"])
        self.text_area.tag_configure("emphasis",
            foreground=self.COLORS["emphasis"],
            font=("Microsoft YaHei", 22, "bold"))
        self.text_area.tag_configure("prompt",
            foreground="#555555",
            font=self.FONT_SMALL)
        self.text_area.tag_configure("shake",
            foreground=self.COLORS["emphasis"])  # 4G: 红色抖动 tag
        self.text_area.tag_configure("key",
            foreground="#ccaa44")  # M7: 关键句淡黄色标记

    def _build_status_bar(self):
        """底部：存档 / 读档 / 天数 / Tab提示"""
        # 顶框分割线
        sep = tk.Frame(self.status_bar, height=1, bg="#333333")
        sep.pack(side=tk.TOP, fill=tk.X)
        for label, attr_name in [(" 存档 ", "on_save_clicked"),
                                  (" 读档 ", "on_load_clicked")]:
            btn = tk.Label(self.status_bar, text=label,
                           font=self.FONT_SMALL,
                           fg=self.COLORS["dim"],
                           bg=self.COLORS["status_bg"],
                           cursor="hand2")
            btn.pack(side=tk.LEFT, padx=(20 if "存档" in label else 4, 4), pady=6)
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg=self.COLORS["text"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(fg=self.COLORS["dim"]))
            btn.bind("<Button-1>", lambda e, a=attr_name: (
                cb := getattr(self, a, None)) and cb())

        self.day_label = tk.Label(self.status_bar, text="",
                                  font=self.FONT_SMALL,
                                  fg=self.COLORS["dim"],
                                  bg=self.COLORS["status_bg"])
        self.day_label.pack(side=tk.RIGHT, padx=20, pady=6)

        self._notify_label = tk.Label(self.status_bar, text="",
                font=("Microsoft YaHei", 8, "bold"),
                fg="#ffffff", bg=self.COLORS["status_bg"],
                padx=4, pady=1)
        self._notify_label.pack(side=tk.RIGHT, padx=4, pady=6)
        self._tab_hint = tk.Label(self.status_bar, text="Tab 备忘录",
                 font=("Microsoft YaHei", 10, "bold"), fg="#555555",
                 bg=self.COLORS["status_bg"])
        self._tab_hint.pack(side=tk.RIGHT, padx=8, pady=6)
        # GM 调试栏快捷键（仅 gm_enabled 时生效）
        self.root.bind("<Control-Shift-G>", lambda e: self._toggle_gm() if self.gm_enabled else None)
        self._panel_open = False
        self._panel_frame = None
        self._dim_layer = None

    # ========== 标题界面 ==========

    def show_title_screen(self, quote: str):
        """引言渐现(2s)→停留(5s,可点击跳过)→渐隐→标题浮现→菜单（OPT-01/02）"""
        self.clear_choices()
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        # 垂直居中
        self.text_area.insert(tk.END, "\n\n\n\n\n\n")
        self.text_area.insert(tk.END, quote, "fade")
        self.text_area.tag_configure("fade", foreground="#000000",
                                      font=("Microsoft YaHei", 11),
                                      justify="center")
        self.text_area.tag_configure("center", justify="center")
        self.text_area.tag_add("center", "1.0", "end")
        self.text_area.config(state=tk.DISABLED)
        # 阶段1：渐现（目标色 #aaaaaa，更白亮）
        # 整个标题序列中，点击 root 即可跳过（渐现/停留期均生效）
        self._title_phase = "fade_in"
        self._title_menu_shown = False
        self._title_click_binding = self.root.bind(
            "<Button-1>", lambda e: self._title_skip(), add="+")
        self._animate_fade("fade", "#000000", "#aaaaaa", 2000,
                           on_done=self._quote_hold_start)

    def _title_skip(self):
        """标题序列中点击任意位置 → 跳过当前阶段直接进入渐隐"""
        if not getattr(self, '_title_phase', None):
            return
        # 取消所有正在运行的动画和计时器
        if self._fade_job:
            self.root.after_cancel(self._fade_job)
            self._fade_job = None
        if hasattr(self, '_hold_timer') and self._hold_timer:
            self.root.after_cancel(self._hold_timer)
            self._hold_timer = None
        self._quote_held = False
        self.root.unbind("<Button-1>", self._title_click_binding)
        self._title_phase = "done"
        # 直接进入渐隐
        self._animate_fade("fade", "#aaaaaa", "#000000", 1000,
                           on_done=self._show_title_and_menu)

    def _animate_fade(self, tag, from_hex, to_hex, duration_ms, on_done, step=0):
        """通用颜色渐变动画。total_steps 按 50ms 一帧计算"""
        total = duration_ms // 50
        if step <= total:
            r = round((step / total) * (int(to_hex[1:3], 16) - int(from_hex[1:3], 16)) + int(from_hex[1:3], 16))
            g = round((step / total) * (int(to_hex[3:5], 16) - int(from_hex[3:5], 16)) + int(from_hex[3:5], 16))
            b = round((step / total) * (int(to_hex[5:7], 16) - int(from_hex[5:7], 16)) + int(from_hex[5:7], 16))
            color = "#{:02x}{:02x}{:02x}".format(r, g, b)
            self.text_area.tag_configure(tag, foreground=color)
            self._fade_job = self.root.after(50, lambda: self._animate_fade(
                tag, from_hex, to_hex, duration_ms, on_done, step + 1))
        else:
            self._fade_job = None
            on_done()

    def _quote_hold_start(self):
        """引言渐现完毕，停留 5 秒（点击已在 fade_in 阶段绑定）"""
        self._quote_held = True
        self._hold_timer = self.root.after(5000, self._quote_fade_out)

    def _quote_fade_out(self):
        """5秒计时到期，自动渐隐"""
        if not getattr(self, '_quote_held', False):
            return
        self._quote_held = False
        self._hold_timer = None
        if self._title_phase != "done":
            self._title_phase = "done"
            self.root.unbind("<Button-1>", self._title_click_binding)
        # 取消残留动画
        if self._fade_job:
            self.root.after_cancel(self._fade_job)
            self._fade_job = None
        self._animate_fade("fade", "#aaaaaa", "#000000", 1000,
                           on_done=self._show_title_and_menu)

    def _show_title_and_menu(self):
        """引言消失后 → 标题渐显动画 → 菜单（OPT-12 浮现动画）"""
        if getattr(self, '_title_menu_shown', False):
            return
        self._title_menu_shown = True
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, "\n\n\n\n")
        # 使用专用 tag 做渐显，避免覆盖全局 emphasis tag
        self._title_index = self.text_area.index("end-1c")
        self.text_area.insert(tk.END, "灯  塔", "title_fade")
        self.text_area.insert(tk.END, "\n\n")
        self.text_area.tag_configure("title_fade",
            foreground="#000000",
            font=("Microsoft YaHei", 22, "bold"),
            justify="center")
        self.text_area.tag_add("center", "1.0", "end")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)
        # 渐显动画 1.5s #cc0000，完成后显示菜单
        self._animate_fade("title_fade", "#000000", "#cc0000", 1500,
                           on_done=self._show_title_menu_after_animate)

    def _show_title_menu_after_animate(self):
        """标题浮现完毕，显示菜单"""
        # 将 title_fade tag 转回 emphasis 以保持一致性
        self.text_area.tag_configure("title_fade",
            foreground="#cc0000",
            font=("Microsoft YaHei", 22, "bold"))
        self._show_menu(["新游戏", "继续游戏", "结局收集", "退出"])


    def _show_menu(self, labels: list, styles: list = None):
        """显示居中箭头菜单。styles: 并行列表，可选 {"important": True} 渲染金色文字"""
        styles = styles or [{}] * len(labels)
        self.clear_choices()
        for i, label in enumerate(labels):
            st = styles[i] if i < len(styles) else {}
            important = st.get("important", False)
            text_color = "#ccaa00" if important else self.COLORS["text"]
            hover_color = "#ffcc00" if important else self.COLORS["accent"]

            row = tk.Frame(self.choice_frame, bg=self.COLORS["bg"])
            row.pack(fill=tk.X, pady=3)
            self._choice_rows.append(row)

            tk.Label(row, text="", bg=self.COLORS["bg"],
                     font=("", 1)).pack(side=tk.LEFT, expand=True)

            arrow = tk.Label(row, text="\u25b6", font=self.FONT_MENU,
                             fg=text_color, bg=self.COLORS["bg"],
                             cursor="hand2")
            arrow.pack(side=tk.LEFT, padx=(0, 4))

            text_lbl = tk.Label(row, text=label, font=self.FONT_MENU,
                                fg=text_color, bg=self.COLORS["bg"],
                                cursor="hand2")
            text_lbl.pack(side=tk.LEFT)
            self._choice_labels.append(text_lbl)

            tk.Label(row, text="", bg=self.COLORS["bg"],
                     font=("", 1)).pack(side=tk.LEFT, expand=True)

            widgets = [arrow, text_lbl]
            def enter(e, ws=widgets, hc=hover_color):
                for w in ws:
                    w.config(fg=hc)
            def leave(e, ws=widgets, tc=text_color):
                for w in ws:
                    w.config(fg=tc)

            row.bind("<Enter>", enter)
            row.bind("<Leave>", leave)
            arrow.bind("<Enter>", enter)
            arrow.bind("<Leave>", leave)
            text_lbl.bind("<Enter>", enter)
            text_lbl.bind("<Leave>", leave)

            if label == "新游戏":
                cb = lambda: self.on_menu_new_game and self.on_menu_new_game()
            elif label == "继续游戏":
                cb = lambda: self.on_menu_continue and self.on_menu_continue()
            elif label == "结局收集":
                cb = lambda: self.on_menu_collection and self.on_menu_collection()
            elif label == "退出":
                cb = self.root.destroy
            elif label == "继续...":
                cb = lambda: self.on_auto_advance and self.on_auto_advance()
            else:
                cb = lambda idx=i: self.on_choice_made and self.on_choice_made(idx)
            row.bind("<Button-1>", lambda e, c=cb: c())
            arrow.bind("<Button-1>", lambda e, c=cb: c())
            text_lbl.bind("<Button-1>", lambda e, c=cb: c())

    def show_choices(self, choice_list: list):
        """显示剧情选项（居中 ▶ 按钮）。choice_list: [{"label": "...", "important": bool}]"""
        labels = [c.get("label", "???") for c in choice_list]
        styles = [{"important": c.get("important", False)} for c in choice_list]
        self._choice_labels = []
        self._show_menu(labels, styles)

    # ========== 文本操作 ==========

    def flash_black_transition(self, callback):
        """节点切换黑屏过渡0.3s，然后执行回调（OPT-07）"""
        overlay = tk.Frame(self.root, bg="#000000")
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        overlay.lift()
        def _done():
            overlay.destroy()
            callback()
        self.root.after(300, _done)


    def show_chunked_text(self, full_text: str, mood: str = None):
        """按 \n\n 分块，逐块逐字打印。mood 可调打字速度。"""
        self._typewrite_delay = self.MOOD_SPEEDS.get(mood, 30)
        import re
        # 取消旧计时器（防止快速节点切换时旧计时器在新文本上执行）
        if self._typewriter_job:
            self.root.after_cancel(self._typewriter_job)
            self._typewriter_job = None
        if self._pause_job:
            self.root.after_cancel(self._pause_job)
            self._pause_job = None
        # 预处理 [shake] 标记：提取并替换为占位
        self._shake_blocks = []
        def _extract_shake(m):
            self._shake_blocks.append(m.group(1))
            return "[SHAKE_{}]".format(len(self._shake_blocks) - 1)
        full_text = re.sub(r'\[shake\](.*?)\[/shake\]', _extract_shake, full_text, flags=re.DOTALL)

        # 预处理 [sound] 标记：提取音效事件，替换为占位（M5 接入，块级关联）
        self._sound_events = {}  # chunk_idx -> [sound_names]
        def _extract_sound(m):
            return "[SOUND_{}]".format(m.group(1))  # 保留占位，后续按块分发
        full_text = re.sub(r'\[sound\s+(\w+)\]', _extract_sound, full_text)
        full_text = re.sub(r'\[/sound\]', '', full_text)

        # 预处理 [pause N] 标记：替换为占位
        self._pause_after = {}
        def _extract_pause(m):
            return "[PAUSE_{}]".format(m.group(1))
        full_text = re.sub(r'\[pause\s+([\d.]+)\]', _extract_pause, full_text, flags=re.IGNORECASE)

        # 预处理 [key]...[/key] 标记：替换为 \x01...\x02 控制符，打字时渲染为淡黄色
        full_text = re.sub(r'\[key\](.*?)\[/key\]', lambda m: "\x01" + m.group(1) + "\x02", full_text, flags=re.DOTALL)

        # 分块
        chunks = re.split(r'\n\s*\n', full_text.strip())
        chunks = [c.strip() for c in chunks if c.strip()]
        if not chunks:
            chunks = [full_text.strip()]

        # 扫描块中的 [PAUSE_N] 占位 + [SOUND_name] 占位
        processed = []
        for c in chunks:
            # 提取 [SOUND_name]：建立块→音效映射，并移除占位（M5）
            sounds_in_chunk = re.findall(r'\[SOUND_(\w+)\]', c)
            if sounds_in_chunk:
                idx = len(processed)  # 当前块在 processed 中的索引
                self._sound_events[idx] = sounds_in_chunk
            c = re.sub(r'\[SOUND_\w+\]', '', c).strip()
            if not c:
                continue

            pm = re.match(r'^\[PAUSE_([\d.]+)\](.*)', c, re.DOTALL)
            if pm:
                seconds = float(pm.group(1))
                rest = pm.group(2).strip()
                if rest:
                    processed.append(rest)
                    self._pause_after[len(processed) - 1] = seconds
                else:
                    if processed:
                        self._pause_after[len(processed) - 1] = seconds
                continue
            processed.append(c)

        self._chunks = processed
        self._chunk_idx = 0
        self._is_typing = False
        self._is_pausing = False

        # 清屏
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.config(state=tk.DISABLED)

        self._typewrite_current_chunk()

    def _typewrite_current_chunk(self):
        """逐字打印当前块。若块含 [SHAKE_N] 占位则渲染红色抖动文字。"""
        self._in_key_mode = False  # 每个新块重置 key 模式
        if self._chunk_idx >= len(self._chunks):
            self._on_all_chunks_done()
            return

        if self._chunk_idx > 0:
            self._append("\n\n")

        # 触发当前块的音效事件（M5 待配表工具启用）
        # sounds = self._sound_events.get(self._chunk_idx, [])
        # for snd in sounds:
        #     if self._sound_mgr:
        #         self._sound_mgr.play(snd)

        # 检查是否有 shake 占位
        chunk = self._chunks[self._chunk_idx]
        import re
        shake_match = re.match(r'\[SHAKE_(\d+)\](.*)', chunk, re.DOTALL)
        if shake_match:
            shake_idx = int(shake_match.group(1))
            rest = shake_match.group(2)
            if shake_idx < len(getattr(self, '_shake_blocks', [])):
                shake_text = self._shake_blocks[shake_idx]
                self._append_tagged(shake_text, "shake")
                self._start_shake_animation()
                # M5 待配表工具启用
                # if self._sound_mgr:
                #     self._sound_mgr.play("heartbeat")  # M5: 红色抖动同步心跳
            # 如果有剩余文本，继续打印；否则当作消耗完毕进入下一块
            if rest:
                self._chunks[self._chunk_idx] = rest
                self._is_typing = True
                self._typewrite_char(0)
                return
            else:
                # 纯 shake 块，无剩余文字，推进到下一块
                self._is_typing = False
                self._chunk_idx += 1
                if self._chunk_idx >= len(self._chunks):
                    self._on_all_chunks_done()
                else:
                    pause_seconds = self._pause_after.get(self._chunk_idx - 1)
                    if pause_seconds:
                        self._start_pause(pause_seconds)
                    else:
                        self._show_prompt()
                return

        self._is_typing = True
        self._typewrite_char(0)

    def _start_shake_animation(self):
        """启动红色抖动动画（5秒后自动停止）"""
        def shake(remaining=125):
            if remaining <= 0:
                self.text_area.tag_configure("shake", offset="0")
                return
            import random
            offset = random.choice([-3, -2, -1, 0, 1, 2, 3])
            self.text_area.tag_configure("shake", offset=str(offset))
            self.root.after(40, lambda: shake(remaining - 1))
        shake()

    def _typewrite_char(self, pos: int):
        """打印当前块的第 pos 个字符"""
        if self._chunk_idx >= len(self._chunks):
            return  # 状态已被外部重置
        chunk = self._chunks[self._chunk_idx]
        if pos >= len(chunk):
            # 当前块打印完毕
            self._is_typing = False
            self._chunk_idx += 1
            if self._chunk_idx >= len(self._chunks):
                self._on_all_chunks_done()
            else:
                # 检查是否需要暂停
                pause_seconds = self._pause_after.get(self._chunk_idx - 1)
                if pause_seconds:
                    self._start_pause(pause_seconds)
                else:
                    self._show_prompt()
            return

        char = chunk[pos]
        if char == "\x01":
            self._in_key_mode = True
        elif char == "\x02":
            self._in_key_mode = False
        elif self._in_key_mode:
            self._append_tagged(char, "key")
        else:
            self._append(char)
        self.text_area.see(tk.END)
        self._typewriter_job = self.root.after(
            self._typewrite_delay, lambda: self._typewrite_char(pos + 1))

    def _skip_typing(self):
        """跳过当前块的逐字动画，直接显示完整块"""
        if self._typewriter_job:
            self.root.after_cancel(self._typewriter_job)
            self._typewriter_job = None
        if self._chunk_idx < len(self._chunks):
            chunk = self._chunks[self._chunk_idx]
            # 从末尾删除正在打印的内容（整块剩余部分由完整重替换）
            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete("1.0", tk.END)
            full = ""
            for i in range(self._chunk_idx):
                full += self._chunks[i] + "\n\n"
            full += chunk
            # 渲染时处理 \x01...\x02 标记（用 re.split 保证顺序）
            import re
            segments = re.split('(\x01.*?\x02)', full, flags=re.DOTALL)
            for seg in segments:
                if seg.startswith("\x01") and seg.endswith("\x02"):
                    self.text_area.insert(tk.END, seg[1:-1], "key")
                else:
                    self.text_area.insert(tk.END, seg)
            self.text_area.see(tk.END)
            self.text_area.config(state=tk.DISABLED)
        self._is_typing = False
        self._chunk_idx += 1
        if self._chunk_idx >= len(self._chunks):
            self._on_all_chunks_done()
        else:
            pause_seconds = self._pause_after.get(self._chunk_idx - 1)
            if pause_seconds:
                self._start_pause(pause_seconds)
            else:
                self._show_prompt()

    def _show_prompt(self):
        """显示翻页提示并启动微弱闪烁"""
        self._append("\n\n")
        self._append_tagged("▼ 空格/回车继续", "prompt")
        self._start_prompt_blink()

    def _start_prompt_blink(self):
        """提示符微弱闪烁动画（OPT-06）"""
        self._cancel_prompt_blink()
        def _blink(state=0):
            if not self._chunks or self._is_typing or self._chunk_idx >= len(self._chunks):
                return  # 提示符已不存在，停止闪烁
            tag = "prompt" if not self._panel_open else "prompt"
            color = "#555555" if state % 2 == 0 else "#333333"
            self.text_area.tag_configure("prompt", foreground=color, font=self.FONT_SMALL)
            self._prompt_blink_job = self.root.after(700, lambda: _blink(state + 1))
        _blink()

    def _cancel_prompt_blink(self):
        """取消提示符闪烁"""
        if self._prompt_blink_job:
            self.root.after_cancel(self._prompt_blink_job)
            self._prompt_blink_job = None

    def _start_pause(self, seconds: float):
        """开始暂停计时，N 秒后自动翻页。玩家按空格可跳过。"""
        self._is_pausing = True
        self._pause_job = self.root.after(int(seconds * 1000), self._finish_pause)

    def _finish_pause(self):
        """暂停结束，自动推进到下一块。面板打开时不推进。"""
        self._is_pausing = False
        self._pause_job = None
        if self._panel_open:
            return
        self._typewrite_current_chunk()

    def _on_text_advance(self, event=None):
        """空格/回车/点击：打字中→跳过；暂停中→跳过等待；等待中→翻页（面板打开时暂停文本推进）"""
        if self._panel_open:
            return "break"
        # 结局画面模式：翻页触发 on_text_complete 回调
        if getattr(self, '_ending_screen', False):
            self._ending_screen = False
            if self.on_text_complete:
                self.on_text_complete()
            return "break"
        # 结局收集模式：空格/回车返回标题
        if getattr(self, '_col_mode', None):
            if self.on_text_complete:
                self.on_text_complete()
            return "break"
        if self._is_pausing:
            if self._pause_job:
                self.root.after_cancel(self._pause_job)
                self._pause_job = None
            self._is_pausing = False
            self._typewrite_current_chunk()
            return "break"
        if not self._chunks:
            return
        if self._is_typing:
            self._skip_typing()
        elif self._chunk_idx < len(self._chunks):
            self._remove_prompt()
            self._typewrite_current_chunk()
        return "break"

    def _remove_prompt(self):
        """移除翻页提示（含前导空行）"""
        self._cancel_prompt_blink()
        self.text_area.config(state=tk.NORMAL)
        # 删除空行+提示行：从倒数第二行行首到末尾
        last_line = self.text_area.index("end-2l linestart")
        self.text_area.delete(last_line, tk.END)
        self.text_area.config(state=tk.DISABLED)

    def _on_all_chunks_done(self):
        """所有块打印完毕 → 触发回调，让外部显示选项"""
        self._is_typing = False
        self._cancel_prompt_blink()
        if self.on_text_complete:
            self.on_text_complete()

    def _append(self, text: str):
        """往文本区末尾追加文字（自动切换 NORMAL/DISABLED）"""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text)
        self.text_area.config(state=tk.DISABLED)

    def _append_tagged(self, text: str, tag: str):
        """追加带 tag 的文字"""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text, tag)
        self.text_area.config(state=tk.DISABLED)

    # ---------- 保留兼容旧调用（show_text_full → show_chunked_text）----------
    def show_text_full(self, text: str):
        self.show_chunked_text(text)

    def clear_choices(self):
        """清除所有选项按钮"""
        for row in self._choice_rows:
            row.destroy()
        self._choice_rows = []
        self._choice_labels = []

    def update_choice_label(self, index: int, new_text: str, fg: str = None):
        """更新指定选项的文字和颜色（multi_click 连点时用）"""
        if index < len(self._choice_labels):
            lbl = self._choice_labels[index]
            lbl.config(text=new_text)
            if fg:
                lbl.config(fg=fg)

    def gray_choices(self):
        """将所有选项变灰并禁用交互（OPT-04）"""
        for row in self._choice_rows:
            for child in row.winfo_children():
                if isinstance(child, tk.Label):
                    try:
                        child.config(fg="#555555", cursor="")
                    except Exception:
                        pass
            # 解绑所有交互事件
            row.unbind("<Enter>")
            row.unbind("<Leave>")
            row.unbind("<Button-1>")
            for child in row.winfo_children():
                child.unbind("<Enter>")
                child.unbind("<Leave>")
                child.unbind("<Button-1>")

    # ========== 实用方法 ==========

    def update_day(self, day: int, chapter: int = None):
        chapter_names = {1: "抵达", 2: "初现", 3: "深入",
                         4: "抉择", 5: "对抗", 6: "结局"}  # OPT-08
        parts = []
        if chapter:
            cname = chapter_names.get(chapter, "")
            if cname:
                parts.append("第{}章 · {}".format(chapter, cname))
            else:
                parts.append("第{}章".format(chapter))
        parts.append("第 {} 天".format(day))
        self.day_label.config(text="  ".join(parts))
        # OPT-10: 窗口标题栏同步章节名
        if chapter:
            self.root.title("灯塔 —— 第{}章 · {}".format(chapter, chapter_names.get(chapter, "")))

    def get_text_widget(self):
        return self.text_area

    # ========== 存档/读档界面（OPT-13：纳入主窗口，不弹独立浮窗） ==========

    def show_save_dialog(self, slots_info, on_slot_click):
        """显示存档界面（主窗口内右侧滑入）。slots_info: [{"slot": 1, "exists": bool, "save_time":"", "day":1}, ...]"""
        self._show_save_load_dialog("存档", slots_info, on_slot_click)

    def show_load_dialog(self, slots_info, on_slot_click):
        """显示读档界面（主窗口内右侧滑入）。slots_info 同上"""
        filtered = [s for s in slots_info if s.get("exists")]
        if not filtered:
            self.flash_save_status("没有可用的存档")
            return
        self._show_save_load_dialog("读档", filtered, on_slot_click)

    def _show_save_load_dialog(self, title: str, slots_info: list, on_slot_click):
        """存档/读档通用面板：右侧滑入，覆盖层半透明"""
        self._sl_panel_open = True
        # 遮罩层（点击关闭）
        self._sl_dim = tk.Frame(self.root, bg="#000000")
        self._sl_dim.place(x=0, y=0, relwidth=1, relheight=1)
        self._sl_dim.lift()
        self._sl_dim.bind("<Button-1>", lambda e: self._hide_save_load_dialog())
        # 面板
        self._sl_frame = tk.Frame(self.root, bg=self.COLORS["panel_bg"])
        self._sl_frame.place(relx=1.0, y=0, relwidth=0.35, relheight=1, anchor="ne")
        self._sl_frame.lift()
        # 标题
        tk.Label(self._sl_frame, text=title,
                 font=("Microsoft YaHei", 13, "bold"),
                 fg=self.COLORS["dim"], bg=self.COLORS["panel_bg"]).pack(
                     anchor=tk.W, padx=20, pady=(20, 12))
        # 存档位列表（手动 4 位在上，自动位独立在下方）
        auto_info = None
        for info in slots_info:
            slot = info["slot"]
            # 自动位单独处理
            if slot == "auto":
                auto_info = info
                continue
            self._render_save_slot_row(slot, info, on_slot_click)
        # 自动存档位（独立区域）
        if auto_info:
            tk.Label(self._sl_frame, text="—— 自动存档 ——",
                     font=("Microsoft YaHei", 9),
                     fg="#555555", bg=self.COLORS["panel_bg"]).pack(
                         anchor=tk.W, padx=20, pady=(16, 4))
            self._render_save_slot_row("auto", auto_info, on_slot_click)

    def _render_save_slot_row(self, slot, info, on_slot_click):
        """渲染单个存档位行（手动位或自动位）"""
        slot_label = "自动存档" if slot == "auto" else "存档位 {}".format(slot)
        if info.get("exists"):
            txt = "{} | {} | 第{}天".format(slot_label,
                info.get("save_time", ""), info.get("day", "?"))
        else:
            txt = "{} | （空）".format(slot_label)
        row = tk.Frame(self._sl_frame, bg=self.COLORS["panel_bg"])
        row.pack(fill=tk.X, padx=20, pady=3)
        lbl = tk.Label(row, text=txt,
                       font=("Microsoft YaHei", 10),
                       fg=self.COLORS["text"], bg=self.COLORS["panel_bg"],
                       cursor="hand2", anchor=tk.W)
        lbl.pack(fill=tk.X)
        lbl.bind("<Enter>", lambda e, l=lbl: l.config(fg=self.COLORS["accent"]))
        lbl.bind("<Leave>", lambda e, l=lbl: l.config(fg=self.COLORS["text"]))
        def make_cb(s=slot, cb=on_slot_click):
            return lambda e: (self._hide_save_load_dialog(), cb(s))
        lbl.bind("<Button-1>", make_cb())

    def _hide_save_load_dialog(self):
        """关闭存档/读档面板"""
        self._sl_panel_open = False
        if hasattr(self, '_sl_dim') and self._sl_dim:
            self._sl_dim.destroy()
            self._sl_dim = None
        if hasattr(self, '_sl_frame') and self._sl_frame:
            self._sl_frame.destroy()
            self._sl_frame = None

    # ========== 状态面板（4B：Tab 滑入遮罩） ==========

    def toggle_panel(self):
        if self._panel_open:
            self._hide_panel()
        else:
            self._show_panel()

    def _show_panel(self):
        """右侧滑入面板（暂停逐字打印 + 文本推进 + M5 音效淡出）"""
        self._panel_open = True
        # M5 面板打开静默，待配表工具启用
        # if self._sound_mgr:
        #     self._sound_mgr.stop_all()
        # 暂停逐字打印定时器
        if self._typewriter_job:
            self.root.after_cancel(self._typewriter_job)
            self._typewriter_job = None
        # 暂停暂停计时器（防止文本在面板背后自动翻页）
        if self._pause_job:
            self.root.after_cancel(self._pause_job)
            self._pause_job = None
        # 遮罩
        self._dim_layer = tk.Frame(self.root, bg="#000000")
        self._dim_layer.place(x=0, y=0, relwidth=1, relheight=1)
        self._dim_layer.lift()
        self._dim_layer.bind("<Button-1>", lambda e: self._hide_panel())
        # 面板
        self._panel_frame = tk.Frame(self.root, bg=self.COLORS["panel_bg"])
        self._panel_frame.place(relx=1.0, y=0, relwidth=0.32, relheight=1,
                                anchor="ne")
        self._panel_frame.lift()
        self._build_panel_content()
        # 从缓存渲染数据
        if self._diary_cache:
            self._render_diary()
        if self._cached_status:
            self.update_panel_status(self._cached_status)
        self.update_panel_items(self._cached_items)
        # 滑入动画
        self._panel_frame.place(relx=1.0, y=0, relwidth=0.32, relheight=1,
                                x=-int(self.root.winfo_width() * 0.32), anchor="ne")
        self.root.update()
        self._panel_frame.place(relx=1.0, y=0, relwidth=0.32, relheight=1,
                                anchor="ne")

    def _hide_panel(self):
        """关闭面板"""
        self._panel_open = False
        if self._dim_layer:
            self._dim_layer.destroy()
            self._dim_layer = None
        if self._panel_frame:
            self._panel_frame.destroy()
            self._panel_frame = None
        if self.on_toggle_panel:
            self.on_toggle_panel(False)

    def _build_panel_content(self):
        """构建面板内容：可滚动区域（OPT-14）+ 标题/笔记/状态/物品"""
        pad = 16
        # 标题（固定不滚动）
        self._panel_title = tk.Label(self._panel_frame, text="备忘录",
                 font=("Microsoft YaHei", 13, "bold"),
                 fg=self.COLORS["dim"], bg=self.COLORS["panel_bg"])
        self._panel_title.pack(anchor=tk.W, padx=pad, pady=(16, 8))
        # 可滚动内容区（Canvas + 内嵌 Frame）
        canvas_container = tk.Frame(self._panel_frame, bg=self.COLORS["panel_bg"])
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=(pad, 0))
        self._panel_canvas = tk.Canvas(canvas_container, bg=self.COLORS["panel_bg"],
                                        highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(canvas_container, orient=tk.VERTICAL,
                                  command=self._panel_canvas.yview)
        self._panel_inner = tk.Frame(self._panel_canvas, bg=self.COLORS["panel_bg"])
        self._panel_inner.bind("<Configure>",
            lambda e: self._panel_canvas.configure(scrollregion=self._panel_canvas.bbox("all")))
        self._panel_canvas_window = self._panel_canvas.create_window((0, 0), window=self._panel_inner, anchor=tk.NW)
        def _on_panel_canvas_resize(event):
            self._panel_canvas.itemconfig(self._panel_canvas_window, width=event.width)
        self._panel_canvas.bind("<Configure>", _on_panel_canvas_resize)
        self._panel_canvas.configure(yscrollcommand=scrollbar.set)
        self._panel_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # 画布本地滚轮
        self._panel_canvas.bind("<MouseWheel>",
            lambda ev: (self._panel_canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")
                        if self._panel_canvas.winfo_exists() else None))

        # 日记区（灰色边框 + 导航 + 加长文本区）
        self._diary_frame = tk.LabelFrame(self._panel_inner, text="日记",
            font=("Microsoft YaHei", 9, "bold"),
            fg="#666666", bg=self.COLORS["panel_bg"],
            foreground="#666666",
            relief=tk.GROOVE, borderwidth=1)
        self._diary_frame.pack(fill=tk.X, pady=(0, 10))

        # 导航栏
        nav_bar = tk.Frame(self._diary_frame, bg=self.COLORS["panel_bg"])
        nav_bar.pack(fill=tk.X, padx=4, pady=(4, 2))
        self._diary_prev_btn = tk.Label(nav_bar, text="◀ 前一天",
            font=("Microsoft YaHei", 8), fg="#555555",
            bg=self.COLORS["panel_bg"], cursor="hand2")
        self._diary_prev_btn.pack(side=tk.LEFT)
        self._diary_prev_btn.bind("<Button-1>", lambda e: self._diary_nav(-1))
        self._diary_day_label = tk.Label(nav_bar, text="",
            font=("Microsoft YaHei", 8, "bold"), fg="#cccccc",
            bg=self.COLORS["panel_bg"])
        self._diary_day_label.pack(side=tk.LEFT, padx=12)
        self._diary_next_btn = tk.Label(nav_bar, text="后一天 ▶",
            font=("Microsoft YaHei", 8), fg="#555555",
            bg=self.COLORS["panel_bg"], cursor="hand2")
        self._diary_next_btn.pack(side=tk.LEFT)
        self._diary_next_btn.bind("<Button-1>", lambda e: self._diary_nav(1))

        self._panl_notes_text = tk.Text(
            self._diary_frame,
            wrap=tk.WORD,
            font=("Microsoft YaHei", 9, "italic"),
            fg="#555555", bg=self.COLORS["panel_bg"],
            borderwidth=0, highlightthickness=0,
            relief=tk.FLAT,
            width=28, height=10,
            state=tk.DISABLED,
        )
        self._panl_notes_text.pack(fill=tk.X, padx=4, pady=(0, 6))
        # 日记文本独立滚轮
        self._panl_notes_text.bind("<MouseWheel>",
            lambda ev: self._panl_notes_text.yview_scroll(int(-1 * (ev.delta / 120)), "units"))
        self._panl_notes_text.tag_configure("notes",
            foreground="#555555", font=("Microsoft YaHei", 9, "italic"))
        self._panl_notes_text.tag_configure("marked",
            foreground="#cc0000", font=("Microsoft YaHei", 9, "italic", "underline"))
        self._panl_notes_text.tag_configure("marked_high",
            foreground="#008800", font=("Microsoft YaHei", 9, "italic", "underline"))
        # 状态标题
        tk.Label(self._panel_inner, text="状态",
                 font=("Microsoft YaHei", 9, "bold"),
                 fg="#555555", bg=self.COLORS["panel_bg"]).pack(
                     anchor=tk.W, pady=(4, 6))
        self._panel_status_area = tk.Frame(self._panel_inner, bg=self.COLORS["panel_bg"])
        self._panel_status_area.pack(fill=tk.X)
        # 物品标题
        tk.Label(self._panel_inner, text="随身物品",
                 font=("Microsoft YaHei", 9, "bold"),
                 fg="#555555", bg=self.COLORS["panel_bg"]).pack(
                     anchor=tk.W, pady=(12, 6))
        self._panel_items_area = tk.Frame(self._panel_inner, bg=self.COLORS["panel_bg"])
        self._panel_items_area.pack(fill=tk.X)

    def update_panel_notes(self, text: str, day: int = None):
        """更新面板日记。缓存数据，面板打开时才渲染。日记仅显示前一天的记录。"""
        if day is not None and text:
            self._diary_cache[str(day)] = text
            # 日记只能在第二天看到前一天的
            display_day = max(1, day - 1)
            self._diary_latest_day = display_day
            self._diary_view_day = display_day
        if self._panel_frame and hasattr(self, '_panl_notes_text'):
            try:
                if self._panl_notes_text.winfo_exists():
                    self._render_diary()
            except tk.TclError:
                pass

    def _render_diary(self):
        """渲染当前 _diary_view_day 对应的日记"""
        if not hasattr(self, '_panl_notes_text'):
            return
        try:
            if not self._panl_notes_text.winfo_exists():
                return
        except tk.TclError:
            return
        day_key = str(self._diary_view_day)
        text = self._diary_cache.get(day_key, "")
        self._panl_notes_text.config(state=tk.NORMAL)
        self._panl_notes_text.delete("1.0", tk.END)
        if text:
            import re
            segments = re.split(r'([\u2021\u2020].*?[\u2021\u2020])', text)
            for seg in segments:
                if seg.startswith("\u2021") and seg.endswith("\u2021"):
                    self._panl_notes_text.insert(tk.END, seg[1:-1], "marked")
                elif seg.startswith("\u2020") and seg.endswith("\u2020"):
                    self._panl_notes_text.insert(tk.END, seg[1:-1], "marked_high")
                else:
                    self._panl_notes_text.insert(tk.END, seg, "notes")
        else:
            self._panl_notes_text.insert(tk.END, "这一天还没有记录。", "notes")
        self._panl_notes_text.config(state=tk.DISABLED)
        if self._diary_view_day > 0:
            ch_names = {1: "抵达", 2: "初现", 3: "深入", 4: "抉择", 5: "对抗", 6: "结局"}
            ch = (self._diary_view_day - 1) // 2 + 1
            ch = min(ch, 6)
            cname = ch_names.get(ch, "")
            self._diary_day_label.config(text="第{}天 · {}".format(self._diary_view_day, cname))
        # 导航按钮可用性
        self._diary_prev_btn.config(
            fg="#888888" if self._diary_view_day <= 1 else "#cccccc",
            cursor="hand2" if self._diary_view_day > 1 else "arrow")
        self._diary_next_btn.config(
            fg="#888888" if self._diary_view_day >= self._diary_latest_day else "#cccccc",
            cursor="hand2" if self._diary_view_day < self._diary_latest_day else "arrow")

    def _diary_nav(self, delta):
        """日记导航：delta=-1上一天，delta=+1下一天"""
        new_day = self._diary_view_day + delta
        if new_day < 1 or new_day > self._diary_latest_day:
            return
        self._diary_view_day = new_day
        self._render_diary()

    def update_panel_status(self, descriptions):
        """更新面板状态区（始终缓存）。descriptions: {"curiosity":"...", "sanity":"...", "trust":"..."}"""
        self._cached_status = descriptions
        if not self._panel_frame:
            return
        for child in self._panel_status_area.winfo_children():
            child.destroy()
        for key in ["curiosity", "sanity", "trust"]:
            desc = descriptions.get(key, "")
            line = tk.Label(self._panel_status_area, text=desc,
                           font=("Microsoft YaHei", 10),
                           fg=self.COLORS["text"], bg=self.COLORS["panel_bg"],
                           wraplength=200, justify=tk.LEFT, anchor=tk.W)
            line.pack(fill=tk.X, pady=3)

    def update_panel_items(self, items):
        """更新面板物品区（始终缓存）。items: [{"name":"日记残页","desc":"模糊的旧日记"}]"""
        self._cached_items = items if items else []
        if not self._panel_frame:
            return
        for child in self._panel_items_area.winfo_children():
            child.destroy()
        if not items:
            tk.Label(self._panel_items_area, text="（空无一物）",
                     font=("Microsoft YaHei", 9, "italic"),
                     fg="#444444", bg=self.COLORS["panel_bg"]).pack(anchor=tk.W)
            return
        # 计算可用宽度（面板 32% 窗口 − 两侧 pad）
        panel_w = self._panel_inner.winfo_width()
        if panel_w < 50:
            panel_w = 240
        wrap_w = max(100, panel_w - 24)
        for item in items:
            item_id = item.get("id", "")
            name = item.get("name", "??")
            desc = item.get("desc", "")
            is_new = item_id and item_id not in self._seen_item_ids
            # 物品行：Frame 容纳名称+可选"（新）"
            row = tk.Frame(self._panel_items_area, bg=self.COLORS["panel_bg"])
            row.pack(fill=tk.X, pady=2)
            lbl = tk.Label(row, text="▸ " + name,
                          font=("Microsoft YaHei", 10),
                          fg=self.COLORS["text"], bg=self.COLORS["panel_bg"],
                          anchor=tk.W, wraplength=wrap_w - 40, justify=tk.LEFT)
            lbl.pack(side=tk.LEFT)
            new_tag = None
            if is_new:
                new_tag = tk.Label(row, text="（新）",
                                   font=("Microsoft YaHei", 10),
                                   fg="#cc0000", bg=self.COLORS["panel_bg"])
                new_tag.pack(side=tk.LEFT)
            if desc:
                def make_enter(d=desc, l=lbl, w=wrap_w - 40, n=name,
                               iid=item_id, row=row):
                    return lambda e: self._on_item_enter(l, w, n, d, iid)
                def make_leave(n=name, l=lbl, w=wrap_w - 40):
                    return lambda e: self._on_item_leave(l, w, n)
                lbl.bind("<Enter>", make_enter())
                lbl.bind("<Leave>", make_leave())

    def _on_item_enter(self, lbl, w, name, desc, item_id):
        lbl.config(wraplength=w, text="▸ " + name + "\n  " + desc)
        if item_id and item_id not in self._seen_item_ids:
            self._seen_item_ids.add(item_id)
            # 刷新面板移除"（新）"
            self.root.after(100, lambda: self.update_panel_items(self._cached_items))

    def _on_item_leave(self, lbl, w, name):
        lbl.config(wraplength=w, text="▸ " + name)

    def flash_save_status(self, msg: str):
        """在状态栏短暂显示存档/读档反馈，1.5秒后恢复"""
        old_text = self.day_label.cget("text")
        self.day_label.config(text=msg, fg=self.COLORS["text"])
        self.root.after(1500, lambda: self.day_label.config(
            text=old_text, fg=self.COLORS["dim"]))

    def show_ending_screen(self, ending_name: str, ending_desc: str, diary_text: str = ""):
        """结局画面：结局名称（大字 #cc0000）+ 描述（小字）+ 可选 D14 日记"""
        self.clear_choices()
        self._is_typewriting = False
        self._chunks = []          # 清空块队列，避免 _on_text_advance 卡在旧数据
        self._ending_screen = True  # 标记结局画面模式，翻页时回调 on_text_complete
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        # 结局名称
        self.text_area.tag_configure("ending_name", font=("Microsoft YaHei", 24, "bold"),
                                     foreground="#cc0000", justify=tk.CENTER)
        self.text_area.tag_configure("ending_desc", font=("Microsoft YaHei", 11),
                                     foreground="#888888", justify=tk.CENTER,
                                     spacing1=8, spacing3=8)
        self.text_area.tag_configure("ending_diary", font=("Microsoft YaHei", 9, "italic"),
                                     foreground="#555555", justify=tk.CENTER,
                                     spacing1=12)
        self.text_area.tag_configure("ending_hint", font=("Microsoft YaHei", 9),
                                     foreground="#444444", justify=tk.CENTER,
                                     spacing1=20)
        self.text_area.insert(tk.END, "\n\n\n")
        self.text_area.insert(tk.END, ending_name + "\n", "ending_name")
        self.text_area.insert(tk.END, "\n")
        self.text_area.insert(tk.END, ending_desc + "\n", "ending_desc")
        if diary_text:
            self.text_area.insert(tk.END, "\n")
            self.text_area.insert(tk.END, diary_text + "\n", "ending_diary")
        self.text_area.insert(tk.END, "\n\n▼ 空格 / 回车返回标题界面", "ending_hint")
        self.text_area.config(state=tk.DISABLED)
        self.day_label.config(text="")

    # ========== GM 调试栏（Ctrl+Shift+G） ==========

    def _toggle_gm(self):
        """切换 GM 调试面板（仅 gm_enabled 时由快捷键调用）"""
        if self._gm_open:
            self._hide_gm_panel()
        else:
            self._show_gm_panel()

    def _show_gm_panel(self):
        """右侧滑入 GM 调试面板"""
        self._gm_open = True
        if self._typewriter_job:
            self.root.after_cancel(self._typewriter_job)
            self._typewriter_job = None
        self._gm_dim_layer = tk.Frame(self.root, bg="#000000")
        self._gm_dim_layer.place(x=0, y=0, relwidth=1, relheight=1)
        self._gm_dim_layer.lift()
        self._gm_dim_layer.bind("<Button-1>", lambda e: self._hide_gm_panel())
        self._gm_frame = tk.Frame(self.root, bg=self.COLORS["panel_bg"])
        self._gm_frame.place(relx=1.0, y=0, relwidth=0.35, relheight=1, anchor="ne")
        self._gm_frame.lift()
        self._build_gm_panel_content()
        # 通知外部刷新数据
        if self.on_gm_open:
            self.on_gm_open()
        self._gm_frame.place(relx=1.0, y=0, relwidth=0.35, relheight=1,
                             x=-int(self.root.winfo_width() * 0.35), anchor="ne")
        self.root.update()
        self._gm_frame.place(relx=1.0, y=0, relwidth=0.35, relheight=1, anchor="ne")

    def _hide_gm_panel(self):
        """关闭 GM 面板"""
        self._gm_open = False
        # 清理全局鼠标滚轮绑定（防止面板关闭后残留绑定访问已销毁 canvas）
        if self.root:
            self.root.unbind_all("<MouseWheel>")
        if self._gm_dim_layer:
            self._gm_dim_layer.destroy()
            self._gm_dim_layer = None
        if self._gm_frame:
            self._gm_frame.destroy()
            self._gm_frame = None

    def _build_gm_panel_content(self):
        """构建 GM 面板内容：加载章节 + 节点列表 + 变量调节 + 预设"""
        pad = 12
        title = tk.Label(self._gm_frame, text="GM 调试",
                          font=("Microsoft YaHei", 12, "bold"),
                          fg="#cc6600", bg=self.COLORS["panel_bg"])
        title.pack(anchor=tk.W, padx=pad, pady=(12, 4))

        # —— 音效状态行（M5 GM） ——
        self._gm_sound_status = tk.Label(self._gm_frame, text="",
                                          font=("Microsoft YaHei", 9, "bold"),
                                          fg="#00cc00", bg=self.COLORS["panel_bg"])
        self._gm_sound_status.pack(anchor=tk.W, padx=pad, pady=(0, 4))

        # —— 加载章节 ——
        tk.Label(self._gm_frame, text="加载章节",
                 font=("Microsoft YaHei", 9, "bold"),
                 fg="#555555", bg=self.COLORS["panel_bg"]).pack(anchor=tk.W, padx=pad, pady=(6, 2))
        self._gm_chapter_btn_frame = tk.Frame(self._gm_frame, bg=self.COLORS["panel_bg"])
        self._gm_chapter_btn_frame.pack(fill=tk.X, padx=pad)

        # —— 节点跳转 ——
        tk.Label(self._gm_frame, text="节点跳转",
                 font=("Microsoft YaHei", 9, "bold"),
                 fg="#555555", bg=self.COLORS["panel_bg"]).pack(anchor=tk.W, padx=pad, pady=(8, 2))
        node_container = tk.Frame(self._gm_frame, bg=self.COLORS["panel_bg"])
        node_container.pack(fill=tk.BOTH, expand=True, padx=pad)
        self._gm_node_canvas = tk.Canvas(node_container, bg=self.COLORS["panel_bg"],
                                         highlightthickness=0, bd=0, width=240)
        scrollbar = tk.Scrollbar(node_container, orient=tk.VERTICAL,
                                 command=self._gm_node_canvas.yview)
        self._gm_node_list = tk.Frame(self._gm_node_canvas, bg=self.COLORS["panel_bg"])
        self._gm_node_list.bind("<Configure>",
            lambda e: self._gm_node_canvas.configure(scrollregion=self._gm_node_canvas.bbox("all")))
        self._gm_node_canvas.create_window((0, 0), window=self._gm_node_list, anchor=tk.NW)
        self._gm_node_canvas.configure(yscrollcommand=scrollbar.set, height=180)
        self._gm_node_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._gm_node_canvas.bind("<Enter>", lambda e: self._gm_node_canvas.bind_all("<MouseWheel>",
            lambda ev: (self._gm_node_canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")
                        if self._gm_node_canvas and self._gm_node_canvas.winfo_exists() else None)))
        self._gm_node_canvas.bind("<Leave>", lambda e: self._gm_node_canvas.unbind_all("<MouseWheel>"))

        # —— 变量调节 ——
        tk.Label(self._gm_frame, text="变量调整",
                 font=("Microsoft YaHei", 9, "bold"),
                 fg="#555555", bg=self.COLORS["panel_bg"]).pack(anchor=tk.W, padx=pad, pady=(8, 2))
        self._gm_var_frame = tk.Frame(self._gm_frame, bg=self.COLORS["panel_bg"])
        self._gm_var_frame.pack(fill=tk.X, padx=pad)

        # —— 预设组合 ——
        tk.Label(self._gm_frame, text="预设组合",
                 font=("Microsoft YaHei", 9, "bold"),
                 fg="#555555", bg=self.COLORS["panel_bg"]).pack(anchor=tk.W, padx=pad, pady=(8, 2))
        self._gm_preset_frame = tk.Frame(self._gm_frame, bg=self.COLORS["panel_bg"])
        self._gm_preset_frame.pack(fill=tk.X, padx=pad)

        # —— GM 工具按钮 ——
        btn_frame = tk.Frame(self._gm_frame, bg=self.COLORS["panel_bg"])
        btn_frame.pack(fill=tk.X, padx=pad, pady=(6, 0))
        self._gm_unlock_btn = tk.Label(btn_frame, text="▸ 解锁全部结局收集",
               font=("Microsoft YaHei", 9),
               fg=self.COLORS["dim"], bg=self.COLORS["panel_bg"],
               cursor="hand2", anchor=tk.W)
        self._gm_unlock_btn.pack(anchor=tk.W)
        self._gm_unlock_btn.bind("<Enter>", lambda e: self._gm_unlock_btn.config(fg=self.COLORS["accent"]))
        self._gm_unlock_btn.bind("<Leave>", lambda e: self._gm_unlock_btn.config(fg=self.COLORS["dim"]))
        self._gm_unlock_btn.bind("<Button-1>",
            lambda e: self.on_gm_unlock_collection and self.on_gm_unlock_collection())

    def refresh_gm_panel(self, nodes_ordered: list, current_node: str, variables: dict,
                          presets: list, chapters_loaded: list, all_chapters: list,
                          node_sounds: dict = None, active_sound: str = None,
                          carry_effects: dict = None):
        """刷新 GM 面板数据。
        nodes_ordered: [(chapter, node_id), ...] 按 JSON 原始顺序
        chapters_loaded: 已加载的章节号列表
        all_chapters: 所有可加载的章节号列表
        node_sounds: {node_id: [sound_name, ...]} M5 GM 音效标注
        active_sound: 当前正在播放的音效名
        """
        if not self._gm_frame:
            return
        node_sounds = node_sounds or {}

        # —— 音效状态更新（M5 GM） ——
        if hasattr(self, '_gm_sound_status') and self._gm_sound_status:
            if active_sound:
                label_map = {"hum_low": "⬤ 播放中: hum_low 低频底噪",
                             "water_drone": "⬤ 播放中: water_drone 水下白噪",
                             "heartbeat": "⬤ 播放中: heartbeat 心跳",
                             "metal_creak": "⬤ 播放中: metal_creak 金属嘎吱",
                             "silence_fade": "⬤ 淡出中..."}
                text = label_map.get(active_sound, "⬤ 播放中: " + active_sound)
                self._gm_sound_status.config(text=text, fg="#00cc00")
            else:
                self._gm_sound_status.config(text="⬤ 无音效播放", fg="#555555")

        # —— 加载章节按钮 ——
        for c in self._gm_chapter_btn_frame.winfo_children():
            c.destroy()
        row = tk.Frame(self._gm_chapter_btn_frame, bg=self.COLORS["panel_bg"])
        row.pack(fill=tk.X)
        for ch in all_chapters:
            loaded = ch in chapters_loaded
            fg = "#00cc00" if loaded else self.COLORS["dim"]
            text = "第{}章{}".format(ch, " ✓" if loaded else "")
            btn = tk.Label(row, text=text, font=("Microsoft YaHei", 9),
                           fg=fg, bg=self.COLORS["panel_bg"], cursor="hand2")
            btn.pack(side=tk.LEFT, padx=4)
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg=self.COLORS["accent"]))
            btn.bind("<Leave>", lambda e, b=btn, f=fg: b.config(fg=f))
            btn.bind("<Button-1>", lambda e, c=ch: self.on_gm_load_chapter(c))

        # —— 节点列表 ——
        self._gm_node_canvas.delete("all")
        if hasattr(self, '_gm_node_list'):
            self._gm_node_list.destroy()
        self._gm_node_list = tk.Frame(self._gm_node_canvas, bg=self.COLORS["panel_bg"])
        self._gm_node_list.bind("<Configure>",
            lambda e: self._gm_node_canvas.configure(scrollregion=self._gm_node_canvas.bbox("all")))
        self._gm_node_canvas.create_window((0, 0), window=self._gm_node_list, anchor=tk.NW, tags="gm_nodes")
        if not nodes_ordered:
            tk.Label(self._gm_node_list, text="请先开始游戏或加载章节",
                     font=("Microsoft YaHei", 9, "italic"),
                     fg="#555555", bg=self.COLORS["panel_bg"]).pack(anchor=tk.W, pady=4)
        else:
            last_ch = None
            for ch, nid in nodes_ordered:
                if ch != last_ch:
                    tk.Label(self._gm_node_list, text="— 第{}章 —".format(ch),
                             font=("Microsoft YaHei", 9, "bold"),
                             fg="#555555", bg=self.COLORS["panel_bg"]).pack(anchor=tk.W, pady=(6, 2))
                    last_ch = ch
                fg = "#cc6600" if nid == current_node else self.COLORS["text"]
                sd_list = node_sounds.get(nid, [])
                sd_text = ""
                if sd_list:
                    abbr = {"hum_low": "L", "heartbeat": "H",
                            "water_drone": "W", "metal_creak": "M",
                            "metal_creak*": "M*"}
                    parts = []
                    for s in sd_list:
                        a = abbr.get(s, "?")
                        parts.append(a)
                    sd_text = "  (" + ",".join(parts) + ")"
                lbl = tk.Label(self._gm_node_list, text="  " + nid + sd_text,
                                font=("Microsoft YaHei", 9),
                                fg=fg, bg=self.COLORS["panel_bg"],
                                cursor="hand2", anchor=tk.W)
                lbl.pack(anchor=tk.W, pady=1)
                lbl.bind("<Enter>", lambda e, l=lbl: l.config(fg=self.COLORS["accent"]))
                lbl.bind("<Leave>", lambda e, l=lbl, f=fg: l.config(fg=f))
                lbl.bind("<Button-1>", lambda e, n=nid: (self.on_gm_jump(n), self._hide_gm_panel()))

        # —— 音效图例（M5 GM） ——
        tk.Label(self._gm_node_list, text="  ──────────────",
                  font=("Microsoft YaHei", 8),
                  fg="#444444", bg=self.COLORS["panel_bg"]).pack(anchor=tk.W, pady=(4, 0))
        legend = "  L=hum_low H=heartbeat W=water_drone M=metal_creak *=失败触发"
        tk.Label(self._gm_node_list, text=legend,
                  font=("Microsoft YaHei", 8, "italic"),
                  fg="#444444", bg=self.COLORS["panel_bg"]).pack(anchor=tk.W, pady=(0, 4))

        # —— 变量调节 ——
        for c in self._gm_var_frame.winfo_children():
            c.destroy()
        var_names = [("curiosity", "好奇心"), ("sanity", "理智"), ("trust", "信任"),
                     ("survival_will", "生存意愿"), ("loyalty", "忠诚")]
        carry = carry_effects or {}
        for key, label in var_names:
            row = tk.Frame(self._gm_var_frame, bg=self.COLORS["panel_bg"])
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text="{}".format(label), font=("Microsoft YaHei", 9),
                     fg="#999999", bg=self.COLORS["panel_bg"], width=8, anchor=tk.W).pack(side=tk.LEFT)
            btn_minus = tk.Label(row, text="−", font=("Microsoft YaHei", 10, "bold"),
                                 fg=self.COLORS["dim"], bg=self.COLORS["panel_bg"], cursor="hand2")
            btn_minus.pack(side=tk.LEFT, padx=2)
            btn_minus.bind("<Button-1>", lambda e, k=key: self.on_gm_set_var(k, -1))
            val = variables.get(key, 0)
            eff = carry.get(key, 0)
            if eff != 0:
                eff_color = "#00cc00" if eff > 0 else "#cc0000"
                display = "{}{:+d}".format(val, eff)
                val_lbl = tk.Label(row, text=display, font=("Microsoft YaHei", 10, "bold"),
                                    fg=eff_color, bg=self.COLORS["panel_bg"], width=6)
            else:
                val_lbl = tk.Label(row, text=str(val), font=("Microsoft YaHei", 10, "bold"),
                                    fg=self.COLORS["text"], bg=self.COLORS["panel_bg"], width=3)
            val_lbl.pack(side=tk.LEFT)
            btn_plus = tk.Label(row, text="+", font=("Microsoft YaHei", 10, "bold"),
                                fg=self.COLORS["dim"], bg=self.COLORS["panel_bg"], cursor="hand2")
            btn_plus.pack(side=tk.LEFT, padx=2)
            btn_plus.bind("<Button-1>", lambda e, k=key: self.on_gm_set_var(k, 1))

        # —— 预设 ——
        for c in self._gm_preset_frame.winfo_children():
            c.destroy()
        for p in presets:
            btn = tk.Label(self._gm_preset_frame, text="▸ " + p["name"],
                           font=("Microsoft YaHei", 9),
                           fg=self.COLORS["dim"], bg=self.COLORS["panel_bg"],
                           cursor="hand2", anchor=tk.W)
            btn.pack(anchor=tk.W, pady=1)
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg=self.COLORS["accent"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(fg=self.COLORS["dim"]))
            def make_cb(preset_name=p["name"]):
                return lambda e: (self.on_gm_preset(preset_name), self._hide_gm_panel())
            btn.bind("<Button-1>", make_cb())

    # ========== 更新闪烁提示 ==========

    def flash_update_indicator(self):
        """备忘录更新提示：'✦ 新内容加入' 亮起在 Tab 左侧，6秒后消失"""
        if not hasattr(self, '_notify_label'):
            return
        if hasattr(self, '_bubble_job') and self._bubble_job:
            self.root.after_cancel(self._bubble_job)
        # 气泡通知
        self._notify_label.config(text=" ✦ 新内容加入", bg="#332200")
        # Tab 标签同步脉冲：亮→暗→亮→恢复（1.5秒）
        self._tab_hint.config(fg="#ccaa44")
        self.root.after(400, lambda: self._tab_hint.config(fg="#333333"))
        self.root.after(800, lambda: self._tab_hint.config(fg="#ccaa44"))
        self.root.after(1200, lambda: self._tab_hint.config(fg="#555555"))
        self._bubble_job = self.root.after(6000, self._hide_bubble)

    # ========== 结局收集界面 ==========

    def show_collection_screen(self, collection_data: dict):
        """结局收集主界面：4×2 格子，已解锁白色/可点击，未解锁灰色/不可点击"""
        self._in_title_screen = False
        self.clear_choices()
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.tag_configure("col_title", font=("Microsoft YaHei", 16, "bold"),
                                     foreground="#e8e8e8", justify=tk.CENTER)
        self.text_area.tag_configure("col_desc", font=("Microsoft YaHei", 9),
                                     foreground="#555555", justify=tk.CENTER)
        self.text_area.tag_configure("col_unlocked", font=("Microsoft YaHei", 11, "bold"),
                                     foreground="#e8e8e8", background="#1a1a1a",
                                     justify=tk.CENTER, lmargin1=20, lmargin2=20,
                                     spacing1=6, spacing3=6)
        self.text_area.tag_configure("col_locked", font=("Microsoft YaHei", 11),
                                     foreground="#333333", background="#0a0a0a",
                                     justify=tk.CENTER, lmargin1=20, lmargin2=20,
                                     spacing1=6, spacing3=6)
        self.text_area.tag_configure("col_back", font=("Microsoft YaHei", 9),
                                     foreground="#888888", justify=tk.CENTER,
                                     spacing1=20)
        endings = collection_data.get("endings", {})
        order = ["G", "death", "F", "A", "E", "B", "D", "C"]
        unlocked = collection_data.get("unlocked", [])

        self.text_area.insert(tk.END, "\n\n")
        self.text_area.insert(tk.END, "结局收集\n", "col_title")
        self.text_area.insert(tk.END, "\n")

        # 4×2 布局：每两个结局一行
        for row_idx in range(4):
            line = ""
            for col_idx in range(2):
                idx = row_idx * 2 + col_idx
                if idx >= len(order):
                    break
                eid = order[idx]
                info = endings.get(eid, {})
                if eid in unlocked:
                    line += info.get("name", eid)
                else:
                    line += "？？？"
                if col_idx == 0:
                    line += "    │    "
            # 判断用哪个 tag（取每行第一个结局的解锁状态）
            first_eid = order[row_idx * 2]
            tag = "col_unlocked" if first_eid in unlocked else "col_locked"
            self.text_area.insert(tk.END, line + "\n", tag)
        self.text_area.insert(tk.END, "\n")
        self.text_area.insert(tk.END, "▼ 空格 / 回车返回    ▸ 点击已解锁结局查看详情\n", "col_back")
        self.text_area.config(state=tk.DISABLED)
        # 绑定回调
        self._collection_data = collection_data
        self._collection_unlocked = unlocked
        self._collection_endings = endings
        self._collection_order = order
        self._col_mode = "main"

    def show_collection_detail(self, ending_id: str):
        """结局收集二级界面：路线+条件"""
        info = self._collection_endings.get(ending_id, {})
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.tag_configure("col_det_name", font=("Microsoft YaHei", 18, "bold"),
                                     foreground="#cc0000", justify=tk.CENTER)
        self.text_area.tag_configure("col_det_label", font=("Microsoft YaHei", 9, "bold"),
                                     foreground="#888888", justify=tk.LEFT)
        self.text_area.tag_configure("col_det_text", font=("Microsoft YaHei", 9),
                                     foreground="#cccccc", justify=tk.LEFT,
                                     spacing1=2, spacing3=4)
        self.text_area.tag_configure("col_det_back", font=("Microsoft YaHei", 9),
                                     foreground="#888888", justify=tk.CENTER,
                                     spacing1=16)
        self.text_area.insert(tk.END, "\n\n")
        self.text_area.insert(tk.END, info.get("name", ending_id) + "\n", "col_det_name")
        self.text_area.insert(tk.END, "\n")
        self.text_area.insert(tk.END, "变量条件\n", "col_det_label")
        self.text_area.insert(tk.END, info.get("var_conditions", "") + "\n", "col_det_text")
        self.text_area.insert(tk.END, "\n")
        self.text_area.insert(tk.END, "物品条件\n", "col_det_label")
        self.text_area.insert(tk.END, info.get("item_conditions", "") + "\n", "col_det_text")
        self.text_area.insert(tk.END, "\n")
        self.text_area.insert(tk.END, "可达路线\n", "col_det_label")
        self.text_area.insert(tk.END, info.get("route", "") + "\n", "col_det_text")
        self.text_area.insert(tk.END, "\n\n")
        self.text_area.insert(tk.END, "▸ 返回收集列表    ▼ 空格返回标题\n", "col_det_back")
        self.text_area.config(state=tk.DISABLED)
        self._col_mode = "detail"

    def _on_collection_click(self, event):
        """处理结局收集界面的点击"""
        if not hasattr(self, '_col_mode'):
            return
        if self._col_mode == "detail":
            # 返回收集列表
            self.show_collection_screen(self._collection_data)
            return
        if self._col_mode != "main":
            return
        # 主界面：判断点击位置对应哪个结局
        index = self.text_area.index("@{},{}".format(event.x, event.y))
        line_num = int(index.split(".")[0])
        # 行 3-6 对应 4 行结局（标题占前 2 行）
        row_idx = line_num - 3
        if row_idx < 0 or row_idx >= 4:
            return
        # 检测点击在左半还是右半
        col_idx = 0 if event.x < self.text_area.winfo_width() // 2 else 1
        idx = row_idx * 2 + col_idx
        if idx >= len(self._collection_order):
            return
        eid = self._collection_order[idx]
        if eid in self._collection_unlocked:
            self.show_collection_detail(eid)

    def _hide_bubble(self):
        if hasattr(self, '_notify_label') and self._notify_label:
            self._notify_label.config(text="", bg=self.COLORS["status_bg"])
        self._bubble_job = None

    # ========== 小游戏区域（OPT-11: 居中 + UI 框） ==========

    MG_WIDTH = 700
    MG_HEIGHT = 550

    def _build_minigame_area(self):
        """构建小游戏外层居中框架（固定尺寸+外框）"""
        # 外层居中容器（带 #555555 可见边框）
        self._mg_outer = tk.Frame(self.root, bg="#000000",
                                   highlightbackground="#555555",
                                   highlightthickness=3)
        # 内层游戏区（MinigameBase / DarknessOverlay 的父容器）
        self.minigame_area = tk.Frame(self._mg_outer, bg="#000000")
        self.minigame_area.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    def show_minigame(self):
        """显示小游戏覆盖层——全屏黑底 + 居中固定尺寸 700×550，带 #555555 可见外框"""
        self.text_area.unbind("<space>")
        self.text_area.unbind("<Return>")
        self.text_area.unbind("<Button-1>")
        # 全屏黑色遮罩（屏蔽文本区）
        self._mg_backdrop = tk.Frame(self.root, bg="#000000")
        self._mg_backdrop.place(x=0, y=0, relwidth=1, relheight=1)
        self._mg_backdrop.lift()
        # 居中（减去底部 32px 状态栏）；未渲染时用默认尺寸兜底
        ww = self.root.winfo_width()
        wh = self.root.winfo_height()
        if ww < 100 or wh < 100:
            ww, wh = 860, 640
        wh -= 32
        x = (ww - self.MG_WIDTH) // 2
        y = (wh - self.MG_HEIGHT) // 2
        self._mg_outer.place(x=x, y=y, width=self.MG_WIDTH, height=self.MG_HEIGHT)
        self._mg_outer.lift()
        self._mg_outer.focus_set()
        self.root.update_idletasks()  # 强制渲染布局，确保 winfo_width 正确

    def hide_minigame(self):
        """隐藏小游戏覆盖层，恢复文本区键盘事件"""
        if hasattr(self, '_mg_backdrop') and self._mg_backdrop:
            self._mg_backdrop.destroy()
            self._mg_backdrop = None
        self._mg_outer.place_forget()
        for child in list(self.minigame_area.winfo_children()):
            child.destroy()
        self.text_area.bind("<space>", self._on_text_advance)
        self.text_area.bind("<Return>", self._on_text_advance)
        self.text_area.bind("<Button-1>", self._on_text_advance)
