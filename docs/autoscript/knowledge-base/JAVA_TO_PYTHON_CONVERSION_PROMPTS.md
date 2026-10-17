# Java to Python Conversion Prompts - Maximo Automation Scripts

## Overview

This file provides structured prompts for coding agents to convert existing Java classes into Maximo automation scripts while preserving context, business logic, and functionality.

**Purpose**: Standardized prompts for converting Java MBO classes to Python automation scripts  
**Usage**: Use these prompts as templates when requesting Java-to-Python conversion  
**Version**: 1.0.0

---

## General Conversion Instructions

### Before Starting Conversion

1. **Analyze Java Class**:
   - Identify the class type (Mbo, MboSet, MboRemote, etc.)
   - Determine launch point type (Object, Attribute, Action, Cron)
   - Identify events (save, validate, init, action, etc.)
   - Map business logic and requirements
   - Identify dependencies and relationships

2. **Understand Context**:
   - Read class documentation/comments
   - Understand business rules and validations
   - Identify implicit variables and context
   - Map Java patterns to Python patterns

3. **Follow Standards**:
   - Use naming convention from `NAMING_CONVENTIONS.md`
   - Include standard header from `script_header_template.py`
   - Convert numeric constants to `MboConstants`
   - Convert Java error handling to `service.error()`
   - Use utility functions from `maximo_utility_library.py`

4. **Preserve Logic**:
   - Maintain all business logic
   - Preserve validation rules
   - Keep relationship logic
   - Maintain error handling behavior

---

## Conversion Prompt Templates

### 1. Object Launch Point - Save Before Conversion

**Prompt Template**:

```
Convert the following Java class to a Maximo automation script:

**Java Class**: [Full Java class name]
**Class Type**: [Mbo, MboSet, etc.]
**Launch Point**: Object Launch Point - Save Before
**Object**: [OBJECT_NAME]
**Event**: Save Before

**Java Code**:
```java
[Paste Java code here]
```

**Business Logic**:
- [Describe what the Java class does]
- [List key validations]
- [List key operations]
- [List relationships]

**Requirements**:
- Preserve all business logic from Java class
- Maintain all validation rules
- Keep all relationship logic
- Convert Java patterns to Python patterns
- Use MboConstants (never numeric constants)
- Use service.error() for errors
- Follow naming convention: [objectname].obj.save.before.py

**Conversion Checklist**:
- [ ] Convert Java imports to Python imports
- [ ] Replace numeric constants with MboConstants
- [ ] Convert Java error handling to service.error()
- [ ] Convert Java syntax to Python syntax
- [ ] Preserve all business logic
- [ ] Maintain validation rules
- [ ] Keep relationship calls
- [ ] Add standard header template
- [ ] Use utility functions where applicable

**Reference Files**:
- Naming: NAMING_CONVENTIONS.md
- Patterns: maximo_script_patterns_reference.md
- Utilities: maximo_utility_library.py
- Context: CLAUDE_CONTEXT.md
```

**Example**:

```
Convert the following Java class to a Maximo automation script:

**Java Class**: WorkOrderSaveBefore.java
**Class Type**: Mbo
**Launch Point**: Object Launch Point - Save Before
**Object**: WORKORDER
**Event**: Save Before

**Java Code**:
```java
public class WorkOrderSaveBefore extends Mbo {
    public void save() throws MXException {
        if (getString("WONUM") == null) {
            setError("WONUM", "Work order number is required");
        }
        if (getInt("STATUS") == 2L) {
            setError("STATUS", "Invalid status");
        }
        // Business logic here
    }
}
```

**Business Logic**:
- Validates work order number is not null
- Validates work order status is valid
- Sets default values for missing fields
- Updates related records

**Requirements**:
- Preserve all business logic from Java class
- Maintain all validation rules
- Convert Java patterns to Python patterns
- Use MboConstants (never numeric constants)
- Use service.error() for errors
- Follow naming convention: workorder.obj.save.before.py

**Conversion Checklist**:
- [ ] Convert Java imports to Python imports
- [ ] Replace numeric constants (2L) with MboConstants
- [ ] Convert Java error handling to service.error()
- [ ] Convert Java syntax to Python syntax
- [ ] Preserve all business logic
- [ ] Add standard header template
```

---

### 2. Object Launch Point - Save After Conversion

**Prompt Template**:

```
Convert the following Java class to a Maximo automation script:

**Java Class**: [Full Java class name]
**Class Type**: [Mbo, MboSet, etc.]
**Launch Point**: Object Launch Point - Save After
**Object**: [OBJECT_NAME]
**Event**: Save After

**Java Code**:
```java
[Paste Java code here]
```

**Business Logic**:
- [Describe what happens after save]
- [List operations performed]
- [List relationships updated]

**Requirements**:
- Preserve all post-save logic
- Maintain relationship updates
- Keep notification logic
- Convert Java patterns to Python patterns
- Follow naming convention: [objectname].obj.save.after.py

**Conversion Checklist**:
- [ ] Convert Java imports to Python imports
- [ ] Replace numeric constants with MboConstants
- [ ] Convert Java syntax to Python syntax
- [ ] Preserve all post-save logic
- [ ] Maintain relationship calls
- [ ] Keep notification/email logic
- [ ] Add standard header template
- [ ] Close all MBO sets when done
```

---

### 3. Object Launch Point - Init Conversion

**Prompt Template**:

```
Convert the following Java class to a Maximo automation script:

**Java Class**: [Full Java class name]
**Class Type**: [Mbo, MboSet, etc.]
**Launch Point**: Object Launch Point - Init
**Object**: [OBJECT_NAME]
**Event**: Initialize

**Java Code**:
```java
[Paste Java code here]
```

**Business Logic**:
- [Describe initialization logic]
- [List default values set]
- [List fields initialized]

**Requirements**:
- Preserve all initialization logic
- Maintain default value setting
- Keep field initialization
- Convert Java patterns to Python patterns
- Follow naming convention: [objectname].obj.init.py

**Conversion Checklist**:
- [ ] Convert Java imports to Python imports
- [ ] Replace numeric constants with MboConstants
- [ ] Convert Java syntax to Python syntax
- [ ] Preserve all initialization logic
- [ ] Maintain default value setting
- [ ] Keep field initialization
- [ ] Add standard header template
```

---

### 4. Attribute Launch Point - Validate Conversion

**Prompt Template**:

```
Convert the following Java class to a Maximo automation script:

**Java Class**: [Full Java class name]
**Class Type**: [Mbo, MboSet, etc.]
**Launch Point**: Attribute Launch Point - Validate
**Object**: [OBJECT_NAME]
**Field**: [FIELD_NAME]
**Event**: Validate

**Java Code**:
```java
[Paste Java code here]
```

**Business Logic**:
- [Describe validation logic]
- [List validation rules]
- [List error conditions]

**Error Messages**:
- [Error message 1]
- [Error message 2]

**Requirements**:
- Preserve all validation logic
- Maintain all validation rules
- Convert Java error handling to service.error()
- Follow naming convention: [objectname].fld.[fieldname].validate.py

**Conversion Checklist**:
- [ ] Convert Java imports to Python imports
- [ ] Replace numeric constants with MboConstants
- [ ] Convert Java error handling to service.error()
- [ ] Convert Java syntax to Python syntax
- [ ] Preserve all validation logic
- [ ] Maintain validation rules
- [ ] Add standard header template
```

---

### 5. Attribute Launch Point - Action Conversion

**Prompt Template**:

```
Convert the following Java class to a Maximo automation script:

**Java Class**: [Full Java class name]
**Class Type**: [Mbo, MboSet, etc.]
**Launch Point**: Attribute Launch Point - Action
**Object**: [OBJECT_NAME]
**Field**: [FIELD_NAME]
**Event**: Action (field change)

**Java Code**:
```java
[Paste Java code here]
```

**Business Logic**:
- [Describe action logic]
- [List operations when field changes]
- [List fields updated]

**Requirements**:
- Preserve all action logic
- Maintain field change handling
- Keep related field updates
- Convert Java patterns to Python patterns
- Use MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION for programmatic updates
- Follow naming convention: [objectname].fld.[fieldname].action.py

**Conversion Checklist**:
- [ ] Convert Java imports to Python imports
- [ ] Replace numeric constants with MboConstants
- [ ] Convert Java syntax to Python syntax
- [ ] Preserve all action logic
- [ ] Maintain field change handling
- [ ] Add standard header template
- [ ] Use MboConstants flags for programmatic updates
```

---

### 6. Action Launch Point Conversion

**Prompt Template**:

```
Convert the following Java class to a Maximo automation script:

**Java Class**: [Full Java class name]
**Class Type**: [Mbo, MboSet, etc.]
**Launch Point**: Action Launch Point
**Object**: [OBJECT_NAME]
**Action**: [ACTION_NAME]

**Java Code**:
```java
[Paste Java code here]
```

**Business Logic**:
- [Describe action logic]
- [List operations performed]
- [List records created/updated]

**Requirements**:
- Preserve all action logic
- Maintain all operations
- Keep record creation/update logic
- Convert Java patterns to Python patterns
- Follow naming convention: [objectname].action.[actionname].py

**Conversion Checklist**:
- [ ] Convert Java imports to Python imports
- [ ] Replace numeric constants with MboConstants
- [ ] Convert Java syntax to Python syntax
- [ ] Preserve all action logic
- [ ] Maintain operations
- [ ] Keep record creation/update logic
- [ ] Add standard header template
- [ ] Close all MBO sets when done
```

---

## Common Java to Python Conversion Patterns

### Pattern 1: Imports

**Java**:
```java
import psdi.mbo.*;
import psdi.server.*;
import psdi.security.*;
```

**Python**:
```python
from psdi.mbo import Mbo, MboConstants, MboSetRemote
from psdi.server import MXServer
from psdi.security import UserInfo
```

### Pattern 2: Error Handling

**Java**:
```java
setError("FIELDNAME", "Error message");
setError("FIELDNAME", "Error message", params);
```

**Python**:
```python
service.error('FIELDNAME', 'Error message')
service.error('FIELDNAME', 'Error message', ['param1', 'param2'])
```

### Pattern 3: Numeric Constants

**Java**:
```java
setValue("FIELD", value, 2L);
setValue("FIELD", value, 11L);
```

**Python**:
```python
from psdi.mbo import MboConstants

mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION | MboConstants.NOACTION)
```

### Pattern 4: Get Values

**Java**:
```java
String value = getString("FIELDNAME");
int intValue = getInt("FIELDNAME");
boolean boolValue = getBoolean("FIELDNAME");
Date dateValue = getDate("FIELDNAME");
```

**Python**:
```python
value = mbo.getString("FIELDNAME")
intValue = mbo.getInt("FIELDNAME")
boolValue = mbo.getBoolean("FIELDNAME")
dateValue = mbo.getDate("FIELDNAME")
```

### Pattern 5: Set Values

**Java**:
```java
setValue("FIELDNAME", value);
setValue("FIELDNAME", value, 2L);
setValueNull("FIELDNAME");
```

**Python**:
```python
mbo.setValue("FIELDNAME", value)
mbo.setValue("FIELDNAME", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
mbo.setValueNull("FIELDNAME")
```

### Pattern 6: Null Checks

**Java**:
```java
if (isNull("FIELDNAME")) {
    // Handle null
}
if (getString("FIELDNAME") == null) {
    // Handle null
}
```

**Python**:
```python
if mbo.isNull("FIELDNAME"):
    # Handle null
if mbo.getString("FIELDNAME") is None:
    # Handle null
```

### Pattern 7: Relationship Access

**Java**:
```java
MboSetRemote relSet = getMboSet("RELATIONSHIPNAME");
relSet.reset();
Mbo mboItem = relSet.getMbo(0);
```

**Python**:
```python
relSet = mbo.getMboSet("RELATIONSHIPNAME")
relSet.reset()
mboItem = relSet.getMbo(0)
```

### Pattern 8: Looping Through MBO Sets

**Java**:
```java
MboSetRemote mboSet = getMboSet("RELATIONSHIPNAME");
mboSet.reset();
for (int i = 0; i < mboSet.count(); i++) {
    Mbo mboItem = mboSet.getMbo(i);
    // Process mboItem
}
```

**Python**:
```python
mboSet = mbo.getMboSet("RELATIONSHIPNAME")
mboSet.reset()
cnt = mboSet.count()
for i in range(cnt):
    mboItem = mboSet.getMbo(i)
    # Process mboItem
mboSet.close()
```

### Pattern 9: User Information

**Java**:
```java
UserInfo userInfo = getUserInfo();
String userId = userInfo.getUserName();
String siteId = userInfo.getSiteId();
```

**Python**:
```python
userInfo = mbo.getUserInfo()
userId = userInfo.getUserName()
siteId = userInfo.getSiteId()
```

### Pattern 10: Date Handling

**Java**:
```java
Date currentDate = new Date();
SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
String formattedDate = sdf.format(currentDate);
```

**Python**:
```python
from java.util import Date
from java.text import SimpleDateFormat

currentDate = Date()
sdf = SimpleDateFormat("yyyy-MM-dd")
formattedDate = sdf.format(currentDate)
```

### Pattern 11: Logging

**Java**:
```java
MXLogger logger = MXLoggerFactory.getLogger("maximo.script");
logger.info("Information message");
logger.error("Error message");
```

**Python**:
```python
from psdi.util.logging import MXLoggerFactory

logger = MXLoggerFactory.getLogger("maximo.script")
logger.info("Information message")
logger.error("Error message")
```

### Pattern 12: Database Operations

**Java**:
```java
Connection conn = MXServer.getMXServer().getDBManager().getConnection();
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery("SELECT * FROM TABLE");
```

**Python**:
```python
from psdi.server import MXServer
from java.sql import Statement, Connection, ResultSet

mxServer = MXServer.getMXServer()
conn = mxServer.getDBManager().getConnection()
stmt = conn.createStatement()
rs = stmt.executeQuery("SELECT * FROM TABLE")
# ... process results ...
rs.close()
stmt.close()
conn.close()
```

---

## Step-by-Step Conversion Process

### Step 1: Analyze Java Class

**Prompt Template**:

```
Analyze the following Java class and identify:

1. **Class Type**: [Mbo, MboSet, MboRemote, etc.]
2. **Launch Point Type**: [Object, Attribute, Action, Cron]
3. **Event Type**: [save, validate, init, action, etc.]
4. **Object Name**: [OBJECT_NAME]
5. **Field Name**: [FIELD_NAME] (if Attribute launch point)
6. **Action Name**: [ACTION_NAME] (if Action launch point)
7. **Business Logic**: [Summary of what the class does]
8. **Dependencies**: [List of dependent classes/objects]
9. **Relationships**: [List of relationships used]
10. **Error Handling**: [List of error conditions and messages]

**Java Code**:
```java
[Paste Java code here]
```

Provide detailed analysis of the Java class structure and functionality.
```

### Step 2: Map Java to Python Patterns

**Prompt Template**:

```
Convert the following Java patterns to Python patterns:

**Java Code**:
```java
[Paste Java code here]
```

**Conversion Requirements**:
- Convert all Java imports to Python imports
- Replace all numeric constants with MboConstants
- Convert Java error handling to service.error()
- Convert Java syntax to Python syntax
- Preserve all business logic
- Maintain all validation rules

**Reference**:
- Patterns: maximo_script_patterns_reference.md
- Conversion: Common Java to Python Conversion Patterns section

Provide Python equivalent code with all conversions applied.
```

### Step 3: Create Python Script

**Prompt Template**:

```
Create a complete Maximo automation script from the following Java class:

**Java Class**: [Full Java class name]
**Converted Python Code**: [From Step 2]
**Script Name**: [Based on naming convention]

**Requirements**:
- Include standard header template
- Use proper naming convention
- Use MboConstants (never numeric constants)
- Use service.error() for errors
- Close all MBO sets when done
- Add proper comments
- Use utility functions where applicable

**Reference**:
- Header: script_header_template.py
- Naming: NAMING_CONVENTIONS.md
- Utilities: maximo_utility_library.py

Provide complete Python script ready for use.
```

---

## Complete Conversion Prompt (All-in-One)

**Prompt Template**:

```
Convert the following Java class to a Maximo automation script:

**Java Class**: [Full Java class name]
**Java Code**:
```java
[Paste complete Java code here]
```

**Conversion Requirements**:

1. **Analysis**:
   - Identify class type (Mbo, MboSet, etc.)
   - Determine launch point type (Object, Attribute, Action, Cron)
   - Identify event type (save, validate, init, action, etc.)
   - Map business logic and requirements

2. **Conversion**:
   - Convert Java imports to Python imports
   - Replace numeric constants with MboConstants
   - Convert Java error handling to service.error()
   - Convert Java syntax to Python syntax
   - Preserve all business logic
   - Maintain all validation rules

3. **Script Creation**:
   - Use proper naming convention: [determine from analysis]
   - Include standard header template
   - Add proper comments
   - Use utility functions where applicable
   - Close all MBO sets when done

4. **Validation**:
   - Ensure all business logic is preserved
   - Verify all validations are maintained
   - Check all relationships are preserved
   - Confirm error handling is correct
   - Validate MboConstants usage (no numeric constants)

**Reference Files**:
- Naming: NAMING_CONVENTIONS.md
- Patterns: maximo_script_patterns_reference.md
- Utilities: maximo_utility_library.py
- Header: script_header_template.py
- Context: CLAUDE_CONTEXT.md

**Provide**:
1. Analysis of Java class
2. Converted Python code
3. Complete script with header
4. Conversion notes (what changed and why)
```

---

## Conversion Checklist

### Analysis Phase
- [ ] Identify class type (Mbo, MboSet, etc.)
- [ ] Determine launch point type (Object, Attribute, Action, Cron)
- [ ] Identify event type (save, validate, init, action, etc.)
- [ ] Map object name
- [ ] Map field name (if Attribute launch point)
- [ ] Map action name (if Action launch point)
- [ ] Understand business logic
- [ ] Identify dependencies
- [ ] Map relationships
- [ ] Identify error handling

### Conversion Phase
- [ ] Convert Java imports to Python imports
- [ ] Replace numeric constants with MboConstants
- [ ] Convert Java error handling to service.error()
- [ ] Convert Java syntax to Python syntax
- [ ] Preserve all business logic
- [ ] Maintain all validation rules
- [ ] Keep relationship logic
- [ ] Preserve error messages

### Script Creation Phase
- [ ] Determine script name using naming convention
- [ ] Add standard header template
- [ ] Add proper comments
- [ ] Use utility functions where applicable
- [ ] Close all MBO sets when done
- [ ] Add proper error handling
- [ ] Add logging if needed

### Validation Phase
- [ ] Verify all business logic is preserved
- [ ] Check all validations are maintained
- [ ] Confirm all relationships are preserved
- [ ] Validate error handling is correct
- [ ] Check MboConstants usage (no numeric constants)
- [ ] Verify script follows naming convention
- [ ] Confirm header is complete
- [ ] Check utility function usage

---

## Common Conversion Issues and Solutions

### Issue 1: Numeric Constants

**Problem**: Java code uses numeric constants like `2L`, `11L`

**Solution**: Replace with `MboConstants` flags:
```python
# Java: setValue("FIELD", value, 2L)
# Python: mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

### Issue 2: Error Handling

**Problem**: Java code uses `setError()` method

**Solution**: Convert to `service.error()`:
```python
# Java: setError("FIELD", "Error message")
# Python: service.error('FIELD', 'Error message')
```

### Issue 3: Relationship Access

**Problem**: Java code doesn't reset or close MBO sets

**Solution**: Always reset and close:
```python
# Add reset() and close() calls
mboSet = mbo.getMboSet("RELATIONSHIPNAME")
mboSet.reset()
# ... use mboSet ...
mboSet.close()
```

### Issue 4: Implicit Variables

**Problem**: Java code uses `this` or implicit context

**Solution**: Use implicit `mbo` variable:
```python
# Java: this.getString("FIELD")
# Python: mbo.getString("FIELD")
```

### Issue 5: Method Calls

**Problem**: Java method names vs Python method names

**Solution**: Use Maximo Python API:
```python
# Java: getString("FIELD")
# Python: mbo.getString("FIELD")
```

---

## Example: Complete Conversion

**Java Class**:
```java
public class WorkOrderSaveBefore extends Mbo {
    public void save() throws MXException {
        if (getString("WONUM") == null) {
            setError("WONUM", "Work order number is required");
        }
        if (getInt("STATUS") == 2L) {
            setError("STATUS", "Invalid status");
        }
        if (isNull("SITEID")) {
            UserInfo userInfo = getUserInfo();
            setValue("SITEID", userInfo.getSiteId());
        }
    }
}
```

**Converted Python Script**:
```python
################
# Script:
# Object Launch Point
#
# Launch Point: WorkOrderSaveBefore
# Object: WORKORDER
#
# Author: [Your Name]
#
# Revision:
# Date        User                        Comment
# [YYYY-MM-DD] [Your Name]                 Initial creation - Converted from WorkOrderSaveBefore.java
################

from psdi.mbo import MboConstants
from psdi.server import MXServer

# Validate work order number
if mbo.getString("WONUM") is None:
    service.error('WONUM', 'Work order number is required')

# Validate work order status
if mbo.getInt("STATUS") == MboConstants.STATUS_ACTIVE:  # Replace 2L with appropriate constant
    service.error('STATUS', 'Invalid status')

# Auto-populate site ID if missing
if mbo.isNull("SITEID"):
    userInfo = mbo.getUserInfo()
    siteId = userInfo.getSiteId()
    mbo.setValue("SITEID", siteId, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

---

## Best Practices for Conversion

### 1. Preserve Business Logic
- Maintain all business rules
- Keep all validation logic
- Preserve relationship handling
- Maintain error handling behavior

### 2. Follow Python Best Practices
- Use proper Python syntax
- Add descriptive comments
- Use utility functions where applicable
- Close all resources (MBO sets, connections)

### 3. Follow Maximo Standards
- Use MboConstants (never numeric constants)
- Use service.error() for errors
- Follow naming conventions
- Include standard header

### 4. Test and Validate
- Verify all business logic works
- Check all validations pass
- Confirm relationships work
- Validate error handling

---

## Summary

This prompt file provides:

✅ **Conversion Templates** - Ready-to-use prompts for all script types  
✅ **Common Patterns** - Java to Python conversion patterns  
✅ **Step-by-Step Process** - Detailed conversion workflow  
✅ **Conversion Checklist** - Complete checklist for conversion  
✅ **Common Issues** - Solutions for common conversion problems  
✅ **Best Practices** - Guidelines for successful conversion  
✅ **Examples** - Real-world conversion examples  

**Usage**: Copy and customize these prompts when requesting Java-to-Python conversion from coding agents.

---

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: Based on IBM Maximo Automation Script best practices

