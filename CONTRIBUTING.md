# Contributing to soia-open-env-tools-skills

1. Fork the repository or create a short-lived branch from `main`.
2. Read [SKILL_SPEC.md](./SKILL_SPEC.md) and [AGENTS.md](./AGENTS.md).
3. Start a skill from `templates/skill-template/` or use the skill creator initializer.
4. Keep provider/version facts in the skill's `references/` and keep public examples free of secrets and personal paths.
5. Add a fixture or forward test for deterministic scripts and document a safe manual check.
6. Regenerate `skills/README.md` instead of editing it by hand.
7. Run the repository validation commands.
8. Open a PR to `main`; the `audit` workflow must pass before merge.

For environment changes, explain the detected OS/architecture, official source,
requested permissions, rollback path, and verification evidence. Do not silently
change PATH, shell profiles, proxies, DNS, certificates, or system-wide tools.
