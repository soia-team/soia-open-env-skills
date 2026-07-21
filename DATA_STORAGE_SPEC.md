# Private Data and Intermediate Storage Spec

This repository publishes public, beginner-facing environment skills. The
skills may inspect or change a customer's machine, but must not turn the public
repository, a customer-readable report, or an ordinary config file into a
credential store.

## Storage classes

| Class | What belongs here | Default location | Retention |
|---|---|---|---|
| Provider credentials | tokens, cookies, refresh tokens, session material | provider-owned login store or OS keychain | controlled by the provider |
| Non-secret config | preferences, provider name, feature flags, user-selected paths | user config directory | until the user removes it |
| Audit state | redacted receipts for machine-changing work | user state directory | bounded and rotated |
| Cache | downloaded metadata and reproducible derived data | user cache directory | safe to delete |
| Temporary data | per-run downloads, extracts, probes, and conversion files | OS temporary directory | remove on success and failure |
| Deliverables | reports or files the customer asked to keep | customer-selected output directory | controlled by the customer |

Read-only skills should stay stateless by default: print a redacted result and
write nothing unless the customer asks for a saved report.

## Canonical locations

Use portable path APIs instead of string-concatenating a home directory.
`templates/skill-template/scripts/resolve_storage.py` is the reference
implementation.

| Purpose | Linux / Unix default | macOS default | Windows default |
|---|---|---|---|
| Config | `${XDG_CONFIG_HOME:-~/.config}/soia-skills/soia-open-env-skills/...` | same unless the host integration deliberately uses the native app-support directory | `%APPDATA%\soia-skills\soia-open-env-skills\...` |
| State | `${XDG_STATE_HOME:-~/.local/state}/soia-skills/soia-open-env-skills/...` | same | `%LOCALAPPDATA%\soia-skills\soia-open-env-skills\state\...` |
| Cache | `${XDG_CACHE_HOME:-~/.cache}/soia-skills/soia-open-env-skills/...` | `~/Library/Caches/soia-skills/soia-open-env-skills/...` | `%LOCALAPPDATA%\soia-skills\soia-open-env-skills\Cache\...` |
| Temporary | OS temporary directory under a per-run subdirectory | OS temporary directory under a per-run subdirectory | OS temporary directory under a per-run subdirectory |

The following environment variables may override the SOIA roots:

```text
SOIA_SKILLS_CONFIG_HOME
SOIA_SKILLS_STATE_HOME
SOIA_SKILLS_CACHE_HOME
SOIA_SKILLS_TEMP_HOME
```

These variables name directories, not secret values.

## Credentials and private information

1. Prefer an official provider login command, browser authorization flow, or OS
   keychain. Store only a provider/profile identifier in SOIA config.
2. If a provider supports only a credential file, leave it in the provider's
   documented location and restrict it to the current user. The skill may check
   whether the file exists, but must not print or copy its contents.
3. Do not put passwords, tokens, cookies, session strings, private keys, or
   authorization headers in `config.yml`, CLI arguments, reports, logs, or
   committed fixtures.
4. Environment variables are a compatibility fallback, not the preferred
   long-lived secret store: process listings, crash dumps, or debug logging can
   expose them.
5. Redact credentials, usernames, account identifiers, query strings, local
   private paths, and response bodies before producing logs or receipts.

## Intermediate data lifecycle

- Audit state is allowed only when a machine-changing action needs traceability.
  Keep the action, result, tool/version, and timestamp; omit command output that
  may contain private data. Rotate or bound retained receipts.
- Authorized installations and updates append one JSONL event per phase under
  the owning skill's state directory. Events contain only `schema_version`,
  opaque `run_id`, skill, action, stage, status, recorder-generated,
  timezone-aware `checked_at`,
  whether the customer explicitly requested the latest version, and a fixed
  privacy-safe `result_code`. The progress store does not accept free-form
  result text. Do not store raw commands, environment dumps, usernames, private
  absolute paths, download URLs with query strings, or provider responses.
- A machine-changing run records at least checking, planning or waiting for
  confirmation, installing/updating, verifying, and completed/failed/blocked.
  The Agent must call the recorder and show each transition before or immediately
  after that real phase happens; writing all events at the end is not sufficient.
  The recorder owns event timestamps, rejects caller-supplied timestamps, and
  does not expose the private record path in customer-facing JSON.
- Read-only version discovery, diagnostics, and "is an update available?"
  requests do not create progress state. A generic update request remains a
  read-only version report and does not create progress state; it must not enter
  the updating stage without an explicit latest request.
- Cache must be reproducible and safe to remove. Never require a cached token to
  recover access.
- Temporary directories must be unique per run, use user-only permissions where
  supported, and be removed in a `finally`/context-manager path after both
  success and failure.
- Files containing private or audit data should use user-only permissions
  (`0600`) and directories should use (`0700`) where the platform supports
  POSIX modes.
- Never use the repository checkout as a runtime state, cache, temp, or
  credential directory.

## Retention and cleanup policy

These are safe defaults. A skill may retain data longer, but shortening a
retention period must be visible in the cleanup plan and explicitly approved by
the customer.

| Class | Default retention | Capacity/count limit | Cleanup condition |
|---|---:|---:|---|
| Provider credentials | provider-controlled | provider-controlled | official logout, revocation, or provider expiry only |
| Non-secret config | indefinite | no automatic limit | customer explicitly requests reset or uninstall-with-config-removal |
| Audit state | 30 days | 100 receipts or 10 MiB per skill | expired or over count/capacity, and covered by a valid managed-storage marker |
| Cache | 7 days since last modification | 512 MiB per skill/root | expired, invalid, source version changed, or over capacity |
| Temporary data | current run | one isolated directory per run | immediately on success/failure/cancel; stale-run fallback after 24 hours |
| Debug temporary data | at most 24 hours | at most 3 retained runs | customer explicitly requests short debug retention, then expiry |
| Rollback backup | verification plus 7 days | at most 3 versions | expiry or version limit, with the declared rollback policy |
| Deliverables | customer-controlled | customer-controlled | explicit customer deletion request only |

Low disk space may trigger a new scan, but never broadens deletion authority.
Only eligible cache and temporary data may be proposed automatically. Config,
credentials, rollback backups, audit state without a cleanup marker, and
deliverables must not be silently deleted.

## Cleanup execution contract

Deletion is irreversible and always requires a fresh customer authorization.
An initial request such as “clean the cache” authorizes scanning and planning,
not deletion of a candidate list the customer has not yet seen.

The required sequence is:

1. Read-only scan of the canonical SOIA roots.
2. Generate an immutable plan with per-class size, candidate size, conditions,
   risks, `plan_id`, 30-minute expiry, and SHA-256 digest.
3. Show the redacted plan and deletion warning to the customer.
4. Wait for a new, explicit confirmation tied to that `plan_id`, and pass the
   exact customer-confirmed id to the executor.
5. Revalidate the digest, expiry, roots, file type, size, modification time,
   active-run markers, symlink boundary, and class policy before every unlink.
6. Delete only unchanged ordinary files in the approved plan; never expand the
   scope, follow symlinks, or use recursive force deletion on unknown paths.
7. Rescan and record deleted/skipped counts, bytes, free-space delta, and a
   timezone-aware `checked_at` in a private receipt.

State cleanup additionally requires `.soia-managed-storage.json` in the owning
skill's state directory:

```json
{
  "schema_version": 1,
  "owner_skill": "soia-env-example",
  "data_class": "audit_state",
  "retention_days": 30,
  "cleanup_allowed": true
}
```

The cleanup plan binds the marker's SHA-256. Missing, malformed, disabled, or
changed markers fail closed. Marker files and fresh `.soia-active` run markers
are never deletion candidates.

Any root supplied through a `SOIA_SKILLS_*_HOME` override must contain
`.soia-storage-root.json` with `managed_by: soia-skills` and the matching
`root_kind`. Creating that marker is a customer-confirmed configuration change.
Without it, the cleanup skill must refuse to claim or scan an arbitrary custom
directory. Root markers are never deletion candidates.

`soia-env-storage-cleanup` is the reference skill for scanning, planning,
authorized deletion, and verification of these managed roots. Whole-disk
cleaning, arbitrary user directories, application data, downloads, projects,
and customer deliverables are outside its authority.

## Time fields

Customer-facing status tables include `更新时间`. Structured receipts use
`checked_at`.

- Record the time after the final verification that supports the reported row.
- Use RFC 3339 with an explicit timezone, for example
  `2026-07-21T00:00:00+08:00`.
- Do not substitute the skill package's frontmatter `updated_at`; that field is
  the source-code modification time, not the runtime verification time.
