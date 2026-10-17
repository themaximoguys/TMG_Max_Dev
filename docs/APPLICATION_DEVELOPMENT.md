# Application development in MAS 9: what goes where

This page says how each kind of Maximo development is built and deployed in this repo. Sources are IBM docs and community work, researched 2026-10-16. Unverified items are marked ⚠.

## 1. Automation scripts: the default for business logic

- **Write a new script**
  1. `maxdev templates` lists the 14 TMG script kinds, each in `mxlogger` and `service` logging styles.
  2. `maxdev build <kind> --object WORKORDER [--attr FIELD | --name N]` writes the script to `src/09-automation-scripts/<type>/`. It uses the TMG template and the TMG name, for example `TMG_WORKORDER.OBJ.SAVE.BEFORE` or `WORKORDER.WOPRIORITY.VALIDATE`.
  3. Fill in the business placeholders: `{PURPOSE_DESCRIPTION}`, the `{BUSINESS_RULE_n}` items, and the logic block.
  4. `maxdev lint` checks the script against the TMG hard rules: Jython 2.7 syntax, SqlFormat for SQL, MboSet close, one logging style, Java 17 APIs, no `setValue` in INIT, and no unfilled placeholders. Deploy refuses any script with lint errors.
  5. Run `maxdev deploy autoscript NAME` for a dry run, then add `--apply`.
- **File format.** Each file holds the real Jython/JS source followed by the TMG `scriptConfig = {...}` dict. On deploy, maxdev maps that dict to `MXAPIAUTOSCRIPT` and sends only the source, without the dict. Re-extracting keeps the TMG format and the documentation keys (`cronSetup`, `integrationBinding`).
- **Not launch points.** Cron scripts bind through a SCRIPTCRONTASK instance (`src/12-cron-tasks`). Integration exits bind by name (`PUBLISH.<CHANNEL>.<EXIT>.OUT`, `SYNC.<SERVICE>.<EXIT>.IN`). maxdev therefore never sends these as launch points.
- **Reference material**:
  - `docs/standards/TMG_AUTOSCRIPT_STANDARDS.md` is the authority.
  - `docs/autoscript/` covers patterns, naming, error handling, launch points, optimisation and the knowledge base.
  - `catalog/samples/` holds 69 working examples.
- **Languages.** Jython 2.7 is the default. Nashorn JavaScript is supported, but on Java 17 it runs through OpenJDK Nashorn ⚠. REST handlers are scripts called at `/maximo/api/script/<NAME>`.

## 2. Java customisations: convert to scripts first

1. **Analyse.** `maxdev java analyze path/To/Class.java` reports:
   - the class family (MBO, field class, cron task, action, integration exit, bean);
   - which TMG template each method maps to;
   - blockers: threads, direct JDBC, `javax.xml.bind`/`sun.misc`, RMI, UI beans.
2. **Convert.** Use the `convert-java-to-script` skill, with `docs/autoscript/JAVA_TO_PYTHON.md` and the prompt guides in `docs/autoscript/prompts/`. Merge each class into the existing script for its MBO and event; don't create a second script for the same pair.
3. **Code that must stay Java** goes in `src/90-java/<module>/`:
   - Layout: source, `product.xml`, `tools/maximo/en/<product>/V*.dbc`, and the `applications/maximo/...` tree.
   - Build: Java 17 is mandatory from MAS 9.1 (March 2025). Code that uses `com.amazonaws.*` must move to AWS SDK v2.
   - Deploy: zip the tree and host it on HTTPS or S3/COS. Add the zip to `ManageWorkspace.spec.settings.customizationList[]`. The operator then rebuilds the images and restarts the pods, which is an outage. maxdev does not do this step, because it is a cluster change.
4. **TRM rules / XML / SCL** use the `convert-trm-to-script` skill and `docs/autoscript/TRM_TO_PYTHON.md`.

## 3. Workflow

- **Generate.** The `maximo-workflow` skill (`.claude/skills/maximo-workflow/`) turns a process description into `MXAPIWFPROCESS` JSON. It handles the whole dependency chain: person groups, roles, actions, sub-processes, then the parent process.
- **Store and deploy.** Save the generated JSON in `src/13-workflows/`; person groups go in `src/02-security/person-groups/`, and actions and roles in their own folders. Then run `maxdev deploy --manifest ...`.
- **Order.** The registry deploys the dependencies first. Each deploy creates a new revision, which you then enable and activate.

## 4. App Designer (classic Manage UI)

- **Workflow.** Run `maxdev extract appxml WOTRACK`, edit `src/07-app-designer/WOTRACK.xml`, then `maxdev deploy`.
- **Safety.** Deploy backs up the live screen and merges your copy onto it, so elements added in the UI are kept. It then reads the screen back to confirm the write landed.
- **Related.** Sig options, conditional UI, saved queries and start centers each have their own folders.
- **Work Centers** were removed in MAS 9. Don't build new ones.

## 5. MAF / Maximo Mobile / role-based apps (Graphite)

- **What it is.** Technician, Inspections, Service Request and the other role-based apps. In MAS 9.1 the MAF Configuration application was renamed **Application Configuration** and now runs in-cluster.
- **What you can customise.** Only `app.xml`, `AppCustomizations.js`, extended controllers and CSS (from 9.0). Changing out-of-the-box controllers is unsupported.
- **Store** in `src/18-mobile/maf-apps/<APP>/`.
- **Build and deploy.** Application Configuration builds the app when you preview or publish it. IBM's early-access **Local Dev Mode** extension for VS Code / IBM Bob gives live preview and XML diff on MAS 9.1.21+ and 9.2.1+.
- **No IBM API or CLI exists for deploying these apps.** Publishing is manual. To move an app between environments, use Migration Manager (`maxdev dm`).

## 6. Integration, reports, data

- **Integration.** Object structures, channels, services, endpoints and JSON maps all deploy over REST (`src/15-integration`). Kafka topics are cluster YAML and are out of scope.
- **BIRT reports.** Registration rows deploy over REST (`src/19-reports`). The `.rptdesign` files are imported through Report Administration, because there is no IBM REST import ⚠.
- **Data.** `maxdev data export|load` uses REST BULK and checks the status of each item. No demo or seed data is loaded at this stage.
