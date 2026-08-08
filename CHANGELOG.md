# Changelog

本文件由 soia-meta-skill-release 在每次正式发版时自动更新，与 GitHub Release 同源；
更早的版本演进见 git 提交历史与 GitHub Releases。

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
