# 测试报告

> 维护者：QA | 最后更新：2026-05-11

---

## QA 批次 · SD 音效模块基础验收（SD-01~04）

### 测试项

| # | 检查项 | 来源 | 结果 | 备注 |
|---|--------|------|------|------|
| SD-01a | SoundManager 实例化正常 | 自动化 | ✅ PASS | 无报错 |
| SD-01b | 注册表含全部 5 音效 | 自动化 | ✅ PASS | hum_low/heartbeat/metal_creak/water_drone/silence_fade |
| SD-01c | 每个音效含完整字段 | 自动化 | ✅ PASS | freq/duration/waveform/loop 四字段齐全 |
| SD-01d | data/sounds/ 目录自动创建 | 自动化 | ✅ PASS | os.makedirs(exist_ok=True) |
| SD-02a | play(name) 可调用 | 自动化 | ✅ PASS | M4 空壳，调用不报错 |
| SD-02b | stop(name) 可调用 | 自动化 | ✅ PASS | — |
| SD-02c | stop_all() 可调用 | 自动化 | ✅ PASS | — |
| SD-02d | set_volume(f) 可调用 | 自动化 | ✅ PASS | — |
| SD-02e | mute()/unmute() 可调用 | 自动化 | ✅ PASS | — |
| SD-02f | to_dict() 返回 dict(3键) | 自动化 | ✅ PASS | active/volume/muted |
| SD-02g | from_dict(dict) 恢复状态 | 自动化 | ✅ PASS | volume/muted 正确恢复 |
| SD-02h | volume / is_muted 属性可读 | 自动化 | ✅ PASS | — |
| SD-03a | play(不存在音效) 抛 ValueError | 自动化 | ✅ PASS | — |
| SD-03b | set_volume(-0.1) 抛 ValueError | 自动化 | ✅ PASS | — |
| SD-03c | set_volume(1.5) 抛 ValueError | 自动化 | ✅ PASS | — |
| SD-03d | set_volume(0.0) 边界通过 | 自动化 | ✅ PASS | — |
| SD-03e | set_volume(1.0) 边界通过 | 自动化 | ✅ PASS | — |
| SD-03f | mute()/unmute() 状态翻转 | 自动化 | ✅ PASS | False→True→False |
| SD-04a | __init__ < 100ms | 自动化 | ✅ PASS | M4 空壳无合成延迟 |
| SD-04b | play() 10次 < 50ms | 自动化 | ✅ PASS | 不阻塞主线程 |
| SD-04c | stop_all() < 10ms | 自动化 | ✅ PASS | 立即返回 |

### FD 交底（W003）

| 功能 | 行为说明 |
|------|----------|
| SoundManager() | 创建实例即注册 5 音效规格、创建 data/sounds/ 缓存目录、默认音量 0.8、muted=False |
| play(name) | M4 阶段检查名字是否在 REGISTRY 中（不在则 ValueError），不实际发声 |
| mute/unmute | 翻转 _muted 标志，to_dict 正确序列化 |

### 已知限制

| 项 | 说明 |
|----|------|
| 无实际音频输出 | M4 空壳，5 音效的 PCM 合成为 M5 任务。当前 play/stop/stop_all 方法体为 pass |
| Game 未调用 SoundManager | B007 已知，延至 M5 实现时接入 story_engine 自动触发逻辑 |

> QA 放行：SD-01~04 共 21 项全部通过。SoundManager API 骨架完整、边界保护到位、不阻塞主线程。
> 
> QA 放行人：QA | 放行时间：2026-05-11

---

## QA 批次 · 存档/读档链路测试 (M4)

### 测试覆盖

| # | 测试项 | 来源 | 结果 | 备注 |
|---|--------|------|------|------|
| SA-01 | 全字段往返（含 sound_state） | 新增 | ✅ PASS | 变量/历史/标志/音效状态 全恢复 |
| SA-02 | sound_state 多取值往返 | 新增 | ✅ PASS | 静音/无活跃/空字典 三种场景 |
| SA-03 | 存档文件包含全部必须键 | 新增 | ✅ PASS | 8 键齐全 + 5 变量子键 |
| SA-04 | 多轮 存档→修改→存→读 循环 | 新增 | ✅ PASS | 变量累积正确 |
| SA-05 | 多个存档位互不干扰 | 新增 | ✅ PASS | 3 手动位 + 1 自动位 |
| SA-06 | get_info 返回完整字段 | 新增 | ✅ PASS | exists/save_time/day/chapter |
| SA-07 | 自动存档位 info 正确 | 新增 | ✅ PASS | auto 槽位正常 |
| SA-08 | 不存在的槽位返回 None | 新增 | ✅ PASS | 边界安全 |
| SA-09 | 覆写存档保持数据格式 | 新增 | ✅ PASS | 旧 flags 被替换 |
| SA-10 | sound_state=None 填入空字典 | 新增 | ✅ PASS | null-safe |
| SA-11 | SoundManager to_dict/from_dict | 新增 | ✅ PASS | 序列化往返 + 空值保持 |
| QA-08 | 存档→读档循环（单元测试） | 存量 | ✅ PASS | 8 项单元全部通过 |
| QA-09 | 未完待工标记 | 存量 | ✅ PASS | auto_next→未加载→reached_end |

### FD 交底（W003）

| 功能 | 行为说明 |
|------|----------|
| 手动存档 | 状态栏点击"存档"→弹出浮窗→选槽位→存当前全部状态（变量/节点/历史/标志/音效）→状态栏 flash 反馈 |
| 手动读档 | 状态栏点击"读档"→弹出浮窗→选有数据的槽位→恢复全部状态→跳转对应节点 |
| 自动存档 | 每次 cmd_choice / cmd_auto_advance / 小游戏结束后自动存 auto 位，不提示 |
| 音效状态 | 存档含 sound_state 字段（active/volume/muted），读档时恢复，旧格式存档无此字段时保持默认 |
| 覆盖存档 | 同名槽位再次保存完全覆盖旧数据，不会残留旧字段 |

### 已知限制

| 项 | 说明 |
|----|------|
| ch03→ch04 断链 | chapter_03.json `ch03_d6_evening` auto_next 指向 ch04_start，第4章未写完导致 reached_end，符合设计 |
| 跨章节存档 | 存档包含 `chapter` 字段，读档时自动加载对应章节 JSON，ch04+ 暂不可用 |

### 修复记录

| 问题 | 修复 |
|------|------|
| B005 存档不包含 sound_state | save_manager.save 新增 sound_state 参数，_do_save/_auto_save/_do_load/cmd_continue 全链路接入 |
| B002 [pause N] 未解析 | show_chunked_text 新增 pause 标记提取 + _start_pause 定时自动翻页 |
| B003 multi_click 未实现 | cmd_choice 新增连点计数，update_choice_label 逐次换字 |

> QA 放行：存档/读档 11 项集成测试 + 8 项单元测试全部通过。存档数据格式完整，全字段往返正确，sound_state 序列化正常。
> 
> QA 放行人：QA | 放行时间：2026-05-11

---

## QA 放行

> 全部 12 项检查通过。菜单可见、点击逻辑正确、状态机正常、第 1 章文本加载成功。
> 
> QA 放行人：QA | 放行时间：2026-05-09

---

## QA 批次 · OPT-01~05,08 重要优化

| # | 检查项 | 结果 |
|---|--------|------|
| QA-OPT-01 | 标题浮现 | ✅ |
| QA-OPT-02 | 菜单3项 | ✅ |
| QA-OPT-03 | 新游戏菜单清除 | ✅ |
| QA-OPT-04 | 选项变灰 | ✅ |
| QA-OPT-05 | 选项区固定180px | ✅ |
| QA-OPT-06 | FSM状态正常 | ✅ |
| QA-OPT-07 | 文本分块+选项 | ✅ |
| QA-OPT-08 | 节点跳转正常 | ✅ |
| QA-OPT-09 | 天数含章节名(抵达) | ✅ |

> 全部通过。QA放行：2026-05-09

---

## QA 批次 · OPT 重要优化逐项验收

| # | 优化 | 检查项 | 结果 |
|---|------|--------|------|
| 1 | OPT-01 | 引言渐现 tag 注册 + root 跳过绑定 | ✅ |
| 2 | OPT-02 | 标题浮现 + 菜单 3 项 + 红色(#cc0000) | ✅ |
| 3 | OPT-03 | 新游戏后菜单清除 | ✅ |
| 4 | OPT-04 | 选择后选项变灰(#555555) | ✅ |
| 5 | OPT-05 | 选项区固定高度 180px | ✅ |
| 6 | OPT-08 | 天数含章节名(抵达/初现/...) | ✅ |

> QA 放行时间：2026-05-09 · 全部 6 项重要优化通过

---

## QA 批次 · GM 调试栏功能验收

### 测试项

| # | 检查项 | 结果 | 备注 |
|---|--------|------|------|
| GM-01 | 启动参数 `--gm` 开启 GM 模式 | ✅ PASS | 不加参数时 Ctrl+Shift+G 无响应 |
| GM-02 | Ctrl+Shift+G 呼出 GM 面板 | ✅ PASS | 右侧滑入 35%，遮罩覆盖主界面 |
| GM-03 | 遮罩点击关闭面板 | ✅ PASS | 点击黑色遮罩区域面板收起 |
| GM-04 | 加载第1章 — 7 节点全部显示 | ✅ PASS | ch01_start → ch01_evening |
| GM-05 | 加载第2章 — 13 节点追加显示 | ✅ PASS | ch02_start → ch02_d3_evening，累积 20 节点 |
| GM-06 | 加载第3章 — 15 节点追加显示 | ✅ PASS | ch03_start → ch03_d6_evening，累积 35 节点 |
| GM-07 | 节点按 JSON 原始顺序排列 | ✅ PASS | 首节点 ch02_start，末节点 ch02_d3_evening |
| GM-08 | 当前节点橙色高亮 | ✅ PASS | #cc6600 标识 |
| GM-09 | 点击节点直跳 — gm_jump 不存档 | ✅ PASS | goto_node 后不调用 _auto_save |
| GM-10 | 变量 +/- 按钮调节 | ✅ PASS | 增量 change()，边界保护生效 |
| GM-11 | 4 组预设组合应用 | ✅ PASS | A/B/C/D 预设全部就绪 |
| GM-12 | 空节点提示 "请先开始游戏或加载章节" | ✅ PASS | 标题界面下 GM 面板不崩溃 |
| GM-13 | 已加载章节绿色 ✓ 标记 | ✅ PASS | 加载后按钮变色 |
| GM-14 | 46 项单元测试不受影响 | ✅ PASS | 46/46 通过 |

### 已知限制

| 项 | 说明 |
|----|------|
| libpng 警告 | Tkinter 内置 PNG 库已知无害警告，不影响功能 |
| GM 面板小游戏期间 | 小游戏中 Ctrl+Shift+G 可呼出但节点跳转可能与小游戏状态冲突——建议小游戏中不使用 GM |

---

> QA 放行：GM 调试栏 14/14 项检查通过。放行人：QA | 放行时间：2026-05-10
