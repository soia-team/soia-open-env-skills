# Changelog

本文件由 soia-meta-skill-release 在每次正式发版时自动更新，与 GitHub Release 同源；
更早的版本演进见 git 提交历史与 GitHub Releases。

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
