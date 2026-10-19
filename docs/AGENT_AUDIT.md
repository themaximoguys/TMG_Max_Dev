# Agent portability and local safety audit — 2026-10-17

Scope: repository instructions, skill discovery, client configuration, and
CLI/MCP write boundaries. This was an offline audit, not a tenant deployment or
an exhaustive review of every Maximo artifact.

## Findings fixed

| Finding | Change |
|---|---|
| Skills existed only under `.claude/`; guides duplicated policy | Canonical `skills/` and `AGENTS.md`, with discovery links and small client adapters |
| Codex had no project MCP configuration or skill UI metadata | Added `.codex/config.toml`, portable template, `.agents/skills`, and five `agents/openai.yaml` files |
| Skills referenced Claude-specific instructions and a missing `PROJECT/` path | Repointed to shared instructions and existing catalog references; corrected workflow skill name |
| Workflow deployment instructions used direct HTTP POST/DELETE and shell credentials | Replaced active deployment workflow with maxdev manifests, staged dependencies, dry run and approval; marked API examples as schema references |
| Old skill evaluation workspace was discoverable as a duplicate skill after relocation | Preserved it under ignored `.maxdev/skill-evals/maximo-dev-workspace/`, outside skill discovery |
| CLI script calls lacked both dry-run and protected-environment guards | Require `--apply` and `guard_write()`, including GET script handlers |
| CLI Admin Mode, DB Configuration and Migration Manager writes executed immediately | Added dry-run invocation plans and explicit `--apply` gates |
| IBM MCP trusted name prefixes and truthy non-boolean annotations as read-only | Require an explicit boolean `readOnlyHint: true`; otherwise apply/protection checks run |
| Default direct IBM MCP registration bypassed the guarded wrapper | Defaults register only the local server; optional IBM tools remain available through the wrapper |
| Bootstrap could return success despite FAILED deployment rows | Return nonzero when bootstrap reports failures |
| Agent configuration could drift or contain nested duplicate skills | Added `tools/check_agent_setup.py` for shared references, discovery content, metadata and MCP defaults |

## Validation

- `python3 -m unittest discover -s tests`: **36 passed** (28 existing + 8 new regression tests).
- Skill creator validation: all **5 skills passed**.
- `python3 tools/check_agent_setup.py`: passed.
- `python3 -m maxdev lint`: **0 errors**, 2 existing warnings in untracked extracts.
- `git diff --check`: passed.
- `python3 -m maxdev types`: offline registry command passed.
- MCP stdio handshake: **23 tools**, with successful offline calls to
  `list_artifact_types` and `list_script_templates`. Sandboxed stdio checks timed
  out; the same SDK handshake passed outside the sandbox after approval.

## Remaining limits and migration notes

- Existing scripts still produce `mboset-close` and `bare-except` warnings. These
  extracts were preserved; review ownership/runtime semantics before changing them.
- No tenant was contacted, no configuration applied, and no secrets changed.
  Client-specific UI behavior outside this Codex session was not exercised.
- Existing callers of `script`, `dbconfig apply`, `adminmode on/off`, and Migration
  Manager write commands must now add `--apply` only after dry-run review and approval.
- `--apply` is an execution gate, not proof of human approval; agents still follow
  the shared instructions. IBM tool annotations remain declarations by that server.
- Workflow subprocess ordering is not inferred by the engine; the skill now
  requires staged dependency/subprocess/parent deployment plans.
- Clones without symlink support can use directory copies, with the checker detecting
  drift. Use an editable Python install because tooling depends on repo resources.
- Historical tenant results in README are pre-existing claims, not verified by this audit.
