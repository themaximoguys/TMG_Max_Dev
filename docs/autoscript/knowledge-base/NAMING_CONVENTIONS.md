# Maximo Automation Script Naming Conventions

## Overview

This document defines the standard naming conventions for Maximo automation scripts. Consistent naming makes scripts easier to find, understand, and maintain.

**Based on IBM Maximo Automation Script best practices. These conventions are generic and can be used across any Maximo project.**

---

## General Naming Rules

### 1. Use Lowercase with Dots
- ✅ **CORRECT**: `workorder.obj.save.before.py`
- ❌ **WRONG**: `WorkOrder.Obj.Save.Before.py` or `workorder_obj_save_before.py`

### 2. Use Descriptive Names
- ✅ **CORRECT**: `workorder.fld.status.validate.py`
- ❌ **WRONG**: `wo.fld.s.validate.py` (too abbreviated)

### 3. Use Dots as Separators
- Use dots (`.`) to separate components: `objectname.launchpoint.event.py`
- No spaces or underscores in the main name structure

### 4. File Extension
- Always use `.py` extension for Python scripts
- Always use `.js` extension for JavaScript scripts

---

## Naming Convention Structure

### Standard Format

```
[objectname].[launchpointtype].[event].[optionaldescription].py
```

### Components

1. **Object Name** (lowercase, no spaces)
   - The Maximo object name (e.g., `workorder`, `asset`, `po`, `inventory`)
   - Use abbreviations only if widely understood (e.g., `wo` for workorder, `po` for purchase order)

2. **Launch Point Type** (abbreviated)
   - `obj` - Object Launch Point
   - `fld` - Attribute Launch Point (field)
   - `action` - Action Launch Point
   - `cron` - Cron Task Script
   - `util` - Utility/Helper Script

3. **Event** (specific event name)
   - For Object: `save`, `init`, `new`, `add`, `delete`, `validate`
   - For Attribute: `validate`, `action`, `init`, `list`, `modify`
   - For Action: action name (e.g., `duplicate`, `approve`)

4. **Optional Description** (additional context)
   - `before`, `after`, `commit` - for save events
   - Field name - for attribute launch points
   - Additional context - for clarification

---

## Object Launch Point Naming

### Format
```
[objectname].obj.[event].[optional].py
```

### Events

#### Save Events
- **Before Save**: `[objectname].obj.save.before.py`
  - Example: `workorder.obj.save.before.py`
  - Example: `crew.obj.save.before.py`
  - Example: `po.obj.save.before.py`

- **After Save**: `[objectname].obj.save.after.py`
  - Example: `po.obj.save.after.py`
  - Example: `matusetrans.obj.save.after.py`

- **After Commit**: `[objectname].obj.save.aftercommit.py`
  - Example: `workorder.obj.save.aftercommit.py`

- **Save Only** (no before/after): `[objectname].obj.save.py`
  - Example: `assetavail.obj.save.py`
  - Example: `obsmaterial.obj.save.py`

#### Initialize Events
- **Object Init**: `[objectname].obj.init.py`
  - Example: `inventory.obj.init.py`
  - Example: `item.obj.init.py`

- **Initialize Value**: `[objectname].obj.init.value.py`
  - Example: `assetavaildlg.obj.init.py`

#### New Events
- **New MBO**: `[objectname].new.py`
  - Example: `obsmaterial.new.py`
  - Example: `invuseline.new.py`

- **Add Before**: `[objectname].obj.add.before.py`
  - Example: `plustclaim.obj.add.before.py`

#### Validate Events
- **Object Validate**: `[objectname].obj.validate.py`
  - Example: `po.object.validate.py`
  - Example: `plustclaim.object.validate.py`

#### Other Events
- **Cron (Object-based)**: `[objectname].obj.cron.py`
  - Example: `inventory.obj.cron.py`

### Examples

```python
# Before Save
workorder.obj.save.before.py
crew.obj.save.before.py
po.obj.save.before.py

# After Save
po.obj.save.after.py
matusetrans.obj.save.after.py

# Save (generic)
assetavail.obj.save.py
obsmaterial.obj.save.py

# Initialize
inventory.obj.init.py
item.obj.init.py

# New
obsmaterial.new.py
invuseline.new.py

# Validate
po.object.validate.py
plustclaim.object.validate.py
```

---

## Attribute Launch Point Naming

### Format
```
[objectname].fld.[fieldname].[event].py
```

### Events

#### Validate Events
- **Validate**: `[objectname].fld.[fieldname].validate.py`
  - Example: `obsmaterial.fld.itemnum.validate.py`
  - Example: `po.fld.fcprojectid.validate.py`

- **Valid** (shorter form): `[objectname].fld.[fieldname].valid.py`
  - Example: `obsmaterial.fld.quantity.valid.py`
  - Example: `caravail.fld.substatus.valid.py`

#### Action Events
- **Action**: `[objectname].fld.[fieldname].action.py`
  - Example: `obsmaterial.fld.storeroom.action.py`
  - Example: `cmpart.fld.plustfailure.action.py`

#### Initialize Events
- **Init**: `[objectname].fld.[fieldname].init.py`
  - Example: `inventory.fld.binnum.init.py`
  - Example: `invbalances.fld.binnum.init.py`

- **Init Value**: `[objectname].fld.[fieldname].initvalue.py`
  - Example: `cmcomponent.fld.dept.initvalue.py`

#### List Events
- **List**: `[objectname].fld.[fieldname].list.py`
  - Example: `crew.fld.crew.list.py`
  - Example: `cmcomponent.fld.component.list.py`

#### Modify Events
- **Modify**: `[objectname].fld.[fieldname].modify.py`
  - Example: `po.fld.recvstore.modify.py`

### Examples

```python
# Validate
obsmaterial.fld.itemnum.validate.py
po.fld.fcprojectid.validate.py

# Valid (shorter)
obsmaterial.fld.quantity.valid.py
caravail.fld.substatus.valid.py

# Action
obsmaterial.fld.storeroom.action.py
cmpart.fld.plustfailure.action.py

# Initialize
inventory.fld.binnum.init.py
invbalances.fld.binnum.init.py

# Init Value
cmcomponent.fld.dept.initvalue.py

# List
crew.fld.crew.list.py
cmcomponent.fld.component.list.py

# Modify
po.fld.recvstore.modify.py
```

---

## Action Launch Point Naming

### Format
```
[objectname].action.[actionname].py
```

### Examples

```python
# Object-specific actions
workorder.action.duplicate.py
workorder.action.approve.py

# OS Actions (Object Structure)
osaction.mxapiinspresult.createwo.py
osaction.sol_pm_genwork.py
osaction.stautoscript.addactionlaunchpoint.js
```

**Note**: Some action scripts use prefixes like `osaction.` for Object Structure actions.

---

## Cron Task Script Naming

### Format
```
cron.[description].py
```

### Examples

```python
# Component-based
cron.mne.wo.update.rfm.email.py
cron.rss.asset.update.serial.py
cron.rss.wo.100runhours.email.py

# Object-based cron
wo.leadcar.create.cron.py
```

---

## Integration Script Naming

### Format
```
[publish|osin|osout].[objectname].[event].py
```

### Examples

```python
# Publish Channel
publish.psf_recptinsp.extexit.out.py
publish.rtv_claim.userexit.out.before.py

# OS In (Object Structure In)
osin.stamassetdetail.js
osin.staminvbalance.js
osin.stampo.py

# OS Out (Object Structure Out)
osout.stamassetdetail.js
```

---

## Utility/Helper Script Naming

### Format
```
[util|helper].[description].py
```

### Examples

```python
# Utility scripts
util_commtemplate.py
calcassetavail.assetavail.py

# Helper scripts (if needed)
helper.dateformat.py
helper.emailtemplate.py
```

---

## Special Cases

### 1. Legacy Scripts
Some existing scripts may not follow the convention. Document these exceptions:

```python
# Legacy naming (keep for backward compatibility)
duplicateactlog.py  # Action script, but doesn't follow action naming
actlgfromwo.py  # Action script
```

### 2. Scripts with Multiple Purposes
For scripts that handle multiple related functions:

```python
# Good - descriptive
workorder.fld.status.validate.required.py
inventory.fld.bin.readonly.py

# Bad - too generic
workorder.fld.status.py
```

### 3. Compound Actions
For scripts that perform multiple related actions:

```python
# Good - descriptive
workorder.fld.assetinsrmvposition.list.py
workorder.fld.installassetnum.list.py

# Bad - unclear
workorder.fld.asset.list.py
```

---

## Naming Patterns by Launch Point Type

### Object Launch Point Patterns

| Launch Point Type | Pattern | Example |
|------------------|---------|---------|
| Before Save | `[object].obj.save.before.py` | `workorder.obj.save.before.py` |
| After Save | `[object].obj.save.after.py` | `po.obj.save.after.py` |
| After Commit | `[object].obj.save.aftercommit.py` | `workorder.obj.save.aftercommit.py` |
| Save (generic) | `[object].obj.save.py` | `assetavail.obj.save.py` |
| Initialize | `[object].obj.init.py` | `inventory.obj.init.py` |
| New | `[object].new.py` | `obsmaterial.new.py` |
| Add Before | `[object].obj.add.before.py` | `plustclaim.obj.add.before.py` |
| Validate | `[object].obj.validate.py` | `po.object.validate.py` |
| Cron | `[object].obj.cron.py` | `inventory.obj.cron.py` |

### Attribute Launch Point Patterns

| Launch Point Type | Pattern | Example |
|------------------|---------|---------|
| Validate | `[object].fld.[field].validate.py` | `obsmaterial.fld.itemnum.validate.py` |
| Valid (short) | `[object].fld.[field].valid.py` | `obsmaterial.fld.quantity.valid.py` |
| Action | `[object].fld.[field].action.py` | `obsmaterial.fld.storeroom.action.py` |
| Initialize | `[object].fld.[field].init.py` | `inventory.fld.binnum.init.py` |
| Init Value | `[object].fld.[field].initvalue.py` | `cmcomponent.fld.dept.initvalue.py` |
| List | `[object].fld.[field].list.py` | `crew.fld.crew.list.py` |
| Modify | `[object].fld.[field].modify.py` | `po.fld.recvstore.modify.py` |
| Readonly | `[object].fld.[field].readonly.py` | `inventory.fld.bin.readonly.py` |

### Action Launch Point Patterns

| Launch Point Type | Pattern | Example |
|------------------|---------|---------|
| Object Action | `[object].action.[actionname].py` | `workorder.action.duplicate.py` |
| OS Action | `osaction.[actionname].py` | `osaction.sol_pm_genwork.py` |

### Cron Task Patterns

| Launch Point Type | Pattern | Example |
|------------------|---------|---------|
| Cron Task | `cron.[description].py` | `cron.rss.asset.update.serial.py` |
| Object Cron | `[object].obj.cron.py` | `inventory.obj.cron.py` |

---

## Best Practices

### 1. Be Specific and Descriptive

**✅ GOOD**:
```python
workorder.fld.status.validate.required.py
inventory.fld.binnum.init.py
po.obj.save.before.py
```

**❌ BAD**:
```python
wo.fld.s.validate.py  # Too abbreviated
inv.fld.init.py  # Unclear which field
po.save.py  # Missing launch point type
```

### 2. Use Consistent Abbreviations

**Common Abbreviations**:
- `wo` - Work Order (acceptable if widely used)
- `po` - Purchase Order (acceptable if widely used)
- `obj` - Object Launch Point
- `fld` - Field/Attribute Launch Point
- `fld` - Field (not `field`)

### 3. Include Field Name in Attribute Launch Points

**✅ GOOD**:
```python
workorder.fld.status.validate.py
inventory.fld.binnum.init.py
```

**❌ BAD**:
```python
workorder.fld.validate.py  # Missing field name
inventory.fld.init.py  # Missing field name
```

### 4. Use Descriptive Event Names

**✅ GOOD**:
```python
workorder.obj.save.before.py
workorder.obj.save.after.py
workorder.obj.save.aftercommit.py
```

**❌ BAD**:
```python
workorder.obj.save1.py
workorder.obj.save2.py
```

### 5. Avoid Special Characters

**✅ GOOD**:
```python
workorder.fld.status.validate.py
inventory.fld.binnum.init.py
```

**❌ BAD**:
```python
workorder.fld.status-validate.py  # No hyphens
workorder.fld.status_validate.py  # No underscores (except in special cases)
workorder fld status validate.py  # No spaces
```

### 6. Use Lowercase Throughout

**✅ GOOD**:
```python
workorder.obj.save.before.py
inventory.fld.binnum.init.py
```

**❌ BAD**:
```python
WorkOrder.Obj.Save.Before.py  # No uppercase
workOrder.obj.save.before.py  # Mixed case
```

---

## Common Naming Patterns Summary

### Most Common Patterns

1. **Object Save Before**: `[object].obj.save.before.py`
2. **Object Save After**: `[object].obj.save.after.py`
3. **Object Init**: `[object].obj.init.py`
4. **Object New**: `[object].new.py`
5. **Field Validate**: `[object].fld.[field].validate.py`
6. **Field Action**: `[object].fld.[field].action.py`
7. **Field Init**: `[object].fld.[field].init.py`
8. **Field List**: `[object].fld.[field].list.py`

### Quick Reference Table

| What You Want | Naming Pattern | Example |
|---------------|----------------|---------|
| Validate before saving an object | `[object].obj.save.before.py` | `workorder.obj.save.before.py` |
| Process after saving an object | `[object].obj.save.after.py` | `po.obj.save.after.py` |
| Initialize object values | `[object].obj.init.py` | `inventory.obj.init.py` |
| Handle new MBO creation | `[object].new.py` | `obsmaterial.new.py` |
| Validate a field value | `[object].fld.[field].validate.py` | `workorder.fld.status.validate.py` |
| Run action when field changes | `[object].fld.[field].action.py` | `inventory.fld.binnum.action.py` |
| Initialize field value | `[object].fld.[field].init.py` | `inventory.fld.binnum.init.py` |
| Populate list values | `[object].fld.[field].list.py` | `crew.fld.crew.list.py` |
| Create custom action | `[object].action.[actionname].py` | `workorder.action.duplicate.py` |
| Schedule cron task | `cron.[description].py` | `cron.rss.asset.update.serial.py` |

---

## Migration Guide

### Converting Existing Scripts

If you have scripts that don't follow the convention:

1. **Document the current name** in the script header
2. **Create a new script** with the standard name
3. **Copy functionality** to the new script
4. **Deactivate the old script**
5. **Test thoroughly** before removing the old script

### Example Migration

**Old Name**: `duplicateactlog.py`
**New Name**: `workorder.action.duplicateactlog.py`

**Steps**:
1. Document in script header: `# Legacy: duplicateactlog.py`
2. Create new script with standard name
3. Update launch point configuration
4. Test
5. Deactivate old script

---

## Quick Reference

### Object Launch Points
- `[object].obj.save.before.py` - Before save
- `[object].obj.save.after.py` - After save
- `[object].obj.save.aftercommit.py` - After commit
- `[object].obj.save.py` - Save (generic)
- `[object].obj.init.py` - Initialize
- `[object].new.py` - New MBO
- `[object].obj.add.before.py` - Add before
- `[object].obj.validate.py` - Validate

### Attribute Launch Points
- `[object].fld.[field].validate.py` - Validate
- `[object].fld.[field].valid.py` - Valid (short)
- `[object].fld.[field].action.py` - Action
- `[object].fld.[field].init.py` - Initialize
- `[object].fld.[field].initvalue.py` - Init value
- `[object].fld.[field].list.py` - List
- `[object].fld.[field].modify.py` - Modify

### Action Launch Points
- `[object].action.[actionname].py` - Object action
- `osaction.[actionname].py` - OS action

### Cron Tasks
- `cron.[description].py` - Cron task
- `[object].obj.cron.py` - Object cron

---

## Examples by Category

### Work Order Scripts
```python
workorder.obj.save.before.py
workorder.obj.save.after.py
workorder.obj.init.py
workorder.fld.status.validate.py
workorder.fld.assetnum.action.py
workorder.action.duplicate.py
```

### Purchase Order Scripts
```python
po.obj.save.before.py
po.obj.save.after.py
po.obj.init.py
po.fld.fcprojectid.validate.py
po.fld.recvstore.modify.py
```

### Inventory Scripts
```python
inventory.obj.init.py
inventory.obj.cron.py
inventory.fld.binnum.init.py
inventory.fld.bin.readonly.py
```

### Asset Scripts
```python
asset.obj.save.before.py
asset.obj.init.py
asset.fld.status.validate.py
asset.fld.location.action.py
```

---

## Notes

- These conventions are based on IBM Maximo Automation Script best practices
- Some legacy scripts may not follow these conventions
- When creating new scripts, always follow these conventions
- When updating existing scripts, consider migrating to the standard naming convention
- Document any exceptions in the script header
- These conventions are generic and can be used across any Maximo project

---

---

## Quick Reference Section

For quick lookup, see the patterns below:

### Object Launch Point Quick Reference

| Event | Pattern | Example |
|-------|---------|---------|
| Before Save | `[object].obj.save.before.py` | `workorder.obj.save.before.py` |
| After Save | `[object].obj.save.after.py` | `po.obj.save.after.py` |
| After Commit | `[object].obj.save.aftercommit.py` | `workorder.obj.save.aftercommit.py` |
| Save (Generic) | `[object].obj.save.py` | `assetavail.obj.save.py` |
| Initialize | `[object].obj.init.py` | `inventory.obj.init.py` |
| New | `[object].new.py` | `obsmaterial.new.py` |
| Add Before | `[object].obj.add.before.py` | `plustclaim.obj.add.before.py` |
| Validate | `[object].obj.validate.py` | `po.object.validate.py` |
| Cron | `[object].obj.cron.py` | `inventory.obj.cron.py` |

### Attribute Launch Point Quick Reference

| Event | Pattern | Example |
|-------|---------|---------|
| Validate | `[object].fld.[field].validate.py` | `obsmaterial.fld.itemnum.validate.py` |
| Valid (Short) | `[object].fld.[field].valid.py` | `obsmaterial.fld.quantity.valid.py` |
| Action | `[object].fld.[field].action.py` | `obsmaterial.fld.storeroom.action.py` |
| Initialize | `[object].fld.[field].init.py` | `inventory.fld.binnum.init.py` |
| Init Value | `[object].fld.[field].initvalue.py` | `cmcomponent.fld.dept.initvalue.py` |
| List | `[object].fld.[field].list.py` | `crew.fld.crew.list.py` |
| Modify | `[object].fld.[field].modify.py` | `po.fld.recvstore.modify.py` |
| Readonly | `[object].fld.[field].readonly.py` | `inventory.fld.bin.readonly.py` |

### Action Launch Point Quick Reference

| Type | Pattern | Example |
|------|---------|---------|
| Object Action | `[object].action.[actionname].py` | `workorder.action.duplicate.py` |
| OS Action | `osaction.[actionname].py` | `osaction.sol_pm_genwork.py` |

### Cron Task Quick Reference

| Type | Pattern | Example |
|------|---------|---------|
| Standard Cron | `cron.[description].py` | `cron.rss.asset.update.serial.py` |
| Object Cron | `[object].obj.cron.py` | `inventory.obj.cron.py` |

---

**Last Updated**: Based on IBM Maximo Automation Script best practices

**Status**: Production Ready - Generic and reusable across any Maximo project

