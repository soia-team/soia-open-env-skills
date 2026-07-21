# soia-open-env-skills

[中文](README.md) | English

Beginner-friendly SOIA skills for network diagnosis, managed-storage cleanup, and safe installation and verification of Codex, Claude Code, Qoder, Google Antigravity, OpenCode, Kimi Code, Deep Code, WorkBuddy, Node.js, Python, and related development prerequisites.

The Deep Code skill targets the community-maintained `lessweb/deepcode-cli`, an open-source agent CLI optimized for DeepSeek models; it does not present that project as an official DeepSeek CLI or confuse it with other products named DeepCode.

The repository keeps environment readiness separate from PKM and private SOIA governance. It produces portable readiness summaries so the three skill libraries can cooperate without copying private state.

Storage cleanup is plan-gated: an initial request authorizes read-only scanning and planning only. Deletion requires a fresh explicit customer approval after the candidate summary and irreversible-risk warning are shown.

Version discovery is read-only by default. Skills update an installed tool only after the customer explicitly asks for the latest version; ambiguous update requests stop after reporting versions. Authorized installs and updates publish live phase status and append redacted progress events to private user state.

Install one skill from the pushed repository:

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-environment-setup -y
```

Install all skills:

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -y
```

See [AGENTS.md](./AGENTS.md), [SKILL_SPEC.md](./SKILL_SPEC.md), and
[CONTRIBUTING.md](./CONTRIBUTING.md) for the public authoring, safety, and PR rules.
