# Work Checklist: {{TICKET}}

Instantiated {{DATE}}. **Owner: work-package-manager.** Tick a gate only with evidence: a file
path or command output, the owner, and the date. Gate definitions: `engine/01_LIFECYCLE.md`.

- **Ticket:** {{TICKET}}
- **Request (user's words):** [[PLACEHOLDER: the request as given | work-package-manager]]
- **Target environment(s), as named by the user:** {{ENV}}
- **Manifest:** `manifests/{{TICKET}}.yaml`

| Gate | | Owner agent | Evidence | Date |
|---|---|---|---|---|
| D0 Intake 🔴 | ⬜ | work-package-manager | | |
| D1 Requirements 🔴 | ⬜ | requirements-analyst | | |
| D2 Current state 🔴 | ⬜ | maximo-technical-architect, legacy-conversion-specialist | | |
| D2e Environment readiness 🔴 | ⬜ | environment-steward | | |
| D3 Solution design 🔴 | ⬜ | functional + technical architects, specialists | | |
| D4 Build 🟢 | ⬜ | type owners (`engine/roster.yaml`) | | |
| D5 Static validation 🔴 | ⬜ | dev-red-team-reviewer | | |
| D6 Dry run 🔴 | ⬜ | release-manager | | |
| D7 Approval 🔴 | ⬜ | the user (recorded by release-manager) | | |
| D8 Apply + verify 🔴 | ⬜ | release-manager | | |
| D9 Test 🔴 | ⬜ | test-engineer | | |
| D10 Handoff 🟠 | ⬜ | technical-writer, work-package-manager | | |

## Dispatch log

Every register is filled by dispatching to its owner. One line per dispatch.

| Date | Agent | Task | Output |
|---|---|---|---|
| | | | |

## Depth reductions

Phases done at reduced depth, and why (never skipped):

-
