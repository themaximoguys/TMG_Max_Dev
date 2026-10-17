---
name: maximo-dev
description: Use for any Maximo/MAS development in the TMG_Max_Dev repo — extracting, editing, diffing or deploying Maximo configuration (domains, objects, relationships, conditions, App Designer XML, automation scripts, actions, escalations, cron tasks, workflows, integration, security, reports) through the maxdev CLI or the tmg-maximo-dev MCP server. Triggers on extract from Maximo, deploy to Maximo, push config, Maximo diff/drift, App Designer XML change, new automation script in the repo, DB Config apply, Migration Manager package, IBM Maximo MCP server.
---

# Maximo development with maxdev

The repo is the source of truth; Maximo is the target. Every change follows the same loop:
**extract → edit file → lint/diff → dry-run deploy → apply → diff again.**

## Rules (do not break)
1. Never write to Maximo without a dry run first. CLI: deploy without `--apply`; MCP: `apply=false`. Show the user the plan and get a yes before applying.
2. Never deploy to an environment the user didn't name. Protected environments (`MAXIMO_PROTECTED=true`) refuse writes, and that is intended — never flip the flag yourself.
3. Edit files in `src/`, not live records. The MCP `query` tool is for reading only.
4. Extract with a filter (names, `--like TMG`, `--where`). Whole-type extracts of OOTB data are refused.
5. App Designer: never use `--force-replace` unless the user asks. The default merge keeps changes made in the UI.
6. No demo or seed data loading unless the user asks for it explicitly.
7. Report results honestly. Read the receipt; FAILED or not-attempted rows must be told to the user.

## Where things go
- `maxdev types` (MCP `list_artifact_types`) gives every area: layer, object structure, folder, gotchas.
- The coverage map is in `docs/COVERAGE.md`; app development (MAF, Java, BIRT) is in `docs/APPLICATION_DEVELOPMENT.md`.

## Automation scripts
- For a new script, `maxdev build <kind> ...` (MCP `build_script`). Then fill the business logic following `docs/standards/TMG_AUTOSCRIPT_STANDARDS.md` and the `create-automation-script` skill.
- To convert Java, run `maxdev java analyze X.java` (MCP `analyze_java`), then the `convert-java-to-script` skill.
- Lint is mandatory: `maxdev lint` / MCP `lint_script`. Deploy blocks on lint errors.
- One script per MBO + event: add the rule to the existing script instead of creating another.

## Workflows
Generate with the `maximo-workflow` skill and save the JSON under `src/13-workflows/`, with its person groups, roles and actions in their folders. Deploy them together with a manifest.

## Database Configuration
After deploying `object` changes, run `maxdev dbconfig status`. Structural changes need Admin Mode, so ask the user before running `dbconfig apply --admin` — it logs users out.

## Change sets
Group a feature's files in `manifests/<TICKET>.yaml`, with `items:` and `manual:` steps (see `manifests/EXAMPLE.yaml`). Deploy with `maxdev deploy --manifest <TICKET>`.

## IBM MCP server (MAS 9.2)
Use `maxdev ibm-mcp tools --env X` or the MCP tools `ibm_mcp_tools` / `ibm_mcp_call`. Tools that aren't marked read-only need `apply`. The feature set is partial, so treat its results as something to verify.
