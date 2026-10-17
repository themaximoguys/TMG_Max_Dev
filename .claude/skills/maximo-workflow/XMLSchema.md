# Maximo Workflow XML Schema (MIF Format)

Complete reference for generating valid Maximo Integration Framework (MIF) XML for workflow import/export.

---

## XML Wrapper

### Export Format (PublishMXWFPROCESS)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<PublishMXWFPROCESS
    xmlns="http://www.ibm.com/maximo"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    creationDateTime="2026-03-12T21:00:00-05:00"
    transLanguage="EN" baseLanguage="EN"
    messageID="{unique_id}"
    maximoVersion="7 6 20250227-0738 V7613-344"
    event="0">
  <MXWFPROCESSSet>
    <WFPROCESS>
      <!-- Full workflow definition here -->
    </WFPROCESS>
  </MXWFPROCESSSet>
</PublishMXWFPROCESS>
```

### Import Format (SyncMXWFPROCESS)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<SyncMXWFPROCESS
    xmlns="http://www.ibm.com/maximo"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    creationDateTime="{timestamp}"
    transLanguage="EN" baseLanguage="EN"
    messageID="{unique_id}"
    event="0">
  <MXWFPROCESSSet>
    <WFPROCESS>
      <!-- Full workflow definition here -->
    </WFPROCESS>
  </MXWFPROCESSSet>
</SyncMXWFPROCESS>
```

**Use `SyncMXWFPROCESS` for import** — it creates or updates.

---

## Object Hierarchy

```
WFPROCESS (process metadata)
  ├── WFNODE[] (one per node)
  │     ├── WFSTART | WFSTOP | WFCONDITION | WFTASK | WFINPUT |
  │     │   WFSUBPROCESS | WFINTERACTION  (type-specific detail, exactly one)
  │     ├── WFWAITLIST[] (for WAIT nodes, one per event)
  │     └── WFASSIGNMENT[] (for TASK nodes, one per assignment)
  ├── WFACTION[] (connection lines)
  │     └── WFNOTIFICATION[] (notifications on connections)
  └── WFNOTIFICATION[] (notifications on nodes)
```

---

## WFPROCESS Fields

| Field | Required | Description |
|-------|----------|-------------|
| PROCESSNAME | YES | Unique name, max 20 chars |
| PROCESSREV | YES | Revision number (start at 1) |
| OBJECTNAME | YES | Maximo object (WORKORDER, PO, etc.) |
| DESCRIPTION | No | Human-readable description |
| ENABLED | YES | 0 for import (enable manually after) |
| ACTIVE | YES | 0 for import (activate manually after) |
| AUTOINITIATE | YES | 0 or 1 |
| DELETABLE | No | 1 (allow deletion) |
| MIGRATED | No | 0 |
| CHANGEBY | No | User who last changed |
| CHANGEDATE | No | Last change timestamp |
| SENDERSYSID | No | "MX" (default) |
| WFPROCESSID | YES | Unique ID (auto-generated, use large numbers for import) |

---

## WFNODE Fields

| Field | Required | Description |
|-------|----------|-------------|
| NODEID | YES | Integer, unique within process |
| NODETYPE | YES | START, STOP, CONDITION, TASK, INPUT, SUBPROCESS, WAIT, INTERACT |
| TITLE | YES | Max 10 characters |
| DESCRIPTION | No | Human-readable name |
| XCOORDINATE | No | Canvas X position (50-800) |
| YCOORDINATE | No | Canvas Y position (50-600) |
| WFNODEID | YES | Unique row ID |

---

## WFACTION Fields (Connection Lines)

| Field | Required | Description |
|-------|----------|-------------|
| ACTIONID | YES | Integer, unique within process |
| OWNERNODEID | YES | Source node ID |
| MEMBERNODEID | YES | Target node ID |
| ISPOSITIVE | YES | 1=positive (solid), 0=negative (dashed) |
| ACTION | No | Maximo Action name to execute |
| INSTRUCTION | No | Label text (option text for INPUT nodes) |
| CONDITION | No | SQL condition (for conditional options on INPUT exits) |
| SEQUENCE | No | Display order (for INPUT node options) |
| AVAILABLE | No | 1=available at runtime |
| OBJECTNAME | No | Object name (inherited from process) |
| PROCESSNAME | YES | Parent process |
| PROCESSREV | YES | Parent revision |
| WFACTIONID | YES | Unique row ID |

---

## Type-Specific Detail Elements

### WFSTART / WFSTOP
```xml
<WFSTART>
  <NODEID>{id}</NODEID>
  <PROCESSNAME>{name}</PROCESSNAME>
  <PROCESSREV>{rev}</PROCESSREV>
</WFSTART>
```

### WFCONDITION
```xml
<WFCONDITION>
  <CONDITION>{sql_expression}</CONDITION>
  <CUSTOMCLASS xsi:nil="true"></CUSTOMCLASS>
  <NODEID>{id}</NODEID>
  <PROCESSNAME>{name}</PROCESSNAME>
  <PROCESSREV>{rev}</PROCESSREV>
  <WFCONDITIONID>{unique_id}</WFCONDITIONID>
</WFCONDITION>
```

### WFTASK
```xml
<WFTASK>
  <APP>{application}</APP>
  <FIRSTCOMPLETE>{0_or_1}</FIRSTCOMPLETE>
  <NODEID>{id}</NODEID>
  <PROCESSNAME>{name}</PROCESSNAME>
  <PROCESSREV>{rev}</PROCESSREV>
  <READONLY>{0_or_1}</READONLY>
  <TIMELIMIT>{hours}</TIMELIMIT>
  <WFTASKID>{unique_id}</WFTASKID>
</WFTASK>
```

### WFINPUT
```xml
<WFINPUT>
  <DISPLAYONE>{0_or_1}</DISPLAYONE>
  <NODEID>{id}</NODEID>
  <PROCESSNAME>{name}</PROCESSNAME>
  <PROCESSREV>{rev}</PROCESSREV>
</WFINPUT>
```

### WFSUBPROCESS
```xml
<WFSUBPROCESS>
  <NODEID>{id}</NODEID>
  <PROCESSNAME>{name}</PROCESSNAME>
  <PROCESSREV>{rev}</PROCESSREV>
  <SUBPROCESSNAME>{subprocess_name}</SUBPROCESSNAME>
</WFSUBPROCESS>
```

### WFINTERACTION
```xml
<WFINTERACTION>
  <ACTION>{action}</ACTION>
  <APP>{application}</APP>
  <DIRECTIONS>{dialog_title}</DIRECTIONS>
  <DIRECTIONS_LONGDESCRIPTION>{dialog_body}</DIRECTIONS_LONGDESCRIPTION>
  <NODEID>{id}</NODEID>
  <PAGE>{tab_id}</PAGE>
  <PROCESSNAME>{name}</PROCESSNAME>
  <PROCESSREV>{rev}</PROCESSREV>
  <RELATION>{NEWWORKORDER|NEWSR|etc}</RELATION>
  <WFINTERACTIONID>{unique_id}</WFINTERACTIONID>
</WFINTERACTION>
```

### WFWAITLIST (child of WAIT node)
```xml
<WFWAITLIST>
  <EVENT>maximo.{object}.{eventtype}[.{status}]</EVENT>
  <NODEID>{id}</NODEID>
  <PROCESSNAME>{name}</PROCESSNAME>
  <PROCESSREV>{rev}</PROCESSREV>
  <WFWAITLISTID>{unique_id}</WFWAITLISTID>
</WFWAITLIST>
```

### WFASSIGNMENT (child of TASK node)
```xml
<WFASSIGNMENT>
  <ASSIGNID>{id}</ASSIGNID>
  <APP>{application}</APP>
  <DESCRIPTION>{assignment_description}</DESCRIPTION>
  <EMAILNOTIFICATION>{0_or_1}</EMAILNOTIFICATION>
  <NODEID>{task_node_id}</NODEID>
  <PROCESSNAME>{name}</PROCESSNAME>
  <PROCESSREV>{rev}</PROCESSREV>
  <ROLEID>{role_name}</ROLEID>
  <TIMELIMIT>{escalation_hours}</TIMELIMIT>
  <TEMPLATEID>{communication_template}</TEMPLATEID>
  <WFASSIGNMENTID>{unique_id}</WFASSIGNMENTID>
</WFASSIGNMENT>
```

### WFNOTIFICATION
```xml
<WFNOTIFICATION>
  <ACTIONID>{action_id_or_nil}</ACTIONID>
  <NODEID>{node_id_or_nil}</NODEID>
  <NOTIFICATIONID>{id}</NOTIFICATIONID>
  <OBJECTNAME>{object}</OBJECTNAME>
  <PROCESSNAME>{name}</PROCESSNAME>
  <PROCESSREV>{rev}</PROCESSREV>
  <ROLEID>{recipient_role}</ROLEID>
  <SUBJECT>{email_subject}</SUBJECT>
  <TEMPLATEID>{template_id}</TEMPLATEID>
  <WFNOTIFICATIONID>{unique_id}</WFNOTIFICATIONID>
</WFNOTIFICATION>
```

---

## Complete Example: Single-Level WO Approval

```xml
<?xml version="1.0" encoding="UTF-8"?>
<SyncMXWFPROCESS xmlns="http://www.ibm.com/maximo"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    creationDateTime="2026-03-13T00:00:00-05:00"
    transLanguage="EN" baseLanguage="EN"
    messageID="WF-IMPORT-001" event="0">
  <MXWFPROCESSSet>
    <WFPROCESS>
      <ACTIVE>0</ACTIVE>
      <AUTOINITIATE>0</AUTOINITIATE>
      <DELETABLE>1</DELETABLE>
      <DESCRIPTION>Work Order Cost Approval</DESCRIPTION>
      <ENABLED>0</ENABLED>
      <MIGRATED>0</MIGRATED>
      <OBJECTNAME>WORKORDER</OBJECTNAME>
      <PROCESSNAME>WOCOSTAPPR</PROCESSNAME>
      <PROCESSREV>1</PROCESSREV>
      <SENDERSYSID>MX</SENDERSYSID>
      <WFPROCESSID>900001</WFPROCESSID>

      <!-- NODE 1: START -->
      <WFNODE>
        <NODEID>1</NODEID>
        <NODETYPE>START</NODETYPE>
        <TITLE>START</TITLE>
        <DESCRIPTION>Start</DESCRIPTION>
        <XCOORDINATE>50</XCOORDINATE>
        <YCOORDINATE>200</YCOORDINATE>
        <WFNODEID>900101</WFNODEID>
        <WFSTART>
          <NODEID>1</NODEID>
          <PROCESSNAME>WOCOSTAPPR</PROCESSNAME>
          <PROCESSREV>1</PROCESSREV>
        </WFSTART>
      </WFNODE>

      <!-- NODE 2: CONDITION - Cost over $5000? -->
      <WFNODE>
        <NODEID>2</NODEID>
        <NODETYPE>CONDITION</NODETYPE>
        <TITLE>HIGHCOST</TITLE>
        <DESCRIPTION>Total cost exceeds $5000?</DESCRIPTION>
        <XCOORDINATE>200</XCOORDINATE>
        <YCOORDINATE>200</YCOORDINATE>
        <WFNODEID>900102</WFNODEID>
        <WFCONDITION>
          <CONDITION>:TOTALCOST &gt; 5000</CONDITION>
          <CUSTOMCLASS xsi:nil="true"></CUSTOMCLASS>
          <NODEID>2</NODEID>
          <PROCESSNAME>WOCOSTAPPR</PROCESSNAME>
          <PROCESSREV>1</PROCESSREV>
          <WFCONDITIONID>900201</WFCONDITIONID>
        </WFCONDITION>
      </WFNODE>

      <!-- NODE 3: TASK - Supervisor Approval -->
      <WFNODE>
        <NODEID>3</NODEID>
        <NODETYPE>TASK</NODETYPE>
        <TITLE>SUPVAPPR</TITLE>
        <DESCRIPTION>Supervisor Approval Required</DESCRIPTION>
        <XCOORDINATE>400</XCOORDINATE>
        <YCOORDINATE>100</YCOORDINATE>
        <WFNODEID>900103</WFNODEID>
        <WFTASK>
          <APP>WOTRACK</APP>
          <FIRSTCOMPLETE>1</FIRSTCOMPLETE>
          <NODEID>3</NODEID>
          <PROCESSNAME>WOCOSTAPPR</PROCESSNAME>
          <PROCESSREV>1</PROCESSREV>
          <READONLY>0</READONLY>
          <TIMELIMIT>24.00</TIMELIMIT>
          <WFTASKID>900301</WFTASKID>
        </WFTASK>
        <WFASSIGNMENT>
          <ASSIGNID>1</ASSIGNID>
          <APP>WOTRACK</APP>
          <DESCRIPTION>Approve or reject this work order</DESCRIPTION>
          <EMAILNOTIFICATION>1</EMAILNOTIFICATION>
          <NODEID>3</NODEID>
          <PROCESSNAME>WOCOSTAPPR</PROCESSNAME>
          <PROCESSREV>1</PROCESSREV>
          <ROLEID>SUPERVISOR</ROLEID>
          <TEMPLATEID>WOAPPRNOTIFY</TEMPLATEID>
          <TIMELIMIT>24.00</TIMELIMIT>
          <WFASSIGNMENTID>900401</WFASSIGNMENTID>
        </WFASSIGNMENT>
      </WFNODE>

      <!-- NODE 4: STOP - Approved -->
      <WFNODE>
        <NODEID>4</NODEID>
        <NODETYPE>STOP</NODETYPE>
        <TITLE>APPROVED</TITLE>
        <DESCRIPTION>Approved</DESCRIPTION>
        <XCOORDINATE>600</XCOORDINATE>
        <YCOORDINATE>100</YCOORDINATE>
        <WFNODEID>900104</WFNODEID>
        <WFSTOP>
          <NODEID>4</NODEID>
          <PROCESSNAME>WOCOSTAPPR</PROCESSNAME>
          <PROCESSREV>1</PROCESSREV>
        </WFSTOP>
      </WFNODE>

      <!-- NODE 5: STOP - Rejected -->
      <WFNODE>
        <NODEID>5</NODEID>
        <NODETYPE>STOP</NODETYPE>
        <TITLE>REJECTED</TITLE>
        <DESCRIPTION>Rejected</DESCRIPTION>
        <XCOORDINATE>600</XCOORDINATE>
        <YCOORDINATE>300</YCOORDINATE>
        <WFNODEID>900105</WFNODEID>
        <WFSTOP>
          <NODEID>5</NODEID>
          <PROCESSNAME>WOCOSTAPPR</PROCESSNAME>
          <PROCESSREV>1</PROCESSREV>
        </WFSTOP>
      </WFNODE>

      <!-- NODE 6: STOP - Auto-approved (under threshold) -->
      <WFNODE>
        <NODEID>6</NODEID>
        <NODETYPE>STOP</NODETYPE>
        <TITLE>AUTOAPPR</TITLE>
        <DESCRIPTION>Auto-approved (under $5000)</DESCRIPTION>
        <XCOORDINATE>400</XCOORDINATE>
        <YCOORDINATE>350</YCOORDINATE>
        <WFNODEID>900106</WFNODEID>
        <WFSTOP>
          <NODEID>6</NODEID>
          <PROCESSNAME>WOCOSTAPPR</PROCESSNAME>
          <PROCESSREV>1</PROCESSREV>
        </WFSTOP>
      </WFNODE>

      <!-- CONNECTIONS -->

      <!-- START -> CONDITION -->
      <WFACTION>
        <ACTIONID>1</ACTIONID>
        <AVAILABLE>1</AVAILABLE>
        <ISPOSITIVE>1</ISPOSITIVE>
        <MEMBERNODEID>2</MEMBERNODEID>
        <OBJECTNAME>WORKORDER</OBJECTNAME>
        <OWNERNODEID>1</OWNERNODEID>
        <PROCESSNAME>WOCOSTAPPR</PROCESSNAME>
        <PROCESSREV>1</PROCESSREV>
        <WFACTIONID>900501</WFACTIONID>
      </WFACTION>

      <!-- CONDITION -> TASK (positive: cost > $5000) -->
      <WFACTION>
        <ACTIONID>2</ACTIONID>
        <ACTION>WAPPR</ACTION>
        <AVAILABLE>1</AVAILABLE>
        <INSTRUCTION>High cost - requires supervisor approval</INSTRUCTION>
        <ISPOSITIVE>1</ISPOSITIVE>
        <MEMBERNODEID>3</MEMBERNODEID>
        <OBJECTNAME>WORKORDER</OBJECTNAME>
        <OWNERNODEID>2</OWNERNODEID>
        <PROCESSNAME>WOCOSTAPPR</PROCESSNAME>
        <PROCESSREV>1</PROCESSREV>
        <WFACTIONID>900502</WFACTIONID>
        <!-- Notification on this connection -->
        <WFNOTIFICATION>
          <ACTIONID>2</ACTIONID>
          <NOTIFICATIONID>1</NOTIFICATIONID>
          <OBJECTNAME>WORKORDER</OBJECTNAME>
          <PROCESSNAME>WOCOSTAPPR</PROCESSNAME>
          <PROCESSREV>1</PROCESSREV>
          <ROLEID>SUPERVISOR</ROLEID>
          <TEMPLATEID>WOAPPRNOTIFY</TEMPLATEID>
          <WFNOTIFICATIONID>900601</WFNOTIFICATIONID>
        </WFNOTIFICATION>
      </WFACTION>

      <!-- CONDITION -> STOP (negative: cost <= $5000, auto-approve) -->
      <WFACTION>
        <ACTIONID>3</ACTIONID>
        <ACTION>APPR</ACTION>
        <AVAILABLE>1</AVAILABLE>
        <INSTRUCTION>Under threshold - auto-approved</INSTRUCTION>
        <ISPOSITIVE>0</ISPOSITIVE>
        <MEMBERNODEID>6</MEMBERNODEID>
        <OBJECTNAME>WORKORDER</OBJECTNAME>
        <OWNERNODEID>2</OWNERNODEID>
        <PROCESSNAME>WOCOSTAPPR</PROCESSNAME>
        <PROCESSREV>1</PROCESSREV>
        <WFACTIONID>900503</WFACTIONID>
      </WFACTION>

      <!-- TASK -> STOP Approved (positive) -->
      <WFACTION>
        <ACTIONID>4</ACTIONID>
        <ACTION>APPR</ACTION>
        <AVAILABLE>1</AVAILABLE>
        <INSTRUCTION>Approve work order</INSTRUCTION>
        <ISPOSITIVE>1</ISPOSITIVE>
        <MEMBERNODEID>4</MEMBERNODEID>
        <OBJECTNAME>WORKORDER</OBJECTNAME>
        <OWNERNODEID>3</OWNERNODEID>
        <PROCESSNAME>WOCOSTAPPR</PROCESSNAME>
        <PROCESSREV>1</PROCESSREV>
        <WFACTIONID>900504</WFACTIONID>
      </WFACTION>

      <!-- TASK -> STOP Rejected (negative) -->
      <WFACTION>
        <ACTIONID>5</ACTIONID>
        <ACTION>CAN</ACTION>
        <AVAILABLE>1</AVAILABLE>
        <INSTRUCTION>Reject work order</INSTRUCTION>
        <ISPOSITIVE>0</ISPOSITIVE>
        <MEMBERNODEID>5</MEMBERNODEID>
        <OBJECTNAME>WORKORDER</OBJECTNAME>
        <OWNERNODEID>3</OWNERNODEID>
        <PROCESSNAME>WOCOSTAPPR</PROCESSNAME>
        <PROCESSREV>1</PROCESSREV>
        <WFACTIONID>900505</WFACTIONID>
      </WFACTION>

    </WFPROCESS>
  </MXWFPROCESSSet>
</SyncMXWFPROCESS>
```

---

## Import Process

### Prerequisites

1. **Object Structure:** MXWFPROCESS must include all child objects:
   ```
   WFPROCESS (level 0)
     WFNODE (level 1)
       WFSTART, WFSTOP, WFCONDITION, WFTASK, WFINPUT,
       WFSUBPROCESS, WFINTERACTION, WFWAITLIST (level 2)
       WFASSIGNMENT (level 2)
     WFACTION (level 1)
       WFNOTIFICATION (level 2)
     WFNOTIFICATION (level 1)
   ```

2. **Enterprise Service:** Must be configured for MXWFPROCESS inbound processing

### Import Methods

| Method | How |
|--------|-----|
| Enterprise Services UI | Integration > Enterprise Services > Data Import |
| External Systems | External Systems app > Data Import action |
| REST API | POST to `/maximo/oslc/os/mxwfprocess` |
| Flat file drop | Place XML in configured file directory |

### Import Rules

- Set `ACTIVE=0` and `ENABLED=0` — let admin validate/enable/activate after review
- PROCESSNAME + PROCESSREV must be unique in target system
- **Import subprocesses BEFORE parent processes**
- Unique IDs (WFPROCESSID, WFNODEID, etc.) must not collide — use high numbers (900000+)

### Post-Import Steps

1. Open Workflow Designer
2. Find the imported process
3. Review on canvas
4. Validate (Common Actions > Validate Process)
5. Enable (Common Actions > Enable Process)
6. Activate (Common Actions > Activate Process)
7. Optional: Set to Auto-Initiate

---

## XML Escaping Reminder

| Character | Entity |
|-----------|--------|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `&` | `&amp;` |
| `'` | `&apos;` |
| `"` | `&quot;` |

Always escape condition expressions: `:TOTALCOST > 5000` becomes `:TOTALCOST &gt; 5000` in XML.
