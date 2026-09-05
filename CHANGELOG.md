# Changelog

本文件由 soia-meta-skill-release 在每次正式发版时自动更新，与 GitHub Release 同源；
更早的版本演进见 git 提交历史与 GitHub Releases。

## v1.18.1 — 2026-09-05

Reuse explicitly approved installation plans without weakening confirmation gates

## 维护
- docs: clarify autonomy and preserve explicit approval gates (#111)
- chore(release): open next train after v1.18.0 (#110)

## v1.18.0 — 2026-09-04

升级 SOIA 技能安装范围选择与计划矩阵

## 新增
- feat(env): add explicit SOIA skill install planning (#107)
- feat(local-model-bench): 请求级推理深度参数——深度矩阵免重启服务（1.5.1）

## 维护
- chore(release): promote train to v1.18.0 (#108)
- chore(release): open next train after v1.17.0 (#106)

## v1.17.0 — 2026-08-21

local-model-bench 1.5.0：两入口场景+市场发现+报告版本化+Apple Silicon 带宽谱系；题库 B 组扩容 36 题（自动判定 27 道）+分维度报告

## 新增
- feat(local-model-bench): 评测报告按维度分层输出（B3）
- feat(soia-env-local-model-bench): 题库 B 组扩容批次1——新增代码题 C4-C8 与结构化题 E4-E6
- feat(bench): B 组扩容批次 1 数学组新增 7 题（D4-D8 原创 + D2b/D2c 扰动变体）
- feat(local-model-bench): 两个入口场景 + 市场发现流程 + 报告版本化 + 带宽谱系（1.4.0）

## 修复
- fix(ci): target Dependabot updates at dev (#101)

## 维护
- chore(train): dev 含 feat（两入口场景/市场发现/报告版本化/B 组题库扩容 36 题），列车提为 minor 1.17.0-SNAPSHOT
- chore(local-model-bench): B 组扩容收口——题库 36 题/前向预期 27/隔离陷阱/温度绑定实况化（1.5.0）
- chore(release): open next train after v1.16.0 (#104)

## v1.16.0 — 2026-08-21

正式发布本地模型基准评测：新增 F 维度实用场景题、翻转检验报告、全量 trace 与续跑模型守卫，并同步 WorkBuddy 安装说明。

## 新增
- feat(local-model-bench): 题库新增 F 维度实用场景六题（日期/拒编/幻觉抵抗/翻译/摘要/格式）
- feat(local-model-bench): 翻转检验 flip_report + 全量 trace 落盘 + 续跑模型守卫 + 统计资格表述规范（1.3.0）

## 修复
- fix(release): reopen CodeBuddy version train (#102)
- fix(local-model-bench): run_agent.sh 的 diff_stat 计入 untracked 新文件
- fix(local-model-bench): 补 WorkBuddy 安装说明（跨仓门禁违规）+ 前向测试预期同步 F 维度
- fix(local-model-bench): regex 判定三态化——any 与 reject 同时命中转 MANUAL

## 维护
- docs(local-model-bench): 维度三加 agent-cli-dispatch 技能交叉引用（接入与纪律以其为真源）
- docs(local-model-bench): 补漏——字段示例注释的温度绑定同步 F 类
- docs(local-model-bench): references 与真源对账修复四处漂移
- chore(train): dev 含 feat（local-model-bench 统计资格），列车提为 minor 1.16.0-SNAPSHOT
- chore(release): open next train after v1.15.0

## v1.15.0 — 2026-08-20

本地模型评测技能：私有题 Markdown 格式支持（知识库内可读可编辑）+ GPU 占用清点与思考依赖性三态评测规范

## 新增
- feat(local-model-bench): 私有题支持 Markdown 格式（知识库内可读可编辑）

## 维护
- chore(train): dev 含 feat（md 题库支持），列车提为 minor 1.15.0-SNAPSHOT
- docs(local-model-bench): 评测前 GPU 占用清点规范 + 思考依赖性三态测试（1.2.1）
- chore(release): open next train after v1.14.0 (#99)

## v1.14.0 — 2026-08-20

dsh 双轨道对齐 DSH_TRACK + profiles 一致性检测 + local-model-bench 增强

## 新增
- feat(ai-cli-upgrade): dsh 双轨道对齐 DSH_TRACK + profiles 版本一致性检测 (2.3.5) (#97)
- feat(local-model-bench): 回填 2026-08-20 实战 8 缺口（1.2.0）
- feat(local-model-bench): 采集缓存命中率 cached_tokens（1.1.0） (#96)

## 维护
- chore(train): dev 含 feat（local-model-bench 增强 + dsh-track），列车提为 minor
- chore(release): open next train after v1.13.0 (#95)

## v1.13.0 — 2026-08-19

新增 soia-env-local-model-bench 本地 LLM 评测技能；ai-cli-upgrade 增 dsh 支持并拆分 providers 架构

## 新增
- feat(ai-cli-upgrade): add DeepSeek Harness (dsh) support (2.3.3) (#91)
- feat(skills): 新增 soia-env-local-model-bench 本地 LLM 评测技能

## 维护
- chore(train): 新技能入列，列车提为 minor（claude/codex 1.13.0-SNAPSHOT，codebuddy 1.4.0-SNAPSHOT）
- refactor(ai-cli-upgrade): split monolithic engine into entry + providers package (#92)
- chore(release): open next train after v1.12.3 (#88)

## v1.12.3 — 2026-08-09

SKILL.md 渐进式披露瘦身（7 技能 ≤200 行/≤10k 字符，细节下沉 references/）+ network-diagnose R6 安全加固

## 修复
- fix(network-diagnose): R6 安全加固——pipe-to-shell 表述三段式化、测试标识符避开密钥前缀模式 (#85)

## 维护
- refactor(skills): SKILL.md 渐进式披露瘦身——7 技能正文 ≤200 行/≤10k 字符，细节下沉 references/ (#86)
- chore(release): open next train after v1.12.2 (#84)

## v1.12.2 — 2026-08-08

ai-cli-upgrade 2.3.1：云鼎安全评估响应——去 pipe-to-shell 字样、标识符避开密钥前缀模式、安全模型披露

## 修复
- fix(ai-cli-upgrade): security hardening per Tencent Yunding assessment (2.3.1) (#82)

## 维护
- chore(release): open next train after v1.12.1 (#81)

## v1.12.1 — 2026-08-08

claude-cli-install 1.0.4 市场上架就绪：能力边界、真机样例、专属测试、境内源提示

## 维护
- docs(claude-cli-install): market readiness — capability boundary, real check sample, exclusive tests, npmmirror hint (#79)
- chore(release): open next train after v1.12.0 (#78)

## v1.12.0 — 2026-08-08

ai-cli-upgrade 2.3.0：原生 Windows 实验性支持（windows-latest 真机契约回归）+ 平台范围声明

## 新增
- feat(ai-cli-upgrade): experimental native Windows support with windows-latest CI regression (#75)

## 维护
- chore(release): promote train to 1.12.0-SNAPSHOT (Windows support = minor) (#76)
- docs(ai-cli-upgrade): declare platform scope — macOS/Linux(WSL) supported, native Windows not yet (#74)
- chore(release): open next train after v1.11.0 (#73)

## v1.11.0 — 2026-08-08

ai-cli-upgrade 2.2.0：契约锁定的 Python 引擎替换 bash，解锁 Red Skill 上架；新增 ~/.opencode/bin 探测回退

## 新增
- feat(ai-cli-upgrade): replace bash engine with contract-locked Python engine (#71)

## 维护
- chore(release): open next train after v1.10.2 (#70)

## v1.10.2 — 2026-08-08

ai-cli-upgrade 市场上架就绪：能力边界、真实样例、专属测试、境内源提示

## 维护
- docs(ai-cli-upgrade): market readiness — capability boundary, real dry-run sample, exclusive test, npmmirror hint (#68)
- chore(release): open next train after v1.10.1 (#67)

## v1.10.1 — 2026-08-08

对齐 codex 版本轨道（v1.10.0 时 codex manifest 停在 1.9.1 的修正补发）；内容与 v1.10.0 一致

## 修复
- fix(release): 对齐 codex 版本轨道至 claude 列车 (1.9.2 -> 1.10.1-SNAPSHOT) (#65)

## 维护
- chore(release): open next train after v1.10.0 (#64)

## v1.10.0 — 2026-08-08

network-diagnose 1.4.2：本机运行时分类盘点（23 项六类）与 AI CLI 可安装性推导、npm 渠道 Node 版本门槛、安装章节规范位；environment-setup 1.6.5 接入运行时盘点

## 新增
- feat(network-diagnose): 新增本机运行时分类盘点与 AI CLI 可安装性推导 (#60)

## 修复
- fix(network-diagnose): 安装命令移入「依赖与安装」节（发版体检要求） (#62)
- fix(network-diagnose): 补齐 npm 渠道的 Node 版本门槛,并修 README 覆盖漏洞 (#61)

## 维护
- chore(release): feat 在列,版本列车提为 next-minor
- chore(release): open next train after release

## v1.9.0 — 2026-08-06

network-diagnose providers 扩展、安装章节三宿主覆盖、config 归位 assets

## 新增
- feat(network-diagnose): 境内基准/镜像三组对照与判定矩阵、真实输出样例、测试双布局 (#56)
- feat(env): add pi install skill and deepcode/pi upgrade support (#46)

## 修复
- fix(metadata): real timestamps from git history (was 00:00:00) (#47)
- fix(pi-install): correct metadata header — real creator/time

## 维护
- chore(release): feat 在列,版本列车提为 next-minor
- docs(network-diagnose): 补「不负责什么」能力边界节（就绪门禁 R1） (#57)
- chore(skills): config.example.yml 归位到 assets/ (#55)
- chore(skills): 补上安装章节改动遗漏的版本 bump (#54)
- docs(skills): 安装章节补齐三个一等宿主 (#53)
- docs(agents): branch off main; releases fast-forward dev onto main (#52)
- chore(sync): merge main into dev and switch train to patch level
- chore(release): open next train after v1.8.0 (#50)
- release: finalize v1.8.0 (drop -SNAPSHOT) (#48)
- docs(changelog): seed with current release baseline (#45)
- docs(agents): SNAPSHOT version rule for dev branch (#44)
- chore(release): open dev branch — audit on dev, version train 1.8.0-SNAPSHOT

## v1.8.0 — 2026-08-03

env v1.8.0: pi-cli-install skill + deepcode/pi upgrade support (2.1.0)

## 新增
- feat(env): add pi install skill and deepcode/pi upgrade support (#46)

## 修复
- fix(metadata): real timestamps from git history (was 00:00:00) (#47)
- fix(pi-install): correct metadata header — real creator/time

## 维护
- docs(changelog): seed with current release baseline (#45)
- docs(agents): SNAPSHOT version rule for dev branch (#44)
- chore(release): open dev branch — audit on dev, version train 1.8.0-SNAPSHOT

## v1.7.1 — 2026-08-01

面向新手的 AI CLI 与运行时安装、网络诊断与环境验证。
