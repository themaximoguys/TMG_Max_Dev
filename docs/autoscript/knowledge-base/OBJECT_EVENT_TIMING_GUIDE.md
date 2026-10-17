# Maximo Object Script Event Timing Guide

**Purpose**: Quick reference for choosing correct event timing in Object Launch Points  
**Version**: 1.0.0  
**Last Updated**: 2025-12-01  
**Context**: MAS 9 Python automation script conversion

---

## Quick Reference Table

| Event | Timing Flag | When It Fires | Use Cases | Java Equivalent |
|-------|-------------|---------------|-----------|-----------------|
| **INIT** | `initializeValue: True` | After object construction | Set default field values | `init()` |
| **ADD** | `afterAdd: True` | After record added to MboSet | Initialize relationships, set flags | `add()` |
| **SAVE (Before)** | `beforeSave: True` | Before database save | Validation, field manipulation | `appValidate()` |
| **SAVE (After)** | `afterSave: True` | After DB save, before commit | Trigger related saves, business logic | `save()` |
| **SAVE (Commit)** | `afterCommit: True` | After transaction committed | Notifications, external systems | N/A |
| **DELETE** | `beforeDelete: True` | Before database deletion | Validation, dependency checks | `canDelete()` |

---

## SAVE Event Timing Details

### 1. beforeSave (Pre-Save Validation)

**When**: Before data is written to the database  
**Can Modify Data**: ✅ Yes  
**Can Prevent Save**: ✅ Yes (throw exception)  
**Transaction State**: Not yet saved  

**Use Cases**:
- ✅ Field validation (GL account completeness)
- ✅ Business rule enforcement
- ✅ Field calculations/manipulation
- ✅ Setting computed values
- ✅ Cross-field validation

**Examples**:
```python
# MR GL Account Validation (mr.obj.appvalidate.py)
scriptConfig = {
    "scriptLaunchPoints": [{
        "objectName": "MR",
        "save": True,
        "beforeSave": True  # Validate before save
    }]
}

# PM Feedback Requirement Check (feedbacklog.obj.save.py)
scriptConfig = {
    "scriptLaunchPoints": [{
        "objectName": "TMG_FEEDBKLOG",
        "save": True,
        "beforeSave": True  # Calculate requirements before save
    }]
}
```

**Java Equivalent**: `appValidate()` method

---

### 2. afterSave (Post-Save Actions)

**When**: After data written to database, before transaction commit  
**Can Modify Data**: ✅ Yes (will trigger another save)  
**Can Prevent Save**: ❌ No (already saved)  
**Transaction State**: Saved but not committed  

**Use Cases**:
- ✅ Calling save() on related objects
- ✅ Creating child/related records
- ✅ Triggering cascading business logic
- ✅ Issue logic calculations
- ✅ Status propagation

**Examples**:
```python
# WPMaterial triggering WO save (wpmaterial.obj.save.py)
scriptConfig = {
    "scriptLaunchPoints": [{
        "objectName": "WPMATERIAL",
        "save": True,
        "afterSave": True  # Call WO.save() after material saved
    }]
}

# Triggering related object updates
def custom_save():
    # This object is already saved to DB
    wo_mbo = mbo.getOwner()
    wo_mbo.save()  # Trigger parent WO save
```

**Java Equivalent**: `save()` method (after `super.save()`)

---

### 3. afterCommit (Post-Transaction)

**When**: After transaction is committed to database  
**Can Modify Data**: ⚠️ Use with caution (new transaction)  
**Can Prevent Save**: ❌ No (already committed)  
**Transaction State**: Committed  

**Use Cases**:
- ✅ Send email notifications
- ✅ Call external web services
- ✅ Update external systems
- ✅ Generate PDF reports
- ✅ Audit logging to separate tables
- ✅ Workflow triggers

**Examples**:
```python
# Send notification after WO completion
scriptConfig = {
    "scriptLaunchPoints": [{
        "objectName": "WORKORDER",
        "save": True,
        "afterCommit": True  # Send email after commit
    }]
}

# Integration with external system
def notify_external_system():
    # Safe to call external APIs here
    # Transaction is already committed
    send_to_sap(mbo.getString("WONUM"))
```

**Java Equivalent**: None (typically done via Maximo Integration Framework)

---

## ADD Event Timing

### afterAdd (Post-Add Initialization)

**When**: After record added to MboSet, before save  
**Can Modify Data**: ✅ Yes  
**Transaction State**: New record (not yet saved)  

**Use Cases**:
- ✅ Set flags on parent objects
- ✅ Initialize relationships
- ✅ Trigger recalculations
- ✅ Set derived values

**Examples**:
```python
# WPMaterial setting flag on WO (wpmaterial.obj.add.py)
scriptConfig = {
    "scriptLaunchPoints": [{
        "objectName": "WPMATERIAL",
        "add": True,
        "afterAdd": True  # Set TMG_UPDATEISLOGIC flag after add
    }]
}

def run_issue_logic_after_wo_save():
    owner = mbo.getOwner()
    if owner:
        owner.setValue("TMG_UPDATEISLOGIC", 1, MboConstants.NOACCESSCHECK)
```

**Java Equivalent**: `add()` method

---

## DELETE Event Timing

### beforeDelete (Pre-Delete Validation)

**When**: Before record deleted from database  
**Can Prevent Delete**: ✅ Yes (throw exception)  
**Transaction State**: Not yet deleted  

**Use Cases**:
- ✅ Validate deletion is allowed
- ✅ Check for dependencies
- ✅ Verify status requirements
- ✅ Audit logging

**Examples**:
```python
# MR delete validation (mr.obj.candelete.py)
scriptConfig = {
    "scriptLaunchPoints": [{
        "objectName": "MR",
        "delete": True,
        "beforeDelete": True  # Validate before deletion
    }]
}

def validate_mr_deletion():
    # Check if PRs exist
    pr_set = mbo.getMboSet("PR")
    if not pr_set.isEmpty():
        pr = pr_set.getMbo(0)
        if pr.getString("STATUS") != "CAN":
            raise MXApplicationException("Cannot delete MR with active PR")
```

**Java Equivalent**: `canDelete()` method

---

## INIT Event Timing

### initializeValue (Object Construction)

**When**: After object constructed, before data loaded  
**Can Modify Data**: ✅ Yes (set defaults)  
**Transaction State**: New or existing record  

**Use Cases**:
- ✅ Set default field values for new records
- ✅ Initialize boolean flags
- ✅ Set date defaults

**Examples**:
```python
# ClassSpec default values (classspec.obj.init.py)
scriptConfig = {
    "scriptLaunchPoints": [{
        "objectName": "CLASSSPEC",
        "initializeValue": True  # Set defaults on init
    }]
}

def initialize_classspec():
    if mbo.toBeAdded():
        mbo.setValue("USEINLOCDESC", False, 
                     MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

**Java Equivalent**: `init()` method

---

## Decision Flow Chart

```
Need to validate before save?
├─ Yes → beforeSave
└─ No ↓

Need to save related objects?
├─ Yes → afterSave
└─ No ↓

Need to notify external systems?
├─ Yes → afterCommit
└─ No ↓

Setting up new record?
├─ Yes → afterAdd or initializeValue
└─ No ↓

Validating deletion?
└─ Yes → beforeDelete
```

---

## Common Patterns by Use Case

### Pattern 1: Field Validation
```python
# Use beforeSave
{
    "save": True,
    "beforeSave": True
}
```

### Pattern 2: Cascading Saves
```python
# Use afterSave
{
    "save": True,
    "afterSave": True
}

def custom_save():
    parent = mbo.getOwner()
    parent.save()  # Trigger parent save
```

### Pattern 3: External Integration
```python
# Use afterCommit
{
    "save": True,
    "afterCommit": True
}

def send_notification():
    # Safe to call external APIs
    send_email(mbo.getString("EMAIL"))
```

### Pattern 4: Parent Object Flags
```python
# Use afterAdd
{
    "add": True,
    "afterAdd": True
}

def set_parent_flag():
    parent = mbo.getOwner()
    parent.setValue("NEEDSRECALC", True)
```

### Pattern 5: Delete Protection
```python
# Use beforeDelete
{
    "delete": True,
    "beforeDelete": True
}

def validate_can_delete():
    if has_dependencies():
        raise MXApplicationException("Cannot delete")
```

---

## Best Practices

### ✅ DO:
- Specify exact event timing for all OBJECT launch points
- Use `beforeSave` for validation that can prevent save
- Use `afterSave` when you need to trigger other object saves
- Use `afterCommit` for external system calls
- Use `beforeDelete` for deletion validation

### ❌ DON'T:
- Don't use generic `save: True` without timing flag
- Don't call external systems in `beforeSave` or `afterSave`
- Don't try to prevent save in `afterSave` (too late)
- Don't modify data in `afterCommit` without caution
- Don't perform heavy operations in `beforeSave`

---

## Conversion Quick Reference

| Java Method | Event Timing | scriptConfig |
|-------------|--------------|--------------|
| `init()` | Initialize | `initializeValue: True` |
| `add()` | After Add | `add: True, afterAdd: True` |
| `appValidate()` | Before Save | `save: True, beforeSave: True` |
| `save()` after `super.save()` | After Save | `save: True, afterSave: True` |
| `canDelete()` | Before Delete | `delete: True, beforeDelete: True` |

---

## Testing Checklist

When testing event timing:

- [ ] Verify script fires at correct point in lifecycle
- [ ] Test validation can prevent save (beforeSave)
- [ ] Test related saves complete successfully (afterSave)
- [ ] Verify external calls happen after commit (afterCommit)
- [ ] Check transaction rollback behavior
- [ ] Verify error handling works correctly
- [ ] Test with nested object hierarchies
- [ ] Validate logging shows correct execution order

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-12-01  
**Next Review**: After first production deployment
