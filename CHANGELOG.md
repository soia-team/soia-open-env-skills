# Changelog

本文件由 soia-meta-skill-release 在每次正式发版时自动更新，与 GitHub Release 同源；
更早的版本演进见 git 提交历史与 GitHub Releases。

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
