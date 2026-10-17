---
name: MaximoWorkflow
description: IBM Maximo workflow generator with API deployment. Converts business process descriptions into deployable Maximo workflows — generates OSLC JSON for API upload, step-by-step UI build guides, or MIF XML. Handles full dependency chain (person groups → roles → actions → subprocesses → parent). USE WHEN Maximo workflow, build workflow, create workflow, deploy workflow, workflow designer, approval workflow, routing workflow, Maximo process automation, workflow JSON, workflow XML, OSLC workflow, mxapiwfprocess, WOAPPR, POAPPR, work order approval, PO approval, status routing, escalation workflow, Maximo no-code workflow, workflow configuration, workflow deployment, upload workflow, push workflow to Maximo.
---

# MaximoWorkflow

Generate and deploy IBM Maximo workflows from natural language. Three output modes: OSLC JSON (API deployment), UI build guide, or MIF XML import.

## Workflow Routing

| Request | Workflow |
|---------|----------|
| Build/create/generate a workflow | `Workflows/Generate.md` |
| Deploy/upload/push workflow to Maximo | `Workflows/Deploy.md` |
| Explain a workflow pattern | Load `WorkflowPatterns.md`, explain |
| Help with conditions/expressions | Load `ExpressionSyntax.md`, assist |
| Troubleshoot a workflow | Load `NodeTypes.md` + `ExpressionSyntax.md`, diagnose |
| Configure roles/assignments | Load `AssignmentsAndRoles.md`, assist |
| Understand node types | Load `NodeTypes.md`, explain |

## Quick Reference

- **OSLC endpoint**: `POST /maximo/oslc/os/mxapiwfprocess?lean=1`
- **Auth**: `maxauth: <base64(user:pass)>` — always include `?lean=1`
- **Coordinates**: Grid units (-10 to +15), NOT pixels
- **Dependency order**: Person Groups → MAXROLE → Subprocesses → Parent
- **INPUT nodes**: Each choice must route to a SEPARATE TASK node with its own role
- **TITLE max**: 10 characters

## Context Files (Load On-Demand)

| File | Contents |
|------|----------|
| `OSLCDeployment.md` | OSLC JSON format, API endpoints, role creation, coordinate system, deployment scripts |
| `NodeTypes.md` | All 8 node types, connection rules, properties |
| `WorkflowPatterns.md` | 7 archetypes with parameterized templates |
| `ExpressionSyntax.md` | Bind variables, operators, 30+ condition examples |
| `AssignmentsAndRoles.md` | MAXROLE types, WFASSIGNMENT config, person groups, notifications |
| `ObjectCatalog.md` | 13+ Maximo objects with fields, statuses, actions |
| `XMLSchema.md` | MIF XML structure for Integration Framework import |

## Quality Rules

1. Never generate CUSTOMCLASS — use SQL expressions only
2. TITLE must be <= 10 characters
3. Always include validation checklist and test scenarios
4. Use `:FIELD` bind syntax with single-quoted strings
5. INPUT choices → separate TASK nodes per role (never single shared TASK)
6. Grid coordinates only (x: -10..15, y: -10..-1)
7. Omit server-generated IDs in OSLC JSON output
