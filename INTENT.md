# Intent

Why this repository exists, how the IBM Maximo framework shapes it, and the decisions that
follow. `README.md` says what it does and how to run it; `AGENTS.md` says how agents must
work in it; `docs/COVERAGE.md` is the per-area detail. When a change seems to fit the code
but not this file, stop and ask.

## Purpose

Make IBM Maximo Application Suite (MAS 9) **Manage** development code-managed and
AI-assisted, without giving up the safety a shared Maximo environment needs.

- Every configuration and code artifact is one reviewable file in Git. Files are pulled from
  and pushed to Maximo through Maximo's own REST APIs, never through direct database access.
- People and coding agents (Claude Code, Codex, Copilot, Cursor, Gemini, others) do the same
  work through the same CLI (`python3 -m maxdev`) and MCP server (`tmg-maximo-dev`).
- Feature, enhancement and bug-fix tickets follow one repeatable flow, with evidence that the
  change works on the tenant.

## Who it is for

TheMaximoGuys consultants, and the agents they direct, who build and fix Maximo configuration
on development environments for clients.

## How the Maximo framework shapes this repo

### Manage is metadata-driven, so most development is configuration

In Manage, behaviour comes mostly from records in Maximo's own configuration tables, not from
compiled code. A domain, an attribute, a relationship, a screen, a workflow and a launch point
are all rows. That is why this repo can treat almost all of Manage development as data: extract
the record, edit the file, write it back. Custom Java is the exception, kept for what the
configuration and scripting layers genuinely cannot do.

| Maximo framework layer | What we develop there | Repo area |
|---|---|---|
| Data dictionary (Database Configuration) | Objects, attributes, indexes, domains, relationships | `03-domains`, `04-objects`, `05-*` |
| Business object (MBO) framework | Conditions, formulas, automation scripts on object, attribute and action launch points | `06-conditions`, `08-formulas`, `09-automation-scripts` |
| Presentation (App Designer) | Screen XML, sig options, conditional UI, queries, start centers | `07-app-designer`, `02-security` |
| Process | Actions, escalations, cron tasks, workflows, communication templates | `10`–`14` |
| Security | Security groups, person groups, sig-option grants, data restrictions | `02-security` |
| Integration Framework (MIF) | Object structures, publish channels, enterprise services, invocation channels, endpoints, external systems, JSON mappings | `15-integration` |
| Industry and add-on features | Classifications, SLAs, response plans, inspections, Mobile, reports, KPIs | `16`–`19` |
| Java (MBO and field classes) | Only when nothing above works; converted to scripts wherever possible | `90-java` |

### Object structures are the only door

Every REST read and write goes through `/maximo/api/os/<object structure>`. On MAS 9 with
`mxe.int.enableosauth=1`, a structure is usable over REST only if it has an authorisation app,
and the caller's security group must hold that app's rights. Three consequences:

- **Use IBM's structures first.** If an IBM structure has no authorisation app, set one on it
  (`maxdev bootstrap authapps`). Do not copy it.
- **Clone only where IBM has nothing REST-usable.** Some areas ship only a Migration Manager
  `DM*` structure, which REST refuses (BMXAA1283E). Only there does the predeployment add a
  `TMG*` clone of the tenant's own definition, and a new clone needs the user's agreement first.
- **Structures can change what you send.** Inbound setting restrictions, required children and
  key rules differ per structure. For example, `MHDOMAIN` restricts `LENGTH` on inbound, so a
  domain's length is only written through `MXDOMAIN`. This is why a deploy is never trusted
  until the record is read back and compared.

`src/00_predeployment/` holds the clones and the read-only `TMG_EXPORT_PRES` script. It is
deployed once per environment, before anything else (`maxdev bootstrap`, then `maxdev doctor`).

### Deploy order follows Maximo's dependencies

Records refer to each other, so `maxdev/registry.yaml` assigns every type a layer and deploys
lower layers first:

```
0 Foundation        properties · security groups · person groups · sig options · domains · messages
1 Data model        objects/attributes (then Database Configuration apply) · relationships · lookup maps · conditions
2 Application / UI  App Designer XML · conditional UI · queries · work queues · KPIs · start centers · views · grants · restrictions · formulas
3 Business logic    automation scripts · actions · escalations
4 Scheduling        cron tasks
5 Workflow          workflow processes (roles, person groups and actions already in place)
6 Communication     communication templates
7 Integration       object structures · channels · services · endpoints · external systems · JSON mappings
8–11                classifications · service management · mobile and inspections · reports
```

A manifest (`manifests/<TICKET>.yaml`) lists one ticket's artifacts. The engine sorts them by
layer, so the author never orders them by hand.

### Each type is written the way Maximo accepts it

| Handler | Used for | Why |
|---|---|---|
| `json` | Most records | Find by key, then MERGE if it exists or POST if not |
| `replace` | Formulas, conditional UI, multi-level trees | MERGE leaves stale child rows, so the record is deleted and re-created, with rollback |
| `autoscript` | Automation scripts | Source plus a `scriptConfig` header that defines launch points and variables |
| `appxml` | App Designer screens | The live screen is backed up and the repo copy is **merged** onto it, so changes others made in the UI survive |
| `manual` | Mobile apps, BIRT designs, Java | MAS 9 has no REST deploy for them; tracked in Git, applied by the documented manual step |

Database Configuration is two steps in Maximo: save the change, then apply it. Structural
changes need Admin Mode, which logs every user out, so it is never used without explicit
approval (`maxdev dbconfig status`, then `apply`).

### The scripting runtime is Jython 2.7 on Java 17

Automation scripts run inside Manage, not on a developer's machine:

- **Python 2.7 syntax, and no Python standard library.** `re`, `json`, `os` and `datetime` fail
  at runtime; use the Java equivalents (`java.util.regex`, `java.util.Calendar`). Java-backed
  modules such as `math` and `time` are fine.
- **Java 17 APIs.** `sun.misc` and `javax.xml.bind` are gone; use `java.util.Base64` and `jakarta.xml.bind`.
- **One script per MBO and event.** Two scripts on the same launch point fight over order, so a
  new rule goes into the existing script.
- **TMG naming, headers, logging and error handling** follow
  `docs/standards/TMG_AUTOSCRIPT_STANDARDS.md`; `maxdev lint` enforces the hard rules.

### Environments are separate tenants

Each MAS environment is its own tenant with its own IDs, data and configuration drift. Facts
from one environment say nothing about another until that environment is queried. Generated
IDs (formulas, data restrictions, domain value rows) differ per environment, so files key on
business keys, never IDs. Promotion re-runs the dry run, approval and re-diff on the next
environment.

## Principles

1. **The repo is the source of truth; Maximo is the target.** Change files, then deploy.
   Investigate live with read-only queries.
2. **Nothing touches a tenant without a dry run and a person's explicit yes.** Protected
   environments (`MAXIMO_PROTECTED=true`) refuse writes, and nothing bypasses that: no curl,
   no other client, no direct IBM MCP registration, no automation-script workaround.
3. **Proof, not claims.** A deploy is done when the re-diff says `same` and the acceptance
   tests pass on that environment, not when the API says "created".
4. **Stay left on the ladder:** out of the box → configuration → automation script →
   integration → custom Java. Each step right states what failed one step to its left.
5. **Use IBM's structures first**, as above.
6. **Never break what others built.** One script per MBO and event; App Designer changes
   merge and never replace; grant deploys merge and never remove access.
7. **Keep it simple.** One ticket file, the repo skills for building, and specialist subagents
   only for design questions that need them. Add process only when a real failure shows it is needed.

## Scope

In scope:
- the `maxdev` CLI and MCP server;
- every artifact type in `maxdev/registry.yaml` (`maxdev types`);
- the predeployment that makes an environment REST-ready;
- Migration Manager packages for what REST cannot reach;
- the optional IBM MAS 9.2 MCP server, through guarded wrappers;
- the ticket engine (`skills/maximo-dev-engine/`);
- the TMG automation-script standards and Java/TRM conversion.

Not in scope:
- CI/CD, pipelines or automatic promotion beyond development environments;
- managing credentials (users own `environments/.env.*`);
- direct database access;
- loading seed or demo data nobody asked for;
- bulk copies of IBM out-of-the-box configuration into Git;
- Work Centers (removed in MAS 9) and Cognos (a separate product).

## What is committed

TMG-authored work only: tooling, skills, the predeployment, and the files a ticket's manifest
names (`tools/track_work.py`). Environment extracts stay out of Git (`src/**` is ignored).
Client configuration, credentials and tenant hostnames are never committed.

## Ownership

Proprietary to TheMaximoGuys LLC (see `LICENSE`). Connecting to Maximo requires a
TheMaximoGuys licence key.
