# TMG Maximo Development (`maxdev`)

Code-managed, AI-assisted IBM Maximo / MAS 9 Manage development. Every
configuration and code artifact lives in Git as one reviewable file. It is pulled
from and pushed to Maximo **through Maximo's own APIs**, from either a CLI or an
MCP server, so any coding agent (CLI or MCP client) can do the same work you do.

What it builds and deploys: Database Configuration, domains, App Designer screens,
automation scripts (from TMG templates, with Java/TRM conversion), workflows,
security, integration, KPIs, work queues, and **operations dashboards** —
Operational Dashboard views and start centers built from one YAML spec.

This repo deliberately contains **no CI/CD or pipelines**. It is the development
layer: extract, edit, diff, deploy to DEV, verify. Promotion beyond DEV is a
separate release process; mark those environments `MAXIMO_PROTECTED=true` and
this tool refuses to write to them.

```
 you / agent  ──► maxdev CLI ─┐
                              ├─► engine ─► registry.yaml (46 artifact types)
 MCP client  ───► MCP server ─┘     │
                                    ├─► Manage JSON API  /maximo/api/os/* , /api/script/*
                                    └─► IBM Maximo MCP server (MAS 9.2, optional)
```

Start coding agents with [AGENTS.md](AGENTS.md) and the [setup guide](docs/AGENT_SETUP.md).

## Quick start

```bash
pip install -r requirements.txt            # requests, PyYAML, mcp
# fill environments/.env.demo (git-ignored, starts read-only)
python3 -m maxdev ping --env demo          # who am I
python3 -m maxdev doctor --env demo        # which object structures exist for every type
python3 -m maxdev bootstrap authapps --env demo  # set auth app on IBM MX* structures (dry run; --apply)
python3 -m maxdev bootstrap --env demo     # TMG structures only where IBM has none usable (dry run; --apply)
```

`pip install -e .` also gives you the `maxdev` and `maxdev-mcp` commands.

## Daily loop

```bash
maxdev extract domain --like TMG            # pull TMG* domains into src/03-domains/
maxdev extract autoscript WORKORDER.SAVE    # one script -> src/09-automation-scripts/object/
maxdev extract appxml WOTRACK               # screen XML -> src/07-app-designer/WOTRACK.xml
maxdev build field_validate --object WORKORDER --attr CUSTOMER_EMAIL   # TMG template -> src/09-...
maxdev lint                                 # TMG standards; deploy refuses lint errors
maxdev java analyze legacy/FldWOEmail.java  # which template a Java class converts to
# ... edit files ...
maxdev diff --path src/03-domains           # repo vs live
maxdev deploy --manifest WO-CUSTOMER-EMAIL  # dry run: shows create/update/merge per file
# Only after approval of the dry run above:
maxdev deploy --manifest WO-CUSTOMER-EMAIL --apply
maxdev dbconfig status                      # objects with unapplied Database Configuration
```

## Dashboards

One YAML spec (`catalog/dashboards/`) builds an Operational Dashboard view and/or a
start center, plus the security group and its rights, saved queries, KPIs and work queues behind them.
The generated manifest deploys them in order and lists the steps no API covers
(group assignment, cards). See
[skills/maximo-dev/references/dashboards.md](skills/maximo-dev/references/dashboards.md).

```bash
maxdev dashboard check maintenance_supervisor
maxdev dashboard build maintenance_supervisor       # src/ files + manifests/TMG_OPS_SUPERVISOR.yaml
maxdev deploy --manifest TMG_OPS_SUPERVISOR --env demo   # dry run; --apply after approval
```

Deploy rules:
- Deploy always runs in dependency order (layer 0 foundation → 11 reporting) and stops at the first failure. Maximo config writes are not a transaction, so the receipt in `.maxdev/receipts/` records exactly what landed.
- Upserts look a record up by its key, then merge into it or create it. A key that matches more than one record is refused rather than guessed.
- Formulas and conditional UI are deleted and re-created, with a read-back check. If the re-create fails, the old rows are restored automatically.
- App Designer XML is a whole-screen document, so deploy:
  - backs up the live screen first;
  - merges the repo copy on top of the live one, so changes made in the UI survive;
  - reads the screen back to catch a write the server silently dropped.

## Layout

| Path | What |
|---|---|
| `src/NN-*/` | Artifacts, one file per record, a folder per area (see [docs/COVERAGE.md](docs/COVERAGE.md)) |
| `manifests/*.yaml` | Change sets: one per feature/ticket, including manual steps |
| `catalog/dashboards/*.yaml` | Dashboard specs for `maxdev dashboard` |
| `src/00_predeployment/` | **Deploy first, once per environment.** TMG helper object structures + `TMG_EXPORT_PRES` script (see its README) |
| `maxdev/` | Engine, CLI, MCP server, IBM MCP client, script and dashboard builders. `registry.yaml` drives everything |
| `catalog/` | TMG script templates (28) and samples (69), from TMG_MAX_CODE (MIT) |
| `docs/standards/` | TMG_AUTOSCRIPT_STANDARDS.md (authoritative) |
| `docs/autoscript/` | Patterns, naming, error handling, launch points, Java/TRM conversion guides, knowledge base |
| `postman/collections/` | Generic MAS 9 config + App Designer collections, for manual API exploration |
| `docs/` | Coverage map, application development, IBM tooling, API notes, standards |
| `skills/` | `maximo-dev`, `maximo-dev-engine`, `create-automation-script`, `convert-java-to-script`, `convert-trm-to-script`, `maximo-workflow` |
| `tests/` | Offline tests against an in-memory fake Manage API (`python3 -m unittest discover -s tests`) |

## MCP

The local **tmg-maximo-dev** server exposes the same engine to MCP clients.
`.mcp.json` configures Claude Code; `config/agents/codex.toml` is the Codex
project configuration. See [agent setup](docs/AGENT_SETUP.md) for discovery,
installation, other clients, and verification. The CLI works without MCP.

IBM MCP is optional and accessed through `maxdev ibm-mcp` or the wrapper's
`ibm_mcp_*` tools so the same apply/protected-environment checks remain in place.
No credentials or default tenant are embedded in shared client configuration.

## Status

**Live on the TMG demo (MAS 9):** `maxdev doctor` reports 41 of the 43 REST areas `ok` (SLAs and response plans have no structure there; 3 more areas are manual by design), and the bootstrap structures are installed. A sample dashboard (12 records, including an Operational Dashboard view and its group rights) is deployed and re-diffs `same`. Write path proven: bootstrap created 16 records, and the export script was updated and verified live. On a new tenant, dry-run and obtain approval before applying: `maxdev bootstrap authapps --apply` sets the authorisation app on 6 IBM MX\* structures; then `maxdev bootstrap --apply` creates 10 TMG structures, only for areas that have no REST-usable IBM structure.


The engine, formats and safety rules are tested offline (run the test command for the current count). These items still need a live check on a TMG tenant:
- Object-structure names marked `verify` in `maxdev types`; run `maxdev doctor` to check them.
- The Admin Mode and Migration Manager service paths.
- The IBM MCP server route.

The reference repo verified the `ok` names on a MAS 9 tenant.

## License

Copyright (c) 2026 TheMaximoGuys LLC. All rights reserved. This is proprietary
software, licensed only under a signed agreement with TheMaximoGuys LLC; see
[LICENSE](LICENSE). The bundled `catalog/` is MIT-licensed; third-party notices
are in [NOTICE](NOTICE).

IBM, Maximo and IBM Maximo Application Suite are trademarks of IBM. This product
is not affiliated with or endorsed by IBM and contains no IBM code.
