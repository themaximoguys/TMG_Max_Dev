# LAUNCH_POINTS.md - Launch Point Types and Events

**Complete reference for all Maximo automation script launch point types and events.**

---

## Launch Point Types Overview

| Type | Trigger | Use Case |
|------|---------|---------|
| **ATTRIBUTE** | Field-level event | Validate or act on a specific field |
| **OBJECT** | Object-level event | Validate or act on the whole record |
| **CRONTASK** | Scheduled execution | Background/batch processing |
| **ACTION** | Workflow or button | Workflow actions, UI buttons |

---

## ATTRIBUTE Launch Points (Field-Level)

### Events

| Event | When It Fires | Common Use |
|-------|--------------|-----------|
| `validate` | When field loses focus after change | Field value validation |
| `action` | After validate passes | Auto-populate related fields |
| `init` | When a new record is created | Set default field values |
| `listfilter` | When a lookup list is opened | Filter lookup results |

### scriptConfig Example

```python
scriptConfig = {
    "autoscript": "PO.FLD.VENDOR.VALIDATE",
    "description": "Validate vendor on PO",
    "version": "1.0.0",
    "active": True,
    "scriptLaunchPoints": [{
        "launchPointName": "PO.FLD.VENDOR.VALIDATE",
        "launchPointType": "ATTRIBUTE",
        "objectName": "PO",
        "attributeName": "VENDOR",
        "description": "Validate PO vendor field"
    }]
}
```

### Naming Convention
```
[object].fld.[field].[event].py

Examples:
  po.fld.vendor.validate.py       ← validate event
  po.fld.vendor.action.py         ← action event
  invoice.fld.invoicedate.init.py ← init event
  company.fld.status.listfilter.py← listfilter event
```

---

## OBJECT Launch Points (Record-Level)

### Events

| Event | When It Fires | Common Use |
|-------|--------------|-----------|
| `init` | When a new record is initialized | Set defaults for new record |
| `add` | When a record is first added | Post-creation logic |
| `save.before` | Before record is saved | Validate full record |
| `save.after` | After record is saved (before commit) | Update related records |
| `save.aftercommit` | After database commit | External notifications |
| `delete.before` | Before record is deleted | Prevent invalid deletions |
| `validate` | When record is validated | Cross-field validation |

### scriptConfig Example

```python
scriptConfig = {
    "autoscript": "INVOICE.OBJ.SAVE.BEFORE",
    "description": "Validate invoice before save",
    "version": "1.0.0",
    "active": True,
    "scriptLaunchPoints": [{
        "launchPointName": "INVOICE.OBJ.SAVE.BEFORE",
        "launchPointType": "OBJECT",
        "objectName": "INVOICE",
        "description": "Invoice pre-save validation"
    }]
}
```

### Naming Convention
```
[object].obj.[event].[timing].py

Examples:
  workorder.obj.save.before.py      ← save before
  workorder.obj.save.after.py       ← save after
  workorder.obj.save.aftercommit.py ← after commit
  workorder.obj.init.py             ← init
  invoice.obj.delete.before.py      ← delete before
```

---

## CRONTASK Launch Points (Scheduled)

### Events

| Event | When It Fires | Common Use |
|-------|--------------|-----------|
| `action` | On cron schedule | Batch jobs, data cleanup, report generation |

### scriptConfig Example

```python
scriptConfig = {
    "autoscript": "TMG_PMWOGEN.CRON.ACTION",
    "description": "Generate PM work orders on schedule",
    "version": "1.0.0",
    "active": True,
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PMWOGEN.CRON.ACTION",
        "launchPointType": "CRONTASK",
        "objectName": "CRONTASKINSTANCE",
        "description": "PM work order generation cron"
    }]
}
```

### Naming Convention
```
[taskname].cron.action.py

Examples:
  tmg_pmwogen.cron.action.py         ← PM work order generation
  tmg_addcimusers.cron.action.py     ← Add CIM users
  tmg_contractalert.cron.action.py   ← Contract expiry alerts
```

---

## ACTION Launch Points (Workflow/Button)

### Events

| Event | When It Fires | Common Use |
|-------|--------------|-----------|
| `action` | When workflow or UI action is triggered | Workflow steps, custom buttons |

### scriptConfig Example

```python
scriptConfig = {
    "autoscript": "PR.ACTION.WFPOFROMPR",
    "description": "Create PO from PR workflow action",
    "version": "1.0.0",
    "active": True,
    "scriptLaunchPoints": [{
        "launchPointName": "PR.ACTION.WFPOFROMPR",
        "launchPointType": "ACTION",
        "objectName": "PR",
        "description": "Workflow action to create PO from PR"
    }]
}
```

### Naming Convention
```
[object].action.[actionname].py

Examples:
  pr.action.wfpofrompr.py           ← PO from PR workflow
  workorder.action.closetasks.py    ← Close all tasks action
```

---

## Event Timing Reference

### ATTRIBUTE Event Sequence
```
User changes field value
    ↓
init (on new record creation only)
    ↓
validate (on field change/blur)
    ↓
action (after validate passes)
    ↓
listfilter (when lookup opens)
```

### OBJECT Event Sequence
```
Record loaded/created
    ↓
init (new record)
    ↓
[user makes changes]
    ↓
validate (on record validate)
    ↓
save.before (before save)
    ↓
[database save]
    ↓
save.after (after save, before commit)
    ↓
[database commit]
    ↓
save.aftercommit (after full commit)
```

---

## Choosing the Right Launch Point

### Decision Tree

```
Is it triggered by a field change?
  ├─ YES → ATTRIBUTE
  │    ├─ Validating the field? → validate event
  │    ├─ Auto-populating other fields? → action event
  │    └─ Setting defaults on new record? → init event
  │
  └─ NO → Is it triggered by saving the record?
       ├─ YES → OBJECT
       │    ├─ Check before save? → save.before
       │    ├─ Update related records? → save.after
       │    └─ Fire external notification? → save.aftercommit
       │
       └─ NO → Is it scheduled?
            ├─ YES → CRONTASK (action event)
            └─ NO  → It's a workflow/button → ACTION (action event)
```

---

## Common Objects and Their Launch Points

| Object | Common ATTRIBUTE Events | Common OBJECT Events |
|--------|------------------------|---------------------|
| **PO** | vendor.validate, status.validate, linecost.validate | save.before, save.after |
| **WORKORDER** | wopriority.init, status.validate | init, save.before, save.aftercommit |
| **INVOICE** | vendor.validate, invoicedate.validate | save.before |
| **PR** | vendor.validate, requestedby.validate | save.before, save.after |
| **ASSET** | location.validate, status.validate | init, save.before |
| **INVENTORY** | quantity.validate, storeloc.validate | save.before |
| **COMPANY** | status.validate, type.validate | save.before |

---

## scriptConfig Required Fields

```python
scriptConfig = {
    # Required
    "autoscript": "OBJECT.LAUNCHPOINTTYPE.EVENT",  # Uppercase, unique name
    "description": "Human-readable description",    # What it does

    # Optional (defaults shown)
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",   # DEBUG, INFO, WARN, ERROR

    "scriptLaunchPoints": [{
        # Required
        "launchPointName": "UNIQUE_LP_NAME",    # Uppercase, matches autoscript
        "launchPointType": "ATTRIBUTE|OBJECT|CRONTASK|ACTION",
        "objectName": "MAXIMO_OBJECT_NAME",     # e.g., PO, WORKORDER

        # ATTRIBUTE only
        "attributeName": "FIELD_NAME",           # e.g., VENDOR, STATUS

        # Optional
        "description": "Launch point description",
        "active": True
    }]
}
```

---

**Last Updated**: March 20, 2026
**See Also**: `NAMING_CONVENTIONS.md`, `SCRIPT_PATTERNS.md`, `ERROR_HANDLING.md`
