# Lifecycle: the gate ladder

> **The lifecycle is a dependency graph, not a timeline.** Phases are ordered because their outputs
> feed each other. A phase is done when its gate clears with evidence: a file path or command
> output, an owner and a date, recorded in `work/<TICKET>/WORK_CHECKLIST.md`.
>
> **🔴 gates stop work.** An open red gate blocks everything downstream. It is never carried forward
> as a risk. **🟠** applies only in the stated circumstances. **🟢** shapes quality without
> stopping work.

---

## The ladder

```
 D0  INTAKE ──────────────────── 🔴 work package scaffolded · sources registered · target env named
      │
 D1  REQUIREMENTS ────────────── 🔴 every requirement has an ID, verbatim text, acceptance criteria
      │
      ├────────────────────────────────────────────┐
      ▼                                            ▼
 D2  CURRENT STATE 🔴                       D2e ENVIRONMENT READINESS 🔴
      filtered extracts of what exists ·         ping · doctor · predeployment ·
      script ownership per MBO+event ·           protection flag · licence
      legacy inventory dispositioned
      │                                            │
      └─────────────────────┬──────────────────────┘
                            ▼
 D3  SOLUTION DESIGN ─────── 🔴 every requirement classified on the ladder · every non-OOB row
      │                          has artifacts · specialists' registers complete · pairs reconciled
      ▼
 D4  BUILD ───────────────── 🟢 owners build their types in src/ (in parallel) · manifest updated
      │
 D5  STATIC VALIDATION ───── 🔴 validate_work · lint · tests · component check · red-team static review
      │
 D6  DRY RUN ─────────────── 🔴 diff + dry-run deploy of the manifest on the named env, recorded
      │
 D7  APPROVAL ────────────── 🔴 the user's explicit yes to that plan, quoted with date (never self-approved)
      │
 D8  APPLY + VERIFY ──────── 🔴 apply · receipt · no FAILED rows · re-diff `same` · dbconfig · manual steps
      │
 D9  TEST ────────────────── 🔴 every requirement's acceptance tests executed on the env, with evidence
      │
 D10 HANDOFF ─────────────── 🟠 design doc · handoff notes · promotion plan (next env re-enters at D2e)
```

Promotion to another environment re-runs **D2e → D6 → D7 → D8 → D9** for that environment. An
approval for `demo` does not authorise `test` or `prod`.

---

## Phase detail

| D | Phase | Owner | Entry | Exit (the gate) | Produces in `work/<TICKET>/` |
|---|---|---|---|---|---|
| 0 | Intake | `work-package-manager` | A request exists | `tools/new_work.py` run; each source document registered; target env named by the user (or `[[PLACEHOLDER]]` and no tenant work) | `WORK_CHECKLIST.md`, `SOURCE_REGISTER.md` |
| 1 | Requirements | `requirements-analyst` | D0 clear | Each requirement has an ID with a prefix, verbatim text, source reference and testable acceptance criteria; conflicts logged as questions | `REQUIREMENT_REGISTER.md` |
| 2 | Current state | `maximo-technical-architect` (+ `legacy-conversion-specialist`) | D1 clear | Filtered extracts of each object, app, script, workflow the requirements touch; existing script per MBO+event recorded; each legacy item dispositioned | `CURRENT_STATE_INVENTORY.md`, `CONVERSION_REGISTER.md` |
| 2e | Environment readiness | `environment-steward` | Env named | `ping` and `doctor` output recorded; needed types `ok`; predeployment state known; `protected` flag stated | `ENVIRONMENT_READINESS.md` |
| 3 | Solution design | Functional + technical architects with integration, GIS, AI, security specialists | D1, D2 clear | Every requirement has a classification row; every non-OOB row has artifact rows with an owner; specialist registers complete; cross-validation pairs reconciled | `SOLUTION_CLASSIFICATION.md`, `ARTIFACT_REGISTER.md`, specialist registers |
| 4 | Build | Type owners (`roster.yaml` `types`) | D3 clear for that artifact | Each artifact file exists in `src/`, built by its owner using the repo skill; manifest lists it | `src/…`, `manifests/<TICKET>.yaml` |
| 5 | Static validation | `dev-red-team-reviewer` | D4 complete | `tools/validate_work.py <TICKET>` has no FAIL; `maxdev lint` 0 errors; unit tests and component check pass; static findings closed | `FINDINGS_LOG.md` |
| 6 | Dry run | `release-manager` | D5, D2e clear | `maxdev diff` and `maxdev deploy --manifest <TICKET> --env E` (no `--apply`) output recorded with date | `DEPLOYMENT_PLAN.md` |
| 7 | Approval | `release-manager` records; **the user decides** | D6 clear | The user's words approving that plan for that env, quoted with date; Admin Mode or `--force-replace` approved separately if used | `DEPLOYMENT_PLAN.md` |
| 8 | Apply + verify | `release-manager` | D7 clear | Apply run; receipt path recorded; no FAILED/not-attempted rows (or reported and reopened); re-diff `same`; `dbconfig status` clean; manual steps done or listed as pending with owner | `DEPLOYMENT_PLAN.md` |
| 9 | Test | `test-engineer` | D8 clear | Each requirement has ≥1 test; each test PASS/FAIL with evidence from that env; FAIL reopens D3 or D4 | `TEST_REGISTER.md` |
| 10 | Handoff | `technical-writer` + `work-package-manager` | D9 clear | Design doc and handoff notes written from the registers; open items, rollback and promotion plan stated | `DESIGN_DOC.md`, `HANDOFF.md` |

---

## Preconditions for build (D4)

A developer does not open a `src/` file for a work package until all of these hold for that artifact:

1. Its requirement has a row in `REQUIREMENT_REGISTER.md` with acceptance criteria.
2. The current state of the record it touches was extracted (or recorded as "does not exist" with the command that showed it).
3. Its classification row names the ladder position and, if right of OOB, the departure reason.
4. Its artifact row names type, name, file path, change kind and the owner from `roster.yaml`.
5. For scripts: the existing script for that MBO+event is known, and the rule goes into it if one exists.
6. For App Designer: the live screen was extracted, and the change is a merge.
7. Any specialist register the row depends on (integration, GIS, AI, security, data) is complete for that row.

## Reducing depth

A one-line domain change still passes every gate, at the depth it needs: one requirement row, one
extract, one classification row, one artifact row, one dry run, one approval, one test. The engine
scales down by doing less in each phase, never by skipping a phase.
