# TRM_TO_PYTHON.md - TRM to Python Conversion Guide

**Methodology for converting IBM Maximo TRM (Transaction Rules Manager) rules to Python automation scripts.**

---

## Overview

TRM rules are XML-based business rules that fire on specific Maximo object events. Python automation scripts replace TRM rules with more powerful, maintainable code using launch points.

---

## TRM Event → Launch Point Mapping

| TRM Event | Python Launch Point | Event |
|-----------|-------------------|-------|
| `onInit` | OBJECT | `init` |
| `onValidate` | ATTRIBUTE | `validate` |
| `onSave` | OBJECT | `save.before` |
| `onAfterSave` | OBJECT | `save.after` |
| `onAfterCommit` | OBJECT | `save.aftercommit` |
| `onDelete` | OBJECT | `delete.before` |
| `onChange` (field) | ATTRIBUTE | `action` |
| `onListFilter` | ATTRIBUTE | `listfilter` |

---

## TRM Condition → Python Translation

### TRM Conditions

| TRM Condition | Python Equivalent |
|--------------|------------------|
| `field == "VALUE"` | `mbo.getString("FIELD") == "VALUE"` |
| `field != null` | `not mbo.isNull("FIELD")` |
| `field == null` | `mbo.isNull("FIELD")` |
| `isNew()` | `mbo.isNew()` |
| `isChanged("F")` | `mbo.toBeChanged("F")` |
| `field > 0` | `mbo.getDouble("FIELD") > 0` |

### TRM Actions

| TRM Action | Python Equivalent |
|-----------|------------------|
| `setField("F", "V")` | `mbo.setValue("F", "V", MboConstants.NOACCESSCHECK)` |
| `throwException(msg)` | `raise MXApplicationException(...)` |
| `logMessage(msg)` | `logger.info(msg)` |
| `getRelated("REL")` | `mbo.getMboSet("REL")` |

---

## Conversion Workflow

### Step 1: Analyze the TRM Rule

From the TRM XML, identify:
- **Object**: Which Maximo object the rule applies to
- **Event**: Which TRM event triggers the rule (`onValidate`, `onSave`, etc.)
- **Conditions**: The `if` conditions in the rule
- **Actions**: What the rule does when conditions are met

### Step 2: Map to Launch Point

Use the TRM Event → Launch Point mapping table above to determine:
- Launch point type (ATTRIBUTE or OBJECT)
- Event name
- Object and field names

### Step 3: Convert Logic

**TRM XML:**
```xml
<rule name="ValidateVendorStatus" object="PO" event="onSave">
  <condition>
    <field name="STATUS" value="APPR"/>
    <field name="VENDOR" notNull="true"/>
  </condition>
  <action type="validate">
    <lookup object="COMPANIES" field="VENDOR" match="PO.VENDOR">
      <condition field="TYPE" value="VENDOR"/>
      <condition field="STATUS" value="ACTIVE"/>
      <onFail throwException="po.vendorinactive" params="VENDOR"/>
    </lookup>
  </action>
</rule>
```

**Python Equivalent:**
```python
################
# Script: Validate Vendor Status on PO Approval
# Object/Field: PO
# Event: save.before
# Author: SDK Conversion Tool
# Naming: po.obj.save.before.py
# Purpose: Validates vendor is active when PO is approved
# Converted from: TRM Rule - ValidateVendorStatus
################

from psdi.util.logging import MXLoggerFactory
from psdi.util import MXApplicationException
from psdi.mbo import MboConstants

logger = MXLoggerFactory.getLogger("maximo.script.po.obj.save")

try:
    status = mbo.getString("STATUS")
    vendor = mbo.getString("VENDOR")

    # Map: TRM condition - STATUS == "APPR" AND VENDOR != null
    if status == "APPR" and vendor:

        company_set = mbo.getMboSet("POVENDOR")
        try:
            company = company_set.getMbo(0)

            # Map: TRM lookup condition - TYPE == "VENDOR" AND STATUS == "ACTIVE"
            if company is None:
                raise MXApplicationException("po", "vendorinactive",
                    [vendor], None)

            vendor_status = company.getString("STATUS")
            if vendor_status != "ACTIVE":
                raise MXApplicationException("po", "vendorinactive",
                    [vendor], None)

        finally:
            company_set.close()

except MXApplicationException:
    raise
except Exception as e:
    logger.error("Error in po.obj.save: " + str(e))
    raise

scriptConfig = {
    "autoscript": "PO.OBJ.SAVE.BEFORE",
    "description": "Validate vendor is active on PO approval",
    "version": "1.0.0",
    "active": True,
    "scriptLaunchPoints": [{
        "launchPointName": "PO.OBJ.SAVE.BEFORE",
        "launchPointType": "OBJECT",
        "objectName": "PO",
        "description": "PO save validation - vendor status"
    }]
}
```

---

## TRM JavaScript/SCL → Python

TRM rules sometimes contain JavaScript or SCL (Script Control Language) logic:

### JavaScript

```javascript
// TRM JavaScript
var vendor = mbo.getString("VENDOR");
if (vendor == null || vendor == "") {
    throw new MXApplicationException("po", "vendorrequired", null, null);
}
```

```python
# Python equivalent
vendor = mbo.getString("VENDOR")
if not vendor:
    raise MXApplicationException("po", "vendorrequired", None, None)
```

### String Operations

```javascript
// TRM JavaScript
var status = mbo.getString("STATUS").toUpperCase();
var trimmed = mbo.getString("VENDOR").trim();

// Python
status = mbo.getString("STATUS").upper()
trimmed = mbo.getString("VENDOR").strip()
```

### Conditional Logic

```javascript
// TRM JavaScript
if (condition1 && condition2) { ... }
if (condition1 || condition2) { ... }
if (!condition) { ... }

// Python
if condition1 and condition2: ...
if condition1 or condition2: ...
if not condition: ...
```

---

## Complete Example: onInit Rule

**TRM rule (initializes defaults on new WO):**
```xml
<rule name="InitWorkOrder" object="WORKORDER" event="onInit">
  <condition><isNew/></condition>
  <action>
    <setField name="WOPRIORITY" value="3"/>
    <setField name="WORKTYPE" value="PM"/>
  </action>
</rule>
```

**Python:**
```python
################
# Script: Initialize Work Order Defaults
# Object/Field: WORKORDER
# Event: init
# Naming: workorder.obj.init.py
# Converted from: TRM Rule - InitWorkOrder
################

from psdi.util.logging import MXLoggerFactory
from psdi.mbo import MboConstants

logger = MXLoggerFactory.getLogger("maximo.script.workorder.obj.init")

try:
    if mbo.isNew():
        mbo.setValue("WOPRIORITY", 3, MboConstants.NOACCESSCHECK)
        mbo.setValue("WORKTYPE", "PM", MboConstants.NOACCESSCHECK)
        logger.debug("Work order defaults initialized")

except Exception as e:
    logger.error("Error in workorder.obj.init: " + str(e))
    raise

scriptConfig = {
    "autoscript": "WORKORDER.OBJ.INIT",
    "description": "Initialize work order default values",
    "version": "1.0.0",
    "active": True,
    "scriptLaunchPoints": [{
        "launchPointName": "WORKORDER.OBJ.INIT",
        "launchPointType": "OBJECT",
        "objectName": "WORKORDER",
        "description": "Initialize WO defaults"
    }]
}
```

---

## Conversion Checklist

- [ ] Identified source TRM rule name and XML location
- [ ] Mapped TRM event to correct Python launch point and event
- [ ] Converted all TRM conditions to Python `if` statements
- [ ] Converted all TRM `setField` actions to `mbo.setValue()`
- [ ] Converted all TRM `throwException` to `raise MXApplicationException`
- [ ] Added `try/finally` for all MboSet closures
- [ ] Added standard header with original TRM rule reference
- [ ] Verified business logic is preserved — tested edge cases
- [ ] Added `scriptConfig` metadata block
- [ ] Applied correct naming convention

---

## Common Pitfalls

| TRM Behavior | Python Gotcha |
|-------------|---------------|
| TRM fires on every event automatically | Python needs explicit launch point per event |
| TRM null check: `field == null` | Python: `mbo.isNull("FIELD")` not `== None` |
| TRM `setField` bypasses security | Python needs `MboConstants.NOACCESSCHECK` flag |
| TRM catches display errors | Python must explicitly `raise MXApplicationException` |
| Multiple TRM rules on same event | Combine into one Python script or use separate LPs |

---

**Last Updated**: March 20, 2026
**See Also**: `JAVA_TO_PYTHON.md`, `SCRIPT_PATTERNS.md`, `LAUNCH_POINTS.md`
**Related Skill**: `/convert-trm-to-script`
