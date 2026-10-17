"""
MAXIMO AUTOMATION SCRIPT PATTERNS REFERENCE
===========================================
This file contains comprehensive syntax patterns and code templates
for building Maximo automation scripts based on IBM Maximo Automation Script
documentation and best practices.

This file is generic and can be used across any Maximo project.
"""

# ============================================================================
# IMPORTS - Common Imports Used in Maximo Scripts
# ============================================================================

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

# ============================================================================
# ERROR HANDLING PATTERNS
# ============================================================================

# Pattern 1: Custom setError Function
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
# if mbo.isNull("ITEMNUM"):
#     setError('Please choose', 'an item number', 'before proceeding')
#     return

# Pattern 2: Service Error Method
# service.error('Field Name', 'error message')
# service.error('SR', 'obsmatnew', [status])
# service.error("Error when DELETE", " Cannot delete the CREW: '"+v_crew+"' Associated with an ACTIVE PM: '"+v_pmnum+"'")

# Pattern 3: Service Error with Status Check
# if status in ('IMREVIEW','FMREVIEW','APPR','RESOLVED'):
#     service.error("SR","obsmatnew",[status])

# Pattern 4: Conditional Error with Field Validation
# if mbo.isNull("TOTALCOST"):
#     service.error('Total Cost', 'can not be empty!')
# elif not totalCost > 0:
#     service.error('Total Cost', 'must be greater than zero!')

# ============================================================================
# WARNING PATTERNS
# ============================================================================

# Pattern 1: Service Warning
# service.warning('Warning Message')

# Pattern 2: Application Warning Exception
# from psdi.util import MXApplicationWarningException
# raise MXApplicationWarningException('Warning message')

# ============================================================================
# RELATIONSHIP CALLING PATTERNS
# ============================================================================

# Pattern 1: Standard Relationship (getMboSet)
# mboSet = mbo.getMboSet("RELATIONSHIPNAME")
# Example:
#   woSet = mbo.getMboSet("WORKORDER")
#   assetSet = mbo.getMboSet("ASSET")
#   polineSet = mbo.getMboSet("POLINE")

# Pattern 2: Relationship with Where Clause
# mboSet = mbo.getMboSet("RELATIONSHIPNAME")
# mboSet.setWhere("WHERE_CLAUSE")
# mboSet.reset()
# Example:
#   activePMSet = mbo.getMboSet("ACTIVEPM")
#   activePMSet.setWhere("status = 'ACTIVE'")
#   activePMSet.reset()

# Pattern 3: Temporary Relationship (using $ prefix)
# mboSet = mbo.getMboSet("$TEMPRELATIONSHIP", "OBJECTNAME", "WHERE_CLAUSE")
# Example:
#   maxRevSet = mbo.getMboSet("$MAXACTLOGSET", "ACTIVITYLOG", 
#                             "dept = '" + dept + "' and SHIFT = '" + origShift + 
#                             "' and SHIFTDATE= to_date('" + vCurrentDate + "','mm/dd/yyyy')")
#   newWarrantyClaimSet = mbo.getMboSet("$PLUSTCLAIM", "PLUSTCLAIM", "1=0")
#   relatedSet = mbo.getMboSet("$RELATEDUOR$", "RELATEDRECORD", 
#                              "CLASS='UORMASTER' AND RECORDKEY='" + ticketId + "'")

# Pattern 4: Relationship from MXServer
# mxServer = MXServer.getMXServer()
# userInfo = mbo.getThisMboSet().getUserInfo()
# mboSet = mxServer.getMboSet("OBJECTNAME", userInfo)
# mboSet.setWhere("WHERE_CLAUSE")
# Example:
#   invSet = mxServer.getMboSet("INVENTORY", userInfo)
#   whereClause = "ITEMNUM = '" + itemNum + "' and SITEID = 'SITE1'"
#   invSet.setWhere(whereClause)

# Pattern 5: Relationship from Owner
# owner = mbo.getOwner()
# ownerSet = owner.getMboSet("RELATIONSHIPNAME")
# Example:
#   ticket = mbo.getOwner()
#   if ticket and ticket.isBasedOn("SR"):
#       status = ticket.getString("STATUS")

# ============================================================================
# LOOPING THROUGH MBO SETS
# ============================================================================

# Pattern 1: Loop with count() and range()
# mboSet = mbo.getMboSet("RELATIONSHIPNAME")
# mboSet.reset()
# count = mboSet.count()
# for i in range(count):
#     mboItem = mboSet.getMbo(i)
#     # Process mboItem
#     value = mboItem.getString("FIELDNAME")

# Pattern 2: Loop with moveFirst() and moveNext()
# mboSet = mbo.getMboSet("RELATIONSHIPNAME")
# mbo = mboSet.moveFirst()
# while mbo:
#     # Process mbo
#     value = mbo.getString("FIELDNAME")
#     mbo = mboSet.moveNext()

# Pattern 3: Loop with moveFirst() and check
# polineSet = mbo.getMboSet("POLINE")
# poline = polineSet.moveFirst()
# while poline:
#     # Process poline
#     status = poline.getString("PL1")
#     poline.setValue("RECEIPTSCOMPLETE", True, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
#     poline = polineSet.moveNext()

# Pattern 4: Loop with isEmpty() check
# mboSet = mbo.getMboSet("RELATIONSHIPNAME")
# if not mboSet.isEmpty():
#     mboItem = mboSet.getMbo(0)
#     value = mboItem.getString("FIELDNAME")

# Pattern 5: Loop with count() check before processing
# dupActLogSet = dupMbo.getMboSet("WO2ACTLOG")
# if dupActLogSet.count() > 0:
#     dupActLogMbo = dupActLogSet.getMbo(0)
#     # Process dupActLogMbo

# ============================================================================
# SETTING VALUES
# ============================================================================

# Pattern 1: Basic setValue
# mbo.setValue("FIELDNAME", value)

# Pattern 2: setValue with Constants (NOACCESSCHECK, NOVALIDATION)
# mbo.setValue("FIELDNAME", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
# Example:
#   asset.setValue('SUBSTATUS', subStatus, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
#   asset.setValue('STATUS', subStatus, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
#   mbo.setValue("GLCREDITACCT", glCredit, MboConstants.NOVALIDATION | MboConstants.NOACCESSCHECK)

# Pattern 3: setValueNull
# mbo.setValueNull("FIELDNAME")
# Example:
#   mbo.setValueNull("STOREROOM")
#   mbo.setValueNull("GLDEBITACCT")
#   mbo.setValueNull("BINNUM")

# Pattern 4: setValue with Previous Value
# previousValue = mbo.getMboValue("FIELDNAME").getPreviousValue().asString()
# newValue = calculateNewValue(previousValue)
# mbo.setValue("FIELDNAME", newValue)

# Pattern 5: setValue with Date
# from java.util import Date
# today = Date()
# mbo.setValue("CHANGEDATE", today)
# mbo.setValue("SHIFTDATE", today)

# Pattern 6: setValue with Calculated Value
# calculatedValue = field1 * field2
# mbo.setValue("CALCULATEDFIELD", calculatedValue, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# ============================================================================
# FIELD TYPES HANDLING
# ============================================================================

# Pattern 1: String Field
# value = mbo.getString("FIELDNAME")
# mbo.setValue("FIELDNAME", "string_value")

# Pattern 2: Integer Field
# value = mbo.getInt("FIELDNAME")
# mbo.setValue("FIELDNAME", 123)

# Pattern 3: Long Field
# value = mbo.getLong("FIELDNAME")
# mbo.setValue("FIELDNAME", 123456L)

# Pattern 4: Double/Float Field
# value = mbo.getDouble("FIELDNAME")
# mbo.setValue("FIELDNAME", 123.45)

# Pattern 5: Boolean Field
# value = mbo.getBoolean("FIELDNAME")
# mbo.setValue("FIELDNAME", True)
# mbo.setValue("FIELDNAME", False)
# mbo.setValue("FIELDNAME", 1)  # True
# mbo.setValue("FIELDNAME", 0)  # False

# Pattern 6: Date Field
# from java.util import Date
# today = Date()
# dateValue = mbo.getDate("FIELDNAME")
# mbo.setValue("FIELDNAME", today)

# Pattern 7: DateTime Field
# from java.util import Calendar
# cal = Calendar.getInstance()
# mbo.setValue("DATETIMEFIELD", cal.getTime())

# Pattern 8: Check if Null
# if mbo.isNull("FIELDNAME"):
#     # Handle null case
#     mbo.setValue("FIELDNAME", defaultValue)

# Pattern 9: Check if Modified
# if mbo.isModified("FIELDNAME"):
#     # Handle modified case
#     previousValue = mbo.getMboValue("FIELDNAME").getPreviousValue().asString()

# ============================================================================
# FIELD FLAGS AND READONLY
# ============================================================================

# Pattern 1: Set Field Readonly
# mbo.setFieldFlag("FIELDNAME", MboConstants.READONLY, True)
# Example:
#   mbo.setFieldFlag("CHECKED", MboConstants.READONLY, 1)

# Pattern 2: Remove Field Readonly
# mbo.setFieldFlag("FIELDNAME", MboConstants.READONLY, False)
# Example:
#   mbo.setFieldFlag("MINLEVEL", MboConstants.READONLY, False)

# Pattern 3: Set Entire MBO Readonly
# mbo.setFlag(MboConstants.READONLY, True)
# Example:
#   mbo.setFlag(MboConstants.READONLY, True)

# Pattern 4: Set Required Field
# mbo.setFieldFlag("FIELDNAME", MboConstants.REQUIRED, True)

# ============================================================================
# EXCEPTION HANDLING
# ============================================================================

# Pattern 1: Try-Except Block
# try:
#     # Code that might raise exception
#     value = mbo.getString("FIELDNAME")
# except Exception, e:
#     # Handle exception
#     service.error('Error', 'An error occurred: ' + str(e))

# Pattern 2: Try-Except with Specific Handling
# try:
#     # Code block
#     result = performOperation()
# except Exception, e:
#     logger.error("Error in operation: " + str(e))
#     service.error('Operation', 'failed')

# Pattern 3: Raise Exception for Testing
# raise Exception("Test exception message")

# ============================================================================
# DATE AND TIME HANDLING
# ============================================================================

# Pattern 1: Get Current Date
# from java.util import Date
# today = Date()
# mxServer = MXServer.getMXServer()
# today = mxServer.getDate()

# Pattern 2: Format Date
# from java.text import SimpleDateFormat
# today = Date()
# vCurrentDate = SimpleDateFormat("MM/dd/yyyy").format(today)

# Pattern 3: Use Date in Where Clause
# vCurrentDate = SimpleDateFormat("MM/dd/yyyy").format(today)
# whereClause = "SHIFTDATE = to_date('" + vCurrentDate + "','mm/dd/yyyy')"

# Pattern 4: Calendar Operations
# from java.util import Calendar
# cal = Calendar.getInstance()
# mbo.setValue("ENTERDATE", cal.getTime())

# ============================================================================
# MBO OPERATIONS
# ============================================================================

# Pattern 1: Get Owner
# owner = mbo.getOwner()
# ownerValue = owner.getString("FIELDNAME")

# Pattern 2: Check Owner Type
# owner = mbo.getOwner()
# if owner and owner.isBasedOn("SR"):
#     # Process SR owner
#     status = owner.getString("STATUS")

# Pattern 3: Duplicate MBO
# dupMbo = mbo.duplicate()
# dupMbo.setValue("FIELDNAME", "new_value")

# Pattern 4: Add New MBO to Set
# mboSet = mbo.getMboSet("RELATIONSHIPNAME")
# newMbo = mboSet.add()
# newMbo.setValue("FIELDNAME", value)

# Pattern 5: Add New MBO with Position
# historySet = asset.getMboSet("PLUSTASSETSTHIST")
# newHistory = historySet.add(2L)  # Add at position 2

# Pattern 6: Get MBO from Set
# mboSet = mbo.getMboSet("RELATIONSHIPNAME")
# mboItem = mboSet.getMbo(0)  # Get first MBO
# value = mboItem.getString("FIELDNAME")

# Pattern 7: Close MBO Set
# mboSet.close()
# Example:
#   hasAsset.close()
#   woMboSet.close()

# Pattern 8: Save MBO Set
# mboSet.save()
# Example:
#   dupActLogSet.save()
#   historySet.save()

# ============================================================================
# USER AND SESSION INFORMATION
# ============================================================================

# Pattern 1: Get User Info
# userInfo = mbo.getThisMboSet().getUserInfo()
# mxServer = MXServer.getMXServer()
# userInfo = MXServer.getMXServer().getSystemUserInfo()

# Pattern 2: Get Current User
# currentUser = user  # Built-in variable

# Pattern 3: Check User in Group
# def userInGroup(grouplist):
#     guSet = MXServer.getMXServer().getMboSet("GROUPUSER", mbo.getUserInfo())
#     guSet.setWhere("userid='" + user + "' and groupname in (" + grouplist + ")")
#     if guSet.isEmpty():
#         return False
#     return True

# Pattern 4: Check Interactive Mode
# if interactive:
#     # Code runs only in interactive mode
#     service.error('Error', 'message')

# Pattern 5: Get Application Name
# appName = mbo.getThisMboSet().getParentApp()
# app = app  # Built-in variable for current application

# Pattern 6: Web Client Session
# from psdi.webclient.system.controller import WebClientEvent
# wcs = service.webclientsession()
# if wcs is not None:
#     newEvent = WebClientEvent("changeapp", wcs.getCurrentApp().getId(), 
#                                "APPNAME", None, None, None, id, wcs)
#     wcs.queueEvent(newEvent)

# Pattern 7: UIContext for Web Client
# from psdi.common.context import UIContext
# context = UIContext.getCurrentContext()
# if context is not None:
#     wcs = context.getWebClientSession()
#     if wcs is not None:
#         databean = wcs.getDataBean("appname")
#         if databean:
#             databean.refreshTable()

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

# Pattern 1: Direct SQL Query
# from java.sql import Statement
# from java.sql import ResultSet
# mxServer = MXServer.getMXServer()
# dbm = mxServer.getDBManager()
# conKey = userInfo.getConnectionKey()
# con = dbm.getConnection(conKey)
# stmt = con.createStatement()
# query = "SELECT nvl(sum(quantity),0) * -1 dissue FROM matusetrans WHERE itemnum = '" + itemNum + "'"
# rs = stmt.executeQuery(query)
# rs.next()
# value = rs.getDouble("dissue")
# stmt.close()
# dbm.freeConnection(conKey)

# Pattern 2: Prepared Statement
# from java.sql import PreparedStatement
# prepStmt = con.prepareStatement("SELECT * FROM table WHERE field = ?")
# prepStmt.setString(1, value)
# rs = prepStmt.executeQuery()

# ============================================================================
# LOGGING PATTERNS
# ============================================================================

# Pattern 1: Get Logger
# from psdi.util.logging import MXLoggerFactory
# logger = service.getLogger("maximo.script")
# logger.info("Message")
# logger.error("Error message")
# logger.warning("Warning message")
# logger.debug("Debug message")

# Pattern 2: Log with Variables
# logger.info("Check Step 1")
# logger.info("Current MATUSETRANSID: " + mbo.getString("MATUSETRANSID"))
# logger.info("Issue To Workorder: " + wonum + ". Car Asset: " + carAssetnum)

# ============================================================================
# VALIDATION PATTERNS
# ============================================================================

# Pattern 1: Field Validation in Field Launch Point
# if mbo.isModified("FIELDNAME"):
#     previousValue = mbo.getMboValue("FIELDNAME").getPreviousValue().asString()
#     newValue = mbo.getString("FIELDNAME")
#     if previousValue == 'OLD' and newValue == 'NEW':
#         mbo.setValue("OTHERFIELD", value, MboConstants.NOVALIDATION | MboConstants.NOACCESSCHECK)

# Pattern 2: Required Field Validation
# if mbo.isNull("REQUIREDFIELD"):
#     service.error('Field Name', 'is required')
#     return

# Pattern 3: Value Range Validation
# value = mbo.getInt("FIELDNAME")
# if value < 0 or value > 100:
#     service.error('Field Name', 'must be between 0 and 100')
#     return

# Pattern 4: Status-based Validation
# status = mbo.getString("STATUS")
# if status in ('IMREVIEW','FMREVIEW','APPR','RESOLVED'):
#     service.error("SR", "obsmatnew", [status])
#     return

# Pattern 5: Conditional Validation
# if condition1 and condition2:
#     if mbo.isNull("FIELDNAME"):
#         service.error('Field Name', 'is mandatory', 'when condition is met')
#         return

# ============================================================================
# ACTION PATTERNS
# ============================================================================

# Pattern 1: Field Action Launch Point
# if not mbo.isNull("FIELDNAME"):
#     # Perform action when field is set
#     relatedSet = mbo.getMboSet("RELATIONSHIP")
#     if not relatedSet.isEmpty():
#         relatedMbo = relatedSet.getMbo(0)
#         value = relatedMbo.getString("VALUE")
#         mbo.setValue("TARGETFIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# Pattern 2: Action with Multiple Conditions
# if condition1:
#     if condition2:
#         # Perform action
#         mbo.setValue("FIELDNAME", value)

# ============================================================================
# INITIALIZATION PATTERNS
# ============================================================================

# Pattern 1: Object Init Launch Point
# # Set default values
# mbo.setValue("FIELDNAME", defaultValue, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
# 
# # Set readonly based on conditions
# if condition:
#     mbo.setFieldFlag("FIELDNAME", MboConstants.READONLY, True)
# else:
#     mbo.setFieldFlag("FIELDNAME", MboConstants.READONLY, False)

# Pattern 2: Field Init Launch Point
# # Set field value from owner
# owner = mbo.getOwner()
# if owner:
#     ownerValue = owner.getString("OWNERFIELD")
#     mbo.setValue("FIELDNAME", ownerValue, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# ============================================================================
# SAVE PATTERNS (BEFORE/AFTER)
# ============================================================================

# Pattern 1: Before Save - Validation
# if onadd:
#     # Validate for new records
#     if mbo.isNull("REQUIREDFIELD"):
#         service.error('Field Name', 'is required')
#         return
# 
# if onupdate:
#     # Validate for updates
#     if mbo.isModified("FIELDNAME"):
#         # Handle modification
#         pass
# 
# if ondelete:
#     # Validate for deletion
#     if condition:
#         service.error('Cannot delete', 'reason message')
#         return

# Pattern 2: Before Save - Auto-populate Fields
# if onadd or onupdate:
#     # Auto-populate related fields
#     relatedSet = mbo.getMboSet("RELATIONSHIP")
#     if not relatedSet.isEmpty():
#         relatedMbo = relatedSet.getMbo(0)
#         mbo.setValue("FIELDNAME", relatedMbo.getString("VALUE"), 
#                      MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# Pattern 3: Before Save - Complex Logic
# if interactive and appName in ('MRGWO', 'NRVEWO', 'ENGWO'):
#     asset = wo.getMboSet("ASSET").moveFirst()
#     if mbo.isNull('SUBSTATUS'):
#         setError('Please choose', 'a', 'Sub Status')
#     elif mbo.getString('SUBSTATUS').upper() == assetStatus.upper():
#         setError('The status you selected', 'is the same as the asset current status.', 
#                  'Please choose a different sub status')
#     else:
#         asset.setValue('SUBSTATUS', subStatus, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# Pattern 4: After Save - Trigger Related Updates
# # After saving, update related records
# relatedSet = mbo.getMboSet("RELATIONSHIP")
# relatedMbo = relatedSet.add()
# relatedMbo.setValue("FIELDNAME", value)
# relatedSet.save()

# Pattern 5: Save with AppBean
# from psdi.webclient.system.beans import AppBean
# session = service.webclientsession()
# if session is not None:
#     appbean = session.getCurrentApp().getAppBean()
#     if appbean is not None:
#         appbean.save()

# ============================================================================
# COMPLEX OPERATIONS PATTERNS
# ============================================================================

# Pattern 1: Duplicate with Related Records
# dupMbo = mbo.duplicate()
# dupSet = dupMbo.getMboSet("RELATIONSHIP")
# origSet = mbo.getMboSet("RELATIONSHIP")
# origCount = origSet.count()
# if origCount > 0:
#     for i in range(origCount):
#         dupItem = dupSet.add()
#         origItem = origSet.getMbo(i)
#         dupItem.setValue("FIELDNAME", origItem.getString("FIELDNAME"))
#     dupSet.save()

# Pattern 2: Find Maximum Value
# maxRevSet = mbo.getMboSet("$MAXREVSET", "OBJECTNAME", "where_clause")
# maxRevSet.reset()
# maxRev = 1
# revCount = maxRevSet.count()
# for i in range(revCount):
#     revMbo = maxRevSet.getMbo(i)
#     newRev = revMbo.getInt("REVISION")
#     if maxRev < newRev:
#         maxRev = newRev
# mbo.setValue("REVISION", maxRev + 1)

# Pattern 3: Aggregate Calculations
# totalValue = 0.0
# mboSet = mbo.getMboSet("RELATIONSHIP")
# mboSet.reset()
# count = mboSet.count()
# for i in range(count):
#     itemMbo = mboSet.getMbo(i)
#     totalValue = totalValue + itemMbo.getDouble("VALUE")
# mbo.setValue("TOTAL", totalValue, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# Pattern 4: Conditional Status Updates
# allComplete = True
# mboSet = mbo.getMboSet("RELATIONSHIP")
# item = mboSet.moveFirst()
# while item:
#     if item.getBoolean("COMPLETE") == False:
#         allComplete = False
#     item = mboSet.moveNext()
# 
# if allComplete:
#     mbo.setValue("STATUS", "COMPLETE", MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
# else:
#     mbo.setValue("STATUS", "PARTIAL", MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# ============================================================================
# SCRIPT CONFIGURATION TEMPLATE
# ============================================================================

# Standard Script Configuration JSON
scriptConfig = """{
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
            "attributeName": "FIELDNAME",  # For ATTRIBUTE launch points
            "actionName": "ACTIONNAME",    # For ACTION launch points
            "save": true,
            "add": true,
            "update": true,
            "delete": false,
            "beforeSave": true,            # For OBJECT save launch points
            "afterCommit": false,         # For OBJECT save launch points
            "initializeValue": true,       # For OBJECT init launch points
            "validate": true,             # For ATTRIBUTE launch points
            "runAction": true              # For ATTRIBUTE launch points
        }
    ]
}"""

# ============================================================================
# COMMON LAUNCH POINT TYPES
# ============================================================================

# OBJECT Launch Points:
# - initializeValue: Runs when object is initialized
# - save (beforeSave/afterCommit): Runs before/after save
# - add/update/delete: Control when script runs

# ATTRIBUTE Launch Points:
# - validate: Runs during field validation
# - runAction: Runs when field value changes
# - initializeValue: Runs when field is initialized

# ACTION Launch Points:
# - actionName: Custom action name

# ============================================================================
# BEST PRACTICES
# ============================================================================

# 1. Always check if interactive mode is needed
#    if interactive:
#         # User interaction code

# 2. Always close MBO sets when done
#    mboSet.close()

# 3. Use MboConstants for flags
#    MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION

# 4. Check for null values before processing
#    if not mbo.isNull("FIELDNAME"):
#         # Process field

# 5. Check if MBO set is empty before accessing
#    if not mboSet.isEmpty():
#         mbo = mboSet.getMbo(0)

# 6. Use try-except for error handling
#    try:
#         # Code
#    except Exception, e:
#         service.error('Error', str(e))

# 7. Use logging for debugging
#    logger = service.getLogger("maximo.script")
#    logger.info("Debug message")

# 8. Always validate user permissions
#    if interactive:
#         # Check user permissions

# 9. Use temporary relationships for complex queries
#    mboSet = mbo.getMboSet("$TEMPREL", "OBJECTNAME", "where_clause")

# 10. Always reset MBO sets after setting where clause
#     mboSet.setWhere("where_clause")
#     mboSet.reset()

# ============================================================================
# COMMON PATTERNS SUMMARY
# ============================================================================

# Error Handling:
# - service.error('Field', 'message')
# - setError(p0, p1, p2) function
# - try-except blocks

# Relationships:
# - mbo.getMboSet("RELATIONSHIP")
# - mbo.getMboSet("$TEMP", "OBJECT", "WHERE")
# - mxServer.getMboSet("OBJECT", userInfo)

# Looping:
# - for i in range(mboSet.count())
# - while mbo = mboSet.moveFirst(); mbo = mboSet.moveNext()

# Setting Values:
# - mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
# - mbo.setValueNull("FIELD")

# Field Types:
# - getString(), getInt(), getLong(), getDouble(), getBoolean(), getDate()
# - isNull(), isModified()

# Validation:
# - Check null, check modified, check status, check conditions

# Save Operations:
# - onadd, onupdate, ondelete flags
# - beforeSave, afterCommit

# Initialization:
# - Set defaults, set readonly, set required

# ============================================================================
# END OF REFERENCE
# ============================================================================

