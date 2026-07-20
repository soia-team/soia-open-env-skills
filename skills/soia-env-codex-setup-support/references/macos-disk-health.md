# macOS 磁盘健康检查边界

## 安装

已有 Homebrew 时安装 `smartmontools`：

```bash
brew install smartmontools
```

如果 `brew` 不存在，先提示客户从 Homebrew 官方页面确认安装方式；不要在对话中执行未知的远程安装脚本。

## 设备确认

`/dev/disk0` 是常见示例，不保证对应目标物理设备。先只读查看：

```bash
diskutil list
smartctl --scan-open
```

根据扫描结果选择设备，再读取：

```bash
sudo smartctl -a <确认后的设备>
```

密码只在系统授权提示中输入。技能不得收集密码，也不得把完整 `smartctl -a` 输出上传到外部服务。

## 关键字段

| 字段 | 用途 | 安全判读 |
|---|---|---|
| `SMART overall-health` | 设备自报健康结果 | `PASSED` 只是一个信号，不是全面诊断 |
| `Percentage Used` | 标称寿命消耗比例 | 高值或达到 100% 时备份并评估更换 |
| `Available Spare` | 备用块余量 | 过低或持续下降时预警 |
| `Data Units Written` | 累计写入量 | 用于识别长期写入压力，不直接换算剩余寿命 |
| `Temperature` | 当前温度 | 异常升高时结合散热、负载和日志判断 |

有些 Apple 内置 SSD、USB 转接设备或厂商实现不提供标准 SMART 字段。遇到“不支持”“没有字段”“权限不足”时，结论应是 `unsupported_or_incomplete`，不是“磁盘坏了”。可改用“磁盘工具”、`diskutil info` 和 Apple Diagnostics 做进一步确认。

## 禁止项

诊断技能不自动执行长测、修复、抹盘、格式化、分区、固件升级、删除文件或清理缓存。先备份，再把硬件更换建议交给客户确认。
