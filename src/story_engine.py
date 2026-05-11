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
