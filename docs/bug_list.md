# Bug 清单

> 维护者：QA（实际执行：老板/FD） | 最后更新：2026-05-15
>
> FD 修复后不得自行标记"已修复"——须老板物理验证后由 QA 关闭。

---

## 待修复

| — | — | — | — | — | — |
|
|----|------|--------|--------|--------|------|
| — | — | — | — | — | — |

## 已修复

| ID | 描述 | 优先级 | 发现人 | 负责人 | 日期 | 修复日期 |
|---|---|---|---|---|---|---|---|
| B001 | OPT-04 选项蒙灰未完成：选择后选项颜色未变灰，点击仍有动画响应 | P1 | 老板 | FD | 2026-05-09 | 2026-05-09 |
| B002 | `[pause N]` 标记未实现——chapter_03.json 5处暂停标记显示为原样文字 | P0 | PM | FD | 2026-05-11 | 2026-05-11 |
| B003 | `multi_click` 连点机制未实现——ch03 连点选项单次点击即执行 | P0 | PM | FD | 2026-05-11 | 2026-05-11 |
| B004 | `[sound]` 标记解析骨架——show_chunked_text 新增音效事件提取 | P1 | PM | FD | 2026-05-11 | 2026-05-11 |
| B005 | 存档不包含 sound_state 字段——save/load/auto_save/continue 全链路接入 | P1 | PM | FD | 2026-05-11 | 2026-05-11 |
| B006 | 第4章缺失时给出友好提示——显示已完成章节名+自动存档提醒 | P2 | PM | FD | 2026-05-11 | 2026-05-11 |
| B008 | 引言结束后"灯塔"标题不显示——`_show_title_and_menu` 在 text_area DISABLED 态执行 delete/insert 静默失败 | P0 | QA | FD | 2026-05-11 | 2026-05-11 |
| B009 | 存档/读档按钮点击无效——`_build_status_bar` lambda 在 `__init__` 期间以默认参数捕获回调为 `None`，后续赋值无效 | P0 | 老板 | FD | 2026-05-11 | 2026-05-11 |
| B010 | 备忘录面板打开内容为空——`update_panel_*` 面板关闭时丢弃数据，无缓存机制 | P0 | 老板 | FD | 2026-05-11 | 2026-05-11 |
| B011 | Tab 键无法调出面板——`bind_all` 在事件链最末层被 Text 类绑定拦截，后改为 widget 级 + `or "break"` 修复 | P1 | QA | FD | 2026-05-11 | 2026-05-11 |
| B012 | Tab 面板闪现后消失——lambda 返回元组 `(None, "break")` 而非字符串 `"break"`，事件未中断 | P0 | 老板 | FD | 2026-05-11 | 2026-05-11 |
| B013 | MG2 光点点击崩溃——`_current_dot` 5 元组 `_on_click` 按 4 解包 | P0 | 老板 | FD | 2026-05-11 | 2026-05-11 |
| B014 | 暂停计时器穿透面板——面板打开期间 `[pause N]` 倒计时照旧推进文本 | P1 | QA | FD | 2026-05-11 | 2026-05-11 |
| B015 | `cmd_choice` 中 `make_choice()` 被调用两次——重复代码块导致 effects 双加、history 双写、节点跳转错乱 | P0 | QA | FD | 2026-05-11 | 2026-05-11 |
| B016 | `show_chunked_text` 不取消旧计时器——快速节点切换时旧 `_typewriter_job`/`_pause_job` 在新文本上执行 | P0 | QA | FD | 2026-05-11 | 2026-05-11 |
| B017 | shake 独块显示 `[SHAKE_N]` 占位原文——纯 shake 无剩余文字时 fall through 到通用打字分支 | P1 | QA | FD | 2026-05-11 | 2026-05-11 |
| B018 | `_display_node` 直接读 `node["text"]` 绕过 `get_current_text()` 中的 text_bridges 拼接，导致全部桥段静默失效 | P0 | 老板 | FD | 2026-05-11 | 2026-05-11 |
| B019 | MG2 太阳能反应光点叠层——`_hit_dot` 与 `_miss_dot` 竞态下 `_spawn_flash` 重复调用，光点成对出现并位置叠加。在 `_clear_dot_and_next` 中 cancel 旧 `_spawn_timer` 修复 | P1 | 老板 | FD | 2026-05-12 | 2026-05-12 |
| B020 | GM 面板关闭后滚轮 TclError——`bind_all("<MouseWheel>")` 残留绑定访问已销毁 canvas。`_hide_gm_panel` 加 `unbind_all` + lambda 加 `winfo_exists` 守卫 | P1 | 老板 | FD | 2026-05-12 | 2026-05-12 |
| B021 | B2 MG1 `_clear_all_highlights` 残留拆包死代码——`_, color = self._relays[0]` 对 4 元组拆 2 值导致 ValueError。删除残留空循环修复 | P0 | FD | FD | 2026-05-14 | 2026-05-14 |
| B022 | B5 MG4B5 `_draw_shrink` 颜色溢出——`_shrink` 超出 1.0 时 `int(100+shrink*155)` > 255 产生无效 hex `#1000000`。全颜色计算加 `min(1.0, shrink)` 钳制修复 | P0 | FD | FD | 2026-05-14 | 2026-05-14 |
| B023 | B5 MG4B5 暗红收缩提前死亡——`_draw_shrink` 用 `min(area_w,area_h)` 算收缩值导致 X/Y 不同步收缩到极限前就判定 `_shrink≥1` 死亡。改为独立 `mx`/`my` 分别收缩 | P0 | FD | FD | 2026-05-14 | 2026-05-14 |
| B024 | B3 MG2 测试失败——旧 API `_hit_dot`/`_miss_dot`/`_clear_dot_and_next`/`_current_dot` 在 B3 重写中删除，`test_interaction.py` 和 `test_qa_logic.py` 引用旧方法导致 3/97 FAIL。适配新 API 修复 | P1 | FD | FD | 2026-05-14 | 2026-05-14 |
| B025 | diary.json JSON 解析失败——ND 文本中混入 ASCII `"`（如 `"不太对"`）破坏 JSON 结构，导致 `_load_diary` 静默返回空字典，日记功能完全失效。重写文件消除所有内层引号修复 | P0 | FD | FD | 2026-05-14 | 2026-05-14 |
| B026 | `_diary_cache` AttributeError——`_diary_cache` 等属性在 `_build_panel_content()`（面板打开时）才初始化，但 `update_panel_notes` 在节点切换时就调用，面板未打开时属性不存在 → crash。属性移至 `__init__` 初始化修复 | P0 | FD | FD | 2026-05-14 | 2026-05-14 |
| B027 | `_panl_notes_text` TclError——`_render_diary` 在面板关闭时调用，widget 已被 `destroy()` 销毁，访问报 `invalid command name`。加 `winfo_exists()` + `try/except TclError` 守卫修复 | P0 | FD | FD | 2026-05-14 | 2026-05-14 |
| B028 | `after_cancel(0)` ValueError——`flash_update_indicator` 中用 `getattr(self, '_flash_job', 0)` 取默认值，`_flash_job` 不存在时返回 `0`，传 `after_cancel(0)` 报非法 ID。改为 `hasattr` 判真才 cancel 修复 | P0 | FD | FD | 2026-05-14 | 2026-05-14 |
| B029 | chapter_02.json JSON 解析失败——`ch02_free_mg1_done` 节点文本内嵌 ASCII `"`（`"没有任务"`）破坏 JSON 结构，导致第 2 章加载失败。改为中文引号修复 | P0 | FD | FD | 2026-05-15 | 2026-05-15 |
| B030 | 物品面板悬停文字溢出——`update_panel_items` 中 `Label` 未设 `wraplength`，物品描述（最长 57 字）超出面板宽度被裁切。加动态 `wraplength` + `justify=LEFT` + `fill=tk.X` 修复 | P1 | FD | FD | 2026-05-15 | 2026-05-15 |
| B031 | 日记重点文字全红——diary.json 中 low/high 阈值共用一个 `‡` 标记，`_get_diary_text()` 无法区分，改 marked 标签颜色后高低阈值全变红。high 文本改用 `†` 标记 + 渲染端分 `marked`(红)/`marked_high`(绿) 双 tag 修复 | P1 | 老板 | FD | 2026-05-15 | 2026-05-15 |
| B032 | `[key]` 标记文字快速点击后消失——两重原因：① `_skip_typing` 正则用 raw string `r'\x01'` 不解析控制符，匹配的字面字符串；② `re.sub` 回调中用 `tk.END` 插入 key 文本，所有 key 文本挤在最前面、后追加普通文本，顺序全乱。改用 `re.split` + 交替插入修复 | P1 | FD | FD | 2026-05-16 | 2026-05-16 |
| B033 | 结局画面无法返回标题界面——`show_ending_screen` 后 `_chunks` 保留旧数据，`_on_text_advance` 发现 `_chunks` 非空但 `_chunk_idx` 已达末尾，直接 return 不触发回调。加 `_ending_screen` 标志+清空 `_chunks` 修复 | P0 | 老板 | FD | 2026-05-15 | 2026-05-15 |
| B034 | 黑暗小游戏死亡结局未走结局画面——`ch04_darkness_death` 和 `ch05_mg5_death` 的 `auto_next` 为 null，未路由到 `ch06_ending_death`（`is_ending_chain`），导致死亡后卡在黑屏。两处 `auto_next` 改为 `"ch06_ending_death"` 修复 | P0 | 老板 | FD | 2026-05-15 | 2026-05-15 |
| B035 | 点击剧情文本偶尔跳行——正常翻页路径中 `_show_prompt` 留 `\n\n` → `_remove_prompt` 仅删提示行（`end-1c`）→ `_typewrite_current_chunk` 再加 `\n\n`，累计双倍行距；快进路径仅单倍行距，两条路径不一致。`_remove_prompt` 改为 `end-2l` 同时删除前导空行修复 | P1 | FD | FD | 2026-05-16 | 2026-05-16 |

|----|------|--------|--------|--------|------|----------|
| — | — | — | — | — | — | — |

---

> **优先级**：P0=阻塞游戏 / P1=影响体验 / P2=小问题




