---
name: maximo-dev
description: How to do IBM Maximo / MAS 9 Manage development in the TMG_Max_Dev repo with the maxdev CLI (python3 -m maxdev) and the tmg-maximo-dev MCP server — connecting an environment, pulling (extracting) configuration into src/, editing it, diffing against live, and deploying it back safely through Maximo's REST API. Use this skill whenever the user wants to pull, push, sync, compare or change anything in Maximo from this repo — domains, objects/attributes (Database Configuration), relationships, conditions, App Designer screens, automation scripts, actions, escalations, cron tasks, workflows, roles, security groups/sig options/grants, publish channels, enterprise services, endpoints, object structures, classifications, reports — and also for connecting or bootstrapping a new Maximo environment, running doctor, predeployment, or diagnosing BMXAA9301E / BMXAA4216E / BMXAA1283E API errors. Use it even when the user just says "deploy this to demo", "what changed on dev", or "get WOTRACK", without naming maxdev.
---

# Maximo development with maxdev

The repo's `src/` folder is the source of truth, and Maximo is the target. Every change follows one loop:

**extract → edit the file → lint / diff → dry-run deploy → (user says yes) → apply → diff again**

Each step exists for a reason:
- Maximo config writes aren't a transaction: a failed step leaves earlier writes in place.
- App Designer screens are whole documents: one bad write can wipe UI changes other people made.
- Working from a file means a human can review the change before it touches a shared environment.

## Working agreements

- **Dry run, then ask.** A deploy without `--apply` (MCP: `apply=false`) shows exactly what would be created, updated or merged. Show that plan and wait for a clear yes before applying, because the user may share the environment with others.
- **Only the environment the user named.** `MAXIMO_PROTECTED=true` environments refuse writes on purpose. The user controls that flag; don't edit `environments/.env.*` yourself.
- **Change files, not live records.** Edit under `src/`, then deploy. Use `query` for investigation. Arbitrary `call_script` handlers can mutate records, even with GET; dry run and approval are required.
- **Filtered extracts.** Pass names, `--like TMG`, `--where` or `--limit`. A whole-type pull of OOTB data is thousands of IBM records nobody wants in Git; maxdev refuses it without a filter.
- **App Designer merges.** Deploy backs up the live screen and merges the repo copy onto it, so UI-made changes survive. Use `--force-replace` only when the user explicitly wants the live screen overwritten.
- **No demo/seed data loads** unless asked.
- **Report what actually happened.** Read the deploy output or receipt (`.maxdev/receipts/<env>/`), and tell the user about any `FAILED` or `not-attempted` rows. Deploy stops at the first failure, so later items didn't run.

## Connecting an environment (once per environment)

On MAS 9, `mxe.int.enableosauth=1` means an object structure only works over REST if it has an authorisation app. Many config areas also have no REST-usable IBM structure at all. So a new environment needs a one-time predeployment before roughly a third of the areas work.

1. `maxdev ping --env X`, then `maxdev doctor --env X`. Doctor marks each area `ok`, `NO-AUTH` (structure exists without an auth app) or `MISSING`.
2. `maxdev bootstrap authapps --env X`. Dry run first, then `--apply` after a yes. It sets an auth app on IBM structures that ship without one, and never overwrites an existing value.
3. `maxdev bootstrap --env X`. Dry run first, then `--apply` after a yes. It deploys `src/00_predeployment/`: the TMG* object structures plus the read-only `TMG_EXPORT_PRES` script.
4. Run `maxdev doctor --env X` again. Everything should be `ok` except SLA and response plans.

**TMG structure rule** (the user decided this, so keep to it):
- Use IBM's structure whenever one exists.
- If it only lacks an auth app, set the auth app.
- Clone into a `TMG*` structure (`maxdev bootstrap generate`) only when nothing REST-usable exists, e.g. only a Migration Manager `DM*` version, which REST refuses with BMXAA1283E.
- Ask before creating any new TMG structure.

## Finding your way

- `maxdev types` (MCP `list_artifact_types`) lists every area: its layer, object structure, `src/` folder and known gotchas. `maxdev/registry.yaml` is the single table behind it.
- Coverage map: `docs/COVERAGE.md`. Mobile/MAF, Java and BIRT: `docs/APPLICATION_DEVELOPMENT.md`.
- Group one feature's files in `manifests/<TICKET>.yaml`, with `items:` and `manual:` steps (see `manifests/EXAMPLE.yaml`). Deploy with `maxdev deploy --manifest <TICKET>`. Deploy order is by layer, with `src/00_predeployment` always first.
- If a pull or deploy errors, read `references/troubleshooting.md`. It covers timeouts, HTTP 500s, BMXAA codes, empty diffs, generated IDs, and promoting to another environment.

## Automation scripts

- New script: `maxdev build <kind> --object X [--attr F | --name N]` (MCP `build_script`) fills a TMG template. Then write the business logic following `docs/standards/TMG_AUTOSCRIPT_STANDARDS.md` and the `create-automation-script` skill.
- Java to script: `maxdev java analyze X.java` (MCP `analyze_java`), then the `convert-java-to-script` skill.
- `maxdev lint` (MCP `lint_script`) runs before every deploy, and deploy blocks on lint errors.
- Maximo's Jython has **no Python standard library**: `import re`, `json`, `os` and `datetime` fail at runtime. Use `java.util.regex`, `java.util.Calendar` and so on. Java-backed modules like `math` and `time` are fine.
- Keep one script per MBO + event. Add a new rule to the existing script so launch points don't fight.

## Workflows, Database Configuration, IBM MCP

- **Workflows.** Generate with the `maximo-workflow` skill and save under `src/13-workflows/`. Person groups, roles and actions go in their own folders, and the manifest deploys them together.
- **Database Configuration.** After deploying `object` changes, run `maxdev dbconfig status`. Structural changes need Admin Mode, which logs users out, so ask before `dbconfig apply --admin --apply`.
- **IBM MCP server (MAS 9.2, partial feature set).** Use `maxdev ibm-mcp tools --env X` or `ibm_mcp_tools` / `ibm_mcp_call`. Tools that aren't marked read-only need `apply`. Treat results as something to verify.
