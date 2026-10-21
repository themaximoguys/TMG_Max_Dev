# Solution taxonomy: the closed enums

> **The CLASSIFIER primitive.** Every value written in these columns comes from the lists below.
> `tools/validate_work.py` rejects anything else. A new value means changing this file, not
> inventing one in a register.

---

## §1 Requirement prefixes: who designs the row

| Prefix | Meaning | Designs the solution row |
|---|---|---|
| `FUN` | Business process, statuses, field behaviour, validation rules | `maximo-functional-architect` |
| `TEC` | Data model, platform, configuration mechanics, performance | `maximo-technical-architect` |
| `UI` | Screens, tabs, fields, dialogs, conditional UI, start centers | `maximo-functional-architect` |
| `WF` | Workflow, approvals, escalations, notifications, cron | `maximo-functional-architect` |
| `INT` | Data crossing a system boundary | `integration-architect` |
| `GIS` | Maps, Esri services, spatial linkage, location geometry | `gis-esri-specialist` |
| `AI` | watsonx Orchestrate agents, MAS AI / Assist, MCP tools, predictive | `ai-orchestrate-specialist` |
| `SEC` | Groups, sig options, data restrictions, auth, audit | `security-architect` |
| `DAT` | Data loads, conversions, reference data | `data-migration-lead` |
| `MOB` | Maximo Mobile apps, offline, inspections | `mobile-specialist` |
| `RPT` | BIRT reports, KPIs, analytics | `reporting-analytics-specialist` |
| `SVC` | Service requests, SLAs, response plans, classifications | `service-management-specialist` |
| `CNV` | Legacy Java / TRM / 7.6 customisation being converted | `legacy-conversion-specialist` |
| `ENV` | Environment, system properties, predeployment, MAS platform | `environment-steward` |

## §2 Ladder position: how a requirement is built

`OOB → CONFIGURATION → AUTOMATION SCRIPT → INTEGRATION → CUSTOM JAVA`

| Value | Meaning | Departure reason required |
|---|---|---|
| `OOB` | Maximo already does it; no artifact (evidence: query, screen or IBM doc) | No |
| `CONFIGURATION` | Domains, attributes, relationships, conditions, formulas, App Designer, sig options, workflow, escalations | No |
| `AUTOMATION SCRIPT` | Jython 2.7 launch-point script | Yes: what configuration could not do |
| `INTEGRATION` | Object structure, channel, service, endpoint, external system | Yes: why the data must cross a boundary |
| `CUSTOM JAVA` | Java class | Yes: why no script launch point works, and user approval |

A departure reason states what **failed** one step to the left. "Cleaner", "more flexible" or
"the client asked" are preferences, not failures.

## §3 Change kind: what the artifact does to the tenant

| Value | Meaning |
|---|---|
| `NEW` | Record does not exist on the target env (shown by extract/query) |
| `MODIFY` | Record exists; repo file was extracted from live, then edited |
| `RETIRE` | Record is deactivated or removed; requires explicit user approval |
| `NO-CHANGE` | Listed for dependency or reference only; not deployed by this package |

## §4 Legacy disposition: the seven values (`CONVERSION_REGISTER.md`, `CURRENT_STATE_INVENTORY.md`)

| Value | Use when |
|---|---|
| `RETAIN` | The artifact carries forward unchanged **and** that has been evidenced, not assumed |
| `RECONFIGURE` | The same outcome is reachable through MAS configuration |
| `REPLACE WITH OOB` | MAS ships the capability; the evidence path proves it |
| `REPLACE WITH AUTOMATION SCRIPT` | Custom Java maps onto a supported launch point |
| `REWRITE` | Outcome still needed, implementation cannot survive the platform change |
| `RETIRE` | Business confirms the outcome is no longer needed (`Confirm-with-business = Y` until confirmed) |
| `REQUIRES INVESTIGATION` | Access or information is missing; names who will get it |

Uncertainty resolves to `REQUIRES INVESTIGATION`, never to `RETAIN`.

## §5 Status values

| Register | Column | Values |
|---|---|---|
| Requirement | Status | `OPEN` · `DESIGNED` · `BUILT` · `DEPLOYED` · `VERIFIED` · `DEFERRED` · `REJECTED` |
| Test | Result | `PASS` · `FAIL` · `NOT RUN` · `BLOCKED` |
| Deployment plan | Mode | `DRY-RUN` · `APPLY` |
| Findings log | Severity | `BLOCKER` · `MAJOR` · `MINOR` |
| Findings log | Status | `OPEN` · `FIXED` · `ACCEPTED` (accepted needs the user's quoted words) |
| Assumption/risk | Kind | `ASSUMPTION` · `RISK` · `QUESTION` |
| Any register | Glyph | ⬜ not started · 🟡 in progress · ✅ evidenced · ⛔ blocked |
