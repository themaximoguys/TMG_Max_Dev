# MAXIMO AUTOMATION SCRIPT PATTERNS REFERENCE

This document contains comprehensive syntax patterns and code templates for building Maximo automation scripts based on analysis of existing scripts.

**Based on IBM Maximo Automation Script documentation and best practices. This document is generic and can be used across any Maximo project.**

## Official IBM Documentation

**⚠️ IMPORTANT**: Always refer to the official IBM Maximo Automation Script documentation for authoritative information:

- **Main Documentation**: [IBM Maximo Automation Script Documentation](https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/)
- **Components Reference**: [Script Components](https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/introduction/components)
- **Core Concepts**: [Service Variable, MBO Constants, Errors](https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/core-concepts/service-variable)
- **Object Scripts**: [Object Launch Points](https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/object-scripts/object-launchpoint)
- **Attribute Scripts**: [Attribute Launch Points](https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/attribute-scripts)
- **Best Practices**: [Scripting Best Practices](https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/best-practices)

**Note**: This local reference complements the official IBM documentation and provides generic patterns based on IBM best practices and production implementations.

---

## Table of Contents

1. [Standard Script Header Template](#standard-script-header-template)
2. [Common Imports](#common-imports)
3. [MboConstants - Flag Usage and Combinations](#mboconstants---flag-usage-and-combinations)
4. [Error Handling Patterns](#error-handling-patterns)
5. [Warning Patterns](#warning-patterns)
6. [Relationship Calling Patterns](#relationship-calling-patterns)
7. [Looping Through MBO Sets](#looping-through-mbo-sets)
8. [Setting Values](#setting-values)
9. [Field Types Handling](#field-types-handling)
10. [Field Flags and Readonly](#field-flags-and-readonly)
11. [Exception Handling](#exception-handling)
12. [Date and Time Handling](#date-and-time-handling)
13. [MBO Operations](#mbo-operations)
14. [User and Session Information](#user-and-session-information)
15. [Database Operations](#database-operations)
16. [Logging Patterns](#logging-patterns)
17. [Validation Patterns](#validation-patterns)
18. [Action Patterns](#action-patterns)
19. [Initialization Patterns](#initialization-patterns)
20. [Save Patterns (Before/After)](#save-patterns-beforeafter)
21. [Complex Operations Patterns](#complex-operations-patterns)
22. [Script Configuration Template](#script-configuration-template)
23. [Best Practices](#best-practices)

---

## Standard Script Header Template

**⚠️ IMPORTANT: Always include this header template at the beginning of every new Maximo automation script!**

This standardized header ensures consistent documentation, revision tracking, and maintainability across all scripts.

**Note**: Also follow the standard naming conventions defined in `NAMING_CONVENTIONS.md` when naming your script files.

### Standard Header Format

```python
################
# Script:
# [Launch Point Type]
#
# Launch Point: [Launch_Point_Name]
# Object: [OBJECT_NAME]
#
# Author: [Author Name]
#
# Revision:
# Date        User                        Comment
# [YYYY-MM-DD] [User Name]                [Initial creation or change description]
# [YYYY-MM-DD] [User Name]                [Change description]
################
```

### Header Template Examples

#### Example 1: Object Launch Point

```python
################
# Script:
# Object Launch Point
#
# Launch Point: WORKORDER.OBJ.SAVE.BEFORE
# Object: WORKORDER
#
# Author: Developer Name
#
# Revision:
# Date        User                        Comment
# 2024-01-15  Developer Name              Initial creation - Validate work order status before save
# 2024-03-20  Developer Name              Added validation for required fields
################

from psdi.mbo import MboConstants
from psdi.server import MXServer

# Script code here...
```

#### Example 2: Attribute Launch Point

```python
################
# Script:
# Attribute Launch Point
#
# Launch Point: WORKORDER.FLD.STATUS.VALIDATE
# Object: WORKORDER
# Attribute: STATUS
#
# Author: Developer Name
#
# Revision:
# Date        User                        Comment
# 2024-01-15  Developer Name              Initial creation - Validate status transitions
################

from psdi.mbo import MboConstants

# Script code here...
```

#### Example 3: Action Launch Point

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
# 2024-01-15  Developer Name              Initial creation - Duplicate work order with related records
################

from psdi.mbo import MboConstants
from psdi.server import MXServer

# Script code here...
```

### Header Template Fields

| Field | Description | Example |
|-------|-------------|---------|
| **Script** | Script name or identifier | `WORKORDER.OBJ.SAVE.BEFORE` |
| **Launch Point Type** | Type of launch point | `Object Launch Point`, `Attribute Launch Point`, `Action Launch Point` |
| **Launch Point** | Full launch point name | `WORKORDER.OBJ.SAVE.BEFORE` |
| **Object** | Maximo object name | `WORKORDER`, `ASSET`, `PO` |
| **Attribute** | Field/attribute name (for Attribute launch points only) | `STATUS`, `ITEMNUM` |
| **Action** | Action name (for Action launch points only) | `DUPLICATE`, `APPROVE` |
| **Author** | Script author name | `Developer Name` |
| **Revision** | Revision history table | See below |

### Revision History Format

The revision history should follow this format:

```python
# Revision:
# Date        User                        Comment
# 2024-01-15  Developer Name              Initial creation - Brief description
# 2024-03-20  Developer Name              Added validation for required fields
# 2024-05-10  Another Developer           Fixed bug in status validation
```

**Revision Guidelines:**
- Use YYYY-MM-DD format for dates (ISO 8601 standard)
- Include full user name or developer name
- Provide clear, descriptive comments about the change
- List revisions in chronological order (oldest to newest)
- Always document the initial creation

### Complete Header Template (Copy and Use)

```python
################
# Script:
# [Launch Point Type: Object/Attribute/Action]
#
# Launch Point: [FULL_LAUNCH_POINT_NAME]
# Object: [OBJECT_NAME]
# [Attribute: [ATTRIBUTE_NAME]]  # Only for Attribute launch points
# [Action: [ACTION_NAME]]        # Only for Action launch points
#
# Author: [Your Name]
#
# Revision:
# Date        User                        Comment
# [YYYY-MM-DD] [Your Name]                 Initial creation - [Brief description]
################

from psdi.mbo import MboConstants
from psdi.server import MXServer
# Add other imports as needed
```

### Best Practices for Headers

1. **Always include the header** - Every script should start with this header
2. **Keep it current** - Update revision history when making changes
3. **Be descriptive** - Use clear, descriptive comments in revision history
4. **Use consistent format** - Follow the template exactly for consistency
5. **Document all changes** - Every modification should be logged in revision history
6. **Include relevant details** - Add Redmine ticket numbers, DR numbers, or other references if applicable

### Header with Additional Information

For scripts with additional context (Redmine tickets, DR numbers, etc.), you can add them:

```python
################
# Script:
# Object Launch Point
#
# Launch Point: WORKORDER.OBJ.SAVE.BEFORE
# Object: WORKORDER
#
# Author: Developer Name
#
# Redmine: FEA-2423
# DR: 3176
#
# Revision:
# Date        User                        Comment
# 2024-01-15  Developer Name              Initial creation - Validate work order status
# 2024-03-20  Developer Name              Added validation for required fields (DR 3176)
################
```

---

## Common Imports

**Always import MboConstants** - This is critical for proper flag usage in Maximo scripts:

```python
from psdi.mbo import Mbo
from psdi.mbo import MboConstants
from psdi.mbo import MboSetRemote
from psdi.server import MXServer
from psdi.security import UserInfo
from psdi.util.logging import MXLoggerFactory
from psdi.common.context import UIContext
from psdi.webclient.system.controller import WebClientEvent
from java.util import Calendar
from java.util import Date
from java.text import SimpleDateFormat
from java.sql import Statement
from java.sql import PreparedStatement
from java.sql import Connection
from java.sql import ResultSet
from java.lang import StringBuilder
```

---

## MboConstants - Flag Usage and Combinations

### ⚠️ IMPORTANT: Always Use MboConstants, Never Numeric Values

**NEVER use numeric constants like `2L`, `11L`, etc. Always use MboConstants flags!**

### Common MboConstants Flags

```python
from psdi.mbo import MboConstants

# Common flags:
MboConstants.NOACCESSCHECK      # Skip access control checks
MboConstants.NOVALIDATION       # Skip validation
MboConstants.NOACTION           # Skip action scripts
MboConstants.READONLY           # Set field/MBO to readonly
MboConstants.REQUIRED           # Set field as required
MboConstants.NOCHECK           # Skip check constraints
```

### Flag Combinations (Bitwise OR - |)

**Always combine flags using the pipe operator (|):**

```python
# Single flag
mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK)

# Two flags combined
mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# Three flags combined
mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION | MboConstants.NOACTION)

# Most common combination (skip validation and access checks)
mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

### Common Flag Combination Patterns

```python
# Pattern 1: Skip validation and access checks (MOST COMMON)
mbo.setValue("FIELDNAME", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# Pattern 2: Skip validation, access checks, and actions
mbo.setValue("FIELDNAME", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION | MboConstants.NOACTION)

# Pattern 3: Skip only validation
mbo.setValue("FIELDNAME", value, MboConstants.NOVALIDATION)

# Pattern 4: Skip only access checks
mbo.setValue("FIELDNAME", value, MboConstants.NOACCESSCHECK)

# Pattern 5: Set field flags (readonly, required)
mbo.setFieldFlag("FIELDNAME", MboConstants.READONLY, True)
mbo.setFieldFlag("FIELDNAME", MboConstants.REQUIRED, True)
```

### Examples: Converting from Numeric to Constants

**❌ WRONG - Don't use numeric values:**
```python
historySet.add(2L)  # BAD - using numeric constant
mbo.setValue("FIELD", value, 2L)  # BAD - using numeric constant
```

**✅ CORRECT - Use MboConstants:**
```python
# For adding to MBO sets with position, use proper constants
historySet.add(2)  # Use regular integer, not 2L

# For setValue flags, always use MboConstants
mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

### Flag Usage in Different Contexts

#### Setting Values
```python
# Standard pattern for setValue
mbo.setValue("FIELDNAME", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

#### Field Flags
```python
# Set readonly
mbo.setFieldFlag("FIELDNAME", MboConstants.READONLY, True)

# Remove readonly
mbo.setFieldFlag("FIELDNAME", MboConstants.READONLY, False)

# Set required
mbo.setFieldFlag("FIELDNAME", MboConstants.REQUIRED, True)
```

#### MBO Flags
```python
# Set entire MBO readonly
mbo.setFlag(MboConstants.READONLY, True)

# Remove readonly
mbo.setFlag(MboConstants.READONLY, False)
```

### Best Practices for Flag Usage

1. **Always import MboConstants at the top of your script**
   ```python
   from psdi.mbo import MboConstants
   ```

2. **Use descriptive flag combinations**
   ```python
   # Good - clear intent
   flags = MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION
   mbo.setValue("FIELD", value, flags)
   ```

3. **Most common combination: NOACCESSCHECK | NOVALIDATION**
   ```python
   # This is the most frequently used pattern
   mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
   ```

4. **Never use numeric constants**
   ```python
   # ❌ WRONG
   mbo.setValue("FIELD", value, 2L)
   
   # ✅ CORRECT
   mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
   ```

---

## Error Handling Patterns

### Pattern 1: Custom setError Function

```python
def setError(p0, p1, p2):
    """
    Custom error function for Maximo automation scripts.
    
    Args:
        p0 (str): First error message parameter
        p1 (str): Second error message parameter
        p2 (str): Third error message parameter
    """
    global errorkey, errorgroup, params
    errorkey = 'InfoParameters3'
    errorgroup = 'AutoScript'
    params = [p0, p1, p2]

# Usage Example:
if mbo.isNull("ITEMNUM"):
    setError('Please choose', 'an item number', 'before proceeding')
    return
```

### Pattern 2: Service Error Method

```python
service.error('Field Name', 'error message')
service.error('SR', 'obsmatnew', [status])
service.error("Error when DELETE", " Cannot delete the CREW: '"+v_crew+"' Associated with an ACTIVE PM: '"+v_pmnum+"'")
```

### Pattern 3: Service Error with Status Check

```python
if status in ('IMREVIEW','FMREVIEW','APPR','RESOLVED'):
    service.error("SR","obsmatnew",[status])
```

### Pattern 4: Conditional Error with Field Validation

```python
if mbo.isNull("TOTALCOST"):
    service.error('Total Cost', 'can not be empty!')
elif not totalCost > 0:
    service.error('Total Cost', 'must be greater than zero!')
```

---

## Warning Patterns

### Pattern 1: Service Warning

```python
service.warning('Warning Message')
```

### Pattern 2: Application Warning Exception

```python
from psdi.util import MXApplicationWarningException
raise MXApplicationWarningException('Warning message')
```

---

## Relationship Calling Patterns

### Pattern 1: Standard Relationship (getMboSet)

```python
mboSet = mbo.getMboSet("RELATIONSHIPNAME")

# Example:
woSet = mbo.getMboSet("WORKORDER")
assetSet = mbo.getMboSet("ASSET")
polineSet = mbo.getMboSet("POLINE")
```

### Pattern 2: Relationship with Where Clause

```python
mboSet = mbo.getMboSet("RELATIONSHIPNAME")
mboSet.setWhere("WHERE_CLAUSE")
mboSet.reset()

# Example:
activePMSet = mbo.getMboSet("ACTIVEPM")
activePMSet.setWhere("status = 'ACTIVE'")
activePMSet.reset()
```

### Pattern 3: Temporary Relationship (using $ prefix)

```python
mboSet = mbo.getMboSet("$TEMPRELATIONSHIP", "OBJECTNAME", "WHERE_CLAUSE")

# Example:
maxRevSet = mbo.getMboSet("$MAXACTLOGSET", "ACTIVITYLOG", 
                          "dept = '" + dept + "' and SHIFT = '" + origShift + 
                          "' and SHIFTDATE= to_date('" + vCurrentDate + "','mm/dd/yyyy')")
newWarrantyClaimSet = mbo.getMboSet("$PLUSTCLAIM", "PLUSTCLAIM", "1=0")
relatedSet = mbo.getMboSet("$RELATEDUOR$", "RELATEDRECORD", 
                           "CLASS='UORMASTER' AND RECORDKEY='" + ticketId + "'")
```

### Pattern 4: Relationship from MXServer

```python
mxServer = MXServer.getMXServer()
userInfo = mbo.getThisMboSet().getUserInfo()
mboSet = mxServer.getMboSet("OBJECTNAME", userInfo)
mboSet.setWhere("WHERE_CLAUSE")

# Example:
invSet = mxServer.getMboSet("INVENTORY", userInfo)
whereClause = "ITEMNUM = '" + itemNum + "' and SITEID = 'SITE1'"
invSet.setWhere(whereClause)
```

### Pattern 5: Relationship from Owner

```python
owner = mbo.getOwner()
ownerSet = owner.getMboSet("RELATIONSHIPNAME")

# Example:
ticket = mbo.getOwner()
if ticket and ticket.isBasedOn("SR"):
    status = ticket.getString("STATUS")
```

---

## Looping Through MBO Sets

### Pattern 1: Loop with count() and range()

```python
mboSet = mbo.getMboSet("RELATIONSHIPNAME")
mboSet.reset()
count = mboSet.count()
for i in range(count):
    mboItem = mboSet.getMbo(i)
    # Process mboItem
    value = mboItem.getString("FIELDNAME")
```

### Pattern 2: Loop with moveFirst() and moveNext()

```python
mboSet = mbo.getMboSet("RELATIONSHIPNAME")
mbo = mboSet.moveFirst()
while mbo:
    # Process mbo
    value = mbo.getString("FIELDNAME")
    mbo = mboSet.moveNext()
```

### Pattern 3: Loop with moveFirst() and check

```python
polineSet = mbo.getMboSet("POLINE")
poline = polineSet.moveFirst()
while poline:
    # Process poline
    status = poline.getString("PL1")
    poline.setValue("RECEIPTSCOMPLETE", True, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
    poline = polineSet.moveNext()
```

### Pattern 4: Loop with isEmpty() check

```python
mboSet = mbo.getMboSet("RELATIONSHIPNAME")
if not mboSet.isEmpty():
    mboItem = mboSet.getMbo(0)
    value = mboItem.getString("FIELDNAME")
```

### Pattern 5: Loop with count() check before processing

```python
dupActLogSet = dupMbo.getMboSet("WO2ACTLOG")
if dupActLogSet.count() > 0:
    dupActLogMbo = dupActLogSet.getMbo(0)
    # Process dupActLogMbo
```

---

## Setting Values

### Pattern 1: Basic setValue

```python
mbo.setValue("FIELDNAME", value)
```

### Pattern 2: setValue with Constants (NOACCESSCHECK, NOVALIDATION)

**⚠️ Always use MboConstants flags, never numeric values like `2L` or `11L`!**

```python
# Standard pattern - Most common combination
mbo.setValue("FIELDNAME", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# Examples:
asset.setValue('SUBSTATUS', subStatus, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
asset.setValue('STATUS', subStatus, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
mbo.setValue("GLCREDITACCT", glCredit, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# Three flags combined (skip validation, access checks, and actions)
mbo.setValue("FIELDNAME", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION | MboConstants.NOACTION)

# Single flag - skip only validation
mbo.setValue("FIELDNAME", value, MboConstants.NOVALIDATION)

# Single flag - skip only access checks
mbo.setValue("FIELDNAME", value, MboConstants.NOACCESSCHECK)
```

**❌ WRONG - Never use numeric constants:**
```python
mbo.setValue("FIELDNAME", value, 2L)  # BAD - Don't do this!
mbo.setValue("FIELDNAME", value, 11L)  # BAD - Don't do this!
```

### Pattern 3: setValueNull

```python
mbo.setValueNull("FIELDNAME")

# Example:
mbo.setValueNull("STOREROOM")
mbo.setValueNull("GLDEBITACCT")
mbo.setValueNull("BINNUM")
```

### Pattern 4: setValue with Previous Value

```python
previousValue = mbo.getMboValue("FIELDNAME").getPreviousValue().asString()
newValue = calculateNewValue(previousValue)
mbo.setValue("FIELDNAME", newValue)
```

### Pattern 5: setValue with Date

```python
from java.util import Date
today = Date()
mbo.setValue("CHANGEDATE", today)
mbo.setValue("SHIFTDATE", today)
```

### Pattern 6: setValue with Calculated Value

```python
calculatedValue = field1 * field2
# Always use MboConstants flags for calculated fields
mbo.setValue("CALCULATEDFIELD", calculatedValue, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

---

## Field Types Handling

### Pattern 1: String Field

```python
value = mbo.getString("FIELDNAME")
mbo.setValue("FIELDNAME", "string_value")
```

### Pattern 2: Integer Field

```python
value = mbo.getInt("FIELDNAME")
mbo.setValue("FIELDNAME", 123)
```

### Pattern 3: Long Field

```python
value = mbo.getLong("FIELDNAME")
mbo.setValue("FIELDNAME", 123456L)
```

### Pattern 4: Double/Float Field

```python
value = mbo.getDouble("FIELDNAME")
mbo.setValue("FIELDNAME", 123.45)
```

### Pattern 5: Boolean Field

```python
value = mbo.getBoolean("FIELDNAME")
mbo.setValue("FIELDNAME", True)
mbo.setValue("FIELDNAME", False)
mbo.setValue("FIELDNAME", 1)  # True
mbo.setValue("FIELDNAME", 0)  # False
```

### Pattern 6: Date Field

```python
from java.util import Date
today = Date()
dateValue = mbo.getDate("FIELDNAME")
mbo.setValue("FIELDNAME", today)
```

### Pattern 7: DateTime Field

```python
from java.util import Calendar
cal = Calendar.getInstance()
mbo.setValue("DATETIMEFIELD", cal.getTime())
```

### Pattern 8: Check if Null

```python
if mbo.isNull("FIELDNAME"):
    # Handle null case
    mbo.setValue("FIELDNAME", defaultValue)
```

### Pattern 9: Check if Modified

```python
if mbo.isModified("FIELDNAME"):
    # Handle modified case
    previousValue = mbo.getMboValue("FIELDNAME").getPreviousValue().asString()
```

---

## Field Flags and Readonly

### Pattern 1: Set Field Readonly

```python
# Use True/False boolean values, not 1/0
mbo.setFieldFlag("FIELDNAME", MboConstants.READONLY, True)

# Example:
mbo.setFieldFlag("CHECKED", MboConstants.READONLY, True)  # Use True, not 1
```

**Note:** Use `True`/`False` boolean values, not `1`/`0` for boolean parameters.

### Pattern 2: Remove Field Readonly

```python
mbo.setFieldFlag("FIELDNAME", MboConstants.READONLY, False)

# Example:
mbo.setFieldFlag("MINLEVEL", MboConstants.READONLY, False)
```

### Pattern 3: Set Entire MBO Readonly

```python
mbo.setFlag(MboConstants.READONLY, True)

# Example:
mbo.setFlag(MboConstants.READONLY, True)
```

### Pattern 4: Set Required Field

```python
mbo.setFieldFlag("FIELDNAME", MboConstants.REQUIRED, True)
```

---

## Exception Handling

### Pattern 1: Try-Except Block

```python
try:
    # Code that might raise exception
    value = mbo.getString("FIELDNAME")
except Exception, e:
    # Handle exception
    service.error('Error', 'An error occurred: ' + str(e))
```

### Pattern 2: Try-Except with Specific Handling

```python
try:
    # Code block
    result = performOperation()
except Exception, e:
    logger.error("Error in operation: " + str(e))
    service.error('Operation', 'failed')
```

### Pattern 3: Raise Exception for Testing

```python
raise Exception("Test exception message")
```

---

## Date and Time Handling

### Pattern 1: Get Current Date

```python
from java.util import Date
today = Date()

# Or using MXServer:
mxServer = MXServer.getMXServer()
today = mxServer.getDate()
```

### Pattern 2: Format Date

```python
from java.text import SimpleDateFormat
today = Date()
vCurrentDate = SimpleDateFormat("MM/dd/yyyy").format(today)
```

### Pattern 3: Use Date in Where Clause

```python
vCurrentDate = SimpleDateFormat("MM/dd/yyyy").format(today)
whereClause = "SHIFTDATE = to_date('" + vCurrentDate + "','mm/dd/yyyy')"
```

### Pattern 4: Calendar Operations

```python
from java.util import Calendar
cal = Calendar.getInstance()
mbo.setValue("ENTERDATE", cal.getTime())
```

---

## MBO Operations

### Pattern 1: Get Owner

```python
owner = mbo.getOwner()
ownerValue = owner.getString("FIELDNAME")
```

### Pattern 2: Check Owner Type

```python
owner = mbo.getOwner()
if owner and owner.isBasedOn("SR"):
    # Process SR owner
    status = owner.getString("STATUS")
```

### Pattern 3: Duplicate MBO

```python
dupMbo = mbo.duplicate()
dupMbo.setValue("FIELDNAME", "new_value")
```

### Pattern 4: Add New MBO to Set

```python
mboSet = mbo.getMboSet("RELATIONSHIPNAME")
newMbo = mboSet.add()
newMbo.setValue("FIELDNAME", value)
```

### Pattern 5: Add New MBO with Position

```python
historySet = asset.getMboSet("PLUSTASSETSTHIST")
newHistory = historySet.add(2)  # Add at position 2 (use regular integer, not 2L)
# Note: Position is just an integer index, not a flag constant
```

### Pattern 6: Get MBO from Set

```python
mboSet = mbo.getMboSet("RELATIONSHIPNAME")
mboItem = mboSet.getMbo(0)  # Get first MBO
value = mboItem.getString("FIELDNAME")
```

### Pattern 7: Close MBO Set

```python
mboSet.close()

# Example:
hasAsset.close()
woMboSet.close()
```

### Pattern 8: Save MBO Set

```python
mboSet.save()

# Example:
dupActLogSet.save()
historySet.save()
```

---

## User and Session Information

### Pattern 1: Get User Info

```python
userInfo = mbo.getThisMboSet().getUserInfo()

# Or using MXServer:
mxServer = MXServer.getMXServer()
userInfo = MXServer.getMXServer().getSystemUserInfo()
```

### Pattern 2: Get Current User

```python
currentUser = user  # Built-in variable
```

### Pattern 3: Check User in Group

```python
def userInGroup(grouplist):
    guSet = MXServer.getMXServer().getMboSet("GROUPUSER", mbo.getUserInfo())
    guSet.setWhere("userid='" + user + "' and groupname in (" + grouplist + ")")
    if guSet.isEmpty():
        return False
    return True
```

### Pattern 4: Check Interactive Mode

```python
if interactive:
    # Code runs only in interactive mode
    service.error('Error', 'message')
```

### Pattern 5: Get Application Name

```python
appName = mbo.getThisMboSet().getParentApp()
app = app  # Built-in variable for current application
```

### Pattern 6: Web Client Session

```python
from psdi.webclient.system.controller import WebClientEvent
wcs = service.webclientsession()
if wcs is not None:
    newEvent = WebClientEvent("changeapp", wcs.getCurrentApp().getId(), 
                               "APPNAME", None, None, None, id, wcs)
    wcs.queueEvent(newEvent)
```

### Pattern 7: UIContext for Web Client

```python
from psdi.common.context import UIContext
context = UIContext.getCurrentContext()
if context is not None:
    wcs = context.getWebClientSession()
    if wcs is not None:
        databean = wcs.getDataBean("appname")
        if databean:
            databean.refreshTable()
```

---

## Database Operations

### Pattern 1: Direct SQL Query

```python
from java.sql import Statement
from java.sql import ResultSet
mxServer = MXServer.getMXServer()
dbm = mxServer.getDBManager()
conKey = userInfo.getConnectionKey()
con = dbm.getConnection(conKey)
stmt = con.createStatement()
query = "SELECT nvl(sum(quantity),0) * -1 dissue FROM matusetrans WHERE itemnum = '" + itemNum + "'"
rs = stmt.executeQuery(query)
rs.next()
value = rs.getDouble("dissue")
stmt.close()
dbm.freeConnection(conKey)
```

### Pattern 2: Prepared Statement

```python
from java.sql import PreparedStatement
prepStmt = con.prepareStatement("SELECT * FROM table WHERE field = ?")
prepStmt.setString(1, value)
rs = prepStmt.executeQuery()
```

---

## Logging Patterns

### Pattern 1: Get Logger

```python
from psdi.util.logging import MXLoggerFactory
logger = service.getLogger("maximo.script")
logger.info("Message")
logger.error("Error message")
logger.warning("Warning message")
logger.debug("Debug message")
```

### Pattern 2: Log with Variables

```python
logger.info("Check Step 1")
logger.info("Current MATUSETRANSID: " + mbo.getString("MATUSETRANSID"))
logger.info("Issue To Workorder: " + wonum + ". Car Asset: " + carAssetnum)
```

---

## Validation Patterns

### Pattern 1: Field Validation in Field Launch Point

```python
if mbo.isModified("FIELDNAME"):
    previousValue = mbo.getMboValue("FIELDNAME").getPreviousValue().asString()
    newValue = mbo.getString("FIELDNAME")
    if previousValue == 'OLD' and newValue == 'NEW':
        mbo.setValue("OTHERFIELD", value, MboConstants.NOVALIDATION | MboConstants.NOACCESSCHECK)
```

### Pattern 2: Required Field Validation

```python
if mbo.isNull("REQUIREDFIELD"):
    service.error('Field Name', 'is required')
    return
```

### Pattern 3: Value Range Validation

```python
value = mbo.getInt("FIELDNAME")
if value < 0 or value > 100:
    service.error('Field Name', 'must be between 0 and 100')
    return
```

### Pattern 4: Status-based Validation

```python
status = mbo.getString("STATUS")
if status in ('IMREVIEW','FMREVIEW','APPR','RESOLVED'):
    service.error("SR", "obsmatnew", [status])
    return
```

### Pattern 5: Conditional Validation

```python
if condition1 and condition2:
    if mbo.isNull("FIELDNAME"):
        service.error('Field Name', 'is mandatory', 'when condition is met')
        return
```

---

## Action Patterns

### Pattern 1: Field Action Launch Point

```python
if not mbo.isNull("FIELDNAME"):
    # Perform action when field is set
    relatedSet = mbo.getMboSet("RELATIONSHIP")
    if not relatedSet.isEmpty():
        relatedMbo = relatedSet.getMbo(0)
        value = relatedMbo.getString("VALUE")
        mbo.setValue("TARGETFIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

### Pattern 2: Action with Multiple Conditions

```python
if condition1:
    if condition2:
        # Perform action
        mbo.setValue("FIELDNAME", value)
```

---

## Initialization Patterns

### Pattern 1: Object Init Launch Point

```python
# Set default values
mbo.setValue("FIELDNAME", defaultValue, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# Set readonly based on conditions
if condition:
    mbo.setFieldFlag("FIELDNAME", MboConstants.READONLY, True)
else:
    mbo.setFieldFlag("FIELDNAME", MboConstants.READONLY, False)
```

### Pattern 2: Field Init Launch Point

```python
# Set field value from owner
owner = mbo.getOwner()
if owner:
    ownerValue = owner.getString("OWNERFIELD")
    mbo.setValue("FIELDNAME", ownerValue, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

---

## Save Patterns (Before/After)

### Pattern 1: Before Save - Validation

```python
if onadd:
    # Validate for new records
    if mbo.isNull("REQUIREDFIELD"):
        service.error('Field Name', 'is required')
        return

if onupdate:
    # Validate for updates
    if mbo.isModified("FIELDNAME"):
        # Handle modification
        pass

if ondelete:
    # Validate for deletion
    if condition:
        service.error('Cannot delete', 'reason message')
        return
```

### Pattern 2: Before Save - Auto-populate Fields

```python
if onadd or onupdate:
    # Auto-populate related fields
    relatedSet = mbo.getMboSet("RELATIONSHIP")
    if not relatedSet.isEmpty():
        relatedMbo = relatedSet.getMbo(0)
        mbo.setValue("FIELDNAME", relatedMbo.getString("VALUE"), 
                     MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

### Pattern 3: Before Save - Complex Logic

```python
if interactive and appName in ('MRGWO', 'NRVEWO', 'ENGWO'):
    asset = wo.getMboSet("ASSET").moveFirst()
    if mbo.isNull('SUBSTATUS'):
        setError('Please choose', 'a', 'Sub Status')
    elif mbo.getString('SUBSTATUS').upper() == assetStatus.upper():
        setError('The status you selected', 'is the same as the asset current status.', 
                 'Please choose a different sub status')
    else:
        asset.setValue('SUBSTATUS', subStatus, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

### Pattern 4: After Save - Trigger Related Updates

```python
# After saving, update related records
relatedSet = mbo.getMboSet("RELATIONSHIP")
relatedMbo = relatedSet.add()
relatedMbo.setValue("FIELDNAME", value)
relatedSet.save()
```

### Pattern 5: Save with AppBean

```python
from psdi.webclient.system.beans import AppBean
session = service.webclientsession()
if session is not None:
    appbean = session.getCurrentApp().getAppBean()
    if appbean is not None:
        appbean.save()
```

---

## Complex Operations Patterns

### Pattern 1: Duplicate with Related Records

```python
dupMbo = mbo.duplicate()
dupSet = dupMbo.getMboSet("RELATIONSHIP")
origSet = mbo.getMboSet("RELATIONSHIP")
origCount = origSet.count()
if origCount > 0:
    for i in range(origCount):
        dupItem = dupSet.add()
        origItem = origSet.getMbo(i)
        dupItem.setValue("FIELDNAME", origItem.getString("FIELDNAME"))
    dupSet.save()
```

### Pattern 2: Find Maximum Value

```python
maxRevSet = mbo.getMboSet("$MAXREVSET", "OBJECTNAME", "where_clause")
maxRevSet.reset()
maxRev = 1
revCount = maxRevSet.count()
for i in range(revCount):
    revMbo = maxRevSet.getMbo(i)
    newRev = revMbo.getInt("REVISION")
    if maxRev < newRev:
        maxRev = newRev
mbo.setValue("REVISION", maxRev + 1)
```

### Pattern 3: Aggregate Calculations

```python
totalValue = 0.0
mboSet = mbo.getMboSet("RELATIONSHIP")
mboSet.reset()
count = mboSet.count()
for i in range(count):
    itemMbo = mboSet.getMbo(i)
    totalValue = totalValue + itemMbo.getDouble("VALUE")
mbo.setValue("TOTAL", totalValue, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

### Pattern 4: Conditional Status Updates

```python
allComplete = True
mboSet = mbo.getMboSet("RELATIONSHIP")
item = mboSet.moveFirst()
while item:
    if item.getBoolean("COMPLETE") == False:
        allComplete = False
    item = mboSet.moveNext()

if allComplete:
    mbo.setValue("STATUS", "COMPLETE", MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
else:
    mbo.setValue("STATUS", "PARTIAL", MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

---

## Script Configuration Template

Standard Script Configuration JSON:

```json
{
    "autoscript": "SCRIPTNAME",
    "description": "Script description",
    "version": "1.0",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "LAUNCHPOINTNAME",
            "launchPointType": "OBJECT|ATTRIBUTE|ACTION",
            "active": true,
            "description": "Launch point description",
            "objectName": "OBJECTNAME",
            "attributeName": "FIELDNAME",
            "actionName": "ACTIONNAME",
            "save": true,
            "add": true,
            "update": true,
            "delete": false,
            "beforeSave": true,
            "afterCommit": false,
            "initializeValue": true,
            "validate": true,
            "runAction": true
        }
    ]
}
```

### Common Launch Point Types

**OBJECT Launch Points:**
- `initializeValue`: Runs when object is initialized
- `save` (`beforeSave`/`afterCommit`): Runs before/after save
- `add`/`update`/`delete`: Control when script runs

**ATTRIBUTE Launch Points:**
- `validate`: Runs during field validation
- `runAction`: Runs when field value changes
- `initializeValue`: Runs when field is initialized

**ACTION Launch Points:**
- `actionName`: Custom action name

---

## Best Practices

**Source**: [IBM Maximo Automation Script Best Practices](https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/bestpractice/overview/)

### 1. Always Import MboConstants at the Top

```python
from psdi.mbo import MboConstants
```

### 2. Always Use MboConstants Flags, Never Numeric Values

```python
# ✅ CORRECT
mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# ❌ WRONG - Never use numeric constants like 2L, 11L
mbo.setValue("FIELD", value, 2L)  # BAD!
```

### 3. Use Standard Flag Combinations

```python
# Most common: Skip validation and access checks
flags = MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION

# With actions skipped too
flags = MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION | MboConstants.NOACTION
```

### 4. Choosing the Right Launch Point and Event

**Critical**: Launch points are script trigger points. Often, choosing the right launch point can help avoid certain performance issues in scripting.

**Example: Attribute Launch Point vs Object Launch Point**

Use Attribute Launch Point for field initialization instead of Object Launch Point Init event to avoid performance issues when selecting multiple MBOs in List tab.

```python
# ✅ GOOD - Attribute Launch Point (Initialize Value)
# This only runs when the attribute is actually referenced
if priority is not None:
    thisvalue = 2 * priority

# ❌ BAD - Object Launch Point Init
# This runs for every MBO in the set, even if attribute is not used
```

### 5. Avoid Costly Object Init Events if Invoked from List Tab

Use `UIContext.isFromListTab()` to avoid costly operations in List tab:

```python
from psdi.common.context import UIContext

if UIContext.getCurrentContext() is not None and UIContext.isFromListTab() == False:
    # Costly initialization code here
    # This only runs when not from List tab
    pass
```

### 6. Watch Out for Conflicting Launch Point Event Scripts

**Problem**: Multiple scripts on the same launch point event execute in unpredictable order (un-ordered map).

**Solutions**:
- Combine scripts into one if possible
- Remove dependencies between scripts

### 7. Avoid Calling Save in Middle of a Transaction

**Best Practice**: MBOs created from launch point MBO are automatically part of the transaction. If you create MBOs using `MXServer.getMXServer().getMboSet()`, add them to the transaction:

```python
# Create MBO outside the current transaction
newMboSet = MXServer.getMXServer().getMboSet("OBJECTNAME", userInfo)

# Add it to the encompassing transaction
mbo.getMXTransaction().add(newMboSet)
```

### 8. Calling MboSet.count() Multiple Times

**Problem**: `count()` fires SQL every time it's called.

**❌ BAD Code**:
```python
if mboset.count() <= 1:
    service.log("skipping this as count is " + mboset.count())
```

**✅ GOOD Code**:
```python
# Call count() once and store the value
cnt = mboset.count()
if cnt <= 1:
    service.log("skipping this as count is " + cnt)
```

### 9. Always Close MBO Sets

**Critical**: Always close MBO sets created using `MXServer.getMXServer().getMboSet()` to prevent memory leaks:

```python
mboset = None
try:
    mboset = MXServer.getMXServer().getMboSet("OBJECTNAME", userInfo)
    # Use mboset here
    pass
finally:
    if mboset is not None:
        mboset.cleanup()
```

**Why**: If not closed, it can result in Out of Memory (OOM) errors.

### 10. Check if Logging is Enabled Before Logging

**Problem**: Logging without checking log level can impact performance:

```python
# ❌ BAD - This calls mboset.count() even if logging is disabled
service.log("count of mbos " + mboset.count())
```

**✅ GOOD - Solution 1** (all versions):
```python
from psdi.util.logging import MXLoggerFactory

logger = MXLoggerFactory.getLogger("maximo.script")
debugEnabled = logger.isDebugEnabled()

if debugEnabled:
    service.log("count of mbos " + mboset.count())
```

**✅ GOOD - Solution 2** (Maximo 7.6.1.2+):
```python
if service.isLoggingEnabled():
    service.log("count of mbos " + mboset.count())
```

### 11. Always Check Interactive Mode

```python
if interactive:
    # Code only runs in UI session
    service.error('Field Name', 'error message')
```

### 12. Check for Null Values Before Processing

```python
if not mbo.isNull("FIELDNAME"):
    # Process field
    pass
```

### 13. Check if MBO Set is Empty Before Accessing

```python
if not mboSet.isEmpty():
    mbo = mboSet.getMbo(0)
    # Process mbo
    pass
```

### 14. Use Try-Except for Error Handling

```python
try:
    # Code that might raise exception
    value = mbo.getString("FIELDNAME")
except Exception, e:
    service.error('Error', 'An error occurred: ' + str(e))
```

### 15. Use Temporary Relationships for Complex Queries

```python
mboSet = mbo.getMboSet("$TEMPREL", "OBJECTNAME", "where_clause")
mboSet.reset()
```

### 16. Always Reset MBO Sets After Setting Where Clause

```python
mboSet.setWhere("where_clause")
mboSet.reset()
```

### 17. Avoid the Mozilla Compatibility Script for Nashorn

**Recommendation**: Moving from Rhino (Java 7) to Nashorn (Java 8) is recommended for performance reasons. However, leveraging the Mozilla compatibility script with Nashorn can result in poor performance in Java 8.

### 18. Use Service Object for Errors (Not Deprecated errorkey/errorgroup)

```python
# ✅ RECOMMENDED
service.error('Field Name', 'error message')
service.error('Field Name', 'error message', ['param1', 'param2'])

# ❌ DEPRECATED - Don't use
errorkey = 'ErrorKey'
errorgroup = 'ErrorGroup'
params = ['param1', 'param2']
```

### 19. Use MBO State Flags for Conditional Logic

```python
if onadd:
    # Code for new MBO
    pass

if onupdate:
    # Code for updated MBO
    pass

if ondelete:
    # Code for deleted MBO
    pass
```

### 20. Use Implicit Variables for Field Flags

```python
# If you have explicit variable "status" bound to MBO attribute
if status_required:
    # Field is required
    pass

if status_readonly:
    # Field is readonly
    pass

if status_modified:
    # Field has been modified
    pass
```

---

## Common Patterns Summary

### Error Handling
- `service.error('Field', 'message')`
- `setError(p0, p1, p2)` function
- `try-except` blocks

### Relationships
- `mbo.getMboSet("RELATIONSHIP")`
- `mbo.getMboSet("$TEMP", "OBJECT", "WHERE")`
- `mxServer.getMboSet("OBJECT", userInfo)`

### Looping
- `for i in range(mboSet.count())`
- `while mbo = mboSet.moveFirst(); mbo = mboSet.moveNext()`

### Setting Values
- `mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)`
- `mbo.setValueNull("FIELD")`
- **Always use MboConstants flags, never numeric values like `2L` or `11L`**
- **Most common combination: `MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION`**

### Field Types
- `getString()`, `getInt()`, `getLong()`, `getDouble()`, `getBoolean()`, `getDate()`
- `isNull()`, `isModified()`

### Validation
- Check null, check modified, check status, check conditions

### Save Operations
- `onadd`, `onupdate`, `ondelete` flags
- `beforeSave`, `afterCommit`

### Initialization
- Set defaults, set readonly, set required

---

**End of Reference**

