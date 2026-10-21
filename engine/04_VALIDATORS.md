# Validators: computed consistency checks

> A **gate** is attested with evidence. A **validator** is computed. A gate fails because
> someone has not done something. A validator fails because two artifacts disagree: each file
> looks fine on its own, but together they don't match.
>
> `python3 tools/validate_work.py <TICKET>` runs every computed validator below and prints PASS,
> FAIL or SKIP (the register has no rows yet) for each. Run it at D5, before D6, and before D10.
> Any FAIL blocks the next 🔴 gate. Record the run in `FINDINGS_LOG.md`.

---

## 1. Traceability (computed)

| ID | Assertion | Joins |
|---|---|---|
| `W-01` | Every requirement ID is unique, uses a §1 prefix, and has acceptance criteria | Requirement register |
| `W-02` | Every requirement (not `DEFERRED`/`REJECTED`) has a classification row | Requirement ↔ Classification |
| `W-03` | Every classification row uses a §2 ladder value; every position right of `CONFIGURATION` has a departure reason | Classification |
| `W-04` | Every non-`OOB` classification row names ≥1 artifact ID that exists in the artifact register | Classification ↔ Artifact |
| `W-05` | Every artifact row traces to ≥1 requirement ID that exists | Artifact ↔ Requirement |

## 2. Repository consistency (computed)

| ID | Assertion | Joins |
|---|---|---|
| `W-10` | Every artifact row (not `NO-CHANGE`) has a file under `src/` that exists | Artifact ↔ `src/` |
| `W-11` | Each artifact file maps (by folder) to the registry type in its row | Artifact ↔ `maxdev/registry.yaml` |
| `W-12` | Each artifact row's owner is the `roster.yaml` owner of its type | Artifact ↔ Roster |
| `W-13` | Every deployable artifact file is resolved by `manifests/<TICKET>.yaml` | Artifact ↔ Manifest |
| `W-14` | Every file the manifest resolves is in the artifact register (no unregistered change) | Manifest ↔ Artifact |
| `W-15` | Script artifacts pass `maxdev lint` with 0 errors | Artifact ↔ TMG standards |
| `W-16` | Change kind uses a §3 value; `RETIRE` rows cite the user's approval | Artifact |
| `W-17` | Every deployable artifact file is tracked by git (`tools/track_work.py <TICKET>`; `src/**` is otherwise ignored) | Artifact ↔ git index |

## 3. Delivery evidence (computed)

| ID | Assertion | Joins |
|---|---|---|
| `W-20` | Every `APPLY` row in the deployment plan has a preceding `DRY-RUN` row for the same env | Deployment plan |
| `W-21` | Every `APPLY` row has an approval quote and date | Deployment plan |
| `W-22` | Every `APPLY` row's receipt path exists under `.maxdev/receipts/<env>/` | Deployment plan ↔ receipts |
| `W-23` | Every requirement with status `VERIFIED` has ≥1 test with result `PASS` and evidence | Requirement ↔ Test |
| `W-24` | Every test references existing requirement IDs and uses a §5 result | Test ↔ Requirement |
| `W-25` | No `OPEN` `BLOCKER` finding remains | Findings log |
| `W-26` | Every `CNV` requirement has a conversion register row with a §4 disposition | Requirement ↔ Conversion |
| `W-27` | Every `INT`/`GIS`/`AI`/`DAT`/`SEC` requirement has a row in its specialist register | Requirement ↔ Specialist registers |
| `W-28` | At D10: no `[[PLACEHOLDER` remains in `DESIGN_DOC.md` or `HANDOFF.md` | Writer output |

## 4. Attested (human; recorded in `FINDINGS_LOG.md`)

| ID | Assertion |
|---|---|
| `W-40` | No artifact adds a second script on an MBO + event that already has one (checked against `CURRENT_STATE_INVENTORY.md`) |
| `W-41` | App Designer artifacts were extracted from the target env before editing and deploy as a merge |
| `W-42` | No tenant fact in any register lacks a command, output and env (provenance tier 3) |
| `W-43` | Each environment named in the deployment plan matches the one the user named |
| `W-44` | Each Admin Mode or `--force-replace` use has its own approval quote |
