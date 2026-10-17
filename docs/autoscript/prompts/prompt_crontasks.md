# Cron Task Conversion Prompt Template

**Purpose**: Systematic prompt template for converting Maximo Java CronTasks to Python automation scripts  
**Version**: 1.0.0  
**Last Updated**: 2025-11-13  
**Context**: MAS 9 upgrade - converting Java SimpleCronTask classes to Python Object Launch Point automation scripts

---

## Table of Contents

1. [Conversion Prompt Template](#conversion-prompt-template)
2. [Context Documents](#context-documents)
3. [Conversion Patterns](#conversion-patterns)
4. [Quality Checklist](#quality-checklist)
5. [Example Conversions](#example-conversions)

---

## Conversion Prompt Template

### Base Prompt for CronTask Conversion

```
I need to convert a Maximo Java CronTask to a Python automation script for MAS 9 upgrade.

**Java CronTask Information:**
- Class Name: [TMG_XXXXXXCronTask]
- Java Path: [Full path to Java file]
- Module: [Work Order/Inventory/Company/Common/etc.]
- Purpose: [Brief description of cron task functionality]
- Complexity: [Simple/Medium/Complex]

**Source Java File:**
[Paste Java source code here]

**Requirements:**
1. Convert to Python automation script with OBJECT launch point (Cron Task Instance)
2. Use proper header template with all metadata
3. Follow naming convention: [taskname].cron.action.py (lowercase)
4. Preserve all business logic from original Java
5. Implement proper parameter handling using croninstance
6. Use correct logger initialization (MXServer lookup)
7. Use proper database operations (JDBC via userInfo.getConnection())
8. Implement proper resource cleanup (close all MboSets, ResultSets, Statements)
9. Use Thread.sleep(milliseconds) instead of TimeUnit
10. Add clear comments explaining complex business logic
11. Include complete scriptConfig JSON at the end
12. Re-raise exceptions to mark cron task as failed in Maximo

**Reference Documents:**
- Use patterns from: CRONTASK_CONVERSION_LOG.md
- Follow header format from existing cron scripts
- Reference: Knowledge-base/maximo_script_patterns_reference.md

**Expected Output:**
- Complete Python automation script ready for deployment
- Proper header with all metadata and revision history
- Business logic preserved and documented
- scriptConfig JSON with Cron Task Instance launch point configuration
- Testing checklist for validation
```

---

## Context Documents

### Required Reading Before Conversion

#### 1. CronTask Conversion Log
**File:** `CRONTASK_CONVERSION_LOG.md`

**Key Information:**
- Conversion strategy and patterns
- Java vs Python differences table
- All 9 completed conversions with detailed notes
- Common issues and solutions
- Testing checklists for each conversion type

#### 2. Existing Cron Task Scripts
**Location:** `automation-scripts/cron_tasks/`

**Reference Scripts:**
1. **tmg_datapurge.cron.action.py** - Batch deletion pattern
2. **tmg_compinactive.cron.action.py** - Complex business logic with date arithmetic
3. **tmg_geninv.cron.action.py** - Invoice creation (1016 lines, complex)
4. **tmg_valclrts.cron.action.py** - Validation checks (515 lines)
5. **tmg_poclose.cron.action.py** - PO closing logic (494 lines)
6. **tmg_addcimusers.cron.action.py** - DBShortcut INSERT/DELETE (162 lines)
7. **tmg_pmwogen.cron.action.py** - PM WO generation (334 lines)
8. **tmg_measurepointwogen.cron.action.py** - Measure point WO generation (481 lines)
9. **tmg_sttupdate.cron.action.py** - Inventory summarization (1040 lines - LARGEST)

#### 3. Maximo Script Patterns
**File:** `Knowledge-base/maximo_script_patterns_reference.md`

**Key Patterns for CronTasks:**
- MboSet operations for batch processing
- Database operations via JDBC
- Date arithmetic with GregorianCalendar
- Status translation (internal vs external values)
- Resource cleanup patterns

#### 4. Naming Conventions
**Cron Task Script Names:**
- Format: `[taskname].cron.action.py`
- All lowercase
- No underscores between words in task name if original Java is camelCase
- Extension: `.cron.action.py`

**Examples:**
- `TMG_DataPurgeCronTask.java` → `tmg_datapurge.cron.action.py`
- `TMG_CompInactiveCronTask.java` → `tmg_compinactive.cron.action.py`
- `TMG_GenInvCronTask.java` → `tmg_geninv.cron.action.py`

---

## Conversion Patterns

### Pattern 1: Class Structure → Script Structure

**Java Pattern:**
```java
package tmg.common;

import psdi.server.*;
import psdi.util.*;
import java.util.*;

public class TMG_DataPurgeCronTask extends SimpleCronTask {
    
    private static final MXLogger iL = MicUtil.INTEGRATIONLOGGER;
    
    public TMG_DataPurgeCronTask() {
        super();
    }
    
    @Override
    public void cronAction() {
        try {
            iL.info("Starting cron task");
            // Business logic here
        } catch (Exception e) {
            iL.error("Error: " + e.getMessage());
        }
    }
}
```

**Python Conversion:**
```python
################
# Script: [Task Name] Cron Task
# Cron Task Action Launch Point
#
# Launch Point: [SCRIPT_NAME].CRON.ACTION
# Object: N/A (Cron Task)
# Action: Cron Task Instance Execution
#
# Author: Converted from Java CronTask ([OriginalClass].java)
# Naming Convention: [taskname].cron.action.py
# Original Java: [OriginalClass].java (package)
# Conversion Date: [Date]
################

from psdi.server import MXServer
from psdi.util.logging import MXLogger

# Initialize logger
logger = MXServer.getMXServer().lookup("LOGGING")
scriptName = "[SCRIPT_NAME].CRON.ACTION"

def main():
    """
    Main cron task execution function.
    [Description of what this cron task does]
    """
    try:
        logger.info(scriptName + ": Starting cron task")
        # Business logic here
        logger.info(scriptName + ": Cron task completed successfully")
    except Exception, e:
        logger.error(scriptName + ": Cron task failed with exception: " + str(e))
        logger.error(scriptName + ": Stack trace", e)
        # Re-raise to mark cron task as failed
        raise

# Execute main function
main()

scriptConfig="""{
    "autoscript": "[SCRIPT_NAME].CRON.ACTION",
    "description": "[Description]",
    "version": "1.0",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "[SCRIPT_NAME]_CRON",
            "launchPointType": "OBJECT",
            "active": true,
            "description": "[Description]",
            "objectName": "CRONTASKINSTANCE"
        }
    ]
}"""
```

---

### Pattern 2: Parameter Retrieval

**Java Pattern:**
```java
@Override
public void cronAction() {
    String purgeConfig = getParamAsString("PURGE_CONFIG");
    Integer batchSize = getParamAsInt("BATCH_SIZE");
    Integer waitSeconds = getParamAsInt("BATCH_WAIT_SECONDS");
    
    if (purgeConfig == null || purgeConfig.isEmpty()) {
        throw new Exception("PURGE_CONFIG parameter is required");
    }
}
```

**Python Conversion:**
```python
def main():
    """Main cron task execution function."""
    try:
        # Get cron task instance parameters
        purgeConfig = croninstance.getParamAsString("PURGE_CONFIG")
        batchSize = croninstance.getParamAsInt("BATCH_SIZE")
        waitSeconds = croninstance.getParamAsInt("BATCH_WAIT_SECONDS")
        
        # Validate required parameters
        if not purgeConfig or purgeConfig.strip() == "":
            raise Exception("PURGE_CONFIG parameter is missing or empty")
        
        if batchSize is None or batchSize <= 0:
            raise Exception("BATCH_SIZE parameter is missing or invalid")
        
        logger.info(scriptName + ": Parameters - Config: " + purgeConfig + 
                   ", BatchSize: " + str(batchSize))
        
        # Continue with business logic...
    except Exception, e:
        logger.error(scriptName + ": Error", e)
        raise
```

---

### Pattern 3: Database Operations (JDBC)

**Java Pattern:**
```java
import java.sql.*;

public void cronAction() {
    DBShortcut dbShortcut = new DBShortcut();
    dbShortcut.connect(getRunasUserInfo().getConnectionKey());
    
    String query = "SELECT * FROM COMPANIES WHERE COMPANY = ?";
    ResultSet rs = dbShortcut.executeQuery(query);
    
    while (rs.next()) {
        String company = rs.getString("COMPANY");
        // Process record
    }
    
    rs.close();
    dbShortcut.disconnect();
}
```

**Python Conversion:**
```python
from java.sql import SQLException

def queryDatabase():
    """Query database using JDBC connection."""
    connection = None
    statement = None
    resultSet = None
    
    try:
        # Get database connection
        userInfo = MXServer.getMXServer().getSystemUserInfo()
        connection = userInfo.getConnection()
        
        # Execute query
        query = "SELECT * FROM COMPANIES WHERE COMPANY = ?"
        statement = connection.prepareStatement(query)
        statement.setString(1, companyValue)
        resultSet = statement.executeQuery()
        
        # Process results
        while resultSet.next():
            company = resultSet.getString("COMPANY")
            # Process record
            
    except SQLException, e:
        logger.error(scriptName + ": Database error", e)
        raise
    finally:
        # Clean up resources
        if resultSet is not None:
            try:
                resultSet.close()
            except:
                pass
        if statement is not None:
            try:
                statement.close()
            except:
                pass
        # Note: Do NOT close connection (it's managed by MXServer)
```

---

### Pattern 4: MboSet Operations

**Java Pattern:**
```java
import psdi.mbo.*;
import psdi.server.*;

public void cronAction() throws Exception {
    MboSetRemote mboSet = null;
    try {
        MXServer mxServer = MXServer.getMXServer();
        mboSet = mxServer.getMboSet("COMPANIES", getRunasUserInfo());
        mboSet.setWhere("TYPE = 'SUPPLIER'");
        mboSet.reset();
        
        Mbo mbo = mboSet.moveFirst();
        while (mbo != null) {
            String company = mbo.getString("COMPANY");
            // Process record
            mbo = mboSet.moveNext();
        }
        
    } finally {
        if (mboSet != null) {
            mboSet.close();
        }
    }
}
```

**Python Conversion:**
```python
from psdi.mbo import MboConstants
from psdi.server import MXServer

def processMboSet():
    """Process records using MboSet."""
    mboSet = None
    
    try:
        # Get MboSet
        mxServer = MXServer.getMXServer()
        userInfo = mxServer.getSystemUserInfo()
        mboSet = mxServer.getMboSet("COMPANIES", userInfo)
        mboSet.setWhere("TYPE = 'SUPPLIER'")
        mboSet.reset()
        
        # Process records
        mbo = mboSet.moveFirst()
        while mbo is not None:
            company = mbo.getString("COMPANY")
            # Process record
            mbo = mboSet.moveNext()
            
    except Exception, e:
        logger.error(scriptName + ": Error processing MboSet", e)
        raise
    finally:
        # Always close MboSet
        if mboSet is not None:
            try:
                mboSet.close()
            except:
                pass
```

---

### Pattern 5: Thread Sleep (Wait Between Batches)

**Java Pattern:**
```java
import java.util.concurrent.TimeUnit;

public void cronAction() {
    for (int batch = 0; batch < totalBatches; batch++) {
        // Process batch
        
        // Wait before next batch
        TimeUnit.SECONDS.sleep(waitSeconds);
    }
}
```

**Python Conversion:**
```python
from java.lang import Thread

def processBatches(batchCount, waitSeconds):
    """Process batches with wait time between each."""
    for batch in range(batchCount):
        logger.info(scriptName + ": Processing batch " + str(batch + 1))
        
        # Process batch logic here
        
        # Wait before next batch (convert seconds to milliseconds)
        if batch < batchCount - 1:  # Don't wait after last batch
            logger.debug(scriptName + ": Waiting " + str(waitSeconds) + " seconds")
            Thread.sleep(waitSeconds * 1000)  # milliseconds
```

---

### Pattern 6: Date Arithmetic

**Java Pattern:**
```java
import java.util.*;

public boolean isOlderThan(Date dateToCheck, int days) {
    GregorianCalendar calendar = new GregorianCalendar();
    calendar.setTime(dateToCheck);
    calendar.add(Calendar.DATE, days);
    Date futureDate = calendar.getTime();
    
    Date currentDate = MXServer.getMXServer().getDate();
    return futureDate.before(currentDate);
}
```

**Python Conversion:**
```python
from java.util import GregorianCalendar, Calendar, Date

def isDateOlderThan(dateToCheck, daysToAdd, compareDate):
    """
    Check if a date plus specified days is before the compare date.
    
    Args:
        dateToCheck (Date): Base date to check
        daysToAdd (int): Number of days to add
        compareDate (Date): Date to compare against
        
    Returns:
        bool: True if dateToCheck + daysToAdd is before compareDate
    """
    calendar = GregorianCalendar()
    calendar.setTime(dateToCheck)
    calendar.add(Calendar.DATE, daysToAdd)
    futureDate = calendar.getTime()
    
    return futureDate.before(compareDate)

# Usage example
def checkInactivityPeriod():
    """Check if company has been inactive for 5 years (1825 days)."""
    currentDate = MXServer.getMXServer().getDate()
    lastActivityDate = company.getDate("TMG_STATUSDATE")
    
    if isDateOlderThan(lastActivityDate, 1825, currentDate):
        logger.info(scriptName + ": Company inactive for over 5 years")
        return True
    return False
```

---

### Pattern 7: Status Translation (Internal vs External)

**Java Pattern:**
```java
import psdi.translate.*;

public void cronAction() {
    Mbo poMbo = poSet.getMbo(0);
    
    // Get internal status value from external display value
    String internalStatus = poMbo.getTranslator()
        .toInternalString("POSTATUS", poMbo.getString("status"));
    
    if (internalStatus.equals("APPR")) {
        // Status is Approved
    }
}
```

**Python Conversion:**
```python
def checkPOStatus(poMbo):
    """
    Check PO status using internal status values.
    
    Args:
        poMbo: PO MBO object
        
    Returns:
        bool: True if PO is approved
    """
    # Get internal status value
    internalStatus = poMbo.getTranslator().toInternalString(
        "POSTATUS", 
        poMbo.getString("status")
    )
    
    # Check against internal status value (not display value)
    if internalStatus == "APPR":
        logger.debug(scriptName + ": PO is approved")
        return True
    
    return False
```

---

### Pattern 8: Batch Deletion with ROWNUM (Oracle)

**Java Pattern:**
```java
public void deleteBatch(String tableName, String whereClause, int batchSize) {
    DBShortcut dbShortcut = new DBShortcut();
    dbShortcut.connect(getRunasUserInfo().getConnectionKey());
    
    String deleteSQL = "DELETE FROM " + tableName + 
                      " WHERE ROWNUM <= " + batchSize + 
                      " AND " + whereClause;
    
    int rowsDeleted = dbShortcut.executeUpdate(deleteSQL);
    dbShortcut.commit();
    
    return rowsDeleted;
}
```

**Python Conversion:**
```python
from java.sql import SQLException

def deleteBatch(tableName, whereClause, batchSize):
    """
    Delete records in batch using ROWNUM (Oracle-specific).
    
    Args:
        tableName (str): Table to delete from
        whereClause (str): WHERE condition
        batchSize (int): Number of records to delete
        
    Returns:
        int: Number of rows deleted
    """
    connection = None
    statement = None
    
    try:
        # Get database connection
        userInfo = MXServer.getMXServer().getSystemUserInfo()
        connection = userInfo.getConnection()
        
        # Build delete SQL with ROWNUM
        deleteSQL = ("DELETE FROM " + tableName + 
                    " WHERE ROWNUM <= " + str(batchSize) + 
                    " AND " + whereClause)
        
        logger.debug(scriptName + ": Executing: " + deleteSQL)
        
        # Execute delete
        statement = connection.createStatement()
        rowsDeleted = statement.executeUpdate(deleteSQL)
        
        # Commit transaction
        connection.commit()
        
        logger.info(scriptName + ": Deleted " + str(rowsDeleted) + " rows")
        return rowsDeleted
        
    except SQLException, e:
        logger.error(scriptName + ": Delete failed", e)
        if connection is not None:
            try:
                connection.rollback()
            except:
                pass
        raise
    finally:
        if statement is not None:
            try:
                statement.close()
            except:
                pass

# Note: ROWNUM is Oracle-specific
# For DB2: Use FETCH FIRST n ROWS ONLY
# For SQL Server: Use TOP n
```

---

### Pattern 9: DBShortcut INSERT Operations

**Java Pattern:**
```java
import psdi.util.DBShortcut;

public void insertRecords() {
    DBShortcut dbShortcut = new DBShortcut();
    dbShortcut.connect(getRunasUserInfo().getConnectionKey());
    
    String insertSQL = "INSERT INTO CIMPRODUSER (USERID, PERSONID) " +
                      "SELECT USERID, PERSONID FROM MAXUSER " +
                      "WHERE STATUS = 'ACTIVE'";
    
    int rowsInserted = dbShortcut.executeUpdate(insertSQL);
    dbShortcut.commit();
    
    dbShortcut.disconnect();
}
```

**Python Conversion:**
```python
from java.sql import SQLException

def insertRecords():
    """Insert records using direct SQL via JDBC."""
    connection = None
    statement = None
    
    try:
        # Get database connection
        userInfo = MXServer.getMXServer().getSystemUserInfo()
        connection = userInfo.getConnection()
        
        # Build INSERT SQL
        insertSQL = ("INSERT INTO CIMPRODUSER (USERID, PERSONID) " +
                    "SELECT USERID, PERSONID FROM MAXUSER " +
                    "WHERE STATUS = 'ACTIVE'")
        
        logger.debug(scriptName + ": Executing: " + insertSQL)
        
        # Execute insert
        statement = connection.createStatement()
        rowsInserted = statement.executeUpdate(insertSQL)
        
        # Commit transaction
        connection.commit()
        
        logger.info(scriptName + ": Inserted " + str(rowsInserted) + " rows")
        
    except SQLException, e:
        logger.error(scriptName + ": Insert failed", e)
        if connection is not None:
            try:
                connection.rollback()
            except:
                pass
        raise
    finally:
        if statement is not None:
            try:
                statement.close()
            except:
                pass
```

---

## Quality Checklist

### Before Submitting Converted Script

- [ ] **Header Complete**
  - [ ] Script title and description
  - [ ] Launch point details (Cron Task Instance)
  - [ ] Author and conversion date
  - [ ] Original Java file path referenced
  - [ ] Complete revision history from Java (all PPM numbers, dates, authors)
  - [ ] Clear description of cron task functionality

- [ ] **Code Quality**
  - [ ] Main function defined and called
  - [ ] All business logic preserved from Java
  - [ ] Comments explain complex logic
  - [ ] Functions extracted for reusability
  - [ ] No deprecated methods used
  - [ ] Proper indentation (4 spaces)

- [ ] **Parameter Handling**
  - [ ] Parameters retrieved using croninstance
  - [ ] Parameter validation (null, empty, invalid)
  - [ ] Parameters logged for debugging
  - [ ] Parameter documentation in header

- [ ] **Logging**
  - [ ] Logger initialized via MXServer.lookup("LOGGING")
  - [ ] Script name constant defined
  - [ ] Info logging for major steps
  - [ ] Debug logging for detailed info
  - [ ] Error logging with exception details
  - [ ] Consistent log message format

- [ ] **Database Operations**
  - [ ] JDBC connection via userInfo.getConnection()
  - [ ] Proper SQL parameter binding (no string concatenation for values)
  - [ ] Commit/rollback handling
  - [ ] ResultSet closed in finally block
  - [ ] Statement closed in finally block
  - [ ] Connection NOT closed (managed by MXServer)

- [ ] **Resource Management**
  - [ ] All MboSets closed in finally block
  - [ ] All ResultSets closed in finally block
  - [ ] All Statements closed in finally block
  - [ ] Try-except-finally structure for cleanup
  - [ ] No memory leaks

- [ ] **Threading**
  - [ ] Thread.sleep() uses milliseconds (seconds * 1000)
  - [ ] Wait times logged
  - [ ] No wait after final iteration

- [ ] **Exception Handling**
  - [ ] Try-except for main function
  - [ ] Exceptions logged with full stack trace
  - [ ] Exceptions re-raised to mark cron task as failed
  - [ ] Rollback on database errors
  - [ ] Specific exception types when possible

- [ ] **scriptConfig Section**
  - [ ] Complete JSON structure
  - [ ] Correct autoscript name
  - [ ] Description provided
  - [ ] Version specified
  - [ ] Active status set
  - [ ] logLevel set to "ERROR"
  - [ ] Launch point type: "OBJECT"
  - [ ] Object name: "CRONTASKINSTANCE"

- [ ] **Naming Convention**
  - [ ] File name: [taskname].cron.action.py
  - [ ] All lowercase
  - [ ] Matches script name in header

- [ ] **Testing Documentation**
  - [ ] Testing checklist included
  - [ ] Dependencies documented (tables, relationships)
  - [ ] Known limitations noted
  - [ ] Database-specific notes (Oracle ROWNUM, etc.)

---

## Example Conversions

### Example 1: Simple Batch Deletion (tmg_datapurge.cron.action.py)

**Original Java:** `TMG_DataPurgeCronTask.java` (251 lines)

```java
package tmg.common;

import psdi.server.*;
import psdi.util.*;
import java.sql.*;
import java.util.concurrent.TimeUnit;

public class TMG_DataPurgeCronTask extends SimpleCronTask {
    
    private static final MXLogger iL = MicUtil.INTEGRATIONLOGGER;
    
    @Override
    public void cronAction() {
        try {
            String purgeConfig = getParamAsString("PURGE_CONFIG");
            Integer batchSize = getParamAsInt("BATCH_SIZE");
            Integer waitSeconds = getParamAsInt("BATCH_WAIT_SECONDS");
            
            purgeTableData(purgeConfig, batchSize, waitSeconds);
            
        } catch (Exception e) {
            iL.error("Cron task failed: " + e.getMessage());
        }
    }
    
    private void purgeTableData(String config, int batchSize, int wait) {
        // Get configuration
        MboSetRemote configSet = MXServer.getMXServer()
            .getMboSet("TMG_DATAPURGECONFIG", getRunasUserInfo());
        configSet.setWhere("TMG_CONFIGNAME = '" + config + "'");
        
        if (!configSet.isEmpty()) {
            String table = configSet.getMbo(0).getString("TMG_TABLE");
            String where = configSet.getMbo(0).getString("TMG_WHERECLAUSE");
            
            // Delete in batches
            int totalDeleted = 0;
            int rowsDeleted = 0;
            
            do {
                rowsDeleted = deleteBatch(table, where, batchSize);
                totalDeleted += rowsDeleted;
                
                if (rowsDeleted > 0) {
                    TimeUnit.SECONDS.sleep(wait);
                }
            } while (rowsDeleted > 0);
            
            iL.info("Total deleted: " + totalDeleted);
        }
        configSet.close();
    }
    
    private int deleteBatch(String table, String where, int size) {
        DBShortcut db = new DBShortcut();
        db.connect(getRunasUserInfo().getConnectionKey());
        
        String sql = "DELETE FROM " + table + 
                    " WHERE ROWNUM <= " + size + 
                    " AND " + where;
        
        int deleted = db.executeUpdate(sql);
        db.commit();
        db.disconnect();
        
        return deleted;
    }
}
```

**Converted Python:** `tmg_datapurge.cron.action.py` (261 lines)

```python
################
# Script: Data Purge Cron Task
# Cron Task Action Launch Point
#
# Launch Point: TMG_DATAPURGE.CRON.ACTION
# Object: N/A (Cron Task)
# Action: Cron Task Instance Execution
#
# Author: Converted from Java CronTask (TMG_DataPurgeCronTask.java)
#
# Naming Convention: tmg_datapurge.cron.action.py
#
# Original Java: TMG_DataPurgeCronTask.java (tmg.common package)
# Conversion Date: 2025-11-06
#
# Description:
#   Cron task to purge data from configurable database tables based on
#   TMG_DATAPURGECONFIG settings. Performs batch deletion with configurable
#   wait times to manage database load.
#
# Parameters (configured in Cron Task Instance):
#   - PURGE_CONFIG: Configuration name from TMG_DATAPURGECONFIG table
#   - BATCH_SIZE: Number of records to delete per batch
#   - BATCH_WAIT_SECONDS: Wait time between batches (seconds)
#
# Revision:
# Date        User                        Comment
# 2025-11-06  System                      Converted from Java CronTask
# 2017-01-25  X2CJCOUR                    Original Java creation
# 2017-06-12  X2CJCOUR                    PPM 32664 - Added wait time
# 2018-07-11  X2CJCOUR                    PPM 33655 - Message Tracking support
################

from psdi.mbo import MboConstants
from psdi.server import MXServer
from psdi.util.logging import MXLogger
from java.util import Date
from java.lang import Thread
from java.sql import SQLException

# Initialize logger
logger = MXServer.getMXServer().lookup("LOGGING")
scriptName = "TMG_DATAPURGE.CRON.ACTION"

def main():
    """
    Main cron task execution function.
    Purges data from configured database tables in batches.
    """
    try:
        logger.info(scriptName + ": Starting data purge cron task")
        
        # Get cron task instance parameters
        purgeConfig = croninstance.getParamAsString("PURGE_CONFIG")
        batchSize = croninstance.getParamAsInt("BATCH_SIZE")
        batchWaitSeconds = croninstance.getParamAsInt("BATCH_WAIT_SECONDS")
        
        # Validate required parameters
        if not purgeConfig or purgeConfig.strip() == "":
            raise Exception("PURGE_CONFIG parameter is missing or empty")
        
        if batchSize is None or batchSize <= 0:
            raise Exception("BATCH_SIZE parameter is missing or invalid")
        
        if batchWaitSeconds is None or batchWaitSeconds < 0:
            raise Exception("BATCH_WAIT_SECONDS parameter is missing or invalid")
        
        logger.info(scriptName + ": Parameters validated - Config: " + purgeConfig + 
                   ", BatchSize: " + str(batchSize) + 
                   ", WaitSeconds: " + str(batchWaitSeconds))
        
        # Execute data purge
        purgeTableData(purgeConfig, batchSize, batchWaitSeconds)
        
        logger.info(scriptName + ": Data purge completed successfully")
        
    except Exception, e:
        errorMsg = scriptName + ": Cron task failed with exception: " + str(e)
        logger.error(errorMsg)
        logger.error(scriptName + ": Stack trace", e)
        # Re-raise to mark cron task as failed
        raise


def purgeTableData(purgeConfig, batchSize, batchWaitSeconds):
    """
    Purge data from specified table using configuration settings.
    
    Args:
        purgeConfig (str): Configuration name from TMG_DATAPURGECONFIG
        batchSize (int): Number of records to delete per batch
        batchWaitSeconds (int): Wait time between batches
    """
    mboSet = None
    
    try:
        # Get purge configuration
        mxServer = MXServer.getMXServer()
        userInfo = mxServer.getSystemUserInfo()
        mboSet = mxServer.getMboSet("TMG_DATAPURGECONFIG", userInfo)
        mboSet.setWhere("TMG_CONFIGNAME = '" + purgeConfig + "'")
        mboSet.reset()
        
        if mboSet.isEmpty():
            raise Exception("Configuration '" + purgeConfig + "' not found")
        
        # Get table and where clause from config
        configMbo = mboSet.getMbo(0)
        tableName = configMbo.getString("TMG_TABLE")
        whereClause = configMbo.getString("TMG_WHERECLAUSE")
        
        logger.info(scriptName + ": Table: " + tableName)
        logger.info(scriptName + ": Where: " + whereClause)
        
        # Delete in batches
        totalDeleted = 0
        batchNumber = 0
        rowsDeleted = 0
        
        while True:
            batchNumber += 1
            logger.info(scriptName + ": Processing batch " + str(batchNumber))
            
            rowsDeleted = deleteBatch(tableName, whereClause, batchSize)
            totalDeleted += rowsDeleted
            
            logger.info(scriptName + ": Batch " + str(batchNumber) + 
                       " deleted " + str(rowsDeleted) + " rows")
            
            if rowsDeleted == 0:
                break
            
            # Wait before next batch
            logger.debug(scriptName + ": Waiting " + str(batchWaitSeconds) + " seconds")
            Thread.sleep(batchWaitSeconds * 1000)
        
        logger.info(scriptName + ": Total rows deleted: " + str(totalDeleted))
        
    finally:
        if mboSet is not None:
            mboSet.close()


def deleteBatch(tableName, whereClause, batchSize):
    """
    Delete a batch of records.
    
    Args:
        tableName (str): Table to delete from
        whereClause (str): WHERE condition
        batchSize (int): Number of records to delete
        
    Returns:
        int: Number of rows deleted
    """
    connection = None
    statement = None
    
    try:
        userInfo = MXServer.getMXServer().getSystemUserInfo()
        connection = userInfo.getConnection()
        
        # Build delete SQL with ROWNUM (Oracle-specific)
        deleteSQL = ("DELETE FROM " + tableName + 
                    " WHERE ROWNUM <= " + str(batchSize) + 
                    " AND " + whereClause)
        
        logger.debug(scriptName + ": SQL: " + deleteSQL)
        
        # Execute delete
        statement = connection.createStatement()
        rowsDeleted = statement.executeUpdate(deleteSQL)
        connection.commit()
        
        return rowsDeleted
        
    except SQLException, e:
        logger.error(scriptName + ": Delete failed", e)
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if statement is not None:
            statement.close()

# Execute main function
main()

scriptConfig="""{
    "autoscript": "TMG.DATAPURGE.CRON.ACTION",
    "description": "Purges data from configured tables in batches",
    "version": "1.0",
    "active": true,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "TMG_DATAPURGE_CRON",
            "launchPointType": "OBJECT",
            "active": true,
            "description": "Data Purge Cron Task",
            "objectName": "CRONTASKINSTANCE"
        }
    ]
}"""
```

---

### Example 2: Complex Business Logic (tmg_compinactive.cron.action.py)

**Original Java:** `TMG_CompInactiveCronTask.java` (475 lines)

**Key Features:**
- Inactivates suppliers with no purchasing activity for 5 years (1825 days)
- 4 validation checks:
  1. No RFQ bidder records in last 5 years
  2. No open POs in last 5 years
  3. All contracts closed for 5 years
  4. Not primary vendor on any inventory items
- Date arithmetic with GregorianCalendar
- Status translation (internal vs external values)

**Converted Python:** `tmg_compinactive.cron.action.py` (460 lines)

**Key Conversion Points:**

1. **Date Comparison Function**
```python
from java.util import GregorianCalendar, Calendar

def isDateOlderThan(dateToCheck, daysToAdd, compareDate):
    """Check if date + days is before compareDate."""
    calendar = GregorianCalendar()
    calendar.setTime(dateToCheck)
    calendar.add(Calendar.DATE, daysToAdd)
    newDate = calendar.getTime()
    return newDate.before(compareDate)
```

2. **Validation Checks**
```python
def canInactivateCompany(company, orgId, currentDate):
    """
    Check if company can be inactivated (no activity for 5 years).
    
    Returns:
        bool: True if company can be inactivated
    """
    companyCode = company.getString("COMPANY")
    
    # Check 1: RFQ bidder activity
    if vendorExistsAsRFQBidder(companyCode, orgId, currentDate):
        return False
    
    # Check 2: Open POs
    if openPOExists(companyCode, orgId, currentDate):
        return False
    
    # Check 3: Open contracts
    if openContractsExist(companyCode, currentDate):
        return False
    
    # Check 4: Primary vendor on items
    if companyExistsAsPrimaryVendor(companyCode, orgId):
        return False
    
    return True
```

3. **Status Translation**
```python
def checkPOStatus(poMbo):
    """Check if PO status is open."""
    internalStatus = poMbo.getTranslator().toInternalString(
        "POSTATUS", 
        poMbo.getString("status")
    )
    
    # Check against internal values
    openStatuses = ["WAPPR", "APPR", "INPRG"]
    return internalStatus in openStatuses
```

---

## Common Issues and Solutions

### Issue 1: TimeUnit Not Available in Jython

**Problem**: Java uses `TimeUnit.SECONDS.sleep(seconds)`  
**Solution**: Use `Thread.sleep(milliseconds)`

```python
from java.lang import Thread

# Convert seconds to milliseconds
waitSeconds = 10
Thread.sleep(waitSeconds * 1000)
```

---

### Issue 2: DBShortcut Class Conversion

**Problem**: Java uses custom `DBShortcut` class  
**Solution**: Use JDBC directly via `userInfo.getConnection()`

```python
from java.sql import SQLException

connection = None
statement = None

try:
    userInfo = MXServer.getMXServer().getSystemUserInfo()
    connection = userInfo.getConnection()
    
    statement = connection.createStatement()
    resultSet = statement.executeQuery(sql)
    
    connection.commit()
finally:
    if statement is not None:
        statement.close()
    # Do NOT close connection
```

---

### Issue 3: ROWNUM is Oracle-Specific

**Problem**: `ROWNUM` clause only works in Oracle  
**Solution**: Document database-specific syntax

```python
# Oracle
deleteSQL = "DELETE FROM TABLE WHERE ROWNUM <= 100 AND condition"

# DB2 alternative
deleteSQL = "DELETE FROM TABLE WHERE condition FETCH FIRST 100 ROWS ONLY"

# SQL Server alternative
deleteSQL = "DELETE TOP 100 FROM TABLE WHERE condition"
```

---

### Issue 4: Logger Initialization

**Problem**: Java uses `MicUtil.INTEGRATIONLOGGER`  
**Solution**: Use `MXServer.getMXServer().lookup("LOGGING")`

```python
# Initialize at script level
from psdi.server import MXServer

logger = MXServer.getMXServer().lookup("LOGGING")
scriptName = "SCRIPT.NAME"

# Use in functions
logger.info(scriptName + ": Message")
logger.error(scriptName + ": Error message", exception)
```

---

### Issue 5: Parameter Type Conversion

**Problem**: Parameter may be None if not configured  
**Solution**: Always validate parameters

```python
def main():
    # Get parameter
    batchSize = croninstance.getParamAsInt("BATCH_SIZE")
    
    # Validate
    if batchSize is None:
        raise Exception("BATCH_SIZE parameter is required")
    
    if batchSize <= 0:
        raise Exception("BATCH_SIZE must be greater than 0")
```

---

## Best Practices Summary

1. **Always re-raise exceptions** - Marks cron task as failed in Maximo
2. **Close all resources** - MboSets, ResultSets, Statements in finally blocks
3. **Never close connection** - Managed by MXServer
4. **Use milliseconds for Thread.sleep()** - Convert seconds * 1000
5. **Validate all parameters** - Check for None, empty, invalid values
6. **Log at all levels** - Info for major steps, debug for details, error for exceptions
7. **Preserve revision history** - Include all PPM numbers and dates from Java
8. **Use proper exception handling** - Try-except-finally structure
9. **Commit after successful operations** - Rollback on errors
10. **Document database-specific SQL** - ROWNUM, FETCH FIRST, TOP

---

## Additional Resources

### Related Documentation Files

1. **CRONTASK_CONVERSION_LOG.md** - Complete conversion log with all 9 conversions
2. **automation-scripts/cron_tasks/README.md** - Usage guide for cron scripts
3. **Knowledge-base/maximo_script_patterns_reference.md** - General patterns

### Completed Cron Task Scripts (Reference)

1. **tmg_datapurge.cron.action.py** - Batch deletion pattern (261 lines)
2. **tmg_compinactive.cron.action.py** - Complex business logic (460 lines)
3. **tmg_geninv.cron.action.py** - Invoice creation (1016 lines - complex)
4. **tmg_valclrts.cron.action.py** - 9 validation checks (515 lines)
5. **tmg_poclose.cron.action.py** - PO closing with PCARD (494 lines)
6. **tmg_addcimusers.cron.action.py** - DBShortcut INSERT/DELETE (162 lines)
7. **tmg_pmwogen.cron.action.py** - PM WO generation (334 lines)
8. **tmg_measurepointwogen.cron.action.py** - Measure point WO (481 lines)
9. **tmg_sttupdate.cron.action.py** - Inventory summarization (1040 lines - LARGEST)

### Java Source Files Location

- **TMGMaximo_MAS/businessobjects/tmg/common/** - Common cron tasks
- **TMGMaximo_MAS/businessobjects/tmg/app/workorder/** - Work order cron tasks
- **TMGMaximo_MAS/businessobjects/tmg/app/company/** - Company cron tasks

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-13 | SDK Conversion Team | Initial creation with complete prompt template, 9 patterns, and 2 detailed examples |

---

**End of Prompt Template**
