# Cron Task Conversion Prompt (Compact)

**Purpose**: Converting Java CronTasks to Python automation scripts  
**Version**: 2.0.0  
**Last Updated**: 2025-12-08  
**Context**: MAS 9 upgrade - Java SimpleCronTask → Python CRON scripts

**📘 PREREQUISITE**: Read `prompt_master_conversion_guide.md` for common standards (headers, Python idioms, scriptConfig, patterns, checklists)

---

## Quick Conversion Prompt

```
Convert Maximo Java CronTask to Python automation script for MAS 9.

**Java CronTask**: [TMG_XXXXXXCronTask]
**Path**: [Full path]
**Module**: [Work Order/Inventory/etc.]
**Purpose**: [Brief description]
**Complexity**: [Simple/Medium/Complex]

**Source**: [Paste Java code]

**Requirements** (see master guide for details):
1. Convert to OBJECT launch point (CRONTASKINSTANCE)
2. Follow master guide: Headers, Python idioms, exception handling
3. Naming: [taskname].cron.action.py (lowercase, no underscores)
4. Parameter handling via croninstance
5. Logger: MXServer.getMXServer().lookup("LOGGING")
6. Database: JDBC via userInfo.getConnection() (DON'T close connection)
7. Thread.sleep(milliseconds) - NOT TimeUnit
8. scriptConfig at END
9. Re-raise exceptions to mark task as failed

**Reference**:
- Master Guide: prompt_master_conversion_guide.md
- Conversion Log: CRONTASK_CONVERSION_LOG.md
- Existing Scripts: automation-scripts/cron_tasks/
```

---

## Naming Convention

| Java Class | Python Script |
|------------|---------------|
| `TMG_DataPurgeCronTask.java` | `tmg_datapurge.cron.action.py` |
| `TMG_CompInactiveCronTask.java` | `tmg_compinactive.cron.action.py` |
| `TMG_GenInvCronTask.java` | `tmg_geninv.cron.action.py` |

**Pattern**: `[taskname].cron.action.py` (all lowercase, no underscores between camelCase words)

---

## Cron-Specific Patterns

### Pattern 1: Parameter Retrieval

```python
from psdi.server import MXServer

# Get cron task instance
mxServer = MXServer.getMXServer()
croninstance = mxServer.lookup("CRONTASK")

# Get parameters
purgeConfig = croninstance.getParamAsString("PURGE_CONFIG")
batchSize = croninstance.getParamAsInt("BATCH_SIZE")
waitSeconds = croninstance.getParamAsInt("BATCH_WAIT_SECONDS")

# Validate parameters
if purgeConfig is None or purgeConfig == "":
    logger.error(scriptName + ": PURGE_CONFIG parameter required")
    return
```

### Pattern 2: Database Operations (JDBC)

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

### Pattern 3: Batch Processing with Sleep

```python
from java.lang import Thread

def processBatches(batchCount, waitSeconds):
    # Process batches with wait time between
    for batch in range(batchCount):
        logger.info(scriptName + ": Processing batch " + str(batch + 1))
        
        # Process batch
        rowsProcessed = processBatch(batch)
        logger.info(scriptName + ": Processed " + str(rowsProcessed) + " rows")
        
        # Wait between batches (NOT after last batch)
        if batch < batchCount - 1:
            logger.info(scriptName + ": Waiting " + str(waitSeconds) + " seconds")
            Thread.sleep(waitSeconds * 1000)  # Convert to milliseconds
```

### Pattern 4: Batch Deletion (Oracle ROWNUM)

```python
def deleteBatch(tableName, whereClause, batchSize):
    # Oracle-specific batch deletion
    # For DB2: Use "FETCH FIRST n ROWS ONLY"
    # For SQL Server: Use "TOP n"
    
    connection = userInfo.getConnection()
    statement = None
    
    try:
        deleteSQL = ("DELETE FROM " + tableName + 
                    " WHERE ROWNUM <= " + str(batchSize) +
                    " AND " + whereClause)
        
        statement = connection.createStatement()
        rowsDeleted = statement.executeUpdate(deleteSQL)
        connection.commit()
        
        return rowsDeleted
        
    finally:
        if statement is not None:
            statement.close()
```

### Pattern 5: MboSet Batch Operations

```python
from psdi.mbo import MboConstants

def processMboSet():
    mboSet = None
    try:
        # Get MboSet
        mboSet = mxServer.getMboSet("OBJECT", userInfo)
        mboSet.setWhere("WHERE_CLAUSE")
        mboSet.reset()
        
        # Process in batches
        batchSize = 100
        totalProcessed = 0
        
        for i in range(mboSet.count()):
            mbo = mboSet.getMbo(i)
            
            # Process mbo
            mbo.setValue("FIELD", "VALUE", MboConstants.NOACCESSCHECK)
            
            # Save in batches
            if (i + 1) % batchSize == 0:
                mboSet.save()
                logger.info(scriptName + ": Saved batch, count=" + str(i + 1))
                totalProcessed += batchSize
        
        # Save remaining
        mboSet.save()
        
        return totalProcessed
        
    finally:
        if mboSet is not None:
            mboSet.close()
```

---

## scriptConfig Template

```python
scriptConfig = {
    "autoscript": "[TASKNAME].CRON.ACTION",
    "description": "[Brief description]",
    "version": "1.0",
    "active": True,
    "logLevel": "ERROR",
    "references": {
        "objects": ["[OBJECT1]", "[OBJECT2]"],
        "TR": ["[TR1]", "[TR2]"]
    },
    "scriptLaunchPoints": [
        {
            "launchPointName": "[TASKNAME]_CRON_ACTION",
            "launchPointType": "OBJECT",
            "objectName": "CRONTASKINSTANCE",
            "active": True,
            "description": "Cron task: [description]",
            "save": True,
            "add": False,
            "update": True,
            "delete": False
        }
    ]
}
```

**CRITICAL**: 
- `objectName` MUST be `"CRONTASKINSTANCE"`
- Use `save: True, add: False, update: True, delete: False`

---

## Cron Task Script Structure

```python
################
# Script: [Task Name] Cron Task
# Cron Task Action Launch Point
#
# Launch Point: [TASKNAME].CRON.ACTION
# Object: N/A (Cron Task)
# Action: Cron Task Instance Execution
#
# Author: Converted from Java CronTask ([ClassName].java)
# Naming Convention: [taskname].cron.action.py
#
# Original Java: [ClassName].java (package)
# Conversion Date: [Date]
#
# Description:
#   [What this cron task does]
#
# Parameters (configured in Cron Task Instance):
#   - PARAM1: [Description]
#   - PARAM2: [Description]
#
# Revision:
# Date        User        Comment
# ----------  ----------  ---------------------------------------
# [Date]      System      Converted from Java CronTask
################

from psdi.server import MXServer
from psdi.util.logging import MXLogger
from java.lang import Thread

# Initialize logger
logger = MXServer.getMXServer().lookup("LOGGING")
scriptName = "[TASKNAME].CRON.ACTION"

def main():
    # Main cron task execution
    try:
        logger.info(scriptName + ": Starting cron task")
        
        # Get cron instance and parameters
        mxServer = MXServer.getMXServer()
        croninstance = mxServer.lookup("CRONTASK")
        
        param1 = croninstance.getParamAsString("PARAM1")
        param2 = croninstance.getParamAsInt("PARAM2")
        
        # Validate parameters
        if param1 is None:
            logger.error(scriptName + ": PARAM1 required")
            return
        
        # Execute cron task logic
        result = processTask(param1, param2)
        
        logger.info(scriptName + ": Completed successfully, result=" + str(result))
        
    except Exception as e:
        logger.error(scriptName + ": Error: " + str(e))
        raise  # Re-raise to mark cron task as failed

def processTask(param1, param2):
    # Cron task logic here
    return 0

# Execute main function
main()

scriptConfig = {
    "autoscript": "[TASKNAME].CRON.ACTION",
    "description": "[Description]",
    "version": "1.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [{
        "launchPointName": "[TASKNAME]_CRON_ACTION",
        "launchPointType": "OBJECT",
        "objectName": "CRONTASKINSTANCE",
        "active": True,
        "description": "Cron task execution",
        "save": True,
        "add": False,
        "update": True,
        "delete": False
    }]
}
```

---

## Common Cron Task Issues

### Issue 1: TimeUnit Not Available

```python
# ❌ WRONG
from java.util.concurrent import TimeUnit
TimeUnit.SECONDS.sleep(10)

# ✅ CORRECT
from java.lang import Thread
Thread.sleep(10 * 1000)  # Milliseconds
```

### Issue 2: DBShortcut Class

```python
# ❌ WRONG (Java DBShortcut not available)
from psdi.util import DBShortcut
dbShortcut = DBShortcut()

# ✅ CORRECT (Use JDBC directly)
userInfo = MXServer.getMXServer().getSystemUserInfo()
connection = userInfo.getConnection()
statement = connection.createStatement()
# Use statement, then close it (NOT connection)
```

### Issue 3: Parameter Type Conversion

```python
# ⚠️ Parameter may be None if not configured
batchSize = croninstance.getParamAsInt("BATCH_SIZE")
if batchSize is None or batchSize <= 0:
    batchSize = 100  # Default value
    logger.info(scriptName + ": Using default batch size: 100")
```

---

## Quick Checklist

See master guide for full checklist. Cron task essentials:

- [ ] Naming: `[taskname].cron.action.py` (lowercase)
- [ ] Parameters via `croninstance.getParamAsXxx()`
- [ ] Logger via `MXServer.getMXServer().lookup("LOGGING")`
- [ ] Database connection via `userInfo.getConnection()` (DON'T close)
- [ ] Thread.sleep uses milliseconds (seconds × 1000)
- [ ] Exceptions re-raised to mark task as failed
- [ ] scriptConfig.objectName = "CRONTASKINSTANCE"
- [ ] ResultSets and Statements closed in finally

---

## Examples

### Example 1: Simple Data Purge

**Java**: `TMG_DataPurgeCronTask.java` (251 lines)

**Python** (`tmg_datapurge.cron.action.py`):
```python
################
# Script: Data Purge Cron Task
# ...
################

from psdi.server import MXServer
from java.lang import Thread

logger = MXServer.getMXServer().lookup("LOGGING")
scriptName = "TMG_DATAPURGE.CRON.ACTION"

def main():
    try:
        # Get parameters
        mxServer = MXServer.getMXServer()
        croninstance = mxServer.lookup("CRONTASK")
        
        purgeConfig = croninstance.getParamAsString("PURGE_CONFIG")
        batchSize = croninstance.getParamAsInt("BATCH_SIZE")
        waitSeconds = croninstance.getParamAsInt("BATCH_WAIT_SECONDS")
        
        # Process batches
        totalDeleted = 0
        batchCount = 0
        
        while True:
            deleted = deleteBatch("TABLENAME", "WHERE ...", batchSize)
            if deleted == 0:
                break
                
            totalDeleted += deleted
            batchCount += 1
            
            # Wait between batches (except after last)
            Thread.sleep(waitSeconds * 1000)
        
        logger.info(scriptName + ": Deleted " + str(totalDeleted) + " records")
        
    except Exception as e:
        logger.error(scriptName + ": Error: " + str(e))
        raise

def deleteBatch(tableName, whereClause, batchSize):
    # Delete implementation
    return 0

main()

scriptConfig = { ... }
```

### Example 2: Complex Business Logic

**Java**: `TMG_CompInactiveCronTask.java` (475 lines)

**Key Features**:
- 4 validation checks before inactivating company
- Date arithmetic (5 years = 1825 days)
- Status translation (internal vs external)
- MboSet operations

See `automation-scripts/cron_tasks/tmg_compinactive.cron.action.py` for full example.

---

## Reference Scripts

**Location**: `automation-scripts/cron_tasks/`

1. **tmg_datapurge.cron.action.py** (261 lines) - Batch deletion
2. **tmg_compinactive.cron.action.py** (460 lines) - Complex business logic
3. **tmg_geninv.cron.action.py** (1016 lines) - Invoice creation
4. **tmg_valclrts.cron.action.py** (515 lines) - Validation
5. **tmg_poclose.cron.action.py** (494 lines) - PO closing
6. **tmg_addcimusers.cron.action.py** (162 lines) - DBShortcut INSERT/DELETE
7. **tmg_pmwogen.cron.action.py** (334 lines) - PM WO generation
8. **tmg_measurepointwogen.cron.action.py** (481 lines) - Measure point WO
9. **tmg_sttupdate.cron.action.py** (1040 lines) - Inventory summarization

---

## See Also

- **Master Guide**: `prompt_master_conversion_guide.md` (Common standards, patterns, Python idioms)
- **Conversion Log**: `CRONTASK_CONVERSION_LOG.md` (9 completed conversions with notes)
- **Patterns**: `Knowledge-base/maximo_script_patterns_reference.md` (MboSet, JDBC, dates)
- **Object Scripts**: `prompt_objectscripts.md` (If converting MBO classes)

---

**VERSION**: 2.0.0 (2025-12-08) - Compact version referencing master guide
