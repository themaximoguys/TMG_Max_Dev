# Maximo Workflow Pattern Templates

7 parameterized workflow archetypes covering 95%+ of real-world Maximo workflow requests. Each template defines the node graph, connections, and configuration points.

---

## Pattern 1: Approval

The most common Maximo workflow pattern. Routes a record through one or more approval levels based on conditions.

### 1a: Single-Level Approval

**Use when:** One person/group approves, with approve/reject outcomes.

**Node Graph:**
```
START → CONDITION → [positive] → TASK (Approver) → [positive] → STOP (Approved)
                  → [negative] → STOP (Auto/Skip)    ↓ [negative]
                                                   STOP (Rejected)
```

**Nodes:**

| # | Type | Title | Description | Config |
|---|------|-------|-------------|--------|
| 1 | START | START | Start | — |
| 2 | CONDITION | CHKCRIT | Check approval criteria | CONDITION: `{criteria_expression}` |
| 3 | TASK | APPROVE | {approver_description} | APP: {app}, ROLEID: {role}, TIMELIMIT: {hours}, FIRSTCOMPLETE: 1 |
| 4 | STOP | APPROVED | Approved | — |
| 5 | STOP | REJECTED | Rejected | — |
| 6 | STOP | SKIPPED | Auto-approved (criteria not met) | — |

**Connections:**

| From | To | Positive | Action | Instruction |
|------|----|----------|--------|-------------|
| 1→2 | START→CONDITION | Yes | — | — |
| 2→3 | CONDITION→TASK | Yes | {set_wappr_action} | Requires approval |
| 2→6 | CONDITION→STOP(Skip) | No | {auto_approve_action} | Auto-approved |
| 3→4 | TASK→STOP(Approved) | Yes | {approve_action} | Approved |
| 3→5 | TASK→STOP(Rejected) | No | {reject_action} | Rejected |

**Parameters to fill:**
- `{criteria_expression}`: e.g., `:TOTALCOST > 5000`
- `{approver_description}`: e.g., "Supervisor Approval Required"
- `{app}`: e.g., WOTRACK, PO, PR
- `{role}`: e.g., SUPERVISOR, MAINT_MGRS (person group)
- `{hours}`: Escalation time limit, e.g., 24.00
- `{set_wappr_action}`: Action to set status to Waiting Approval
- `{approve_action}`: Action to approve (e.g., APPR)
- `{reject_action}`: Action to reject/cancel
- `{auto_approve_action}`: Action when criteria not met (direct approve or different path)

---

### 1b: Multi-Level Threshold Approval

**Use when:** Different approvers based on cost thresholds or other criteria.

**Node Graph:**
```
START → COND1 (>$10K) → [pos] → TASK (VP) → [pos] → STOP (Approved)
                       → [neg]                ↓ [neg] → STOP (Rejected)
                          ↓
        COND2 (>$1K)  → [pos] → TASK (Manager) → [pos] → STOP (Approved)
                       → [neg]                    ↓ [neg] → STOP (Rejected)
                          ↓
                       STOP (Auto-Approved)
```

**Nodes:**

| # | Type | Title | Description | Config |
|---|------|-------|-------------|--------|
| 1 | START | START | Start | — |
| 2 | CONDITION | HIGH$ | Over $10,000? | `:TOTALCOST > 10000` |
| 3 | CONDITION | MED$ | Over $1,000? | `:TOTALCOST > 1000` |
| 4 | TASK | VPAPPR | VP Approval | ROLEID: {vp_role} |
| 5 | TASK | MGRAPPR | Manager Approval | ROLEID: {mgr_role} |
| 6 | STOP | APPROVED | Approved | — |
| 7 | STOP | REJECTED | Rejected | — |
| 8 | STOP | AUTOAPPR | Auto-Approved (under $1K) | — |

**Connections:**
| From→To | Pos | Action | Note |
|---------|-----|--------|------|
| 1→2 | Yes | — | Start to first check |
| 2→4 | Yes | WAPPR | High cost → VP |
| 2→3 | No | — | Not high → check medium |
| 3→5 | Yes | WAPPR | Medium cost → Manager |
| 3→8 | No | APPR | Low cost → auto-approve |
| 4→6 | Yes | APPR | VP approved |
| 4→7 | No | REJECT | VP rejected |
| 5→6 | Yes | APPR | Manager approved |
| 5→7 | No | REJECT | Manager rejected |

**Scaling:** Add more CONDITION→TASK pairs for additional levels. Each condition checks a progressively lower threshold.

---

### 1c: Recursive/Dynamic Approval

**Use when:** Approval hierarchy is configured in Security Groups > Limits and Tolerances, not hard-coded.

**Node Graph:**
```
START → CONDITION (within user limit?) → [pos] → STOP (Approved)
                                        → [neg] → TASK (Route to supervisor)
                                                    ↓ [pos] → loops back to CONDITION
                                                    ↓ [neg] → STOP (Rejected)
```

**Key expression:**
```sql
:TOTALCOST <= (
  SELECT MAX(lt.polimit)
  FROM groupuser gu
  LEFT JOIN limittolerance lt ON lt.groupname = gu.groupname AND lt.orgid = :ORGID
  WHERE gu.userid = :&user&
)
```

**This pattern uses a subprocess** that calls itself recursively via escalation to the supervisor chain.

---

## Pattern 2: Status Routing

**Use when:** The workflow path depends on the record's current status. Each status maps to a different action or assignment.

**Node Graph:**
```
START → COND1 (:STATUS='WAPPR') → [pos] → TASK (Approval) → paths...
                                 → [neg]
                                    ↓
        COND2 (:STATUS='APPR')  → [pos] → TASK (Schedule) → paths...
                                 → [neg]
                                    ↓
        COND3 (:STATUS='INPRG') → [pos] → TASK (Complete) → paths...
                                 → [neg] → STOP (Unknown status)
```

**Key principle:** Each condition checks for a specific status value. The workflow guides the record through its lifecycle by assigning appropriate tasks at each stage.

**Best practice:** Status-driven workflows should change the record's status on each transition, so the same workflow can be re-initiated to move the record to the next stage.

---

## Pattern 3: Record Creation

**Use when:** A record of one type should automatically create a record of another type.

### 3a: Service Request to Work Order (WR2WO)

**Node Graph:**
```
START → CONDITION (criteria) → [pos] → INTERACT (Create WO) → STOP
                              → [neg] → STOP (No WO needed)
```

**Nodes:**

| # | Type | Title | Description | Config |
|---|------|-------|-------------|--------|
| 1 | START | START | Start | — |
| 2 | CONDITION | CHKPRI | Check priority/criteria | `:REPORTEDPRIORITY = 1` |
| 3 | INTERACT | CREATEWO | Create Work Order | APP: WOTRACK, RELATION: NEWWORKORDER |
| 4 | STOP | DONE | Complete | — |
| 5 | STOP | SKIP | No creation needed | — |

**Interaction node config:**
- **APP:** WOTRACK (for WO), SR (for SR), etc.
- **RELATION:** NEWWORKORDER, NEWSR, NEWINCIDENT, NEWPROBLEM, NEWCHANGE
- **DIRECTIONS:** Instructions shown to user about the new record

### 3b: Automated Creation (No User Interaction)

For fully automated creation, use a **Set Value action** or **Action Group** on the connection line instead of an Interaction node. The action executes the standard Maximo "Create Work Order" action programmatically.

---

## Pattern 4: Escalation

**Use when:** Tasks must be completed within a time limit, with notification/reassignment if overdue.

**Node Graph:** Same as Approval, but TASK nodes include:
- **TIMELIMIT:** Hours before escalation (e.g., 4.00 for 4 hours)
- **ESCROLE:** Escalation role in WFASSIGNMENT
- **EMAILNOTIFICATION:** 1 (send email on assignment)
- **TEMPLATEID:** Communication template for notification

**Escalation on TASK node:**
```
TASK node configured with:
  TIMELIMIT = 4.00 hours
  Assignment 1: ROLEID = MAINT_SUPV (primary assignee)
  Assignment 2: ROLEID = MAINT_MGR, ESCROLE (escalation if overdue)
```

**Notification on connection:**
Add WFNOTIFICATION to the connection line entering the task, or configure EMAILNOTIFICATION=1 on the WFASSIGNMENT.

---

## Pattern 5: User Management

**Use when:** Approving/rejecting user accounts (LDAP auto-created or self-registered).

**Object:** MAXUSER

**Node Graph:**
```
START → TASK (Admin Review) → [pos: Activate User action on connection] → STOP (Active)
                             → [neg: Block User action on connection] → STOP (Blocked)
```

**Nodes:**

| # | Type | Title | Description | Config |
|---|------|-------|-------------|--------|
| 1 | START | START | Start | — |
| 2 | TASK | ADMRVW | Admin Review | APP: MAXUSER, ROLEID: {security_admin_group} |
| 3 | STOP | ACTIVE | User Activated | — |
| 4 | STOP | BLOCKED | User Blocked | — |

**Connections:**
| From→To | Pos | Action | Note |
|---------|-----|--------|------|
| 1→2 | Yes | — | Start to review |
| 2→3 | Yes | ACTIVATE | Positive exit activates user (MAXUSER.STATUS → ACTIVE) |
| 2→4 | No | BLOCK | Negative exit blocks user (MAXUSER.STATUS → BLOCKED) |

**Notes:**
- The approve/reject actions are configured on the **connection lines** (WFACTION.ACTION), not on separate nodes
- Typically assigned to a security admin person group

---

## Pattern 6: Email Processing

**Use when:** Processing inbound emails via Maximo Email Listener.

**Object:** INBOUNDCOMM

**Node Graph:**
```
START → COND1 (Has ticket ref?) → [pos: Update Ticket action] → STOP
                                 → [neg]
                                    ↓
        COND2 (Priority keywords?) → [pos] → INTERACT (Create high-pri SR) → STOP
                                    → [neg] → INTERACT (Create standard SR) → STOP
```

**Nodes:**

| # | Type | Title | Description | Config |
|---|------|-------|-------------|--------|
| 1 | START | START | Start | — |
| 2 | CONDITION | HASTICKET | Has existing ticket reference? | `:TICKETID IS NOT NULL` |
| 3 | CONDITION | ISURGENT | Priority keywords in subject? | `:MSGSUBJECT LIKE '%URGENT%' OR :MSGSUBJECT LIKE '%EMERGENCY%'` |
| 4 | INTERACT | CREATEHSR | Create high-priority SR | APP: SR, RELATION: NEWSR |
| 5 | INTERACT | CREATESR | Create standard SR | APP: SR, RELATION: NEWSR |
| 6 | STOP | UPDATED | Ticket updated | — |
| 7 | STOP | CREATED | SR created | — |

**Connections:**
| From→To | Pos | Action | Note |
|---------|-----|--------|------|
| 1→2 | Yes | — | Start |
| 2→6 | Yes | UPDATETICKET | Has ticket → update it (action on connection line) |
| 2→3 | No | — | No ticket → check urgency |
| 3→4 | Yes | — | Urgent → create high-pri SR |
| 3→5 | No | — | Normal → create standard SR |
| 4→7 | Yes | — | Done |
| 5→7 | Yes | — | Done |

**Notes:**
- Record creation uses INTERACT nodes with RELATION field, not a separate "ACTION" node
- The "Update Ticket" logic uses an **action on the connection line** (WFACTION.ACTION)

**Key expressions:**
```sql
-- Check if email references existing ticket
:TICKETID IS NOT NULL

-- Check for priority keywords in subject
:MSGSUBJECT LIKE '%URGENT%' OR :MSGSUBJECT LIKE '%EMERGENCY%'
```

---

## Pattern 7: Composite

**Use when:** The business process combines multiple patterns. Break into parent process + subprocesses.

**Architecture:**
```
Parent Process:
  START → SUBPROCESS (Approval) → SUBPROCESS (Notification) → SUBPROCESS (Creation) → STOP

Each subprocess follows one of the patterns above.
```

**Rules:**
- Each subprocess must be on the same object as the parent
- Subprocesses must be enabled but NOT activated
- Only the parent process is activated
- Import subprocesses BEFORE the parent

---

## Pattern Selection Decision Tree

```
Is it about approving/authorizing a record?
  ├─ YES: Is it one level or multiple?
  │   ├─ One level → Pattern 1a: Single-Level Approval
  │   ├─ Multiple fixed levels → Pattern 1b: Multi-Level Threshold
  │   └─ Dynamic/configurable levels → Pattern 1c: Recursive Approval
  │
  └─ NO: Is it about routing based on status?
      ├─ YES → Pattern 2: Status Routing
      │
      └─ NO: Is it about creating a new record from an existing one?
          ├─ YES → Pattern 3: Record Creation
          │
          └─ NO: Is it about time-based escalation/notification?
              ├─ YES → Pattern 4: Escalation
              │
              └─ NO: Is it about user account management?
                  ├─ YES → Pattern 5: User Management
                  │
                  └─ NO: Is it about processing inbound emails?
                      ├─ YES → Pattern 6: Email Processing
                      │
                      └─ NO: Does it combine multiple patterns?
                          └─ YES → Pattern 7: Composite
```
