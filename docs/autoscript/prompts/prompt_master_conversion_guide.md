# Master Java to Python Conversion Guide

**Purpose**: Common standards, patterns, and practices for all Maximo Java to Python conversions  
**Version**: 1.0.0  
**Last Updated**: 2025-12-08  
**Context**: MAS 9 upgrade - Shared conversion standards for CronTasks, Field Validators, and Object Scripts

---

## Table of Contents

1. [Universal Conversion Standards](#universal-conversion-standards)
2. [Python Best Practices](#python-best-practices)
3. [Standard Header Format](#standard-header-format)
4. [scriptConfig Standards](#scriptconfig-standards)
5. [Common Conversion Patterns](#common-conversion-patterns)
6. [Quality Checklist](#quality-checklist)
7. [Common Issues and Solutions](#common-issues-and-solutions)
8. [Reference Documentation](#reference-documentation)

---

## Universal Conversion Standards

### CRITICAL Comment Format Rules

**NEVER use triple-quote docstrings (""") anywhere in Maximo automation scripts**

```python
# ❌ WRONG - Will cause parsing errors in Maximo
"""
This is a docstring
Multiple lines
"""

# ✅ CORRECT - Use single-line comments
# This is proper documentation
# Multiple lines with # prefix
# Works correctly in Maximo
```

**Header Format Standards:**
- File headers: Use `################` comment blocks (80 chars wide)
- Function documentation: Use `# ` single-line comments
- Inline comments: Use `# ` single-line comments
- **MANDATORY**: All documentation must use `#` comments only

---

## Python Best Practices

### Jython-Specific Python Idioms

**CRITICAL**: Always use Python idioms, never Java-style method calls:

```python
# ═══════════════════════════════════════════════════════════
# STRING COMPARISONS
# ═══════════════════════════════════════════════════════════

# ❌ WRONG - Java style
if string.equalsIgnoreCase("VALUE"):
if not string.equalsIgnoreCase("VALUE"):
if string1.equalsIgnoreCase("A") or string2.equalsIgnoreCase("B"):

# ✅ CORRECT - Python style
if string.upper() == "VALUE":
if string.upper() != "VALUE":
if string1.upper() in ["A", "B", "C"]:  # More efficient for multiple checks

# ═══════════════════════════════════════════════════════════
# BOOLEAN CHECKS
# ═══════════════════════════════════════════════════════════

# ❌ WRONG
if flag.equals("Y"):
if not flag.equalsIgnoreCase("Y"):

# ✅ CORRECT
if flag == "Y":
if flag.upper() != "Y":

# ═══════════════════════════════════════════════════════════
# CLASS TYPE CHECKING
# ═══════════════════════════════════════════════════════════

# ❌ WRONG - isinstance() can fail with Java classes in Jython
if isinstance(obj, tmg.app.workorder.TMG_PlusWO):

# ✅ CORRECT - Use getClass().getName()
obj_class = obj.getClass().getName()
if "TMG_PlusWO" in obj_class:
    # Process TMG_PlusWO
elif "PlusPermit" in obj_class:
    # Process PlusPermit

# ═══════════════════════════════════════════════════════════
# NULL/NONE CHECKS
# ═══════════════════════════════════════════════════════════

# ❌ WRONG
if value is not None and not value.isEmpty():

# ✅ CORRECT
if value is not None and value != "":
if value:  # Pythonic way for truthy check
```

### MboConstants Usage

**Always use named constants instead of magic numbers:**

```python
from psdi.mbo import MboConstants

# ❌ WRONG - Magic numbers (Java style)
mbo.setValue("field", value, 2L)
mbo.setValue("field", value, 7L)
mbo.setValue("field", value, 11L)

# ✅ CORRECT - Named constants
mbo.setValue("field", value, MboConstants.NOVALIDATION)
mbo.setValue("field", value, MboConstants.NOACCESSCHECK)
mbo.setValue("field", value, 
    MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
mbo.setValue("field", value, 
    MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION_AND_NOACTION)
```

**Common MboConstants:**
- `NOACCESSCHECK` - Bypass security checks (Java: 2L)
- `NOVALIDATION` - Skip field validation (Java: 7L)
- `NOVALIDATION_AND_NOACTION` - Skip validation and actions (Java: 8L)
- Combined: `NOACCESSCHECK | NOVALIDATION` (Java: 11L)

### Resource Management

**Always close MboSets in finally blocks:**

```python
# ✅ CORRECT Pattern
mboSet = None
try:
    mboSet = mbo.getMboSet("RELATIONSHIP")
    # Process mboSet
finally:
    if mboSet is not None:
        mboSet.close()
```

### Exception Handling

**Always re-raise exceptions to mark Maximo script as failed:**

```python
# ✅ CORRECT Pattern
try:
    # Main script logic
    pass
except Exception as e:
    logger.error(className + ": Error message: " + str(e))
    raise  # CRITICAL - Re-raise to mark script as failed in Maximo
```

---

## Standard Header Format

### File Header Template

```python
################################################################################
# Script: [Descriptive Title]
# [Launch Point Type]: [OBJECT/ATTRIBUTE/CRON/ACTION]
#
# Launch Point: [SCRIPT_NAME]
# Object: [OBJECT_NAME or N/A]
#
# Author: Converted from Java [ClassName]
#
# Revision:
# Date        User                        Comment
# ----------  --------------------------  ---------------------------------------
# 2025-12-08  Automation                  Converted from [ClassName].java
#                                         [TR number]: [Description]
#
# Conversion Review:
# - Convert to AutoScript: [Yes/Partially/No]
# - Complexity: [Simple/Medium/Complex]
# - Status: [Good/Need TMG Action]
# - Business Area: [Module/Domain]
#
################################################################################
#
# DESCRIPTION:
#   [Detailed description of functionality]
#
# BUSINESS REQUIREMENTS ([TR/ALM/PPM numbers]):
#   - [Requirement 1]
#   - [Requirement 2]
#
# CONVERTED FROM: [package].[ClassName].[method]()
#   Original: [Java file path]
#   TR: [TR numbers]
#
################################################################################

from psdi.util.logging import MXLoggerFactory
from psdi.mbo import MboConstants

# Initialize logger
logger = MXLoggerFactory.getLogger("maximo.[domain].[script]")
className = "[script.name]"

# Script logic here
```

### Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Object Script | `[object].[type].[event].py` | `invoice.obj.save.py` |
| Action Script | `[object].action.[name].py` | `invoice.action.doclrprocess.py` |
| Field Validator | `[object].[attribute].[type].py` | `inventory.itemnum.listfilter.py` |
| Cron Task | `[taskname].cron.action.py` | `tmg_datapurge.cron.action.py` |
| Script Name | `[OBJECT].[TYPE].[EVENT]` | `INVOICE.OBJ.SAVE` |
| Launch Point | `[OBJECT]_[TYPE]_[EVENT]` | `INVOICE_OBJ_SAVE` |

**Rules:**
- All filenames: lowercase with dots
- Script names in scriptConfig: UPPERCASE with dots
- Launch point names: UPPERCASE with underscores
- No spaces in any names

---

## scriptConfig Standards

### CRITICAL Placement Rule

**⚠️ scriptConfig MUST be placed at the ABSOLUTE END of the file**

```python
# Script logic here
try:
    # Main code
    pass
except Exception as e:
    logger.error("Error: " + str(e))
    raise

# Script Configuration for Launch Point Creation
scriptConfig = {
    "autoscript": "[SCRIPT.NAME]",
    "description": "[Description]",
    "version": "1.0",
    "active": True,
    "logLevel": "ERROR"
}
# <-- END OF FILE - NOTHING AFTER scriptConfig
```

### scriptConfig Structure

```python
scriptConfig = {
    "autoscript": "[SCRIPT_NAME]",
    "description": "[Brief description]",
    "version": "1.0",
    "active": True,
    "logLevel": "ERROR",  # or "DEBUG" for development
    "references": {
        "objects": ["[OBJECT1]", "[OBJECT2]"],
        "attributes": ["[ATTR1]", "[ATTR2]"],
        "relationships": ["[REL1]"],
        "TR": ["[TR1]", "[TR2]"]
    }
}
```

### Launch Point Types

#### 1. OBJECT Launch Points

```python
scriptConfig = {
    "autoscript": "[OBJECT].OBJ.[EVENT]",
    # ... other fields
    "scriptLaunchPoints": [
        {
            "launchPointName": "[OBJECT]_OBJ_[EVENT]",
            "launchPointType": "OBJECT",
            "objectName": "[OBJECT]",
            "active": True,
            "description": "[Description]",
            # Event-specific fields (see specific conversion guides)
        }
    ]
}
```

#### 2. ATTRIBUTE Launch Points

```python
scriptConfig = {
    "autoscript": "[object].[attribute].[type]",
    # ... other fields
    "scriptLaunchPoints": [
        {
            "launchPointName": "[OBJECT]_[ATTRIBUTE]_[TYPE]",
            "launchPointType": "ATTRIBUTE",
            "objectName": "[OBJECT]",
            "attributeName": "[ATTRIBUTE]",
            "active": True,
            "description": "[Description]"
            # Type-specific fields (VALIDATE, INIT, ACTION, RETRIEVE_LIST)
        }
    ]
}
```

#### 3. ACTION Launch Points

```python
scriptConfig = {
    "autoscript": "[OBJECT].ACT.[ACTIONNAME]",
    # ... other fields
    "scriptLaunchPoints": [
        {
            "launchPointName": "[OBJECT]_ACT_[ACTIONNAME]",
            "launchPointType": "ACTION",
            "objectName": "[OBJECT]",
            "action": "[ACTIONNAME]",
            "active": True,
            "description": "[Description]"
        }
    ],
    "scriptVariables": [
        {
            "varName": "[paramName]",
            "varBindingType": "[INPARAM/OUTPARAM/INOUTPARAM]",
            "varBindingValue": "[paramName]",
            "varType": "[String/Integer/Boolean/etc.]"
        }
    ]
}
```

#### 4. CRON Launch Points

```python
scriptConfig = {
    "autoscript": "[TASKNAME].CRON.ACTION",
    # ... other fields
    "scriptLaunchPoints": [
        {
            "launchPointName": "[TASKNAME]_CRON_ACTION",
            "launchPointType": "OBJECT",
            "objectName": "CRONTASKINSTANCE",
            "active": True,
            "description": "[Description]",
            "save": True,
            "add": False,
            "update": True,
            "delete": False
        }
    ]
}
```

---

## Common Conversion Patterns

### Pattern 1: Database Operations (JDBC)

```python
from java.sql import SQLException

def queryDatabase():
    # Get connection from Maximo (DO NOT CLOSE)
    userInfo = MXServer.getMXServer().getSystemUserInfo()
    connection = userInfo.getConnection()
    
    statement = None
    resultSet = None
    try:
        statement = connection.createStatement()
        resultSet = statement.executeQuery("SELECT ...")
        
        while resultSet.next():
            value = resultSet.getString("COLUMN")
            # Process row
            
    finally:
        # Close statement and resultSet, but NOT connection
        if resultSet is not None:
            resultSet.close()
        if statement is not None:
            statement.close()
        # DO NOT close connection - managed by MXServer
```

### Pattern 2: MboSet Operations

```python
from psdi.mbo import MboConstants

mboSet = None
try:
    # Get MboSet from relationship
    mboSet = mbo.getMboSet("RELATIONSHIP")
    
    # Iterate through records
    for i in range(mboSet.count()):
        childMbo = mboSet.getMbo(i)
        # Process childMbo
        
    # Or query with where clause
    mboSet = mbo.getMboSet("$rel", "OBJECT", 
        "WHERE_CLAUSE")
    
finally:
    if mboSet is not None:
        mboSet.close()
```

### Pattern 3: Date Arithmetic

```python
from java.util import GregorianCalendar, Calendar, Date

def isDateOlderThan(dateToCheck, daysToAdd, compareDate):
    # Check if date + days is before compareDate
    if dateToCheck is None:
        return False
        
    calendar = GregorianCalendar()
    calendar.setTime(dateToCheck)
    calendar.add(Calendar.DAY_OF_MONTH, daysToAdd)
    newDate = calendar.getTime()
    
    return newDate.before(compareDate)

# Usage
from psdi.server import MXServer
currentDate = MXServer.getMXServer().getDate()
isOld = isDateOlderThan(recordDate, 1825, currentDate)  # 5 years
```

### Pattern 4: Thread Sleep (Batch Processing)

```python
from java.lang import Thread

# Convert seconds to milliseconds
waitSeconds = 10
Thread.sleep(waitSeconds * 1000)

# In batch processing
for batch in range(totalBatches):
    # Process batch
    processBatch(batch)
    
    # Wait between batches (except after last one)
    if batch < totalBatches - 1:
        Thread.sleep(waitSeconds * 1000)
```

### Pattern 5: Logger Initialization

```python
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory

# Method 1: MXLoggerFactory (recommended for most scripts)
logger = MXLoggerFactory.getLogger("maximo.[domain].[script]")

# Method 2: MXServer lookup (for cron tasks)
logger = MXServer.getMXServer().lookup("LOGGING")

# Usage
className = "[script.name]"
logger.info(className + ": Info message")
logger.error(className + ": Error message", exception)
logger.debug(className + ": Debug message")
```

### Pattern 6: Status Translation

```python
def getInternalStatus(externalValue):
    # Convert external status to internal value
    synonymDomain = mbo.getTranslator().toInternalString(
        "SYNONYMDOMAIN", externalValue)
    return synonymDomain

def getExternalStatus(internalValue):
    # Convert internal status to external value
    externalValue = mbo.getTranslator().toExternalDefaultValue(
        "SYNONYMDOMAIN", internalValue, mbo)
    return externalValue

# Example
poStatus = mbo.getString("STATUS")
internalStatus = mbo.getTranslator().toInternalString("POSTATUS", poStatus)
if internalStatus in ["WAPPR", "APPR"]:
    # Process approved/pending approval POs
    pass
```

---

## Quality Checklist

### Universal Checklist (All Conversion Types)

- [ ] **Header Complete**
  - [ ] Script title and description
  - [ ] Launch point information
  - [ ] Conversion source (Java class)
  - [ ] Revision history
  - [ ] Business requirements

- [ ] **Code Quality**
  - [ ] NO triple-quote docstrings (`"""`)
  - [ ] All comments use `#` single-line format
  - [ ] Python idioms used (no `.equalsIgnoreCase()`)
  - [ ] MboConstants for all flags (no 2L, 7L, 11L)
  - [ ] Proper indentation (4 spaces)
  - [ ] Clear variable names

- [ ] **Resource Management**
  - [ ] All MboSets closed in finally blocks
  - [ ] Database ResultSets closed
  - [ ] Database Statements closed
  - [ ] Connection NOT closed (managed by MXServer)

- [ ] **Exception Handling**
  - [ ] Try-except blocks present
  - [ ] Exceptions re-raised (`raise`)
  - [ ] Error messages logged
  - [ ] Specific exception types when possible

- [ ] **scriptConfig Section**
  - [ ] Placed at ABSOLUTE END of file
  - [ ] Complete JSON structure
  - [ ] All launch points defined
  - [ ] Proper naming conventions
  - [ ] Active flag set correctly

- [ ] **Logging**
  - [ ] Logger initialized correctly
  - [ ] className variable defined
  - [ ] Consistent log message format
  - [ ] Appropriate log levels

- [ ] **Testing**
  - [ ] Expected lint errors documented
  - [ ] Testing checklist included
  - [ ] Special test cases noted

---

## Common Issues and Solutions

### Issue 1: Triple-Quote Docstrings

**Problem**: Using `"""` docstrings causes Maximo parsing errors

**Solution**: Use `#` comments only

```python
# ❌ WRONG
def myFunction():
    """
    This is a docstring
    """
    pass

# ✅ CORRECT
def myFunction():
    # This is proper documentation
    # Multiple lines with # prefix
    pass
```

### Issue 2: Java-Style String Comparisons

**Problem**: `.equalsIgnoreCase()` not Pythonic

**Solution**: Use `.upper() ==` or `.upper() in []`

```python
# ❌ WRONG
if status.equalsIgnoreCase("ACTIVE"):

# ✅ CORRECT
if status.upper() == "ACTIVE":

# For multiple values
if status.upper() in ["ACTIVE", "PENDING", "APPROVED"]:
```

### Issue 3: TimeUnit Sleep

**Problem**: `TimeUnit` not available in Jython

**Solution**: Use `Thread.sleep(milliseconds)`

```python
# ❌ WRONG
from java.util.concurrent import TimeUnit
TimeUnit.SECONDS.sleep(10)

# ✅ CORRECT
from java.lang import Thread
Thread.sleep(10 * 1000)  # Convert seconds to milliseconds
```

### Issue 4: Numeric Flag Constants

**Problem**: Magic numbers (2L, 7L, 11L) not clear

**Solution**: Use MboConstants

```python
# ❌ WRONG
mbo.setValue("field", value, 11L)

# ✅ CORRECT
from psdi.mbo import MboConstants
mbo.setValue("field", value, 
    MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

### Issue 5: MboSet Memory Leaks

**Problem**: Not closing MboSets causes memory leaks

**Solution**: Always use try/finally

```python
# ❌ WRONG
mboSet = mbo.getMboSet("REL")
# Process mboSet
# No close() call

# ✅ CORRECT
mboSet = None
try:
    mboSet = mbo.getMboSet("REL")
    # Process mboSet
finally:
    if mboSet is not None:
        mboSet.close()
```

### Issue 6: scriptConfig Placement

**Problem**: Code after scriptConfig causes issues

**Solution**: scriptConfig must be LAST

```python
# ❌ WRONG
scriptConfig = { ... }
# Additional code here

# ✅ CORRECT
# All code here
scriptConfig = { ... }
# <-- END OF FILE
```

### Issue 7: isinstance() with Java Classes

**Problem**: `isinstance()` unreliable in Jython

**Solution**: Use `getClass().getName()`

```python
# ❌ WRONG
if isinstance(obj, tmg.app.TMG_PlusWO):

# ✅ CORRECT
obj_class = obj.getClass().getName()
if "TMG_PlusWO" in obj_class:
```

### Issue 8: Database Connection Management

**Problem**: Closing connection breaks Maximo

**Solution**: Never close connection obtained from userInfo

```python
# ❌ WRONG
connection = userInfo.getConnection()
try:
    # Use connection
finally:
    connection.close()  # DON'T DO THIS

# ✅ CORRECT
connection = userInfo.getConnection()
statement = None
try:
    statement = connection.createStatement()
    # Use statement
finally:
    if statement is not None:
        statement.close()
    # Connection managed by MXServer
```

---

## Reference Documentation

### Common Reference Files (All Conversion Types)

1. **Maximo Script Patterns**: `Knowledge-base/maximo_script_patterns_reference.md`
   - MboSet operations
   - Database operations
   - Date arithmetic
   - Status translation
   - Logging patterns

2. **Naming Conventions**: `Knowledge-base/NAMING_CONVENTIONS.md`
   - File naming standards
   - Script naming conventions
   - Launch point naming
   - Variable naming

3. **Java to Python Guide**: `Knowledge-base/JAVA_TO_PYTHON_CONVERSION_PROMPTS.md`
   - Syntax differences
   - Import mappings
   - Exception handling
   - Method signature changes

4. **Utility Library**: `Knowledge-base/maximo_utility_library.py`
   - Helper functions
   - Reusable patterns
   - Common utilities

5. **Launch Point Configuration**: `docs/LAUNCH_POINT_CONFIGURATION_GUIDE.md`
   - How to create launch points in Maximo
   - Variable binding configuration
   - Testing procedures

6. **Official Documentation**: `Knowledge-base/OFFICIAL_DOCUMENTATION.md`
   - IBM Maximo documentation links
   - API references
   - Best practices

### Expected Lint Errors (Normal for Maximo Scripts)

The following variables are implicit and provided by Maximo's automation script runtime:

- `mbo` - The MBO or MboValue being processed
- `scriptExit()` - Function to exit script early
- `launchpoint` - Launch point configuration dictionary
- `croninstance` - Cron task instance (cron tasks only)

These "undefined" warnings can be safely ignored as they are injected at runtime by Maximo.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-08 | Initial master guide created from common patterns across all conversion types |

---

## See Also

- **Specific Conversion Guides:**
  - `prompt_objectscripts.md` - Object/Action script conversions
  - `prompt_crontasks.md` - Cron task conversions

- **Launch Point Reference:**
  - `Knowledge-base/LAUNCH_POINT_REFERENCE_PATTERNS.md` - Complete launch point examples


---

**END OF MASTER CONVERSION GUIDE**
