---
name: maximo-dev-engine
description: How to run any IBM Maximo / MAS 9 ticket in TMG_Max_Dev end to end — feature, enhancement or bug fix — with one ticket file, design-phase specialist subagents only where a requirement needs them, and the repo skills for build, deploy and test. Use whenever the user says "work ticket X", "build this requirement", "implement this spec", "fix this bug in Maximo", "enhance <app/script/workflow>", "convert these customisations", or hands over a functional spec, TDD, Java class or TRM rule. For a single quick pull/diff/deploy with no ticket, use maximo-dev.
---

# Maximo ticket engine

One ticket, one file, one flow. Feature, enhancement and bug fix follow the same seven steps; only
step 2 differs for bugs. **Subagents are used in Design only, and only when a requirement needs a
specialist.** Everything else runs calmly in the main session, following the repo skills. Tenant
safety rules from `AGENTS.md` and `skills/maximo-dev/SKILL.md` always apply.

## The flow

| # | Step | Who | Done when |
|---|---|---|---|
| 1 | **Intake** | main | `python3 tools/new_work.py TICKET --type feature\|enhancement\|bug --env ENV` ran; requirements written verbatim with testable acceptance |
| 2 | **Current state** | main | Filtered read-only extracts/queries of everything touched are in the ticket. **Bug:** reproduced on the env, root cause stated with evidence |
| 3 | **Design** | main, + design subagents if triggered | Every requirement has a ladder position and artifact rows; open questions asked to the user |
| 4 | **Build** | main, by skill | Artifact files exist in `src/`, manifest lists them, `track_work.py` staged them |
| 5 | **Verify** | main | `validate_work.py TICKET` has no FAIL; `maxdev lint` 0 errors |
| 6 | **Deploy** | main | Dry run shown → user's explicit yes quoted → `--apply` → receipt read → **re-diff `same`** |
| 7 | **Test & close** | main | Each acceptance test run on the env with evidence (bug: regression test included); status `done` |

Steps are never skipped; for a one-artifact ticket each is a line or two. Stop and ask the user at
step 3 for any decision the source does not make, and at step 6 before every apply.

## Design subagents: when to spin one

Default: **no subagent.** The main session designs small tickets itself (≤ 5 artifacts, one area,
no open functional question). Dispatch a specialist only when a requirement triggers it:

| Trigger in the ticket | Subagent (`subagent_type`) |
|---|---|
| ≥ 3 business-process / UI / workflow requirements, or the process itself is unclear | `maximo-functional-architect` |
| Data-model change, > 5 artifacts, or current state too large to inventory inline | `maximo-technical-architect` |
| Data crosses a system boundary | `integration-architect` |
| Maps, Maximo Spatial, Esri | `gis-esri-specialist` |
| watsonx Orchestrate, MAS AI/Assist, MCP agents touching Maximo | `ai-orchestrate-specialist` |
| New groups, grants, data restrictions or an integration/AI user's permissions | `security-architect` |
| Custom Java, TRM rules or 7.6 customisations to convert | `legacy-conversion-specialist` |

How to dispatch, to keep tokens down:
- Send only the ticket path, the requirement IDs it owns and the env. Dispatch independent
  specialists in one message so they run in parallel.
- A design subagent **returns its design as text** (the Design and Artifacts rows plus questions).
  The main session writes it into the ticket. Subagents never write `src/`, the manifest or the ticket.
- One pass each. Re-dispatch only if the user's answer changes that specialist's area.
- Never in build, deploy or test. Those steps follow the skills below.

## Build: follow the skill for the artifact

| Artifact | Skill |
|---|---|
| Domains, objects, relationships, conditions, formulas, App Designer, security, integration, reports, mobile, data loads | `skills/maximo-dev/SKILL.md` |
| Automation scripts | `skills/create-automation-script/SKILL.md` |
| Java class → script | `skills/convert-java-to-script/SKILL.md` |
| TRM rule → script | `skills/convert-trm-to-script/SKILL.md` |
| Workflows, roles, person groups, actions | `skills/maximo-workflow/SKILL.md` |

Build rules that matter: one script per MBO + event; App Designer is extracted first and merged;
JSON is written with maxdev's serializer; `src/**` is git-ignored, so stage artifacts with
`python3 tools/track_work.py TICKET`.

## Bug fixes and enhancements

- **Bug.** Step 2 is the work: reproduce read-only on the named env, record the command and the
  wrong result, and state the root cause with evidence before designing. The fix is the smallest
  change to the existing artifact (`Change: MODIFY`). Step 7 must include a regression test that
  failed before the fix.
- **Enhancement.** Extract the live artifact first and modify it (`MODIFY`). Never create a second
  script on the same MBO + event, and never replace a screen.
- **Feature.** As above, usually `NEW` artifacts.

## Deploy, the part that is never shortened

1. `python3 -m maxdev --env ENV deploy --manifest TICKET`: a dry run. Paste it into the Deploy log.
2. Show the user the plan and **wait**. Record their words verbatim in the Approval column.
3. Re-check that nothing changed since the dry run, then add `--apply`. Read the receipt and report
   FAILED or not-attempted rows.
4. `python3 -m maxdev --env ENV diff --manifest TICKET` (or per path). Record it as a `RE-DIFF` row.
   **Anything but `same` means the deploy is not done**, even if the receipt says created. Find out
   why before testing.

## Files

- Ticket: one file per ticket in `work/`, from `skills/maximo-dev-engine/TICKET_TEMPLATE.md`. It is the only record.
- Manifest: `manifests/TICKET.yaml`.
- Check: `python3 tools/validate_work.py TICKET`. T-01 to T-10 are listed in its docstring.
