# Coverage: every Maximo development area

**Live status (TMG demo, MAS 9, 2026-10-16):**
- 39 of 41 areas work over REST, and every one of them passed the extract → diff "same" test against live data.
- SLAs and response plans have no structure yet.
- MAF, Java and data loads are manual by design.
- `mxe.int.enableosauth=1` requires every structure to have an authorisation app.
  - 6 IBM MX\* structures (MXOBJECTCFG, MXIFACEOUT, MXIFACEINVOKE, MXEXTSYSTEM, MXIFACECONTROL, MXJSONMAPPING) had none, so `maxdev bootstrap authapps` set one. No copy was made.
  - 10 areas have no REST-usable IBM structure (only a Migration Manager DM\* version, or none), so they use TMG\* copies of the tenant's own definitions: relationships, lookup maps, conditions, conditional UI, sig options, App Designer screens, escalations, start centers, enterprise services and roles.

Source of truth is `maxdev/registry.yaml`. `maxdev types` prints it, and `maxdev doctor --env X` checks each object structure on a live tenant.

Route column key:
- **REST**: deployed by `maxdev deploy` through `/maximo/api/os/<OS>`.
- **REST-replace**: the record is deleted and re-created, with rollback.
- **Script**: deployed through an automation-script REST handler.
- **Manual / other**: tracked in Git, applied outside this tool. The reason is given in the table.

| Layer | Area | Repo folder | Format | Route | Notes |
|---|---|---|---|---|---|
| 0 | System properties | `01-system-properties` | JSON | REST `MXAPIPROP` | Secure values are never exported; set per env. `/api/service/system?action=wsmethod:setProperty` does live refresh |
| 0 | Security groups | `02-security/groups` | JSON | REST `MXAPIGROUP` | |
| 0 | Person groups | `02-security/person-groups` | JSON | REST `MXAPIPERGROUP` | Must exist before workflow/escalation routing |
| 0 | Sig options | `02-security/sigoptions` | JSON | REST `TMGMXAPISIGOPTION` (bootstrap) / `MXAPISIGOPTION` | Before App Designer XML that references them |
| 0 | Domains (ALN/numeric/synonym/table/crossover) | `03-domains` | JSON | REST `MHDOMAIN` | MXAPIDOMAIN can't ADD; MXDOMAIN can't create crossover |
| 0 | Messages | `03-messages` | JSON | REST `MXAPIMAXMESSAGE(S)` | verify |
| 1 | Objects & attributes (DB Config) | `04-objects` | JSON | REST `MXOBJECTCFG`, then apply | `maxdev dbconfig status/apply`; Admin Mode for structural changes |
| 1 | Relationships | `05-relationships` | JSON | REST `MXAPIRELATIONSHIP` | Live on save, no apply |
| 1 | Lookup maps | `05-lookupmaps` | JSON | REST, custom OS | verify |
| 1 | Conditional expressions | `06-conditions` | JSON | REST `MXAPICONDITION` | |
| 2 | App Designer screens (incl. LIBRARY, LOOKUPS) | `07-app-designer/*.xml` | XML | REST `MXAPIPRESENTATION` (merge-safe) | Extract falls back to `TMG_EXPORT_PRES` |
| 2 | App descriptions | `07-app-designer/_apps` | JSON | REST | verify |
| 2 | Conditional UI | `07-app-designer/_conditional-ui` | JSON | REST-replace `TMGMXAPICONDPROP` | 3-level tree |
| 2 | App / object-structure rights per group | `02-security/app-rights` | JSON | REST `MXAPIGROUP` (maxapps sig options) | Grant-only; works for APP/OS-type apps the `grant` type cannot write |
| 2 | Saved queries | `07-app-designer/_queries` | JSON | REST `MXAPIQUERY` | queryid left out (generated) |
| 2 | Work queues | `07-app-designer/_workqueues` | JSON | REST-replace `MXAPIWORKQUEUE` | columns/actions are child rows |
| 2 | KPIs | `19-kpi` | JSON | REST `MXAPIKPIMAIN` | Definition fields only; calculated values left out |
| 2 | Start centers | `07-app-designer/_startcenters` | JSON | REST `TMGMXSCTEMPLATE` | Keyed on contentuid; group assignment is manual. Build with `maxdev dashboard` ([dashboards](../skills/maximo-dev/references/dashboards.md)) |
| 2 | Operational Dashboard views, saved table views | `07-app-designer/_views` | JSON | REST `MXAPIVIEWMANAGER` | Proven on demo; built by `maxdev dashboard`, cards captured from the app; group access (DASHBOARDAUTH) manual |
| 2 | Data restrictions | `02-security/data-restrictions` | JSON | REST `MXAPIDATARESTRICTION` | Generated ids differ per env |
| 2 | Sig option grants | `02-security/grants` | JSON | REST `MXAPIGROUP` children | Merge, never removes |
| 2 | Attribute formulas | `08-formulas` | JSON | REST-replace `MXAPIATTRFORMULA` | |
| 2 | Object formulas | `08-formulas/object` | JSON | REST-replace `MXAPIOBJFORMULA` | extract, diff and replace-deploy verified on demo |
| 3 | Automation scripts (all launch point types) | `09-automation-scripts/<type>/` | `.py`/`.js` + scriptConfig | REST `MXAPIAUTOSCRIPT` / `MXSCRIPT` | object, attribute, action, condition, crontask, integration, library, REST handlers |
| 3 | Actions & action groups | `10-actions` | JSON | REST `MXAPIACTION` | Members sorted before groups |
| 3 | Escalations | `11-escalations` | JSON | REST `MXAPIESCALATION` | |
| 4 | Cron tasks | `12-cron-tasks` | JSON | REST `MXAPICRONTASKDEF` | |
| 5 | Workflows | `13-workflows` | JSON | REST `MXAPIWFPROCESS` | Per revision; generate with the MaximoWorkflow skill |
| 6 | Communication templates | `14-comm-templates` | JSON | REST | verify |
| 7 | Object structures, publish channels, enterprise services, invocation channels, endpoints, external systems, integration controls, JSON mappings | `15-integration/*` | JSON | REST | Endpoint secrets not exported; Kafka topics are cluster YAML (out of scope) |
| 8 | Classifications | `16-classifications` | JSON | REST `MXAPICLASSSTRUCTURE` | |
| 9 | SLAs, response plans | `17-service-mgmt/*` | JSON | REST via custom OS | verify; no OOTB structure found |
| 10 | Inspection forms | `18-mobile/inspection-forms` | JSON | REST | verify; needs OS authorisation |
| 10 | MAF / Mobile / role-based apps | `18-mobile/maf-apps/<APP>/` | app.xml, AppCustomizations.js | **Manual** publish in Application Configuration | No IBM deploy API, see [APPLICATION_DEVELOPMENT.md](APPLICATION_DEVELOPMENT.md) |
| 11 | BIRT reports | `19-reports` | registration JSON + `.rptdesign` | REST registration; design import manual | No IBM REST import for designs |
| 99 | Java customisations | `90-java` | source + customization archive | **Other**: ManageWorkspace CR | Java 17; rebuild = pod restart |
| 99 | Data loads | `91-data` | JSON/CSV | `maxdev data load` (REST BULK) | Per-item status checked |
| — | Migration Manager packages | n/a | zip | `maxdev dm create/download/upload/deploy` | For areas REST can't reach; verify `/dm/*` path on MAS 9 |

**Out of scope by design:** Work Centers (removed in MAS 9), Cognos (separate product), and CI/CD pipelines (excluded at your request).
