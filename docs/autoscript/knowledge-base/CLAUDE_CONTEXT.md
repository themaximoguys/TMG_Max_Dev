# Claude Context - Maximo Automation Scripts

## Project Overview

This GENERAL folder is a production-ready reference library for building IBM Maximo automation scripts and converting Java code to automation scripts. It contains standards, patterns, utilities, and documentation for AI-assisted development.

**Purpose**: Master context and reference library for Maximo automation script development  
**Status**: Production Ready - Generic and reusable across any Maximo project  
**Version**: 1.0.0

---

## Critical Rules (MUST FOLLOW)

### 1. Script Naming Convention
**Format**: `[objectname].[launchpointtype].[event].[optional].py`

**Examples**:
- Object Launch: `workorder.obj.save.before.py`
- Attribute Launch: `inventory.fld.binnum.validate.py`
- Action Launch: `workorder.action.duplicate.py`
- Cron Task: `cron.rss.asset.update.serial.py`

**Reference**: See `NAMING_CONVENTIONS.md` for complete standards (includes quick reference section)

### 2. Standard Script Header (REQUIRED)
Every script MUST include this header:

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
################
```

**Template**: See `script_header_template.py`

### 3. MboConstants (CRITICAL - NEVER USE NUMERIC CONSTANTS)

**✅ CORRECT**:
```python
from psdi.mbo import MboConstants

# Always use MboConstants
mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# Common flags
MboConstants.NOACCESSCHECK      # Skip access control
MboConstants.NOVALIDATION       # Skip validation
MboConstants.NOACTION           # Skip action scripts
MboConstants.READONLY           # Set readonly
MboConstants.REQUIRED           # Set required
```

**❌ WRONG** - Never use numeric constants:
```python
mbo.setValue("FIELD", value, 2L)      # WRONG!
mbo.setValue("FIELD", value, 11L)     # WRONG!
```

### 4. Error Handling (Use service.error)

**✅ CORRECT**:
```python
# Recommended approach
service.error('Field Name', 'error message')
service.error('Field Name', 'error message', ['param1', 'param2'])
```

**⚠️ Deprecated** (but may exist in legacy code):
```python
# Custom setError function (deprecated, use service.error instead)
def setError(p0, p1, p2):
    global errorkey, errorgroup, params
    errorkey = 'InfoParameters3'
    errorgroup = 'AutoScript'
    params = [p0, p1, p2]
```

---

## File Priority for Context

When working on Maximo scripts, reference these files in priority order:

1. **`AGENT_CONTEXT_GUIDE.md`** - Master guide (workflows, rules, patterns)
2. **`NAMING_CONVENTIONS.md`** - Naming standards (includes quick reference)
3. **`script_header_template.py`** - Header template (required)
4. **`maximo_script_patterns_reference.md`** - Code patterns (comprehensive)
5. **`maximo_utility_library.py`** - Utility functions (reusable)
6. **`OFFICIAL_DOCUMENTATION.md`** - IBM official patterns

---

## Common Code Patterns

### Error Handling
```python
# Use service.error (recommended)
service.error('FIELDNAME', 'Error message text')

# With parameters
service.error('FIELDNAME', 'Error with {0} and {1}', ['param1', 'param2'])
```

### Relationship Access
```python
# Standard relationship
mboSet = mbo.getMboSet("RELATIONSHIPNAME")
mboSet.reset()

# Temporary relationship
mboSet = mbo.getMboSet("$TEMPREL", "OBJECTNAME", "WHERE_CLAUSE")
mboSet.reset()
```

### Looping Through MBO Sets
```python
# Method 1: Using count() - store result to avoid multiple calls
cnt = mboSet.count()
for i in range(cnt):
    mboItem = mboSet.getMbo(i)
    # Process mboItem

# Method 2: Using moveFirst/moveNext
mbo = mboSet.moveFirst()
while mbo:
    # Process mbo
    mbo = mboSet.moveNext()

# Always close sets when done
mboSet.close()
```

### Setting Values
```python
from psdi.mbo import MboConstants

# With flags (most common)
mbo.setValue("FIELDNAME", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# Set null
mbo.setValueNull("FIELDNAME")

# With previous value check
if mbo.toBeAdded() or mbo.isModified("FIELDNAME"):
    mbo.setValue("FIELDNAME", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

### Getting Values
```python
# Get string value
fieldValue = mbo.getString("FIELDNAME")

# Get integer value
intValue = mbo.getInt("FIELDNAME")

# Get double value
doubleValue = mbo.getDouble("FIELDNAME")

# Get date value
dateValue = mbo.getDate("FIELDNAME")

# Get boolean value
boolValue = mbo.getBoolean("FIELDNAME")

# Check for null
if mbo.isNull("FIELDNAME"):
    # Handle null case
```

### User and Group Operations
```python
from psdi.server import MXServer

# Get user info
userInfo = mbo.getUserInfo()
currentUser = userInfo.getUserName()

# Check if user is in a group
mxServer = MXServer.getMXServer()
guSet = mxServer.getMboSet("GROUPUSER", userInfo)
guSet.setWhere("userid='" + userid + "' and groupname in ('GROUP1', 'GROUP2')")
guSet.reset()
isInGroup = not guSet.isEmpty()
guSet.close()
```

### Date Handling
```python
from java.util import Date, Calendar
from java.text import SimpleDateFormat

# Get current date
currentDate = Date()

# Format date
sdf = SimpleDateFormat("yyyy-MM-dd")
formattedDate = sdf.format(currentDate)

# Set date field
mbo.setValue("DATEFIELD", currentDate, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

### Logging
```python
from psdi.util.logging import MXLoggerFactory

# Get logger
logger = MXLoggerFactory.getLogger("maximo.script")

# Log messages
logger.info("Information message")
logger.warn("Warning message")
logger.error("Error message")
logger.debug("Debug message: " + str(variable))
```

### Database Operations
```python
from psdi.server import MXServer
from psdi.mbo import SqlFormat

# Get database connection
mxServer = MXServer.getMXServer()
conn = mxServer.getDBManager().getConnection(mxServer.getSystemUserInfo())

# Execute query
stmt = conn.createStatement()
rs = stmt.executeQuery("SELECT * FROM TABLENAME WHERE CONDITION")

while rs.next():
    value = rs.getString("COLUMNNAME")
    # Process result

# Close resources
rs.close()
stmt.close()
conn.close()
```

### Field Flags (Readonly/Required)
```python
# Set field readonly
mbo.setFieldFlag("FIELDNAME", MboConstants.READONLY, True)

# Remove readonly
mbo.setFieldFlag("FIELDNAME", MboConstants.READONLY, False)

# Set field required
mbo.setFieldFlag("FIELDNAME", MboConstants.REQUIRED, True)

# Remove required
mbo.setFieldFlag("FIELDNAME", MboConstants.REQUIRED, False)
```

---

## Common Implicit Variables

These variables are automatically available in all Maximo automation scripts:

| Variable | Type | Description |
|----------|------|-------------|
| `mbo` | psdi.mbo.Mbo | Current MBO object |
| `mboname` | String | Name of current MBO |
| `user` | String | Current user ID |
| `app` | String | Application name |
| `interactive` | boolean | True if UI session, False if background |
| `onadd` | boolean | True if new MBO |
| `onupdate` | boolean | True if existing MBO is updated |
| `ondelete` | boolean | True if MBO is deleted |
| `service` | ScriptService | Global service object for errors, warnings |

---

## Workflow: Building New Scripts

1. **Determine Script Name**
   - Reference: `NAMING_CONVENTIONS.md` (includes quick reference section)
   - Format: `[objectname].[launchpointtype].[event].[optional].py`

2. **Add Standard Header**
   - Copy from: `script_header_template.py`
   - Include: Launch point type, name, object, author, revisions

3. **Select Code Patterns**
   - Reference: `maximo_script_patterns_reference.md`
   - Use appropriate patterns for your use case

4. **Import Utility Functions**
   - Check: `maximo_utility_library.py`
   - Reuse existing functions instead of duplicating code

5. **Follow Best Practices**
   - Always use MboConstants (never numeric constants)
   - Always use `service.error()` for errors
   - Always close MBO sets when done
   - Include proper error handling

---

## Workflow: Converting Java to Python

1. **Analyze Java Class**
   - Identify launch point type (Object, Attribute, Action, Cron)
   - Identify events (save, validate, init, etc.)

2. **Create Script Name**
   - Reference: `NAMING_CONVENTIONS.md`
   - Convert Java class name to script naming convention

3. **Add Standard Header**
   - Use: `script_header_template.py`

4. **Convert Code**
   - Reference: `maximo_script_patterns_reference.md`
   - Common conversions:
     - Java → Python syntax
     - Numeric constants → MboConstants
     - Java imports → Python imports
     - Java error handling → `service.error()`

5. **Use Utility Functions**
   - Check: `maximo_utility_library.py`
   - Replace custom code with utility functions where possible

---

## Utility Library Functions

The `maximo_utility_library.py` contains reusable functions organized by category:

### User/Group Operations
- `checkUserInGroup(mbo, userid, groupList)` - Check if user is in groups
- `getUserGroups(mbo, userid)` - Get all groups for a user
- `checkUserInSecurityGroup(mbo, userid, securityGroupList)` - Check security group membership

### Type Conversions
- `safeGetString(mbo, fieldName, defaultValue)` - Safe string getter
- `safeGetInt(mbo, fieldName, defaultValue)` - Safe integer getter
- `safeGetDouble(mbo, fieldName, defaultValue)` - Safe double getter
- `safeGetDate(mbo, fieldName)` - Safe date getter

### Validations
- `isFieldModified(mbo, fieldName)` - Check if field is modified
- `isFieldNull(mbo, fieldName)` - Check if field is null
- `validateRequired(mbo, fieldName, errorMessage)` - Validate required field

### MBO Operations
- `safeSetValue(mbo, fieldName, value, flags)` - Safe value setter
- `safeCloseMboSet(mboSet)` - Safe MBO set closer
- `getMboSetCount(mboSet)` - Get MBO set count safely

**Reference**: See `UTILITY_LIBRARY_README.md` for complete function documentation

---

## Launch Point Types

### Object Launch Point
**Events**: `save.before`, `save.after`, `save.aftercommit`, `init`, `validate`  
**Pattern**: `[object].obj.[event].py`  
**Example**: `workorder.obj.save.before.py`

### Attribute Launch Point
**Events**: `validate`, `action`, `init`, `list`, `modify`, `readonly`  
**Pattern**: `[object].fld.[field].[event].py`  
**Example**: `inventory.fld.binnum.validate.py`

### Action Launch Point
**Events**: Custom action names  
**Pattern**: `[object].action.[actionname].py`  
**Example**: `workorder.action.duplicate.py`

### Cron Task Script
**Pattern**: `cron.[description].py`  
**Example**: `cron.rss.asset.update.serial.py`

---

## Best Practices Summary

### Code Quality
✅ Always use MboConstants (never numeric constants)  
✅ Always use `service.error()` for errors  
✅ Always include standard script header  
✅ Always close MBO sets when done  
✅ Use utility library functions (don't duplicate code)  
✅ Include proper error handling  
✅ Add comments for complex logic  
✅ Follow naming conventions strictly  

### Performance
✅ Store MBO set count before loops (`cnt = mboSet.count()`)  
✅ Close MBO sets immediately after use  
✅ Use temporary relationships for complex queries  
✅ Avoid multiple database calls in loops  
✅ Use batch operations where possible  

### Maintainability
✅ Use descriptive variable names  
✅ Include revision history in header  
✅ Document non-obvious logic  
✅ Keep functions small and focused  
✅ Reuse utility functions  

---

## Quick Reference: Common Imports

```python
# Core Maximo imports
from psdi.mbo import Mbo
from psdi.mbo import MboConstants
from psdi.mbo import MboSetRemote
from psdi.server import MXServer
from psdi.security import UserInfo
from psdi.util.logging import MXLoggerFactory
from psdi.mbo import SqlFormat

# Java utilities
from java.util import Date, Calendar
from java.text import SimpleDateFormat

# Database operations
from java.sql import Statement, Connection, ResultSet
```

---

## Official IBM Documentation

**Primary Reference**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/

**Key Sections**:
- Components: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/introduction/components
- Best Practices: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/bestpractice/overview/
- Object Scripts: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/object-scripts/object-launchpoint
- Attribute Scripts: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/attribute-scripts

**Local Copy**: See `OFFICIAL_DOCUMENTATION.md` for offline reference

---

## File Structure Summary

**Total Files**: 13 files (optimized from 19 files)

**Core Files**:
- `README.md` - Complete overview
- `AGENT_CONTEXT_GUIDE.md` - Master guide
- `CLAUDE_CONTEXT.md` - This file

**Standards**:
- `NAMING_CONVENTIONS.md` - Naming standards (includes quick reference)
- `script_header_template.py` - Header template

**Patterns**:
- `maximo_script_patterns_reference.md` - Code patterns (comprehensive)
- `maximo_script_patterns_reference.py` - Patterns (Python format)

**Utilities**:
- `maximo_utility_library.py` - Utility functions
- `UTILITY_LIBRARY_README.md` - Utility documentation

**Reference**:
- `OFFICIAL_DOCUMENTATION.md` - Local IBM docs
- `REFERENCES.md` - Links to official docs

**Project Management**:
- `FILE_STRUCTURE.md` - File structure overview
- `CHANGELOG.md` - Version history
- `LICENSE.md` - License information

---

## Quick Start for Claude

### Task: Create New Script

1. Ask user for:
   - Object name (e.g., WORKORDER, ASSET, PO)
   - Launch point type (Object, Attribute, Action, Cron)
   - Event (save.before, validate, action, etc.)
   - Field name (if Attribute launch point)

2. Generate script name using naming convention

3. Add standard header from `script_header_template.py`

4. Reference `maximo_script_patterns_reference.md` for code patterns

5. Check `maximo_utility_library.py` for reusable functions

6. Follow all critical rules (MboConstants, error handling, etc.)

### Task: Convert Java to Python

1. Analyze Java class to identify:
   - Launch point type
   - Events
   - Business logic

2. Create Python script name using naming convention

3. Add standard header

4. Convert Java code to Python:
   - Replace numeric constants with MboConstants
   - Convert Java syntax to Python
   - Replace error handling with `service.error()`
   - Use utility functions where applicable

5. Test and validate

### Task: Review/Fix Script

1. Check naming convention compliance

2. Verify standard header is present

3. Check for numeric constants (replace with MboConstants)

4. Verify error handling uses `service.error()`

5. Check if utility functions can replace custom code

6. Verify MBO sets are closed

7. Check for best practices compliance

---

## Context Usage Tips

### For Simple Tasks
Reference only:
- This file (`CLAUDE_CONTEXT.md`)
- `NAMING_CONVENTIONS.md` (for naming)
- `script_header_template.py` (for header)

### For Complex Tasks
Reference:
- This file (`CLAUDE_CONTEXT.md`)
- `AGENT_CONTEXT_GUIDE.md` (complete workflow)
- `maximo_script_patterns_reference.md` (detailed patterns)
- `maximo_utility_library.py` (utility functions)

### For Java Conversion
Reference:
- This file (`CLAUDE_CONTEXT.md`)
- `AGENT_CONTEXT_GUIDE.md` (conversion workflow)
- `maximo_script_patterns_reference.md` (Java→Python patterns)
- `maximo_utility_library.py` (reusable functions)

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: Based on IBM Maximo Automation Script documentation and best practices

This context file provides essential information for Claude AI to assist with Maximo automation script development effectively.

