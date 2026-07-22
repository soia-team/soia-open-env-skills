# THIRD_PARTY_NOTICES

> Last updated: 2026-07-22
> License values are metadata snapshots. Recheck the upstream source before reuse.

## Managed external CLIs

| Upstream | License snapshot | Used by | Relationship |
|---|---|---|---|
| [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) | Apache-2.0 | `soia-env-ai-cli-upgrade` | User-installed external AI CLI that the skill audits or upgrades. |
| [google-antigravity/antigravity-cli](https://github.com/google-antigravity/antigravity-cli) | NOASSERTION | `soia-env-ai-cli-upgrade`, `soia-env-antigravity-cli-install` | User-installed external CLI managed at runtime; no code is copied. |

Other supported user-installed AI CLIs are managed tools rather than dependencies distributed by this repository and are not enumerated here.

## Maintenance

- NOASSERTION upstreams remain external tools; do not copy their code.
- Record newly documented upstream links or install commands here.
