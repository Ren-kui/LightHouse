---
name: lighthouse
description: Use ONLY when working on the Lighthouse text adventure game project (灯塔/Lighthouse). Triggers on keywords: 灯塔, Lighthouse, chapter_0*.json, Tkinter, 物品系统, 结局判定, MG1/MG2/MG3/MG4/MG5, minigame, ItemManager, story_engine, 配电连线, 太阳能, 平台平衡, 海鸟, 黑暗收缩.
---

# Lighthouse 游戏开发规范（摘要）

> **当前状态**：M0~M6 ✅。M7 🔄 85%。详见 `docs/progress.md`。
>
> 本文档为项目规则的**精简摘要**。冲突时以 `docs/` 下各 MD 文件原文为准。动态内容（进度/Bug/决策）不要在此修改——去对应 MD 改。

---

## 1. 全局技术约束

| # | 约束 |
|---|------|
| 1 | Python 标准库 only，不引入第三方库 |
| 2 | Tkinter GUI，单线程 |
| 3 | 中文注释（D013） |
| 4 | JSON 数据驱动（剧情/日记/物品/音效配置全部 JSON） |

---

## 2. 角色总表

| 角色 | 核心职责 | 对标文档 |
|------|---------|---------|
| **PM** | 文档同步第一；优先级 Bug→优化→GD→UI→ND；不放行未经 QA 验收的交付 | `work_standards.md` W001-W005 |
| **GD** | 8 结局变量+物品判定；维护 `data/items.json` 物品定义+结局关联；维护 `data/markup_registry.json` | `design.md` §2.3/§2.5/§2.7 |
| **ND** | 白描>渲染；`[key]`≤3处/节点；物品描述文案写入 items.json desc 字段；JSON 文本值禁止 ASCII `"` | `text_markup_spec.md` / `bridges.md` / `nd_selfcheck.md` |
| **FD** | 纯执行者，不自行新增功能；Bug 优先；中文注释；交付前自检（双击bat物理验证） | `story_engine.py` / `main_window.py` / `item_manager.py` / `fd_selfcheck.md` |
| **UI** | Undertale 哲学；W002-4 面板文本不溢出；`#000000`黑底 `#e8e8e8`白字 `#cc0000`/`#cc6600`唯一强调色 | `design.md` §1.2/§1.3 |
| **QA** | 逻辑层 AI 覆盖+物理层老板覆盖；每份声明须附实际命令输出 | `test_report.md` / `bug_list.md` |
| **SD** | 极简低频；音效全局暂停中 | `sound_spec.md` |

### 会话规则

1. 专职应答——向任一角色提问，必须由该角色本人回答
2. 声明确认制——FD/ND/SD/QA 完成交付必须输出 W005 声明
3. 角色隔离——PM 不可自行写业务逻辑代码；跨角色执行须声明 `[角色名] 开始工作`

---

## 3. 核心设计参数速查

### 变量（`state_manager.py`）

| 变量 | 显隐 | 范围 | 初始 |
|------|:---:|------|------|
| curiosity | 显 | 0~10 | 0 |
| sanity | 显 | 0~10 | 10 |
| trust | 显 | 0~10 | 4 |
| survival_will | 隐 | 0~10 | 6 |
| loyalty | 隐 | 0~5 | 3 |

### 结局判定（`story_engine.py:check_ending()`）

| 优 | ID | 结局 | 变量条件 | 物品条件 |
|:--:|----|------|---------|---------|
| 1 | G | 荒诞 | — | tin_soldier + music_box + warm_marble |
| 2 | death | 死亡 | MG4B/MG5 失败 | — |
| 3 | F | 被背叛 | c≥7,s≤3,t≤3,l≤2 | 无 |
| 4 | A | 疯狂 | c≥7,s≤3,(t≥5或l≥3) | 无 |
| 5 | E | 逃离 | sw≥8,s≤4,t≤4(ch05) | 无 |
| 6 | B | 一起逃离 | c≥6,s≥6,t≥7,l≥4 | pen |
| 7 | D | 被杀 | c≤3,s≥6,t≤3,l≤2 | zhang_textbook |
| 8 | C | 平安离开 | c≤3,s≥6 | 无 |

### 物品（`data/items.json` + `src/item_manager.py`）

| ID | 名称 | 效果 | 获取 |
|----|------|------|------|
| key | 父亲的钥匙 | survival_will+2 | 开局 |
| tin_soldier | 不锈的锡兵 | — | ch02 墙缝 |
| music_box | 自鸣八音盒 | survival_will-1 | ch03 三选一 |
| warm_marble | 暖弹珠 | — | ch04 梦境醒·选项1 |
| evil_wood_carving | 邪恶木雕 | sanity-2 | ch04 梦境醒·选项2（互斥） |
| pen | 纯黑钢笔 | — | 闲逛全清 |
| zhang_textbook | 张望潮物理课本 | — | ch03 夹层(loyalty≤2) |

---

## 4. 工作准则（W 编号速查）

详见 `docs/work_standards.md` 原文。

| 编号 | 核心规则 |
|------|---------|
| W001 | 设计文档权威——变更先开会→老板确认→更新 MD→再写代码 |
| W002 | Undertale 交互哲学 + W002-4 面板不溢出 + W002-5 双路径渲染一致 |
| W003 | QA 验收前置 + 留痕纪律 |
| W004 | FD 执行优先级 Bug→优化→GD→UI→ND |
| W005 | 声明确认制——无声明=工作从未发生 |
| W006 | 异步防卫——`after()` cancel旧→设状态→schedule新 |
| W007 | 小游戏生命周期——`_complete` 用 `after` 延迟回调 |
| W008 | Tkinter布局防卫——尺寸<50阈值 + 禁止`place(in_=pack_widget)` |
| W009 | 分支对称性——同一状态判断多路径必须一致 |
| W010 | 状态隔离——JSON写入即验证 + `winfo_exists`守卫 + `after_cancel`判真 |
| W011 | 物品效果穿透——carry_effects必须参与`check_ending`有效值计算 |

---

## 5. 文本标记速查

详见 `docs/text_markup_spec.md`。

| 标记 | 语法 | 效果 |
|------|------|------|
| `[shake]...[/shake]` | 抖动文字 | #cc0000 红，水平±3px，5秒 |
| `[pause N]` | 停顿 N 秒 | 块间额外等待 |
| `[key]...[/key]` | 关键句 | #ccaa44 淡黄，≤3处/节点 |
| ‡...‡（low阈值） | 日记低阈值 | #cc0000 红+下划线 |
| †...†（high阈值） | 日记高阈值 | #008800 绿+下划线 |

---

## 6. 文档索引

| 需要时去读 | 内容 |
|-----------|------|
| `docs/progress.md` | 里程碑进度、M7 任务状态 |
| `docs/design.md` | 完整游戏设计（卷1-4，504行） |
| `docs/decisions.md` | D001~D048 决策记录 |
| `docs/bug_list.md` | B001~B035 Bug 清单 |
| `docs/fd_selfcheck.md` | FD 交付自检矩阵 |
| `docs/nd_selfcheck.md` | ND 交付自检流程 |
| `docs/bridges.md` | text_bridges 写作原则 |
| `docs/text_markup_spec.md` | 标记规范全文 |
| `tests/run_all.py` | 全量测试入口（138/139 PASS） |
