# Operations dashboards: Operational Dashboard and start centers

Manage has two dashboard front ends. Both read the same building blocks:

| Front end | App | Layout stored in | Content |
|---|---|---|---|
| **Operational Dashboard** | `OPDASHBOARD` (role-based) | `VIEWMANAGER` row (`viewtype` DASHBOARD, `componentid` NX_PV), with the app's card JSON in `content.delta` | Cards: KPI value, KPI trend, KPI comparison, work queues (single or multiple), map, table, value, gauge, threshold, favourites, quick actions, bulletin board, external content |
| **Start center** | classic home page | `SCTEMPLATE.PRESENTATION` (XML) | Portlets: result set, KPI list, KPI graph, favourites, quick insert, inbox, bulletin board |

`maxdev dashboard build <spec>` builds every supporting component from one YAML spec:

| Component | Feeds | Repo type / folder | REST |
|---|---|---|---|
| Security group (optional) | who sees it | `securitygroup` → `02-security/groups` | ok |
| Rights: OPDASHBOARD sig options, plus READ on MXAPIVIEWMANAGER, MXAPIWORKQUEUE, MXAPIWFASSIGNMENT, MXAPIPERSON and MXAPIKPIMAIN | without them, cards come up empty (BMXAA0024E) | `apprights` → `02-security/app-rights` (grant-only, never revokes) | ok (demo), through MXAPIGROUP maxapps; the `grant` type's APPLICATIONAUTH route rejects these apps (BMXAA4191E) |
| Saved queries | result sets, work queues | `query` → `07-app-designer/_queries` | ok |
| KPIs | KPI cards and portlets | `kpi` → `19-kpi` | ok |
| Work queues (+ columns, actions) | work queue, map and table cards | `workqueue` → `07-app-designer/_workqueues` | ok (demo) |
| Operational Dashboard view | the dashboard tab | `view` → `07-app-designer/_views` | ok (demo) |
| Start center template | the home page | `startcenter` → `07-app-designer/_startcenters` | ok |

Some things no REST structure can do. The generated manifest prints each as a `manual:` step:

- **Dashboard → group** (DASHBOARDAUTH) and **start center → group** (MAXGROUP.SCTEMPLATEID) both store generated ids. Set them in Security Groups.
- **Work queue person-group members** have no REST structure. Add them in Work Queue Manager (public queues need none).
- **KPI history** for trend cards and non-realtime KPIs needs the KPICronTask instance `KPINONREALTIME` scheduled and active.
- **Value / Table / Gauge card data sources** are defined in the OPDASHBOARD app through MAF Configuration (`mafapp`, manual). Prefer work queue cards, which need no data source.

## Cards: the one part built in the app first

IBM doesn't document the card JSON. OOTB dashboards keep their cards in the app's own XML, so their
VIEWMANAGER rows hold an empty delta (`{"delta":{"cards":[],"layouts":{}}, ...}`, as seen on demo).
To version cards:

1. Deploy the spec without `cards_from`. That gives an empty dashboard, plus the KPIs and queues the cards will use.
2. In Operational Dashboard, open it, then **Edit → Card gallery**. Add the cards the manifest step lists and save.
3. `maxdev extract view --where 'app="OPDASHBOARD" and viewid="<ID>"' --env X`
4. Set `opdashboard.cards_from:` to the extracted file and rebuild. From then on, the cards travel with the
   spec to every environment, and `maxdev diff` shows any card edits made in the UI.

## Build one

1. Copy `catalog/dashboards/maintenance_supervisor.yaml` to `catalog/dashboards/<name>.yaml`.
   - `name`: UPPER_CASE, used as the manifest name and the start center contentuid.
   - `security`: groups, `create_group`, `dashboard_rights` (READ, INSERT_PRIVATE, INSERT_PUBLIC,
     MANAGE_PRIVATE, HIDE_PUBLIC, DELETE_PUBLIC).
   - `queries`, `kpis`, `workqueues`.
   - `opdashboard` and/or `portlets`. One front end is enough.
2. `maxdev dashboard check <name>` lists every spec error at once.
3. `maxdev dashboard build <name>` writes the files and `manifests/<NAME>.yaml`. MCP: `build_dashboard(spec)`.
   Edit the spec and rebuild; don't hand-edit the generated files.
4. `maxdev deploy --manifest <NAME> --env X` is the dry run. Show it, get a yes, then add `--apply`.
   Deploy order: group (layer 0), then queries, work queues, KPIs, start center and view (layer 2, registry order).
5. Run `maxdev diff --path <file> --env X` on each file. Every one should show `same`.
6. Do the manifest's `manual:` steps.

## Spec rules worth knowing

- **Keep SQL portable.** Query `where` and KPI `select`/`where` run on the tenant's database.
  Resolve statuses through `synonymdomain` (`maxvalue in (...)`) so client synonyms still match,
  and write "now" as `{now}` with `database: sqlserver|oracle|db2` in the spec. The builder swaps in
  `GETDATE()`, `SYSDATE` or `CURRENT TIMESTAMP`. Don't use `:sysdate`: Maximo doesn't bind it, and the
  saved query fails with HTTP 500. `:user` is fine.
- **KPI `where` starts with `where`.** Maximo appends it to `select`, the same way as the OOTB KPIs.
- `realtime: true` (the default) calculates when the card or portlet loads. `trend: true` keeps
  KPIHISTORY for trend cards, and needs the cron step above.
- **Work queue actions** are Actions app records (`WO COMP`, ...). `completes: true` drops the record
  from the queue once the action runs. A queue refers to its query as `APP:CLAUSENAME`.
- **Start center portlets:** a `resultset` `chart` column must be one of its `columns`. `highlight` rules
  colour rows where the named column matches. With layout `NW`, column 0 is the narrow left side and 1 the wide right side.

## Gotchas

- `kpi`, `query` and `workqueue` extracts select definition fields only. Values, dates, `itemcount` and
  generated ids would show as drift in every diff.
- `startcenter` is keyed on `contentuid` (OOTB templates are `BMXAA<n>`). `view` is keyed on
  app + componentid + userid + viewid.
- `view` was proven on demo (create, then re-diff `same`). Still re-diff after the first deploy on each new tenant.
- An administrator must open Operational Dashboard once on a new tenant, so the app loads its OOTB views.
- Start center templates go through `TMGMXSCTEMPLATE` from the predeployment. Run `maxdev doctor` if `startcenter` isn't `ok`.
