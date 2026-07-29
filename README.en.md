# SOIA Environment Skills

[中文](README.md) · English

Beginner-friendly skills that turn a machine which "can't quite work yet" into an environment other skills can rely on: network diagnosis, runtime installation, AI CLI setup, login verification, and safe storage cleanup.

## What this is

`soia-open-env-skills` is SOIA's public source of truth for environment skills. It gets a machine ready and hands off a redacted readiness summary:

```text
Network reachability
    ↓
Base runtimes (Node.js / Python / npm / pip)
    ↓
Desktop apps and agent CLIs
    ↓
First login, API configuration, real usability verification
    ↓
Redacted readiness summary
    ↓
soia-open-skills / soia-private-skills
```

This repository owns environment readiness only. It does not own vault content, cloud-drive workflows, or SOIA internal governance.

### When to use it

- "Set up this Mac/Windows/Linux machine from scratch."
- "Install Codex, Claude Code, OpenCode, Kimi, or Deep Code CLI."
- "Find out why the network, npm, pip, or an official installer keeps failing."
- "Check whether a tool is actually logged in and usable — not just that the command exists."
- "Measure what SOIA-managed directories consume, then clean the cache once I confirm the risk."

### What it does not do

- Does not treat `ChatGPT.app` as a standalone Codex CLI, and never conflates desktop and CLI versions, logins, or updates.
- Does not treat "the command exists" or "a default config path is present" as "logged in, configured, and able to call a model".
- Does not store API keys, passwords, cookies, tokens, or private customer configuration.
- Does not auto-upgrade installed tools. An update runs only when you explicitly ask for the latest version.
- Does not copy skills from `soia-open-skills` or `soia-private-skills`.

## Where to start

### Recommended entry points

| Goal | Start with | Done when |
|---|---|---|
| Build an environment from scratch | `soia-env-environment-setup` | Network, runtimes, target tools, and first-run config each verified |
| Diagnose the network first | `soia-env-network-diagnose` | DNS, HTTPS, proxy, certificates, and download sources have evidence |
| Install Codex | `soia-env-codex-install` | Standalone CLI and ChatGPT.app kept separate; login verified independently |
| Install Deep Code | `soia-env-deepcode-cli-install` | DeepSeek API key configured locally and a real request verified |
| Install any other agent CLI | The matching `soia-env-*-cli-install` | Command, source, version, config/credentials, and first login each confirmed |
| Check disk usage | `soia-env-storage-cleanup` | Scan and plan first; deletion only after a second explicit authorization |

### How one request is handled

1. Detect OS, architecture, shell, package manager, existing versions, and the actual installation source.
2. Check network and dependencies read-only, then show the install or configuration plan.
3. Install missing tools after you authorize. Installing an existing tool is not authorization to update it.
4. Start the official login flow for tools that need it; you complete authorization in the vendor's own UI.
5. Verify that config directories and files really exist, then run one side-effect-free startup or auth check.
6. Report current state, version, install method, directories, timestamp, and outcome in a fixed table.

## Skill catalog

The full generated catalog is in [skills/README.md](./skills/README.md). 15 skills are published, grouped below.

> **Status legend**: ✅ usable right after install, no extra credentials or client login · 🟡 you must still request an API key or complete a separate client login
> **Dependencies** come from each skill's `dependencies` frontmatter; all hard dependencies stay inside this repository — see [Three-repository cooperation](#three-repository-cooperation).

### Orchestration and diagnosis

Core value: before installing anything, establish what the machine is actually missing and whether the network works — that is what keeps every later step from being wasted.

| Skill | Summary | Status | Dependencies |
|---|---|:---:|---|
| [`soia-env-environment-setup`](./skills/soia-env-environment-setup/) | Step-by-step orchestration from network to runtimes, CLIs, and desktop tools, ending with a downstream readiness summary | ✅ | Hard: `soia-env-network-diagnose`; optionally enables the other 12 environment skills by goal |
| [`soia-env-network-diagnose`](./skills/soia-env-network-diagnose/) | Read-only diagnosis of DNS, HTTPS, proxy, certificates, and official-source reachability | ✅ | None |
| [`soia-env-codex-setup-support`](./skills/soia-env-codex-setup-support/) | Triage ChatGPT.app/Codex desktop capability, standalone CLI, login, log write amplification, and disk health | ✅ | Optional: `soia-env-network-diagnose`, `soia-env-node-install`, `soia-env-codex-install` |
| [`soia-env-storage-cleanup`](./skills/soia-env-storage-cleanup/) | Measure managed directories, produce a cleanup plan with expiry conditions and risk, then clean safely once authorized | ✅ | No skill dependency (needs Python 3.10+) |

### Base runtimes

Core value: agent CLIs and most development tooling ultimately land on Node.js or Python — these two skills are the foundation nearly every later install stands on.

| Skill | Summary | Status | Dependencies |
|---|---|:---:|---|
| [`soia-env-node-install`](./skills/soia-env-node-install/) | Check, install, and verify Node.js, npm, and PATH; never updates on its own | ✅ | Optional: `soia-env-network-diagnose` |
| [`soia-env-python-install`](./skills/soia-env-python-install/) | Check, install, and verify Python, pip, and virtual environments; prefers `python -m pip` | ✅ | Optional: `soia-env-network-diagnose` |

### Agent CLIs

Core value: every coding-agent CLI has its own install channel, login flow, and "the command exists but it doesn't work" trap. These skills close those traps one by one instead of leaving you to hit them.

| Skill | Summary | Status | Dependencies | First-run verification |
|---|---|:---:|---|---|
| [`soia-env-ai-cli-upgrade`](./skills/soia-env-ai-cli-upgrade/) | Batch-audit and upgrade several installed AI CLIs; aimed at advanced maintenance | ✅ | None | Dry-run version audit plus per-tool upgrade results |
| [`soia-env-codex-install`](./skills/soia-env-codex-install/) | Install, verify, and — on explicit request — update the OpenAI Codex CLI, identifying the source actually in effect | ✅ | Hard: `soia-env-ai-cli-upgrade` (this repo); optional: `soia-env-node-install`, `soia-env-network-diagnose` | `codex --login`, verified separately from ChatGPT.app |
| [`soia-env-claude-cli-install`](./skills/soia-env-claude-cli-install/) | Check, install, log in, and — on explicit request — update the Anthropic Claude Code CLI | ✅ | Optional: `soia-env-node-install`, `soia-env-network-diagnose` | Official browser login plus `claude doctor` |
| [`soia-env-qoder-cli-install`](./skills/soia-env-qoder-cli-install/) | Check, install, log in, and — on explicit request — update the Qoder CLI | ✅ | Optional: `soia-env-node-install`, `soia-env-network-diagnose` | `/login` browser authorization or the official PAT flow |
| [`soia-env-antigravity-cli-install`](./skills/soia-env-antigravity-cli-install/) | Check, install, log in, migrate, and — on explicit request — update the Google Antigravity CLI (`agy`), distinguishing `agy` from the legacy Gemini CLI | ✅ | Optional: `soia-env-network-diagnose` | Official Google login; never treats `gemini` as `agy` |
| [`soia-env-opencode-cli-install`](./skills/soia-env-opencode-cli-install/) | Check, install, log in, configure, and — on explicit request — update the open-source OpenCode CLI | ✅ | Optional: `soia-env-node-install`, `soia-env-network-diagnose` | `opencode auth login` and `auth list` |
| [`soia-env-kimi-cli-install`](./skills/soia-env-kimi-cli-install/) | Check, install, log in, and — on explicit request — update the Moonshot AI Kimi Code CLI | ✅ | Optional: `soia-env-node-install`, `soia-env-network-diagnose` | `kimi login` or the TUI `/login` |
| [`soia-env-deepcode-cli-install`](./skills/soia-env-deepcode-cli-install/) | Check, install, configure, and — on explicit request — update the open-source Deep Code agent CLI optimized for DeepSeek (`lessweb/deepcode-cli`) | 🟡 you must request an API key on the official DeepSeek platform | Hard: `soia-env-node-install` (Node.js 22+); optional: `soia-env-network-diagnose` | `~/.deepcode/settings.json` plus a real DeepSeek API call |

### Desktop tools

Core value: not every customer tool is a CLI. This group applies the same "verify the source, verify the first login" standard to desktop clients.

| Skill | Summary | Status | Dependencies |
|---|---|:---:|---|
| [`soia-env-workbuddy-install`](./skills/soia-env-workbuddy-install/) | Install from the official WorkBuddy package, then verify signature, launch, and login | 🟡 login happens inside the desktop client | Optional: `soia-env-network-diagnose` |

## First-run configuration is not "installed"

This is the state boundary the whole repository follows:

```text
the command exists
  ≠ installed from the right source
  ≠ configuration created
  ≠ login / API key completed
  ≠ a real request succeeds
```

Every CLI skill checks these separately:

- `config_status` — whether the config or state directory really exists;
- `config_file_status` — whether the known config file really exists;
- `credential_status` — whether credentials are found for tools with their own credential file;
- whether first launch, browser authorization, or a side-effect-free model call actually succeeds.

For example, a first Deep Code run may create part of `~/.deepcode` runtime state, but it will not generate a `settings.json` containing your API key. You create the key at [DeepSeek API Keys](https://platform.deepseek.com/api_keys), write it into `~/.deepcode/settings.json` on your machine, and the agent then verifies it. That is exactly why `soia-env-deepcode-cli-install` is marked 🟡 rather than ✅ in the catalog above.

## Five skills up close

Five of the 15 skills, chosen because each represents a different way of working. A minimal example and its typical output lower the barrier to the first run.

### soia-env-environment-setup

The entry point for building an environment from scratch. It only decides the order and aggregates downstream results — it never reimplements the individual install logic.

```text
get this machine ready for Codex
set up my dev environment from scratch
```

**Typical output**: first a customer-facing status list with fixed columns (skill / state / current version / latest version / runtime status / updated at / outcome), one row per target; then a secret-free YAML summary (`schema_version`, `os`, `arch`, `tools`, `network`, `blockers`, `next_handoff`) that downstream skills such as `soia-open-skills` can consume.

### soia-env-network-diagnose

Read-only diagnosis, and the first stop whenever an install skill stalls. It never modifies proxies, DNS, certificates, or the firewall.

```bash
python3 scripts/probe_endpoints.py --url https://nodejs.org/en --url https://www.python.org/downloads/ --json
```

**Typical output**: a fixed seven-column status table whose `outcome` states either "safe to continue installing" or "needs attention: `<error class>`". Error classes are limited to `dns_failed` / `tls_failed` / `timeout` / `http_error` / `proxy_required` / `reachable` — it never concludes "the network is down" from a single probe.

### soia-env-codex-install

Distinguishes "ChatGPT.app desktop" from "the standalone Codex CLI"; the state boundaries of this repository show up most completely here.

```bash
python3 scripts/inspect_installation.py --json
TOOLS=codex DRY_RUN=1 bash ~/.agents/skills/soia-env-ai-cli-upgrade/scripts/upgrade-ai-clis.sh
```

**Typical output**: the ten-column status table, one row for `Codex CLI` only. When not logged in, `outcome` says "waiting for first login" and offers `codex --login` — the presence of a `~/.codex` directory is never taken as proof of login.

### soia-env-deepcode-cli-install

Demonstrates the 🟡 class of skill, where you must obtain an API key from an external platform.

```bash
python3 scripts/inspect_cli.py --json
npm install -g @vegamo/deepcode-cli
```

**Typical output**: the same ten-column table. While `config_file_status` shows nothing created, `outcome` reads "waiting for first-run configuration" and links [DeepSeek API Keys](https://platform.deepseek.com/api_keys) plus the local `~/.deepcode/settings.json` path — a command that merely runs is never reported as healthy.

### soia-env-storage-cleanup

Demonstrates the mandatory authorization flow for deletions: scan, plan, and clean are three separate stages, and none may be skipped on your behalf.

```bash
python3 scripts/storage_cleanup.py scan --json
python3 scripts/storage_cleanup.py plan --json
# only after you see the risk notice and reply "confirm deletion per plan <plan_id>":
python3 scripts/storage_cleanup.py clean --plan <plan-path> --confirmed-plan-id <plan-id> --execute --json
python3 scripts/storage_cleanup.py verify --receipt <receipt-path> --json
```

**Typical output**: first the size, reclaimable size, and candidate count for four managed data classes (config / audit state / cache / temporary files), then a `plan_id` with an irreversible-risk notice. Deletion happens only after you confirm that specific `plan_id`, and a `verify` run afterwards must confirm the space actually reclaimed — an exit code of 0 is not a substitute for that check.

## Install

Installing the whole domain plugin is recommended — it brings every skill in this repo:

```bash
claude plugin marketplace add soia-team/soia-open-skills
```

```bash
claude plugin install soia-env@soia
```

For Codex:

```bash
codex plugin marketplace add soia-team/soia-open-skills
codex plugin add soia-env@soia
```

For a single skill you can use the npx route. Note the skill lands in the shared source `~/.agents/skills`; if the plugin is installed too, the same skill shows up twice and the two copies drift apart — pick one:

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s <skill-name> -y
```

## Trigger phrases

Once installed, just speak naturally — the agent routes to a skill by these phrases (the full trigger list lives in each skill's `SKILL.md` `description`).

> Trigger phrases are listed in the language the skill actually matches on. Some are Chinese because that is what these skills were written to recognize; describing the same intent in English works too — the agent matches on meaning, not on the literal string.

| You say | Skill |
|---|---|
| `set up my dev environment` / `install tools from scratch` | `soia-env-environment-setup` |
| `network is down` / `download failed` / `npm/pip timeout` / `certificate error` | `soia-env-network-diagnose` |
| `Codex won't open` / `Codex is slow` / `check disk health` | `soia-env-codex-setup-support` |
| `check SOIA disk usage` / `clean temporary files` / `free disk space` | `soia-env-storage-cleanup` |
| `install Node` / `node: command not found` / `npm timeout` | `soia-env-node-install` |
| `install Python` / `python: command not found` / `pip doesn't work` | `soia-env-python-install` |
| `install Codex` / `update Codex to latest` / `Codex login` | `soia-env-codex-install` |
| `install Claude CLI` / `claude: command not found` / `Claude login` | `soia-env-claude-cli-install` |
| `install Qoder CLI` / `qodercli not found` / `Qoder login` | `soia-env-qoder-cli-install` |
| `install agy` / `migrate from Gemini CLI` / `agy login` | `soia-env-antigravity-cli-install` |
| `install OpenCode` / `opencode not found` / `OpenCode login` | `soia-env-opencode-cli-install` |
| `install Kimi CLI` / `kimi not found` / `Kimi login` | `soia-env-kimi-cli-install` |
| `install DeepCode` / `deepcode not found` / `configure DeepSeek agent` | `soia-env-deepcode-cli-install` |
| `install WorkBuddy` / `WorkBuddy won't open` | `soia-env-workbuddy-install` |

## Repository layout

This repository uses a single skill prefix, `soia-env-`, so it has no separate naming section; cross-domain naming rules live in [SKILL_SPEC.md](./SKILL_SPEC.md).

```text
soia-open-env-skills/
├── AGENTS.md
├── README.md · README.en.md
├── LICENSE · SECURITY.md
├── SKILL_SPEC.md                    ← skill structure and frontmatter rules
├── DATA_STORAGE_SPEC.md             ← credential / state / cache / temp boundaries
├── requirements-dev.txt
├── scripts/
│   ├── audit_skills.py              ← public skill audit (naming, frontmatter, secrets, links)
│   ├── audit_skill_output.py        ← validates the machine-readable readiness summary
│   ├── generate_skill_catalog.py    ← generates skills/README.md from SKILL.md files
│   └── check_readme_coverage.py     ← checks this file mentions every skill name
├── templates/skill-template/        ← starting point for a new skill
├── tests/                           ← unittest cases covering scripts and table formats
└── skills/                          ← npx skills scans this directory
    ├── README.md                          ← generated catalog, do not edit by hand
    └── soia-env-*/                        ← one directory per skill
```

## Three-repository cooperation

| Repository | Visibility | Owns |
|---|---|---|
| [`soia-open-env-skills`](https://github.com/soia-team/soia-open-env-skills) | Public | Network, runtimes, desktop tools, agent CLIs, safe cleanup |
| [`soia-open-skills`](https://github.com/soia-team/soia-open-skills) | Public | Portal, specifications, and the domain plugins for vaults, media, dev, and collaboration |
| [`soia-private-skills`](https://github.com/soia-team/soia-private-skills) | Private | SOIA internal governance, audit, development, and execution |

### Hard dependencies between skills

Most skills here are independent. After the AI CLI upgrade skill was absorbed into this repository, every hard dependency lives inside it:

| Skill | Hard dependency | Location | Why |
|---|---|---|---|
| `soia-env-codex-install` | `soia-env-ai-cli-upgrade` | This repo | One place performs Codex version audit and same-channel updates; single-tool installers do not reimplement upgrade logic |
| `soia-env-environment-setup` | `soia-env-network-diagnose` | This repo | Confirm reachability before orchestration begins |
| `soia-env-deepcode-cli-install` | `soia-env-node-install` | This repo | Deep Code CLI requires Node.js 22+ |

Environment setup must end with a machine-readable readiness summary that a downstream skill can consume. Do not copy or modify skills from the other two repositories — check availability, state the dependency, and pass only portable output such as OS, tool, version, and status.

## Permissions and safety boundaries

- Read-only checks write nothing by default. Show the plan before installing, launching a login, changing PATH or shell profiles, using administrator privileges, or altering network settings.
- Version discovery only reports. When "update" is ambiguous, report current and latest versions and stop; run an updater only on an explicit "update to the latest version".
- Official scripts are downloaded into a per-run temporary directory and their source verified — never pipe an unchecked network response straight into a shell.
- You should not need to operate a terminal. You handle official browser login, CAPTCHAs, OS security prompts, and product consent.
- API keys, passwords, cookies, tokens, and sessions stay in vendor login state, the OS keychain, or a local location you approve.
- Status receipts never record full command text, credentials, response bodies, accounts, or your private absolute paths.
- Deletion is irreversible: cleanup scans first, then shows an immutable plan with candidates, retain/clean conditions, and risk. You must authorize a specific `plan_id` again before anything is removed.

Full rules are in [DATA_STORAGE_SPEC.md](./DATA_STORAGE_SPEC.md).

## State, records, and storage

Every customer-visible install receipt uses one fixed table:

| Skill | State | Current version | Latest version | Runtime status | Install method | Install directory | Config directory | Updated at | Outcome |
|---|---|---|---|---|---|---|---|---|---|
| `<target skill>` | `<installed/not installed/blocked>` | `<version>` | `<version/unavailable>` | `<ok/error/unverified>` | `<source>` | `<directory>` | `<directory/unavailable>` | `<RFC3339 with timezone>` | `<result>` |

When a skill genuinely changes the machine it also records checking, planning/confirmation, install or update, verification, and the terminal state in real time. Read-only version checks create no progress state. Config, audit state, cache, temporary data, and cleanup conditions all follow [DATA_STORAGE_SPEC.md](./DATA_STORAGE_SPEC.md).

## Official sources

Skills prefer the vendor's own entry points. Version facts and alternative sources live in each skill's `references/official-sources.md`:

- [OpenAI Codex CLI](https://help.openai.com/en/articles/11381614-api-codex-cli-and-sign-in-with-chatgpt)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/getting-started)
- [Qoder CLI](https://docs.qoder.com/en/cli/quick-start)
- [Google Antigravity CLI](https://codelabs.developers.google.com/antigravity-cli-hands-on)
- [OpenCode](https://opencode.ai/docs)
- [Kimi Code CLI](https://www.kimi.com/code/docs/kimi-code-cli/guides/getting-started)
- [DeepSeek API](https://api-docs.deepseek.com/)
- [Deep Code CLI upstream](https://github.com/lessweb/deepcode-cli)
- [WorkBuddy](https://www.workbuddy.cn/)
- [Node.js](https://nodejs.org/en)
- [Python](https://www.python.org/downloads/)

The Deep Code skill targets the community-maintained `lessweb/deepcode-cli`, an open-source agent CLI optimized for DeepSeek models. It does not present that project as an official DeepSeek CLI, nor confuse it with other products named DeepCode.

## Acknowledgements

- `soia-env-ai-cli-upgrade` carries version audit and upgrade logic for several AI CLIs in one place; single-tool installers only handle their own install, login, and usability verification, and never reimplement the batch updater.
- Install and login flows follow each vendor's own documentation, linked under [Official sources](#official-sources). This repository does not mirror or rewrite vendor installation logic.

## Validate & contribute

Maintainers should read first:

- [AGENTS.md](./AGENTS.md) — repository boundaries, permissions, and release flow;
- [SKILL_SPEC.md](./SKILL_SPEC.md) — skill structure and frontmatter rules;
- [DATA_STORAGE_SPEC.md](./DATA_STORAGE_SPEC.md) — private data, intermediate data, and cleanup rules;
- [CONTRIBUTING.md](https://github.com/soia-team/soia-open-skills/blob/main/CONTRIBUTING.md) — contribution, audit, and PR flow.

Run before committing:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/generate_skill_catalog.py --check
python3 scripts/audit_skills.py --strict
git diff --check
```

## License

MIT License — see [LICENSE](./LICENSE).
