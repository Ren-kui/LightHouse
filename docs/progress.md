# 项目进度看板

> 维护者：PM | 最后更新：2026-05-10
> 
> ⚠️ 使用前必读：docs/work_standards.md (W001/W002/W003)

---

## 总体里程碑

```
里程碑 0 · 重建筹备+文档同步  ████████████████████ 100% ✅
里程碑 1 · 最小窗口验证      ████████████████████ 100% ✅
里程碑 2 · 状态机+标题界面    ████████████████████ 100% ✅
里程碑 3 · 文本打印+选项跳转  ████████████████████ 100% ✅
里程碑 4 · 存档+面板         ████████████████░░░░ 80% 🔄
里程碑 5 · 第2-6章+小游戏    ░░░░░░░░░░░░░░░░░░░░  0%
里程碑 6 · 打磨+exe打包      ░░░░░░░░░░░░░░░░░░░░  0%
```

---

## 里程碑 0 · 重建筹备 ✅ 100%

| 任务 | 负责人 | 状态 |
|------|--------|------|
| 全量重建决定（D025） | PM/老板 | ✅ |
| 重建顺序确认（D026） | PM/各方 | ✅ |
| 第一步确认（D027） | PM | ✅ |
| decisions.md 同步 | PM | ✅ |
| design.md 第四卷更新 | FD | ✅ |
| progress.md 重建看板 | PM | ✅ |
| changelog 记录 | PM | ✅ |

---

## 里程碑 1 · 最小窗口验证      ████████████████████ 100% ✅

| 任务 | 负责人 |
|------|--------|
| 纯黑 Tkinter 窗口 + "灯塔"标题，验证字体/配色/尺寸 | FD |
| QA 验证窗口渲染正常 | QA |

---

## 里程碑 2 · 状态机 + 标题界面 ⏳

| 任务 | 负责人 |
|------|--------|
| Game 类状态机骨架（TITLE→TYPING→WAITING→CHOICES→MINIGAME→SAVE_LOAD） | FD |
| 标题界面 + 菜单交互（▶ 新游戏 / 继续 / 退出） | FD+UI |
| QA 验证标题菜单交互 | QA |

---

## 里程碑 3 · 文本打印 + 选项跳转 ⏳

| 任务 | 负责人 |
|------|--------|
| 逐字打印 + 按 \n\n 分块 + 按键翻页 + "▼ 空格继续"提示 | FD+UI |
| 选项生成（▶ 箭头 + 居中 + 悬停变色） | FD+UI |
| story_engine 接入（JSON 加载 + 节点跳转 + conditions 判定） | FD |
| state_manager 接入（effects 应用 + 变量描述） | FD |
| chapter_01.json 格式重调 + effects 对齐 | ND |
| QA 第1章全分支可达性测试 | QA |

---

## 里程碑 4 · 存档 + 面板 ⏳

| 任务 | 负责人 |
|------|--------|
| 存档/读档 UI 浮窗 + save_manager 接入 | FD+UI |
| 状态面板（Tab 键右侧滑入遮罩）| FD+UI |
| QA 存档/读档完整链路测试 | QA |
| 第2-3章 JSON 编写 (4D/4E) | ND/FD |
| 今日笔记 + 面板暂停文本 + 存档反馈 | FD |
| sound_manager.py 空壳 API（play/stop/stop_all/volume/mute/unmute） | SD/FD |
| sound_spec.md 规范文档 + 静默规则表 + 音效注册表 | SD |
| QA 音效模块基础验收（SD-01~04：实例化/API/边界/不阻塞） | QA |
| 脚本化测试体系搭建（validate_data + 3 单元测试 + run_all） | FD/QA |
| GM 调试栏（Ctrl+Shift+G / 节点跳转 / 变量调节 / 预设组合 / --gm） | FD/GD/QA |
| text_bridges 来路分流引擎（story_engine + ch01/ch02_evening 分流桥段 + validate_data 验证） | FD/ND/QA |
| ND P5 人际兑现原则 + nd_selfcheck.md + fd_selfcheck.md 交互矩阵 | ND/FD/PM |

---

## 里程碑 5 · 第 2-6 章 + 小游戏 ⏳

### M5 预备任务（老板已确认）

| 任务 | 负责人 | 状态 |
|------|--------|------|
| GD 交付 5 结局精确定量阈值表（A/B/C/D 四组，[var ≥/≤ value] 组合；E 留扩展槽） | GD | 待 |
| FD 按 GD 阈值表写入 story_engine 结局判定逻辑，GM 预设验证 | FD | 待 |
| ND 等待老板意见后启动第 4 章 JSON | ND | 待 |

### 正式任务

| 任务 | 负责人 |
|------|--------|
| 日记残页 4 段原文 delivery | ND |
| chapter_02~06.json 编写 | ND |
| MG1/MG2/MG3 小游戏实现 | FD |
| MG4/MG5 黑暗收缩集成 + darkness_overlay 模块 | FD |
| 标记叠加回归测试（每章 JSON 完成后 FD 验 [shake]+[pause]+[sound] 共现不互污染） | FD |
| 5 核心音效实现（hum_low/heartbeat/metal_creak/water_drone/silence_fade），按 ch02/ch03 触发点落地 | SD/FD |
| ND 第 4 章 JSON 中预标 [sound name] 标记 | ND/SD |
| QA 全章节测试 | QA |

---

## 里程碑 6 · 打磨 + exe 打包 ⏳

| 任务 | 负责人 |
|------|--------|
| [shake] / [pause] 标记解析 | FD |
| 多次点击按钮颜色渐变 | FD+UI |
| 全结局可达性测试 | QA |
| 错别字审查 | QA/ND |
| exe 打包 + 运行测试 | FD+QA |

---

> **当前状态**：M4 代码端完成。B002~B011 全部修复，57 测试通过，GM 栏可用，存档/面板 bug 清零。剩余：QA 手动验收 SD 音效基础验收（SD-01~04）。

---

## 根目录文件清单

> 维护者：PM | 根目录启动/工具脚本的用途索引。新增脚本须同步记入 changelog.md。

| 文件 | 用途 |
|------|------|
| `启动游戏.bat` | 普通模式启动（`python src\main.py %*`） |
| `启动游戏_GM模式.bat` | GM 调试模式启动（`python src\main.py --gm`） |

