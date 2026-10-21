# Coding-agent setup

`AGENTS.md` is the shared repository contract. `skills/` contains all five maintained
skills and their references. Client entry files route to these sources; changes to
standards belong in the shared sources. No global skills, plugins, or proprietary
agent SDK are needed. CLI access is the fallback for every agent.

## Install and check

Use Python 3.10 or newer from the repository root:

```bash
python3 -m venv .venv
# Linux/macOS; on Windows activate .venv\Scripts\Activate.ps1 instead
. .venv/bin/activate
python3 -m pip install -e .
python3 tools/check_agent_setup.py
python3 -m unittest discover -s tests
python3 -m maxdev types
python3 -m maxdev lint
```

These checks do not contact Maximo. Local tooling is Python 3; deployed scripts are
Jython 2.7 and must follow the TMG standards. Do not compile the entire `src/` or
`catalog/` trees with Python 3 as a validation step.

## Client entry points

| Client | Repository instructions | Skills / tools |
|---|---|---|
| Codex | `AGENTS.md` | `.agents/skills` links to `skills/`; `.codex/config.toml` registers local MCP |
| Claude Code | `CLAUDE.md` | `.claude/skills` links to `skills/`; `.mcp.json` registers local MCP |
| GitHub Copilot | `.github/copilot-instructions.md` | Read referenced skills; use terminal CLI or configure MCP in the client |
| Cursor | `.cursor/rules/maximo.mdc` (always applied) | Read referenced skills; use CLI or configure local stdio MCP |
| Gemini CLI | `GEMINI.md` | Read referenced skills; use CLI or configure local stdio MCP |
| IBM Bob, Windsurf, Cline, Aider, other agents | Explicitly load `AGENTS.md` | Read the applicable `skills/<name>/SKILL.md`; use CLI or the client's MCP settings |

For clients without instruction discovery, start with: “Read AGENTS.md and
skills/maximo-dev/SKILL.md, then carry out this task.” Support here means shared
instructions plus CLI/MCP access, not that every vendor's UI was tested.

Codex and Claude Code should be restarted after adding skills. For a clone that
cannot preserve Git symlinks (for example, Windows without symlink support), replace
the `.agents/skills` and `.claude/skills` link entries with directory copies of
`skills/`. Recopy after every skill change; the checker detects drift. Edit the
canonical `skills/` files, never the discovery copies.

## MCP configuration

Launch the agent from the repository root with the Python environment activated.
The committed configs use `python3 -m maxdev.mcp_server`, with no credentials and
no forced environment. Codex project config is used only for a trusted project;
trust and tool approvals remain user choices. The portable template is also at
`config/agents/codex.toml` for restoring the project configuration.

If a client launches servers elsewhere, configure an absolute interpreter and
working directory using that client's supported settings. A client-neutral stdio
registration consists of:

- Name: `tmg-maximo-dev`
- Command: absolute path to this clone's virtual-environment Python
- Arguments: `-m`, `maxdev.mcp_server`
- Working directory: absolute path to this clone

Use an **editable** install (`pip install -e .`), since maxdev resolves `src/`,
`catalog/`, and `environments/` relative to its source package. A standalone wheel
is not a replacement for the repository. Windows can use the virtual environment's
`python.exe` instead of `python3` in local client configuration.

Verify the connected server by calling `list_artifact_types` or
`list_script_templates`; these are offline tools. A server starting successfully
does not establish that a tenant is reachable. Optional IBM MAS MCP tools are
accessed through this server's `ibm_mcp_*` wrappers or `maxdev ibm-mcp`, preserving
write guards. Direct remote registration is deliberately absent from defaults.

## Tenant operations

The user creates `environments/.env.<name>` using `.env.example` as the template.
Agents must not edit environment files or output credentials. Use the explicitly
selected environment for each tenant operation:

```bash
python3 -m maxdev ping --env NAME
python3 -m maxdev diff --manifest TICKET --env NAME
python3 -m maxdev deploy --manifest TICKET --env NAME
# After approval of the concrete dry-run plan:
python3 -m maxdev deploy --manifest TICKET --env NAME --apply
```

For nested CLI commands put `--env` before the subcommand group, e.g.
`python3 -m maxdev --env NAME dm create PACKAGE`. `script`, `dbconfig apply`,
`adminmode on/off`, and Migration Manager `create/upload/deploy` now require
`--apply` to execute. Without it they return an invocation plan without calling
the remote handler. A handler plan does not simulate its internal effects.
Protected targets refuse execution. Scripts require approval even with `--get`.
IBM MCP tools need a boolean `readOnlyHint: true` annotation to be called without
`--apply`; tool names alone do not establish that they are read-only.

For audit findings, validation results, and migration notes, see [AGENT_AUDIT.md](AGENT_AUDIT.md).

## Development engine and subagents

`engine/` turns a work package into gated, owner-filled registers, following the same model
as the RFP engine: seven primitives, gates D0–D10, one owner per register and per artifact type,
and computed validators. Start with `skills/maximo-dev-engine/SKILL.md`.

- `engine/00_MASTER_PROMPT.md` (constitution) · `01_LIFECYCLE.md` (gates) · `02_AGENT_ROSTER.md`
  (owners and cross-validation pairs) · `03_SOLUTION_TAXONOMY.md` (enums) · `04_VALIDATORS.md`.
- `engine/roster.yaml` is the machine-readable owner table; `check_components.py` fails if a
  registry type, template or agent file has no owner, or has more than one.
- `.claude/agents/*.md` holds 23 specialists. Claude Code dispatches them as subagents; other
  clients read the matching file and play that role.
- `python3 tools/new_work.py TICKET --env ENV` scaffolds `work/TICKET/` and the manifest;
  `python3 tools/validate_work.py TICKET` runs W-01–W-28.

## Hooks

Enable the offline git hooks once per clone (they never contact Maximo):

```bash
git config core.hooksPath .githooks
```

- `pre-commit`: `git diff --check`, `check_agent_setup.py`, `check_components.py`,
  `maxdev lint` on staged scripts, unit tests when `maxdev/`, `tests/` or `tools/` change.
- `pre-push`: setup and component checks, all unit tests, lint of every script.

Claude Code also loads `.claude/settings.json` (`tools/agent_hook.py`): at session start it
runs both checkers, before tool use it refuses reading/editing `environments/.env.*` and raw
`curl`/`Invoke-RestMethod` writes to `/maximo/`, and after an edit under `src/` it lints the
script and returns errors to the agent. Other clients rely on the git hooks.

## Maintenance and references

Run `python3 tools/check_agent_setup.py` after changing skills or adapters. It
checks discovery, skill metadata/references, required config files, and MCP defaults.
No automatic deployment or CI pipeline is added.

Entry formats were checked against vendor documentation on 2026-10-17:
[Codex skills](https://developers.openai.com/codex/skills/),
[Codex MCP configuration](https://developers.openai.com/codex/config-reference/),
[Copilot instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions),
[Cursor rules](https://cursor.com/docs/rules), and
[Gemini context](https://geminicli.com/docs/cli/gemini-md/).
