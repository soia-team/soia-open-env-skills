# Official Sources — soia-env-soia-skills-install

## SOIA 开源技能市场

| 项目 | 地址 |
|---|---|
| 元仓（市场入口） | https://github.com/soia-team/soia-open-skills |
| Claude 市场配置 | `.claude-plugin/marketplace.json` in soia-open-skills |
| Codex 市场配置 | `.agents/plugins/marketplace.json` in soia-open-skills |

## 接入命令

以下命令只是已选计划的执行候选，不能绕过 selection/confirmation gate。先用当前 CLI 的 `--help` 验证参数，再按计划列出的宿主和目标运行。

### 项目级单技能（npx）
```bash
# 不带 -g 表示项目范围；宿主和技能必须来自已确认计划
npx skills add <skill-repo> --agent <agent> --skill <skill>
```

### 全局单技能（npx）
```bash
npx skills add <skill-repo> --global --agent <agent> --skill <skill>
```

### Claude Code
```bash
# 用户级域插件；不是项目安装
claude plugin marketplace add soia-team/soia-open-skills
claude plugin install <domain>@soia
claude plugin update <domain>@soia   # 已有版本时
```

### Codex
```bash
# 用户级域插件；不是项目安装
codex plugin marketplace add soia-team/soia-open-skills
codex plugin add <domain>@soia
```

### WorkBuddy（无 CLI，脚本代劳）
```bash
python3 <soia-open-skills>/skills/soia-meta-skill-release/scripts/install_workbuddy_experts.py --dry-run
python3 <soia-open-skills>/skills/soia-meta-skill-release/scripts/install_workbuddy_experts.py
```
该脚本写用户级专家目录；不支持项目范围。执行前必须 dry-run 和确认。

## 开源域插件

使用[插件目录](plugins.md)的现行映射；设计能力已并入 dev。既有旧插件的迁移或卸载须另有明确目标和影响确认。

## 已知约束

- Codex 若因旧克隆导致市场更新失败，先核实当前 CLI 行为和精确缓存目录；只有证明确为可丢弃缓存、展示影响并获确认后才清理，不默认删除缓存。
- Claude 的 `plugin details <name>` 对私有市场要带后缀 `@soia`，不带会报「not installed」。
- WorkBuddy 专家安装后**必须重启应用**，否则不显示。
- `soia-meta-skill-release` 的 `install_workbuddy_experts.py` 要求 Python 3 且需找到 soia-open-skills checkout 路径（通过 `SOIA_SKILL_REPOS_ROOT` 或 `--repo-dir` 传入）。
