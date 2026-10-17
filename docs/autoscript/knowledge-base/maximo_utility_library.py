"""
MAXIMO AUTOMATION UTILITY LIBRARY
=================================
Generic reusable library functions for IBM Maximo automation scripts.
This library contains common functions that can be used across all Maximo automation scripts.

Usage:
    from psdi.mbo import MboConstants
    from psdi.server import MXServer
    # Import utility functions from this library
    # Example: userInGroup = checkUserInGroup(mbo, user, groupList)
"""

# ============================================================================
# REQUIRED IMPORTS
# ============================================================================

from psdi.mbo import Mbo
from psdi.mbo import MboConstants
from psdi.mbo import MboSetRemote
from psdi.server import MXServer
from psdi.security import UserInfo
from java.util import Date
from java.text import SimpleDateFormat
from java.sql import Statement
from java.sql import ResultSet

# ============================================================================
# USER AND GROUP OPERATIONS
# ============================================================================

def checkUserInGroup(mbo, userid, groupList):
    """
    Check if a user is in any of the specified groups.
    
    Args:
        mbo (Mbo): The MBO object (can be any MBO)
        userid (str): User ID to check
        groupList (str): Comma-separated list of group names in SQL IN format
                        Example: "'GROUP1', 'GROUP2', 'GROUP3'"
    
    Returns:
        bool: True if user is in at least one of the groups, False otherwise
    
    Example:
        if checkUserInGroup(mbo, user, "'ALOGMGR', 'SRINVANALYST', 'INVMGR'"):
            # User is in one of the groups
            pass
    """
    try:
        mxServer = MXServer.getMXServer()
        userInfo = mbo.getThisMboSet().getUserInfo()
        guSet = mxServer.getMboSet("GROUPUSER", userInfo)
        guSet.setWhere("userid='" + userid + "' and groupname in (" + groupList + ")")
        guSet.reset()
        return not guSet.isEmpty()
    except Exception, e:
        return False


def checkUserInSingleGroup(mbo, userid, groupName):
    """
    Check if a user is in a specific group.
    
    Args:
        mbo (Mbo): The MBO object (can be any MBO)
        userid (str): User ID to check
        groupName (str): Group name to check
    
    Returns:
        bool: True if user is in the group, False otherwise
    
    Example:
        if checkUserInSingleGroup(mbo, user, "MAXADMIN"):
            # User is MAXADMIN
            pass
    """
    try:
        mxServer = MXServer.getMXServer()
        userInfo = mbo.getThisMboSet().getUserInfo()
        guSet = mxServer.getMboSet("GROUPUSER", userInfo)
        guSet.setWhere("userid='" + userid + "' and groupname='" + groupName + "'")
        guSet.reset()
        return not guSet.isEmpty()
    except Exception, e:
        return False


def getUserGroups(mbo, userid):
    """
    Get all groups for a specific user.
    
    Args:
        mbo (Mbo): The MBO object (can be any MBO)
        userid (str): User ID
    
    Returns:
        list: List of group names, empty list if error or no groups
    
    Example:
        groups = getUserGroups(mbo, user)
        if "MAXADMIN" in groups:
            # User is admin
            pass
    """
    groups = []
    try:
        mxServer = MXServer.getMXServer()
        userInfo = mbo.getThisMboSet().getUserInfo()
        guSet = mxServer.getMboSet("GROUPUSER", userInfo)
        guSet.setWhere("userid='" + userid + "'")
        guSet.reset()
        count = guSet.count()
        for i in range(count):
            groupMbo = guSet.getMbo(i)
            groups.append(groupMbo.getString("GROUPNAME"))
        guSet.close()
    except Exception, e:
        pass
    return groups


def checkUserInSecurityGroup(mbo, userid, securityGroup):
    """
    Check if a user is in a security group (PERSONGROUPTEAM).
    
    Args:
        mbo (Mbo): The MBO object (can be any MBO)
        userid (str): User ID to check
        securityGroup (str): Security group name
    
    Returns:
        bool: True if user is in the security group, False otherwise
    
    Example:
        if checkUserInSecurityGroup(mbo, user, "ENGINEERS"):
            # User is in ENGINEERS group
            pass
    """
    try:
        mxServer = MXServer.getMXServer()
        userInfo = mbo.getThisMboSet().getUserInfo()
        pgSet = mxServer.getMboSet("PERSONGROUPTEAM", userInfo)
        pgSet.setWhere("personid='" + userid + "' and groupname='" + securityGroup + "'")
        pgSet.reset()
        return not pgSet.isEmpty()
    except Exception, e:
        return False


def getPersonEmail(personid, mbo):
    """
    Get primary email address for a person.
    
    Args:
        personid (str): Person ID
        mbo (Mbo): The MBO object (can be any MBO)
    
    Returns:
        str: Email address, empty string if not found or error
    
    Example:
        email = getPersonEmail("PERSON001", mbo)
        if email:
            MXServer.sendEMail([email], "admin@example.com", "Subject", "Body")
    """
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


def getUserInfo(mbo):
    """
    Get UserInfo object from MBO.
    
    Args:
        mbo (Mbo): The MBO object
    
    Returns:
        UserInfo: UserInfo object, None if error
    
    Example:
        userInfo = getUserInfo(mbo)
        if userInfo:
            # Use userInfo
            pass
    """
    try:
        return mbo.getThisMboSet().getUserInfo()
    except Exception, e:
        return None


def getSystemUserInfo():
    """
    Get system UserInfo object.
    
    Returns:
        UserInfo: System UserInfo object, None if error
    
    Example:
        sysUserInfo = getSystemUserInfo()
        mboSet = mxServer.getMboSet("OBJECT", sysUserInfo)
    """
    try:
        return MXServer.getMXServer().getSystemUserInfo()
    except Exception, e:
        return None

# ============================================================================
# TYPE CONVERSIONS
# ============================================================================

def safeGetString(mbo, fieldName, defaultValue=""):
    """
    Safely get string value from MBO field, returning default if null or error.
    
    Args:
        mbo (Mbo): The MBO object
        fieldName (str): Field name
        defaultValue (str): Default value to return if null or error
    
    Returns:
        str: Field value or default value
    
    Example:
        status = safeGetString(mbo, "STATUS", "UNKNOWN")
    """
    try:
        if mbo.isNull(fieldName):
            return defaultValue
        return mbo.getString(fieldName)
    except Exception, e:
        return defaultValue


def safeGetInt(mbo, fieldName, defaultValue=0):
    """
    Safely get integer value from MBO field, returning default if null or error.
    
    Args:
        mbo (Mbo): The MBO object
        fieldName (str): Field name
        defaultValue (int): Default value to return if null or error
    
    Returns:
        int: Field value or default value
    
    Example:
        quantity = safeGetInt(mbo, "QUANTITY", 0)
    """
    try:
        if mbo.isNull(fieldName):
            return defaultValue
        return mbo.getInt(fieldName)
    except Exception, e:
        return defaultValue


def safeGetDouble(mbo, fieldName, defaultValue=0.0):
    """
    Safely get double value from MBO field, returning default if null or error.
    
    Args:
        mbo (Mbo): The MBO object
        fieldName (str): Field name
        defaultValue (float): Default value to return if null or error
    
    Returns:
        float: Field value or default value
    
    Example:
        cost = safeGetDouble(mbo, "TOTALCOST", 0.0)
    """
    try:
        if mbo.isNull(fieldName):
            return defaultValue
        return mbo.getDouble(fieldName)
    except Exception, e:
        return defaultValue


def safeGetBoolean(mbo, fieldName, defaultValue=False):
    """
    Safely get boolean value from MBO field, returning default if null or error.
    
    Args:
        mbo (Mbo): The MBO object
        fieldName (str): Field name
        defaultValue (bool): Default value to return if null or error
    
    Returns:
        bool: Field value or default value
    
    Example:
        active = safeGetBoolean(mbo, "ACTIVE", False)
    """
    try:
        if mbo.isNull(fieldName):
            return defaultValue
        return mbo.getBoolean(fieldName)
    except Exception, e:
        return defaultValue


def safeGetDate(mbo, fieldName, defaultValue=None):
    """
    Safely get date value from MBO field, returning default if null or error.
    
    Args:
        mbo (Mbo): The MBO object
        fieldName (str): Field name
        defaultValue (Date): Default date to return if null or error
    
    Returns:
        Date: Field value or default value
    
    Example:
        today = safeGetDate(mbo, "CHANGEDATE", MXServer.getMXServer().getDate())
    """
    try:
        if mbo.isNull(fieldName):
            return defaultValue
        return mbo.getDate(fieldName)
    except Exception, e:
        return defaultValue


def formatDate(date, formatString="MM/dd/yyyy"):
    """
    Format a date object to string.
    
    Args:
        date (Date): Date object to format
        formatString (str): Format pattern (default: "MM/dd/yyyy")
    
    Returns:
        str: Formatted date string, empty string if error
    
    Example:
        today = MXServer.getMXServer().getDate()
        dateStr = formatDate(today, "MM/dd/yyyy")
    """
    try:
        if date is None:
            return ""
        sdf = SimpleDateFormat(formatString)
        return sdf.format(date)
    except Exception, e:
        return ""


def parseDateString(dateString, formatString="MM/dd/yyyy"):
    """
    Parse a date string to Date object.
    
    Args:
        dateString (str): Date string to parse
        formatString (str): Format pattern (default: "MM/dd/yyyy")
    
    Returns:
        Date: Parsed Date object, None if error
    
    Example:
        dateObj = parseDateString("12/31/2023", "MM/dd/yyyy")
    """
    try:
        if not dateString:
            return None
        sdf = SimpleDateFormat(formatString)
        return sdf.parse(dateString)
    except Exception, e:
        return None

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validateRequiredField(mbo, fieldName, fieldLabel="Field"):
    """
    Validate that a required field is not null.
    
    Args:
        mbo (Mbo): The MBO object
        fieldName (str): Field name to validate
        fieldLabel (str): Human-readable field label for error message
    
    Returns:
        bool: True if valid (not null), False if null (error set)
    
    Example:
        if not validateRequiredField(mbo, "ITEMNUM", "Item Number"):
            return  # Error already set
    """
    try:
        if mbo.isNull(fieldName):
            service.error(fieldLabel, 'is required')
            return False
        return True
    except Exception, e:
        service.error('Validation Error', 'Error validating field: ' + str(e))
        return False


def validateFieldValue(mbo, fieldName, allowedValues, fieldLabel="Field"):
    """
    Validate that a field value is in the allowed values list.
    
    Args:
        mbo (Mbo): The MBO object
        fieldName (str): Field name to validate
        allowedValues (list/tuple): Allowed values
        fieldLabel (str): Human-readable field label for error message
    
    Returns:
        bool: True if valid, False if invalid (error set)
    
    Example:
        if not validateFieldValue(mbo, "STATUS", ("ACTIVE", "INACTIVE"), "Status"):
            return  # Error already set
    """
    try:
        value = mbo.getString(fieldName)
        if value not in allowedValues:
            service.error(fieldLabel, 'must be one of: ' + ', '.join(allowedValues))
            return False
        return True
    except Exception, e:
        service.error('Validation Error', 'Error validating field: ' + str(e))
        return False


def validateNumericRange(mbo, fieldName, minValue=None, maxValue=None, fieldLabel="Field"):
    """
    Validate that a numeric field is within a range.
    
    Args:
        mbo (Mbo): The MBO object
        fieldName (str): Field name to validate
        minValue (int/float): Minimum allowed value (None for no minimum)
        maxValue (int/float): Maximum allowed value (None for no maximum)
        fieldLabel (str): Human-readable field label for error message
    
    Returns:
        bool: True if valid, False if invalid (error set)
    
    Example:
        if not validateNumericRange(mbo, "QUANTITY", minValue=1, maxValue=1000, fieldLabel="Quantity"):
            return  # Error already set
    """
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


def validateStringLength(mbo, fieldName, minLength=None, maxLength=None, fieldLabel="Field"):
    """
    Validate that a string field length is within a range.
    
    Args:
        mbo (Mbo): The MBO object
        fieldName (str): Field name to validate
        minLength (int): Minimum allowed length (None for no minimum)
        maxLength (int): Maximum allowed length (None for no maximum)
        fieldLabel (str): Human-readable field label for error message
    
    Returns:
        bool: True if valid, False if invalid (error set)
    
    Example:
        if not validateStringLength(mbo, "DESCRIPTION", minLength=10, maxLength=100, fieldLabel="Description"):
            return  # Error already set
    """
    try:
        value = mbo.getString(fieldName)
        if value is None:
            value = ""
        length = len(value)
        if minLength is not None and length < minLength:
            service.error(fieldLabel, 'must be at least ' + str(minLength) + ' characters')
            return False
        if maxLength is not None and length > maxLength:
            service.error(fieldLabel, 'must be at most ' + str(maxLength) + ' characters')
            return False
        return True
    except Exception, e:
        service.error('Validation Error', 'Error validating field: ' + str(e))
        return False

# ============================================================================
# DATE AND TIME UTILITIES
# ============================================================================

def getCurrentDate():
    """
    Get current date from Maximo server.
    
    Returns:
        Date: Current date, None if error
    
    Example:
        today = getCurrentDate()
        mbo.setValue("CHANGEDATE", today, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
    """
    try:
        return MXServer.getMXServer().getDate()
    except Exception, e:
        return None


def formatDateForSQL(date, formatString="MM/dd/yyyy"):
    """
    Format a date for use in SQL WHERE clauses.
    
    Args:
        date (Date): Date object to format
        formatString (str): Format pattern (default: "MM/dd/yyyy")
    
    Returns:
        str: Formatted date string for SQL, empty string if error
    
    Example:
        today = getCurrentDate()
        dateStr = formatDateForSQL(today)
        whereClause = "SHIFTDATE = to_date('" + dateStr + "','mm/dd/yyyy')"
    """
    try:
        if date is None:
            return ""
        return formatDate(date, formatString)
    except Exception, e:
        return ""

# ============================================================================
# MBO OPERATIONS
# ============================================================================

def safeSetValue(mbo, fieldName, value, useFlags=True):
    """
    Safely set a value on an MBO with standard flags.
    
    Args:
        mbo (Mbo): The MBO object
        fieldName (str): Field name
        value: Value to set (any type)
        useFlags (bool): If True, use NOACCESSCHECK | NOVALIDATION flags
    
    Returns:
        bool: True if successful, False if error
    
    Example:
        safeSetValue(mbo, "STATUS", "ACTIVE", True)
    """
    try:
        if useFlags:
            mbo.setValue(fieldName, value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
        else:
            mbo.setValue(fieldName, value)
        return True
    except Exception, e:
        return False


def safeSetValueNull(mbo, fieldName):
    """
    Safely set a field to null.
    
    Args:
        mbo (Mbo): The MBO object
        fieldName (str): Field name
    
    Returns:
        bool: True if successful, False if error
    
    Example:
        safeSetValueNull(mbo, "OPTIONALFIELD")
    """
    try:
        mbo.setValueNull(fieldName)
        return True
    except Exception, e:
        return False


def getMboSetSafely(mbo, relationshipName, whereClause=None):
    """
    Safely get an MBO set with optional where clause.
    
    Args:
        mbo (Mbo): The MBO object
        relationshipName (str): Relationship name
        whereClause (str): Optional WHERE clause
    
    Returns:
        MboSetRemote: MBO set, None if error
    
    Example:
        assetSet = getMboSetSafely(mbo, "ASSET", "status='ACTIVE'")
        if assetSet:
            # Use assetSet
            pass
    """
    try:
        mboSet = mbo.getMboSet(relationshipName)
        if whereClause:
            mboSet.setWhere(whereClause)
            mboSet.reset()
        return mboSet
    except Exception, e:
        return None


def getOwnerSafely(mbo):
    """
    Safely get the owner MBO.
    
    Args:
        mbo (Mbo): The MBO object
    
    Returns:
        Mbo: Owner MBO, None if error or no owner
    
    Example:
        owner = getOwnerSafely(mbo)
        if owner and owner.isBasedOn("SR"):
            # Process SR owner
            pass
    """
    try:
        return mbo.getOwner()
    except Exception, e:
        return None


def closeMboSetSafely(mboSet):
    """
    Safely close an MBO set.
    
    Args:
        mboSet (MboSetRemote): MBO set to close
    
    Example:
        assetSet = mbo.getMboSet("ASSET")
        # Use assetSet
        closeMboSetSafely(assetSet)
    """
    try:
        if mboSet is not None:
            mboSet.close()
    except Exception, e:
        pass

# ============================================================================
# ERROR HANDLING UTILITIES
# ============================================================================

def setErrorSafe(p0, p1, p2):
    """
    Set error using standard error format.
    
    Args:
        p0 (str): First error message parameter
        p1 (str): Second error message parameter
        p2 (str): Third error message parameter
    
    Example:
        if mbo.isNull("ITEMNUM"):
            setErrorSafe('Please choose', 'an item number', 'before proceeding')
            return
    """
    global errorkey, errorgroup, params
    errorkey = 'InfoParameters3'
    errorgroup = 'AutoScript'
    params = [p0, p1, p2]


def raiseError(fieldLabel, message, detail=""):
    """
    Raise a service error with formatted message.
    
    Args:
        fieldLabel (str): Field or object label
        message (str): Error message
        detail (str): Optional detail message
    
    Example:
        if mbo.isNull("REQUIREDFIELD"):
            raiseError("Required Field", "is required", "Please enter a value")
            return
    """
    if detail:
        service.error(fieldLabel, message + ' - ' + detail)
    else:
        service.error(fieldLabel, message)

# ============================================================================
# SQL UTILITIES
# ============================================================================

def executeQuery(userInfo, query):
    """
    Execute a SQL query and return ResultSet.
    
    Args:
        userInfo (UserInfo): UserInfo object
        query (str): SQL query string
    
    Returns:
        ResultSet: Query result set, None if error
    
    Example:
        userInfo = getUserInfo(mbo)
        query = "SELECT COUNT(*) as cnt FROM WORKORDER WHERE status='ACTIVE'"
        rs = executeQuery(userInfo, query)
        if rs and rs.next():
            count = rs.getInt("cnt")
    """
    try:
        mxServer = MXServer.getMXServer()
        dbm = mxServer.getDBManager()
        conKey = userInfo.getConnectionKey()
        con = dbm.getConnection(conKey)
        stmt = con.createStatement()
        rs = stmt.executeQuery(query)
        return rs
    except Exception, e:
        return None


def executeQueryAndClose(userInfo, query):
    """
    Execute a SQL query, get result, and close connection.
    
    Args:
        userInfo (UserInfo): UserInfo object
        query (str): SQL query string
    
    Returns:
        ResultSet: Query result set, None if error
    
    Note: Caller is responsible for closing the ResultSet
    
    Example:
        userInfo = getUserInfo(mbo)
        query = "SELECT nvl(sum(quantity),0) * -1 dissue FROM matusetrans WHERE itemnum = '" + itemNum + "'"
        rs = executeQueryAndClose(userInfo, query)
        if rs and rs.next():
            value = rs.getDouble("dissue")
        # Close rs when done
    """
    try:
        mxServer = MXServer.getMXServer()
        dbm = mxServer.getDBManager()
        conKey = userInfo.getConnectionKey()
        con = dbm.getConnection(conKey)
        stmt = con.createStatement()
        rs = stmt.executeQuery(query)
        stmt.close()
        dbm.freeConnection(conKey)
        return rs
    except Exception, e:
        return None

# ============================================================================
# FIELD FLAG OPERATIONS
# ============================================================================

def setFieldReadonly(mbo, fieldName, readonly=True):
    """
    Set or remove readonly flag on a field.
    
    Args:
        mbo (Mbo): The MBO object
        fieldName (str): Field name
        readonly (bool): True to set readonly, False to remove
    
    Returns:
        bool: True if successful, False if error
    
    Example:
        setFieldReadonly(mbo, "STATUS", True)  # Make readonly
        setFieldReadonly(mbo, "STATUS", False)  # Remove readonly
    """
    try:
        mbo.setFieldFlag(fieldName, MboConstants.READONLY, readonly)
        return True
    except Exception, e:
        return False


def setFieldRequired(mbo, fieldName, required=True):
    """
    Set or remove required flag on a field.
    
    Args:
        mbo (Mbo): The MBO object
        fieldName (str): Field name
        required (bool): True to set required, False to remove
    
    Returns:
        bool: True if successful, False if error
    
    Example:
        setFieldRequired(mbo, "ITEMNUM", True)  # Make required
    """
    try:
        mbo.setFieldFlag(fieldName, MboConstants.REQUIRED, required)
        return True
    except Exception, e:
        return False


def setMboReadonly(mbo, readonly=True):
    """
    Set or remove readonly flag on entire MBO.
    
    Args:
        mbo (Mbo): The MBO object
        readonly (bool): True to set readonly, False to remove
    
    Returns:
        bool: True if successful, False if error
    
    Example:
        setMboReadonly(mbo, True)  # Make entire MBO readonly
    """
    try:
        mbo.setFlag(MboConstants.READONLY, readonly)
        return True
    except Exception, e:
        return False

# ============================================================================
# COMMON CHECKS
# ============================================================================

def isInteractive():
    """
    Check if script is running in interactive mode.
    
    Returns:
        bool: True if interactive, False otherwise
    
    Example:
        if isInteractive():
            # Code only runs in interactive mode
            pass
    """
    try:
        return interactive
    except NameError:
        return False


def getCurrentApp(mbo):
    """
    Get current application name from MBO.
    
    Args:
        mbo (Mbo): The MBO object
    
    Returns:
        str: Application name, empty string if error
    
    Example:
        appName = getCurrentApp(mbo)
        if appName in ('MRGWO', 'NRVEWO', 'ENGWO'):
            # Process for specific apps
            pass
    """
    try:
        return mbo.getThisMboSet().getParentApp()
    except Exception, e:
        return ""


def getCurrentUser():
    """
    Get current user ID.
    
    Returns:
        str: User ID, empty string if error
    
    Example:
        currentUser = getCurrentUser()
        if currentUser == "MAXADMIN":
            # Admin user
            pass
    """
    try:
        return user
    except NameError:
        return ""

# ============================================================================
# MBO SET OPERATIONS
# ============================================================================

def getMboSetCount(mboSet):
    """
    Safely get count of MBO set.
    
    Args:
        mboSet (MboSetRemote): MBO set
    
    Returns:
        int: Count of MBOs, 0 if error or empty
    
    Example:
        assetSet = mbo.getMboSet("ASSET")
        count = getMboSetCount(assetSet)
    """
    try:
        if mboSet is None:
            return 0
        return mboSet.count()
    except Exception, e:
        return 0


def isMboSetEmpty(mboSet):
    """
    Safely check if MBO set is empty.
    
    Args:
        mboSet (MboSetRemote): MBO set
    
    Returns:
        bool: True if empty or error, False if has items
    
    Example:
        assetSet = mbo.getMboSet("ASSET")
        if not isMboSetEmpty(assetSet):
            # Process assetSet
            pass
    """
    try:
        if mboSet is None:
            return True
        return mboSet.isEmpty()
    except Exception, e:
        return True


def getFirstMbo(mboSet):
    """
    Safely get first MBO from set.
    
    Args:
        mboSet (MboSetRemote): MBO set
    
    Returns:
        Mbo: First MBO, None if error or empty
    
    Example:
        assetSet = mbo.getMboSet("ASSET")
        firstAsset = getFirstMbo(assetSet)
        if firstAsset:
            # Process firstAsset
            pass
    """
    try:
        if mboSet is None or mboSet.isEmpty():
            return None
        return mboSet.getMbo(0)
    except Exception, e:
        return None


def loopMboSet(mboSet, callback):
    """
    Safely loop through MBO set with callback function.
    
    Args:
        mboSet (MboSetRemote): MBO set to loop through
        callback (function): Callback function that takes Mbo as parameter
    
    Returns:
        int: Number of MBOs processed, 0 if error
    
    Example:
        def processAsset(assetMbo):
            status = assetMbo.getString("STATUS")
            # Process asset
        
        assetSet = mbo.getMboSet("ASSET")
        count = loopMboSet(assetSet, processAsset)
    """
    count = 0
    try:
        if mboSet is None:
            return 0
        mboSet.reset()
        mboCount = mboSet.count()
        for i in range(mboCount):
            mboItem = mboSet.getMbo(i)
            if mboItem:
                callback(mboItem)
                count += 1
    except Exception, e:
        pass
    return count

# ============================================================================
# END OF UTILITY LIBRARY
# ============================================================================

