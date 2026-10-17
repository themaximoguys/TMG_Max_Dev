# SCRIPT_PATTERNS.md - Common Automation Script Patterns

**Reference guide for common patterns used across 460+ production Maximo automation scripts.**

---

## Standard Script Structure

Every script follows this structure:

```python
################
# Script: [Descriptive name]
# Object/Field: [OBJECT.FIELD or OBJECT]
# Event: [EVENT_TYPE]
# Author: SDK Conversion Tool
# Naming: [filename.py]
# Purpose: [Business logic description]
################

# --- Imports ---
from psdi.util.logging import MXLoggerFactory
from psdi.util import MXApplicationException
from psdi.mbo import MboConstants, SqlFormat

# --- Logger Setup ---
logger = MXLoggerFactory.getLogger("maximo.script.[scriptname]")

# --- Main Logic ---
# [script body]

# --- Script Config ---
scriptConfig = {
    "autoscript": "OBJECT.EVENT.TYPE",
    "description": "Human-readable description",
    "version": "1.0.0",
    "active": True,
    "scriptLaunchPoints": [{ ... }]
}
```

---

## Pattern 1: Field Validation (Most Common)

**Use case:** Validate a field value before saving.

```python
################
# Script: Validate PO Vendor
# Object/Field: PO.VENDOR
# Event: validate
# Naming: po.fld.vendor.validate.py
# Purpose: Ensure vendor is active and approved
################

from psdi.util.logging import MXLoggerFactory
from psdi.util import MXApplicationException

logger = MXLoggerFactory.getLogger("maximo.script.po.vendor.validate")

try:
    vendor = mbo.getString("VENDOR")
    if vendor:
        vendor_set = mbo.getMboSet("POVENDOR")
        try:
            vendor_mbo = vendor_set.getMbo(0)
            if vendor_mbo is None:
                raise MXApplicationException("po", "invalidvendor",
                    [vendor], None)
            status = vendor_mbo.getString("STATUS")
            if status != "APPR":
                raise MXApplicationException("po", "vendornotapproved",
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
    "description": "Validate PO vendor is active and approved",
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

## Pattern 2: Object Save Validation

**Use case:** Validate multiple fields before the record saves.

```python
################
# Script: Validate Invoice Before Save
# Object/Field: INVOICE
# Event: save.before
# Naming: invoice.obj.save.before.py
# Purpose: Validate required fields before save
################

from psdi.util.logging import MXLoggerFactory
from psdi.util import MXApplicationException
from psdi.mbo import MboConstants

logger = MXLoggerFactory.getLogger("maximo.script.invoice.obj.save")

try:
    # Only validate on ADD or CHANGE
    if mbo.isNew() or mbo.toBeChanged():

        vendor = mbo.getString("VENDOR")
        invoice_date = mbo.getDate("INVOICEDATE")
        total_cost = mbo.getDouble("TOTALCOST")

        if not vendor:
            raise MXApplicationException("invoice", "vendorrequired",
                None, None)

        if invoice_date is None:
            raise MXApplicationException("invoice", "daterequired",
                None, None)

        if total_cost <= 0:
            raise MXApplicationException("invoice", "invalidtotal",
                [str(total_cost)], None)

        logger.debug("Invoice validation passed for: " +
            mbo.getString("INVOICENUM"))

except MXApplicationException:
    raise
except Exception as e:
    logger.error("Error in invoice.obj.save: " + str(e))
    raise

scriptConfig = {
    "autoscript": "INVOICE.OBJ.SAVE.BEFORE",
    "description": "Validate invoice before save",
    "version": "1.0.0",
    "active": True,
    "scriptLaunchPoints": [{
        "launchPointName": "INVOICE.OBJ.SAVE.BEFORE",
        "launchPointType": "OBJECT",
        "objectName": "INVOICE",
        "description": "Validate invoice fields on save"
    }]
}
```

---

## Pattern 3: MboSet Iteration

**Use case:** Iterate over related child records.

```python
# Standard MboSet iteration — ALWAYS use try/finally to close
line_set = mbo.getMboSet("INVOICELINE")
try:
    i = 0
    while i < line_set.count():
        line = line_set.getMbo(i)
        line_cost = line.getDouble("LINECOST")
        # Process line...
        i += 1
finally:
    line_set.close()  # CRITICAL: Always close to prevent memory leaks
```

---

## Pattern 4: Filtered MboSet Query

**Use case:** Query related records with a filter condition.

```python
from psdi.mbo import SqlFormat

# Get open PO lines for a vendor
po_set = mbo.getMboSet("$OPENPO",
    "PO",
    SqlFormat.format("vendor = :1 and status = :2", [vendor, "APPR"]))
try:
    count = po_set.count()
    logger.debug("Found " + str(count) + " approved POs for vendor: " + vendor)
finally:
    po_set.close()
```

---

## Pattern 5: Field Initialization (init event)

**Use case:** Set default field values when a record is created.

```python
################
# Script: Initialize Work Order Defaults
# Object/Field: WORKORDER
# Event: init
# Naming: workorder.obj.init.py
################

from psdi.mbo import MboConstants

try:
    if mbo.isNew():
        # Set default priority
        if mbo.isNull("WOPRIORITY"):
            mbo.setValue("WOPRIORITY", 3, MboConstants.NOACCESSCHECK)

        # Set default work type
        if mbo.isNull("WORKTYPE"):
            mbo.setValue("WORKTYPE", "PM", MboConstants.NOACCESSCHECK)

        logger.debug("Work order defaults initialized")

except Exception as e:
    logger.error("Error in workorder.obj.init: " + str(e))
    raise
```

---

## Pattern 6: Field Action (Cascade/Auto-populate)

**Use case:** Auto-populate other fields when a field changes.

```python
################
# Script: Auto-populate Ship Address from Vendor
# Object/Field: PO.VENDOR
# Event: action
# Naming: po.fld.vendor.action.py
################

try:
    vendor = mbo.getString("VENDOR")
    if vendor:
        vendor_set = mbo.getMboSet("POVENDOR")
        try:
            vendor_mbo = vendor_set.getMbo(0)
            if vendor_mbo is not None:
                address = vendor_mbo.getString("ADDRESS1")
                city    = vendor_mbo.getString("CITY")
                state   = vendor_mbo.getString("STATEPROVINCE")

                mbo.setValue("SHIPADDRESS", address, MboConstants.NOACCESSCHECK)
                mbo.setValue("SHIPCITY",    city,    MboConstants.NOACCESSCHECK)
                mbo.setValue("SHIPSTATE",   state,   MboConstants.NOACCESSCHECK)
        finally:
            vendor_set.close()

except Exception as e:
    logger.error("Error in po.vendor.action: " + str(e))
    raise
```

---

## Pattern 7: Status-Conditional Logic

**Use case:** Apply different logic based on current record status.

```python
try:
    status = mbo.getString("STATUS")

    if status == "WAPPR":
        # Waiting for approval — validate approver
        approver = mbo.getString("SUPERVISOR")
        if not approver:
            raise MXApplicationException("wo", "approverrequired", None, None)

    elif status == "APPR":
        # Approved — set approved date
        from psdi.server import MXServer
        now = MXServer.getMXServer().getDate()
        mbo.setValue("APPROVEDDATE", now, MboConstants.NOACCESSCHECK)

    elif status == "COMP":
        # Complete — require actual dates
        actual_finish = mbo.getDate("ACTFINISH")
        if actual_finish is None:
            raise MXApplicationException("wo", "actfinishrequired", None, None)

except MXApplicationException:
    raise
except Exception as e:
    logger.error("Error in status logic: " + str(e))
    raise
```

---

## Pattern 8: Cron Task Structure

**Use case:** Scheduled background processing.

```python
################
# Script: Generate PM Work Orders
# Object/Field: CRONTASK
# Event: action
# Naming: tmg_pmwogen.cron.action.py
################

from psdi.util.logging import MXLoggerFactory
from psdi.server import MXServer
from psdi.mbo import SqlFormat

logger = MXLoggerFactory.getLogger("maximo.script.tmg_pmwogen.cron")

try:
    logger.info("PM Work Order Generation cron task starting")
    mx_server = MXServer.getMXServer()
    user_info = mbo.getUserInfo()

    # Get overdue PMs
    pm_set = mx_server.getMboSet("PM", user_info,
        SqlFormat.format("nextdate <= :1 and status = :2",
        [mx_server.getDate(), "ACTIVE"]))

    try:
        count = 0
        i = 0
        while i < pm_set.count():
            pm = pm_set.getMbo(i)
            # Generate work order from PM
            wo_set = pm.getMboSet("GENERATEWO")
            try:
                wo_set.add()
                wo_set.save()
                count += 1
            finally:
                wo_set.close()
            i += 1

        logger.info("Generated " + str(count) + " work orders from PMs")

    finally:
        pm_set.close()

except Exception as e:
    logger.error("Error in PM generation cron: " + str(e))
    raise

scriptConfig = {
    "autoscript": "TMG_PMWOGEN.CRON.ACTION",
    "description": "Generate work orders from overdue PMs",
    "version": "1.0.0",
    "active": True,
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PMWOGEN.CRON.ACTION",
        "launchPointType": "CRONTASK",
        "objectName": "CRONTASKINSTANCE",
        "description": "PM work order generation"
    }]
}
```

---

## Pattern 9: Server-Side Lookups

**Use case:** Access server resources and system sets.

```python
from psdi.server import MXServer

mx_server = MXServer.getMXServer()
user_info  = mbo.getUserInfo()

# Get system date
today = mx_server.getDate()

# Access a system MboSet
company_set = mx_server.getMboSet("COMPANIES", user_info,
    SqlFormat.format("company = :1", [company_code]))
try:
    company = company_set.getMbo(0)
    if company is None:
        raise MXApplicationException("mbo", "companynotfound",
            [company_code], None)
finally:
    company_set.close()
```

---

## Pattern 10: Null / Empty Checks

**Use case:** Safely check field values.

```python
# Check if field is null
if mbo.isNull("VENDOR"):
    raise MXApplicationException("po", "vendorrequired", None, None)

# Check if string field is empty
vendor = mbo.getString("VENDOR")
if not vendor or vendor.strip() == "":
    raise MXApplicationException("po", "vendorrequired", None, None)

# Check if date is null
invoice_date = mbo.getDate("INVOICEDATE")
if invoice_date is None:
    raise MXApplicationException("invoice", "daterequired", None, None)

# Check if numeric is zero or null
total = mbo.getDouble("TOTALCOST")
if total is None or total <= 0:
    raise MXApplicationException("invoice", "invalidamount", None, None)
```

---

## Common Imports Reference

```python
# Logging
from psdi.util.logging import MXLoggerFactory

# Exceptions
from psdi.util import MXApplicationException

# MBO constants and SQL
from psdi.mbo import MboConstants, SqlFormat

# Server access
from psdi.server import MXServer

# Date utilities
from psdi.util import MXFormat
```

---

## Anti-Patterns to Avoid

```python
# ❌ NEVER forget to close MboSets
related = mbo.getMboSet("RELATED")
# ... no close() = memory leak

# ✅ ALWAYS use try/finally
related = mbo.getMboSet("RELATED")
try:
    # process
finally:
    related.close()

# ❌ NEVER swallow exceptions silently
try:
    # logic
except:
    pass  # Hides bugs!

# ✅ ALWAYS log and re-raise or handle properly
try:
    # logic
except MXApplicationException:
    raise
except Exception as e:
    logger.error("Error: " + str(e))
    raise
```

---

**Last Updated**: March 20, 2026
**See Also**: `NAMING_CONVENTIONS.md`, `LAUNCH_POINTS.md`, `ERROR_HANDLING.md`
