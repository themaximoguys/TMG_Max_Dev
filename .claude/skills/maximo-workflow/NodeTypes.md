# Maximo Workflow Node Types Reference

Complete reference for all 8 node types in the Maximo Workflow Designer.

---

## Node Type Summary

| Type | Icon Shape | Detail Table | Max Positive Out | Max Negative Out | Key Config |
|------|-----------|--------------|-----------------|-----------------|------------|
| START | Green circle | WFSTART | 1 | 0 | None |
| STOP | Red circle | WFSTOP | 0 | 0 | None |
| CONDITION | Yellow diamond | WFCONDITION | 1 | 1 | SQL expression |
| TASK | Blue rectangle | WFTASK | 1 | 1 | Assignments, app, time limit |
| INPUT | White rectangle | WFINPUT | 1+ | 0 | Options from exit connections |
| SUBPROCESS | Nested square | WFSUBPROCESS | 1 | 1 | Subprocess name |
| WAIT | Hourglass | WFWAITLIST | 1 | 0 | Event name(s) |
| INTERACT | Double rectangle | WFINTERACTION | 1 | 0 | App, page, relation |

---

## START Node

**Purpose:** Entry point of the workflow. Every process must have exactly one.

**Properties:** None configurable. Automatically placed on canvas.

**Connection Rules:**
- Exactly 1 positive exit (to the first real node)
- 0 negative exits

**TITLE Convention:** `START`

**Detail Table: WFSTART**
| Field | Type | Description |
|-------|------|-------------|
| PROCESSNAME | VARCHAR(20) | Parent process |
| PROCESSREV | INT | Parent revision |
| NODEID | INT | Node ID |

---

## STOP Node

**Purpose:** Exit point. A process can have multiple stop nodes for different exit paths (approved path stop, rejected path stop, etc.).

**Properties:** None configurable.

**Connection Rules:**
- 0 positive exits
- 0 negative exits
- Can receive connections from any node type

**TITLE Convention:** `STOP`, `STOP2`, `STOPAPPR`, `STOPREJ`

**Detail Table: WFSTOP**
| Field | Type | Description |
|-------|------|-------------|
| PROCESSNAME | VARCHAR(20) | Parent process |
| PROCESSREV | INT | Parent revision |
| NODEID | INT | Node ID |

---

## CONDITION Node

**Purpose:** Evaluates a SQL WHERE clause expression against the controlled record. Routes to positive exit if true, negative exit if false.

**Properties:**
- **Condition:** SQL expression (see ExpressionSyntax.md)
- **Custom Class:** Java class name (only for code-based workflows, NOT no-code)

**Connection Rules:**
- Exactly 1 positive exit (condition evaluates to TRUE)
- Exactly 1 negative exit (condition evaluates to FALSE)

**TITLE Convention:** Short descriptor, max 10 chars. Examples: `COST`, `PRIORITY`, `HIGHCOST`, `ISEM`, `CHKSTATUS`

**Detail Table: WFCONDITION**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| PROCESSNAME | VARCHAR(20) | YES | Parent process |
| PROCESSREV | INT | YES | Parent revision |
| NODEID | INT | YES | Node ID |
| CONDITION | CLOB | YES* | SQL WHERE clause |
| CUSTOMCLASS | VARCHAR(200) | NO | Java class (not for no-code) |
| WFCONDITIONID | BIGINT | YES | Unique row ID |

*Either CONDITION or CUSTOMCLASS must be filled. For no-code, always use CONDITION.

---

## TASK Node

**Purpose:** Creates an assignment in a user's Workflow Inbox. The user must take action (approve/reject/complete) to move the workflow forward.

**Properties:**
- **App:** Application to open when user accesses assignment (e.g., WOTRACK, PO, PR)
- **Time Limit:** Hours before escalation (e.g., 24.00)
- **First Complete:**
  - `1` = "When any assignment is accepted" (first person to act resolves it)
  - `0` = "When all assignments are accepted" (everyone must act)
- **Read Only:** Whether non-assigned users see the record as read-only

**Connection Rules:**
- Exactly 1 positive exit (task approved/accepted)
- Exactly 1 negative exit (task rejected/denied)

**Requires:** At least 1 WFASSIGNMENT child record defining who receives the task.

**TITLE Convention:** `MGRAPPR`, `SUPVAPPR`, `VPAPPR`, `REVIEW`, `ACCEPT`

**Detail Table: WFTASK**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| PROCESSNAME | VARCHAR(20) | YES | Parent process |
| PROCESSREV | INT | YES | Parent revision |
| NODEID | INT | YES | Node ID |
| APP | VARCHAR(20) | NO | Application name |
| TIMELIMIT | FLOAT | NO | Hours before escalation |
| FIRSTCOMPLETE | YORN (0/1) | NO | Any vs all must complete |
| READONLY | YORN (0/1) | NO | Read-only for others |
| WFTASKID | BIGINT | YES | Unique row ID |

---

## INPUT (Manual Input) Node

**Purpose:** Presents the user with multiple choices. Each positive exit connection becomes a selectable option. The user picks one, and the workflow follows that path.

**Properties:**
- **Display One:** What to do if user has security for only one option (auto-select it)

**Connection Rules:**
- 1 or more positive exits (each one = a user choice)
- 0 negative exits (not allowed)

**The options:** Each WFACTION exiting this node has an INSTRUCTION field that becomes the option label shown to the user. The SEQUENCE field controls display order.

**Optional conditions on exits:** Each exit connection can have a CONDITION expression. If the condition evaluates to false, that option is hidden from the user. This allows dynamic option visibility based on record data.

**TITLE Convention:** `DECISION`, `CHOOSE`, `ACTION`, `ROUTE`

**Detail Table: WFINPUT**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| PROCESSNAME | VARCHAR(20) | YES | Parent process |
| PROCESSREV | INT | YES | Parent revision |
| NODEID | INT | YES | Node ID |
| DISPLAYONE | YORN (0/1) | NO | Auto-select if only one option |

---

## SUBPROCESS Node

**Purpose:** Invokes another workflow process as a subprocess. The subprocess runs to completion, then control returns to this node's exit path.

**Properties:**
- **Subprocess Name:** The PROCESSNAME of the subprocess to invoke

**Connection Rules:**
- Exactly 1 positive exit (subprocess completed successfully)
- Exactly 1 negative exit (subprocess completed with negative result)

**Requirements:**
- The subprocess must exist and be **enabled** (but NOT activated — only the parent is activated)
- The subprocess must be on the **same object** (OBJECTNAME must match)
- Subprocesses can be nested (a subprocess can call another subprocess)

**TITLE Convention:** `SUB_xxx` or abbreviated subprocess name

**Detail Table: WFSUBPROCESS**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| PROCESSNAME | VARCHAR(20) | YES | Parent process |
| PROCESSREV | INT | YES | Parent revision |
| NODEID | INT | YES | Node ID |
| SUBPROCESSNAME | VARCHAR(20) | YES | Name of subprocess to invoke |

---

## WAIT Node

**Purpose:** Pauses the workflow until a specific database event occurs. The workflow resumes automatically when the event is detected.

**Properties:**
- **Event(s):** One or more event names to wait for

**Connection Rules:**
- Exactly 1 positive exit (event occurred)
- 0 negative exits

**Event Name Format:** `maximo.<objectname>.<eventtype>[.<status>]`
- `maximo.workorder.statuschange.appr` — Wait for WO to be approved
- `maximo.po.add` — Wait for a new PO to be created
- `maximo.sr.statuschange.resolved` — Wait for SR to be resolved
- `maximo.asset.update` — Wait for any asset update
- `maximo.change.init` — Wait for change record initialization

**Event Types:** `init`, `add`, `update`, `delete`, `statuschange`

**TITLE Convention:** `WAIT`, `WAITAPPR`, `WAITSTAT`

**Detail Table: WFWAITLIST** (child of WFNODE)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| PROCESSNAME | VARCHAR(20) | YES | Parent process |
| PROCESSREV | INT | YES | Parent revision |
| NODEID | INT | YES | Node ID |
| EVENT | VARCHAR(100) | YES | Event name |
| WFWAITLISTID | BIGINT | YES | Unique row ID |

---

## INTERACT (Interaction) Node

**Purpose:** Displays a message to the user, redirects them to another application/tab, or creates a new related record.

**Properties:**
- **App:** Application to display (e.g., WOTRACK, SR, PO)
- **Page:** Tab ID within the application (from presentation XML)
- **Action:** Application action to trigger
- **Relation:** Relationship for new record creation (see values below)
- **Directions:** Title of the directions dialog shown to user
- **Directions Long Description:** Body text of the directions dialog

**Connection Rules:**
- Exactly 1 positive exit
- 0 negative exits

**Relation Values for New Records:**

| Relation | Creates |
|----------|---------|
| NEWWORKORDER | New Work Order |
| NEWSR | New Service Request |
| NEWINCIDENT | New Incident |
| NEWPROBLEM | New Problem |
| NEWCHANGE | New Change |
| NEWRELEASE | New Release |
| NEWACTIVITY | New Activity |
| NEWTICKET | New Ticket |

**TITLE Convention:** `CREATEWO`, `CREATESR`, `NAVTAB`, `DIRECT`

**Detail Table: WFINTERACTION**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| PROCESSNAME | VARCHAR(20) | YES | Parent process |
| PROCESSREV | INT | YES | Parent revision |
| NODEID | INT | YES | Node ID |
| APP | VARCHAR(20) | NO | Application name |
| PAGE | VARCHAR(50) | NO | Tab/page ID |
| ACTION | VARCHAR(60) | NO | Application action |
| RELATION | VARCHAR(50) | NO | New record relationship |
| DIRECTIONS | VARCHAR(100) | NO | Dialog title |
| DIRECTIONS_LONGDESCRIPTION | CLOB | NO | Dialog body |
| WFINTERACTIONID | BIGINT | YES | Unique row ID |

---

## Canvas Layout Guidelines

| Element | Typical X | Typical Y | Notes |
|---------|----------|----------|-------|
| START node | 50 | 200 | Left side of canvas |
| First decision | 200 | 200 | 150px right of START |
| Approval tasks | 400 | 100-300 | Staggered vertically for branches |
| STOP nodes | 600-800 | Various | Right side, one per exit path |
| Node spacing | 150-200px horizontal, 100-150px vertical | | Readable at 100% zoom |

**Flow direction:** Left-to-right (primary) or top-to-bottom (alternative). Stay consistent within one process.
