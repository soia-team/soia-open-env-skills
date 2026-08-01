# Official Sources — soia-env-soia-skills-install

## SOIA 开源技能市场

| 项目 | 地址 |
|---|---|
| 元仓（市场入口） | https://github.com/soia-team/soia-open-skills |
| Claude 市场配置 | `.claude-plugin/marketplace.json` in soia-open-skills |
| Codex 市场配置 | `.agents/plugins/marketplace.json` in soia-open-skills |

## 接入命令

### Claude Code
```bash
claude plugin marketplace add soia-team/soia-open-skills
claude plugin install <domain>@soia
claude plugin update <domain>@soia   # 已有版本时
```

### Codex
```bash
rm -rf ~/.codex/.tmp/marketplaces/soia   # 必须清暂存，否则拉旧缓存
codex plugin marketplace add soia-team/soia-open-skills
codex plugin add <domain>@soia
```

### WorkBuddy（无 CLI，脚本代劳）
```bash
python3 <soia-open-skills>/skills/soia-meta-skill-release/scripts/install_workbuddy_experts.py --dry-run
python3 <soia-open-skills>/skills/soia-meta-skill-release/scripts/install_workbuddy_experts.py
```

## 8 个开源域插件

| 插件名 | 域仓 |
|---|---|
| soia-meta | soia-open-skills |
| soia-dev | soia-open-dev-skills |
| soia-dev-design | soia-open-dev-design-skills |
| soia-pkm-vault | soia-open-pkm-vault-skills |
| soia-media-content | soia-open-media-content-skills |
| soia-cwork-office | soia-open-cwork-office-skills |
| soia-env | soia-open-env-skills |
| soia-edu-course | soia-open-edu-course-skills |

## 已知约束

- Codex 的 `plugin marketplace add` 会复用旧克隆，必须先 `rm -rf ~/.codex/.tmp/marketplaces/soia`。
- Claude 的 `plugin details <name>` 对私有市场要带后缀 `@soia`，不带会报「not installed」。
- WorkBuddy 专家安装后**必须重启应用**，否则不显示。
- `soia-meta-skill-release` 的 `install_workbuddy_experts.py` 要求 Python 3 且需找到 soia-open-skills checkout 路径（通过 `SOIA_SKILL_REPOS_ROOT` 或 `--repo-dir` 传入）。
