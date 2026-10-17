# JAVA_TO_PYTHON.md - Java to Python Conversion Guide

**Methodology and patterns for converting IBM Maximo Java classes to Python automation scripts.**

---

## Overview

Java MBO classes in Maximo handle business logic through inheritance from `MboSet`, `Mbo`, `FldVar`, etc. Python automation scripts access the same MBO objects through Jython bindings, but with a simpler, script-based structure.

---

## Key Differences

| Concept | Java Class | Python Script |
|---------|-----------|---------------|
| Structure | Class with methods | Flat script body |
| MBO access | `this` (the Mbo itself) | `mbo` (implicit variable) |
| Event binding | Method override (`validate()`) | Launch point configuration |
| Error handling | `throw new MXApplicationException` | `raise MXApplicationException` |
| Logging | `MXLogger log = ...` | `logger = MXLoggerFactory...` |
| String access | `getString("FIELD")` | `mbo.getString("FIELD")` |

---

## Type Conversion Table

| Java Type | Python Equivalent | Getter | Setter |
|-----------|------------------|--------|--------|
| `String` | `str` | `mbo.getString("F")` | `mbo.setValue("F", value)` |
| `int` / `Integer` | `int` | `mbo.getInt("F")` | `mbo.setValue("F", value)` |
| `double` / `Double` | `float` | `mbo.getDouble("F")` | `mbo.setValue("F", value)` |
| `boolean` / `Boolean` | `bool` | `mbo.getBoolean("F")` | `mbo.setValue("F", value)` |
| `java.util.Date` | Date object | `mbo.getDate("F")` | `mbo.setValue("F", value)` |
| `BigDecimal` | `float` | `mbo.getDouble("F")` | `mbo.setValue("F", value)` |
| `null` | `None` | `mbo.isNull("F")` | `mbo.setValueNull("F")` |

---

## Method Translation Reference

### MBO Methods

| Java | Python |
|------|--------|
| `this.getString("F")` | `mbo.getString("F")` |
| `this.setValue("F", v)` | `mbo.setValue("F", v, MboConstants.NOACCESSCHECK)` |
| `this.isNew()` | `mbo.isNew()` |
| `this.isNull("F")` | `mbo.isNull("F")` |
| `this.toBeChanged()` | `mbo.toBeChanged()` |
| `this.getMboSet("REL")` | `mbo.getMboSet("REL")` |
| `this.getUserInfo()` | `mbo.getUserInfo()` |
| `set.getMbo(0)` | `set.getMbo(0)` |
| `set.count()` | `set.count()` |
| `set.close()` | `set.close()` |

### Server Methods

| Java | Python |
|------|--------|
| `MXServer.getMXServer()` | `MXServer.getMXServer()` *(import required)* |
| `MXServer.getMXServer().getDate()` | `mx_server.getDate()` |
| `MXServer.getMXServer().getMboSet(...)` | `mx_server.getMboSet(...)` |

### Exception Handling

| Java | Python |
|------|--------|
| `throw new MXApplicationException(b, k, p, c)` | `raise MXApplicationException(b, k, p, c)` |
| `catch (MXApplicationException e) { throw e; }` | `except MXApplicationException: raise` |
| `catch (Exception e) { ... throw e; }` | `except Exception as e: ... raise` |

---

## Conversion Workflow

### Step 1: Understand the Java Class

Identify:
- Which class it extends (`Mbo`, `MboSet`, `FldVar`, `MaxFieldValidator`)
- Which methods are overridden (`validate()`, `action()`, `init()`)
- What MBO relationships are used
- What exceptions are thrown

### Step 2: Determine the Launch Point

| Java Base Class / Method | Python Launch Point |
|--------------------------|-------------------|
| `FldVar.validate()` | ATTRIBUTE → validate |
| `FldVar.action()` | ATTRIBUTE → action |
| `FldVar.init()` | ATTRIBUTE → init |
| `Mbo.save()` | OBJECT → save.before or save.after |
| `Mbo.init()` | OBJECT → init |
| `Mbo.delete()` | OBJECT → delete.before |
| `MboSet` cron | CRONTASK → action |

### Step 3: Convert the Code

**Java:**
```java
public class POVendorValidator extends FldVar {
    public void validate() throws MXException, RemoteException {
        String vendor = getMbo().getString("VENDOR");
        if (vendor == null || vendor.isEmpty()) {
            throw new MXApplicationException("po", "vendorrequired", null, null);
        }
        MboSetRemote vendorSet = getMbo().getMboSet("POVENDOR");
        try {
            MboRemote vendorMbo = vendorSet.getMbo(0);
            if (vendorMbo == null) {
                throw new MXApplicationException("po", "invalidvendor",
                    new Object[]{vendor}, null);
            }
        } finally {
            vendorSet.close();
        }
    }
}
```

**Python:**
```python
################
# Script: Validate PO Vendor
# Object/Field: PO.VENDOR
# Event: validate
# Author: SDK Conversion Tool
# Naming: po.fld.vendor.validate.py
# Purpose: Validates vendor exists on PO
# Converted from: POVendorValidator.java
################

from psdi.util.logging import MXLoggerFactory
from psdi.util import MXApplicationException

logger = MXLoggerFactory.getLogger("maximo.script.po.vendor.validate")

try:
    vendor = mbo.getString("VENDOR")

    if not vendor:
        raise MXApplicationException("po", "vendorrequired", None, None)

    vendor_set = mbo.getMboSet("POVENDOR")
    try:
        vendor_mbo = vendor_set.getMbo(0)
        if vendor_mbo is None:
            raise MXApplicationException("po", "invalidvendor",
                [vendor], None)
    finally:
        vendor_set.close()

except MXApplicationException:
    raise
except Exception as e:
    logger.error("Error in po.vendor.validate: " + str(e))
    raise

scriptConfig = {
    "autoscript": "PO.FLD.VENDOR.VALIDATE",
    "description": "Validate PO vendor exists",
    "version": "1.0.0",
    "active": True,
    "scriptLaunchPoints": [{
        "launchPointName": "PO.FLD.VENDOR.VALIDATE",
        "launchPointType": "ATTRIBUTE",
        "objectName": "PO",
        "attributeName": "VENDOR",
        "description": "Validate vendor on PO"
    }]
}
```

---

## Common Java Patterns → Python

### Null Check
```java
// Java
if (getString("VENDOR") == null || getString("VENDOR").isEmpty()) { }

// Python
if not mbo.getString("VENDOR"):
```

### String Comparison
```java
// Java
if ("APPR".equals(getString("STATUS"))) { }

// Python
if mbo.getString("STATUS") == "APPR":
```

### Numeric Comparison
```java
// Java
if (getDouble("TOTALCOST") < 0.0) { }

// Python
if mbo.getDouble("TOTALCOST") < 0.0:
```

### MboSet Iteration
```java
// Java
MboSetRemote lines = getMboSet("POLINE");
try {
    for (int i = 0; i < lines.count(); i++) {
        MboRemote line = lines.getMbo(i);
        // process...
    }
} finally {
    lines.close();
}

// Python
lines = mbo.getMboSet("POLINE")
try:
    i = 0
    while i < lines.count():
        line = lines.getMbo(i)
        # process...
        i += 1
finally:
    lines.close()
```

### setValue with Access Override
```java
// Java
mbo.setValue("STATUS", "APPR", MboConstants.NOACCESSCHECK);

// Python
from psdi.mbo import MboConstants
mbo.setValue("STATUS", "APPR", MboConstants.NOACCESSCHECK)
```

---

## Conversion Checklist

- [ ] Identified source Java class and which method to convert
- [ ] Determined correct launch point type and event
- [ ] Converted all `getString`/`setValue`/`getDouble` calls
- [ ] Replaced `throw new MXApplicationException` with `raise`
- [ ] Replaced `null` with `None`
- [ ] Added `try/finally` for all MboSet closures
- [ ] Added proper logger setup
- [ ] Added standard header with original Java class reference
- [ ] Added `scriptConfig` metadata block
- [ ] Applied correct naming convention

---

**Last Updated**: March 20, 2026
**See Also**: `TRM_TO_PYTHON.md`, `SCRIPT_PATTERNS.md`, `NAMING_CONVENTIONS.md`
**Related Skill**: `/convert-java-to-script`
