# Maximo Automation Script Launch Point Reference Examples

This document provides comprehensive reference examples for all available launch point types in Maximo automation scripts. Each example is based on real production scripts from the codebase and demonstrates best practices.

**Purpose**: Quick reference guide for creating automation scripts with proper patterns and structure  
**Version**: 1.0.0  
**Last Updated**: Based on production scripts analysis

---

## Table of Contents

1. [OBJECT Launch Point Types - Comprehensive Reference](#object-launch-point-types---comprehensive-reference)
   - [Launch Point Types Overview](#launch-point-types-overview)
   - [initializeValue - Object Initialization](#initializevalue---object-initialization)
   - [beforeSave - Before Save](#beforesave---before-save)
   - [afterSave - After Save](#aftersave---after-save)
   - [afterCommit - After Commit](#aftercommit---after-commit)
   - [afterAdd - After Add](#afteradd---after-add)
   - [beforeDelete - Before Delete](#beforedelete---before-delete)
   - [validateApplication - Object Validation](#validateapplication---object-validation)
   - [allowObjectCreation - Allow Creation](#allowobjectcreation---allow-creation)
   - [allowObjectDeletion - Allow Deletion](#allowobjectdeletion---allow-deletion)
2. [Attribute Launch Points](#attribute-launch-points)
   - [FLD.VALIDATE - Field Validation](#fldvalidate---field-validation)
   - [FLD.ACTION - Field Action](#fldaction---field-action)
   - [FLD.INIT - Field Initialization](#fldinit---field-initialization)
   - [FLD.LIST - Field List](#fldlist---field-list)
3. [Action Launch Points](#action-launch-points)
   - [ACTION.[ACTIONNAME] - Custom Actions](#actionactionname---custom-actions)
4. [Cron Task Scripts](#cron-task-scripts)
5. [Integration Scripts](#integration-scripts)

---

## OBJECT Launch Point Types - Comprehensive Reference

This section provides comprehensive patterns for all OBJECT launch point types in Maximo automation scripts, based on the updated Java-to-Python conversion guidelines.

### Launch Point Types Overview

OBJECT launch points are triggered at different stages of an MBO's lifecycle. The following table summarizes all available OBJECT launch point event types:

| Event Type | JSON Property | When It Runs | Java Method Mapping | Common Use Cases |
|-----------|---------------|--------------|---------------------|------------------|
| **Initialize Value** | `"initializeValue": true` | When MBO is initialized (loaded) | `init()` | Set defaults, initialize fields, set readonly flags |
| **Before Save** | `"beforeSave": true` | Before MBO is saved to database | `appValidate()`, `save()` BEFORE `super.save()` | Validation, auto-populate, prevent save |
| **After Save** | `"afterSave": true` | After MBO saved (before commit) | `save()` AFTER `super.save()`, calls other `mbo.save()` | Create related records, trigger related saves |
| **After Commit** | `"afterCommit": true` | After transaction is committed | `save()` with notifications/external calls | Notifications, external systems |
| **After Add** | `"afterAdd": true` | After MBO is added to MboSet | `add()` override | Set flags, initialize after add |
| **Before Delete** | `"beforeDelete": true` | Before MBO is deleted | `canDelete()` override | Validate before deletion |
| **Validate Application** | `"validateApplication": true` | During object-level validation | `appValidate()` (alternative approach) | Cross-field validation, business rules |
| **Allow Object Creation** | `"allowObjectCreation": true` | Before new MBO is created | N/A | Prevent creation, set defaults |
| **Allow Object Deletion** | `"allowObjectDeletion": true` | Before MBO is deleted | `canDelete()` (alternative approach) | Prevent deletion, cleanup |

**CRITICAL: Java Method to Event Timing Mapping**

When converting Java MBO classes to Python automation scripts, analyze the Java method structure to determine the correct event timing:

| Java Method | Java Code Pattern | Event Timing | scriptConfig Property |
|------------|-------------------|--------------|----------------------|
| `init()` | Object initialization | `initializeValue: True` | Object initialization |
| `appValidate()` | Any validation logic | `beforeSave: True` | Validation before DB save |
| `save()` | Logic BEFORE `super.save()` | `beforeSave: True` | Field manipulation before save |
| `save()` | Logic AFTER `super.save()` | `afterSave: True` | Trigger related saves |
| `save()` | Calls `otherMbo.save()` | `afterSave: True` | Cascading saves |
| `save()` | Sends email/notification | `afterCommit: True` | External communication |
| `save()` | Calls external API/service | `afterCommit: True` | External integration |
| `add()` | Sets flags/values | `afterAdd: True` | Post-add initialization |
| `canDelete()` | Validation logic | `beforeDelete: True` | Delete validation |

---

### initializeValue - Object Initialization

**When it runs**: When an MBO is initialized (loaded into memory)

**Java Method**: `init()`

**JSON Configuration**:
```json
{
    "launchPointType": "OBJECT",
    "objectName": "OBJECTNAME",
    "initializeValue": true
}
```

**Use cases**:
- Set default values
- Initialize fields from related objects
- Set field flags (readonly, required) based on conditions
- Populate fields from owner MBO

**Example 1: Basic Initialization with Default Values**

```python
################
# Script:
# Object Launch Point
#
# Launch Point: BRTOBSMATERIAL.OBJ.INIT
# Object: BRTOBSMATERIAL
#
# Author: Developer Name
#
# Revision:
# Date        User                        Comment
# 2024-01-15  Developer Name              Initial creation - Set link to Ticket
################

from psdi.mbo import MboConstants
from psdi.mbo import Mbo
from psdi.mbo import MboSet

# Set entire MBO readonly based on owner status
ticket = mbo.getOwner()
if ticket and ticket.isBasedOn("SR"):
    tkStatus = ticket.getString("STATUS")
    if tkStatus in ('IMREVIEW', 'FMREVIEW', 'APPR', 'RESOLVED', 'IMCAREVIEW', 'ISUPREVIEW', 'IALMREVIEW'):
        mbo.setFlag(MboConstants.READONLY, True)

scriptConfig="""{
    "autoscript": "BRTOBSMATERIAL.OBJ.INIT",
    "description": "Set link to Ticket",
    "version": "",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "BRTOBSMATERIAL.OBJ.INIT",
            "launchPointType": "OBJECT",
            "active": true,
            "description": "Set link to Ticket",
            "objectName": "BRTOBSMATERIAL",
            "initializeValue": true
        }
    ]
}"""
```

**Example 2: Initialize from Owner with Conditional Logic**

```python
################
# Script:
# Object Launch Point
#
# Launch Point: BRTASSETAVAILDLG.OBJ.INIT
# Object: BRTASSETAVAIL
#
# Author: Kevin Lin
# Date: 05/18/2022
# DR: 2423
################

from psdi.server import MXServer
from psdi.mbo import MboConstants
from psdi.mbo import Mbo
from psdi.security import UserInfo

def setError(p0, p1, p2):
    global errorkey, errorgroup, params
    errorkey = 'InfoParameters3'
    errorgroup = 'AutoScript'
    params = [p0, p1, p2]

# Initialize asset number from owner work order
if interactive and mbo.getThisMboSet().getParentApp() in ('MRGWO', 'NRVEWO', 'ENGWO'):
    wo = mbo.getOwner()
    woNum = wo.getString("WONUM")
    assetNum = wo.getString("ASSETNUM")
    if len(assetNum) > 4:
        mbo.setValue("ASSETNUM", assetNum)
        mbo.setValue("CHANGEDT", MXServer.getMXServer().getDate())

scriptConfig="""{
    "autoscript": "BRTASSETAVAILDLG.OBJ.INIT",
    "description": "Initialize Asset Sub Status Change Dialog",
    "version": "",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "BRTASSETAVAILDLG.OBJ.INIT",
            "launchPointType": "OBJECT",
            "active": true,
            "description": "Initialize Asset Sub Status Change Dialog",
            "objectName": "BRTASSETAVAIL",
            "initializeValue": true
        }
    ]
}"""
```

**Key Patterns for initializeValue**:
- Use `mbo.setValue()` with `MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION` for programmatic updates
- Use `mbo.setFieldFlag()` to set readonly/required flags
- Use `mbo.setFlag()` to set MBO-level flags
- Check `interactive` if logic should only run in UI
- Get owner with `mbo.getOwner()` to access parent MBO
- Use `mbo.toBeAdded()` to check if MBO is being added

---

### beforeSave - Before Save

**When it runs**: Before an MBO is saved to the database

**Java Methods**: `appValidate()`, `save()` with logic BEFORE `super.save()`

**JSON Configuration**:
```json
{
    "launchPointType": "OBJECT",
    "objectName": "OBJECTNAME",
    "save": true,
    "add": true,        // Optional: true/false - run on add
    "update": true,     // Optional: true/false - run on update
    "delete": false,    // Optional: true/false - run on delete
    "beforeSave": true
}
```

**Use cases**:
- Validate business rules before save
- Auto-populate fields before save
- Prevent save with errors if validation fails
- Update related fields before save

**Example 1: Validation Before Save**

```python
################
# Script:
# Object Launch Point
#
# Launch Point: BRTOBSMAT.OBJ.SAVE
# Object: BRTOBSMATERIAL
#
# Author: Kevin Lin
# Redmine: 3149
# Date: 12/13/2023
################

from psdi.server import MXServer
from psdi.mbo import MboConstants

# Validate total cost for IAR application
if app == 'IAR':
    totalCost = mbo.getString('TOTALCOST')
    if not totalCost:
        service.error('Total Cost', 'can not be empty!')
    elif not totalCost > 0:
        service.error('Total Cost', 'must be greater than zero!')

scriptConfig="""{
    "autoscript": "BRTOBSMAT.OBJ.SAVE",
    "description": "Set sequence of Events on Save",
    "version": "",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "BRTOBSMAT.OBJ.SAVE",
            "launchPointType": "OBJECT",
            "active": true,
            "description": "Set sequence of Events on Save",
            "objectName": "BRTOBSMATERIAL",
            "save": true,
            "add": true,
            "update": true,
            "delete": false,
            "beforeSave": true
        }
    ]
}"""
```

**Example 2: Complex Validation with Owner and Related Records**

```python
################
# Script:
# Object Launch Point
#
# Launch Point: BRTASSETAVAIL.OBJ.SAVE
# Object: BRTASSETAVAIL
#
# Author: Kevin Lin
# Date: 05/31/2022
# Redmine: FEA 2423
################

from psdi.server import MXServer
from psdi.mbo import MboConstants
from psdi.mbo import Mbo
from psdi.security import UserInfo

def setError(p0, p1, p2):
    global errorkey, errorgroup, params
    errorkey = 'InfoParameters3'
    errorgroup = 'AutoScript'
    params = [p0, p1, p2]

mxServer = MXServer.getMXServer()
today = mxServer.getDate()

mbo = mboset.getMbo(0)
userInfo = mbo.getThisMboSet().getUserInfo()
subStatus = mbo.getString('SUBSTATUS')
memo = mbo.getString('MEMO')

wo = mbo.getOwner()
woNum = wo.getString('WONUM')
appName = wo.getThisMboSet().getParentApp()

if interactive and appName in ('MRGWO', 'NRVEWO', 'ENGWO'):
    asset = wo.getMboSet('ASSET').moveFirst()
    assetStatus = asset.getString('STATUS')
    assetId = asset.getString('ASSETID')
    
    # Validation logic
    if mbo.isNull('SUBSTATUS'):
        setError('Please choose', 'a', 'Sub Status')
    elif mbo.getString('SUBSTATUS').upper() == assetStatus.upper():
        setError('The status you selected', 'is the same as the asset current status.', 
                 'Please choose a different sub status')
    elif mbo.isNull('MEMO') and mbo.getString('SUBSTATUS') == 'OOS':
        setError('The MEMO Field', 'is Mandatory', 
                 'Please enter a reason for moving asset to OOS Status')
    else:
        # Update asset with new status
        asset.setValue('SUBSTATUS', subStatus, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
        asset.setValue('STATUS', subStatus, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
        asset.setValue('MEMO', memo, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
        asset.setValue('ORIGAPP', appName, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
        asset.setValue('RECORDID', woNum, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
        wo.getThisMboSet().save()
        
        # Create history record
        historySet = asset.getMboSet("PLUSTASSETSTHIST")
        newHistory = historySet.add(2)  # Use regular integer, not 2L
        if newHistory is not None:
            newHistory.setValue('ASSETID', assetId)
            newHistory.setValue("STATUS", subStatus)
            newHistory.setValue("DESCRIPTION", asset.getString('DESCRIPTION'))
            newHistory.setValue("CHANGEDATE", today)
            newHistory.setValue("CHANGEBY", user)
            newHistory.setValue("CHANGEAPP", appName)
            newHistory.setValue("CHANGEAPPREF", 'WO: ' + woNum + " of Asset Availability Change Action")
            newHistory.setValue("MEMO", memo)
            newHistory.setValue("SITEID", 'BART')
            historySet.save()

scriptConfig="""{
    "autoscript": "BRTASSETAVAIL.OBJ.SAVE",
    "description": "When Asset Availability Change Dialog Save",
    "version": "",
    "active": false,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "BRTASSETAVAIL.OBJ.SAVE",
            "launchPointType": "OBJECT",
            "active": false,
            "description": "When Asset Availability Change Dialog Save",
            "objectName": "BRTASSETAVAIL",
            "save": true,
            "add": true,
            "update": false,
            "delete": false,
            "beforeSave": true
        }
    ]
}"""
```

**Key Patterns for beforeSave**:
- Use `onadd`, `onupdate`, `ondelete` to check MBO state
- Use `service.error()` to prevent save with validation errors
- Use `mbo.isNull()` and `mbo.isModified()` to check field state
- Always use `MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION` for programmatic updates
- Access owner with `mbo.getOwner()`
- Access related sets with `mbo.getMboSet("RELATIONSHIPNAME")`
- Use `return` to exit early if validation fails

---

### afterSave - After Save

**When it runs**: After an MBO is saved to the database (but before transaction commit)

**Java Methods**: `save()` with logic AFTER `super.save()`, calls `otherMbo.save()`

**JSON Configuration**:
```json
{
    "launchPointType": "OBJECT",
    "objectName": "OBJECTNAME",
    "save": true,
    "add": true,        // Optional: true/false
    "update": true,     // Optional: true/false
    "delete": false,    // Optional: true/false
    "afterSave": true
}
```

**Use cases**:
- Create related records after save
- Update related objects after save
- Send notifications/emails after save
- Log audit information

**Example: Create Related Records After Save**

```python
################
# Script:
# Object Launch Point
#
# Launch Point: WORKORDER.OBJ.SAVE.AFTER
# Object: WORKORDER
#
# Author: Developer Name
#
# Revision:
# Date        User                        Comment
# 2024-01-15  Developer Name              Initial creation - Create activity log after save
################

from psdi.mbo import MboConstants
from psdi.server import MXServer

# Only run after successful save
if onadd or onupdate:
    # Create activity log entry
    actLogSet = mbo.getMboSet("ACTIVITYLOG")
    newActLog = actLogSet.add()
    if newActLog is not None:
        newActLog.setValue("DESCRIPTION", "Work order saved", 
                          MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
        newActLog.setValue("CHANGEDATE", MXServer.getMXServer().getDate(),
                          MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
        newActLog.setValue("CHANGEBY", user,
                          MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
        actLogSet.save()

scriptConfig="""{
    "autoscript": "WORKORDER.OBJ.SAVE.AFTER",
    "description": "Create activity log after save",
    "version": "",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "WORKORDER.OBJ.SAVE.AFTER",
            "launchPointType": "OBJECT",
            "active": true,
            "description": "Create activity log after save",
            "objectName": "WORKORDER",
            "save": true,
            "add": true,
            "update": true,
            "delete": false,
            "afterCommit": true
        }
    ]
}"""
```

**Key Patterns for afterSave**:
- Use `onadd`, `onupdate` to check what triggered the save
- Create related records using `mboSet.add()`
- Always save the MBO set after adding records
- Use flags when setting values on new records
- Send emails using `MXServer.sendEMail()`
- Use communication templates for email content
- Check `interactive` and `app` for conditional logic

---

### afterCommit - After Commit

**When it runs**: After the transaction is committed to the database

**Java Methods**: `save()` with email/notification/external API calls

**JSON Configuration**:
```json
{
    "launchPointType": "OBJECT",
    "objectName": "OBJECTNAME",
    "save": true,
    "add": true,
    "update": true,
    "delete": false,
    "afterCommit": true
}
```

**Use cases**:
- Post-commit operations that must happen after transaction is committed
- External system notifications
- Audit logging to external systems
- Trigger external processes

**Example: After Commit - Post-Commit Operations**

```python
################
# Script:
# Object Launch Point - After Commit
#
# Launch Point: WORKORDER.OBJ.SAVE.AFTERCOMMIT
# Object: WORKORDER
#
# Author: Developer Name
################

from psdi.mbo import MboConstants
from psdi.server import MXServer

# Post-commit operations
if onadd or onupdate:
    wonum = mbo.getString("WONUM")
    status = mbo.getString("STATUS")
    
    # Operations that must happen after commit
    # Example: Call external web service
    # Example: Write to external audit log
    # Example: Trigger external process

scriptConfig="""{
    "autoscript": "WORKORDER.OBJ.SAVE.AFTERCOMMIT",
    "description": "Post-commit operations",
    "version": "",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "WORKORDER.OBJ.SAVE.AFTERCOMMIT",
            "launchPointType": "OBJECT",
            "active": true,
            "description": "Post-commit operations",
            "objectName": "WORKORDER",
            "save": true,
            "add": true,
            "update": true,
            "delete": false,
            "afterCommit": true
        }
    ]
}"""
```

**Key Patterns for afterCommit**:
- Use for operations that must happen after database commit
- Typically used for external system integration
- Cannot rollback transaction from afterCommit
- Use for audit logging to external systems
- Send notifications after data is committed

---

### afterAdd - After Add

**When it runs**: After an MBO is added to an MboSet

**Java Method**: `add()` override

**JSON Configuration**:
```json
{
    "launchPointType": "OBJECT",
    "objectName": "OBJECTNAME",
    "add": true,
    "afterAdd": true
}
```

**Use cases**:
- Set flags after add completes
- Initialize relationships after add
- Set field values after add
- Trigger related object updates

**Example: After Add - Set Flags After Add**

```python
################
# Script:
# Object Launch Point - After Add
#
# Launch Point: CLASSSPEC.OBJ.ADD
# Object: CLASSSPEC
#
# Author: Converted from Java MBO TMG_ClassSpec
#
# Revision:
# Date        User                        Comment
# 2025-12-01  Automation                  Converted from TMG_ClassSpec.java add() method
#                                         TR008763: Set USEINLOCDESC to null on add
################

# Set USEINLOCDESC to null
# This allows the init() method to set the proper default value
mbo.setValueNull("USEINLOCDESC")

scriptConfig="""{
    "autoscript": "CLASSSPEC.OBJ.ADD",
    "description": "Add CLASSSPEC - Set USEINLOCDESC to null (TR008763)",
    "version": "1.0.0",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "CLASSSPEC_OBJ_ADD",
            "launchPointType": "OBJECT",
            "active": true,
            "description": "Add new CLASSSPEC record with proper field initialization",
            "objectName": "CLASSSPEC",
            "add": true,
            "afterAdd": true  # Set USEINLOCDESC after add completes
        }
    ]
}"""
```

**Key Patterns for afterAdd**:
- Use for operations that must happen after add completes
- Set field values with `mbo.setValue()` or `mbo.setValueNull()`
- Initialize relationships with related objects
- Set flags on parent objects
- Use `MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION` for programmatic updates

---

### beforeDelete - Before Delete

**When it runs**: Before an MBO is deleted from the database

**Java Method**: `canDelete()` override

**JSON Configuration**:
```json
{
    "launchPointType": "OBJECT",
    "objectName": "OBJECTNAME",
    "delete": true,
    "beforeDelete": true
}
```

**Use cases**:
- Validate before deletion
- Check for related records
- Prevent deletion based on business rules
- Check status before allowing deletion

**Example: Before Delete - Validate Before Deletion**

```python
################
# Script:
# Object Launch Point - Before Delete
#
# Launch Point: MR.OBJ.CANDELETE
# Object: MR
#
# Author: Converted from Java MBO TMG_MR
################

from psdi.mbo import MboConstants

# Prevent deletion if MR has related PR records
prSet = mbo.getMboSet("PR")
if not prSet.isEmpty():
    pr = prSet.getMbo(0)
    prStatus = pr.getString("STATUS").upper()
    
    if prStatus != "CAN":
        service.error("Cannot delete MR", 
                     "MR has related PR in status: " + prStatus)

scriptConfig="""{
    "autoscript": "MR.OBJ.CANDELETE",
    "description": "MR canDelete - Validate before deletion",
    "version": "1.0.0",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "MR_OBJ_CANDELETE",
            "launchPointType": "OBJECT",
            "active": true,
            "description": "Validate before MR deletion",
            "objectName": "MR",
            "delete": true,
            "beforeDelete": true  # Validate before deletion
        }
    ]
}"""
```

**Key Patterns for beforeDelete**:
- Use `ondelete` to check if deletion is happening
- Use `service.error()` to prevent deletion
- Check for related records before allowing deletion
- Validate business rules before deletion
- Use `return` to exit early

---

### validateApplication - Object Validation

**When it runs**: During object-level validation (alternative to beforeSave for validation-only logic)

**Use cases**:
- Cross-field validation
- Complex business rule validation
- Validation that requires multiple fields

**Example: Object-Level Validation**

```python
################
# Script:
# Object Launch Point
#
# Launch Point: PO.OBJ.VALID
# Object: PO
#
# Author: Developer Name
#
# Revision:
# Date        User                        Comment
# 2024-01-15  Developer Name              Initial creation - Validate purchase order totals
################

from psdi.mbo import MboConstants

# Validate that total cost matches sum of line items
totalCost = mbo.getDouble("TOTALCOST")
polineSet = mbo.getMboSet("POLINE")
polineSet.reset()

calculatedTotal = 0.0
count = polineSet.count()
for i in range(count):
    poline = polineSet.getMbo(i)
    if poline:
        calculatedTotal = calculatedTotal + poline.getDouble("LINECOST")

if abs(totalCost - calculatedTotal) > 0.01:  # Allow for rounding
    service.error('Total Cost', 'does not match sum of line items')

scriptConfig="""{
    "autoscript": "PO.OBJ.VALID",
    "description": "Validate purchase order totals",
    "version": "",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "PO.OBJ.VALID",
            "launchPointType": "OBJECT",
            "active": true,
            "description": "Validate purchase order totals",
            "objectName": "PO",
            "save": true,
            "add": true,
            "update": true,
            "delete": false,
            "beforeSave": true
        }
    ]
}"""
```

---

## Attribute Launch Points

### FLD.VALIDATE - Field Validation

**When it runs**: When a field value is being validated (before it's set)

**Use cases**:
- Validate field value meets business rules
- Check field value against related records
- Prevent invalid values from being set
- Cross-reference validation with other objects

**Example 1: Basic Field Validation**

```python
################
# Script:
# Attribute Launch Point
#
# Launch Point: BRTOBSMAT.FLD.ITEMNUM.VALIDATE
# Object: BRTOBSMATERIAL
# Attribute: ITEMNUM
#
# Author: Developer Name
#
# Revision:
# Date        User                        Comment
# 2024-01-15  Developer Name              Initial creation - Validate Itemnum
################

from psdi.mbo import MboConstants

def setError(p0, p1, p2):
    global errorkey, errorgroup, params
    errorkey = 'InfoParameters3'
    errorgroup = 'AutoScript'
    params = [p0, p1, p2]

# Clear related fields when item number is cleared
if mbo.isModified("ITEMNUM") and mbo.isNull("ITEMNUM"):
    mbo.setValueNull("GLDEBITACCT")
    mbo.setValueNull("BINNUM")
    mbo.setValueNull("QUANTITY")
    mbo.setValueNull("CONDITIONCODE")
    mbo.setValueNull("ROTASSETNUM")

scriptConfig="""{
    "autoscript": "BRTOBSMAT.FLD.ITEMNUM.VALIDATE",
    "description": "Validate Itemnum",
    "version": "",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "BRTOBSMAT.FLD.ITEMNUM.VALIDATE",
            "launchPointType": "ATTRIBUTE",
            "active": true,
            "description": "Validate itemnum",
            "objectName": "BRTOBSMATERIAL",
            "attributeName": "ITEMNUM",
            "validate": true
        }
    ]
}"""
```

**Example 2: Complex Validation with Related Records**

```python
################
# Script:
# Attribute Launch Point
#
# Launch Point: BRTOBSMATERIAL.FLD.BINNUM.VALID
# Object: BRTOBSMATERIAL
# Attribute: BINNUM
#
# Author: Kevin Lin
# Date: 09/19/2023
# Redmine: 2947
################

owner = mbo.getOwner()
srClass = owner.getString('CLASS')
srApp = owner.getThisMboSet().getParentApp()
itemNum = mbo.getString('ITEMNUM')
storeRoom = mbo.getString('STOREROOM')
binNum = mbo.getString('BINNUM')

# Validate duplicate item, storeroom and binnum combination for IAR tickets
if srClass.upper() == 'IAR' and srApp.upper() == 'IAR':
    obsMatSet = owner.getMboSet("$obsMat", "BRTOBSMATERIAL", 
                                "ITEMNUM = '" + itemNum + "' AND STOREROOM = '" + storeRoom + 
                                "' AND BINNUM = '" + binNum + "'")
    obsMatSet.setOrderBy("TICKETID DESC")
    obsMatSet.reset()
    obsMat = obsMatSet.moveFirst()
    if obsMat:
        srStatus = obsMat.getString('TOSR.STATUS')
        if srStatus not in ('RESOLVED', 'CLOSED'):
            service.error('ERROR', 'A duplicate IAR ticket ' + obsMat.getString('TICKETID') + 
                         ' is in the system! The duplication is based on ITEMNUM, STOREROOM and BINNUM combination.')

scriptConfig="""{
    "autoscript": "BRTOBSMATERIAL.FLD.BINNUM.VALID",
    "description": "Validate duplicated item, storeroom and binnum combination when create IAR ticket",
    "version": "",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "BRTOBSMATERIAL.FLD.BINNUM.VALID",
            "launchPointType": "ATTRIBUTE",
            "active": true,
            "description": "Validate duplicated item, storeroom and binnum combination when create IAR ticket",
            "objectName": "BRTOBSMATERIAL",
            "attributeName": "BINNUM",
            "validate": true
        }
    ]
}"""
```

**Example 3: Validation with Field Flags**

```python
################
# Script:
# Attribute Launch Point
#
# Launch Point: BRTOBSMAT.FLD.SOURCE
# Object: BRTOBSMATERIAL
# Attribute: SOURCE
#
# Author: Vamsi
################

from psdi.mbo import MboConstants

def setError(p0, p1, p2):
    global errorkey, errorgroup, params
    errorkey = 'InfoParameters3'
    errorgroup = 'AutoScript'
    params = [p0, p1, p2]

# Set required fields based on source selection
if mbo.isModified("SOURCE"):
    if not mbo.isNull("SOURCE"):
        source = mbo.getString("SOURCE")
        if source == 'CYCLE COUNT':
            mbo.setFieldFlag("COUNTBOOKNUM", MboConstants.REQUIRED, True)
            mbo.setFieldFlag("WONUM", MboConstants.REQUIRED, False)
            mbo.setFieldFlag("PONUM", MboConstants.REQUIRED, False)
        elif source == 'ISSUE':
            mbo.setFieldFlag("WONUM", MboConstants.REQUIRED, True)
            mbo.setFieldFlag("PONUM", MboConstants.REQUIRED, False)
            mbo.setFieldFlag("COUNTBOOKNUM", MboConstants.REQUIRED, False)
        elif source == 'TRANSFER':
            mbo.setFieldFlag("PONUM", MboConstants.REQUIRED, True)
            mbo.setFieldFlag("COUNTBOOKNUM", MboConstants.REQUIRED, False)
            mbo.setFieldFlag("WONUM", MboConstants.REQUIRED, False)
        else:
            mbo.setFieldFlag("PONUM", MboConstants.REQUIRED, False)
            mbo.setFieldFlag("COUNTBOOKNUM", MboConstants.REQUIRED, False)
            mbo.setFieldFlag("WONUM", MboConstants.REQUIRED, False)
    else:
        mbo.setFieldFlag("PONUM", MboConstants.REQUIRED, False)
        mbo.setFieldFlag("COUNTBOOKNUM", MboConstants.REQUIRED, False)
        mbo.setFieldFlag("WONUM", MboConstants.REQUIRED, False)

scriptConfig="""{
    "autoscript": "BRTOBSMAT.FLD.SOURCE",
    "description": "Set WONUM,PO,countbook required",
    "version": "",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "BRTOBSMAT.FLD.SOURCE",
            "launchPointType": "ATTRIBUTE",
            "active": true,
            "description": "Set WONUM,PO,countbook required",
            "objectName": "BRTOBSMATERIAL",
            "attributeName": "SOURCE",
            "validate": true
        }
    ]
}"""
```

**Key Patterns for FLD.VALIDATE**:
- Use `mbo.isModified("FIELDNAME")` to check if field changed
- Use `mbo.isNull("FIELDNAME")` to check if field is null
- Use `service.error()` to prevent invalid values
- Use `mbo.setFieldFlag()` to dynamically set required/readonly flags
- Access previous value with `mbo.getMboValue("FIELDNAME").getPreviousValue()`

---

### FLD.ACTION - Field Action

**When it runs**: When a field value changes (after validation passes)

**Use cases**:
- Auto-populate related fields when field changes
- Update related records when field changes
- Clear dependent fields when field changes
- Trigger calculations when field changes

**Example: Auto-Populate Related Fields**

```python
################
# Script:
# Attribute Launch Point
#
# Launch Point: BRTOBSMATERIAL.FLD.STOREROOM.ACTION
# Object: BRTOBSMATERIAL
# Attribute: STOREROOM
#
# Author: Developer Name
################

from psdi.mbo import Mbo
from psdi.mbo import MboConstants

# Set GL accounts from inventory when storeroom changes
if not mbo.isNull("STOREROOM"):
    invSet = mbo.getMboSet("INVENTORY")
    if invSet.getMbo(0) is not None:
        glCredit = invSet.getMbo(0).getString("CONTROLACC")
        glDBAcctSegment = invSet.getMbo(0).getString("SHRINKAGEACC")
        glDBAccount = glDBAcctSegment.split('-')
        
        mbo.setValue("GLCREDITACCT", glCredit, 
                    MboConstants.NOVALIDATION | MboConstants.NOACCESSCHECK)
        
        itemMbo = invSet.getMbo(0).getMboSet("ITEM").getMbo(0)
        if itemMbo is not None:
            deptDetailMbo = itemMbo.getMboSet("DEPTGLCOMP").getMbo(0)
            if deptDetailMbo is not None:
                glDebitAccount = deptDetailMbo.getString("GLACCOUNT")
                glDebit = glDebitAccount.split('-')
                glDebitAcct = '-'.join([glDebit[0], glDebit[1], glDBAccount[2], glDebit[3]])
                mbo.setValue("GLDEBITACCT", glDebitAcct, 
                            MboConstants.NOVALIDATION | MboConstants.NOACCESSCHECK)

scriptConfig="""{
    "autoscript": "BRTOBSMATERIAL.FLD.STOREROOM.ACTION",
    "description": "Set GL from Inventory",
    "version": "",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "BRTOBSMATERIAL.FLD.STOREROOM.ACTION",
            "launchPointType": "ATTRIBUTE",
            "active": true,
            "description": "Set GL from Inventory",
            "objectName": "BRTOBSMATERIAL",
            "attributeName": "STOREROOM",
            "runAction": true
        }
    ]
}"""
```

**Key Patterns for FLD.ACTION**:
- Always check if field is not null before processing
- Use `MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION` when setting values
- Access related sets with `mbo.getMboSet("RELATIONSHIPNAME")`
- Navigate through relationships to get related data

---

### FLD.INIT - Field Initialization

**When it runs**: When a field is initialized (value is first accessed)

**Use cases**:
- Set default field values
- Initialize field from related objects
- Set field flags based on conditions
- Populate field from owner MBO

**Example 1: Initialize Field Value**

```python
################
# Script:
# Attribute Launch Point
#
# Launch Point: WORKORDER.FLD.WOCREATESTATUS.INIT
# Object: WORKORDER
# Attribute: WOCREATESTATUS
#
# Author: Eric Zuo
# Date: 2018 July 31
################

import sys

def setError(p0, p1, p2):
    global errorkey, errorgroup, params
    errorkey = 'InfoParameters3'
    errorgroup = 'AutoScript'
    params = [p0, p1, p2]

try:
    thismbo = mbo
    if not thismbo.isNull("wocreatestatus"):
        status = thismbo.getString('status')
        
        if thismbo.toBeAdded():
            editable = False
        elif status != 'WAPPR':
            editable = True
        else:
            editable = False
        
        # Set field flag (Note: 7L is READONLY flag, but should use MboConstants.READONLY)
        thismbo.setFieldFlag('wocreatestatus', MboConstants.READONLY, not editable)

except Exception, e:
    setError('Exception Captured.', sys.exc_info()[0], ', workorder.FldWoCreateStatus.Init')

scriptConfig="""{
    "autoscript": "WORKORDER.FLD.WOCREATESTATUS.INIT",
    "description": "WORKORDER.FLD.WOCREATESTATUS.INIT Script",
    "version": "1.0",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "WORKORDER.FLD.WOCREATESTATUS.INIT",
            "launchPointType": "ATTRIBUTE",
            "active": true,
            "description": "WORKORDER.FLD.WOCREATESTATUS.INIT LP",
            "objectName": "WORKORDER",
            "attributeName": "WOCREATESTATUS",
            "initializeAccessRestriction": true
        }
    ]
}"""
```

**Example 2: Initialize Field from Owner**

```python
################
# Script:
# Attribute Launch Point
#
# Launch Point: BRTOBSMATERIAL.FLD.TICKETID.INIT
# Object: BRTOBSMATERIAL
# Attribute: TICKETID
#
# Author: Developer Name
################

from psdi.mbo import MboConstants
from psdi.mbo import Mbo

# Initialize ticket ID from owner service request
ticket = mbo.getOwner()
if ticket and ticket.isBasedOn("SR"):
    status = ticket.getString("STATUS")
    if status not in ('IMREVIEW', 'FMREVIEW', 'APPR', 'RESOLVED'):
        ticketid = ticket.getString("TICKETID")
        mbo.setValue("TICKETID", ticketid, MboConstants.NOACCESSCHECK)
        mbo.setValue("ORGID", ticket.getString("ORGID"), MboConstants.NOACCESSCHECK)
        mbo.setValue("SITEID", ticket.getString("SITEID"), MboConstants.NOACCESSCHECK)

scriptConfig="""{
    "autoscript": "BRTOBSMATERIAL.FLD.TICKETID.INIT",
    "description": "Initialize ticket ID from owner",
    "version": "",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "BRTOBSMATERIAL.FLD.TICKETID.INIT",
            "launchPointType": "ATTRIBUTE",
            "active": true,
            "description": "Initialize ticket ID from owner",
            "objectName": "BRTOBSMATERIAL",
            "attributeName": "TICKETID",
            "initializeValue": true
        }
    ]
}"""
```

**Key Patterns for FLD.INIT**:
- Use `mbo.setValue()` with flags for programmatic initialization
- Use `mbo.setFieldFlag()` to set readonly/required flags
- Check `mbo.isNull()` before setting values
- Access owner with `mbo.getOwner()`

---

### FLD.LIST - Field List

**When it runs**: When a field list/domain is being retrieved

**Use cases**:
- Filter domain values dynamically
- Add custom values to field list
- Restrict available values based on conditions
- Customize list based on related object values

**Example: Filter Domain Values**

```python
################
# Script:
# Attribute Launch Point
#
# Launch Point: WORKORDER.FLD.ASSETINSRMVLOCATION.LIST
# Object: ASSETINSRMV
# Attribute: LOCATION
#
# Author: Eric Zuo
# Date: 2018 Sept 17
################

# Filter location domain to show only operating locations
domainid = "LOCATIONST2"
listWhere = "status in ('OPERATING')"

scriptConfig="""{
    "autoscript": "WORKORDER.FLD.ASSETINSRMVLOCATION.LIST",
    "description": "workorder.Fld.AssetInsRmvLocation.List",
    "version": "1.0",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "WORKORDER.FLD.ASSETINSRMVLOCATION.LIST",
            "launchPointType": "ATTRIBUTE",
            "active": true,
            "description": "workorder.Fld.AssetInsRmvLocation.List",
            "objectName": "ASSETINSRMV",
            "attributeName": "LOCATION",
            "retrieveList": true
        }
    ]
}"""
```

**Key Patterns for FLD.LIST**:
- Set `domainid` to specify which domain to filter
- Set `listWhere` to filter domain values with WHERE clause
- Use SQL WHERE clause syntax for filtering

---

## Action Launch Points

### ACTION.[ACTIONNAME] - Custom Actions

**When it runs**: When a custom action is executed (from workflow, UI button, etc.)

**Use cases**:
- Execute custom business logic when action is triggered
- Create related records when action executes
- Update multiple objects when action executes
- Send notifications when action executes

**Example: Custom Action Script**

```python
################
# Script:
# Action Launch Point
#
# Launch Point: WORKORDER.ACTION.DUPLICATE
# Object: WORKORDER
# Action: DUPLICATE
#
# Author: Developer Name
#
# Revision:
# Date        User                        Comment
# 2024-01-15  Developer Name              Initial creation - Duplicate work order
################

from psdi.mbo import MboConstants
from psdi.server import MXServer

# Duplicate work order with related records
dupMbo = mbo.duplicate()
if dupMbo is not None:
    # Update duplicate work order number and status
    dupMbo.setValue("WONUM", generateNewWONum(), 
                   MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
    dupMbo.setValue("STATUS", "NEW", 
                   MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
    
    # Duplicate related activities
    origActSet = mbo.getMboSet("WOACTIVITY")
    dupActSet = dupMbo.getMboSet("WOACTIVITY")
    origCount = origActSet.count()
    
    if origCount > 0:
        for i in range(origCount):
            dupAct = dupActSet.add()
            origAct = origActSet.getMbo(i)
            if origAct and dupAct:
                dupAct.setValue("DESCRIPTION", origAct.getString("DESCRIPTION"),
                               MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
                dupAct.setValue("DURATION", origAct.getDouble("DURATION"),
                               MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
        
        dupActSet.save()

scriptConfig="""{
    "autoscript": "WORKORDER.ACTION.DUPLICATE",
    "description": "Duplicate work order with related records",
    "version": "",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "WORKORDER.ACTION.DUPLICATE",
            "launchPointType": "ACTION",
            "active": true,
            "description": "Duplicate work order with related records",
            "objectName": "WORKORDER",
            "actionName": "DUPLICATE"
        }
    ]
}"""
```

**Key Patterns for ACTION Launch Points**:
- Use `mbo.duplicate()` to create copies
- Use `mboSet.add()` to create related records
- Always save MBO sets after adding records
- Use flags when setting values programmatically

---

## Cron Task Scripts

**When it runs**: On a scheduled basis (configured in Cron Task Setup)

**Use cases**:
- Scheduled batch processing
- Data synchronization
- Automated notifications
- Scheduled data updates
- Report generation

**Example: Cron Task Script**

```python
################
# Script:
# Cron Task Script
#
# Cron Task: RSS Asset Update Serial
# Description: Update asset serial numbers from external system
#
# Author: Venkat Achanta
# Version: 1.0
# Date: 09-05-2024
# DR: 2893
################

from psdi.util.logging import MXLoggerFactory
from psdi.server import MXServer
from psdi.mbo import MboConstants
from psdi.security import UserInfo
from java.sql import Connection
from java.sql import Statement

logger = service.getLogger("maximo.bart")

def get_connection():
    """Get database connection for cron task"""
    mxServer = MXServer.getMXServer()
    userInfo = mxServer.getSystemUserInfo()
    dbm = mxServer.getDBManager()
    conKey = userInfo.getConnectionKey()
    return dbm.getConnection(conKey)

def update_asset_serial_numbers():
    """Update asset serial numbers from external data"""
    mxServer = MXServer.getMXServer()
    userInfo = mxServer.getSystemUserInfo()
    
    try:
        conn = get_connection()
        stmt = conn.createStatement()
        
        # Query for assets needing serial number updates
        query = "SELECT ASSETNUM, SERIALNUM FROM TEMP_ASSET_UPDATE WHERE PROCESSED = '0'"
        rs = stmt.executeQuery(query)
        
        assetSet = mxServer.getMboSet("ASSET", userInfo)
        count = 0
        
        while rs.next():
            assetNum = rs.getString("ASSETNUM")
            serialNum = rs.getString("SERIALNUM")
            
            assetSet.setWhere("ASSETNUM = '" + assetNum + "'")
            assetSet.reset()
            
            if not assetSet.isEmpty():
                asset = assetSet.getMbo(0)
                asset.setValue("SERIALNUM", serialNum, 
                              MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
                assetSet.save()
                count = count + 1
                logger.info("Updated serial number for asset: " + assetNum)
        
        assetSet.close()
        stmt.close()
        conn.close()
        
        logger.info("Cron task completed. Updated " + str(count) + " assets.")
        
    except Exception, e:
        logger.error("Error in cron task: " + str(e))
        raise

# Execute the cron task
update_asset_serial_numbers()

scriptConfig="""{
    "autoscript": "CRON.RSS.ASSET.UPDATE.SERIAL",
    "description": "Update asset serial numbers from external system",
    "version": "1.0",
    "active": true,
    "logLevel": "INFO"
}"""
```

**Key Patterns for Cron Tasks**:
- Always use `MXServer.getMXServer().getSystemUserInfo()` for user context
- Use proper logging with `service.getLogger()`
- Always close MBO sets and database connections
- Use try-except blocks for error handling
- Log progress and errors for troubleshooting

---

## Integration Scripts

Integration scripts are used to customize data processing during integration operations. There are several types of integration launch points:

1. **Publish Channel Scripts** - Transform data before publishing to external systems
2. **Object Structure In (OSIN)** - Process inbound data from external systems
3. **Object Structure Out (OSOUT)** - Process outbound data before sending
4. **Object Structure Action (OSACTION)** - Custom actions on object structures
5. **Invoke Channel Scripts** - Process data in invoke channels (query, sync)

---

### Publish Channel Scripts

**When it runs**: Before data is published to external systems via publish channels

**Use cases**:
- Transform data before publishing
- Add/remove fields from integration payload
- Format data for external systems
- Set audit action flags
- Skip transactions based on conditions

**Example 1: Publish Channel - External Exit Out**

```python
################
# Script:
# Integration Script - Publish Channel
#
# Launch Point: PUBLISH.PSF_RECPTINSP.EXTEXIT.OUT
# Publish Channel: PSF_RECPTINSP
# Processing Point: External Exit Out
#
# Author: Developer Name
#
# Revision:
# Date        User                        Comment
# 2024-01-15  Developer Name              Initial creation - Transform inspection data for PS
################

from psdi.util import MXApplicationException
from psdi.mbo import MboConstants
from psdi.server import MXServer

# Process each record in the integration data
osSize = irData.getSize()
for i in range(osSize):
    # Get current MBO
    v_irmbo = irData.getCurrentMbo()
    skip = 0
    
    # Set default reject action
    vREJECTACTION = "R"
    irData.setCurrentData("REJECTACTION", vREJECTACTION)
    
    # Get data from current record
    issueType = irData.getCurrentData("ISSUETYPE")
    receiptRef = irData.getCurrentData("RECEIPTREF")
    transid = irData.getCurrentData("MATRECTRANSID")
    
    # Skip logic based on issue type
    if issueType == "RECEIPT":
        skip = 0
    elif issueType == "TRANSFER":
        vRotassetnum = irData.getCurrentData("ROTASSETNUM")
        if vRotassetnum is None:
            skip = 0
        else:
            skip = 1  # Skip transfers with rotating assets
    elif issueType == "RETURN":
        # Skip partial returns, process full returns
        skip = 1  # Set skip logic based on business rules
    
    # Transform status values
    mxstatus = irData.getCurrentData("STATUS")
    if mxstatus == 'COMP':
        irData.setCurrentData("STATUS", "C")
    else:
        irData.setCurrentData("STATUS", "I")
    
    # Set audit action
    irData.setCurrentData("AUDIT_ACTN", 'U')
    
    # Move to next record
    irData.moveToNextObjectStructure()
    
    # Skip transaction if needed
    if skip == 1:
        errorgroup = "iface"
        errorkey = "SKIP_TRANSACTION"

scriptConfig="""{
    "autoscript": "PUBLISH.PSF_RECPTINSP.EXTEXIT.OUT",
    "description": "Script for Inspection Rejection to PS",
    "version": "2.0",
    "active": true,
    "logLevel": "ERROR"
}"""
```

**Example 2: Publish Channel - User Exit Out Before**

```python
################
# Script:
# Integration Script - Publish Channel
#
# Launch Point: PUBLISH.RTV_BRTCLAIM.USEREXIT.OUT.BEFORE
# Publish Channel: RTV_BRTCLAIM
# Processing Point: User Exit Out Before
#
# Author: Vijet Shanbhag
################

from psdi.server import MXServer

def getAdditionalColDetails(mboName, whereClause, colName):
    """Helper function to get additional column details"""
    userInfo = MXServer.getMXServer().getSystemUserInfo()
    mboSetItm = MXServer.getMXServer().getMboSet(mboName, userInfo)
    mboSetItm.setWhere(whereClause)
    if mboSetItm.isEmpty():
        mboSetItm.close()
        return None
    else:
        colValue = mboSetItm.getMbo(0).getString(colName)
        mboSetItm.close()
        return colValue

# Break data into individual records
irData.breakData()
osSize = irData.getSize()

for i in range(osSize):
    # Get item number and populate related fields
    itmNum = irData.getCurrentData("ITEMNUM")
    if len(itmNum) > 0:
        irData.setCurrentData("ITEMDESC", 
                             getAdditionalColDetails("ITEM", 
                                                     "ITEMNUM = '" + itmNum + "'", 
                                                     "DESCRIPTION"))
        irData.setCurrentData("ISSUEUNIT", 
                             getAdditionalColDetails("ITEM", 
                                                     "ITEMNUM = '" + itmNum + "'", 
                                                     "ISSUEUNIT"))
    
    # Get vendor and populate vendor location
    vendor = irData.getCurrentData("VENDOR")
    if len(vendor) > 0:
        irData.setCurrentData("VENDORLOC", 
                             getAdditionalColDetails("COMPANIES", 
                                                     "COMPANY = '" + vendor + "'", 
                                                     "ADDRESS2"))
    
    # Set audit action based on MBO state
    if irData.getCurrentMbo().toBeAdded():
        irData.setCurrentData("AUDIT_ACTN", 'A')
    elif (not irData.getCurrentMbo().isNew()) and irData.getCurrentMbo().toBeSaved():
        irData.setCurrentData("AUDIT_ACTN", 'C')
    elif irData.getCurrentMbo().toBeDeleted():
        irData.setCurrentData("AUDIT_ACTN", 'D')
    
    irData.moveToNextObjectStructure()

scriptConfig="""{
    "autoscript": "PUBLISH.RTV_BRTCLAIM.USEREXIT.OUT.BEFORE",
    "description": "RTV Interface Script before sending to PSF",
    "version": "",
    "active": false,
    "logLevel": "ERROR"
}"""
```

---

### Object Structure In (OSIN) Scripts

**When it runs**: When processing inbound data from external systems via Object Structures

**Use cases**:
- Validate incoming data
- Transform data before processing
- Set default values
- Skip transactions based on conditions
- Call external services to enrich data

**Example 1: OSIN - Python Script**

```python
################
# Script:
# Integration Script - Object Structure In
#
# Launch Point: OSIN.PSF_PO
# Object Structure: PSF_PO
# Processing Point: Before Process
#
# Author: Developer Name
#
# Revision:
# Date        User                        Comment
# 2024-01-15  Developer Name              Initial creation - PO CREATE/UPDATE from PS
################

from psdi.server import MXServer
from psdi.mbo import MboConstants
from psdi.iface.mic import MicConstants
from java.sql import Statement
from java.sql import PreparedStatement
from java.sql import Connection
from java.sql import ResultSet
from java.util import HashMap

def beforeProcess(ctx):
    """Process PO data before it's saved to Maximo"""
    ponum = ctx.getData().getCurrentData("PONUM")
    siteid = ctx.getData().getCurrentData("SITEID")
    status = ctx.getData().getCurrentData("STATUS")
    vendor = ctx.getData().getCurrentData("VENDOR")
    
    whereclause = ("ponum='" + ponum + "' and siteid='" + siteid + 
                   "' and revisionnum = (select max(revisionnum) from po where ponum='" + 
                   ponum + "' and siteid='" + siteid + "')")
    
    if ponum is not None:
        # Check if vendor exists, call external service if not
        vendorSet = MXServer.getMXServer().getMboSet("COMPANIES", ctx.getUserInfo())
        vendorSet.setWhere("COMPANY = '" + vendor + "'")
        vendorSet.reset()
        if vendorSet.isEmpty():
            nvendor = vendor.split("_")[0]
            # Call external REST service to get vendor
            # callPSVendorService(nvendor, ctx)
        
        # Process PO lines
        poSet = MXServer.getMXServer().getMboSet("PO", ctx.getUserInfo())
        poSet.setWhere(whereclause)
        poSet.reset()
        
        polines = ctx.getData().getChildrenData("POLINE")
        i = 0
        if polines is not None:
            for value in polines:
                ctx.getData().setAsCurrent(polines, i)
                itemNum = ctx.getData().getCurrentData('INV_ITEM_ID')
                phyNature = ctx.getData().getCurrentData('PHYSICAL_NATURE')
                prNum = ctx.getData().getCurrentData('PRNUM')
                
                # Set line type based on item and physical nature
                if prNum is None:
                    ctx.getData().setCurrentDataNull('PRNUM')
                    ctx.getData().setCurrentDataNull('PRLINENUM')
                    if itemNum is not None and len(itemNum) > 0 and phyNature == 'G':
                        lnType = 'ITEM'
                    elif itemNum is not None and len(itemNum) > 0 and phyNature == 'S':
                        lnType = 'STDSERVICE'
                    elif itemNum is None and phyNature == 'G':
                        lnType = 'MATERIAL'
                    elif itemNum is None and phyNature == 'S':
                        lnType = 'SERVICE'
                    else:
                        lnType = 'MATERIAL'
                    ctx.getData().setCurrentData("LINETYPE", lnType)
                i += 1
        
        ctx.getData().setParentAsCurrent()
        
        # Handle status changes
        if (poSet.isEmpty() == False):
            poMbo = poSet.getMbo(0)
            if (status == "CLOSE" or status == "CAN"):
                ctx.getData().setCurrentData("STATUSIFACE", MicConstants.sYes)
                ctx.getData().setCurrentData("REVISIONNUM", poMbo.getString("REVISIONNUM"))
                ctx.getData().setCurrentData("NP_STATUSMEMO", "Status Change via interface")

# Call the beforeProcess function
beforeProcess(ctx)

scriptConfig="""{
    "autoscript": "OSIN.PSF_PO",
    "description": "PO CREATE/UPDATE from PS",
    "version": "",
    "active": true,
    "logLevel": "ERROR"
}"""
```

**Example 2: OSIN - JavaScript Script**

```javascript
/**
 * Integration Script - Object Structure In
 *
 * Launch Point: OSIN.STAMASSETDETAIL
 * Object Structure: STAMASSETDETAIL
 * Processing Point: Before MBO Data
 *
 * Author: Developer Name
 */

var ConversionUtil = Java.type("psdi.iface.mos.ConversionUtil");

function beforeMboData(ctx) {
    _ensureNonFutureNewReadingDate(ctx);
}

// Adjusts any NEWREADINGDATE value to account for device time discrepancies
function _ensureNonFutureNewReadingDate(ctx) {
    var processTable = ctx.processTable;
    if (processTable === "ASSETMETER") {
        var data = ctx.getData().getCurrentObject();
        if (data.isCurrentDataNull("NEWREADINGDATE")) return;

        var newReadingDate = data.getCurrentDataAsDate("NEWREADINGDATE");
        // Adjust the new reading date to handle device time discrepancies
        var nonFutureDate = ctx.invokeScript("STAUTOSCRIPT.DATEUTILS.LIB")
                              .ensureNonFutureDate(newReadingDate);
        data.setCurrentData("NEWREADINGDATE", 
                           ConversionUtil.dateToString(nonFutureDate));
    }
}

var scriptConfig = {
    "autoscript": "OSIN.STAMASSETDETAIL",
    "description": "Sharptree Asset Detail OS Inbound processing",
    "version": "1.0.3",
    "active": true,
    "logLevel": "ERROR"
};
```

---

### Object Structure Out (OSOUT) Scripts

**When it runs**: When processing outbound data via Object Structures before sending

**Use cases**:
- Transform data before sending
- Add calculated fields
- Override values based on conditions
- Format data for external systems

**Example: OSOUT - JavaScript Script**

```javascript
/**
 * Integration Script - Object Structure Out
 *
 * Launch Point: OSOUT.STAMASSETDETAIL
 * Object Structure: STAMASSETDETAIL
 * Processing Point: Override Values
 *
 * Author: Developer Name
 */

function overrideValues(ctx) {
    if (ctx.getMboName() == 'ASSET') {
        var meterSet = ctx.getMbo().getMboSet("ACTIVEASSETMETER");
        
        if (!meterSet.isEmpty()) {
            for (var i = 0; i < meterSet.count(); i++) {
                var meter = meterSet.getMbo(i);
                // Check if position is available, set if it is
                if (!meter.isNull("DMUENGINEPOS.POSITION")) {
                    meter.setValue("METER.DESCRIPTION", 
                                  meter.getString("METER.DESCRIPTION") + 
                                  ", Position " + 
                                  meter.getString("DMUENGINEPOS.POSITION"));
                }
            }
        }
    }
}

var scriptConfig = {
    "autoscript": "OSOUT.STAMASSETDETAIL",
    "description": "Add meter position 1.0.0",
    "version": "1.0.0",
    "active": true,
    "logLevel": "ERROR"
};
```

---

### Object Structure Action (OSACTION) Scripts

**When it runs**: When a custom action is executed on an Object Structure (typically via REST API)

**Use cases**:
- Create related records when action executes
- Perform custom business logic
- Process JSON request data
- Update multiple objects

**Example 1: OSACTION - Python Script**

```python
################
# Script:
# Integration Script - Object Structure Action
#
# Launch Point: OSACTION.MXAPIINSPRESULT.CREATEWO
# Object Structure: MXAPIINSPRESULT
# Action: CREATEWO
#
# Author: Developer Name
#
# Revision:
# Date        User                        Comment
# 2024-01-15  Developer Name              Initial creation - Create WO for items that require action
################

print "=============== EXECUTING CREATE WO SCRIPT ==============="

# Determine if inspection is planned (has work order)
planned = False
if (mbo.getString("REFERENCEOBJECT") == "WORKORDER" or 
    mbo.getString("REFERENCEOBJECT") == "WOACTIVITY"):
    planned = True
else:
    planned = False

# Iterate through inspection field results
resultSet = mbo.getMboSet("INSPFIELDRESULT")
for i in range(0, resultSet.count()):
    currentResult = resultSet.getMbo(i)
    
    # Check if result requires action
    requireActionSet = currentResult.getMboSet("INSPFIELDOPTIONACT")
    requireAction = False
    if requireActionSet.count() > 0:
        requireAction = True
    
    if requireAction:
        # Get question description
        questionDetailSet = currentResult.getMboSet("INSPQUESTION")
        desc = (questionDetailSet.getMbo(0).getString("description") + " = " + 
                currentResult.getString("TXTRESPONSE"))
        
        # For planned inspections, create follow-up WO
        if (planned and currentResult.getString("FUPOBJECT") == ""):
            if mbo.getString("PARENT") is not None:
                woSet = mbo.getMboSet("PARENTWO")
            else:
                woSet = mbo.getMboSet("WORKORDER")
            wo = woSet.getMbo(0)
            
            # Create follow-up work order
            newWO = wo.createWorkorder()
            
            # Set WO description and link to inspection
            newWOSet = mbo.getMboSet("$NewWO", "WORKORDER", 
                                     "wonum='" + newWO.getString("wonum") + 
                                     "' and siteid='" + newWO.getString("siteid") + "'")
            newWOSet.getMbo(0).setValue("description", desc)
            newWOSet.getMbo(0).setValue("location", mbo.getString("location"))
            newWOSet.getMbo(0).setValue("assetnum", mbo.getString("asset"))
            
            # Link result to work order
            currentResult.setValue("FUPOBJECT", "WORKORDER")
            currentResult.setValue("FUPOBJECTID", newWO.getString("wonum"))
            currentResult.setValue("DISPLAYMESSAGE", 
                                  "Workorder " + str(newWO.getString("wonum")) + " created")
            newWOSet.save()
        
        # For unplanned inspections, create new WO with tasks
        if (planned == False and currentResult.getString("FUPOBJECT") == ""):
            woSet = mbo.getMboSet("WORKORDER")
            if mbo.getString("FUPOBJECT") == "":
                newWO = woSet.add()
                newWO.setValue("Description", 
                              "Follow Up Work Order for Inspection " + 
                              str(mbo.getString("resultnum")))
                newWO.setValue("location", mbo.getString("location"))
                newWO.setValue("assetnum", mbo.getString("asset"))
                mbo.setValue("FUPOBJECT", "WORKORDER")
                mbo.setValue("FUPOBJECTID", newWO.getString("wonum"))
                mbo.setValue("DISPLAYMESSAGE", 
                            "Workorder " + str(newWO.getString("wonum")) + " created")
                print "Created WO " + str(newWO.getString("wonum"))
                woSet.save()
            
            # Add task to the work order
            woSet = mbo.getMboSet("FUPWORKORDER")
            newTask = woSet.getMbo(0).getMboSet("WOACTIVITY").add()
            newTask.setValue("PARENT", mbo.getString("FUPOBJECTID"))
            print "Created Task " + str(newTask.getString("taskid"))
            newTask.setValue("description", desc)
            currentResult.setValue("FUPOBJECT", "WORKORDER")
            currentResult.setValue("FUPOBJECTID", newTask.getString("wonum"))
            currentResult.setValue("DISPLAYMESSAGE", 
                                  "Work Order " + mbo.getString("FUPOBJECTID") + 
                                  " Task " + str(newTask.getString("taskid")) + " created")
            woSet.save()

resultSet.save()
print "=============== END CREATE WO SCRIPT ==============="

scriptConfig="""{
    "autoscript": "OSACTION.MXAPIINSPRESULT.CREATEWO",
    "description": "Create WO for items that require action",
    "version": "1.0",
    "active": true,
    "logLevel": "ERROR"
}"""
```

**Example 2: OSACTION - JavaScript Script with JSON Request**

```javascript
/**
 * Integration Script - Object Structure Action
 *
 * Launch Point: OSACTION.STAMINVBALANCE.STAMADJUSTBALANCE
 * Object Structure: STAMINVBALANCE
 * Action: STAMADJUSTBALANCE
 *
 * Author: Developer Name
 * 
 * Sample JSON request:
 * {
 *     "newcurbal": 500.0,
 *     "memo": "This is the adjustment memo"
 * }
 */

var MXApplicationException = Java.type("psdi.util.MXApplicationException");

main();

function main() {
    if (requestBody) {
        var adjustmentDetails = JSON.parse(requestBody);
        recordBalanceAdjustment(adjustmentDetails);
    } else {
        service.log_error("Unable to record inventory balance adjustment because the request was empty.");
        throwMissingNewcurbalError();
    }
}

function recordBalanceAdjustment(adjustmentDetails) {
    // Ensure we have a newcurbal value
    if (!adjustmentDetails.newcurbal) {
        service.log_error("Unable to record inventory balance adjustment because no newcurbal was provided.");
        throwMissingNewcurbalError();
    }

    mbo.setValue("NEWCURBAL", adjustmentDetails.newcurbal);

    var invTrans = mbo.adjustCurrentBalance(adjustmentDetails.newcurbal);

    if (adjustmentDetails.memo) {
        invTrans.setValue("MEMO", adjustmentDetails.memo);
    }
}

function throwMissingNewcurbalError() {
    var Array = Java.type("java.lang.Object[]");
    var params = new Array(1);
    params[0] = "newcurbal";
    throw new MXApplicationException("system", "nullvalue", params);
}

var scriptConfig = {
    "autoscript": "OSACTION.STAMINVBALANCE.STAMADJUSTBALANCE",
    "description": "Record inventory balance adjustment",
    "version": "1.0.1",
    "active": true,
    "logLevel": "ERROR"
};
```

---

### Invoke Channel Scripts

**When it runs**: During invoke channel operations (query, sync)

**Use cases**:
- Transform incoming data from external systems
- Validate data before processing
- Convert data formats
- Skip transactions based on conditions

**Example: Invoke Channel - External Exit In**

```python
################
# Script:
# Integration Script - Invoke Channel
#
# Launch Point: SYNC.PSF_UOMCONV_IN.EXTEXIT.IN
# Invoke Channel: PSF_UOMCONV_IN
# Processing Point: External Exit In
#
# Author: Vamsi
# Description: UOM conversion interface - flip from/to units if conversion_rate < 1
################

from psdi.mbo import Mbo
from psdi.mbo import MboSetRemote

# Break data into individual records
erData.breakData()
osSize = erData.getSize()

for i in range(osSize):
    # If conversion rate is less than 1, flip the units
    if (erData.getCurrentDataAsDouble("CONVERSION") < 1.00):
        fromUOM = erData.getCurrentData("FROMMEASUREUNIT")
        toUOM = erData.getCurrentData("TOMEASUREUNIT")
        conversion = erData.getCurrentDataAsDouble("CONVERSION")
        
        # Flip the units
        erData.setCurrentData("FROMMEASUREUNIT", toUOM)
        erData.setCurrentData("TOMEASUREUNIT", fromUOM)
        # Set conversion to 1/conversion_rate
        erData.setCurrentData("CONVERSION", 1 / conversion)
    
    erData.moveToNextObjectStructure()

scriptConfig="""{
    "autoscript": "SYNC.PSF_UOMCONV_IN.EXTEXIT.IN",
    "description": "Set Conversion rate",
    "version": "",
    "active": true,
    "logLevel": "ERROR"
}"""
```

---

**Key Patterns for Integration Scripts**:

### Publish Channel Scripts
- Use `irData` object to access integration data
- Use `irData.getCurrentData()` to get field values
- Use `irData.setCurrentData()` to set field values
- Use `irData.breakData()` to process individual records
- Use `irData.moveToNextObjectStructure()` to move to next record
- Set `errorgroup` and `errorkey` to skip transactions
- Set `AUDIT_ACTN` to 'A' (Add), 'C' (Change), 'D' (Delete), or 'U' (Update)

### Object Structure In (OSIN) Scripts
- Use `ctx` (context) object to access integration context
- Use `ctx.getData()` to access integration data
- Use `ctx.getUserInfo()` to get user information
- Use `ctx.getMbo()` to access MBO objects
- Use `ctx.skipTxn()` to skip transaction
- Use `ctx.getData().getCurrentData()` to get field values
- Use `ctx.getData().setCurrentData()` to set field values
- Use `ctx.getData().getChildrenData()` to access child records

### Object Structure Out (OSOUT) Scripts
- Use `ctx` (context) object
- Use `ctx.getMboName()` to get current MBO name
- Use `ctx.getMbo()` to access MBO objects
- Override values using `overrideValues(ctx)` function

### Object Structure Action (OSACTION) Scripts
- Use `mbo` object to access current MBO
- Use `requestBody` to access JSON request data (JavaScript)
- Parse JSON with `JSON.parse(requestBody)`
- Create related records using `mbo.getMboSet()`
- Use standard MBO operations (add, save, etc.)

### Invoke Channel Scripts
- Use `erData` object for incoming data
- Use `erData.breakData()` to process individual records
- Use `erData.getCurrentData()` and `erData.setCurrentData()`
- Use `erData.moveToNextObjectStructure()` to move to next record

---

## Summary of All Launch Point Types

| Launch Point Type | Event | When It Runs | Java Method | Common Use Cases |
|------------------|-------|--------------|-------------|------------------|
| **initializeValue** | Initialize | When MBO is loaded | `init()` | Set defaults, initialize from owner |
| **beforeSave** | Before Save | Before save to DB | `appValidate()`, `save()` before `super.save()` | Validation, auto-populate |
| **afterSave** | After Save | After save to DB | `save()` after `super.save()` | Create related records, trigger saves |
| **afterCommit** | After Commit | After transaction committed | `save()` with notifications | Notifications, external systems |
| **afterAdd** | After Add | After MBO added to set | `add()` | Set flags, initialize after add |
| **beforeDelete** | Before Delete | Before MBO deleted | `canDelete()` | Validate before deletion |
| **validateApplication** | Validation | During object validation | `appValidate()` (alt) | Cross-field validation |
| **allowObjectCreation** | Allow Creation | Before MBO created | N/A | Prevent creation, set defaults |
| **allowObjectDeletion** | Allow Deletion | Before MBO deleted | `canDelete()` (alt) | Prevent deletion, cleanup |
| **FLD.VALIDATE** | Field Validation | When field is validated | N/A | Field value validation |
| **FLD.ACTION** | Field Action | When field changes | N/A | Auto-populate related fields |
| **FLD.INIT** | Field Init | When field is initialized | N/A | Set default field values |
| **FLD.LIST** | Field List | When list is retrieved | N/A | Filter domain values |
| **ACTION.[NAME]** | Custom Action | When action executes | Custom methods | Custom business logic |
| **CRON** | Scheduled | On schedule | N/A | Batch processing, sync |
| **PUBLISH** | Publish Channel | Before publishing | N/A | Transform data, set audit flags |
| **OSIN** | Object Structure In | When processing inbound data | N/A | Validate, transform incoming data |
| **OSOUT** | Object Structure Out | When processing outbound data | N/A | Transform data before sending |
| **OSACTION** | Object Structure Action | When action executes | N/A | Custom actions via REST API |
| **SYNC/QUERY** | Invoke Channel | During invoke operations | N/A | Transform, validate invoke data |

---

## Best Practices Summary

1. **Always use MboConstants flags** - Never use numeric constants like `2L`, `11L`
2. **Analyze Java methods to determine event timing** - Use the mapping table to convert correctly
3. **Use standard header template** - Include all required information
4. **Close MBO sets** - Always close sets created with `MXServer.getMXServer().getMboSet()`
5. **Use proper error handling** - Use `service.error()` for validation errors
6. **Check interactive mode** - Use `if interactive:` for UI-only logic
7. **Use MBO state flags** - Check `onadd`, `onupdate`, `ondelete` when needed
8. **Set specific event timing** - Always specify beforeSave/afterSave/afterCommit/afterAdd/beforeDelete based on Java code
9. **Log appropriately** - Use logging for cron tasks and complex operations
10. **Follow naming conventions** - Use standard naming from `NAMING_CONVENTIONS.md`

---

## Quick Reference: Common Patterns

### Setting Values
```python
mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

### Field Flags
```python
mbo.setFieldFlag("FIELD", MboConstants.READONLY, True)
mbo.setFieldFlag("FIELD", MboConstants.REQUIRED, True)
```

### Error Handling
```python
service.error('Field Name', 'error message')
```

### Accessing Owner
```python
owner = mbo.getOwner()
if owner and owner.isBasedOn("SR"):
    value = owner.getString("FIELD")
```

### Accessing Related Sets
```python
mboSet = mbo.getMboSet("RELATIONSHIPNAME")
mboSet.reset()
if not mboSet.isEmpty():
    item = mboSet.getMbo(0)
```

### Looping Through Sets
```python
count = mboSet.count()
for i in range(count):
    item = mboSet.getMbo(i)
    # Process item
```

---

**End of Reference**

For more detailed patterns, see:
- `maximo_script_patterns_reference.md` - Comprehensive patterns
- `AGENT_PROMPTS.md` - Prompt templates for creating scripts
- `NAMING_CONVENTIONS.md` - Naming standards
- `script_header_template.py` - Header template

