# Generate Workflow from Description

Convert a natural language business process description into a deployable Maximo workflow.

## Step 1: Extract Requirements

From the user's description, identify:

1. **Object**: Which Maximo object? Load `ObjectCatalog.md` if unclear.
2. **Archetype**: Load `WorkflowPatterns.md` and classify (Approval, Status Routing, Record Creation, Escalation, User Management, Email Processing, Composite).
3. **Conditions**: What decisions/branches exist?
4. **Assignments**: Who handles tasks? (roles, person groups, supervisors)
5. **Actions**: What happens at each step? (status changes, notifications)
6. **Escalation**: Any time limits?

## Step 2: Build Node Graph

Load `NodeTypes.md` for connection rules. Critical constraints:
- TITLE max 10 characters
- START: 1 positive exit, 0 negative
- CONDITION: 1 positive + 1 negative
- TASK: 1 positive + 1 negative
- INPUT: 1+ positive, 0 negative (each choice → SEPARATE TASK node with own role)
- STOP: 0 exits

## Step 3: Generate Conditions

Load `ExpressionSyntax.md`. Use `:FIELDNAME` syntax, single-quoted strings.

## Step 4: Configure Assignments

Load `AssignmentsAndRoles.md`. Map each TASK to a role/person group.

## Step 5: Choose Output Format

| Format | When to Use | Reference |
|--------|-------------|-----------|
| **OSLC JSON** (preferred) | API deployment via `mxapiwfprocess` | `OSLCDeployment.md` |
| **Step-by-step guide** | Admin builds manually in Workflow Designer UI | Inline instructions |
| **MIF XML** | Integration Framework import | `XMLSchema.md` |

### OSLC JSON Output

Generate JSON matching the `mxapiwfprocess` OSLC format:
- Actions nested inside owning nodes (not separate)
- Grid coordinates (x: -10..15, y: -10..-1), NOT pixels
- Omit server-generated IDs (wfprocessid, wfnodeid, etc.)
- Include dependency checklist (person groups, roles, actions needed)

### Step-by-step Guide Output

Structure as: Prerequisites → Process Setup → Nodes → Connections → Assignments → Validation Checklist → Test Scenarios → Activation Steps.

### MIF XML Output

Load `XMLSchema.md` and generate valid `SyncMXWFPROCESS` XML.

## Step 6: Generate Deployment Plan

For any output format, include:
1. **Dependency checklist** — person groups, roles, actions, comm templates
2. **Upload order** — subprocesses first, parent last
3. **Test scenarios** — happy path + rejection path minimum
4. **Activation steps** — validate → enable → activate → auto-initiate
