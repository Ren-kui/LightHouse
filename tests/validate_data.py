# -*- coding: utf-8 -*-
"""
validate_data.py —— JSON 数据零维护验证
检查全部章节 JSON 文件的结构合法性：
  - node_id 唯一性
  - next_node 引用闭合
  - effect 变量名合法性
  - condition 格式正确
  - auto_next 引用有效
不检查剧情内容、文本质量、设计正确性。
"""

import json
import os
import sys

# 确保项目根目录在 path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from state_manager import StateManager

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
VALID_VARS = set(StateManager.SPEC.keys())


def validate_all():
    errors = []

    for fname in sorted(os.listdir(DATA_DIR)):
        if not fname.startswith("chapter_") or not fname.endswith(".json"):
            continue
        path = os.path.join(DATA_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                errors.append("{} JSON 解析失败: {}".format(fname, e))
                continue

        errors.extend(_validate_chapter(fname, data))

    # 汇聚节点信息报告（供 ND 同源异构扫描用）
    _report_convergence()

    if errors:
        print("\n[FAIL] 发现 {} 个错误:".format(len(errors)))
        for e in errors:
            print("  - {}".format(e))
        return False
    else:
        print("\n[PASS] 全部 JSON 文件结构合法")
        return True


def _validate_chapter(fname, data):
    errors = []
    nodes = data.get("nodes", [])
    if not nodes:
        errors.append("{} 没有节点".format(fname))
        return errors

    # 1. node_id 唯一性
    ids = [n.get("node_id") for n in nodes if n.get("node_id")]
    seen = set()
    for nid in ids:
        if nid in seen:
            errors.append("{} node_id 重复: {}".format(fname, nid))
        seen.add(nid)

    # 收集所有章节的全部 node_id，用于跨章引用检查
    all_ids = set()
    for cf in os.listdir(DATA_DIR):
        if cf.startswith("chapter_") and cf.endswith(".json"):
            with open(os.path.join(DATA_DIR, cf), "r", encoding="utf-8") as f:
                try:
                    cd = json.load(f)
                    for n in cd.get("nodes", []):
                        nid = n.get("node_id")
                        if nid:
                            all_ids.add(nid)
                except json.JSONDecodeError:
                    pass

    # 2. 起始节点存在
    start = data.get("start_node")
    if start and start not in seen:
        errors.append("{} start_node '{}' 不存在".format(fname, start))

    # 3. 每个节点的检查
    for n in nodes:
        nid = n.get("node_id", "???")
        # 必须字段
        for field in ["node_id", "chapter", "day", "text"]:
            if field not in n:
                errors.append("{} / {} 缺少字段: {}".format(fname, nid, field))

        # choices
        choices = n.get("choices", [])
        for i, c in enumerate(choices):
            prefix = "{} / {} / choices[{}]".format(fname, nid, i)

            # next_node 引用
            nxt = c.get("next_node")
            if nxt and nxt not in all_ids:
                errors.append("{} next_node '{}' 不存在".format(prefix, nxt))

            # effects 变量名
            effects = c.get("effects")
            if effects:
                for var_name in effects:
                    if var_name not in VALID_VARS:
                        errors.append("{} effect 非法变量: '{}'".format(prefix, var_name))

            # conditions 格式
            conditions = c.get("conditions")
            if conditions:
                for var_name, constraint in conditions.items():
                    if var_name not in VALID_VARS:
                        errors.append("{} condition 非法变量: '{}'".format(prefix, var_name))
                    if not isinstance(constraint, dict):
                        errors.append("{} condition 值格式错误（应为 dict）: {}".format(prefix, var_name))
                    elif not any(k in constraint for k in ("min", "max", "eq")):
                        errors.append("{} condition 缺少判定符 min/max/eq: {}".format(prefix, var_name))

            # multi_click 格式
            mc = c.get("multi_click")
            if mc:
                if "count" not in mc:
                    errors.append("{} multi_click 缺少 count".format(prefix))
                elif not isinstance(mc["count"], int) or mc["count"] < 1:
                    errors.append("{} multi_click count 无效: {}".format(prefix, mc["count"]))
                texts = mc.get("texts", [])
                if len(texts) != mc.get("count", 0):
                    errors.append("{} multi_click texts 数量({}) != count({})".format(prefix, len(texts), mc["count"]))

        # auto_next 引用（跨章引用合法，检查全库 node_id）
        auto = n.get("auto_next")
        if auto and auto not in all_ids:
            errors.append("{} / {} auto_next '{}' 指向不存在节点".format(fname, nid, auto))

    # 4. text_bridges key 合法性检查
    # 收集所有合法的源→目标跳转关系（choices.next_node、minigame、auto_next）
    valid_sources = {}  # target_node → set of source nodes that can reach it
    for n in nodes:
        choices = n.get("choices", [])
        for c in choices:
            nxt = c.get("next_node")
            if nxt:
                valid_sources.setdefault(nxt, set()).add(n["node_id"])
            mg = c.get("minigame")
            if mg:
                sn = c.get("success_node")
                if sn:
                    valid_sources.setdefault(sn, set()).add(n["node_id"])
                fn = c.get("failure_node")
                if fn:
                    valid_sources.setdefault(fn, set()).add(n["node_id"])
        # auto_next 也是合法前置节点（中间桥节点通过 auto_next 到达目标）
        auto = n.get("auto_next")
        if auto:
            valid_sources.setdefault(auto, set()).add(n["node_id"])

    for n in nodes:
        nid = n.get("node_id")
        bridges = n.get("text_bridges")
        if not bridges:
            continue
        allowed = valid_sources.get(nid, set())
        for key in bridges:
            if key == "*":
                continue
            if key not in allowed:
                errors.append("{} / {} text_bridges key '{}' 不是合法前置节点".format(
                    fname, nid, key))
            if key not in all_ids:
                errors.append("{} / {} text_bridges key '{}' 指向不存在的节点".format(
                    fname, nid, key))

    # 5. mood 值域检查（可选字段，存在时须为合法值）
    VALID_MOODS = {"dread", "tension", "loss", "quiet"}
    for n in nodes:
        mood = n.get("mood")
        if mood is not None and mood not in VALID_MOODS:
            errors.append("{} / {} mood 值非法: '{}'（合法: {}）".format(
                fname, n.get("node_id"), mood, ", ".join(sorted(VALID_MOODS))))

    return errors


def _report_convergence():
    """打印汇聚节点信息——供 ND 同源异构扫描用。不阻断，纯信息。"""
    # 收集所有 chapter JSON 的节点和 choice 关系
    target_sources = {}  # target_node → [(source_node, choice_label), ...]
    chapter_nodes = {}    # node_id → (chapter, title)

    for fname in sorted(os.listdir(DATA_DIR)):
        if not fname.startswith("chapter_") or not fname.endswith(".json"):
            continue
        path = os.path.join(DATA_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            continue
        chapter = data.get("chapter", 0)
        title = data.get("title", "")
        for n in data.get("nodes", []):
            nid = n.get("node_id")
            if nid:
                chapter_nodes[nid] = (chapter, title)
        for n in data.get("nodes", []):
            src_id = n.get("node_id", "?")
            for c in n.get("choices", []):
                tgt = c.get("next_node")
                if tgt:
                    target_sources.setdefault(tgt, []).append(
                        (src_id, c.get("label", "?")))

    # 收集小游戏路径
    for fname in sorted(os.listdir(DATA_DIR)):
        if not fname.startswith("chapter_") or not fname.endswith(".json"):
            continue
        path = os.path.join(DATA_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            continue
        for n in data.get("nodes", []):
            src_id = n.get("node_id", "?")
            for c in n.get("choices", []):
                for key in ("success_node", "failure_node"):
                    tgt = c.get(key)
                    if tgt:
                        target_sources.setdefault(tgt, []).append(
                            (src_id, c.get("label", "?") + " [" + key + "]"))

    # 找出汇聚节点（被 ≥2 条路径指向的节点）
    converged = {t: srcs for t, srcs in target_sources.items() if len(srcs) >= 2}
    if converged:
        print("\n[汇聚节点报告] 以下节点被多条路径指向，ND 须用 GM 逐路扫描状态一致性：")
        for t, srcs in sorted(converged.items()):
            ch = chapter_nodes.get(t, (0, "?"))
            labels = [l[:30] + ("..." if len(l) > 30 else "") for _, l in srcs]
            print("  {} (第{}章) ← {} 条路径: {}".format(t, ch[0], len(srcs), ", ".join(labels)))
    else:
        print("\n[汇聚节点报告] 无汇聚节点")


if __name__ == "__main__":
    ok = validate_all()
    sys.exit(0 if ok else 1)
