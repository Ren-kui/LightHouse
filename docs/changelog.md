# 代码修改日志

> 维护者：FD | 记录每次代码文件的增删改
> 最后更新：2026-05-12

| 日期 | 文件 | 改动类型 | 描述 |
|------|------|----------|------|
| 2026-05-08 | 全部文档 | 新建 | 项目初始化，创建记忆文档系统 |
| 2026-05-08 | docs/decisions.md, docs/design.md, docs/progress.md | 更新 | 同步黑暗收缩死亡场景设计（D015/D016），追加设计文档第十一章 |
| 2026-05-08 | src/state_manager.py | 新建 | 变量管理器，含5变量显隐分离、边界保护、条件判定、文字描述转换 |
| 2026-05-08 | src/save_manager.py | 新建 | 存档系统，3手动+1自动，JSON读写 |
| 2026-05-08 | src/story_engine.py | 新建 | 剧情引擎，JSON加载、节点跳转、条件过滤、变量联动 |
| 2026-05-08 | src/main_window.py | 新建 | Tkinter主窗口，布局/配色/文本区/选项按钮/状态栏 |
| 2026-05-08 | src/status_panel.py | 新建 | Tab浮层面板，笔记风格状态+物品列表+悬停简述 |
| 2026-05-08 | src/darkness_overlay.py | 新建 | V1黑暗收缩覆盖层，矩形边框100ms帧动画 |
| 2026-05-08 | src/effects.py | 新建 | 红色抖动文字、逐字打印、多次点击按钮 |
| 2026-05-08 | src/minigame_base.py | 新建 | 小游戏抽象基类 |
| 2026-05-08 | src/main.py | 新建 | 主入口，Game类协调全部子系统 |
| 2026-05-08 | data/chapter_01.json | 新建 | 第1章可达剧情，8节点含4选择支+双分支文本 |
| 2026-05-08 | src/main_window.py | 重写 | Undertale 风格翻新：纯黑底、微软雅黑粗体、逐字分块打印、▶箭头选项、空格/回车翻页、标题界面 |
| 2026-05-08 | src/main.py | 重写 | 接入标题界面流程（引语→标题→菜单→新游戏/继续）；文本完成回调驱动选项显示 |
| 2026-05-08 | src/status_panel.py | 重写 | 改为右侧滑入遮罩面板（非独立窗口），嵌入主窗口内 |
| 2026-05-08 | src/main_window.py | 修复 | 标题界面卡死：增加 _in_title_screen 标志阻断文本区点击；_is_typewriting 状态管理修正；_on_text_advance 标题期屏蔽；标题完成后正确清状态 |
| 2026-05-08 | src/main_window.py | 简化 | 标题界面改为整体渲染+单after回调，消除mainloop启动前after链时序问题；text_area状态管理修正 |
| 2026-05-08 | docs/work_rules.md | 新增 | 工作准则文档：为人类设计、QA验收制、人类可读反馈、文档同步 |
| 2026-05-08 | src/main_window.py | 修复 | 标题界面改为回车键触发菜单（消除after时序bug）；菜单居中显示；修复逐字跳过逻辑；提示符可见性优化 |
| 2026-05-08 | docs/work_standards.md | 新建 | 工作准则（W001设计文档权威制 / W002 Undertale交互逻辑 / W003 QA验收前置） |
| 2026-05-08 | docs/design.md | 重构 | 按角色栏目重组为5卷：交互逻辑(UI)/玩法(GD)/剧情(ND)/程序(FD)/任务清单；精简冗余内容 |
| 2026-05-08 | docs/progress.md | 重构 | 改为4里程碑结构，每里程碑明确交付物+责任到人 |
| 2026-05-08 | — | 决议 | D025全量重建游戏客户端（全删旧代码，按界面流重建，7迭代） |
| 2026-05-08 | docs/decisions.md / design.md / progress.md | 同步 | 重建决议写入文档：D025/D026/D027 + 第四卷模块状态重置 + progress看板重制 |
| 2026-05-09 | src/*.py | 删除 | 清理全部 9 个旧版模块 |
| 2026-05-09 | src/main.py | 新建 | 迭代1最小窗口验证：纯黑窗口+灯塔标题，验证字体配色尺寸通过 |
| 2026-05-09 | src/main_window.py | 新建 | 纯 UI 层：5界面骨架+标题菜单（Undertale风格居中箭头+悬停变色） |
| 2026-05-09 | src/main.py | 新建 | Game状态机+FSM枚举+子系统接入；title/new_game/continue命令处理 |
| 2026-05-09 | src/state_manager.py src/save_manager.py src/story_engine.py | 新建 | 基础引擎三层（变量/存档/剧情），36~100行，接口干净 |
| 2026-05-09 | src/main_window.py | 修复 | 菜单改为Button实现（Label bind不可靠）；修正show_title_screen直接tag分段渲染 |
| 2026-05-09 | src/main.py | 修复 | os.chdir项目根目录修正story_engine路径；_show_error改用show_text_full |
| 2026-05-09 | src/main_window.py | 修复 | _show_menu 回退至 Label+Frame 方案：文字色 #e8e8e8 清晰可见；整行 Frame 绑定点击；悬停变色 #cc6600；弃用不可靠的 tk.Button |
| 2026-05-09 | docs/work_standards.md | 新增 | W004 程序执行优先级；准则层级 W001 > W002 > W003=W004 |
| 2026-05-09 | docs/work_standards.md | 新增 | W002 追加"UI验收前置"条款（UI人类视角验证→QA验证） |
| 2026-05-09 | src/main_window.py | 修复 | 布局重排：choice_frame 固定 side=BOTTOM before=status_bar，菜单锁定窗口底部；text_frame expand 填空余空间 |
| 2026-05-09 | — | 验收 | 老板验证通过：菜单可见可点击，标题→新游戏→第1章全流程正常 |
| 2026-05-09 | src/main_window.py | 重写 | show_text_full → show_chunked_text：按\n\n分块逐字打印(30ms/字)+空格翻页+▼提示符+溢出保护 |
| 2026-05-09 | src/main.py | 更新 | cmd_choice实现选择跳转+自动存档；_on_text_done文本完成后显示选项；完整游戏循环 |
| 2026-05-09 | docs/optimizations.md | 新建 | 优化清单：6项重要(OPT-01~05,08)+4项轻度(OPT-06~07,09~10) |
| 2026-05-09 | docs/work_standards.md | 更新 | W004 需求优先级扩展：Bug→重要优化→GD→UI→ND→轻度优化 |
| 2026-05-09 | src/main_window.py | 优化 | OPT-01/02 引言渐现(2s)→停留(5s,点击跳过)→渐隐→标题+菜单浮现 |
| 2026-05-09 | src/main_window.py + main.py | 优化 | OPT-03 新游戏清除菜单 / OPT-04 选择后变灰 / OPT-05 选项区固定180px / OPT-08 天数加章节名 |
| 2026-05-09 | src/main_window.py | 修复 | 引言点击跳过无效(text_area DISABLED不接收事件)→改为root绑定；标题期_un_text_advance不拦截事件 |
| 2026-05-09 | src/main_window.py | 优化 | 引言渐现目标色 #666666→#aaaaaa 更白亮 |
| 2026-05-09 | src/main_window.py | 修复 | 引言点击跳过改为全程生效(渐现+停留)；title_click_binding 统一绑定到root |
| 2026-05-09 | docs/work_standards.md | 更新 | W003 新增：QA全程介入、Bug清单(bug_list.md)、优化督促+打勾 |
| 2026-05-09 | docs/bug_list.md | 新建 | Bug清单表格(P0/P1/P2)，QA维护 |
| 2026-05-09 | docs/optimizations.md | 移交 | 维护人 PM→QA |
| 2026-05-09 | src/main_window.py | 修复 | B001 OPT-04 选项蒙灰不完整：gray_choices 增加解绑Enter/Leave/Button-1+清空cursor |
| 2026-05-09 | src/main_window.py | 修复 | B002 标题多重弹出：_animate_fade存储after ID供取消；_title_skip取消渐现链+hold计时器；_show_title_and_menu防重复调用 |
| 2026-05-09 | — | 验收 | 老板验证通过：B002 标题界面不再多重弹出 |
| 2026-05-09 | docs/text_markup_spec.md | 新建 | 4F 文本标记规范v1：分块/shake/pause/multi_click/逃避对白 |
| 2026-05-09 | data/diary_fragments.json | 新建 | 4C 日记残页4段原文(约900字) |
| 2026-05-09 | src/main_window.py + main.py | 新建 | 4A 存档读档浮窗(复用_show_menu)+ 4B 状态面板(Tab滑入)+ 4G shake标记解析集成 |
| 2026-05-09 | — | 会话 | 里程碑4进度60%：4F标记规范+4C日记残页+4A存档浮窗+4B状态面板+4G shake解析；剩余4D/4E第2-3章JSON |
| 2026-05-10 | data/chapter_02.json | 新建 | 4D 第2章JSON：13节点，D2设备维护(配电/太阳能，含逃避选项)+D3初现低语(shake标记)·水下轮廓(双分支结局) |
| 2026-05-10 | data/chapter_03.json | 新建 | 4E 第3章JSON：15节点，D4平台高空(逃避选项)+D5地下室探索(日记残页·多击破墙·夹层文字)+D6遗留物发现(情绪高潮·双关系选项) |
| 2026-05-10 | src/main_window.py | 优化 | 状态面板增加"今日笔记"摘要区 + 面板打开时暂停文本推进(含逐字打印)+ 存档/读档完成后状态栏反馈提示 |
| 2026-05-10 | src/main.py | 优化 | _refresh_panel增加每日笔记生成 + _do_save/_do_load增加flash_save_status反馈 |
| 2026-05-10 | docs/progress.md | 更新 | 里程碑4：60%→80%，补充4D/4E/笔记/暂停/反馈任务项 |
| 2026-05-10 | — | 会话 | 里程碑4进度80%：今日笔记+面板暂停文本+存档反馈完成；剩余QA测试(20%)。
| 2026-05-10 | docs/decisions.md | 更新 | D029: 新增SD音效设计师角色，7人编制，纯代码合成音频，M4空壳→M5落地→M6调优 |
| 2026-05-10 | docs/design.md | 更新 | 新增4.5音效模块(sound_manager.py API/注册表/静默规则/自动化触发/存档格式)；第五卷增加SD角色任务清单+FD-12 |
| 2026-05-10 | docs/progress.md | 更新 | 里程碑4追加音效基础架构3项任务(空壳API/规范文档/QA验收)，SD/FD/QA分工 |
| 2026-05-10 | src/sound_manager.py | 新建 | 音效管理器空壳：REGISTRY 5音效注册、play/stop/stop_all/set_volume/mute/unmute API、to_dict/from_dict存档序列化、_generate_tone占位(预生成缓存) |
| 2026-05-10 | docs/sound_spec.md | 新建 | 音效设计规范v1：设计哲学/5音效完整规格/静默规则4条/[sound]标记规范/生命周期规则/ND标记原则/自动化触发逻辑/存档格式/技术约束 |
| 2026-05-10 | src/main.py | 更新 | FD-12: Game.__init__ 挂载 SoundManager 实例（M4 空壳，不调用任何方法）；新增 import |
| 2026-05-10 | data/sounds/ | 新建 | 音效缓存目录占位，SoundManager 运行时自动生成 .wav 到此 |
| 2026-05-10 | tests/validate_data.py | 新建 | JSON 零维护验证：node_id唯一性/next_node引用闭合/effect变量名合法/condition格式/multi_click/multi_click格式/auto_next引用 |
| 2026-05-10 | tests/test_state_manager.py | 新建 | 变量管理器23项单元测试：初始化/边界保护/CRUD/apply_effects/条件判定(min,max,eq,组合)/描述/显隐/序列化往返/重置 |
| 2026-05-10 | tests/test_story_engine.py | 新建 | 剧情引擎12项单元测试：加载/跳转/文本获取/条件过滤/选择效果应用/历史记录/auto_next触发/越界保护 |
| 2026-05-10 | tests/test_save_manager.py | 新建 | 存档系统8项单元测试：存档读档往返/覆写/空存档/自动档位/存档信息 |
| 2026-05-10 | tests/run_all.py | 新建 | 测试运行器：先数据验证后单元测试，汇总PASS/FAIL |
| 2026-05-10 | tests/启动测试.bat | 新建 | QA双击运行：chcp 65001 → python run_all.py → pause |
| 2026-05-10 | src/main_window.py | 新建 | GM 调试栏：Ctrl+Shift+G 右侧滑入35%面板（节点列表按章分组+Scrollbar+当前高亮/变量5行±调节/4组预设按钮）；仅 --gm 模式下快捷键生效 |
| 2026-05-10 | src/main.py | 新建 | GM 命令处理：cmd_gm_jump(直跳节点不存档)、cmd_gm_set_var(增量调节)、cmd_gm_preset(预设覆盖)、4组结局预设(GM_PRESETS)；_refresh_gm_panel 随 _display_node 自动刷新 |
| 2026-05-10 | docs/decisions.md | 更新 | D032: GM 调试栏方案——Ctrl+Shift+G/+--gm参数/节点跳转/变量调节/预设组合/不污染存档 |
| 2026-05-10 | 启动游戏.bat | 修复 | cd 路径从硬编码 C:\ 改为 %~dp0（自动定位bat所在目录）；追加 %* 支持传参 |
| 2026-05-10 | src/main_window.py + src/story_engine.py | 修复 | GM 节点列表按 JSON 原始顺序显示（story_engine._node_order）；GM 面板新增"加载章节"按钮（第1/2/3章，已加载显示 ✓）；空节点时显示"请先开始游戏或加载章节" |
| 2026-05-10 | src/main.py | 修复 | GM 加载章节：cmd_gm_load_chapter 从 _node_order 找该章首个节点作为起始（修复 nodes.get("start_node") None bug）；_refresh_gm_panel 使用 _node_order 保序；on_gm_open 回调每次面板打开时刷新数据 |
| 2026-05-10 | src/minigame_base.py + main.py | Bug修复 | 小游戏结束销毁顺序：_on_minigame_complete 先 destroy 实例再 hide_minigame；destroy 防重复 _on_stop；子类 _on_stop 加 winfo_exists 守卫；修复 Tkinter 8位色值 #RRGGBBAA→#RRGGBB |
| 2026-05-10 | docs/agents.md | 重写 | 原则栏 P1-P4 扩充至 P1-P8；FD 新增 P2(自验收清单)/P3(幂等性)/P4(防御性清理)；QA 新增 P2(破坏性路径)/P3(工具vs流程)/P4(测试矩阵)；PM 新增 P2(会毕即录)/P3(关键抽检)/P4(任务质量)；原始 P2-P3 顺延至 P5-P6 |
| 2026-05-10 | docs/work_standards.md | 更新 | W003 追加"FD 交底"条款：FD 交付功能时须附带一句行为说明，QA 据此验证并写入测试矩阵；无交底说明→QA 有权拒绝验收 |
| 2026-05-10 | docs/test_report.md | 更新 | QA 批次：GM 调试栏功能验收 14/14 通过（GM-01~GM-14）/ 已知限制 2 条 |
| 2026-05-10 | docs/agents.md | 新增 | 预检清单：7 项自检（PM 文档同步/FD 自验收/FD 幂等性/FD→QA 交底/QA 破坏性路径/QA 测试矩阵/PM 会毕即录）；"检查原则"纠偏暗号 |
| 2026-05-10 | 启动游戏_GM模式.bat | 新建 | GM 调试模式启动脚本：chcp 65001 → cd %~dp0 → python src\main.py --gm → pause |
| 2026-05-10 | — | 会话 | 本日工作结束。里程碑4：存档+面板+3章JSON+GM栏+脚本化测试+音效架构+代理原则8栏化+预检清单，46/46测试通过，GM QA验收14/14通过。下步：QA存读档链路测试。
| 2026-05-10 | src/main.py + src/minigame_base.py | Bug修复 | 小游戏结束时 `_on_minigame_complete` 先调 `hide_minigame`（销毁canvas）后调 `destroy`（unbind canvas）→ 顺序对调；`destroy` 防重复 `_on_stop`；子类 `_on_stop` 加 `winfo_exists` 守卫 |
| 2026-05-10 | docs/work_standards.md | 更新 | W001 追加"PM 文档同步"条款：PM 须将每次讨论结论同步至 decisions/design/optimizations/progress；漏同步=决策未生效 |
| 2026-05-10 | docs/work_standards.md | 更新 | W001 追加"PM 文档同步"条款：PM 须将每次讨论结论同步至 decisions/design/optimizations/progress；漏同步=决策未生效 |
| 2026-05-10 | docs/decisions.md | 更新 | D030: PM 文档同步纪律——4 份文档对应 4 类结论，漏同步任何人有权拒绝执行 |
| 2026-05-10 | docs/agents.md | 新建 | 代理人设文档：全局技术约束5条 + 7角色×5列表格(角色/职责/原则/对标/边界)，每角色3-4条P1-P4优先级原则，顶部状态行(M4 80%) |
| 2026-05-11 | tests/test_save_integration.py | 新建 | 存档/读档集成测试：11 项（SA-01~11），覆盖完整往返/sound_state/数据格式/多槽位/边界 |
| 2026-05-11 | docs/test_report.md | 更新 | QA 存档/读档链路测试通过：19/19 全部通过（SA-01~11 + QA-08~09 + 单元 8） |
| 2026-05-11 | src/main_window.py | Bug修复 | B008: `_show_title_and_menu` 在 text_area DISABLED 态执行 delete/insert 静默失败，导致引言结束后"灯塔"标题不显示。修复：delete/insert 前补 `text_area.config(state=tk.NORMAL)` |
| 2026-05-11 | src/main_window.py | Bug修复 | B009: `_build_status_bar` 存档/读档按钮回调 lambda 改为 `getattr(self, attr_name)` 动态查找，修复 `__init__` 期间 `None` 永久捕获 |
| 2026-05-11 | src/main_window.py | Bug修复 | B010: `update_panel_notes/status/items` 新增缓存字段 `_cached_*`，`_show_panel` 打开时从缓存渲染，修复面板关闭期间数据丢弃导致打开空白 |
| 2026-05-11 | src/main_window.py | Bug修复 | B011: Tab 键绑定 `root.bind` → `root.bind_all`，防 Text 组件焦点遍历拦截 |
| 2026-05-11 | docs/agents.md | 更新 | 新增「会话规则」节（专职应答）；角色原则表扩展 P5 列；FD 新增 P4 交付前自检+P5 回归三点+空壳禁令；QA P2 扩充人手令+P4 启动即测；SD 新增 P5 空壳禁令；GD 新增 P5 标记注册表 |
| 2026-05-11 | docs/decisions.md | 更新 | D033: Bug 复盘与工作流强化——FD/QA/SD/GD 新增原则、五条根因归类、标记注册表计划 |
| 2026-05-11 | tests/test_sound_manager.py | 新建 | SD 音效验收测试：21 项（SD-01~04），覆盖实例化/API签名/边界保护/不阻塞 |
| 2026-05-11 | tests/test_interaction.py | 新建 | 交互状态机交叉测试：9 项（面板×暂停/面板×打字/光点tuple一致性），对应 fd_selfcheck.md 交互矩阵 X1~X6 |
| 2026-05-11 | docs/fd_selfcheck.md | 更新 | 追加交互矩阵表（X1~X6）：覆盖面板×暂停/面板×打字/面板×选项/小游戏/浮窗六种交叉场景 |
| 2026-05-11 | — | 会议 | Tab 键四轮修复复盘：根因不在原则设计而在执行——FD 未按 P4 做物理自检、QA 未按 P2 区隔脚本与物理操作、PM 未逐轮记录中间版本。结论：不新增原则，在 W003 加 FD 自检声明强制手续 |
| 2026-05-11 | docs/changelog.md | 更新 | 补记 启动游戏_GM模式.bat 创建记录 |
| 2026-05-11 | docs/work_standards.md | 更新 | W001 新增「文件入库」条款：新文件须入 changelog，根目录脚本须入 progress 清单 |
| 2026-05-11 | docs/progress.md | 更新 | M5 正式任务表追加：FD 标记叠加回归测试、darkness_overlay 模块、SD 5 音效实现、ND [sound] 预标 |
| 2026-05-11 | docs/nd_selfcheck.md | 新建 | ND 剧情自检清单：8 项叙事检查 + 交付声明模板 + 变更通知模板 |
| 2026-05-11 | docs/agents.md | 更新 | 角色表扩展 P6 列；ND 新增 P6 句式多样性（比喻句式每节点≤1处）；优先级延至 P6 |
| 2026-05-11 | src/state_manager.py | 更新 | `describe()` 新增 `day` 参数，trust/curiosity/sanity 描述按天数分段返回，消除早期天预知感 |
| 2026-05-11 | src/main.py | 更新 | `_refresh_panel` 调用 `describe()` 时传入 `self.story.day` |
| 2026-05-11 | tests/test_state_manager.py | 更新 | trust 描述测试同步到新文案 |
| 2026-05-11 | docs/optimizations.md | 新增 | OPT-14: 备忘录支持前后文翻阅 + 下划线/颜色标记重点文字（轻度优化，M6执行） |
| 2026-05-11 | docs/work_standards.md | 更新 | W003 新增「ND 自检声明」条款；关联文档补注 nd_selfcheck.md |
| 2026-05-11 | data/chapter_01.json | 优化 | ND: ch01_evening 开门改为完整下午垫片——覆盖设备学习/翻抽屉/独探三条分支路径（"下午的时间在塔里过得很快——不管你是…"） |
| 2026-05-11 | data/chapter_01.json | 优化 | ND: ch01_evening 开头加行为垫句 "你看了很久。"——选择→转场之间多一步缓冲 |
| 2026-05-11 | data/chapter_01.json | 优化 | ND: ch01_explore 结尾“床单铺好了”加视觉/嗅觉细节（肥皂味/折痕/带上门） |
| 2026-05-11 | data/chapter_01.json | 优化 | ND: ch01_evening 张海生离场加听觉/视觉描写（门口顿步/铰链声/空盘凉水） |
| 2026-05-11 | src/story_engine.py | 新增 | `text_bridges` 来路分流引擎：`_last_node_id` 记录跳转源节点，`get_current_text()` 按前置节点匹配桥段拼接到正文前（`*` 作 fallback） |
| 2026-05-11 | data/chapter_01.json | 新增 | ch01_evening 添加 `text_bridges` 字段（5 条特定桥 + `*` fallback），正文去除通用桥段 |
| 2026-05-11 | data/chapter_02.json | 新增 | ch02_evening 添加 `text_bridges` 字段（3 条特定桥 + `*` fallback），正文去除通用桥段 |
| 2026-05-11 | tests/validate_data.py | 新增 | 汇聚节点信息报告（`_report_convergence`）：打印全部被 ≥2 条路径指向的节点及来路标签，供 ND 同源异构扫描 |
| 2026-05-11 | docs/nd_selfcheck.md | 更新 | 第 2 条拆为 2A 时间连续性/2B 动作连续性/2C 人物状态一致性；新增第 9 条同源异构路径状态一致；使用方式新增第 7 步专项扫描 |
| 2026-05-11 | src/story_engine.py | 新增 | `check_ending()` 结局判定函数——8 结局优先级链（G 隐藏道具 > death 死亡 > F > A > E > B > D > C），D 在 C 前判定避免子集覆盖 |
| 2026-05-11 | src/main.py | 更新 | GM_PRESETS 扩至 6 组覆盖 6 个变量结局（A/B/C/D/E/F），移除无效旧预设 |
| 2026-05-11 | docs/nd_selfcheck.md | 新增 | 第 11 条：新增 effects 终点可达性检查 |
| 2026-05-11 | docs/design.md | 更新 | §2.3 effects 表 GD+ND 对齐（精确数字）；§2.5 优先级修正（D 移到 C 前） |
| 2026-05-11 | — | 会议 | 结局设计讨论：ND 提出 3 件 X 道具（撕页/画/日志）+ 荒诞结局；GD 给 8 结局优先级映射；FD 确定递进链技术方案（auto_next+单选+只读模式）；QA 制 GM 预设 + 结局链验证流程 |
| 2026-05-11 | src/main_window.py | 新增 | `MOOD_SPEEDS` 字典 + `_typewrite_delay` 动态打字速度：dread 35ms / tension 22ms / loss 40ms / quiet 30ms（默认） |
| 2026-05-11 | src/main.py | Bug修复 | B018: `_display_node` 直接读 `node["text"]` 绕过 `get_current_text()` 中的 text_bridges 拼接逻辑，导致全部来路分流桥段静默失效。修复：改为 `self.story.get_current_text()` |
| 2026-05-11 | tests/validate_data.py | 更新 | 新增 mood 值域检查（dread/tension/loss/quiet/None） |
| 2026-05-11 | data/chapter_01~03.json | 新增 | 全部 35 节点标注 `mood` 字段（ch01: 7, ch02: 13, ch03: 15） |
| 2026-05-11 | docs/design.md | 更新 | §4.2 JSON 格式字段列表补 `mood` |
| 2026-05-11 | data/chapter_02.json | 优化 | ND: ch02_d3_start 开门加走廊→早晨垫片（"什么都没有。或者说，什么都已经走了。"） |
| 2026-05-11 | data/chapter_03.json | 优化 | ND: ch03_d5_start 开门加地下室问话→次日垫片（"他把最后一桶油漆码好——那个动作像是在给对话盖章"） |
| 2026-05-11 | data/chapter_03.json | 优化 | ND: ch03_d6_start 开门加傍晚对峙→没睡垫片（"他走过去把铁门的插销重新插上了——那个声音比任何一句话都重"） |
| 2026-05-11 | data/chapter_01.json | 优化 | ND: ch01_evening 5 条 text_bridges 每桥末尾加动作过渡句（起身/走去厨房） |
| 2026-05-11 | data/chapter_02.json | 优化 | ND: ch02_evening 3 条 text_bridges + * fallback 末尾加动作过渡句；ch02_night 加 "你洗了碗，回了房间"；ch02_d3_evening 加 "你一个人吃了晚饭。碗是你自己洗的" |
| 2026-05-11 | data/chapter_02.json | 优化 | ND: ch02_evening 开门加时间过渡桥（"天黑之后你走进厨房，发现张海生已经在灶台前面了"） |
| 2026-05-11 | data/chapter_03.json | 优化 | ND: ch03_basement_find [shake] "它在等"→"它就在那面墙的后面。等着。" 扩充至 11 字 |
| 2026-05-11 | docs/nd_selfcheck.md | 更新 | 使用方式增加"回顾重检"路径（启动游戏.bat 从头走，捕捉跨章过渡）；自检表 8 PASS |
| 2026-05-11 | src/minigame_base.py | Bug修复 | B013: `_on_click` 解包 4→5 元素（`dot_id`→`dot_inner, dot_outer`），修复 MG2 光点点击崩溃 |
| 2026-05-11 | src/main_window.py | Bug修复 | B014: `_show_panel` 取消 `_pause_job`、`_finish_pause` 检查 `_panel_open`，修复暂停计时器穿透面板导致文本背后翻页 |
| 2026-05-11 | src/main.py | Bug修复 | B015: 删除 `cmd_choice` 中重复的 `gray_choices()+make_choice()` 代码块（行163-172），修复 effects 双加/history 双写/节点跳转错乱 |
| 2026-05-11 | src/main_window.py | Bug修复 | B016: `show_chunked_text` 开头新增取消旧 `_typewriter_job` 和 `_pause_job`，修复快速节点切换时旧计时器在新文本上执行 |
| 2026-05-11 | src/main_window.py | Bug修复 | B017: `_typewrite_current_chunk` shake 独块无剩余文字时不再 fall through 到通用打字分支，改为直接推进到下一块 |
| 2026-05-11 | docs/bug_list.md | 更新 | B015~B017 修复并转入已修复表 |
| 2026-05-11 | data/chapter_01~03.json | 优化 | ND: 5 处同源异构选择汇聚节点做兼容修复 |
| 2026-05-11 | data/chapter_04.json | 新建 | ND: 第4章骨架——16节点全覆盖 D7-D9（坦白/梦境/海鸟/黑暗收缩/隐藏道具），effects+mood 预填 |
| 2026-05-11 | data/chapter_05.json | 新建 | ND: 第5章骨架——17节点全覆盖 D10-D12（撕页/合作对抗/黑暗收缩对抗/提前逃离E链） |
| 2026-05-11 | src/darkness_overlay.py | 新建 | 黑暗收缩覆盖层 V1（100ms帧/50s矩形收缩），MG4B/MG5共用 |
| 2026-05-11 | src/minigame_base.py | 新增 | MG4A_SeabirdDodge 海鸟躲避（鼠标避鸟，5次闪避） |
| 2026-05-11 | src/minigame_base.py | Bug修复 | test_interaction 编码修复：从 git 恢复原始 MG1/MG2/MG3 + 追加 MG4A（清除重复代码和 BOM 污染） |
| 2026-05-11 | — | 配置 | GitHub 远程仓库配置：`https://github.com/Ren-kui/LightHouse`，`git push origin master:main` |
| 2026-05-11 | docs/progress.md | 更新 | 根目录文件清单新增 GitHub 远程仓库地址 |
| 2026-05-11 | docs/agents.md | 更新 | 状态行更新：M5 实际进度（第 4-6 章完成/87 测试/结局引擎/MG4A/MG4B/MG5/darkness_overlay） |
| 2026-05-12 | docs/progress.md | 更新 | PM 文档同步：M2/M3/M4→100%✅，M5→75%，M6→20%；M5 预备任务+正式任务全部补状态列；根目录文件清单追加启动测试.bat |
| 2026-05-12 | docs/decisions.md | 新增 | D034：GD 5 结局精确定量阈值表正式交付（design.md §2.5 与 story_engine.py 全 8 结局逐项对齐） |
| 2026-05-12 | docs/decisions.md | 新增 | D035：角色交付不可绕过+声明确认制（W005 + agents.md 会话规则 #2/#3） |
| 2026-05-12 | docs/work_standards.md | 新增 | W005：角色交付不可绕过规则——5 角色强制声明格式表、PM 放行前验声明、角色隔离挡板 |
| 2026-05-12 | docs/agents.md | 更新 | 会话规则表新增 #2 声明确认制、#3 角色隔离 |
| 2026-05-12 | src/sound_manager.py | 重写 | M5 PCM 合成实装：_generate_tone/_gen_sine/_gen_square/_gen_pulse/_gen_noise/_gen_fade 六波形生成器；_generate_all 预生成 5 音效 wav 到 data/sounds/；play 使用 winsound SND_ASYNC 异步线程播放；stop/stop_all/mute 完整实现 |
| 2026-05-12 | tests/test_sound_manager.py | 更新 | SD-04 时序约束从 M4 空壳（100ms/50ms/10ms）更新为 M5 实装（2000ms/500ms/50ms），匹配 PCM 合成 I/O 开销 |
| 2026-05-12 | data/chapter_01.json | 优化 | ND P6 隐喻清理：5 节点修复（比…更…2→1，像-类 4→1，不是…是… 3→1）；ch01_evening text_bridge 修复 |
| 2026-05-12 | data/chapter_02.json | 优化 | ND P6 隐喻清理：10 节点修复（ch02_silhouette 像-类 5→1、ch02_night 像+不是 4+2→各1、其余各节点单类超标修复） |
| 2026-05-12 | data/chapter_03.json | 优化 | ND P6 隐喻清理：6 节点修复（ch03_d5_search 不是…是… 4→1、ch03_basement_enter 像+不是 2+3→各1、其余节点单类超标修复） |
| 2026-05-12 | docs/bridges.md | 新建 | ND 桥段文档：定义（4 连续性）→ 写作原则（8 条）→ 汇聚节点配置表（6 章全部节点）→ `*` fallback 原则。ND 维护，QA 对表验收。 |
| 2026-05-12 | docs/nd_selfcheck.md | 更新 | 第 7 条同源异构专项扫描扩充为 bridges.md 对表流程；第 7/9 条自检项增加 bridges.md 引用；交付声明追加桥配置行 |
| 2026-05-12 | docs/agents.md | 更新 | ND 对标列追加 bridges.md §2 写作原则 |
| 2026-05-12 | docs/design.md | 更新 | §4.2 JSON 格式 text_bridges 说明追加 bridges.md 引用 |
| 2026-05-12 | docs/work_standards.md | 更新 | ND 自检声明格式追加汇聚节点数 + text_bridges 条数 + bridges.md 对表确认 |
| 2026-05-12 | src/main_window.py | 新增 | M5 音效集成：set_sound_manager 接收注入；[shake]→heartbeat 同步播放；[sound] 块级关联（SOUND_N 占位→chunk_idx→play）；_show_panel 面板打开→stop_all 静默；_hide_panel→on_toggle_panel 回调 |
| 2026-05-12 | data/chapter_02~03~06.json | 新增 | 22 个中间桥节点：拆分同源汇聚选择路径，消除"也许A也许B"条件桥语言 |
| 2026-05-12 | data/chapter_02~06.json | 重写 | 110+ text_bridges 全量重写：ch02 5组/ch03 5组/ch04 3组/ch05 2组/ch06 1组 |
| 2026-05-12 | tests/validate_data.py | 更新 | text_bridges 合法前置节点检查追加 `auto_next` 支持 |
| 2026-05-12 | src/minigame_base.py | Bug修复 | B019: MG2 光点叠层——`_clear_dot_and_next` 中取消旧 `_spawn_timer` 防重复召唤 |
| 2026-05-12 | docs/work_standards.md | 新增 | W006: 异步回调防卫——cancel 旧→设状态→schedule 新 |
| 2026-05-12 | docs/agents.md | 更新 | FD P5 扩充异步防卫；状态行更新 M5 85% |
| 2026-05-12 | docs/fd_selfcheck.md | 新增 | X7 交互矩阵：计时器到期瞬间点击验证 |
| 2026-05-12 | docs/decisions.md | 新增 | D036: B019 复盘，异步回调防卫制 |
| 2026-05-12 | docs/bug_list.md | 新增 | B019: MG2 光点叠层 P1 已修复 |
| 2026-05-12 | docs/bridges.md | 更新 | ch02~06 汇聚节点配置表全部更新为 ✅ |
| 2026-05-12 | docs/progress.md | 更新 | M5 75%→85%；任务状态同步桥段+音效+B019 |
| 2026-05-12 | data/chapter_02.json | 修复 | ND自检：ch02_night_walk P6/ ch02_d3_start桥P6/ ch02_mg2_failure桥POV/ ch02_even_ask桥#9预演/ ch02_sil_ask P6+POV/ ch02_mg2_success 具体替换抽象+体验感 |
| 2026-05-12 | data/chapter_03.json | 修复 | ND自检：ch03_d4_note P6/ ch03_belong_hold P6/ ch03_belong_silent P6 |
| 2026-05-12 | docs/agents.md | 更新 | ND P1 扩充"不绕"示例；ND P3 扩充"体验感"——不是加个"好像"就够，须写"看→判断"的完整心理过程 |
| 2026-05-12 | docs/bridges.md | 更新 | §2 新增写作原则 #9：桥段不预演正文 |
| 2026-05-12 | docs/bug_list.md | 新增 | B020: GM面板关闭后滚轮 TclError P1 已修复 |
| 2026-05-12 | docs/bridges.md | 重写 | §1 桥的两类作用（类型一分叉叙事/类型二体验过渡）；新增原则 #10（时间线停在正文前）+黄金规则 |
| 2026-05-12 | docs/agents.md | 更新 | ND P4 追加桥分类引用 |
| 2026-05-12 | docs/design.md | 更新 | §2.1 标注主线固定+变量分叉结构 |
| 2026-05-12 | docs/decisions.md | 新增 | D037: 桥设计澄清——两类作用+主线固定结构 |
| 2026-05-12 | data/chapter_02.json | 修复 | ch02_explore_tell/stay 桥节点剧透+上帝视角修复；ch02_silhouette text_bridges 缩为简短承接 |
| 2026-05-12 | src/minigame_base.py | Bug修复 | MG4A 崩溃：`_complete` 回调 `after(10)` 延迟防调用栈内销毁；`destroy` 始终执行 `_on_stop`；`_on_stop` 去除条件 return |
| 2026-05-12 | src/darkness_overlay.py | Bug修复 | V1 启动崩溃：`w`/`h` 赋值缩进在 `if version>=2:` 块内，V1 启始时未绑定。移出为公共代码 |
| 2026-05-12 | src/darkness_overlay.py | Bug修复 | MG4B 全黑：`winfo_width()=1` 非 falsy→`or 860`不生效，改为 `<50` 阈值判断 |
| 2026-05-12 | src/main.py | 更新 | GM 加载章节从 3 章扩展为 6 章；`_analyze_node_sounds` day 用 `or 1` 防 `null`；MG4B/MG5 回调传实际成功/失败 |
| 2026-05-12 | data/chapter_04.json | 修复 | ch04_darkness_end 选择标签乱码修复（"一层你是再也睡不着的"→"反正睡不着"） |
| 2026-05-12 | data/chapter_05.json | 修复 | 日记原文"不能抓——只能接"→"不抢——只收"；张海生对白"那不是文学"→"我不是在形容。它是真的。"；"它是接收"→"它不收——只等" |
| 2026-05-12 | docs/agents.md | 更新 | ND P1 追加"对话口语化"规则：NPC 对白须符合身份背景语感 |
| 2026-05-12 | docs/agents.md | 更新 | FD P5 扩充"生命周期"；状态行 M5 详情重写 |
| 2026-05-12 | docs/work_standards.md | 新增 | W007: 小游戏生命周期防卫（回调延迟+destroy无条件清理+_on_stop禁条件return） |
| 2026-05-12 | docs/work_standards.md | 新增 | W008: Tkinter 尺寸防卫（winfo_width()未渲染=1，须<50阈值判断） |
| 2026-05-12 | docs/decisions.md | 新增 | D038: MG4A 崩溃复盘——小游戏生命周期防卫 |
| 2026-05-12 | docs/fd_selfcheck.md | 更新 | X8: MG4A 连中 3 次→canvas 安全销毁；交互矩阵补 W008 自检 |
| 2026-05-12 | docs/work_standards.md | 更新 | W003 Bug 清单条款重写：QA 两层分工（逻辑层 AI / 物理层老板）+ 老板关闭 + FD 不得自行标记已修复 |
| 2026-05-12 | docs/agents.md | 重写 | QA 行：从"测试验收·独立放行官"→"测试审计员·两层分工"；去放行权、加验证记录交付 |
| 2026-05-12 | docs/bug_list.md | 更新 | 维护人改为 QA（实际执行：老板/FD）；新增 FD 不得自行标记已修复条款 |
| 2026-05-12 | tests/test_qa_logic.py | 新建 | QA 逻辑层验证：10 项——flag 写入/结局不可达/桥段匹配/多击可用/MG2 竞态修复/6 章加载/8 结局节点/return_drawer 存在 |
| 2026-05-12 | docs/decisions.md | 新增 | D039: QA 角色重定义——从独立放行官→测试审计员，两层分工（逻辑 AI + 物理老板） |
| 2026-05-12 | docs/progress.md | 更新 | M5 90%→100% ✅；音效 6 项蒙灰不计入；darkness V2 + 多击渐变完成 |
| 2026-05-12 | docs/agents.md | 更新 | 状态行重写；M5 ✅ 100% M6 🔄 20% |
| 2026-05-14 | docs/agents.md | 更新 | GD P4 标记注册表从"待创建，M6 执行"→"持续维护"（三向流：FD实现→GD同步→ND查表）；FD P2 追加设计级 Bug 上报 PM 通道 |
| 2026-05-14 | docs/decisions.md | 新增 | D041：标记注册表维护流程 + Bug 设计级分级（专题会议结论） |
| 2026-05-14 | docs/agents.md | 更新 | UI/FD 边界"不新增交互模式"→"不自行新增"；ND P2 追加音效暂停期间继续预标 [sound]；使用说明追加跨角色同级 P 升级链 + 新交互模式流程 |
| 2026-05-14 | data/markup_registry.json | 更新 | [sound] 条目 note 追加"ND 继续预标 [sound name]"指引 |
| 2026-05-14 | docs/decisions.md | 新增 | D042：角色边界澄清三案（交互模式归属/SD暂停连锁/同级P冲突升级链） |
| 2026-05-14 | docs/agents.md | 更新 | QA P2 "未完待工"扩充代码层空壳验证；FD P5 回归三点明确触发文件范围；使用说明追加 W005 声明遗忘修复通道 |
| 2026-05-14 | docs/decisions.md | 新增 | D043：低优先隐患三案（空壳验证/声明遗忘修复/回归三点范围明确） |
| 2026-05-14 | docs/agents.md | 更新 | QA P1 追加留痕纪律（命令输出/声明一致性/数据完整性主动扫描）；QA P3 追加 bug_list 主动扫描提醒；QA 边界追加可追溯要求 |
| 2026-05-14 | docs/work_standards.md | 更新 | W005 QA 声明格式升级：新增测试输出/FD声明一致性/数据完整性三个强制字段，禁止模糊陈述 |
| 2026-05-14 | docs/decisions.md | 新增 | D044：QA 留痕纪律强化（被动记录员→主动留痕审计） |
| 2026-05-14 | src/main_window.py | 更新 | B1: OPT-11 小游戏界面居中 + UI 外框——minigame_area 改为居中 700×550 固定尺寸框架，外框 #555555 3px；所有小游戏自动受益 |
| 2026-05-14 | src/minigame_base.py | 重写 | B2: MG1 配电连线——6对端子+6中继点+亮灭灯循环(亮1.5s/灭2.5s)；左→中继→右三段点击配对 |
| 2026-05-14 | src/minigame_base.py | 修复 | B2 后续：`_clear_all_highlights` 删除残留拆包死代码（`_, color = self._relays[0]` 4元组拆2值导致 ValueError） |
| 2026-05-14 | src/main_window.py / minigame_base.py | 修复 | B2/MG1: 灭灯阶段不再清除选中状态；亮灯恢复已选高亮；灭灯时中继点保持暗色；时间30→36s；中继Y序打乱(错位不失控)；画布<50阈值兜底；游戏区居中扣状态栏+<100窗口尺寸兜底 |
| 2026-05-14 | docs/bug_list.md | 新增 | B021：B2 MG1 `_clear_all_highlights` ValueError P0/FD自发现 |
| 2026-05-14 | docs/work_standards.md / agents.md | 更新 | FD W005 声明 + FD P4 追加 "crash 必须报告" 条款，填补 FD 自发现 bug 的记录空白 |
| 2026-05-14 | src/minigame_base.py | 重写 | B3: MG2 太阳能反应——黄点缩小至50%+蓝干扰点(0-2，点中-1)+光点移动+15%双黄点；目标6/12 |
| 2026-05-14 | tests/test_interaction.py / test_qa_logic.py | 更新 | B3: 适配新MG2 API（`_hit_yellow`/`_hit_blue`/`_schedule_next`） |
| 2026-05-14 | src/minigame_base.py | 重写 | B4: MG4A 海鸟躲避——25s计时赛（被击中≤4次胜利），灰鸟1x/红鸟2.5x(1/15)，鼠标归正中心，`found_bird_skull` flag |
| 2026-05-14 | src/story_engine.py / data/chapter_04.json | 更新 | B4: 小游戏结果新增 `success_flags` 支持，MG4A成功写入鸟头骨flag |
| 2026-05-14 | src/minigame_base.py / main.py | 重写 | B5: 新增 MG4B5_DarkCircuit 复合小游戏——上屏6对配电+下屏暗红收缩(#aa0000)+能量条(30格/-1每2s/点击+1/过热10连击4s冷却/归零收缩×3/收缩≥1死亡) |
| 2026-05-14 | src/minigame_base.py / main_window.py | 修复 | 全局居中：全部 `int(canvas["width"])`→`winfo_width()`+`<50`兜底；`show_minigame`加`update_idletasks()`强制渲染；status_bar高度扣除 |
| 2026-05-14 | src/minigame_base.py | 优化 | B5 微调：收缩速度×4(0.008)、能量消退2s、X/Y独立收缩计算防提前死亡、起始红框#aa0000、能量条400ms闪烁提醒、"黑暗逼近！"移到底部中央、死亡警告字号加大 |
| 2026-05-14 | docs/progress.md / design.md / agents.md / optimizations.md | 同步 | M6 20%→50%；B1~B5全部✅；design.md §2.4更新最终小游戏规格；OPT-11完成 |
| 2026-05-14 | src/main_window.py | 新增 | 关键选项金色显示——`_show_menu`新增`styles`参数，`important:true`选项文字#ccaa00(金)/悬停#ffcc00(亮金) |
| 2026-05-14 | data/chapter_02~06.json | 更新 | 24个关键选项加`"important":true`：minigame触发(8)+multi_click(1)+故事关键分支(15) |
| 2026-05-14 | docs/design.md | 更新 | §4.2 JSON格式追加`"important"`字段说明 |
