# -*- coding: utf-8 -*-
"""
test_all_endings_walkthrough.py —— 8 结局全路径模拟验证
模拟玩家选择链，到达 ch06_ending_check 后验证 check_ending() 返回预期结局。
"""
import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from state_manager import StateManager
from story_engine import StoryEngine
from item_manager import ItemManager


class TestAllEndingsWalkthrough(unittest.TestCase):

    def setUp(self):
        self.sm = StateManager()
        self.im = ItemManager()
        self.st = StoryEngine(self.sm)
        self.st.set_item_manager(self.im)
        self.im.reset()
        self.st.flags.clear()

    def _pick(self, label_contains: str):
        choices = self.st.get_available_choices()
        for i, c in enumerate(choices):
            if label_contains in c.get("label", ""):
                return self.st.make_choice(i)
        return None

    def _goto_ch06_check(self):
        self.st.load_chapter(6)
        self.st.goto_node("ch06_ending_check")

    # ===== 结局 G：荒诞（三玩具） =====

    def test_ending_G_path(self):
        # 锡兵（ch02 墙缝） + 八音盒（ch03 拿走八音盒） + 暖弹珠（ch04 梦境醒选弹珠）
        self.im.acquire("tin_soldier")
        self.im.acquire("music_box")
        self.im.acquire("warm_marble")
        self._goto_ch06_check()
        self.assertEqual(self.st.check_ending(), "G",
            "三玩具齐 → 结局 G")

    # ===== 结局 F：被背叛 =====

    def test_ending_F_path(self):
        # 全程高好奇 + 降信任 + 降低忠诚
        # ch01: 探索灯塔(c+2→1) + 问张海生(c+1→1?)
        # ch02: 追问螺丝(c+1,t-1) + 下床检查(c+1,s-1) + 站着不动(c+1,s-2) + 追问十年前(c+1,t+1) + 四处走走(c+1)
        # ch03: 开铁门(c+1,s-1,l-1) + 打开墙(c+1,s-1) + 继续拆(c+1,s-2) + 偷课本(t-2,l-2,条件l≤2)
        # ch05: 逃跑(t-2,l-2) — 但这条走E路线
        # 走 F 路线：c≥7,s≤3,t≤3,l≤2
        self.sm.change("curiosity", 8 - self.sm.get("curiosity"))
        self.sm.change("sanity", 3 - self.sm.get("sanity"))
        self.sm.change("trust", 3 - self.sm.get("trust"))
        self.sm.change("loyalty", 2 - self.sm.get("loyalty"))
        self._goto_ch06_check()
        self.assertEqual(self.st.check_ending(), "F",
            "c≥7,s≤3,t≤3,l≤2 → 结局 F")

    # ===== 结局 A：疯狂 =====

    def test_ending_A_path(self):
        # c≥7,s≤3,(t≥5 或 l≥3)
        self.sm.change("curiosity", 8 - self.sm.get("curiosity"))
        self.sm.change("sanity", 3 - self.sm.get("sanity"))
        self.sm.change("trust", 5 - self.sm.get("trust"))  # trust≥5
        self.sm.change("loyalty", 2 - self.sm.get("loyalty"))
        self._goto_ch06_check()
        self.assertEqual(self.st.check_ending(), "A",
            "c≥7,s≤3,t≥5 → 结局 A")

    def test_ending_A_path_loyalty(self):
        # A 路径：靠 loyalty≥3 进入
        self.sm.change("curiosity", 8 - self.sm.get("curiosity"))
        self.sm.change("sanity", 3 - self.sm.get("sanity"))
        self.sm.change("trust", 2 - self.sm.get("trust"))
        self.sm.change("loyalty", 3 - self.sm.get("loyalty"))
        self._goto_ch06_check()
        self.assertEqual(self.st.check_ending(), "A",
            "c≥7,s≤3,l≥3 → 结局 A")

    # ===== 结局 E：提前逃离 =====

    def test_ending_E_path(self):
        """E 路径需要原始 survival_will≥8（不含物品效果）在 ch05 条件选项中"""
        self.sm.change("survival_will", 8 - self.sm.get("survival_will"))
        self.sm.change("sanity", 4 - self.sm.get("sanity"))
        self.sm.change("trust", 4 - self.sm.get("trust"))
        self.st.load_chapter(5)
        self.st.goto_node("ch05_d12_start")
        choices = self.st.get_available_choices()
        escape = [c for c in choices if "通讯室" in c.get("label", "")]
        self.assertTrue(len(escape) > 0, "E 逃离选项应对 sw≥8,s≤4,t≤4 可见（需原始值，不含物品效果）")

    # ===== 结局 B：一起逃离（变量 + 钢笔） =====

    def test_ending_B_path(self):
        # c≥6,s≥6,t≥7,l≥4 + 钢笔
        self.im.acquire("pen")
        self.sm.change("curiosity", 6 - self.sm.get("curiosity"))
        self.sm.change("sanity", 6 - self.sm.get("sanity"))
        self.sm.change("trust", 7 - self.sm.get("trust"))
        self.sm.change("loyalty", 4 - self.sm.get("loyalty"))
        self._goto_ch06_check()
        self.assertEqual(self.st.check_ending(), "B",
            "c≥6,s≥6,t≥7,l≥4+钢笔 → 结局 B")

    def test_ending_B_no_pen(self):
        # 同样变量但无钢笔 → 不触发 B
        self.sm.change("curiosity", 6 - self.sm.get("curiosity"))
        self.sm.change("sanity", 6 - self.sm.get("sanity"))
        self.sm.change("trust", 7 - self.sm.get("trust"))
        self.sm.change("loyalty", 4 - self.sm.get("loyalty"))
        self._goto_ch06_check()
        self.assertNotEqual(self.st.check_ending(), "B",
            "同样变量无钢笔 → 非 B")

    # ===== 结局 D：被杀（变量 + 课本） =====

    def test_ending_D_path(self):
        # c≤3,s≥6,t≤3,l≤2 + 课本
        self.im.acquire("zhang_textbook")
        self.sm.change("curiosity", 3 - self.sm.get("curiosity"))
        self.sm.change("sanity", 6 - self.sm.get("sanity"))
        self.sm.change("trust", 3 - self.sm.get("trust"))
        self.sm.change("loyalty", 2 - self.sm.get("loyalty"))
        self._goto_ch06_check()
        self.assertEqual(self.st.check_ending(), "D",
            "c≤3,s≥6,t≤3,l≤2+课本 → 结局 D")

    def test_ending_D_no_textbook(self):
        # D 变量条件但无课本 → C
        self.sm.change("curiosity", 3 - self.sm.get("curiosity"))
        self.sm.change("sanity", 6 - self.sm.get("sanity"))
        self.sm.change("trust", 3 - self.sm.get("trust"))
        self.sm.change("loyalty", 2 - self.sm.get("loyalty"))
        self._goto_ch06_check()
        self.assertEqual(self.st.check_ending(), "C",
            "c≤3,s≥6,t≤3,l≤2无课本 → C（不是 D）")

    # ===== 结局 C：平安离开（万能结局） =====

    def test_ending_C_default(self):
        """C 为万能结局——任意变量组合下，若无其他结局触发，默认进入 C"""
        self._goto_ch06_check()
        self.assertEqual(self.st.check_ending(), "C",
            "C 是万能结局，任何条件下默认进入")

    def test_ending_C_path(self):
        """C 仍可通过保守路径到达"""
        self.sm.change("curiosity", 3 - self.sm.get("curiosity"))
        self.sm.change("sanity", 6 - self.sm.get("sanity"))
        self._goto_ch06_check()
        self.assertEqual(self.st.check_ending(), "C",
            "c≤3,s≥6 → 结局 C")

    # ===== 道具助推验证 =====

    def test_evil_wood_carving_pushes_A(self):
        """邪恶木雕 sanity-2 可助推进入 A/F"""
        self.im.acquire("evil_wood_carving")
        # 有效值 sanity = raw 5 - carry 2 = 3
        self.sm.change("sanity", 5 - self.sm.get("sanity"))
        self.sm.change("curiosity", 8 - self.sm.get("curiosity"))
        self.sm.change("trust", 5 - self.sm.get("trust"))
        self.sm.change("loyalty", 2 - self.sm.get("loyalty"))
        self._goto_ch06_check()
        self.assertEqual(self.st.check_ending(), "A",
            "邪恶木雕 sanity-2 → 有效sanity=3 → 结局 A")

    def test_key_boosts_E(self):
        """钥匙 survival_will+2 帮助结局判定，但 ch05 条件选项读原始值"""
        self.im.acquire("key")
        self.sm.change("survival_will", 6 - self.sm.get("survival_will"))  # 原始 6
        self.sm.change("sanity", 4 - self.sm.get("sanity"))
        self.sm.change("trust", 4 - self.sm.get("trust"))
        cond = {"survival_will": {"min": 8}, "sanity": {"max": 4}, "trust": {"max": 4}}
        # ch05 条件选项读 StateManager 原始值，非有效值
        self.assertFalse(self.sm.check_condition(cond),
            "有效值 sw=8(6+2) 但原始值=6 → E 条件选项不可见")

    # ===== 互斥道具 =====

    def test_warm_marble_evil_wood_mutex(self):
        """暖弹珠和邪恶木雕在 ch04_d8_wake 节点互斥——三选一，不可同时获取。
        测试：仅能通过游戏流程互斥，ItemManager 层面不强制。"""
        self.im.acquire("warm_marble")
        self.im.acquire("evil_wood_carving")  # 直接 acquire 不互斥（互斥在 JSON 选择层）
        self.assertTrue(self.im.has("warm_marble"))
        self.assertTrue(self.im.has("evil_wood_carving"),
            "ItemManager 级别不强制互斥——互斥由 ch04_d8_wake 三选一保证")

    # ===== 优先级验证 =====

    def test_G_overrides_all(self):
        """G 三玩具优先于任何变量组合"""
        self.im.acquire("tin_soldier")
        self.im.acquire("music_box")
        self.im.acquire("warm_marble")
        # 同时满足 F 条件
        self.sm.change("curiosity", 8 - self.sm.get("curiosity"))
        self.sm.change("sanity", 3 - self.sm.get("sanity"))
        self.sm.change("trust", 3 - self.sm.get("trust"))
        self.sm.change("loyalty", 2 - self.sm.get("loyalty"))
        self._goto_ch06_check()
        self.assertEqual(self.st.check_ending(), "G",
            "G 优先于 F")

    def test_D_overrides_C(self):
        """D（c≤3,s≥6,t≤3,l≤2+课本）优先于 C"""
        self.im.acquire("zhang_textbook")
        self.sm.change("curiosity", 3 - self.sm.get("curiosity"))
        self.sm.change("sanity", 6 - self.sm.get("sanity"))
        self.sm.change("trust", 3 - self.sm.get("trust"))
        self.sm.change("loyalty", 2 - self.sm.get("loyalty"))
        self._goto_ch06_check()
        self.assertEqual(self.st.check_ending(), "D",
            "D 优先于 C")

    def test_F_overrides_A(self):
        """F（t≤3,l≤2）优先于 A（t≥5 或 l≥3）"""
        self.sm.change("curiosity", 8 - self.sm.get("curiosity"))
        self.sm.change("sanity", 3 - self.sm.get("sanity"))
        self.sm.change("trust", 3 - self.sm.get("trust"))
        self.sm.change("loyalty", 2 - self.sm.get("loyalty"))
        self._goto_ch06_check()
        self.assertEqual(self.st.check_ending(), "F",
            "F 优先于 A")


if __name__ == "__main__":
    unittest.main()
