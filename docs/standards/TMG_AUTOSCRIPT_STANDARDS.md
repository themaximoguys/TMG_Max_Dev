# TMG Automation Script Standards

> Standardization reference for all TMG Maximo Automation Scripts
> Target Platform: MAS 9 | Date: 2026-02-24

---

## Naming Conventions

### General

| Standard | Details | Example | Notes |
|----------|---------|---------|-------|
| Lowercase with dots | All script filenames use lowercase, dot-separated components | `workorder.obj.save.before.py` | No underscores, hyphens, or spaces in filename structure |
| File extension | `.py` for all Jython scripts | `company.disabled.validate.py` | Never `.jy` or `.jython` |
| TMG_ prefix for launch points | All TMG launch point names start with `TMG_` or `SC` prefix | `TMG_PLUSWO_OBJ_ADD` | DB-level identifiers use underscores, not dots |

### Field Validator

| Standard | Details | Example | Notes |
|----------|---------|---------|-------|
| Filename pattern | `[object].fld.[field].[event].py` OR `[object].[field].[event].py` | `company.disabled.validate.py` | Events: validate, action, init, listfilter |
| Launch point name | `TMG[OBJECT][FIELD]_[EVENT]` | `SCCOMPANYDISABLED_VALIDATE` | Uppercase with underscores |
| Script name (DB) | `TMG.[OBJECT][FIELD].[EVENT]` OR `[object].[field].[event]` | `company.disabled.validate` | Matches filename without `.py` |

### Object Script

| Standard | Details | Example | Notes |
|----------|---------|---------|-------|
| Filename pattern | `[object].obj.[event].py` | `pluswo.obj.add.py` | Events: add, init, save, save.before, save.after, save.aftercommit, delete |
| Launch point name | `TMG_[OBJECT]_OBJ_[EVENT]` | `TMG_PLUSWO_OBJ_ADD` | Uppercase with underscores |
| Script name (DB) | `TMG_[OBJECT].OBJ.[EVENT]` | `TMG_PLUSWO.OBJ.ADD` | Matches pattern |

### Cron Task

| Standard | Details | Example | Notes |
|----------|---------|---------|-------|
| Filename pattern | `tmg_[name].cron.action.py` | `tmg_pmwogen.cron.action.py` | Always starts with `tmg_` prefix |
| Script name (DB) | `TMG_[NAME].CRON.ACTION` | `TMG_PMWOGEN.CRON.ACTION` | Uppercase in DB |

### Workflow Action

| Standard | Details | Example | Notes |
|----------|---------|---------|-------|
| Filename pattern | `[object].action.[actionname].py` | `pr.action.wfpofrompr.py` | Action name matches workflow action code |
| Script name (DB) | `[OBJECT].ACTION.[ACTIONNAME]` | `PR.ACTION.WFPOFROMPR` | Uppercase in DB |

### Integration

| Standard | Details | Example | Notes |
|----------|---------|---------|-------|
| Publish Channel exit | `PUBLISH.[CHANNEL].[EXITTYPE].OUT.py` | `PUBLISH.MXWOINTERFACE.EXTEXIT.OUT.py` | EXITTYPE: USEREXIT, EXTEXIT |
| Enterprise Service exit | `SYNC.[SERVICE].[EXITTYPE].IN.py` | `SYNC.MXPERSON.EXTEXIT.IN.py` | EXITTYPE: USEREXIT, EXTEXIT |
| User exit (outbound) | `PUBLISH.[CHANNEL].USEREXIT.OUT.BEFORE.py` | `PUBLISH.MXASSET.USEREXIT.OUT.BEFORE.py` | Add `.BEFORE` or `.AFTER` suffix |

### Escalation Action

| Standard | Details | Example | Notes |
|----------|---------|---------|-------|
| Filename pattern | `[object].escalation.[name].py` | `workorder.escalation.autoclose.py` | Escalation name matches escalation point |

### Status Handler

| Standard | Details | Example | Notes |
|----------|---------|---------|-------|
| Filename pattern | `[object].status.[statuscode].py` | `workorder.status.appr.py` | One script per status transition if needed |

---

## Script Headers

| Script Type | Required Fields | Reference | Delimiter |
|-------------|----------------|-----------|-----------|
| Field Validator | Script name, Object/Field, Event, Author, Naming Convention, Conversion source, Purpose, Business Logic, Launch Points, Dependencies, Revision history | `company.disabled.validate.py` | `################` |
| Object Script | Script name, Object, Launch Point type+event, Description, Converted From (Java class+method), Conversion Review, History | `pluswo.obj.add.py` | `# =======` |
| Cron Task | Script name, Launch Point Type, Active, Debug Mode, Description, Key Features, Author, Revision History | `tmg_pmwogen.cron.action.py` | `# =======` |
| Workflow Action | Script name, Object, Action, Author, Date, Description, Business Requirements, Converted From | `pr.action.wfpofrompr.py` | `########` |
| Integration | Script name, Component type, Channel/Service, Processing Point, Direction, Description, Binding type, Wizard Path, Implicit Variables, History | `PUBLISH.MXWOINTERFACE.EXTEXIT.OUT.py` | `# =======` |

---

## Imports

| Category | Standard | Details | Example | Notes |
|----------|----------|---------|---------|-------|
| Required | Base imports | `from psdi.mbo import MboConstants` `from psdi.server import MXServer` | Always include MboConstants for flags like NOACCESSCHECK, NOVALIDATION | Only import what you use |
| Logging (Option A) | Logger import | `from psdi.util.logging import MXLoggerFactory` | `MXLoggerFactory.getLogger("maximo.script.[scriptname]")` | Required for MXLoggerFactory style; skip if using `service` implicit variable |
| Logging (Option B) | No import needed | `service.log("message")` | Implicit `service` variable | See Logging section for full API |
| Exception | Exception import | `from psdi.util import MXApplicationException` | Used for throwing Maximo-standard business errors | Always re-raise MXApplicationException, catch generic Exception separately |
| SQL | SQL formatting | `from psdi.mbo import SqlFormat` | SqlFormat for parameterized queries | Never concatenate user values into SQL strings directly |
| Integration | Integration imports | `from psdi.iface.mic import MicSetIn` `from psdi.iface.omp import OmpServiceRemote` | Integration scripts may need MicSetIn, MicSetOut, StructureData | Import based on exit type |

---

## Logging

Two logging approaches are available. Choose one per script — do not mix them.

### Option A: MXLoggerFactory (Java Logger)

Uses Java's logging framework via import. Provides fine-grained log level control (DEBUG, INFO, WARN, ERROR) and integrates with Maximo's server-side log configuration.

**Templates:** `templates/mxlogger/`

| Standard | Details | Example | Notes |
|----------|---------|---------|-------|
| Import required | `from psdi.util.logging import MXLoggerFactory` | — | Must import before use |
| Logger Name Convention | `maximo.script.[object].[event]` OR `maximo.application.[CLASSNAME]` | `maximo.script.company.disabled.validate` | Use lowercase dot notation, mirrors Java logger namespace |
| className variable | Set `className = "[scriptname]"` at module level for log prefixes | `className = "pluswo.obj.add"` | Used in `logger.debug(className + ": message")` |
| Log Levels | DEBUG for trace, INFO for milestones, WARN for recoverable, ERROR for failures | `logger.debug(className + ": Starting...")` | Set logLevel to ERROR in production, DEBUG in dev |
| No print() | Never use `print()` or `System.out.println()` in automation scripts | — | Use logger or service, never print |

### Option B: Service Implicit Variable

Uses the `service` implicit variable (ScriptService) available to all automation scripts at runtime. No imports needed. Simpler syntax and provides field-level error binding for UI feedback.

**Templates:** `templates/service/`

| Standard | Details | Example | Notes |
|----------|---------|---------|-------|
| No import needed | `service` is an implicit variable injected at runtime | — | Available in all script types (object, attribute, cron, integration) |
| Script name constant | Set `SCRIPT_NAME = "[scriptname]"` at module level | `SCRIPT_NAME = "pluswo.obj.add"` | Used in `service.log(SCRIPT_NAME + ": message")` |
| General logging | `service.log("message")` | `service.log(SCRIPT_NAME + ": Processing started")` | General-purpose log output |
| Warning logging | `service.log_warn("message")` | `service.log_warn(SCRIPT_NAME + ": Unexpected value")` | Non-fatal warnings |
| Error logging | `service.log_error("message")` | `service.log_error(SCRIPT_NAME + ": Failed")` | Error-level logging |
| Field-level error | `service.error("FIELDNAME", "message")` | `service.error("STATUS", "Cannot close without approval")` | Ties error to specific UI field — user sees error on that field |
| Field error with params | `service.error("FIELDNAME", "message", [params])` | `service.error("PONUM", "Active POs exist", [poList])` | Parameterized field errors |
| User warning popup | `service.warning("message")` | `service.warning("This action cannot be undone")` | Shows warning dialog to user |

### When to Use Which

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Field validation with UI feedback | **Service** | `service.error("FIELD", "msg")` binds errors to specific fields in the UI |
| Background processing (cron tasks) | **MXLoggerFactory** | Fine-grained log levels (DEBUG/INFO) for server-side diagnostics |
| Integration scripts | **Service** | `service` is the MicService — native to integration context |
| Simple object scripts | **Service** | Less boilerplate, no import needed |
| Complex debugging / production diagnostics | **MXLoggerFactory** | Log level filtering via Maximo logging config (System Properties > Logging) |
| Quick prototyping | **Service** | Zero setup, just call `service.log()` |

---

## Error Handling

Two approaches for raising errors to the user. Choose based on your logging style.

### Option A: MXApplicationException (with MXLoggerFactory)

| Standard | Details | Example | Notes |
|----------|---------|---------|-------|
| Try/except structure | `try: [logic] except MXApplicationException: raise except Exception: logger.error(); raise` | See `company.disabled.validate.py` | Always re-raise MXApplicationException so Maximo shows proper error message to user |
| Validation errors | `raise MXApplicationException("group", "key", params)` | `raise MXApplicationException("company", "activePONoDisable", [poList])` | Error group/key must exist in Maximo message table |
| MboSet cleanup | Always close MboSets in finally blocks | `try: [use set] finally: mbo_set.close()` | Prevents memory leaks and DB cursor exhaustion |

### Option B: service.error() (with Service Implicit Variable)

| Standard | Details | Example | Notes |
|----------|---------|---------|-------|
| Try/except structure | `try: [logic] except Exception: service.log_error(); raise` | See service templates | No need to separately catch MXApplicationException when using service.error() |
| Field-level validation | `service.error("FIELDNAME", "error message")` | `service.error("STATUS", "Cannot close without required fields")` | Error displays on the specified field in UI — no message table entry needed |
| Parameterized errors | `service.error("FIELD", "message", [param1, param2])` | `service.error("PONUM", "Active POs: {0}", [poList])` | Supports parameter substitution |
| User warning (non-blocking) | `service.warning("warning message")` | `service.warning("This will affect related records")` | Shows dialog but does not block save |
| MboSet cleanup | Always close MboSets in finally blocks | `try: [use set] finally: mbo_set.close()` | Same rule applies regardless of logging style |

### Comparison

| Aspect | MXApplicationException | service.error() |
|--------|----------------------|-----------------|
| **Import** | `from psdi.util import MXApplicationException` | None (implicit) |
| **Message source** | Maximo message table (group + key) | Inline string |
| **Field binding** | No (generic error dialog) | Yes (error shows on specific field) |
| **Parameterization** | Via message table placeholders | Via `[param]` list |
| **Best for** | Reusable error messages defined in message table | Quick field-level validation feedback |
| **Localization** | Yes (message table supports multi-language) | No (inline strings are hardcoded) |

---

## Script Consolidation Rules

### One Script Per MBO Per Event (CRITICAL)

Each MBO object must have **only one** script per event type. Do NOT create duplicate script names or multiple scripts for the same object + event combination.

| Rule | Details | Example |
|------|---------|---------|
| **One before-save per MBO** | All pre-save logic for an object goes into a single `[object].obj.save.before.py` | `workorder.obj.save.before.py` handles ALL before-save rules for WORKORDER |
| **One after-save per MBO** | All post-save logic for an object goes into a single `[object].obj.save.after.py` | `workorder.obj.save.after.py` handles ALL after-save rules for WORKORDER |
| **One add per MBO** | All add/initialization logic goes into a single `[object].obj.add.py` | `pluswo.obj.add.py` handles ALL new-record defaults for PLUSWO |
| **One init per MBO** | All init logic goes into a single `[object].obj.init.py` | `asset.obj.init.py` handles ALL load-time setup for ASSET |
| **No duplicate script names** | Script names (autoscript in DB) must be unique across the entire system | Never create two scripts with the same `autoscript` value |

### Organize Logic Into Functions

When a single script handles multiple business rules (which it will, since there's one script per event), organize each concern into its own function. Call them from the main execution block.

**Pattern:**

```python
# workorder.obj.save.before.py — ALL before-save logic for WORKORDER

SCRIPT_NAME = "workorder.obj.save.before"

def validate_required_fields():
    """Rule 1: Check required fields based on status."""
    status = mbo.getString("STATUS")
    if status == "APPR" and mbo.isNull("TMG_APPROVEDBY"):
        service.error("TMG_APPROVEDBY", "Approver is required")

def validate_gl_account():
    """Rule 2: Validate GL account format."""
    if not mbo.isNull("GLACCOUNT"):
        gl = mbo.getString("GLACCOUNT")
        if len(gl) < 10:
            service.error("GLACCOUNT", "GL Account format is invalid")

def set_calculated_fields():
    """Rule 3: Auto-populate calculated fields before save."""
    if mbo.isNull("TMG_TOTALCOST"):
        labor = mbo.getDouble("TMG_LABORCOST")
        material = mbo.getDouble("TMG_MATERIALCOST")
        mbo.setValue("TMG_TOTALCOST", labor + material, MboConstants.NOACCESSCHECK)

def apply_org_specific_rules():
    """Rule 4: ORG1-specific business rules."""
    orgid = mbo.getString("ORGID")
    if orgid and orgid.upper() == "ORG1":
        # ORG1-specific logic here
        pass

# ==========================================================================================
# MAIN EXECUTION — Call each function in order
# ==========================================================================================
try:
    validate_required_fields()
    validate_gl_account()
    set_calculated_fields()
    apply_org_specific_rules()
    service.log(SCRIPT_NAME + ": Before save completed")
except Exception as e:
    service.log_error(SCRIPT_NAME + ": Error: " + str(e))
    raise
```

### Why This Matters

| Problem | Consequence |
|---------|-------------|
| Multiple scripts on same MBO + event | Execution order is unpredictable; race conditions; debugging nightmare |
| Duplicate script names | Second script silently overwrites the first in DB; lost business logic |
| All logic in one big block | Impossible to test, debug, or maintain individual rules |
| Functions without clear names | Hard to trace which business rule failed in logs |

---

## scriptConfig Block

| Standard | Details | Example | Notes |
|----------|---------|---------|-------|
| Required structure | Dict with: `autoscript`, `description`, `version`, `active`, `logLevel`, `scriptLaunchPoints` | See any template | Placed at bottom of every script |
| Launch Point fields | `launchPointName`, `launchPointType`, `objectName`, `attributeName` (for ATTRIBUTE), `event`/`action`, `description`, `active` | See templates | launchPointType: OBJECT, ATTRIBUTE, ACTION |
| Object LP event flags | `init`, `add`, `update`, `delete`, `save`, `beforeSave`, `afterSave`, `afterCommit` — set True/False | See `pluswo.obj.add.py` | Only set True for the events this script handles; include `beforeSave: True` for pre-save scripts |
| Attribute LP event field | `validate: True` for validation, `runAction: True` for action | `validate: True` OR `runAction: True` | One or the other per launch point |
| Integration binding | Integration scripts bind by name, not launch points | Binding: Name-based (NO launch point) | Configured via Automation Scripts wizard > Script for Integration |

---

## Implicit Variables

| Scope | Variable | Details | Example | Notes |
|-------|----------|---------|---------|-------|
| All scripts | `mbo` | Current MBO being processed | `mbo.getString("FIELDNAME")` | Available in all script types |
| Field validators | `mbo` (as MboValue) | MboValue when script is attribute launch point | `mbo.getMbo()` to get parent Mbo | Note: `mbo` is MboValue not Mbo in attribute scripts |
| Cron tasks | `croninstance` | CronTaskInstance for accessing cron parameters | `croninstance.getParamAsString("paramname")` | Only in cron task scripts |
| Integration | `irData` / `erData` | Internal and External StructureData | `irData.getCurrentData("WORKORDER")` | irData = Maximo side, erData = external side |
| All scripts | `service` | ScriptService — logging, errors, warnings | `service.log("msg")`, `service.error("FIELD", "msg")` | Available in all script types; in integration scripts this is MicService |

---

## MBO Access Patterns

| Standard | Details | Example | Notes |
|----------|---------|---------|-------|
| Get values | `mbo.getString("FIELD")`, `mbo.getInt("FIELD")`, `mbo.getBoolean("FLAG")` | `status = mbo.getString("STATUS")` | Returns typed value from MBO field |
| Set values | `mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK)` | `mbo.setValue("TMG_UNITCOND", "ONLINE", MboConstants.NOACCESSCHECK)` | Use NOACCESSCHECK to bypass field-level security |
| Related sets | `mbo.getMboSet("RELATIONSHIPNAME")` or `mbo.getMboSet("$alias", "OBJECT", "where")` | `po_set = mbo.getMboSet("TMG_PO_ACTIVE")` | Named relationships preferred; ad-hoc sets use `$` prefix |
| SQL queries | SqlFormat for parameterized queries with `:1`, `:2` placeholders | `sf = SqlFormat(mbo, "field = :1"); sf.setObject(1, "OBJ", "FIELD", val)` | Never concatenate values into SQL strings |

---

## TMG-Specific Conventions

| Standard | Details | Example | Notes |
|----------|---------|---------|-------|
| TMG_ prefix | All TMG custom fields/objects/relationships use `TMG_` prefix | `TMG_UNITCOND`, `TMG_TRR`, `TMG_PO_ACTIVE` | Applies to fields, attributes, relationships, and custom objects |
| Organization checks | ORG1 org has special rules in many scripts (ORG1 = (client-specific organization), different from TMG parent) | `if orgid.upper() == "ORG1":` | Many field validators branch on ORG1 vs non-ORG1 |
| GL account validation | `TMG_FldFullGLAccount` is the most reused field validator class (appears 50+ times) | Shared across COMPANIES, INVBALANCES, PO, CONTRACTLINE, etc. | Consider single shared script with multiple launch points |
| Inactive statuses | Common inactive status list: NOT READY, REMOVED, RIP, INACTIVE | `inactive_statuses = ["NOT READY", "REMOVED", "RIP", "INACTIVE"]` | Used in location and asset scripts |

---

## Template Paths

| Logging Style | Directory | Description |
|---------------|-----------|-------------|
| MXLoggerFactory (Java Logger) | `conversion-catalog/templates/mxlogger/` | 14 templates using `from psdi.util.logging import MXLoggerFactory` |
| Service Implicit Variable | `conversion-catalog/templates/service/` | 14 templates using `service.log()`, `service.error()` — no logging imports |

---

## Deployment Paths

| Script Type | Output Path | Example | Notes |
|-------------|-------------|---------|-------|
| Object scripts | `automation-scripts/object_scripts/[objectname]/` | `automation-scripts/object_scripts/pluswo/` | One folder per object |
| Field validators | `automation-scripts/field_validators/module_[nn]_[name]/` | `automation-scripts/field_validators/module_00_company_glaccount/` | Numbered modules group related validators |
| Cron tasks | `automation-scripts/cron_tasks/` | `automation-scripts/cron_tasks/tmg_pmwogen.cron.action.py` | Flat directory |
| Workflow actions | `automation-scripts/workflow_actions/[module]/` | `automation-scripts/workflow_actions/wfpofrompr/` | One folder per action |
| Integration scripts | `automation-scripts/integration_scripts/[type]/` | `[type]`: publish_channel or enterprise_service or object_structure | Organized by integration component type |

---

## Testing

| Standard | Details | Notes |
|----------|---------|-------|
| Required steps | 1) Script created 2) Launch point configured 3) Launch point active 4) Script active 5) Functional test 6) Error handling test 7) Performance check 8) Logs reviewed | Document results per script |
| Implicit vars warning | `mbo`/`service`/`irData`/`erData` show as undefined in IDE — this is expected | Maximo runtime provides these variables |

---

## Anti-Patterns and Security (DO NOT DO)

> Things to **never** do in Maximo automation scripts. Every item includes the bad pattern and the correct alternative.

---

### 1. SQL Injection — String Concatenation in Where Clauses

Never build SQL where clauses by concatenating user-supplied values.

**BAD:**
```python
# DANGEROUS — SQL injection via user input
wonum = mbo.getString("WONUM")
wo_set = mbo.getMboSet("$wocheck", "WORKORDER", "wonum = '" + wonum + "'")
```

**CORRECT:**
```python
# SAFE — Use SqlFormat for parameterized queries
from psdi.mbo import SqlFormat

sf = SqlFormat(mbo, "wonum = :1")
sf.setObject(1, "WORKORDER", "WONUM", mbo.getString("WONUM"))
wo_set = mbo.getMboSet("$wocheck", "WORKORDER", sf.format())
```

**Why:** A value like `' OR 1=1 --` in WONUM would return all work orders or worse. SqlFormat parameterizes the value, preventing injection.

---

### 2. Swallowing Exceptions Silently

Never catch exceptions without re-raising or logging. Silent failures are invisible in production.

**BAD:**
```python
try:
    mbo.setValue("STATUS", "APPR")
except:
    pass  # Silently swallowed — no one will ever know this failed
```

**CORRECT:**
```python
try:
    mbo.setValue("STATUS", "APPR")
except MXApplicationException as mxe:
    service.log_warn(SCRIPT_NAME + ": Status change failed: " + str(mxe))
    raise
except Exception as e:
    service.log_error(SCRIPT_NAME + ": Unexpected error: " + str(e))
    raise
```

**Why:** Silent exceptions cause data inconsistency — record appears saved but business rules didn't execute.

---

### 3. Using print() or System.out for Logging

Never use `print()` or Java's `System.out.println()`. Output goes to server stdout and is not captured by Maximo's logging system.

**BAD:**
```python
print("Processing work order: " + wonum)
from java.lang import System
System.out.println("Debug: status = " + status)
```

**CORRECT:**
```python
# Option A: MXLoggerFactory
logger.debug(className + ": Processing work order: " + wonum)

# Option B: service implicit variable
service.log(SCRIPT_NAME + ": Processing work order: " + wonum)
```

**Why:** `print()` output is lost in clustered environments, cannot be filtered by log level, and may expose data in server console logs.

---

### 4. Not Closing MboSets (Memory / Cursor Leak)

Always close MboSets obtained via ad-hoc queries. Unclosed sets leak database cursors and JVM memory.

**BAD:**
```python
po_set = mbo.getMboSet("$pocheck", "PO", "status = 'APPR'")
po = po_set.getMbo(0)
if po is not None:
    total = po.getDouble("TOTALCOST")
# po_set is NEVER closed — cursor stays open until GC (if ever)
```

**CORRECT:**
```python
po_set = mbo.getMboSet("$pocheck", "PO", "status = 'APPR'")
try:
    po = po_set.getMbo(0)
    if po is not None:
        total = po.getDouble("TOTALCOST")
finally:
    po_set.close()
```

**Why:** Each unclosed MboSet holds a JDBC cursor. Under load, this exhausts the connection pool and causes `ORA-01000: maximum open cursors exceeded` or equivalent.

---

### 5. Hardcoding Credentials, URLs, or Environment Values

Never embed passwords, API keys, URLs, or environment-specific values in script source.

**BAD:**
```python
import urllib2
url = "https://prod-api.tmg.com/endpoint"
headers = {"Authorization": "Bearer sk-abc123secretkey"}
req = urllib2.Request(url, headers=headers)
```

**CORRECT:**
```python
from psdi.server import MXServer

# Use Maximo system properties or endpoint configuration
mxserver = MXServer.getMXServer()
url = mxserver.getProperty("tmg.api.endpoint")
api_key = mxserver.getProperty("tmg.api.key")
# Or use Maximo's End Point configuration for integration
```

**Why:** Credentials in source code get committed to version control, are visible to anyone with script access, and break during environment promotion (dev → test → prod).

---

### 6. Abusing NOACCESSCHECK and NOVALIDATION

Don't blindly use `NOACCESSCHECK | NOVALIDATION` on every `setValue`. Only bypass checks when you have a specific reason.

**BAD:**
```python
# Bypasses ALL security and validation on every field — why?
mbo.setValue("STATUS", user_input, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
mbo.setValue("DESCRIPTION", user_input, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
mbo.setValue("WONUM", user_input, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

**CORRECT:**
```python
# NOACCESSCHECK: Only when script needs to set fields the current user can't edit
# (e.g., system-populated audit fields)
mbo.setValue("TMG_APPROVEDBY", username, MboConstants.NOACCESSCHECK)

# No flags: When the user's security profile should be respected
mbo.setValue("DESCRIPTION", new_desc)

# NOVALIDATION: Only when setting intermediate values that will be valid after more fields are set
mbo.setValue("GLACCOUNT", partial_gl, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
mbo.setValue("GLCOMP1", segment1)  # This triggers revalidation
```

**Why:** `NOVALIDATION` skips business rules that exist for a reason. `NOACCESSCHECK` bypasses security groups. Use them surgically, not as defaults.

---

### 7. Threading in Automation Scripts

Never create threads in Jython automation scripts. Maximo manages its own thread pool and transaction context.

**BAD:**
```python
from java.lang import Thread, Runnable

class MyTask(Runnable):
    def run(self):
        # This runs OUTSIDE the Maximo transaction context
        mbo.setValue("STATUS", "COMP")  # Will fail or corrupt data

Thread(MyTask()).start()
```

**CORRECT:**
```python
# Do work synchronously within the script
# For async work, use Maximo's built-in mechanisms:
# - Cron tasks for scheduled background work
# - Escalations for condition-based triggers
# - Integration queues for async messaging
mbo.setValue("STATUS", "COMP")
```

**Why:** Spawned threads don't have MBO transaction context, UserInfo, or database connection. They cause `NullPointerException`, data corruption, or silent failures.

---

### 8. Unbounded MboSet Queries (N+1 and Full Table Scans)

Never fetch all records without a where clause or iterate without limits.

**BAD:**
```python
# Fetches ALL work orders in the system — could be millions
wo_set = mxserver.getMboSet("WORKORDER", userInfo)
# No setWhere() — full table scan
index = 0
while True:
    wo = wo_set.getMbo(index)
    if wo is None:
        break
    # Process every record...
    index += 1
```

**CORRECT:**
```python
wo_set = mxserver.getMboSet("WORKORDER", userInfo)
wo_set.setWhere("siteid = 'BEDFORD' and status in ('APPR', 'INPRG')")
wo_set.setOrderBy("wonum")
wo_set.reset()

# Process with bounds
index = 0
while index < 1000:  # Safety limit
    wo = wo_set.getMbo(index)
    if wo is None:
        break
    # Process record
    index += 1
```

**Why:** Unbounded queries load millions of MBO objects into JVM heap, causing `OutOfMemoryError` and server crashes. Always filter with `setWhere()` and consider batch limits.

---

### 9. Modifying MBO During Init Event

Don't call `setValue()` during the INIT event for existing records. Init is for read-only setup (field flags, visibility).

**BAD:**
```python
# In an INIT script — this triggers save/dirty on every record load
mbo.setValue("TMG_CALCFIELD", computed_value)  # Marks record as modified!
```

**CORRECT:**
```python
# INIT: Only set field flags, readonly, visibility
mbo.setFieldFlag("TMG_CALCFIELD", MboConstants.READONLY, True)

# If you need to set values, do it in ADD (new records) or SAVE (updates)
```

**Why:** Setting values during INIT marks the record as modified. Users see "Save changes?" dialogs when they haven't changed anything. In list views, this can trigger mass-save loops.

---

### 10. Hardcoding Site/Org/Status Values

Don't hardcode site IDs, org IDs, or status values that vary across environments.

**BAD:**
```python
if mbo.getString("SITEID") == "BEDFORD":
    # What about other sites? What about test environments?
    pass
if mbo.getString("STATUS") == "WAPPR":
    # Status synonyms exist — "WAPPR" might be mapped differently
    pass
```

**CORRECT:**
```python
# Use Maximo's domain/synonym lookups
from psdi.mbo import MboConstants

siteid = mbo.getString("SITEID")
orgid = mbo.getString("ORGID")

# For status, use internal value or check synonyms
status_mbovalue = mbo.getMboValue("STATUS")
internal_status = status_mbovalue.getString()
# Or check against maxvalue for synonym-safe comparison

# For TMG: Use org-based branching, not site-specific
if orgid and orgid.upper() == "ORG1":
    # ORG1-specific rules
    pass
```

**Why:** Hardcoded values break during environment promotion, don't account for new sites/orgs, and ignore Maximo's synonym domain system.

---

### 11. Direct Java Class Imports for Removed/Deprecated APIs

Don't import Java classes that were removed or deprecated in Java 17 / MAS 9.

**BAD:**
```python
from sun.misc import BASE64Encoder  # Removed in Java 17
from javax.xml.bind import DatatypeConverter  # Moved to jakarta.*
import thread  # Python threading — not safe in Maximo
```

**CORRECT:**
```python
from java.util import Base64  # Java 17 standard
encoder = Base64.getEncoder()
encoded = encoder.encodeToString(data)

# For XML binding in MAS 9
from jakarta.xml.bind import DatatypeConverter
```

**Why:** `sun.misc.*` and `javax.xml.bind.*` are removed in Java 17. Scripts will fail with `ImportError` on MAS 9.

---

### 12. Not Checking for Null Values

Never assume a field has a value. Always null-check before operations.

**BAD:**
```python
wonum = mbo.getString("WONUM")
prefix = wonum[0:2]  # NullPointerException if WONUM is null
total = mbo.getDouble("TOTALCOST") + mbo.getDouble("TAX")  # NPE if null
```

**CORRECT:**
```python
if not mbo.isNull("WONUM"):
    wonum = mbo.getString("WONUM")
    prefix = wonum[0:2]

# For numeric fields, getDouble/getInt return 0 for null — but check if logic requires distinction
if not mbo.isNull("TOTALCOST"):
    total = mbo.getDouble("TOTALCOST") + mbo.getDouble("TAX")
```

**Why:** Null fields are common in Maximo. `getString()` returns empty string for null, but downstream operations (substring, comparison) can still fail.

---

### 13. Using `fetchStopLimitEnabled(false)` Without Justification

Don't disable the fetch stop limit to load all records.

**BAD:**
```python
wo_set = mbo.getMboSet("$allwo", "WORKORDER", "status = 'APPR'")
wo_set.setFlag(MboConstants.DISCARDABLE, True)
wo_set.fetchStopLimitEnabled(False)  # Loads ALL matching records into memory
```

**CORRECT:**
```python
wo_set = mbo.getMboSet("$allwo", "WORKORDER", "status = 'APPR' and siteid = :1")
# Process in batches using getMbo(index) — Maximo fetches pages automatically
# If you truly need all records, document WHY and add a count check first
count = wo_set.count()
if count > 10000:
    service.log_warn(SCRIPT_NAME + ": Large set detected: " + str(count))
```

**Why:** Disabling fetch limits loads entire result sets into JVM heap. With 100K+ records this causes OutOfMemoryError.

---

### 14. Committing Transactions Inside Scripts

Never call `MXTransaction.commit()` inside an automation script. Maximo manages the transaction.

**BAD:**
```python
mxserver = MXServer.getMXServer()
conn = mxserver.getDBConnection()
conn.commit()  # Breaks Maximo's transaction boundary
```

**CORRECT:**
```python
# Let Maximo manage the transaction
# Your script runs inside Maximo's transaction scope
# Changes commit when the user saves (or cron task completes)
# If you need separate transaction, use MXServer.runAsNewTransaction()
```

**Why:** Manual commits break Maximo's transaction integrity. If a later step fails, the committed changes can't be rolled back, leaving data in an inconsistent state.

---

### 15. Logging Sensitive Data

Never log passwords, SSNs, financial account numbers, or PII.

**BAD:**
```python
service.log("User password: " + mbo.getString("TMG_PASSWORD"))
service.log("SSN: " + mbo.getString("TMG_SSN"))
logger.debug("Credit card: " + mbo.getString("TMG_CCNUMBER"))
```

**CORRECT:**
```python
service.log(SCRIPT_NAME + ": Processing user: " + mbo.getString("PERSONID"))
# Never log sensitive fields — log identifiers only
# If debugging auth, log success/failure status, not credentials
service.log(SCRIPT_NAME + ": Auth result: " + ("success" if authenticated else "failed"))
```

**Why:** Log files are accessible to system admins, stored in plain text, and often included in support tickets. Sensitive data in logs violates compliance (SOX, PCI, HIPAA).

---

### Quick Reference Summary

| # | Anti-Pattern | Risk Level | Remedy |
|---|-------------|------------|--------|
| 1 | SQL injection via string concat | **CRITICAL** | Use `SqlFormat` for all where clauses |
| 2 | Swallowing exceptions silently | **HIGH** | Always log + re-raise |
| 3 | Using print() / System.out | **MEDIUM** | Use MXLoggerFactory or service.log() |
| 4 | Not closing MboSets | **HIGH** | `try/finally` with `.close()` |
| 5 | Hardcoded credentials/URLs | **CRITICAL** | Use system properties or endpoint config |
| 6 | Blanket NOACCESSCHECK/NOVALIDATION | **HIGH** | Use only when specifically justified |
| 7 | Threading in scripts | **CRITICAL** | Use cron tasks, escalations, or queues |
| 8 | Unbounded MboSet queries | **HIGH** | Always `setWhere()` + batch limits |
| 9 | setValue() during INIT | **MEDIUM** | INIT = read-only setup; use ADD/SAVE for values |
| 10 | Hardcoded site/org/status | **MEDIUM** | Use org-based branching + synonym lookups |
| 11 | Deprecated Java imports | **HIGH** | Use Java 17 / jakarta.* equivalents |
| 12 | No null checking | **MEDIUM** | `mbo.isNull("FIELD")` before access |
| 13 | Disabling fetch stop limit | **HIGH** | Process in batches; count before loading |
| 14 | Manual transaction commits | **CRITICAL** | Let Maximo manage transactions |
| 15 | Logging sensitive data | **CRITICAL** | Log identifiers only, never credentials/PII |
