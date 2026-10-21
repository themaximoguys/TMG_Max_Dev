# ENG-TEST-001: Engine test, ALN domain TMGENGTEST

- **Type:** feature
- **Env:** demo
- **Status:** deploy (length fix pending approval)
- **Opened:** 2026-10-21
- **Source:** Test ticket chosen by the orchestrator under the user's request "run the engine on a test ticket on demo": "Add an ALN domain TMGENGTEST with values LOW, MEDIUM, HIGH (descriptions Low, Medium, High) so it can later be attached to attributes."
- **Manifest:** `manifests/ENG-TEST-001.yaml`

Condensed 2026-10-21 from the earlier 20-register run (git history keeps the full registers).

## Requirements
| ID | Requirement | Acceptance |
|---|---|---|
| TEC-001 | "Add an ALN domain TMGENGTEST" (maxtype ALN, length 10 per user, Q-002) | `python3 -m maxdev --env demo query MXAPIDOMAIN --where 'domainid="TMGENGTEST"' --select domainid,domaintype,maxtype,length --limit 1` returns one record: ALN, maxtype ALN, length 10 |
| TEC-002 | "with values LOW, MEDIUM, HIGH (descriptions Low, Medium, High)" | Same query with `alndomain{value,description}` returns exactly LOW/Low, MEDIUM/Medium, HIGH/High; `diff domain TMGENGTEST` reports `same` |

## Current state
| Check | Env | Command | Result |
|---|---|---|---|
| Domain absent before build | demo | `query MXAPIDOMAIN --where 'domainid="TMGENGTEST"'` and the same via MHDOMAIN | `[]` both (YORN as positive control returns 1) |
| Readiness | demo | `ping`, `doctor`, `license`, `dbconfig status` | protected false; `domain ok MHDOMAIN`; licence valid to 2027-12-31; 0 pending |
| ALN length-10 precedent | demo | `query MXAPIDOMAIN --where 'domainid="RAILSEVCOD"' --select domainid,domaintype,maxtype,length` | ALN, ALN, 10 |
| Post-apply length | demo | `query MXAPIDOMAIN --where 'domainid="TMGENGTEST"' --select ...,length,...` | length **50**, values correct |
| Why 50 | demo | `query MXINTOBJECT --where 'intobjectname="MHDOMAIN"' --select 'intobjectname,maxintobjdetail{objectname,maxintobjcols{name,intobjfldtype}}'` | MAXDOMAIN `LENGTH` is `RESTRICTED` on MHDOMAIN, so it is dropped on inbound; maxdev sent 10 (offline reproduction of the POST body) |

**Root cause (bug only):**

## Design
| Req | Ladder | Why not further left | Artifacts | Designed by |
|---|---|---|---|---|
| TEC-001 | CONFIGURATION | | ART-001 | maximo-technical-architect |
| TEC-002 | CONFIGURATION | | ART-001 | maximo-technical-architect |

## Artifacts
| Art | Type | File | Change | Skill |
|---|---|---|---|---|
| ART-001 | domain | src/03-domains/TMGENGTEST.json | NEW | maximo-dev |

## Deploy log
| Step | Env | Command | Mode | Result | Receipt | Approval (quote) | Date |
|---|---|---|---|---|---|---|---|
| 1 | demo | `python3 -m maxdev --env demo deploy --manifest ENG-TEST-001` | DRY-RUN | `would-create 1` (re-checked before apply; files unchanged) | | | 2026-10-21 |
| 2 | demo | `python3 -m maxdev --env demo deploy --manifest ENG-TEST-001 --apply` | APPLY | `created 1`; 0 FAILED; dbconfig pending 0 | .maxdev/receipts/demo/20261021-155642.json | "I accept R-004 and approve applying ENG-TEST-001 to demo" | 2026-10-21 |
| 3 | demo | `python3 -m maxdev --env demo diff domain TMGENGTEST` | RE-DIFF | `changed`: live length 50 vs repo 10 (not order-only) | | | 2026-10-21 |
| 4 | demo | `MAXIMO_OS_DOMAIN=MXDOMAIN python3 -m maxdev --env demo deploy --manifest ENG-TEST-001` | DRY-RUN | `would-update 1` (length 50 → 10 via MXDOMAIN, which does not restrict LENGTH) | | | 2026-10-21 |

## Tests
| Test | Req | Env | Command / steps | Result | Evidence |
|---|---|---|---|---|---|
| | | | | | |

## Decisions and open questions
- Q-002 (user, 2026-10-21): maxtype "ALN (mixed case)", length "10".
- Q-003 (user, 2026-10-21): attaching the domain to attributes is "Out of scope".
- Priority (user, 2026-10-21): "n/a, engine test".
- R-004 (user, 2026-10-21): accepted the D2e role-file fallback.
- Length 50 (user, 2026-10-21): "Investigate, then fix". Next: approval of step 4 with `--apply`, then RE-DIFF via MXDOMAIN must say `same`.
- Follow-up outside this ticket: route non-crossover domains to MXDOMAIN first in `maxdev/registry.yaml`; read back after json writes.
- Cleanup: TMGENGTEST stays on demo after the test; remove it by hand in the Domains app if not wanted.
