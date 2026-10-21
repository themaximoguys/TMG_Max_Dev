# Agent roster: who owns what

> **The OWNER primitive.** Every register and every artifact type has exactly one accountable
> specialist. A register with no owner never gets filled, and one with two owners gets filled twice
> and inconsistently. The machine-readable source is `roster.yaml`, and the checks enforce it.
>
> **Anti-shelfware rule.** The orchestrator populates a register *only* by dispatching to its owner,
> and creates or edits a `src/` file *only* by dispatching to that type's owner. A register whose
> owner was never invoked is an incomplete phase, and an incomplete phase fails its gate. You cannot
> clear a gate by writing the register yourself. Each dispatch is logged in `WORK_CHECKLIST.md`.

Agent files live in `.claude/agents/<name>.md`. In Claude Code, invoke one with the `Agent` tool and
`subagent_type` set to its name. Other clients load the same file as role instructions.

---

## Run the work package

| Agent | Owns | Clears |
|---|---|---|
| `work-package-manager` | Work checklist · assumption/risk register · dispatch log | D0 · D10 (with writer) |
| `requirements-analyst` | Source register · requirement register | D1 |

## Embedded functional and technical design

| Agent | Owns | Req prefixes | Clears |
|---|---|---|---|
| `maximo-functional-architect` | Classification rows for `FUN` `UI` `WF` | `FUN` `UI` `WF` | D3 (functional) |
| `maximo-technical-architect` | Current-state inventory · solution classification (integrity, `TEC` rows) · artifact register | `TEC` | D2 · D3 (technical) |
| `integration-architect` | Integration register; also **builds** integration types | `INT` | D3 · D4 |
| `gis-esri-specialist` | GIS register (Maximo Spatial, Esri ArcGIS services, map manager) | `GIS` | D3 · D4 |
| `ai-orchestrate-specialist` | AI agent register (watsonx Orchestrate, MAS AI/Assist, IBM MAS MCP, maxdev MCP) | `AI` | D3 · D4 |
| `security-architect` | Security register; also **builds** security types | `SEC` | D3 · D4 |
| `environment-steward` | Environment readiness (ping, doctor, predeployment, dbconfig, MAS platform) | `ENV` | D2e |
| `maximo-api-researcher` | Research register (object structures, schemas, BMXAA errors, IBM docs) | — | any phase, on request |

## Build: one owner per artifact type

| Agent | Registry types (`maxdev types`) | Uses skill |
|---|---|---|
| `configuration-developer` | property · domain · message · object · relationship · lookupmap · condition · formula · objformula | `maximo-dev` |
| `app-designer-developer` | appxml · appdesc · condprop · query · startcenter | `maximo-dev` |
| `automation-script-developer` | autoscript | `create-automation-script` |
| `legacy-conversion-specialist` | java (inventory); owns the conversion register (`CNV`) | `convert-java-to-script` · `convert-trm-to-script` |
| `workflow-developer` | persongroup · role · action · escalation · crontask · workflow · commtemplate | `maximo-workflow` |
| `integration-architect` | objectstructure · publishchannel · enterpriseservice · invocationchannel · endpoint · extsystem · ifacecontrol · jsonmapping | `maximo-dev` |
| `security-architect` | securitygroup · sigoption · grant · datarestriction | `maximo-dev` |
| `mobile-specialist` | mafapp · inspectionform (`MOB`) | `maximo-dev` |
| `service-management-specialist` | classification · sla · responseplan (`SVC`) | `maximo-dev` |
| `reporting-analytics-specialist` | report · kpi (`RPT`) | `maximo-dev` |
| `data-migration-lead` | dataload; owns the data load register (`DAT`) | `maximo-dev` |

GIS and AI work produces artifacts of other owners' types, such as a property, an endpoint, an
object structure or a script. The specialist designs the row in their register and raises the
artifact row. The type owner builds the file, and the specialist reviews it.

## Ship and prove

| Agent | Owns | Clears |
|---|---|---|
| `release-manager` | Manifest · deployment plan (dry runs, approvals, applies, receipts) | D6 · D7 (records) · D8 |
| `test-engineer` | Test register | D9 |
| `dev-red-team-reviewer` | Findings log · validator runs | D5, and a final pass before D10 |
| `technical-writer` | Design doc · handoff | D10 |

---

## Cross-validation pairs

Each agent analyses independently, then these pairs reconcile. A disagreement is escalated to
the user with both positions stated, never averaged.

| Pair | What they reconcile |
|---|---|
| Functional ↔ Technical architect | The OOB / config / script / Java call on contested requirements |
| Technical architect ↔ Automation script developer | One script per MBO + event; the rule goes into the existing script |
| Technical architect ↔ App Designer developer | The live screen was extracted; the change is a merge |
| Integration ↔ Security | Endpoint auth, API keys, certificates, which group the integration user runs as |
| Integration ↔ AI/Orchestrate | Which object structures and APIs an agent calls; read vs write; approval points |
| GIS ↔ Integration | Esri service URLs and auth as endpoints; sync direction; linkage keys |
| GIS ↔ Mobile | Offline maps, map layers on Maximo Mobile |
| Workflow ↔ Security | Roles, person groups, and the sig options workflow actions need |
| Data migration ↔ Functional | The loaded data supports the configured process and statuses |
| Legacy conversion ↔ Technical architect | Each disposition, and the target artifact it produces |
| Environment steward ↔ Release manager | Predeployment present; the env is not protected; the target env is the one the user named |
| Test engineer ↔ Requirements analyst | Each acceptance criterion has a test that can fail |
| Release manager ↔ Red team | No apply without a clean D5 and a recorded approval |
| Writer ↔ every owner | Every sentence in the design doc traces to a register row |

---

## Binding rules for every agent

1. **Zero hallucination.** Tenant facts come from a maxdev command against a named env, and
   business facts from a person or a document. Anything missing is `[[PLACEHOLDER: what | owner]]`.
2. **Evidence, not assertion.** Every cleared row has a command or file path, an owner and a date.
3. **Stay in lane.** Fill only your own registers and types. When your analysis implies a change
   to another owner's register or file, raise it to that owner.
4. **No live writes without the gate.** Agents may run read-only maxdev commands (`ping`,
   `doctor`, `query`, `schema`, `extract` with a filter, `diff`, and `deploy` without `--apply`).
   Only `release-manager` runs `--apply`, and only after D7.
5. **Never touch secrets.** Never read or edit `environments/.env.*`, and never bypass protection.
6. **The writer decides nothing technical.** The writer turns registers into prose, and never
   writes around a gap.
7. **Flag conflicts, never resolve them silently.** Sources that disagree produce an
   assumption/risk row of kind `QUESTION`.
