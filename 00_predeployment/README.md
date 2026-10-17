# 00_predeployment: deploy first, once per environment

Run this before deploying anything from `src/`. It makes Maximo's REST API able to
read and write every config area. With `mxe.int.enableosauth=1` an object structure
must have an authorisation app, and several areas have no REST-usable structure at all.

```bash
maxdev bootstrap authapps --env <env>            # dry run
maxdev bootstrap authapps --env <env> --apply    # 1. set auth app on 6 IBM MX* structures (no copies)
maxdev bootstrap --env <env>                     # dry run
maxdev bootstrap --env <env> --apply             # 2. create everything in this folder
maxdev doctor --env <env>                        # 3. confirm every area is ok
```

## Contents

**`15-integration/object-structures/`** holds the TMG structures. Each one is created only where IBM ships no REST-usable structure; in most cases IBM has only a Migration Manager DM* version, which the API refuses.

| Structure | Cloned from | Auth app | Unlocks |
|---|---|---|---|
| TMGMXAPICONDITION | DMCONDITION | CONDEXPMGR | Conditional expressions |
| TMGMXAPICONDPROP | DMCTRLGROUP | CONDEXPMGR | Conditional UI |
| TMGMXAPIESCALATION | DMESCALATION | ESCALATION | Escalations |
| TMGMXAPIGRANT | DMMAXGROUP (group + grants) | SECURGROUP | Sig-option grants |
| TMGMXAPIPRESENTATION | MAXPRESENTATION | DESIGNER | App Designer screens |
| TMGMXAPIRELATIONSHIP | DMMAXRELATIONSHIP | CONFIGUR | Relationships |
| TMGMXAPIROLE | DMROLE | ROLE | Roles |
| TMGMXAPISIGOPTION | DMSIGOPTION | DESIGNER | Sig options |
| TMGMXIFACEIN | DMMAXIFACEIN | INTSRV | Enterprise services |
| TMGMXLOOKUPMAP | DMMAXLOOKUPMAP | CONFIGUR | Lookup maps |
| TMGMXSCTEMPLATE | DMSCTEMPLATE | STARTCNTR | Start centers |

**`09-automation-scripts/library/TMG_EXPORT_PRES.py`** is a read-only REST handler that exports App Designer XML. It has no launch point.

## How the definitions are built

`maxdev bootstrap generate --env <env>` rebuilds these JSON files from the target tenant's own DM*/MX* definitions. The plan lives in `maxdev/bootstrap_gen.py`:
- `PLAN` lists the clones.
- `AUTHAPP_PATCH` lists the IBM structures that only need an auth app set.

## Undo

Delete the TMG* records in Object Structures, and the TMG_EXPORT_PRES script.
