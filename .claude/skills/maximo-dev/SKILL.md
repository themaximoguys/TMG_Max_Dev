---
name: maximo-dev
description: Use for any Maximo/MAS development in the TMG_Max_Dev repo — extracting, editing, diffing or deploying Maximo configuration (domains, objects, relationships, conditions, App Designer XML, automation scripts, actions, escalations, cron tasks, workflows, integration, security, reports) through the maxdev CLI or the tmg-maximo-dev MCP server. Triggers on extract from Maximo, deploy to Maximo, push config, Maximo diff/drift, App Designer XML change, new automation script in the repo, DB Config apply, Migration Manager package, IBM Maximo MCP server, connect a new Maximo environment, bootstrap / predeployment, doctor, BMXAA9301E or BMXAA4216E errors.
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

## New environment: predeploy first (once)
Without these steps, about a third of the areas fail with BMXAA9301E (not authorised) or BMXAA4216E (unknown object). With `mxe.int.enableosauth=1`, every object structure needs an authorisation app.
1. `maxdev ping --env X` and `maxdev doctor --env X`. Doctor separates `NO-AUTH` from `MISSING`.
2. `maxdev bootstrap authapps --env X`. Dry run, then `--apply`. It sets the auth app on IBM structures that ship without one (MXOBJECTCFG, MXIFACEOUT, MXIFACEINVOKE, MXEXTSYSTEM, MXIFACECONTROL, MXJSONMAPPING). It never overwrites an existing value.
3. `maxdev bootstrap --env X`. Dry run, then `--apply`. It creates `src/00_predeployment/`: the TMG* structures plus TMG_EXPORT_PRES.
4. `maxdev doctor --env X` again. Every area should be ok, except SLA and response plans.

Rule for TMG structures: use the IBM structure whenever one exists. If it only lacks an auth app, set the auth app (step 2). Clone into a TMG* structure (`maxdev bootstrap generate`, from the tenant's own DM* definition) only when no REST-usable structure exists. A DM* MIGRATIONMGR structure is refused by REST (BMXAA1283E). Ask the user before creating any new TMG structure.

## Lessons from the live demo (MAS 9)
- `src/00_predeployment` always deploys before everything else, in any deploy that includes it.
- Heavy child trees need a narrow `select` and a small `page` in registry.yaml. Signs of this are a timeout, an HTTP 500, or a read-only child error on page 2. Records the server can't serialise go in that type's `skip:` list. OSLC has no `not in`, so maxdev writes `!=` clauses.
- Rows that come back `_hidden` or without their key are skipped and counted, never written.
- Maximo's Jython has no Python stdlib: `import re`/`json`/`os` fail at runtime. Use `java.*` instead. Lint enforces this. Java-backed modules such as `math` and `time` are fine.
- App Designer XML comes back as one line. Extract pretty-prints it, with a check that only whitespace changes.
- Extracted records can carry environment-generated ids (e.g. `alndomainid`). They're fine within one environment, but strip them before promoting to another one.
- Diff ignores null vs [] vs {}. A diff that shows only those is not a change.

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
