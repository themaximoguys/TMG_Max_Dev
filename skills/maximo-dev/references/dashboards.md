# Operational dashboards

In Manage, an operational dashboard is a **start center**: a template of portlets that each read
other configuration records. `maxdev dashboard` builds the whole set from one YAML spec, so the
dashboard is reviewed and deployed like any other change.

| Portlet (spec `type`) | Reads | Repo type / folder |
|---|---|---|
| `resultset` | a saved query (app + clausename + owner) | `query` → `07-app-designer/_queries` |
| `kpilist`, `kpigraph` | KPI definitions by name | `kpi` → `19-kpi` |
| `favorites`, `quickinsert` | application names | (none) |
| `inbox`, `bulletin` | workflow assignments, bulletins | (none) |
| (separate app, WQMANAGER) | a saved query | `workqueue` → `07-app-designer/_workqueues` |
| the template itself | presentation XML | `startcenter` → `07-app-designer/_startcenters` |

The Operational Dashboard app (`OPDASHBOARD`) and role-based app table views store layouts in
VIEWMANAGER. Extract and diff them with the `view` type. Their card definitions belong to the app,
so build those in the app and pull them; don't write the `content` JSON by hand.

## Build one

1. Copy `catalog/dashboards/maintenance_supervisor.yaml` to `catalog/dashboards/<name>.yaml`.
   Set `name` (UPPER_CASE; it becomes the start center contentuid and the manifest name), `description`,
   `owner`, `groups`, then the `queries`, `kpis`, `workqueues` and `portlets`.
2. `maxdev dashboard check <name>` lists every spec error at once.
3. `maxdev dashboard build <name>` writes the files and `manifests/<NAME>.yaml`.
   MCP: `build_dashboard(spec)`. Edit the spec and rebuild; don't hand-edit the generated files.
4. `maxdev deploy --manifest <NAME> --env X` is the dry run. Show it, get a yes, then add `--apply`.
   The engine deploys queries and KPIs before the start center that refers to them (all layer 2, registry order).
5. `maxdev diff --path <file> --env X` for each file should show `same`.
6. Do the manifest's `manual:` steps. Assigning a template to a security group uses the generated
   `sctemplateid`, so it happens in Security Groups. Users pick the template up at next login or
   with **Update Start Center**.

## Spec rules worth knowing

- **Keep SQL portable.** Query `where` and KPI `select`/`where` run on the tenant's database.
  Resolve statuses through `synonymdomain` (`maxvalue in (...)`) so client synonyms still match,
  and write "now" as `{now}` with `database: sqlserver|oracle|db2` in the spec. The builder swaps in
  `GETDATE()`, `SYSDATE` or `CURRENT TIMESTAMP`. Don't use `:sysdate`: Maximo doesn't bind it, and the
  saved query fails with HTTP 500. `:user` is fine.
- **KPI `where` starts with `where`.** Maximo appends it to `select`, the same way as the OOTB KPIs.
- `realtime: true` (the default) calculates when the portlet loads. Set it `false` for heavy SQL
  and let the KPI cron task refresh it. The manifest then adds a step to check that the cron task is active.
- A `resultset` `chart` column must be one of its `columns`. `highlight` rules colour rows where
  the named column matches (`expression` `=`, `<`, `>`, `!=`).
- Layout `NW`: column 0 is the narrow left side and column 1 the wide right side. Order within a
  column follows the spec.

## Gotchas

- `kpi` and `query` extracts select definition fields only. KPI values, dates and `queryid` are
  recalculated or generated, so they would show as drift in every diff.
- `startcenter` is keyed on `contentuid`. OOTB templates use `BMXAA<n>`, and TMG templates use the spec `name`.
- `workqueue` and `view` are `status: verify`. Extract and diff work, but confirm the first deploy
  on each tenant by re-diffing it.
- Start center templates go through `TMGMXSCTEMPLATE` from the predeployment. Run `maxdev doctor`
  if `startcenter` isn't `ok`.
