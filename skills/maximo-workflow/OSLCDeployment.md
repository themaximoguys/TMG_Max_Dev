# Maximo Workflow OSLC API Deployment

> Repository use: payload reference only. Follow `Workflows/Deploy.md` and use
> maxdev with dry run and approval. Do not execute the direct HTTP examples below.

Reference for deploying workflows programmatically via Maximo OSLC REST API using JSON format. Tested and verified on Maximo 7.6.x and MAS 9.x.

---

## API Endpoints

| Endpoint | Object | Purpose |
|----------|--------|---------|
| `/maximo/oslc/os/mxapiwfprocess` | WFPROCESS | Create/Read/Update/Delete workflow processes |
| `/maximo/oslc/os/mxapirole` | MAXROLE | Create/Read/Update/Delete workflow roles |
| `/maximo/oslc/os/mxapipersongroup` | PERSONGROUP | Read person groups (ADD may be restricted) |
| `/maximo/oslc/os/mxapiwfassignment` | WFASSIGNMENT | Read workflow assignments |
| `/maximo/oslc/os/mxapiaction` | ACTION | Read CHANGESTATUS actions |

**Note:** `mxapirole` may need to be created as a custom Object Structure if not already exposed. Map it to the MAXROLE table with all columns.

---

## Authentication

### maxauth Header (Preferred)
```
maxauth: <base64(username:password)>
```
```bash
MAXAUTH=$(echo -n "username:password" | base64)
curl -H "maxauth: $MAXAUTH" ...
```

### apikey Header
```
apikey: <api_key_value>
```

### Important Parameters
- `?lean=1` — **REQUIRED** for JSON without namespace prefixes. Without this, field names won't match.
- `Properties: *` — Return all fields in response (optional, for verification)

---

## Dependency Chain (Order Matters)

Workflows depend on prerequisites that must exist BEFORE upload:

```
1. POSTATUS Synonym Domains  ← Status values used in CHANGESTATUS actions
       ↓
2. ACTION (CHANGESTATUS)     ← Actions referenced on workflow connections
       ↓
3. PERSONGROUP               ← Person groups that roles reference
       ↓
4. MAXROLE                   ← Roles that WFASSIGNMENT.ROLEID references
       ↓
5. WFPROCESS (subprocesses)  ← Must exist before parent references them
       ↓
6. WFPROCESS (parent)        ← References subprocesses by name
```

**Upload order for multi-process workflows:**
1. Innermost subprocesses first (e.g., CORP1 subprocess)
2. Mid-level subprocesses (e.g., Budgeted chain, Unbudgeted chain)
3. Parent process last

---

## JSON Format — Workflow Process

The OSLC JSON format nests actions INSIDE nodes (unlike MIF XML which can have them separate).

### Top-Level Process
```json
{
  "processname": "POAPPR_CRP",
  "processrev": 1,
  "objectname": "PO",
  "description": "CORP1 Subprocess",
  "active": false,
  "enabled": false,
  "autoinitiate": false,
  "deletable": 1,
  "langcode": "EN",
  "hasld": false,
  "migrated": false,
  "wfnode": [ ... ]
}
```

**Do NOT include server-generated IDs** (wfprocessid, wfnodeid, wfactionid, wfconditionid, wftaskid, wfassignmentid, wfstartid, wfstopid, wfinputid) — Maximo generates these on POST.

### Node Types

#### START Node
```json
{
  "nodeid": 1,
  "nodetype": "START",
  "title": "START",
  "description": "Start",
  "xcoordinate": -1,
  "ycoordinate": -4,
  "langcode": "EN",
  "hasld": false,
  "wfstart": [{}],
  "wfaction": [
    {
      "actionid": 1,
      "ownernodeid": 1,
      "membernodeid": 2,
      "instruction": "Next Step",
      "ispositive": true
    }
  ]
}
```

#### STOP Node
```json
{
  "nodeid": 8,
  "nodetype": "STOP",
  "title": "APPROVED",
  "description": "Approved",
  "xcoordinate": 9,
  "ycoordinate": -4,
  "langcode": "EN",
  "hasld": false,
  "wfstop": [{}]
}
```

#### TASK Node (with Assignment)
```json
{
  "nodeid": 3,
  "nodetype": "TASK",
  "title": "PM",
  "description": "Plant Manager Approval",
  "xcoordinate": 3,
  "ycoordinate": -4,
  "langcode": "EN",
  "hasld": false,
  "wftask": [
    {
      "app": "PO",
      "firstcomplete": true,
      "readonly": false,
      "displayone": false,
      "timelimit": 0.0,
      "calendarbased": false
    }
  ],
  "wfassignment": [
    {
      "app": "PO",
      "assignid": 1,
      "roleid": "PLANTMAN",
      "description": "Approve PO :ponum",
      "templateid": "WFASSIGN",
      "emailnotification": true,
      "assignstatus": "DEFAULT",
      "ownertable": "PO",
      "separategroups": true,
      "keeporigassgn": false,
      "timelimit": 0.0,
      "calendarbased": false,
      "langcode": "EN",
      "hasld": false
    }
  ],
  "wfaction": [
    {
      "actionid": 2,
      "ownernodeid": 3,
      "membernodeid": 4,
      "instruction": "Approved",
      "ispositive": true
    },
    {
      "actionid": 3,
      "ownernodeid": 3,
      "membernodeid": 9,
      "instruction": "Rejected",
      "ispositive": false
    }
  ]
}
```

#### CONDITION Node
```json
{
  "nodeid": 4,
  "nodetype": "CONDITION",
  "title": "LE25K",
  "description": "<=25,000",
  "xcoordinate": 5,
  "ycoordinate": -4,
  "langcode": "EN",
  "hasld": false,
  "wfcondition": [
    {
      "condition": ":totalbasecost <= 25000"
    }
  ],
  "wfaction": [
    {
      "actionid": 4,
      "ownernodeid": 4,
      "membernodeid": 5,
      "instruction": "Within Limit",
      "ispositive": true
    },
    {
      "actionid": 5,
      "ownernodeid": 4,
      "membernodeid": 6,
      "instruction": "Exceeds Limit",
      "ispositive": false
    }
  ]
}
```

#### INPUT Node (Manual Routing)
```json
{
  "nodeid": 2,
  "nodetype": "INPUT",
  "title": "SELAPPR",
  "description": "Select Approver",
  "xcoordinate": 1,
  "ycoordinate": -4,
  "langcode": "EN",
  "hasld": false,
  "wfinput": [
    {
      "displayone": false
    }
  ],
  "wfaction": [
    {
      "actionid": 2,
      "sequence": 1,
      "ownernodeid": 2,
      "membernodeid": 3,
      "instruction": "Route to Manager A",
      "action": "WSTATUSA",
      "ispositive": true
    },
    {
      "actionid": 3,
      "sequence": 2,
      "ownernodeid": 2,
      "membernodeid": 4,
      "instruction": "Route to Manager B",
      "action": "WSTATUSB",
      "ispositive": true
    }
  ]
}
```
**Note:** INPUT actions use `sequence` for ordering and are ALL `ispositive: true`. Each choice should route to a SEPARATE TASK node with its own role assignment.

#### SUBPROCESS Node
```json
{
  "nodeid": 5,
  "nodetype": "SUBPROCESS",
  "title": "CRP1",
  "description": "CORP1 Subprocess",
  "xcoordinate": 5,
  "ycoordinate": -1,
  "langcode": "EN",
  "hasld": false,
  "wfaction": [
    {
      "actionid": 6,
      "ownernodeid": 5,
      "membernodeid": 8,
      "instruction": "Approved",
      "ispositive": true
    },
    {
      "actionid": 7,
      "ownernodeid": 5,
      "membernodeid": 9,
      "instruction": "Rejected",
      "ispositive": false
    }
  ]
}
```

### Connection Actions (WFACTION)

Actions on connections fire CHANGESTATUS or other operations when the workflow traverses that path.

```json
{
  "actionid": 1,
  "ownernodeid": 1,
  "membernodeid": 2,
  "instruction": "Waiting on Plant Manager",
  "action": "WPLANTM",
  "ispositive": true,
  "sequence": 1
}
```

| Field | Description |
|-------|-------------|
| `actionid` | Sequential integer (unique within the process) |
| `ownernodeid` | Source node's `nodeid` |
| `membernodeid` | Target node's `nodeid` |
| `instruction` | Label shown on the connection arrow |
| `action` | Maximo ACTION name (e.g., "WPLANTM", "PO APPR") — omit if no status change |
| `ispositive` | `true` = positive exit, `false` = negative exit |
| `sequence` | Required for INPUT nodes (ordering of choices) |

---

## Canvas Coordinates

**Maximo uses grid units, NOT pixels.** The coordinate system uses small integers (typically -10 to +15).

### Coordinate Reference (from production POWF1 workflow)
```
X range: -2 to 14
Y range: -9 to -1
Grid spacing: ~1-2 units between adjacent nodes
```

### Layout Guidelines
- Horizontal flow: increment X by 2 for sequential nodes
- Vertical branching: offset Y by 1-2 for parallel paths
- START node: leftmost (low X)
- STOP nodes: rightmost (high X)
- Rejected/negative paths: lower Y values (more negative)
- Approved/positive paths: higher Y values (less negative)

### Conversion from pixel coordinates
```
x_grid = round(x_pixels / 100) - 1
y_grid = -(round(y_pixels / 100) + 1)
```

---

## JSON Format — MAXROLE

### Query Existing Roles
```
GET /maximo/oslc/os/mxapirole?lean=1&oslc.where=objectname="PO"&oslc.select=maxrole,description,value,type,objectname
```

### Create a Role
```
POST /maximo/oslc/os/mxapirole?lean=1
Content-Type: application/json
```
```json
{
  "maxrole": "PLANTMAN",
  "description": "Plant Manager",
  "objectname": "PO",
  "type": "PERSONGROUP",
  "value": "PLANTMAN",
  "isbroadcast": true,
  "isemaildataset": false
}
```

### MAXROLE Fields

| Field | Description | Example |
|-------|-------------|---------|
| `maxrole` | Role ID (unique key) | `"PLANTMAN"` |
| `description` | Human-readable name | `"Plant Manager"` |
| `objectname` | Maximo object this role applies to | `"PO"` |
| `type` | Resolution type | `"PERSONGROUP"` |
| `value` | Person group name or SQL expression | `"PLANTMAN"` or `":purchaseagent"` |
| `isbroadcast` | Send to all group members | `true` |
| `isemaildataset` | Use email dataset | `false` |

### Role Type Values

| type | value field contains | Example |
|------|---------------------|---------|
| `PERSONGROUP` | Person group name | `"PLANTMAN"` |
| `DATA` | SQL expression resolving to person | `":purchaseagent"` |
| `PERSON` | Specific person ID | `"JSMITH"` |

**Note:** MAXROLE key is `maxrole` alone (NOT `maxrole + objectname`). You cannot have two roles with the same name even for different objects.

---

## Deployment Script Pattern

### Bash deployment script
```bash
#!/bin/bash
MAXAUTH=$(echo -n "$MAX_USER:$MAX_PASS" | base64)
BASE="$MAX_URL/oslc/os"

# Step 1: Create roles
for role_json in roles/*.json; do
  echo -n "Creating role: "
  curl -s -w "%{http_code}" -X POST "$BASE/mxapirole?lean=1" \
    -H "Content-Type: application/json" \
    -H "maxauth: $MAXAUTH" \
    -d @"$role_json"
  echo
done

# Step 2: Upload subprocesses (innermost first)
for wf in POAPPR_CRP POAPPR_BUD POAPPR_UNB POAPPR; do
  echo -n "Uploading $wf: "
  curl -s -w "%{http_code}" -X POST "$BASE/mxapiwfprocess?lean=1" \
    -H "Content-Type: application/json" \
    -H "maxauth: $MAXAUTH" \
    -d @"workflows/$wf.json"
  echo
done
```

### Postman Collection Pattern

Create a Postman collection with:
1. **Collection-level auth**: `apikey` header or basic auth
2. **Collection variable**: `baseUrl` = Maximo instance URL
3. **Folder: Roles** — POST requests for each MAXROLE
4. **Folder: Workflows** — POST requests in dependency order
5. **Environment**: Store credentials (apikey, baseUrl)

---

## Common Errors

| Error Code | Message | Cause | Fix |
|-----------|---------|-------|-----|
| BMXAA3608E | Role ID X is not a valid role | MAXROLE record doesn't exist | Create role via `mxapirole` first |
| BMXAA4195E | A value is required for Process field | Missing `?lean=1` parameter | Add `?lean=1` to URL |
| BMXAA4129E | Record already exists | Duplicate role/process name | Delete first or use different name |
| BMXAA0021E | User name and password not valid | Bad credentials | Use `maxauth` header with base64 encoding |
| BMXAA0024E | Action ADD is not allowed | Object structure doesn't permit creation | Check object structure permissions |
| 404 | Unknown Object | Object structure not exposed | Create/enable the object structure in Maximo admin |

---

## Verified Workflow: Complete Example (POAPPR_CRP)

Tested and deployed successfully. 9 nodes, 14 actions, 4 task nodes with separate role assignments.

```
START → INPUT(Select Approver)
           ├─ seq 1: Route to OSM → TASK(OSM, role=OSM)
           ├─ seq 2: Route to DIT → TASK(DIT, role=DIT)
           └─ seq 3: Route to SDE → TASK(SDE, role=SDE)
                                         ↓ (all three)
                                    CONDITION(<=150k?)
                                    ├─ YES → STOP(Approved)
                                    └─ NO → TASK(VPO, role=VPO) → STOP(Approved)
         All TASK reject exits → STOP(Rejected)
```

**Key pattern:** INPUT node choices route to SEPARATE TASK nodes, each with its own ROLEID. Do NOT route multiple INPUT choices to a single TASK node — the assignment role would be wrong for some paths.
