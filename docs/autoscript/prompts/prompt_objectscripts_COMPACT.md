# Object Script Conversion Prompt (Compact)

**Purpose**: Converting Java MBO classes to Python automation scripts  
**Version**: 2.0.0  
**Last Updated**: 2025-12-08  
**Context**: MAS 9 upgrade - 110+ Java MBO classes → Python Object/Action scripts

**📘 PREREQUISITE**: Read `prompt_master_conversion_guide.md` for common standards (headers, Python idioms, scriptConfig, patterns, checklists)

---

## Quick Conversion Prompt

```
Convert Maximo Java MBO to Python automation script for MAS 9.

**Java MBO**: [TMG_XXXXX]
**Path**: [Full path]
**Module**: [Invoice/Work Order/etc.]
**Base Class**: [Mbo/MboSet]
**Complexity**: [Simple/Medium/Complex]
**LOC**: [XXX]

**Source**: [Paste Java code]

**Requirements** (see master guide for details):
1. Analyze Java: Identify methods (init, add, save, delete, custom actions)
2. Create directory: automation-scripts/object_scripts/[objectname]/
3. Follow master guide: Headers, Python idioms, MboConstants, exception handling
4. **CRITICAL**: Determine event timing from Java method analysis (see table below)
5. scriptConfig at END with all launch points
6. Update OBJECT_INVENTORY.md

**Reference**: 
- Master Guide: prompt_master_conversion_guide.md
- Launch Points: Knowledge-base/LAUNCH_POINT_REFERENCE_PATTERNS.md
- Inventory: automation-scripts/object_scripts/OBJECT_INVENTORY.md
```

---

## Object Launch Point Types (Quick Reference)

### Java Method → Event Timing Mapping

| Java Method | Java Pattern | Python Event | Operation Flags | scriptConfig |
|------------|--------------|--------------|-----------------|--------------|
| `init()` | Set defaults | `initializeValue: True` | None | NO operation flags |
| `appValidate()` | Validation | `save: True, beforeSave: True` | `add: True, update: True, delete: False` | Validate before save |
| `save()` BEFORE `super.save()` | Field changes | `save: True, beforeSave: True` | `add: True, update: True, delete: False` | Modify before save |
| `save()` AFTER `super.save()` | Trigger saves | `save: True, afterSave: True` | `add: True, update: True, delete: False` | After record saved |
| `save()` with `otherMbo.save()` | Cascading | `save: True, afterSave: True` | `add: True, update: True, delete: False` | Cascade to related |
| `save()` with email/notify | External calls | `save: True, afterCommit: True` | `add: True, update: True, delete: False` | After DB commit |
| `add()` | New records | `save: True, afterSave: True` | `add: True, update: False, delete: False` | NEW records only |
| `canDelete()` | Delete validation | `save: True, beforeSave: True` | `add: False, update: False, delete: True` | Validate deletion |
| `delete(long)` | Delete cleanup | `save: True, afterSave: True` | `add: False, update: False, delete: True` | After deletion |

**CRITICAL**: 
- ALL events use SAVE launch point with operation flags (add/update/delete)
- INIT is the ONLY exception (uses `initializeValue: True`, no operation flags)
- ADD events MUST include `save: True` with timing
- DELETE operations use SAVE with `delete: True` flag

---

## scriptConfig Templates

### 1. INIT Event (Object Initialization)

```python
scriptConfig = {
    "autoscript": "[OBJECT].OBJ.INIT",
    "description": "Initialize [object] defaults",
    "version": "1.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [{
        "launchPointName": "[OBJECT]_OBJ_INIT",
        "launchPointType": "OBJECT",
        "objectName": "[OBJECT]",
        "active": True,
        "description": "Initialize object",
        "initializeValue": True
        # NO operation flags for INIT
    }]
}
```

### 2. SAVE Event - beforeSave (Validation/Field Changes)

```python
scriptConfig = {
    "autoscript": "[OBJECT].OBJ.BEFORESAVE",
    "description": "Validate/modify [object] before save",
    "version": "1.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [{
        "launchPointName": "[OBJECT]_OBJ_BEFORESAVE",
        "launchPointType": "OBJECT",
        "objectName": "[OBJECT]",
        "active": True,
        "description": "Process before save",
        "save": True,
        "add": True,      # Run on new records
        "update": True,   # Run on updates
        "delete": False,  # Don't run on deletes
        "beforeSave": True
    }]
}
```

### 3. SAVE Event - afterSave (Cascade/Related Updates)

```python
scriptConfig = {
    "autoscript": "[OBJECT].OBJ.AFTERSAVE",
    "description": "Process [object] after save",
    "version": "1.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [{
        "launchPointName": "[OBJECT]_OBJ_AFTERSAVE",
        "launchPointType": "OBJECT",
        "objectName": "[OBJECT]",
        "active": True,
        "description": "Cascade updates after save",
        "save": True,
        "add": True,      # Run on new records
        "update": True,   # Run on updates
        "delete": False,  # Don't run on deletes
        "afterSave": True
    }]
}
```

### 4. SAVE Event - afterCommit (Notifications/External)

```python
scriptConfig = {
    "autoscript": "[OBJECT].OBJ.AFTERCOMMIT",
    "description": "Send notifications after [object] commit",
    "version": "1.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [{
        "launchPointName": "[OBJECT]_OBJ_AFTERCOMMIT",
        "launchPointType": "OBJECT",
        "objectName": "[OBJECT]",
        "active": True,
        "description": "Notify after DB commit",
        "save": True,
        "add": True,
        "update": True,
        "delete": False,
        "afterCommit": True
    }]
}
```

### 5. ADD Event (New Records Only)

```python
scriptConfig = {
    "autoscript": "[OBJECT].OBJ.ADD",
    "description": "Process new [object] records",
    "version": "1.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [{
        "launchPointName": "[OBJECT]_OBJ_ADD",
        "launchPointType": "OBJECT",
        "objectName": "[OBJECT]",
        "active": True,
        "description": "Process after adding new record",
        "save": True,
        "add": True,       # ONLY new records
        "update": False,   # NOT on updates
        "delete": False,
        "afterSave": True  # After new record saved
    }]
}
```

### 6. canDelete (Delete Validation)

```python
scriptConfig = {
    "autoscript": "[OBJECT].OBJ.CANDELETE",
    "description": "Validate [object] deletion",
    "version": "1.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [{
        "launchPointName": "[OBJECT]_OBJ_CANDELETE",
        "launchPointType": "OBJECT",
        "objectName": "[OBJECT]",
        "active": True,
        "description": "Validate before deletion",
        "save": True,
        "add": False,
        "update": False,
        "delete": True,     # Run on deletes
        "beforeSave": True  # Validate before deletion
    }]
}
```

### 7. delete() (Delete Cleanup)

```python
scriptConfig = {
    "autoscript": "[OBJECT].OBJ.DELETE",
    "description": "Cleanup after [object] deletion",
    "version": "1.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [{
        "launchPointName": "[OBJECT]_OBJ_DELETE",
        "launchPointType": "OBJECT",
        "objectName": "[OBJECT]",
        "active": True,
        "description": "Process after deletion",
        "save": True,
        "add": False,
        "update": False,
        "delete": True,    # Run on deletes
        "afterSave": True  # After record deleted
    }]
}
```

### 8. ACTION (Custom Method)

```python
scriptConfig = {
    "autoscript": "[OBJECT].ACT.[ACTIONNAME]",
    "description": "Custom action for [object]",
    "version": "1.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [{
        "launchPointName": "[OBJECT]_ACT_[ACTIONNAME]",
        "launchPointType": "ACTION",
        "objectName": "[OBJECT]",
        "action": "[ACTIONNAME]",
        "active": True,
        "description": "Custom action"
        # NO operation flags for ACTION
    }],
    "scriptVariables": [
        {
            "varName": "[param1]",
            "varBindingType": "INPARAM",
            "varBindingValue": "[param1]",
            "varType": "String"
        },
        {
            "varName": "[result]",
            "varBindingType": "OUTPARAM",
            "varBindingValue": "[result]",
            "varType": "Boolean"
        }
    ]
}
```

---

## Object-Specific Patterns

### Pattern: Multiple Events (init + save)

If Java class has BOTH `init()` and `save()`, create TWO separate scripts:

```
classspec/
  ├── classspec.obj.init.py          # For init() method
  ├── classspec.obj.beforesave.py    # For save() method (if before super.save())
  └── classspec.obj.aftersave.py     # For save() method (if after super.save())
```

Each script has ONE launch point. Do NOT combine multiple events in one script.

---

## Code Optimization (Object Scripts)

### Minimize MboSet Operations

```python
# ❌ INEFFICIENT - Multiple queries
for i in range(mboSet1.count()):
    mbo1 = mboSet1.getMbo(i)
    mboSet2 = mbo1.getMboSet("REL")
    for j in range(mboSet2.count()):  # Nested loop
        # Process

# ✅ EFFICIENT - Single query with SQL
mboSet = mbo.getMboSet("$combined", "OBJECT",
    "WHERE condition IN (SELECT ...)")
for i in range(mboSet.count()):
    # Process once
```

### Cache Frequently Accessed Values

```python
# ❌ INEFFICIENT - Repeated getString
for i in range(100):
    if mbo.getString("STATUS") == "ACTIVE":
        # Calls getString 100 times

# ✅ EFFICIENT - Cache value
status = mbo.getString("STATUS")
for i in range(100):
    if status == "ACTIVE":
        # Cached value
```

### Use Relationships vs Manual Queries

```python
# ❌ AVOID - Manual query
mboSet = mxServer.getMboSet("WORKORDER", userInfo)
mboSet.setWhere("WONUM='" + wonum + "'")

# ✅ PREFERRED - Use relationship
mboSet = mbo.getMboSet("WORKORDER")  # If relationship defined
```

---

## Quick Checklist

See master guide for full checklist. Object script essentials:

- [ ] Java method → event timing correctly mapped
- [ ] Operation flags match use case (add/update/delete)
- [ ] scriptConfig at END with all launch points
- [ ] INIT uses `initializeValue: True` (no operation flags)
- [ ] SAVE events use operation flags (add/update/delete)
- [ ] ACTION has scriptVariables if parameters exist
- [ ] MboSets closed in finally blocks
- [ ] Exceptions re-raised
- [ ] Update OBJECT_INVENTORY.md

---

## Examples

### Example 1: Simple Init

**Java**: `public void init() { setValue("field", "default", 11L); }`

**Python** (`classspec.obj.init.py`):
```python
from psdi.mbo import MboConstants

mbo.setValue("field", "default", 
    MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

scriptConfig = {
    "autoscript": "CLASSSPEC.OBJ.INIT",
    # ...
    "scriptLaunchPoints": [{
        "launchPointName": "CLASSSPEC_OBJ_INIT",
        "launchPointType": "OBJECT",
        "objectName": "CLASSSPEC",
        "active": True,
        "initializeValue": True
    }]
}
```

### Example 2: Save with Validation

**Java**: `public void save() throws ... { if (invalid) throw MXException; super.save(); }`

**Python** (`invoice.obj.beforesave.py`):
```python
# Validation before save
if someCondition:
    from psdi.util import MXException
    raise MXException("error", "key")

scriptConfig = {
    "autoscript": "INVOICE.OBJ.BEFORESAVE",
    # ...
    "scriptLaunchPoints": [{
        "launchPointName": "INVOICE_OBJ_BEFORESAVE",
        "launchPointType": "OBJECT",
        "objectName": "INVOICE",
        "active": True,
        "save": True,
        "add": True,
        "update": True,
        "delete": False,
        "beforeSave": True
    }]
}
```

---

## See Also

- **Master Guide**: `prompt_master_conversion_guide.md` (Common standards, patterns, Python idioms)
- **Launch Points**: `Knowledge-base/LAUNCH_POINT_REFERENCE_PATTERNS.md` (Complete examples)
- **Inventory**: `automation-scripts/object_scripts/OBJECT_INVENTORY.md` (Track progress)
- **Cron Tasks**: `prompt_crontasks.md` (If converting cron tasks)

---

**VERSION**: 2.0.0 (2025-12-08) - Compact version referencing master guide
