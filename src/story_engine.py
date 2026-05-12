# -*- coding: utf-8 -*-
"""
story_engine.py —— 剧情引擎
加载 JSON 剧情文件，管理节点跳转、条件判定筛选。
详见 design.md 4.2 JSON 格式
"""

import json, os, re
from state_manager import StateManager


class StoryEngine:
    """从 JSON 读取剧情节点，根据变量筛选可选选项"""

    def __init__(self, state_mgr: StateManager, data_dir: str = "data"):
        self.state = state_mgr
        self.data_dir = data_dir
        self.nodes = {}
        self._node_order = []  # GM 调试栏用：按 JSON 原始顺序
        self.current_node = None
        self._last_node_id = None  # 最近一次跳转的源节点（text_bridges 来路分流用）
        self.history = []
        self.flags = {}
        self.chapter = 1
        self.day = 1
        self.reached_end = False

    def load_chapter(self, chapter_num: int):
        self.reached_end = False
        path = os.path.join(self.data_dir,
                            f"chapter_{chapter_num:02d}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"剧情文件不存在: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for node in data.get("nodes", []):
            self.nodes[node["node_id"]] = node
            self._node_order.append(node["node_id"])
        start = data.get("start_node")
        if start and self.current_node is None:
            self.current_node = start

    def _ensure_node_loaded(self, node_id: str) -> bool:
        """确保目标节点已加载。若不在 nodes 中，尝试自动加载对应章节。"""
        if node_id in self.nodes:
            return True
        m = re.match(r'ch(\d+)_', node_id)
        if m:
            chapter_num = int(m.group(1))
            try:
                self.load_chapter(chapter_num)
            except FileNotFoundError:
                return False
            return node_id in self.nodes
        return False

    def _jump_to_node(self, node_id: str) -> bool:
        """跳转到目标节点（含跨章节自动加载），返回是否成功"""
        if not self._ensure_node_loaded(node_id):
            self.reached_end = True
            self._last_node_id = self.current_node
            self.current_node = None
            return False
        self._last_node_id = self.current_node
        self.current_node = node_id
        n = self.nodes[node_id]
        self.chapter = n.get("chapter", self.chapter)
        self.day = n.get("day", self.day)
        return True

    def goto_node(self, node_id: str):
        self._last_node_id = self.current_node
        if self._ensure_node_loaded(node_id):
            self.current_node = node_id
            n = self.nodes[node_id]
            self.chapter = n.get("chapter", self.chapter)
            self.day = n.get("day", self.day)
        return self.get_current_node()

    def get_current_node(self):
        return self.nodes.get(self.current_node) if self.current_node else None

    def get_current_text(self) -> str:
        n = self.get_current_node()
        if not n:
            return ""
        text = n.get("text", "")
        # text_bridges 来路分流：根据源节点选择不同的承接桥段
        bridges = n.get("text_bridges")
        if bridges and self._last_node_id:
            bridge = bridges.get(self._last_node_id) or bridges.get("*")
            if bridge:
                text = bridge + "\n\n" + text
        return text

    def check_ending(self) -> str:
        """结局判定（优先级从高到低，命中即止）。
        返回 ending_id ('G'/'death'/'F'/'A'/'E'/'B'/'C'/'D') 或 None（未触发结局）。
        依据 design.md §2.5 结局触发条件表。
        """
        # 优先级 1：隐藏道具三件集齐 → 荒诞
        if (self.flags.get("found_diary_page")
                and self.flags.get("found_wangchao_drawing")
                and self.flags.get("found_dad_logbook")):
            return "G"

        # 优先级 2：MG4/MG5 死亡 → 特殊死亡
        # 由小游戏结果直接触发，不在此处理（见 _on_minigame_complete）

        c = self.state.get("curiosity")
        s = self.state.get("sanity")
        t = self.state.get("trust")
        sw = self.state.get("survival_will")
        l = self.state.get("loyalty")

        # 优先级 3: F 被背叛
        if c >= 7 and s <= 3 and t <= 3 and l <= 2:
            return "F"
        # 优先级 4: A 疯狂
        if c >= 7 and s <= 3 and (t >= 5 or l >= 3):
            return "A"
        # 优先级 5: E 提前逃离
        if sw >= 8 and s <= 4 and t <= 4:
            return "E"
        # 优先级 6: B 一起逃离
        if c >= 6 and s >= 6 and t >= 7 and l >= 4:
            return "B"
        # 优先级 7: D 被杀（必须先于 C 判定——D 是 C 的子集）
        if c <= 3 and s >= 6 and t <= 3 and l <= 2:
            return "D"
        # 优先级 7: C 平安离开
        if c <= 3 and s >= 6:
            return "C"

        return None

    def get_available_choices(self) -> list:
        n = self.get_current_node()
        if not n:
            return []
        choices = n.get("choices", [])
        return [c for c in choices
                if self.state.check_condition(c.get("conditions"))]

    def make_choice(self, idx: int):
        """执行选择，返回 None(结束) / node dict(正常跳转) / minigame dict(触发小游戏)"""
        available = self.get_available_choices()
        if idx < 0 or idx >= len(available):
            raise IndexError(f"无效选择索引: {idx}")
        choice = available[idx]

        if self.current_node:
            self.history.append(self.current_node)

        # 小游戏选择
        mg = choice.get("minigame")
        if mg:
            return {
                "type": "minigame",
                "minigame": mg,
                "success_node": choice.get("success_node"),
                "failure_node": choice.get("failure_node"),
                "success_effects": choice.get("success_effects"),
                "failure_effects": choice.get("failure_effects"),
            }

        # 普通选择：执行 effects + 跳转节点
        effects = choice.get("effects")
        if effects:
            self.state.apply_effects(effects)
        nxt = choice.get("next_node")
        if nxt:
            self._jump_to_node(nxt)
        else:
            cur = self.get_current_node()
            if cur:
                auto = cur.get("auto_next")
                if auto:
                    self._jump_to_node(auto)
        return self.get_current_node()

    def apply_minigame_result(self, success: bool, mg_info: dict):
        """小游戏结束后，根据结果执行 effects 并跳转到对应节点"""
        key = "success" if success else "failure"
        effects = mg_info.get(f"{key}_effects")
        if effects:
            self.state.apply_effects(effects)
        nxt = mg_info.get(f"{key}_node")
        if nxt:
            self._jump_to_node(nxt)
        return self.get_current_node()
