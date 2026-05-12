# -*- coding: utf-8 -*-
"""
main.py —— 游戏主入口 + Game 状态机
迭代 2+3：状态机骨架 + 标题界面交互

状态枚举：
  TITLE        标题界面
  GAME_READY   文本等待中（逐字打印 / 块间等待）
  CHOICES      选项展示中
  MINIGAME     小游戏进行中
  SAVE_LOAD    存档/读档弹窗

运行方式：python src/main.py
"""

import tkinter as tk
import sys, os

from state_manager import StateManager
from save_manager import SaveManager
from story_engine import StoryEngine
from main_window import MainWindow
from sound_manager import SoundManager
from minigame_base import MG1_PowerConnect, MG2_SolarReaction, MG3_PlatformBalance, MG4A_SeabirdDodge
from darkness_overlay import DarknessOverlay

# 结局路由映射（结局 ID → 章节 6 结局链首节点）
ch06_ending_map = {
    "G": "ch06_ending_G",
    "death": "ch06_ending_death",
    "F": "ch06_ending_F",
    "A": "ch06_ending_A",
    "E": "ch06_ending_E",
    "B": "ch06_ending_B",
    "C": "ch06_ending_C",
    "D": "ch06_ending_D",
}


class Game:
    """主控制器 + 状态机"""

    TITLE_QUOTE = (
        "灯塔是活的。它不是石头和铁。它在呼吸。\n"
        "每逢尾数为3的年份，它的呼吸最深。\n"
        "它需要一样东西——一个人。"
    )

    def __init__(self):
        self.root = tk.Tk()
        self.window = MainWindow(self.root)

        # 确保工作目录为项目根
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_dir)

        # 子系统
        self.state_mgr = StateManager()
        self.save_mgr = SaveManager()
        self.story = StoryEngine(self.state_mgr)
        self.sound_mgr = SoundManager()  # FD-12: 音效模块挂载（M4 空壳）

        # 绑定 UI 回调
        self.window.on_menu_new_game = self.cmd_new_game
        self.window.on_menu_continue = self.cmd_continue
        self.window.on_choice_made = self.cmd_choice
        self.window.on_text_complete = self._on_text_done
        self.window.on_save_clicked = self.cmd_save
        self.window.on_load_clicked = self.cmd_load

        # GM 调试栏（--gm 启动参数启用）
        if "--gm" in sys.argv:
            self.window.gm_enabled = True
            self.window.on_gm_jump = self.cmd_gm_jump
            self.window.on_gm_set_var = self.cmd_gm_set_var
            self.window.on_gm_preset = self.cmd_gm_preset
            self.window.on_gm_open = self._refresh_gm_panel
            self.window.on_gm_load_chapter = self.cmd_gm_load_chapter

        # GD 预设组合（GM 栏 v2 · 8 结局）
        self.GM_PRESETS = [
            {"name": "A · 高好奇+低理智（疯狂）", "desc": "结局 A 方向",
             "vars": {"curiosity": 8, "sanity": 2, "trust": 6, "survival_will": 7, "loyalty": 3}},
            {"name": "B · 高好奇+高理智+高信任（一起逃离）", "desc": "结局 B 方向",
             "vars": {"curiosity": 7, "sanity": 7, "trust": 8, "survival_will": 7, "loyalty": 5}},
            {"name": "C · 低好奇+高理智（平安离开）", "desc": "结局 C 方向",
             "vars": {"curiosity": 2, "sanity": 8, "trust": 5, "survival_will": 7, "loyalty": 3}},
            {"name": "D · 低好奇+低信任+低忠诚（被杀）", "desc": "结局 D 方向",
             "vars": {"curiosity": 2, "sanity": 7, "trust": 2, "survival_will": 7, "loyalty": 1}},
            {"name": "E · 高生存+低信任（提前逃离）", "desc": "结局 E 方向",
             "vars": {"curiosity": 5, "sanity": 3, "trust": 3, "survival_will": 9, "loyalty": 3}},
            {"name": "F · 高好奇+背弃（被背叛）", "desc": "结局 F 方向",
             "vars": {"curiosity": 8, "sanity": 2, "trust": 2, "survival_will": 7, "loyalty": 1}},
        ]

        # 当前状态
        self._fsm = "TITLE"

        # 小游戏状态
        self._mg_instance = None
        self._mg_info = None

        # multi_click 状态：{choice_index: click_count}
        self._multi_click_state = {}

    # ========== FSM 状态转移 ==========

    def _goto(self, state: str):
        """状态转移（单出口，方便加日志）"""
        self._fsm = state

    # ========== 命令处理 ==========

    def cmd_new_game(self):
        """新游戏（OPT-03：清除标题菜单残留）"""
        if self._fsm != "TITLE":
            return
        self.window.clear_choices()  # OPT-03
        self._goto("GAME_READY")
        self.state_mgr.reset()
        try:
            self.story.load_chapter(1)
            self.story.goto_node("ch01_start")
        except FileNotFoundError:
            self._show_error("剧情文件未找到\n\n请确保 data/chapter_01.json 存在。")
            return
        self._display_node()

    def cmd_continue(self):
        """继续游戏"""
        if self._fsm != "TITLE":
            return
        data = self.save_mgr.load("auto") or \
               self.save_mgr.load(1) or \
               self.save_mgr.load(2) or \
               self.save_mgr.load(3)
        if data is None:
            self.cmd_new_game()
            return
        self._goto("GAME_READY")
        self.state_mgr.from_dict(data.get("variables", {}))
        self.story.current_node = data.get("current_node")
        self.story.chapter = data.get("chapter", 1)
        self.story.day = data.get("day", 1)
        self.story.history = data.get("history", [])
        self.story.flags = data.get("flags", {})
        self.sound_mgr.from_dict(data.get("sound_state", {}))
        try:
            self.story.load_chapter(self.story.chapter)
        except FileNotFoundError:
            self.story.load_chapter(1)
        self._display_node()

    def cmd_choice(self, index: int):
        """选项点击 → 处理普通选项 / multi_click / 小游戏触发"""
        if self._fsm != "GAME_READY":
            return

        # 检查 multi_click
        node = self.story.get_current_node()
        if node:
            available = self.story.get_available_choices()
            if index < len(available):
                choice = available[index]
                mc = choice.get("multi_click")
                if mc:
                    required = mc.get("count", 3)
                    texts = mc.get("texts", [])
                    if index not in self._multi_click_state:
                        self._multi_click_state[index] = 0
                    self._multi_click_state[index] += 1
                    current = self._multi_click_state[index]
                    if current < required:
                        text_idx = min(current, len(texts) - 1)
                        self.window.update_choice_label(index, texts[text_idx])
                        return
                    else:
                        del self._multi_click_state[index]

        self.window.gray_choices()
        try:
            result = self.story.make_choice(index)
        except (IndexError, KeyError):
            return

        if result is None:
            # 到达终点 / 未完待工
            self._display_node()
            return

        if isinstance(result, dict) and result.get("type") == "minigame":
            # 触发小游戏
            self._mg_info = result
            self._start_minigame(result["minigame"])
            return

        # 普通节点跳转
        self._auto_save()
        self._display_node()

    # ========== 内部方法 ==========

    def _display_node(self):
        """渲染当前节点：逐字文本 + 刷新状态面板"""
        self.window.clear_choices()
        self._multi_click_state = {}
        node = self.story.get_current_node()
        if node is None:
            if self.story.reached_end:
                chapter_name = {1: "抵达", 2: "初现", 3: "深入",
                                4: "抉择", 5: "对抗", 6: "结局"}.get(
                                    self.story.chapter, "第{}章".format(self.story.chapter))
                self.window.show_chunked_text(
                    "（未完待工）\n\n"
                    "你已完成第{}章 · {}。\n"
                    "后续章节正在开发中，请关注更新。\n\n"
                    "[pause 2.0]\n\n"
                    "已为你自动存档。你可以从标题界面\"继续游戏\"回到此处。".format(
                        self.story.chapter, chapter_name)
                )
            else:
                self.window.show_chunked_text("【没有可显示的剧情】")
            self.window.clear_choices()
            self._refresh_panel()
            return

        self.window.show_chunked_text(self.story.get_current_text(), mood=node.get("mood"))
        self.window.update_day(node.get("day", 1), node.get("chapter", 1))
        self._refresh_panel()
        self._refresh_gm_panel()

    def _refresh_panel(self):
        """刷新状态面板：变量描述 + 今日笔记 + 物品列表"""
        desc = {}
        for key in ["curiosity", "sanity", "trust"]:
            desc[key] = self.state_mgr.describe(key, day=self.story.day)
        self.window.update_panel_status(desc)
        # 今日笔记（含章节名 + 天数）
        chapter_names = {1: "抵达", 2: "初现", 3: "深入",
                         4: "抉择", 5: "对抗", 6: "结局"}
        cname = chapter_names.get(self.story.chapter, "第{}章".format(self.story.chapter))
        notes = "第{}天 · {}\n——".format(self.story.day, cname)
        if self.story.day == 1:
            notes += " 抵达灯塔。认识了守塔人张海生。"
        elif self.story.day == 2:
            notes += " 完成设备维护。塔里的声音让人在意。"
        elif self.story.day == 3:
            notes += " 听到了不该听到的声音。水下有东西。"
        elif self.story.day == 4:
            notes += " 高空作业。塔的下面藏着什么。"
        elif self.story.day == 5:
            notes += " 发现了被封住的地下室。墙上有字。"
        elif self.story.day == 6:
            notes += " 找到了不该存在的空间。和遗留的痕迹。"
        elif self.story.day >= 7:
            notes += " 继续守塔的日子。"
        self.window.update_panel_notes(notes)
        # 物品列表
        items = []
        if self.story.flags.get("found_diary"):
            items.append({"name": "日记残页", "desc": "1930年代守塔人的破旧日记，部分页面被撕去。"})
        self.window.update_panel_items(items)

    def _on_text_done(self):
        """文本全部打印完毕 → 显示可选选项，或自动推进"""
        node = self.story.get_current_node()
        if node is None:
            return
        choices = self.story.get_available_choices()
        if choices:
            self.window.show_choices(choices)
        else:
            # 结局判定节点：无选项时自动执行 ending 路由
            if node.get("is_ending_node"):
                ending = self.story.check_ending()
                if ending:
                    target = ch06_ending_map.get(ending)
                    if target:
                        self.story.goto_node(target)
                        self._display_node()
                    return
            auto_next = node.get("auto_next")
            if auto_next:
                self.window.show_choices([{"label": "继续..."}])
                # 覆盖选择回调：无真实选项时，"继续..." 直接触发自动推进
                self.window.on_auto_advance = self.cmd_auto_advance

    def cmd_auto_advance(self):
        """无选项时的自动推进（跟随 auto_next）"""
        self.window.on_auto_advance = None
        self.window.gray_choices()
        node = self.story.get_current_node()
        if node is None:
            return
        auto = node.get("auto_next")
        if auto:
            self.story._jump_to_node(auto)
            self._auto_save()
            self._display_node()

    def _auto_save(self):
        """自动存档"""
        try:
            self.save_mgr.save("auto", self.state_mgr,
                               self.story.current_node,
                               self.story.chapter, self.story.day,
                               self.story.history, self.story.flags,
                               self.sound_mgr.to_dict())
        except Exception:
            pass

    # ========== GM 调试栏命令 ==========

    def cmd_gm_jump(self, node_id: str):
        """GM 节点直跳——跳转后不自动存档"""
        self.story.goto_node(node_id)
        self.window.clear_choices()
        self._goto("GAME_READY")
        self._display_node()
        self._refresh_gm_panel()

    def cmd_gm_set_var(self, key: str, delta: int):
        """GM 变量增量调节"""
        self.state_mgr.change(key, delta)
        self._refresh_panel()
        self._refresh_gm_panel()

    def cmd_gm_preset(self, preset_name: str):
        """GM 应用预设变量组合"""
        for p in self.GM_PRESETS:
            if p["name"] == preset_name:
                self.state_mgr.from_dict(p["vars"])
                break
        self._refresh_panel()
        self._refresh_gm_panel()

    def _refresh_gm_panel(self):
        """刷新 GM 面板数据（从 story_engine 和 state_manager 读取）"""
        if not self.window.gm_enabled:
            return
        # 按 JSON 原始顺序构建节点列表：[(chapter, node_id), ...]
        ordered = []
        for nid in self.story._node_order:
            node = self.story.nodes.get(nid)
            if node:
                ordered.append((node.get("chapter", 0), nid))
        variables = self.state_mgr.get_all()
        # 列出所有已加载的章节号
        chapters_loaded = sorted(set(c for c, _ in ordered))
        all_chapters = [1, 2, 3]  # M4 可用章节
        self.window.refresh_gm_panel(ordered, self.story.current_node or "",
                                     variables, self.GM_PRESETS,
                                     chapters_loaded, all_chapters)

    def cmd_gm_load_chapter(self, chapter_num: int):
        """GM 加载指定章节（已加载则跳过重复加载，仅跳转）"""
        # 检查是否已加载该章任何节点
        already_loaded = any(
            node.get("chapter") == chapter_num
            for node in self.story.nodes.values()
        )
        if not already_loaded:
            try:
                self.story.load_chapter(chapter_num)
            except FileNotFoundError:
                pass
        # 找该章第一个节点作为起始节点
        start = None
        for nid in self.story._node_order:
            node = self.story.nodes.get(nid)
            if node and node.get("chapter") == chapter_num:
                start = nid
                break
        if start:
            self.story.goto_node(start)
        self._refresh_panel()
        self._refresh_gm_panel()

    # ========== 小游戏 ==========

    MG_MAP = {
        "MG1": MG1_PowerConnect,
        "MG2": MG2_SolarReaction,
        "MG3": MG3_PlatformBalance,
        "MG4A": MG4A_SeabirdDodge,
    }

    def _start_minigame(self, mg_name: str):
        """启动小游戏。MG4B 使用 DarknessOverlay 特殊处理。"""
        self._goto("MINIGAME")
        self.window.clear_choices()

        # MG4B 黑暗收缩：使用 DarknessOverlay
        if mg_name == "MG4B":
            self._mg_instance = DarknessOverlay(self.window.minigame_area)
            self._mg_instance.set_complete_callback(lambda: self._on_minigame_complete(True))
            self.window.show_minigame()
            self._mg_instance.start(duration_seconds=50)
            return

        # MG5 黑暗收缩·对抗：使用 DarknessOverlay（V2 不对称，此处暂用 V1）
        if mg_name == "MG5":
            self._mg_instance = DarknessOverlay(self.window.minigame_area)
            self._mg_instance.set_complete_callback(lambda: self._on_minigame_complete(True))
            self.window.show_minigame()
            self._mg_instance.start(duration_seconds=45)
            return

        mg_cls = self.MG_MAP.get(mg_name)
        if mg_cls is None:
            self._on_minigame_complete(False)
            return
        self._mg_instance = mg_cls(self.window.minigame_area)
        self._mg_instance.set_complete_callback(self._on_minigame_complete)
        self.window.show_minigame()
        self._mg_instance.start()

    def _on_minigame_complete(self, success: bool):
        """小游戏结束回调——先销毁实例再清理覆盖层，避免 canvas 已销毁后 unbind 报错"""
        if self._mg_instance:
            self._mg_instance.destroy()
            self._mg_instance = None
        self.window.hide_minigame()
        self._goto("GAME_READY")

        if self._mg_info:
            self.story.apply_minigame_result(success, self._mg_info)
            self._mg_info = None

        self._auto_save()
        self._display_node()

    def cmd_save(self):
        """存档——弹出浮窗选择存档位"""
        info = []
        for slot in [1, 2, 3]:
            si = self.save_mgr.get_info(slot)
            si["slot"] = slot
            info.append(si)
        self.window.show_save_dialog(info, self._do_save)

    def cmd_load(self):
        """读档——弹出浮窗选择存档位"""
        info = []
        for slot in [1, 2, 3, "auto"]:
            si = self.save_mgr.get_info(str(slot))
            si["slot"] = str(slot)
            info.append(si)
        self.window.show_load_dialog(info, self._do_load)

    def _do_save(self, slot):
        """执行存档"""
        try:
            self.save_mgr.save(slot, self.state_mgr,
                               self.story.current_node,
                               self.story.chapter, self.story.day,
                               self.story.history, self.story.flags,
                               self.sound_mgr.to_dict())
            self.window.flash_save_status("已存档 (存档位 {})".format(slot))
        except Exception:
            self.window.flash_save_status("存档失败")
            pass

    def _do_load(self, slot):
        """执行读档"""
        data = self.save_mgr.load(str(slot))
        if data is None:
            self.window.flash_save_status("读档失败：存档不存在")
            return
        self.state_mgr.from_dict(data.get("variables", {}))
        self.story.current_node = data.get("current_node")
        self.story.chapter = data.get("chapter", 1)
        self.story.day = data.get("day", 1)
        self.story.history = data.get("history", [])
        self.story.flags = data.get("flags", {})
        self.sound_mgr.from_dict(data.get("sound_state", {}))
        try:
            self.story.load_chapter(self.story.chapter)
        except FileNotFoundError:
            self.story.load_chapter(1)
        self._goto("GAME_READY")
        self._display_node()
        self.window.flash_save_status("读档完成")

    # ========== 启动 ==========

    def run(self):
        self.window.show_title_screen(self.TITLE_QUOTE)
        self.root.mainloop()

    def _show_error(self, msg: str):
        self.window.show_text_full(msg)


if __name__ == "__main__":
    game = Game()
    game.run()
