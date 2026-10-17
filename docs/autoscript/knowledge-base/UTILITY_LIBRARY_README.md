# Maximo Utility Library - Usage Guide

## Overview

The `maximo_utility_library.py` is a generic, reusable library containing common functions for IBM Maximo automation scripts. This library provides standardized functions that can be used across all Maximo automation scripts to reduce code duplication and improve maintainability.

## Features

- **User and Group Operations**: Check user membership in groups, get user groups, check security groups
- **Type Conversions**: Safe getters for MBO fields with default values
- **Validations**: Common validation functions for fields
- **Date and Time Utilities**: Date formatting and parsing functions
- **MBO Operations**: Safe MBO set operations and value setting
- **Error Handling**: Standardized error handling functions
- **SQL Utilities**: Database query execution helpers
- **Field Flag Operations**: Readonly, required field management
- **Common Checks**: Interactive mode, application name, user checks

## Importing the Library

**Note**: In Maximo automation scripts, you cannot directly import Python files. Instead, copy the functions you need into your script, or use the library as a reference to copy specific functions.

### Option 1: Copy Functions to Your Script

Copy the functions you need directly into your automation script:

```python
from psdi.mbo import MboConstants
from psdi.server import MXServer

# Copy the function you need from the library
def checkUserInGroup(mbo, userid, groupList):
    try:
        mxServer = MXServer.getMXServer()
        userInfo = mbo.getThisMboSet().getUserInfo()
        guSet = mxServer.getMboSet("GROUPUSER", userInfo)
        guSet.setWhere("userid='" + userid + "' and groupname in (" + groupList + ")")
        guSet.reset()
        return not guSet.isEmpty()
    except Exception, e:
        return False

# Use the function
if checkUserInGroup(mbo, user, "'ALOGMGR', 'SRINVANALYST', 'INVMGR'"):
    # User is in one of the groups
    pass
```

### Option 2: Use as Reference

Use the library as a reference guide and adapt the functions to your needs.

## Usage Examples

### User and Group Operations

#### Check if User is in Group

```python
from psdi.mbo import MboConstants
from psdi.server import MXServer

# Copy function from library
def checkUserInGroup(mbo, userid, groupList):
    try:
        mxServer = MXServer.getMXServer()
        userInfo = mbo.getThisMboSet().getUserInfo()
        guSet = mxServer.getMboSet("GROUPUSER", userInfo)
        guSet.setWhere("userid='" + userid + "' and groupname in (" + groupList + ")")
        guSet.reset()
        return not guSet.isEmpty()
    except Exception, e:
        return False

# Usage
if checkUserInGroup(mbo, user, "'ALOGMGR', 'SRINVANALYST', 'INVMGR'"):
    mbo.setFieldFlag("MINLEVEL", MboConstants.READONLY, False)
else:
    mbo.setFieldFlag("MINLEVEL", MboConstants.READONLY, True)
```

#### Check if User is in Single Group

```python
def checkUserInSingleGroup(mbo, userid, groupName):
    try:
        mxServer = MXServer.getMXServer()
        userInfo = mbo.getThisMboSet().getUserInfo()
        guSet = mxServer.getMboSet("GROUPUSER", userInfo)
        guSet.setWhere("userid='" + userid + "' and groupname='" + groupName + "'")
        guSet.reset()
        return not guSet.isEmpty()
    except Exception, e:
        return False

# Usage
if checkUserInSingleGroup(mbo, user, "MAXADMIN"):
    # User is admin
    pass
```

#### Get Person Email

```python
def getPersonEmail(personid, mbo):
    try:
        mxServer = MXServer.getMXServer()
        userInfo = mbo.getThisMboSet().getUserInfo()
        personSet = mxServer.getMboSet("PERSON", userInfo)
        personSet.setWhere("personid='" + personid + "'")
        personSet.reset()
        if not personSet.isEmpty():
            personMbo = personSet.getMbo(0)
            email = personMbo.getString("PRIMARYEMAIL")
            personSet.close()
            return email if email else ""
        personSet.close()
    except Exception, e:
        pass
    return ""

# Usage
email = getPersonEmail("PERSON001", mbo)
if email:
    MXServer.sendEMail([email], "admin@example.com", "Subject", "Body")
```

### Type Conversions

#### Safe Get String

```python
def safeGetString(mbo, fieldName, defaultValue=""):
    try:
        if mbo.isNull(fieldName):
            return defaultValue
        return mbo.getString(fieldName)
    except Exception, e:
        return defaultValue

# Usage
status = safeGetString(mbo, "STATUS", "UNKNOWN")
description = safeGetString(mbo, "DESCRIPTION", "")
```

#### Safe Get Integer

```python
def safeGetInt(mbo, fieldName, defaultValue=0):
    try:
        if mbo.isNull(fieldName):
            return defaultValue
        return mbo.getInt(fieldName)
    except Exception, e:
        return defaultValue

# Usage
quantity = safeGetInt(mbo, "QUANTITY", 0)
totalCost = safeGetInt(mbo, "TOTALCOST", 0)
```

### Validations

#### Validate Required Field

```python
def validateRequiredField(mbo, fieldName, fieldLabel="Field"):
    try:
        if mbo.isNull(fieldName):
            service.error(fieldLabel, 'is required')
            return False
        return True
    except Exception, e:
        service.error('Validation Error', 'Error validating field: ' + str(e))
        return False

# Usage
if not validateRequiredField(mbo, "ITEMNUM", "Item Number"):
    return  # Error already set
```

#### Validate Field Value

```python
def validateFieldValue(mbo, fieldName, allowedValues, fieldLabel="Field"):
    try:
        value = mbo.getString(fieldName)
        if value not in allowedValues:
            service.error(fieldLabel, 'must be one of: ' + ', '.join(allowedValues))
            return False
        return True
    except Exception, e:
        service.error('Validation Error', 'Error validating field: ' + str(e))
        return False

# Usage
if not validateFieldValue(mbo, "STATUS", ("ACTIVE", "INACTIVE"), "Status"):
    return  # Error already set
```

#### Validate Numeric Range

```python
def validateNumericRange(mbo, fieldName, minValue=None, maxValue=None, fieldLabel="Field"):
    try:
        value = mbo.getDouble(fieldName)
        if minValue is not None and value < minValue:
            service.error(fieldLabel, 'must be at least ' + str(minValue))
            return False
        if maxValue is not None and value > maxValue:
            service.error(fieldLabel, 'must be at most ' + str(maxValue))
            return False
        return True
    except Exception, e:
        service.error('Validation Error', 'Error validating field: ' + str(e))
        return False

# Usage
if not validateNumericRange(mbo, "QUANTITY", minValue=1, maxValue=1000, fieldLabel="Quantity"):
    return  # Error already set
```

### Date and Time Utilities

#### Get Current Date

```python
def getCurrentDate():
    try:
        return MXServer.getMXServer().getDate()
    except Exception, e:
        return None

# Usage
today = getCurrentDate()
mbo.setValue("CHANGEDATE", today, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

#### Format Date

```python
from java.text import SimpleDateFormat

def formatDate(date, formatString="MM/dd/yyyy"):
    try:
        if date is None:
            return ""
        sdf = SimpleDateFormat(formatString)
        return sdf.format(date)
    except Exception, e:
        return ""

# Usage
today = MXServer.getMXServer().getDate()
dateStr = formatDate(today, "MM/dd/yyyy")
whereClause = "SHIFTDATE = to_date('" + dateStr + "','mm/dd/yyyy')"
```

### MBO Operations

#### Safe Set Value

```python
def safeSetValue(mbo, fieldName, value, useFlags=True):
    try:
        if useFlags:
            mbo.setValue(fieldName, value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
        else:
            mbo.setValue(fieldName, value)
        return True
    except Exception, e:
        return False

# Usage
safeSetValue(mbo, "STATUS", "ACTIVE", True)
safeSetValue(mbo, "DESCRIPTION", "New description", True)
```

#### Get MBO Set Safely

```python
def getMboSetSafely(mbo, relationshipName, whereClause=None):
    try:
        mboSet = mbo.getMboSet(relationshipName)
        if whereClause:
            mboSet.setWhere(whereClause)
            mboSet.reset()
        return mboSet
    except Exception, e:
        return None

# Usage
assetSet = getMboSetSafely(mbo, "ASSET", "status='ACTIVE'")
if assetSet:
    if not assetSet.isEmpty():
        asset = assetSet.getMbo(0)
        # Process asset
    assetSet.close()
```

### Field Flag Operations

#### Set Field Readonly

```python
def setFieldReadonly(mbo, fieldName, readonly=True):
    try:
        mbo.setFieldFlag(fieldName, MboConstants.READONLY, readonly)
        return True
    except Exception, e:
        return False

# Usage
setFieldReadonly(mbo, "STATUS", True)  # Make readonly
setFieldReadonly(mbo, "STATUS", False)  # Remove readonly
```

### Error Handling

#### Set Error Safe

```python
def setErrorSafe(p0, p1, p2):
    global errorkey, errorgroup, params
    errorkey = 'InfoParameters3'
    errorgroup = 'AutoScript'
    params = [p0, p1, p2]

# Usage
if mbo.isNull("ITEMNUM"):
    setErrorSafe('Please choose', 'an item number', 'before proceeding')
    return
```

## Best Practices

1. **Copy Functions**: Since Maximo scripts can't import Python files directly, copy the functions you need into your script.

2. **Error Handling**: Always use try-except blocks when using utility functions.

3. **Close MBO Sets**: Always close MBO sets when done to free resources:
   ```python
   assetSet = mbo.getMboSet("ASSET")
   # Use assetSet
   assetSet.close()
   ```

4. **Use MboConstants**: Always use MboConstants flags, never numeric values:
   ```python
   # ✅ CORRECT
   mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
   
   # ❌ WRONG
   mbo.setValue("FIELD", value, 2L)  # BAD!
   ```

5. **Validate Input**: Use validation functions before processing data.

6. **Safe Operations**: Use safe getters and setters to avoid errors with null values.

## Function Categories

### User and Group Operations
- `checkUserInGroup(mbo, userid, groupList)` - Check if user is in any of the groups
- `checkUserInSingleGroup(mbo, userid, groupName)` - Check if user is in a specific group
- `getUserGroups(mbo, userid)` - Get all groups for a user
- `checkUserInSecurityGroup(mbo, userid, securityGroup)` - Check security group membership
- `getPersonEmail(personid, mbo)` - Get person's email address
- `getUserInfo(mbo)` - Get UserInfo from MBO
- `getSystemUserInfo()` - Get system UserInfo

### Type Conversions
- `safeGetString(mbo, fieldName, defaultValue="")` - Safe get string with default
- `safeGetInt(mbo, fieldName, defaultValue=0)` - Safe get integer with default
- `safeGetDouble(mbo, fieldName, defaultValue=0.0)` - Safe get double with default
- `safeGetBoolean(mbo, fieldName, defaultValue=False)` - Safe get boolean with default
- `safeGetDate(mbo, fieldName, defaultValue=None)` - Safe get date with default
- `formatDate(date, formatString="MM/dd/yyyy")` - Format date to string
- `parseDateString(dateString, formatString="MM/dd/yyyy")` - Parse string to date

### Validations
- `validateRequiredField(mbo, fieldName, fieldLabel="Field")` - Validate required field
- `validateFieldValue(mbo, fieldName, allowedValues, fieldLabel="Field")` - Validate field value
- `validateNumericRange(mbo, fieldName, minValue=None, maxValue=None, fieldLabel="Field")` - Validate numeric range
- `validateStringLength(mbo, fieldName, minLength=None, maxLength=None, fieldLabel="Field")` - Validate string length

### Date and Time Utilities
- `getCurrentDate()` - Get current date from Maximo server
- `formatDateForSQL(date, formatString="MM/dd/yyyy")` - Format date for SQL WHERE clauses

### MBO Operations
- `safeSetValue(mbo, fieldName, value, useFlags=True)` - Safe set value with flags
- `safeSetValueNull(mbo, fieldName)` - Safe set field to null
- `getMboSetSafely(mbo, relationshipName, whereClause=None)` - Safe get MBO set
- `getOwnerSafely(mbo)` - Safe get owner MBO
- `closeMboSetSafely(mboSet)` - Safe close MBO set

### Error Handling
- `setErrorSafe(p0, p1, p2)` - Set error using standard format
- `raiseError(fieldLabel, message, detail="")` - Raise service error

### SQL Utilities
- `executeQuery(userInfo, query)` - Execute SQL query
- `executeQueryAndClose(userInfo, query)` - Execute query and close connection

### Field Flag Operations
- `setFieldReadonly(mbo, fieldName, readonly=True)` - Set/remove readonly flag
- `setFieldRequired(mbo, fieldName, required=True)` - Set/remove required flag
- `setMboReadonly(mbo, readonly=True)` - Set/remove readonly on entire MBO

### Common Checks
- `isInteractive()` - Check if running in interactive mode
- `getCurrentApp(mbo)` - Get current application name
- `getCurrentUser()` - Get current user ID

### MBO Set Operations
- `getMboSetCount(mboSet)` - Get count of MBO set
- `isMboSetEmpty(mboSet)` - Check if MBO set is empty
- `getFirstMbo(mboSet)` - Get first MBO from set
- `loopMboSet(mboSet, callback)` - Loop through MBO set with callback

## Notes

- All functions follow Maximo best practices
- Functions use MboConstants flags instead of numeric values
- Functions include proper error handling
- Functions are designed to be reusable across different scripts
- Functions follow the patterns found in existing AutoScripts

## Maintenance

When adding new functions to the library:

1. Follow the existing function patterns
2. Include proper error handling
3. Use MboConstants flags
4. Add docstrings with examples
5. Update this README with new functions

