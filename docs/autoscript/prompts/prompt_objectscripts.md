# Object Script Conversion Prompt Template

**Purpose**: Systematic prompt template for converting Maximo Java MBO (Mbo/MboSet) classes to Python automation scripts  
**Version**: 1.0.0  
**Last Updated**: 2025-12-01  
**Context**: MAS 9 upgrade - converting 110+ Java MBO custom classes to Python Object/Action Launch Point automation scripts

---

## Table of Contents

1. [Conversion Prompt Template](#conversion-prompt-template)
2. [Standard Header Format](#standard-header-format)
3. [Context Documents](#context-documents)
4. [Conversion Patterns](#conversion-patterns)
5. [Quality Checklist](#quality-checklist)
6. [Example Conversions](#example-conversions)

---

## Conversion Prompt Template

### Base Prompt for MBO Object Script Conversion

```
I need to convert a Maximo Java MBO class to Python automation scripts for MAS 9 upgrade.

**Java MBO Information:**
- Class Name: [TMG_XXXXX]
- Java Path: [Full path to Java file]
- Module: [Invoice/Work Order/Inventory/Purchase Order/etc.]
- Base Class: [Mbo/MboSet/specific Maximo class]
- Complexity: [Simple/Medium/Complex]
- Lines of Code: [XXX]

**Source Java File:**
[Paste Java source code here]

**Requirements:**
1. **Analyze Java Source**:
   - Identify all overridden methods (init, add, save, delete, etc.)
   - Identify all custom action methods
   - Identify all custom business logic
   - Note any special flags or constants used
   - Document TR/business requirements from comments

2. **Create Module Directory Structure**:
   - Directory: automation-scripts/object_scripts/[objectname]/
   - Files needed:
     * [object].obj.[event].py - For Object launch points (init, save, delete, etc.)
     * [object].action.[actionname].py - For Action launch points (custom methods)
     * README.md - Module documentation
     * SCRIPT_CONFIGURATION.md - Deployment guide

3. **Python Script Requirements**:
   - Use proper header template with all metadata (see Standard Header Format)
   - Follow naming convention: [object].[type].[event/action].py (all lowercase)
   - Preserve all business logic from original Java
   - Use MboConstants for all flags (no numeric constants like 2L, 7L, 11L)
   - Implement proper error handling with try/except
   - Add clear comments explaining business logic
   - Include complete scriptConfig dictionary at END of file
   - Re-raise exceptions to ensure Maximo marks script execution as failed
   - **CRITICAL**: Analyze Java method to determine correct event timing (beforeSave/afterSave/afterCommit)

4. **Launch Point Types**:
   - **OBJECT Launch Points**: init, add, save, delete, undelete events
     * **INIT**: `initializeValue: True` - After object initialization (no operation flags needed)
     * **ADD**: For Java `add()` method that runs on new records only:
       - Use: `save: True, add: True, update: False, delete: False, afterSave: True`
       - **IMPORTANT**: ADD events MUST include save event with operation flags
       - ADD cannot be standalone - must be combined with save event timing
     * **SAVE**: **MUST analyze Java code to choose correct timing**:
       - `save: True, add: True, update: True, delete: False, beforeSave: True` - Use if Java method is `appValidate()` OR logic runs BEFORE `super.save()`
       - `save: True, add: True, update: True, delete: False, afterSave: True` - Use if Java method is `save()` with logic AFTER `super.save()` OR calls save on other objects
       - `save: True, add: True, update: True, delete: False, afterCommit: True` - Use if Java sends notifications/emails OR calls external systems
     * **DELETE**: For Java `delete(long)` method - deletion cleanup logic:
       - Use: `save: True, add: False, update: False, delete: True, afterSave: True`
       - **IMPORTANT**: DELETE uses SAVE launch point with delete flag, NOT separate DELETE event
       - Delete operations are part of the save lifecycle
       - Use `afterSave: True` for post-deletion cleanup (update totals, cascade deletes, etc.)
     * **canDelete**: For Java `canDelete()` method - deletion validation:
       - Use: `save: True, add: False, update: False, delete: True, beforeSave: True`
       - **IMPORTANT**: canDelete also uses SAVE launch point with delete flag
       - Use `beforeSave: True` for validation logic that runs before deletion
       - Throw exceptions to prevent deletion if validation fails
   - **ACTION Launch Points**: Custom methods invoked via mbo.invokeAction() (no operation flags needed)
   
5. **scriptConfig Requirements**:
   - Must be placed at ABSOLUTE END of file
   - Include all launch point definitions
   - **CRITICAL - Specify exact event timing and operation flags based on Java method analysis**:
     * If Java method = `appValidate()` → Use `save: True, add: True, update: True, delete: False, beforeSave: True`
     * If Java method = `save()` with logic BEFORE `super.save()` → Use `save: True, add: True, update: True, delete: False, beforeSave: True`
     * If Java method = `save()` with logic AFTER `super.save()` → Use `save: True, add: True, update: True, delete: False, afterSave: True`
     * If Java method calls `save()` on other MBOs → Use `save: True, add: True, update: True, delete: False, afterSave: True`
     * If Java method sends emails/notifications → Use `save: True, add: True, update: True, delete: False, afterCommit: True`
     * If Java method = `canDelete()` → Use `save: True, add: False, update: False, delete: True, beforeSave: True` (**canDelete uses SAVE launch point with delete flag**)
     * If Java method = `delete(long)` → Use `save: True, add: False, update: False, delete: True, afterSave: True` (**delete uses SAVE launch point with delete flag**)
     * If Java method = `add()` → Use `save: True, add: True, update: False, delete: False, afterSave: True` (**ADD events MUST include save with operation flags**)
     * If Java method = `init()` → Use `initializeValue: True` (no operation flags)
   - **IMPORTANT**: Operation flags control when SAVE scripts execute:
     * `add: True` - Run on new records being added
     * `update: True` - Run on existing record updates
     * `delete: True` - Run when deleting records (NOT `delete: False`)
     * For ADD events: Use `add: True, update: False, delete: False` to run ONLY on new records
     * For DELETE events: Use `add: False, update: False, delete: True` to run ONLY on deletion
     * **CRITICAL**: All delete operations (canDelete, delete) use SAVE launch point with `delete: True` flag
   - **CRITICAL**: ADD events cannot be standalone - they MUST include `save: True` with timing (beforeSave/afterSave/afterCommit)
   - Specify script variables for ACTION launch points
   - Use proper binding types (INPARAM, OUTPARAM, INOUTPARAM)

**Reference Documents:**
- **Launch Point Reference**: Knowledge-base/LAUNCH_POINT_REFERENCE_PATTERNS.md (PRIMARY REFERENCE)
- Object Inventory: automation-scripts/object_scripts/OBJECT_INVENTORY.md
- Patterns: Knowledge-base/maximo_script_patterns_reference.md
- Header Template: See "Standard Header Format" section below
- Example Conversions: classspec.obj.init.py, invoice.obj.save.py, invoice.action.doclrprocess.py

**Expected Output:**
- Complete Python automation script(s) with standardized headers
- Business logic preserved and documented with TR references
- scriptConfig dictionary with all launch points
- README.md documenting module functionality
- SCRIPT_CONFIGURATION.md with deployment instructions
- Testing checklist for validation
- **CRITICAL**: Update OBJECT_INVENTORY.md tracking document with conversion details
```

---

## Standard Header Format

### CRITICAL INSTRUCTIONS

**Header Format Rules:**
1. Use `################ ` comment blocks for file headers (80 chars wide)
2. Use `# ` single-line comments for ALL inline documentation
3. **NEVER use triple-quote docstrings (""")** - Not compatible with Maximo automation scripts
4. **ALWAYS use # for comments** - Single-line comments only, no docstrings
5. **Use Python idioms, not Java-style methods** - See Python Best Practices below
6. Include all metadata: Script name, Object, Launch Point, Description, Converted From, History, Conversion Review

### Python Best Practices (Jython-Specific)

**CRITICAL**: Convert all Java-style methods to Python idioms:

```python
# ❌ WRONG - Java style
if string.equalsIgnoreCase("VALUE"):
if not string.equalsIgnoreCase("VALUE"):
if string1.equalsIgnoreCase("A") or string2.equalsIgnoreCase("B"):
if isinstance(obj, tmg.app.SomeClass):

# ✅ CORRECT - Python style
if string.upper() == "VALUE":
if string.upper() != "VALUE":
if string1.upper() in ["A", "B", "C"]:  # More efficient for multiple checks
obj_class = obj.getClass().getName()
if "ClassName" in obj_class:

# String comparisons
# ❌ WRONG: value.equals("TEST")
# ✅ CORRECT: value == "TEST"

# ❌ WRONG: value.equalsIgnoreCase("TEST")
# ✅ CORRECT: value.upper() == "TEST"

# Multiple string checks
# ❌ WRONG: x.equalsIgnoreCase("A") or x.equalsIgnoreCase("B") or x.equalsIgnoreCase("C")
# ✅ CORRECT: x.upper() in ["A", "B", "C"]

# Boolean checks
# ❌ WRONG: if not flag.equalsIgnoreCase("Y"):
# ✅ CORRECT: if flag.upper() != "Y":

# Class type checking (avoid isinstance with Java classes)
# ❌ WRONG: isinstance(obj, tmg.app.workorder.TMG_PlusWO)
# ✅ CORRECT: 
obj_class = obj.getClass().getName()
if "TMG_PlusWO" in obj_class:
    # Process TMG_PlusWO
elif "PlusPermit" in obj_class:
    # Process PlusPermit
```

**Why avoid isinstance()?**
- Import dependencies can cause issues in Maximo
- Jython class loading is inconsistent
- `getClass().getName()` is more reliable in Maximo context

### Object Launch Point Header Template

```python
################################################################################
# Script:
# Object Launch Point - [EVENT]
#
# Launch Point: [OBJECT].[TYPE].[EVENT]
# Object: [OBJECT]
#
# Author: Converted from Java MBO [TMG_ClassName]
#
# Revision:
# Date        User                        Comment
# ----------  --------------------------  ---------------------------------------
# 2025-12-01  Automation                  Converted from [TMG_ClassName].java [method]() method
#                                         [TR number]: [Brief description]
#
# Conversion Review:
# - Convert to AutoScript: [Yes/Partially/No]
# - Complexity: [Simple/Medium/Complex]
# - Status: [Good/Need TMG Action]
# - Business Area: [Invoice/Work Order/Asset/Inventory/etc.]
#
################################################################################
#
# DESCRIPTION:
#   [Detailed description of what this script does]
#   [Business requirements and logic explanation]
#
# BUSINESS REQUIREMENTS ([TR number]):
#   - [Requirement 1]
#   - [Requirement 2]
#   - [Additional requirements]
#
# CONVERTED FROM: tmg.app.[module].[TMG_ClassName].[method]()
#   Original: Java MBO [method]() method
#   TR: [TR number]
#
################################################################################

from psdi.mbo import MboConstants
from psdi.util.logging import MXLoggerFactory

# Initialize logger
logger = MXLoggerFactory.getLogger("maximo.application.[OBJECT]")
className = "[object].[type].[event]"

# Main script logic here
```

### Action Launch Point Header Template

```python
# ============================================================================
# Script: [object].action.[actionname].py
# Object: [OBJECT]
# Launch Point: Action ([ACTIONNAME])
# 
# Description:
# [Brief description of action]
#
# Converted From:
# Java Class: tmg.app.[module].[TMG_ClassName].java
# Method: [actionMethodName]()
#
# Launch Point Configuration:
# ---------------------------
# Launch Point Name: [OBJECT]_ACT_[ACTIONNAME]
# Launch Point Type: ACTION
# Active: Yes
# 
# Action Launch Point Settings:
#   Object: [OBJECT]
#   Action: [ACTIONNAME]
#
# Script Settings:
#   Script Name: [OBJECT].ACT.[ACTIONNAME]
#   Language: python
#   Log Level: [DEBUG/ERROR]
#
# Script Variables:
#   Variable Name: [varname]
#   Binding Type: [INPARAM/OUTPARAM/INOUTPARAM]
#   Binding Value: [varname]
#   Description: [Purpose of variable]
#   Type: [String/Integer/Boolean/etc.]
#   Access: [READONLY/READWRITE]
#
# Usage Examples:
#   Python: mbo.invokeAction("[ACTIONNAME]", [param1], [param2])
#   Java:   mbo.invokeAction("[ACTIONNAME]", [param1], [param2]);
#
# History:
# Date       Developer  Description
# ---------- ---------- ---------------------------------------------------
# 2025-12-01 Auto       Converted from Java to Python automation script
# ============================================================================

from psdi.util.logging import MXLoggerFactory
from psdi.mbo import MboConstants

# Initialize logger
logger = MXLoggerFactory.getLogger("maximo.application.[OBJECT]")
className = "[object].action.[actionname]"

# Main script logic here
```

---

## Context Documents

### Required Reading Before Conversion

#### 1. Object Inventory Tracking
**File:** `automation-scripts/object_scripts/OBJECT_INVENTORY.md`

**Key Information:**
- Complete list of 110+ MBO classes to convert
- Priority assignments (High/Medium/Low)
- Complexity ratings (Simple/Medium/Complex)
- Conversion status tracking
- File paths for source Java files
- Lines of code for each class

**Usage:**
- Check which MBOs are converted vs not started
- Identify high priority conversions
- Track progress (currently 2/110 complete)
- Update status when conversion complete

#### 2. Existing Object Scripts
**Location:** `automation-scripts/object_scripts/`

**Reference Scripts:**

**Simple Examples:**
1. **classspec/classspec.obj.init.py** (89 lines)
   - Simple init() override
   - Sets default field value
   - Basic MboConstants usage
   - Good template for simple object scripts

**Complex Examples:**
2. **invoice/invoice.obj.save.py** (58 lines)
   - Save event logging
   - Logger initialization pattern
   - Minimal logic example

3. **invoice/invoice.action.doclrprocess.py** (418 lines)
   - Complex business logic
   - Multiple MboSet operations
   - Receipt creation (MATRECTRANS, SERVRECTRANS)
   - Database updates and calculations
   - Script variables with INPARAM
   - Comprehensive error handling
   - Good template for complex action scripts

#### 3. Maximo Script Patterns
**File:** `Knowledge-base/maximo_script_patterns_reference.md`

**Key Patterns for Object Scripts:**
- MBO operations (setValue, getString, getInt, getBoolean, etc.)
- MboSet queries and iteration patterns
- Flag constants (NOACCESSCHECK, NOVALIDATION, etc.)
- Status change operations (changeStatus)
- Relationship traversal (getMboSet)
- Action invocation patterns (invokeAction)
- Date/time handling (MXServer.getDate())
- Transaction management
- Error handling and logging

**Reference Implementation:** `Knowledge-base/maximo_script_patterns_reference.py`

**Note:** For launch point-specific patterns and examples, always refer to `LAUNCH_POINT_REFERENCE_PATTERNS.md`

#### 4. Java to Python Conversion Guide
**File:** `Knowledge-base/JAVA_TO_PYTHON_CONVERSION_PROMPTS.md`

**Key Information:**
- Java vs Python syntax differences
- Common conversion patterns
- Exception handling translation
- Import statement mapping
- Method signature changes

#### 5. Launch Point Reference Patterns (PRIMARY REFERENCE)
**File:** `Knowledge-base/LAUNCH_POINT_REFERENCE_PATTERNS.md`

**Key Information:**
- **CRITICAL**: Complete OBJECT launch point reference with Java-to-Python mapping
- All OBJECT event types: initializeValue, beforeSave, afterSave, afterCommit, afterAdd, beforeDelete
- Java method to event timing decision table
- ATTRIBUTE launch points: FLD.VALIDATE, FLD.ACTION, FLD.INIT, FLD.LIST
- ACTION launch points with parameter examples
- CRON task examples
- Integration script examples (Publish Channel, OSIN, OSOUT, OSACTION)
- Complete scriptConfig templates with all variations
- Variable binding examples for all launch point types
- Real production script examples from the codebase

**Usage:**
- **ALWAYS refer to this file for launch point examples and patterns**
- Use the Java Method to Event Timing mapping table to determine correct timing
- Copy scriptConfig patterns from this file
- Follow the examples for each launch point type

#### 5a. Object Event Timing Guide

**CRITICAL**: Always analyze the Java method to determine correct event timing!

**For complete scriptConfig templates and examples, see:** `Knowledge-base/LAUNCH_POINT_REFERENCE_PATTERNS.md`

**Quick Reference - Java Method to Event Timing Mapping**:

| Java Method | Java Code Pattern | Event Timing | Operation Flags | Use When |
|------------|-------------------|--------------|-----------------|----------|
| `init()` | Sets defaults | `initializeValue: True` | None (no operation flags) | Object initialization |
| `appValidate()` | Validation logic | `save: True, beforeSave: True` | `add: True, update: True, delete: False` | Validation before DB save |
| `save()` | BEFORE `super.save()` | `save: True, beforeSave: True` | `add: True, update: True, delete: False` | Field manipulation before save |
| `save()` | AFTER `super.save()` | `save: True, afterSave: True` | `add: True, update: True, delete: False` | Trigger related saves |
| `save()` | Calls `otherMbo.save()` | `save: True, afterSave: True` | `add: True, update: True, delete: False` | Cascading saves |
| `save()` | Sends email/notification | `save: True, afterCommit: True` | `add: True, update: True, delete: False` | External communication |
| `add()` | Sets flags/values | `save: True, afterSave: True` | `add: True, update: False, delete: False` | Post-add (NEW records only) |
| `canDelete()` | Validation logic | `delete: True, beforeDelete: True` | None (no operation flags) | Delete validation |

**Complete scriptConfig Examples**: See LAUNCH_POINT_REFERENCE_PATTERNS.md sections:
- initializeValue examples (lines 84-203)
- beforeSave examples (lines 216-391)
- afterSave examples (lines 400-483)
- afterCommit examples (lines 493-564)
- afterAdd examples (lines 576-640)
- beforeDelete examples (lines 649-714)

#### 6. Naming Conventions
**File:** `Knowledge-base/NAMING_CONVENTIONS.md`

**Key Standards:**
- File naming: [object].[type].[event/action].py (lowercase)
- Script naming: [OBJECT].[TYPE].[EVENT] (uppercase)
- Launch point naming: [OBJECT]_[TYPE]_[EVENT] (uppercase with underscores)
- Variable naming conventions
- Module directory structure

#### 7. Utility Library
**File:** `Knowledge-base/maximo_utility_library.py`

**Key Utilities:**
- Common helper functions
- Reusable code patterns
- Database query utilities
- Date/time utilities
- String manipulation helpers

#### 8. Launch Point Configuration Guide
**File:** `docs/LAUNCH_POINT_CONFIGURATION_GUIDE.md`

**Key Information:**
- How to create Object launch points in Maximo
- How to create Action launch points in Maximo
- Variable binding configuration
- Event types and when to use them (INIT, ADD, SAVE, DELETE, UNDELETE)
- Testing and validation procedures
- Troubleshooting common issues

#### 9. Official Maximo Documentation
**File:** `Knowledge-base/OFFICIAL_DOCUMENTATION.md`

**Key References:**
- Maximo automation scripting documentation links
- API reference documentation
- Best practices from IBM
- MAS 9 migration guidelines

---

## Conversion Patterns

### CRITICAL: Launch Point Reference

**ALWAYS refer to:** `Knowledge-base/LAUNCH_POINT_REFERENCE_PATTERNS.md`

This file contains:
- Complete OBJECT launch point examples with Java method mapping
- All event types: initializeValue, beforeSave, afterSave, afterCommit, afterAdd, beforeDelete
- ATTRIBUTE launch point examples (FLD.VALIDATE, FLD.ACTION, FLD.INIT, FLD.LIST)
- ACTION launch point examples with parameters
- scriptConfig templates for all launch point types
- Real production script examples

**Java Method to Event Timing Quick Reference** (see full details in LAUNCH_POINT_REFERENCE_PATTERNS.md):
```python
# Java: init() → Python: initializeValue: True (no operation flags)
# Java: appValidate() → Python: save: True, add: True, update: True, delete: False, beforeSave: True
# Java: save() BEFORE super.save() → Python: save: True, add: True, update: True, delete: False, beforeSave: True
# Java: save() AFTER super.save() → Python: save: True, add: True, update: True, delete: False, afterSave: True
# Java: save() with otherMbo.save() → Python: save: True, add: True, update: True, delete: False, afterSave: True
# Java: save() with email/notifications → Python: save: True, add: True, update: True, delete: False, afterCommit: True
# Java: add() → Python: save: True, add: True, update: False, delete: False, afterSave: True (ADD must include save!)
# Java: canDelete() → Python: delete: True, beforeDelete: True (no operation flags)
```

### Code Optimization Best Practices

**1. Use Constants for Magic Strings/Numbers**
```python
# ❌ WRONG - Hardcoded values scattered throughout
if status.upper() == "WAPPR":
    if eval_code in ["T", "J", "G"]:
        mbo.setValue("TMG_ISSUELOGIC", "APPR", 2)

# ✅ CORRECT - Constants defined at top
AUTO_APPROVE_CODES = ["T", "J", "G"]
WAPPR_STATUS = "WAPPR"
APPR_STATUS = "APPR"

if status.upper() == WAPPR_STATUS:
    if eval_code in AUTO_APPROVE_CODES:
        mbo.setValue("TMG_ISSUELOGIC", APPR_STATUS, MboConstants.NOACCESSCHECK)
```

**2. Early Returns to Reduce Nesting**
```python
# ❌ WRONG - Deep nesting
def process_data():
    if condition1:
        if condition2:
            if condition3:
                # Do work
                pass

# ✅ CORRECT - Early returns
def process_data():
    if not condition1:
        return
    if not condition2:
        return
    if not condition3:
        return
    # Do work
```

**3. Extract Complex Conditions**
```python
# ❌ WRONG - Complex inline conditions
if (mbo.isModified("field1") or mbo.isModified("field2") or 
    mbo.isModified("field3") or mbo.isModified("field4")) and mbo.isNull("field5"):
    # Do something

# ✅ CORRECT - Extract to variable
eval_fields_modified = (
    mbo.isModified("field1") or 
    mbo.isModified("field2") or 
    mbo.isModified("field3") or 
    mbo.isModified("field4")
)

if eval_fields_modified and mbo.isNull("field5"):
    # Do something
```

**4. Simplify Boolean Logic**
```python
# ❌ WRONG - Unnecessary flag variables
is_rerun_required = True
if status in ["ONE-TIME", "REJECT"]:
    is_rerun_required = False

if is_rerun_required:
    do_work()

# ✅ CORRECT - Direct returns
if status in ["ONE-TIME", "REJECT"]:
    logger.debug("Status is " + status + ", skipping")
    return

do_work()
```

**5. Cache Repeated Method Calls**
```python
# ❌ WRONG - Multiple identical calls
if mbo.getString("STATUS").upper() == "ACTIVE":
    logger.debug("Status: " + mbo.getString("STATUS"))
    process(mbo.getString("STATUS"))

# ✅ CORRECT - Cache the value
status = mbo.getString("STATUS").upper()
if status == "ACTIVE":
    logger.debug("Status: " + status)
    process(status)
```

**6. Use List Comprehension for Validation**
```python
# ❌ WRONG - Multiple OR conditions
if (code.upper() == "T" or code.upper() == "J" or code.upper() == "G"):
    approve()

# ✅ CORRECT - Use list membership
if code.upper() in AUTO_APPROVE_CODES:
    approve()
```

**7. Simplify String Operations**
```python
# ❌ WRONG - Verbose null/empty checks
if memo_value is not None and memo_value != "" and len(memo_value) > 30:
    memo_value = memo_value[0:30]

# ✅ CORRECT - Pythonic checks and slicing
if memo_value and len(memo_value) > MEMO_MAX_LENGTH:
    memo_value = memo_value[:MEMO_MAX_LENGTH]
```

**8. Consistent Error Handling**
```python
# ❌ WRONG - Inconsistent exception handling
try:
    do_work()
except:
    pass

# ✅ CORRECT - Proper logging and re-raise
try:
    do_work()
except Exception as e:
    logger.error(className + ": Error during work", e)
    raise
```

---

### Conversion Pattern Examples

**For complete conversion patterns with scriptConfig templates, see:** `Knowledge-base/LAUNCH_POINT_REFERENCE_PATTERNS.md`

#### Pattern 1: init() → initializeValue

**Java**: `public void init() throws MXException`  
**Python Event**: `initializeValue: True`  
**Reference**: LAUNCH_POINT_REFERENCE_PATTERNS.md lines 77-203

**Key Points**:
- No `super.init()` call needed in Python
- Use `mbo.setValue()` with `MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION`
- Use `mbo.toBeAdded()` to check if new record
- Copy scriptConfig template from reference file

---

#### Pattern 2: appValidate() or save() BEFORE super.save() → beforeSave

**Java**: `public void appValidate() throws MXException` or logic before `super.save()`  
**Python Event**: `beforeSave: True`  
**Reference**: LAUNCH_POINT_REFERENCE_PATTERNS.md lines 206-391

**Key Points**:
- Use for validation and field manipulation before DB save
- Use `service.error()` to prevent save
- Check `onadd`, `onupdate`, `ondelete` for MBO state
- Copy scriptConfig template from reference file

---

#### Pattern 3: save() AFTER super.save() → afterSave

**Java**: Logic after `super.save()` or calls `otherMbo.save()`  
**Python Event**: `afterSave: True`  
**Reference**: LAUNCH_POINT_REFERENCE_PATTERNS.md lines 394-483

**Key Points**:
- Use for creating related records or triggering related saves
- Use `mboSet.add()` and `mboSet.save()` for related records
- Check `onadd`, `onupdate` for trigger conditions
- Copy scriptConfig template from reference file

---

#### Pattern 4: save() with notifications → afterCommit

**Java**: Sends emails, calls external APIs after save  
**Python Event**: `afterCommit: True`  
**Reference**: LAUNCH_POINT_REFERENCE_PATTERNS.md lines 486-564

**Key Points**:
- Use for operations after transaction commit
- Send emails with `MXServer.sendEMail()`
- Cannot rollback from afterCommit
- Copy scriptConfig template from reference file

---

#### Pattern 5: add() → afterAdd

**Java**: `public void add() throws MXException`  
**Python Event**: `afterAdd: True`  
**Reference**: LAUNCH_POINT_REFERENCE_PATTERNS.md lines 567-640

**Key Points**:
- Use for operations after MBO added to set
- Set field values or flags after add completes
- Copy scriptConfig template from reference file

---

#### Pattern 6: canDelete() → beforeDelete

**Java**: `public void canDelete() throws MXException`  
**Python Event**: `beforeDelete: True`  
**Reference**: LAUNCH_POINT_REFERENCE_PATTERNS.md lines 643-714

**Key Points**:
- Use for validation before deletion
- Use `service.error()` to prevent deletion
- Check for related records
- Copy scriptConfig template from reference file

---

#### Pattern 7: Custom Actions

**Java**: `public void customMethod(params) throws MXException`  
**Python Event**: ACTION launch point  
**Reference**: LAUNCH_POINT_REFERENCE_PATTERNS.md lines 1244-1319

**Key Points**:
- Access parameters via `scriptVariables.get("varname")`
- Include `scriptVariables` array in scriptConfig
- Always close MboSets in finally blocks
- Copy scriptConfig template from reference file

---

### Legacy Pattern Examples (For Reference Only)

These examples show the detailed conversion, but **ALWAYS copy scriptConfig from LAUNCH_POINT_REFERENCE_PATTERNS.md**.

#### Pattern 1 (Legacy): Object Launch Point - init() Method

**Java Pattern:**
```java
package tmg.app.assetcatalog;

import psdi.mbo.*;
import psdi.util.*;

public class TMG_ClassSpec extends Mbo {
    
    public TMG_ClassSpec(MboSet ms) throws MXException, RemoteException {
        super(ms);
    }
    
    @Override
    public void init() throws MXException, RemoteException {
        super.init();
        
        // TR008763: Set default value for USEINLOCDESC
        if (toBeAdded()) {
            setValue("USEINLOCDESC", false, 
                    MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION);
        }
    }
}
```

**Python Conversion:**
```python
################################################################################
# Script:
# Object Launch Point - INIT
#
# Launch Point: CLASSSPEC.OBJ.INIT
# Object: CLASSSPEC
################################################################################

from psdi.mbo import MboConstants


def initialize_classspec():
    # Initialize CLASSSPEC object.
    # TR008763: Default USEINLOCDESC to false for new records
    #
    # This function sets default field values for new CLASSSPEC records.
    # Called automatically by Maximo when a new record is initialized.
    
    # Check if this is a new record being added
    if mbo.toBeAdded():
        # Set USEINLOCDESC to false (0) with flags:
        # MboConstants.NOACCESSCHECK (2) | MboConstants.NOVALIDATION (8) = 11
        mbo.setValue("USEINLOCDESC", False, 
                     MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)


# ==========================================================================================
# MAIN EXECUTION
# ==========================================================================================

try:
    initialize_classspec()
    
except Exception as e:
    # Log error and re-raise
    service.error("Error initializing CLASSSPEC: " + str(e))
    raise


# ==========================================================================================
# SCRIPT CONFIGURATION
# ==========================================================================================
scriptConfig = {
    "autoscript": "CLASSSPEC.OBJ.INIT",
    "description": "Initialize CLASSSPEC - Set USEINLOCDESC default value (TR008763)",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "CLASSSPEC_OBJ_INIT",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Initialize CLASSSPEC object with default values",
            "objectName": "CLASSSPEC",
            "initializeValue": True
        }
    ]
}
```

**Key Differences:**
| Java | Python | Notes |
|------|--------|-------|
| `init() throws MXException` | `try/except` block | Python uses exception handling |
| `super.init()` | Not needed | Maximo handles parent initialization |
| `this.setValue()` | `mbo.setValue()` | `mbo` is implicit variable |
| Numeric flags (2L, 8L, 11L) | `MboConstants.NOACCESSCHECK` | Use named constants |
| Constructor required | No constructor | Script executes directly |

---

### Pattern 2: Object Launch Point - save() Method

**Java Pattern:**
```java
package tmg.app.invoice;

import psdi.mbo.*;
import psdi.util.*;
import psdi.util.logging.*;

public class TMG_Invoice extends Mbo {
    
    private static MXLogger logger = MXLoggerFactory.getLogger("maximo.application.INVOICE");
    
    @Override
    public void save() throws MXException, RemoteException {
        logger.debug("TMG_Invoice: Entering save() - Enter");
        super.save();
        logger.debug("TMG_Invoice: Exiting save()");
    }
}
```

**Python Conversion:**
```python
# ============================================================================
# Script: invoice.obj.save.py
# Object: INVOICE
# Launch Point: Object (SAVE event)
# ============================================================================

from psdi.util.logging import MXLoggerFactory

# Initialize logger
logger = MXLoggerFactory.getLogger("maximo.application.INVOICE")
className = "invoice.obj.save"

logger.debug(className + ": Entering save() - Enter")

# Call parent save - this is handled automatically by Maximo
# No additional custom logic needed beyond logging

logger.debug(className + ": Exiting save()")


# ==========================================================================================
# SCRIPT CONFIGURATION
# ==========================================================================================
scriptConfig = {
    "autoscript": "INVOICE.OBJ.SAVE",
    "description": "Invoice save event handler - Logs save operations",
    "version": "1.0.0",
    "active": True,
    "logLevel": "DEBUG",
    "scriptLaunchPoints": [
        {
            "launchPointName": "INVOICE_OBJ_SAVE",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Log invoice save operations",
            "objectName": "INVOICE",
            "save": True,
            "afterSave": True  # Execute after database save
        }
    ]
}
```

**scriptConfig Event Timing Examples:**

```python
# beforeSave - Validation, field manipulation (runs on add and update, not delete)
{
    "objectName": "MR",
    "save": True,
    "add": True,
    "update": True,
    "delete": False,
    "beforeSave": True  # Runs before DB save (appValidate equivalent)
}

# afterSave - Related object saves, business logic (runs on add and update, not delete)
{
    "objectName": "WPMATERIAL",
    "save": True,
    "add": True,
    "update": True,
    "delete": False,
    "afterSave": True  # Runs after DB save, before commit
}

# afterCommit - Notifications, external systems (runs on add and update, not delete)
{
    "objectName": "WORKORDER",
    "save": True,
    "add": True,
    "update": True,
    "delete": False,
    "afterCommit": True  # Runs after transaction commit
}

# add - Post-add initialization (runs ONLY on new records, NOT on updates)
# CRITICAL: ADD events MUST include save: True with timing flags
{
    "objectName": "WPMATERIAL",
    "save": True,
    "add": True,
    "update": False,  # Don't run on updates
    "delete": False,
    "afterSave": True  # Run after add completes
}

# beforeDelete - Delete validation (runs only on deletion)
{
    "objectName": "MR",
    "delete": True,
    "beforeDelete": True  # Runs before deletion (canDelete equivalent)
}
```

**Key Points:**
- Logger initialization at module level
- No explicit super.save() call needed (Maximo handles it)
- Simple logging before/after save
- scriptConfig specifies `"save": True`

---

### Pattern 3: Action Launch Point - Custom Method with Parameters

**Java Pattern:**
```java
package tmg.app.invoice;

import psdi.mbo.*;
import psdi.server.*;

public class TMG_Invoice extends Mbo {
    
    public void doCLRProcess(String desiredStatus) throws MXException, RemoteException {
        MXLogger logger = MXLoggerFactory.getLogger("maximo.application.INVOICE");
        logger.debug("doCLRProcess: Starting CLR processing for status: " + desiredStatus);
        
        // Complex business logic for CLR invoice processing
        MboSetRemote invoiceLineSet = getMboSet("INVOICELINE");
        
        for (int i = 0; i < invoiceLineSet.count(); i++) {
            MboRemote invoiceLine = invoiceLineSet.getMbo(i);
            
            // Process each line
            String ponum = invoiceLine.getString("PONUM");
            int polinenum = invoiceLine.getInt("POLINENUM");
            
            // Create material receipt
            MboSetRemote matRecSet = invoiceLine.getMboSet("MATRECTRANS");
            MboRemote matRec = matRecSet.add();
            matRec.setValue("PONUM", ponum);
            matRec.setValue("POLINENUM", polinenum);
            // ... more logic
        }
        
        // Change invoice status
        changeStatus(desiredStatus, getMXTransaction().getDate(), "");
        
        logger.debug("doCLRProcess: Completed");
    }
}
```

**Python Conversion:**
```python
# ============================================================================
# Script: invoice.action.doclrprocess.py
# Object: INVOICE
# Launch Point: Action (DOCLRPROCESS)
#
# Script Variables:
#   Variable Name: desiredStatus
#   Binding Type: INPARAM
#   Binding Value: desiredStatus
#   Description: Target invoice status (e.g., APPR, PAID)
#
# Usage Examples:
#   Python: mbo.invokeAction("DOCLRPROCESS", "APPR")
#   Java:   mbo.invokeAction("DOCLRPROCESS", "APPR");
# ============================================================================

from psdi.util.logging import MXLoggerFactory
from psdi.mbo import MboConstants

# Initialize logger
logger = MXLoggerFactory.getLogger("maximo.application.INVOICE")
className = "invoice.action.doclrprocess"


def process_clr_invoice():
    # Process CLR invoice with material/service receipts and status changes.
    # This function handles the complex business logic for CLR invoice processing.
    #
    # Parameters:
    #   desiredStatus (str): Target invoice status passed via scriptVariables
    #
    # Raises:
    #   Exception: If desiredStatus parameter is missing
    
    # Get script parameter - desiredStatus passed via invokeAction()
    desiredStatus = scriptVariables.get("desiredStatus")
    
    if not desiredStatus:
        raise Exception("desiredStatus parameter is required")
    
    logger.debug(className + ": Starting CLR processing for status: " + desiredStatus)
    
    # Complex business logic for CLR invoice processing
    invoiceLineSet = mbo.getMboSet("INVOICELINE")
    
    try:
        for i in range(invoiceLineSet.count()):
            invoiceLine = invoiceLineSet.getMbo(i)
            
            # Process each line
            ponum = invoiceLine.getString("PONUM")
            polinenum = invoiceLine.getInt("POLINENUM")
            
            # Create material receipt
            matRecSet = invoiceLine.getMboSet("MATRECTRANS")
            matRec = matRecSet.add()
            matRec.setValue("PONUM", ponum)
            matRec.setValue("POLINENUM", polinenum)
            # ... more logic
            
            matRecSet.save()
            matRecSet.close()
    
    finally:
        # Always close MboSets
        if invoiceLineSet:
            invoiceLineSet.close()
    
    # Change invoice status
    mbo.changeStatus(desiredStatus, MXServer.getMXServer().getDate(), "")
    
    logger.debug(className + ": Completed")


# ==========================================================================================
# MAIN EXECUTION
# ==========================================================================================

try:
    process_clr_invoice()
except Exception as e:
    logger.error(className + ": Error processing CLR invoice", e)
    raise


# ==========================================================================================
# SCRIPT CONFIGURATION
# ==========================================================================================
scriptConfig = {
    "autoscript": "INVOICE.ACT.DOCLRPROCESS",
    "description": "Invoice DOCLRPROCESS action - Process CLR invoice receipts and status changes",
    "version": "1.0.0",
    "active": True,
    "logLevel": "DEBUG",
    "scriptLaunchPoints": [
        {
            "launchPointName": "INVOICE_ACT_DOCLRPROCESS",
            "launchPointType": "ACTION",
            "active": True,
            "description": "Process CLR invoice with material and service receipts",
            "objectName": "INVOICE",
            "action": "DOCLRPROCESS"
        }
    ],
    "scriptVariables": [
        {
            "varname": "desiredStatus",
            "vartype": "IN",
            "description": "Target invoice status (e.g., APPR, PAID)",
            "bindingType": "INPARAM",
            "bindingValue": "desiredStatus",
            "noAccessCheck": False,
            "noValidation": False
        }
    ]
}
```

**Key Points:**
- Action parameters accessed via `scriptVariables.get("varname")`
- MboSets must be closed in finally blocks
- scriptConfig includes `scriptVariables` array
- `vartype` can be "IN", "OUT", or "INOUT"
- `bindingType` matches: INPARAM, OUTPARAM, INOUTPARAM

---

### Pattern 4: Multiple Launch Points (One Script, Multiple Events)

**Scenario:** Sometimes one Java method handles multiple events (rare, but possible)

**scriptConfig Format:**
```python
scriptConfig = {
    "autoscript": "WORKORDER.OBJ.LIFECYCLE",
    "description": "Work order lifecycle management - save, delete, undelete",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "WORKORDER_OBJ_SAVE",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Handle work order save events",
            "objectName": "WORKORDER",
            "save": True
        },
        {
            "launchPointName": "WORKORDER_OBJ_DELETE",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Handle work order delete events",
            "objectName": "WORKORDER",
            "delete": True
        }
    ]
}
```

**Note:** Generally prefer **ONE script per launch point** for clarity and maintainability.

---

## Quality Checklist

### Pre-Conversion Checklist

- [ ] Read complete Java source file
- [ ] Identify all methods to convert (init, save, delete, custom actions)
- [ ] Document TR/business requirements from comments
- [ ] Identify required imports and dependencies
- [ ] Note any organization-specific logic (e.g., ORG1 vs non-ORG1)
- [ ] Check for database operations (JDBC, DBShortcut)
- [ ] Check for relationship traversal (getMboSet)
- [ ] Check for status changes (changeStatus)
- [ ] Determine launch point types needed (OBJECT vs ACTION)
- [ ] Check OBJECT_INVENTORY.md for priority and complexity

### During Conversion Checklist

- [ ] **Copied scriptConfig template from LAUNCH_POINT_REFERENCE_PATTERNS.md**
- [ ] Created module directory: `automation-scripts/object_scripts/[objectname]/`
- [ ] Used proper header format (################ blocks, NO triple quotes)
- [ ] **Used Python idioms, not Java-style methods (.upper() ==, not equalsIgnoreCase)**
- [ ] Extracted magic strings/numbers to module-level constants
- [ ] Used MboConstants instead of numeric flags (2L, 8L, 11L)
- [ ] Implemented proper error handling (try/except with re-raise)
- [ ] **Added comments using # only (NO """ docstrings)**
- [ ] Closed all MboSets in finally blocks
- [ ] Placed scriptConfig at ABSOLUTE END of file
- [ ] **Verified event timing matches Java method analysis**
- [ ] Named file correctly: [object].[type].[event/action].py (lowercase)

### Post-Conversion Checklist

- [ ] **Verified scriptConfig matches template from LAUNCH_POINT_REFERENCE_PATTERNS.md**
- [ ] **Verified event timing correct (beforeSave/afterSave/afterCommit/afterAdd/beforeDelete)**
- [ ] Verified all business logic converted
- [ ] **Verified NO Java-style methods remain (.equalsIgnoreCase → .upper() ==)**
- [ ] **Verified all magic strings/numbers extracted to constants**
- [ ] Verified MboConstants used (no numeric flags like 2L, 8L, 11L)
- [ ] Verified MboSets closed properly in finally blocks
- [ ] Verified logger used for debug/error messages
- [ ] Created README.md for module
- [ ] Updated OBJECT_INVENTORY.md with conversion status
- [ ] Code reviewed against LAUNCH_POINT_REFERENCE_PATTERNS.md examples

### README.md Template

Each object module should include a README.md:

```markdown
# [Object Name] Object Scripts

**Object:** [OBJECTNAME]  
**Module:** [Invoice/Work Order/Inventory/etc.]  
**Status:** ✅ Converted  
**Conversion Date:** 2025-12-01

## Overview

[Brief description of the object and its purpose in Maximo]

## Converted Scripts

### 1. [object].obj.[event].py

**Launch Point Type:** Object  
**Event:** [INIT/SAVE/DELETE/etc.]  
**Purpose:** [Description]

**Business Logic:**
- [Key logic point 1]
- [Key logic point 2]

**TR References:**
- [TR number]: [Description]

---

### 2. [object].action.[actionname].py

**Launch Point Type:** Action  
**Action:** [ACTIONNAME]  
**Purpose:** [Description]

**Parameters:**
- `[paramName]` (IN): [Description]

**Business Logic:**
- [Key logic point 1]
- [Key logic point 2]

**TR References:**
- [TR number]: [Description]

---

## Dependencies

### Maximo Objects Referenced
- [OBJECTNAME1]: [Relationship/purpose]
- [OBJECTNAME2]: [Relationship/purpose]

### Java Imports (Original)
- [Import statements from Java that indicate dependencies]

## Testing Checklist

- [ ] Script deploys successfully in Maximo
- [ ] Launch points created correctly
- [ ] [Event] event triggers script
- [ ] Business logic executes correctly
- [ ] No errors in Maximo logs
- [ ] [Specific test case 1]
- [ ] [Specific test case 2]

## Migration Notes

**Original Java Class:** `tmg.app.[module].[TMG_ClassName]`  
**Lines of Code:** [Java LOC] → [Python LOC]  
**Complexity:** [Simple/Medium/Complex]

**Known Issues:**
- [Any known limitations or issues]

**Special Considerations:**
- [Organization-specific logic notes]
- [Performance considerations]
- [Security considerations]

## See Also

- [SCRIPT_CONFIGURATION.md](SCRIPT_CONFIGURATION.md) - Deployment instructions
- [OBJECT_INVENTORY.md](../OBJECT_INVENTORY.md) - Full conversion tracking
```

### SCRIPT_CONFIGURATION.md Template

Each object module should include deployment instructions:

```markdown
# [Object Name] Script Configuration Guide

**Last Updated:** 2025-12-01  
**Maximo Version:** MAS 9.x  
**Scripts:** [Number] automation scripts

---

## Overview

This document provides step-by-step instructions for deploying the [OBJECT] automation scripts in Maximo.

## Prerequisites

- [ ] Maximo administrator access
- [ ] Access to Automation Scripts application
- [ ] Python language configured in Maximo
- [ ] [Object] object exists in database

---

## Script 1: [object].[type].[event].py

### Launch Point Creation

1. **Navigate to Automation Scripts**
   - Go to: System Configuration > Platform Configuration > Automation Scripts

2. **Create New Script**
   - Click **New Automation Script**
   - Script: `[OBJECT].[TYPE].[EVENT]`
   - Description: `[Description from scriptConfig]`
   - Script Language: **python**
   - Log Level: **[DEBUG/ERROR]**
   - Active: **✓** (checked)

3. **Add Script Source**
   - Copy entire contents of `[object].[type].[event].py`
   - Paste into **Source Code** section
   - Click **Save**

4. **Create Launch Point**
   - In **Launch Points** section, click **New Launch Point**
   - Launch Point: `[LAUNCHPOINT_NAME]`
   - Launch Point Type: **Object**
   - Active: **✓** (checked)
   - Description: `[Description]`

5. **Configure Object Launch Point**
   - Object: `[OBJECT]`
   - Event: **[Event Name]** (e.g., Initialize, Save, Delete)
   - [Event-specific checkbox]: **✓** (checked)

6. **Save Launch Point**
   - Click **OK** to save launch point
   - Click **Save** to save automation script

---

## Script 2: [object].action.[actionname].py

### Launch Point Creation

1. **Navigate to Automation Scripts**
   - Go to: System Configuration > Platform Configuration > Automation Scripts

2. **Create New Script**
   - Click **New Automation Script**
   - Script: `[OBJECT].ACT.[ACTIONNAME]`
   - Description: `[Description from scriptConfig]`
   - Script Language: **python**
   - Log Level: **[DEBUG/ERROR]**
   - Active: **✓** (checked)

3. **Add Script Source**
   - Copy entire contents of `[object].action.[actionname].py`
   - Paste into **Source Code** section
   - Click **Save**

4. **Create Launch Point**
   - In **Launch Points** section, click **New Launch Point**
   - Launch Point: `[LAUNCHPOINT_NAME]`
   - Launch Point Type: **Action**
   - Active: **✓** (checked)
   - Description: `[Description]`

5. **Configure Action Launch Point**
   - Object: `[OBJECT]`
   - Action: `[ACTIONNAME]`

6. **Configure Script Variables** (if applicable)
   
   Click **Create/Manage Variables**
   
   | Variable Name | Binding Type | Binding Value | Description | Type |
   |--------------|-------------|---------------|-------------|------|
   | [varname] | [INPARAM/OUTPARAM] | [varname] | [Description] | [String/Integer/etc.] |

7. **Save Launch Point**
   - Click **OK** to save launch point
   - Click **Save** to save automation script

---

## Testing Checklist

### Script 1: [OBJECT].[TYPE].[EVENT]

- [ ] Script created successfully
- [ ] Launch point created successfully
- [ ] No syntax errors in script
- [ ] [Event] event triggers script execution
- [ ] Logging appears in Maximo logs
- [ ] Business logic executes correctly
- [ ] [Specific test case 1]
- [ ] [Specific test case 2]

### Script 2: [OBJECT].ACT.[ACTIONNAME]

- [ ] Script created successfully
- [ ] Launch point created successfully
- [ ] Script variables configured correctly
- [ ] No syntax errors in script
- [ ] Action invocation works: `mbo.invokeAction("[ACTIONNAME]", [params])`
- [ ] Logging appears in Maximo logs
- [ ] Business logic executes correctly
- [ ] [Specific test case 1]
- [ ] [Specific test case 2]

---

## Deployment Order

**Development Environment:**
1. Deploy Script 1 ([object].[type].[event].py)
2. Test Script 1 thoroughly
3. Deploy Script 2 ([object].action.[actionname].py) (if applicable)
4. Test Script 2 thoroughly
5. Perform integration testing

**Test Environment:**
1. Repeat all development deployment steps
2. Perform comprehensive testing
3. Document any issues

**Production Environment:**
1. Schedule deployment during maintenance window
2. Deploy all scripts in order
3. Verify all launch points are active
4. Monitor Maximo logs for errors
5. Perform smoke testing

---

## Rollback Plan

If issues are encountered:

1. **Disable Launch Points**
   - Navigate to Automation Scripts
   - Find each script
   - Uncheck **Active** on launch points
   - Click **Save**

2. **Deactivate Scripts**
   - Uncheck **Active** on each automation script
   - Click **Save**

3. **Monitor Logs**
   - Check Maximo logs for any errors
   - Document issues for troubleshooting

4. **Re-enable After Fix**
   - Fix issues in development environment
   - Re-test thoroughly
   - Re-deploy to production

---

## Logging Configuration

**Log Levels:**
- **DEBUG**: Detailed execution flow (development/testing)
- **ERROR**: Only errors (production recommended)

**View Logs:**
- Navigate to: Logging > View Logs
- Filter by: `maximo.application.[OBJECT]`
- Review execution details and errors

---

## Support

For issues or questions:
- Review: [README.md](README.md)
- Check: Maximo logs in Logging application
- Reference: [OBJECT_INVENTORY.md](../OBJECT_INVENTORY.md)

---

## Script Invocation Examples

### Object Launch Point (Automatic)
```python
# Script executes automatically on [event] event
# No manual invocation needed
```

### Action Launch Point (Manual)
```python
# Python invocation
invoice = mbo.getMboSet("INVOICE").getMbo(0)
invoice.invokeAction("[ACTIONNAME]", [param1], [param2])
```

```java
// Java invocation
MboRemote invoice = mbo.getMboSet("INVOICE").getMbo(0);
invoice.invokeAction("[ACTIONNAME]", [param1], [param2]);
```

---

**End of Configuration Guide**
```

---

## Example Conversions

### Example 1: Simple Object Init Script

**File:** `automation-scripts/object_scripts/classspec/classspec.obj.init.py`  
**Complexity:** Simple (89 lines)  
**Launch Point:** Object (INIT event)

**Highlights:**
- Simple field initialization
- Uses MboConstants
- Basic error handling
- Complete scriptConfig

**Use Case:** Template for simple object initialization scripts

---

### Example 2: Medium Object Save Script

**File:** `automation-scripts/object_scripts/invoice/invoice.obj.save.py`  
**Complexity:** Simple (58 lines)  
**Launch Point:** Object (SAVE event)

**Highlights:**
- Logger initialization pattern
- Minimal business logic (logging only)
- Clean scriptConfig

**Use Case:** Template for save event handlers with logging

---

### Example 3: Complex Action Script

**File:** `automation-scripts/object_scripts/invoice/invoice.action.doclrprocess.py`  
**Complexity:** Complex (418 lines)  
**Launch Point:** Action (DOCLRPROCESS)

**Highlights:**
- Complex business logic
- Multiple MboSet operations
- Script variables (INPARAM)
- Receipt creation logic
- Database calculations
- Comprehensive error handling
- Complete scriptConfig with variables

**Use Case:** Template for complex action scripts with parameters and business logic

---

## Common Patterns and Solutions

### Pattern: Accessing Script Parameters in Action Scripts

```python
# In ACTION launch point scripts, parameters come from scriptVariables
param1 = scriptVariables.get("param1")
param2 = scriptVariables.get("param2")

# Always validate parameters
if not param1:
    raise Exception("param1 is required")
```

### Pattern: MboSet Operations

```python
# Get related MboSet
relatedSet = mbo.getMboSet("RELATIONSHIPNAME")

try:
    # Iterate through MboSet
    for i in range(relatedSet.count()):
        relatedMbo = relatedSet.getMbo(i)
        
        # Process each MBO
        value = relatedMbo.getString("ATTRIBUTE")
        relatedMbo.setValue("ATTRIBUTE", newValue)
    
    # Save changes
    relatedSet.save()

finally:
    # ALWAYS close MboSets
    if relatedSet:
        relatedSet.close()
```

### Pattern: Using MboConstants

```python
from psdi.mbo import MboConstants

# Instead of: mbo.setValue("FIELD", value, 11L)
# Use named constants:
mbo.setValue("FIELD", value, 
             MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# Common flag combinations:
# - NOACCESSCHECK = 2
# - NOVALIDATION = 8
# - NOACCESSCHECK | NOVALIDATION = 11
# - NOVALIDATION_AND_NOACTION = 128
# - NOVALIDATION_AND_NOACTION_AND_NOCHECK = 130
```

### Pattern: Conditional Logic Based on Object State

```python
# Check if new record
if mbo.toBeAdded():
    # Initialize default values
    mbo.setValue("FIELD", defaultValue)

# Check if being deleted
if mbo.toBeDeleted():
    # Clean up related records
    pass

# Check if specific field changed
if mbo.toBeSaved() and mbo.getMboValue("STATUS").isModified():
    # React to status change
    newStatus = mbo.getString("STATUS")
```

### Pattern: Logger Initialization

```python
from psdi.util.logging import MXLoggerFactory

# Initialize logger (module level)
logger = MXLoggerFactory.getLogger("maximo.application.OBJECTNAME")
className = "objectname.type.event"

# Use logger throughout script
logger.debug(className + ": Starting execution")
logger.error(className + ": Error occurred", exception)
```

### Pattern: Error Handling with Re-raise

```python
try:
    # Main business logic
    process_data()
    
except Exception as e:
    # Log error with context
    logger.error(className + ": Error processing data", e)
    
    # ALWAYS re-raise to mark script execution as failed
    raise
```

---

## scriptConfig Reference

### Object Launch Point Templates

#### 1. INIT Event (Initialize)
```python
scriptConfig = {
    "autoscript": "[OBJECT].OBJ.INIT",
    "description": "Initialize [OBJECT] - [Brief description]",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "[OBJECT]_OBJ_INIT",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Initialize [OBJECT] object with default values",
            "objectName": "[OBJECT]",
            "initializeValue": True
        }
    ]
}
```

#### 2. ADD Event
```python
# CRITICAL: ADD events MUST include save: True with timing flags
# ADD cannot be standalone - must be combined with save event
scriptConfig = {
    "autoscript": "[OBJECT].OBJ.ADD",
    "description": "Handle [OBJECT] add event - [Brief description]",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "[OBJECT]_OBJ_ADD",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Process new [OBJECT] records on add",
            "objectName": "[OBJECT]",
            "save": True,
            "add": True,
            "update": False,  # Don't run on updates
            "delete": False,
            "afterSave": True  # Or beforeSave/afterCommit based on Java method
        }
    ]
}
```

#### 3. SAVE Event - beforeSave
```python
scriptConfig = {
    "autoscript": "[OBJECT].OBJ.SAVE",
    "description": "Handle [OBJECT] save event - [Brief description]",
    "version": "1.0.0",
    "active": True,
    "logLevel": "DEBUG",
    "scriptLaunchPoints": [
        {
            "launchPointName": "[OBJECT]_OBJ_SAVE",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Validate [OBJECT] before save",
            "objectName": "[OBJECT]",
            "save": True,
            "add": True,      # Run on new records
            "update": True,   # Run on existing record updates
            "delete": False,  # Don't run on deletion
            "beforeSave": True
        }
    ]
}
```

#### 3b. SAVE Event - afterSave
```python
scriptConfig = {
    "autoscript": "[OBJECT].OBJ.SAVE",
    "description": "Handle [OBJECT] save event - [Brief description]",
    "version": "1.0.0",
    "active": True,
    "logLevel": "DEBUG",
    "scriptLaunchPoints": [
        {
            "launchPointName": "[OBJECT]_OBJ_SAVE",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Process [OBJECT] after save",
            "objectName": "[OBJECT]",
            "save": True,
            "add": True,      # Run on new records
            "update": True,   # Run on existing record updates
            "delete": False,  # Don't run on deletion
            "afterSave": True
        }
    ]
}
```

#### 3c. SAVE Event - afterCommit
```python
scriptConfig = {
    "autoscript": "[OBJECT].OBJ.SAVE",
    "description": "Handle [OBJECT] save event - [Brief description]",
    "version": "1.0.0",
    "active": True,
    "logLevel": "DEBUG",
    "scriptLaunchPoints": [
        {
            "launchPointName": "[OBJECT]_OBJ_SAVE",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Send notifications after [OBJECT] saved",
            "objectName": "[OBJECT]",
            "save": True,
            "add": True,      # Run on new records
            "update": True,   # Run on existing record updates
            "delete": False,  # Don't run on deletion
            "afterCommit": True
        }
    ]
}
```

#### 4. DELETE Event
```python
scriptConfig = {
    "autoscript": "[OBJECT].OBJ.DELETE",
    "description": "Handle [OBJECT] delete event - [Brief description]",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "[OBJECT]_OBJ_DELETE",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Process [OBJECT] records on delete",
            "objectName": "[OBJECT]",
            "delete": True
        }
    ]
}
```

#### 5. UNDELETE Event
```python
scriptConfig = {
    "autoscript": "[OBJECT].OBJ.UNDELETE",
    "description": "Handle [OBJECT] undelete event - [Brief description]",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "[OBJECT]_OBJ_UNDELETE",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Process [OBJECT] records on undelete",
            "objectName": "[OBJECT]",
            "undelete": True
        }
    ]
}
```

### Action Launch Point Templates

#### 1. Action with Single Input Parameter
```python
scriptConfig = {
    "autoscript": "[OBJECT].ACT.[ACTIONNAME]",
    "description": "[Action description] - [Brief purpose]",
    "version": "1.0.0",
    "active": True,
    "logLevel": "DEBUG",
    "scriptLaunchPoints": [
        {
            "launchPointName": "[OBJECT]_ACT_[ACTIONNAME]",
            "launchPointType": "ACTION",
            "active": True,
            "description": "[Detailed action description]",
            "objectName": "[OBJECT]",
            "action": "[ACTIONNAME]"
        }
    ],
    "scriptVariables": [
        {
            "varname": "inputParam",
            "vartype": "IN",
            "description": "Input parameter description",
            "bindingType": "INPARAM",
            "bindingValue": "inputParam",
            "noAccessCheck": False,
            "noValidation": False
        }
    ]
}
```

#### 2. Action with Multiple Parameters (IN, OUT, INOUT)
```python
scriptConfig = {
    "autoscript": "[OBJECT].ACT.[ACTIONNAME]",
    "description": "[Action description] with multiple parameters",
    "version": "1.0.0",
    "active": True,
    "logLevel": "DEBUG",
    "scriptLaunchPoints": [
        {
            "launchPointName": "[OBJECT]_ACT_[ACTIONNAME]",
            "launchPointType": "ACTION",
            "active": True,
            "description": "[Action description]",
            "objectName": "[OBJECT]",
            "action": "[ACTIONNAME]"
        }
    ],
    "scriptVariables": [
        {
            "varname": "inputValue",
            "vartype": "IN",
            "description": "Input value to process",
            "bindingType": "INPARAM",
            "bindingValue": "inputValue",
            "noAccessCheck": False,
            "noValidation": False
        },
        {
            "varname": "resultMessage",
            "vartype": "OUT",
            "description": "Result message returned to caller",
            "bindingType": "OUTPARAM",
            "bindingValue": "resultMessage",
            "noAccessCheck": False,
            "noValidation": False
        },
        {
            "varname": "statusFlag",
            "vartype": "INOUT",
            "description": "Status flag (input/output)",
            "bindingType": "INOUTPARAM",
            "bindingValue": "statusFlag",
            "noAccessCheck": False,
            "noValidation": False
        }
    ]
}
```

#### 3. Action with No Parameters
```python
scriptConfig = {
    "autoscript": "[OBJECT].ACT.[ACTIONNAME]",
    "description": "[Action description] - No parameters",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "[OBJECT]_ACT_[ACTIONNAME]",
            "launchPointType": "ACTION",
            "active": True,
            "description": "[Action description]",
            "objectName": "[OBJECT]",
            "action": "[ACTIONNAME]"
        }
    ]
    # No scriptVariables array needed
}
```

**Variable Types Reference:**
| vartype | bindingType | Usage | Access Pattern |
|---------|-------------|-------|----------------|
| `IN` | `INPARAM` | Input parameter (read-only from script) | `value = scriptVariables.get("varname")` |
| `OUT` | `OUTPARAM` | Output parameter (script sets value) | `scriptVariables["varname"] = value` |
| `INOUT` | `INOUTPARAM` | Input/output parameter (read and write) | Read: `value = scriptVariables.get("varname")`<br>Write: `scriptVariables["varname"] = value` |

**Common Variable Data Types:**
- String: Text values
- Integer: Whole numbers
- Boolean: True/False values
- Date: Date/time values
- Decimal: Decimal numbers
    "description": "[OBJECT] lifecycle management - multiple events",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "[OBJECT]_OBJ_INIT",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Initialize [OBJECT] with defaults",
            "objectName": "[OBJECT]",
            "initializeValue": True
        },
        {
            "launchPointName": "[OBJECT]_OBJ_SAVE",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Validate and save [OBJECT]",
            "objectName": "[OBJECT]",
            "save": True
        },
        {
            "launchPointName": "[OBJECT]_OBJ_DELETE",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Clean up on [OBJECT] delete",
            "objectName": "[OBJECT]",
            "delete": True
        }
    ]
}
```
**Note:** Only use multiple launch points in one script when events share common logic. Otherwise, create separate scripts for clarity.

#### 5. Complete Real-World Example (INVOICE.ACT.DOCLRPROCESS)
```python
scriptConfig = {
    "autoscript": "INVOICE.ACT.DOCLRPROCESS",
    "description": "Invoice DOCLRPROCESS action - Process CLR invoice receipts and status changes",
    "version": "1.0.0",
    "active": True,
    "logLevel": "DEBUG",
    "scriptLaunchPoints": [
        {
            "launchPointName": "INVOICE_ACT_DOCLRPROCESS",
            "launchPointType": "ACTION",
            "active": True,
            "description": "Process CLR invoice with material and service receipts",
            "objectName": "INVOICE",
            "action": "DOCLRPROCESS"
        }
    ],
    "scriptVariables": [
        {
            "varname": "desiredStatus",
            "vartype": "IN",
            "description": "Target invoice status (e.g., APPR, PAID)",
            "bindingType": "INPARAM",
            "bindingValue": "desiredStatus",
            "noAccessCheck": False,
            "noValidation": False
        }
    ]
}
```

#### 6. Complete Real-World Example (CLASSSPEC.OBJ.INIT)
```python
scriptConfig = {
    "autoscript": "CLASSSPEC.OBJ.INIT",
    "description": "Initialize CLASSSPEC - Set USEINLOCDESC default value (TR008763)",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "CLASSSPEC_OBJ_INIT",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Initialize CLASSSPEC object with default values",
            "objectName": "CLASSSPEC",
            "initializeValue": True
        }
    ]
}
```

---

## Post-Conversion Tracking

### Update OBJECT_INVENTORY.md

After completing conversion, update the tracking document:

1. **Find the MBO** in OBJECT_INVENTORY.md
2. **Move from "Not Started" to "Converted"** section
3. **Add conversion metadata**:
   ```markdown
   - [ ] TMG_Invoice - `TMGMaximo/businessobjects/classes/tmg/app/invoice/TMG_Invoice.java` (418 LOC)
         - **Priority**: High
         - **Complexity**: Complex
         - **Scripts Created**: invoice.obj.save.py, invoice.action.doclrprocess.py
         - **Conversion Date**: 2025-12-01
         - **Notes**: CLR invoice processing, material/service receipt creation
   ```

4. **Update conversion count** in header
   - Increment "Converted" count
   - Decrement appropriate priority count

5. **Git commit** with conversion details

---

## Common Issues and Solutions

### Issue 1: Implicit Variables Undefined (Lint Errors)

**Problem:** Linter shows errors for `mbo`, `scriptVariables`, `service`

**Solution:** These are **expected** and **normal**
- These variables are provided by Maximo's automation script runtime
- They are injected when the script executes
- Lint errors can be safely ignored

**Expected implicit variables:**
- `mbo` - The MBO or MboValue being processed
- `scriptVariables` - Dictionary of script variables (ACTION launch points)
- `service` - Maximo service object
- `launchpoint` - Launch point configuration

### Issue 2: MboSets Not Closed

**Problem:** Memory leaks or locked records

**Solution:** **ALWAYS** close MboSets in finally blocks
```python
mboSet = None
try:
    mboSet = mbo.getMboSet("RELATIONSHIP")
    # Use mboSet
finally:
    if mboSet:
        mboSet.close()
```

### Issue 3: Numeric Flag Constants

**Problem:** Java uses numeric constants (2L, 7L, 11L)

**Solution:** Use MboConstants named constants
```python
# Instead of: mbo.setValue("FIELD", value, 11)
# Use:
from psdi.mbo import MboConstants
mbo.setValue("FIELD", value, 
             MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

**Common Flag Values:**
| Numeric | Constant | Meaning |
|---------|----------|---------|
| 2 | NOACCESSCHECK | Skip access check |
| 8 | NOVALIDATION | Skip validation |
| 11 | NOACCESSCHECK \| NOVALIDATION | Skip both |
| 128 | NOVALIDATION_AND_NOACTION | Skip validation and action |
| 130 | NOVALIDATION_AND_NOACTION_AND_NOCHECK | Skip all checks |

### Issue 4: scriptConfig Placement

**Problem:** Code after scriptConfig causes issues

**Solution:** **ALWAYS** place scriptConfig at **ABSOLUTE END** of file
```python
# Main code
try:
    # Business logic
    pass
except Exception as e:
    raise

# Script Configuration - MUST BE LAST
scriptConfig = {
    # ... config
}
# <-- END OF FILE
```

---

## Summary

This prompt template provides a comprehensive guide for converting Java MBO classes to Python automation scripts for Maximo MAS 9 upgrade.

**Key Principles:**
1. **Analyze before converting** - Understand all methods and logic, refer to LAUNCH_POINT_REFERENCE_PATTERNS.md
2. **Use proper headers** - Follow standardized format
3. **Preserve business logic** - Don't skip or simplify
4. **Close all resources** - MboSets, ResultSets, Connections
5. **Use named constants** - MboConstants instead of numbers
6. **Handle errors properly** - try/except with re-raise
7. **Document thoroughly** - Comments, README, SCRIPT_CONFIGURATION
8. **Track progress** - Update OBJECT_INVENTORY.md
9. **Test completely** - Use testing checklists
10. **Map Java methods correctly** - Use Java-to-timing mapping from LAUNCH_POINT_REFERENCE_PATTERNS.md

**Primary Reference Documents (in order of importance):**
1. **`Knowledge-base/LAUNCH_POINT_REFERENCE_PATTERNS.md`** - ALWAYS use this for launch point examples and scriptConfig
2. `Knowledge-base/maximo_script_patterns_reference.md` - General MBO patterns and best practices
3. `automation-scripts/object_scripts/OBJECT_INVENTORY.md` - Conversion tracking and priority
4. `Knowledge-base/JAVA_TO_PYTHON_CONVERSION_PROMPTS.md` - Java to Python syntax conversion
5. `Knowledge-base/NAMING_CONVENTIONS.md` - Naming standards
6. `Knowledge-base/script_header_template.py` - Header template
7. `Knowledge-base/AGENT_PROMPTS.md` - Additional prompt templates

**Next Steps:**
1. Select next MBO from OBJECT_INVENTORY.md (prioritize High priority)
2. Apply this prompt template
3. Convert Java to Python
4. Create documentation
5. Update tracking
6. Test and deploy

---

**End of Prompt Template**
