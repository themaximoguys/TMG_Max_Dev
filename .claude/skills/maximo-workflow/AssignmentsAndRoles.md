# Maximo Workflow Assignments, Roles, and Notifications

Reference for configuring who receives work, how escalation works, and how notifications are sent.

---

## Roles (MAXROLE)

Roles define WHO receives a task assignment. They are configured in the Roles application and referenced by ROLEID in WFASSIGNMENT.

### Built-In Roles

| Role | Type | Resolves To | Use When |
|------|------|-------------|----------|
| ORIGINATOR | System | Person who created/routed the record | Route back to creator for review |
| SUPERVISOR | Data | Value of SUPERVISOR field on record | Standard hierarchical approval |
| OWNER | Data | Value of OWNER field on record | Route to record owner |

### Role Types

| Type | Description | Example |
|------|-------------|---------|
| **Person** | Specific named person | Always routes to "JSMITH" |
| **Person Group** | Named group of people | Routes to "MAINT_MGRS" group |
| **Data Set** | SQL query resolving to person(s) | Query based on record fields |
| **Login User Relation** | Relative to logged-in user | "Supervisor of current user" |
| **Custom Class** | Java class resolution | Not for no-code workflows |

### Common Person Groups Used in Workflows

| Group | Typical Use |
|-------|-------------|
| MAINT_MGRS | Maintenance management approval |
| PURCH_MGRS | Purchasing management approval |
| EXEC_TEAM | Executive-level approval |
| IT_ADMINS | IT administration tasks |
| SAFETY_TEAM | Safety review and approval |
| FACILITIES | Facilities management |

These are examples — actual groups depend on the customer's configuration.

---

## WFASSIGNMENT Configuration

Each Task node requires at least one assignment. Assignments appear in users' **Inbox/Assignments** portlet.

### Key Fields

| Field | Description | Example |
|-------|-------------|---------|
| ROLEID | Role that determines assignee | SUPERVISOR, MAINT_MGRS |
| APP | Application to open | WOTRACK, PO, PR |
| DESCRIPTION | What the assignee should do | "Approve this work order" |
| EMAILNOTIFICATION | Send email on assignment | 1 (yes) / 0 (no) |
| TEMPLATEID | Communication template for email | WOAPPRNOTIFY |
| TIMELIMIT | Hours before escalation | 24.00 |
| ESCROLE | Role for escalation | MAINT_DIR (director) |
| CONDITION | Conditional assignment expression | `:SITEID = 'BEDFORD'` |
| CALENDARBASED | Use calendar for due dates | 1 (yes) / 0 (no) |

### Assignment Routing Modes

**Single Assignment (one person from group):**
- ROLEID points to a Person Group
- FIRSTCOMPLETE=1 on the WFTASK
- Maximo uses the group's **search logic** to find one available person
- First person to accept completes the task

**Broadcast Assignment (all members):**
- ROLEID points to a Person Group with broadcast enabled
- Each member gets an assignment in their inbox
- FIRSTCOMPLETE determines behavior:
  - `1`: First to act resolves it (race condition — good for "whoever's available")
  - `0`: ALL must act (consensus — good for "everyone must review")

**Conditional Assignment:**
- Add a CONDITION on the WFASSIGNMENT record
- The assignment is only created if the condition evaluates to true
- Allows site-specific or department-specific routing

Example:
```
Assignment 1: ROLEID=MAINT_MGRS_NORTH, CONDITION=:SITEID='NORTH'
Assignment 2: ROLEID=MAINT_MGRS_SOUTH, CONDITION=:SITEID='SOUTH'
```

---

## Escalation

### Task-Level Escalation

Configure on the WFTASK node:
- **TIMELIMIT:** Hours before escalation triggers
- On WFASSIGNMENT, set **ESCROLE** to the escalation target

### What Happens on Escalation

When TIMELIMIT expires:
1. Original assignment remains active
2. A new assignment is created for the ESCROLE
3. Optional: email notification sent via TEMPLATEID on the escalation assignment

### Escalation Chain Pattern

For multi-level escalation:
```
TASK node:
  Assignment 1: ROLEID=SUPERVISOR, TIMELIMIT=4.00, ESCROLE=MANAGER
  Assignment 2: ROLEID=MANAGER, TIMELIMIT=8.00, ESCROLE=DIRECTOR
```

This creates a cascade: after 4 hours the manager gets it, after 8 hours (from task start) the director gets it.

### External Escalation Records

For more complex escalation (repeated notifications, automatic actions), configure **Escalation records** in the Escalation application (System Configuration > Platform Configuration > Escalation). These can:
- Send repeated notifications at intervals
- Change record status automatically
- Reassign to different groups
- Run automation scripts

---

## Communication Templates

### What They Are

Pre-configured email templates with substitution variables. Created in **Administration > Communication Templates**.

### Substitution Variables

| Syntax | Description | Example |
|--------|-------------|---------|
| `@@:FIELDNAME@@` | Field value from the record | `@@:WONUM@@`, `@@:DESCRIPTION@@` |
| `@@:RELATIONSHIP.FIELD@@` | Related record field | `@@:ASSET.DESCRIPTION@@` |
| `@@:&user&@@` | System variable | Current user |

### Template Configuration

| Field | Description |
|-------|-------------|
| Template ID | Unique identifier (e.g., WOAPPRNOTIFY) |
| Subject | Email subject with substitution vars |
| Message | Email body (HTML supported) |
| Send From | Sender email address |
| Recipients | To/CC/BCC — can reference roles |
| Attachments | Optional file attachments |

### Example Templates

**Work Order Approval Request:**
```
Template ID: WOAPPRNOTIFY
Subject: Work Order @@:WONUM@@ Requires Your Approval
Message:
  Work Order @@:WONUM@@ - @@:DESCRIPTION@@
  Priority: @@:WOPRIORITY@@
  Estimated Cost: @@:TOTALCOST@@
  Requested By: @@:REPORTEDBY@@

  Please review and approve/reject in your Maximo Inbox.
```

**PO Approval Notification:**
```
Template ID: POAPPRNOTIFY
Subject: PO @@:PONUM@@ - $@@:TOTALCOST@@ Requires Approval
Message:
  Purchase Order @@:PONUM@@
  Vendor: @@:VENDOR@@
  Total Cost: $@@:TOTALCOST@@
  Purchasing Agent: @@:PURCHASEAGENT@@

  Please review in your Maximo Inbox.
```

**Rejection Notification:**
```
Template ID: WOREJNOTIFY
Subject: Work Order @@:WONUM@@ Has Been Rejected
Message:
  Your Work Order @@:WONUM@@ - @@:DESCRIPTION@@ has been rejected.
  Please review the comments and resubmit if appropriate.
```

---

## Notifications in Workflow

### Where Notifications Can Be Attached

1. **On connection lines (WFACTION):** Triggered when the workflow traverses that connection
2. **On task nodes:** Triggered when an assignment is created (via EMAILNOTIFICATION=1 on WFASSIGNMENT)
3. **On escalation:** Triggered when TIMELIMIT expires

### WFNOTIFICATION Configuration

| Field | Description |
|-------|-------------|
| TEMPLATEID | Communication template to use |
| ROLEID | Role to send to (resolved at runtime) |
| SUBJECT | Override subject (if not using template) |
| MESSAGE | Override body (if not using template) |
| NODEID | Attached to a node |
| ACTIONID | Attached to a connection line |

### Best Practices

1. **Create communication templates BEFORE building the workflow** — the workflow references them by TEMPLATEID
2. **Use templates over inline subject/message** — templates are reusable and maintainable
3. **Notify on key transitions**: approval requested, approved, rejected, escalated
4. **Include the record identifier** (WONUM, PONUM, etc.) in the subject line for easy identification
5. **Don't over-notify** — only send notifications that require action or awareness

---

## Quick Reference: Assignment Configuration for Common Scenarios

| Scenario | ROLEID | FIRSTCOMPLETE | EMAILNOTIFICATION | TIMELIMIT |
|----------|--------|---------------|-------------------|-----------|
| Supervisor approves | SUPERVISOR | 1 | 1 | 24.00 |
| Any maintenance manager | MAINT_MGRS | 1 | 1 | 8.00 |
| All team leads must review | TEAM_LEADS | 0 | 1 | 48.00 |
| Director emergency approval | DIRECTOR | 1 | 1 | 2.00 |
| Route back to originator | ORIGINATOR | 1 | 1 | — |
| Site-specific routing | {site_group} | 1 | 1 | 24.00 |
