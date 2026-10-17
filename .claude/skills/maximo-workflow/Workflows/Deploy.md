# Deploy Workflow via OSLC API

Deploy Maximo workflows programmatically using the OSLC REST API (`mxapiwfprocess`).

## Prerequisites Check

Before deploying, verify these exist in the target Maximo instance:

### 1. Connection Details
Read `.env` or ask user for:
- `max_url` — Maximo base URL (e.g., `http://192.255.2.42:9082/maximo`)
- `max_username` / `max_password` — Credentials for `maxauth` header

### 2. Verify Dependencies Exist

**Load:** `OSLCDeployment.md` for API reference.

Run checks in this order:

```bash
MAXAUTH=$(echo -n "$username:$password" | base64)

# Check person groups exist
curl -s "$BASE/oslc/os/mxapipersongroup?lean=1&oslc.select=persongroup,description&oslc.pageSize=200" -H "maxauth: $MAXAUTH"

# Check roles exist (mxapirole object structure must be exposed)
curl -s "$BASE/oslc/os/mxapirole?lean=1&oslc.where=objectname=\"PO\"&oslc.select=maxrole,description,value,type" -H "maxauth: $MAXAUTH"

# Check CHANGESTATUS actions exist
curl -s "$BASE/oslc/os/mxapiaction?lean=1&oslc.where=objectname=\"PO\" and type=\"CHANGESTATUS\"&oslc.select=action,description" -H "maxauth: $MAXAUTH"
```

### 3. Create Missing MAXROLE Records

For each role referenced in workflow JSON `wfassignment.roleid`:

```bash
curl -X POST "$BASE/oslc/os/mxapirole?lean=1" \
  -H "Content-Type: application/json" \
  -H "maxauth: $MAXAUTH" \
  -d '{
    "maxrole": "ROLEID",
    "description": "Role Description",
    "objectname": "PO",
    "type": "PERSONGROUP",
    "value": "PERSONGROUPNAME",
    "isbroadcast": true,
    "isemaildataset": false
  }'
```

**Key:** MAXROLE name must be globally unique (not per-object). If a role name exists for another object, you cannot reuse it.

## Deploy Workflow JSON

### Upload Order (Subprocesses First)
1. Innermost subprocesses
2. Mid-level subprocesses
3. Parent process (last)

### POST Request
```bash
curl -s -X POST "$BASE/oslc/os/mxapiwfprocess?lean=1" \
  -H "Content-Type: application/json" \
  -H "Properties: *" \
  -H "maxauth: $MAXAUTH" \
  -d @workflow.json
```

### Verify Upload
```bash
curl -s "$BASE/oslc/os/mxapiwfprocess?lean=1&oslc.where=processname=\"PROCESSNAME\"" \
  -H "maxauth: $MAXAUTH"
```

### Delete and Re-upload (if fixing)
```bash
# Get the resource URL key
# Format: _<base64(OBJECTNAME+PROCESSNAME/PROCESSREV)>
curl -s -X DELETE "$BASE/oslc/os/mxapiwfprocess/_RESOURCEKEY?lean=1" \
  -H "maxauth: $MAXAUTH"
```

## Post-Deploy Verification

1. Query back the workflow and verify node count, actions, assignments
2. Open Workflow Designer in Maximo UI — verify canvas shows nodes
3. Validate process (no orphan nodes, all connections present)
4. Enable process (do NOT activate subprocesses — only parent)

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Canvas empty but data exists | Coordinates in pixel scale (50-900) | Use grid units (-10 to +15) |
| Role ID not valid | MAXROLE record missing | Create via `mxapirole` API |
| Missing `?lean=1` | Field names don't match | Always include `?lean=1` |
| Process field required | JSON property naming mismatch | Use `lean=1` for lowercase fields |
| INPUT routes to wrong role | Single TASK for multiple INPUT choices | Create separate TASK per INPUT choice |
