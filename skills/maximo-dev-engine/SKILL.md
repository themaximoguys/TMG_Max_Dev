---
name: maximo-dev-engine
description: The orchestrator for any IBM Maximo / MAS 9 development work package in TMG_Max_Dev. It walks the gate ladder D0–D10 and dispatches each phase to its specialist agent (functional, technical, integration, GIS/Esri, AI/watsonx Orchestrate, security, configuration, App Designer, automation script, legacy conversion, workflow, mobile, service management, reporting, data, release, test, red team, writer). Use it whenever the user wants a feature, ticket, functional spec, TDD, Java/TRM conversion or multi-artifact change built end to end, e.g. "build this requirement", "work ticket X", "implement this spec in Maximo", "convert these customisations", "run the dev team on this", or "who owns this". For a single quick pull/diff/deploy, use maximo-dev instead.
---

# Maximo development engine

The entry point for a Maximo work package. **Read `engine/00_MASTER_PROMPT.md` before anything
else.** It is the constitution, and it governs everything below. Read `AGENTS.md` and
`skills/maximo-dev/SKILL.md` for the tenant safety rules, which bind every agent.

## Non-negotiables

- **Never begin by writing code.** Build has seven preconditions; see `engine/01_LIFECYCLE.md`.
- **Never invent a tenant fact.** Object names, attributes, scripts, statuses and environment facts
  come from a maxdev command against a named environment. If missing, write
  `[[PLACEHOLDER: what | owner]]`.
- **🔴 gates stop work.** An open red gate is never carried forward as a risk.
- **Registers are filled only by dispatching to their owner agent** (`engine/02_AGENT_ROSTER.md`,
  `engine/roster.yaml`). A `src/` file is built only by its type's owner.
- **Only `release-manager` applies**, only after the user's explicit yes to a concrete dry-run
  plan for the environment the user named. Agents never approve their own plan.

## Run a work package

1. **D0 Intake.** Dispatch `work-package-manager`. It runs `python3 tools/new_work.py <TICKET> --env <ENV>`
   and registers the request. If the user named no environment, do only offline work and ask.
2. **D1.** Dispatch `requirements-analyst`, which builds the source and requirement registers (`engine/templates/SOURCE_REGISTER.md`, `engine/templates/REQUIREMENT_REGISTER.md`).
3. **D2 / D2e, in parallel.** Dispatch `maximo-technical-architect` (current state, read-only
   extracts) and `environment-steward` (ping, doctor, predeployment). Also dispatch
   `legacy-conversion-specialist` when there are `CNV` rows.
4. **D3 Design, in parallel by prefix.** Functional architect: `FUN` `UI` `WF`. Technical architect:
   `TEC`, plus the artifact register. `integration-architect`: `INT`. `gis-esri-specialist`: `GIS`.
   `ai-orchestrate-specialist`: `AI`. `security-architect`: `SEC`. `data-migration-lead`: `DAT`.
   Then run the cross-validation pairs in the roster, and escalate disagreements to the user.
5. **D4 Build, in parallel by type owner.** Dispatch each artifact row's owner with its row and
   requirement. `release-manager` keeps `manifests/<TICKET>.yaml` in step with the artifact register.
6. **D5.** Dispatch `dev-red-team-reviewer`, which runs `python3 tools/validate_work.py <TICKET>`,
   lint, tests and the component check. Any FAIL or open BLOCKER goes back to its owner.
7. **D6.** Dispatch `release-manager` for the diff and dry run, then **show the user the plan and stop.**
8. **D7.** The user approves in their own words. `release-manager` quotes them in the deployment plan (`engine/templates/DEPLOYMENT_PLAN.md`).
9. **D8.** `release-manager` applies, then records the receipt, re-diff, dbconfig status and manual steps.
10. **D9.** Dispatch `test-engineer`, which runs each acceptance test on the environment with evidence.
    A FAIL reopens D3 or D4.
11. **D10.** Dispatch `technical-writer` for the design doc and handoff (`engine/templates/DESIGN_DOC.md`, `engine/templates/HANDOFF.md`), then run the
    final `dev-red-team-reviewer` pass. Report what changed, where, and what is still open.

Log every dispatch in the work checklist (`engine/templates/WORK_CHECKLIST.md`). Run independent dispatches in one message so they
run concurrently. Give each agent the ticket, its rows and the env, not the whole conversation.

## Dispatch table

| Need | Agent (`subagent_type`) |
|---|---|
| Scaffold, checklist, assumptions, risks | `work-package-manager` |
| Sources, requirements, acceptance criteria | `requirements-analyst` |
| Business process, UI, workflow design (`FUN` `UI` `WF`) | `maximo-functional-architect` |
| Current state, data model, ladder, artifact register (`TEC`) | `maximo-technical-architect` |
| Interfaces, object structures, channels, endpoints (`INT`) | `integration-architect` |
| Maximo Spatial, Esri ArcGIS, maps (`GIS`) | `gis-esri-specialist` |
| watsonx Orchestrate, MAS AI/Assist, IBM MAS MCP (`AI`) | `ai-orchestrate-specialist` |
| Groups, sig options, grants, data restrictions (`SEC`) | `security-architect` |
| ping, doctor, predeployment, dbconfig, properties (`ENV`) | `environment-steward` |
| Unknown object structure, schema, BMXAA error | `maximo-api-researcher` |
| Domains, objects, relationships, conditions, formulas | `configuration-developer` |
| App Designer XML, conditional UI, queries, start centers | `app-designer-developer` |
| Automation scripts | `automation-script-developer` |
| Java / TRM / 7.6 customisation inventory and conversion (`CNV`) | `legacy-conversion-specialist` |
| Person groups, roles, actions, escalations, cron, workflow, comm templates | `workflow-developer` |
| Maximo Mobile, inspections (`MOB`) | `mobile-specialist` |
| Classifications, SLAs, response plans (`SVC`) | `service-management-specialist` |
| BIRT reports, KPIs (`RPT`) | `reporting-analytics-specialist` |
| Data loads (`DAT`) | `data-migration-lead` |
| Manifest, dry run, approval record, apply, receipts | `release-manager` |
| Acceptance tests on the tenant | `test-engineer` |
| Validators, static review, findings | `dev-red-team-reviewer` |
| Design doc, handoff | `technical-writer` |

## Reference

Constitution `engine/00_MASTER_PROMPT.md` · gates `engine/01_LIFECYCLE.md` · owners
`engine/02_AGENT_ROSTER.md` · enums `engine/03_SOLUTION_TAXONOMY.md` · validators
`engine/04_VALIDATORS.md` · templates `engine/templates/` · agents `.claude/agents/`.

Clients without subagents (Codex, Copilot, Cursor, Gemini): play each role in turn by reading
that agent's file in `.claude/agents/` before doing that phase's work. The gates and registers are the same.
