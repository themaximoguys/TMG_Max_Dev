# Code Optimization Guide

**Purpose**: Comprehensive guide for optimizing Python automation scripts converted from Java MBOs  
**Version**: 1.0.0  
**Last Updated**: 2025-12-01  
**Context**: MAS 9 upgrade - Best practices for clean, efficient Python/Jython code

---

## Table of Contents

1. [Python Idioms vs Java Style](#python-idioms-vs-java-style)
2. [Code Optimization Patterns](#code-optimization-patterns)
3. [Performance Best Practices](#performance-best-practices)
4. [Maintainability Improvements](#maintainability-improvements)
5. [Before/After Examples](#beforeafter-examples)

---

## Python Idioms vs Java Style

### String Comparisons

#### ❌ WRONG - Java Style
```python
if string.equalsIgnoreCase("VALUE"):
if not string.equalsIgnoreCase("VALUE"):
if string.equals("TEST"):
if string1.equalsIgnoreCase("A") or string2.equalsIgnoreCase("B") or string3.equalsIgnoreCase("C"):
```

#### ✅ CORRECT - Python Style
```python
if string.upper() == "VALUE":
if string.upper() != "VALUE":
if string == "TEST":
if string.upper() in ["A", "B", "C"]:  # More efficient for multiple checks
```

**Benefits:**
- Native Python operators (faster)
- More readable
- Handles None gracefully with proper checks
- List membership is O(1) for small lists

---

### Type Checking

#### ❌ WRONG - Using isinstance with Java Classes
```python
if isinstance(obj, tmg.app.workorder.TMG_PlusWO):
    # Process TMG_PlusWO
elif isinstance(obj, psdi.plus.app.permit.PlusPermit):
    # Process PlusPermit
```

#### ✅ CORRECT - Use getClass().getName()
```python
obj_class = obj.getClass().getName()
if "TMG_PlusWO" in obj_class:
    # Process TMG_PlusWO
elif "PlusPermit" in obj_class:
    # Process PlusPermit
```

**Benefits:**
- Avoids import dependencies
- More reliable in Maximo/Jython environment
- Handles class loading inconsistencies
- Works with proxy objects

---

## Code Optimization Patterns

### 1. Use Constants for Magic Values

#### ❌ WRONG - Hardcoded Values
```python
def check_org():
    if mbo.getString("ORGID").upper() != "ORG1":
        return

def check_status():
    if status.upper() == "WAPPR":
        process()

def check_eval_code():
    if code.upper() in ["T", "J", "G"]:
        approve()
```

#### ✅ CORRECT - Constants at Module Level
```python
# Constants
SNC_ORG = "ORG1"
WAPPR_STATUS = "WAPPR"
AUTO_APPROVE_CODES = ["T", "J", "G"]  # PPM33237
REVIEW_STATUS = "REVIEW"
APPR_STATUS = "APPR"
MEMO_MAX_LENGTH = 30

def check_org():
    if mbo.getString("ORGID").upper() != SNC_ORG:
        return

def check_status():
    if status.upper() == WAPPR_STATUS:
        process()

def check_eval_code():
    if code.upper() in AUTO_APPROVE_CODES:
        approve()
```

**Benefits:**
- Single source of truth
- Easy to update values
- Self-documenting code
- Easier testing
- Reduces typos

---

### 2. Early Returns to Reduce Nesting

#### ❌ WRONG - Deep Nesting
```python
def process_material():
    if wo_mbo is not None:
        if status.upper() == "WAPPR":
            if asset_remote is not None:
                if mbo.getString("TMG_ISSUELOGIC") == "":
                    # Deep nested logic here
                    if mbo.getBoolean("DIRECTREQ"):
                        # Even deeper
                        pass
```

#### ✅ CORRECT - Guard Clauses
```python
def process_material():
    # Guard clauses - fail fast
    if wo_mbo is None:
        logger.debug("No work order found")
        return
    
    if status.upper() != "WAPPR":
        logger.debug("Status not WAPPR, skipping")
        return
    
    if asset_remote is None:
        logger.debug("No asset found")
        return
    
    if mbo.getString("TMG_ISSUELOGIC") != "":
        logger.debug("Issue logic already set")
        return
    
    # Main logic at top level
    if mbo.getBoolean("DIRECTREQ"):
        process_direct_req()
```

**Benefits:**
- Reduces cognitive load
- Easier to read and debug
- Clear exit conditions
- Less indentation
- Better error messages

---

### 3. Extract Complex Conditions

#### ❌ WRONG - Complex Inline Conditions
```python
if ((mbo.isModified("tmg_evalcomment") or 
     mbo.isModified("tmg_feedbkqual") or 
     mbo.isModified("tmg_pmrecexp") or 
     mbo.isModified("tmg_pmrecommend")) and 
    mbo.isNull("tmg_evaluationby")):
    populate_evaluation()
```

#### ✅ CORRECT - Named Variables
```python
eval_fields_modified = (
    mbo.isModified("tmg_evalcomment") or 
    mbo.isModified("tmg_feedbkqual") or 
    mbo.isModified("tmg_pmrecexp") or 
    mbo.isModified("tmg_pmrecommend")
)

if eval_fields_modified and mbo.isNull("tmg_evaluationby"):
    populate_evaluation()
```

**Benefits:**
- Self-documenting
- Easier to debug
- Can be reused
- Clear intent

---

### 4. Eliminate Unnecessary Boolean Flags

#### ❌ WRONG - Redundant Flag Variable
```python
is_rerun_required = True

if (not mbo.isNull("TMG_ISSUELOGIC") and 
    (mbo.getString("TMG_ISSUELOGIC").equals("ONE-TIME") or
     mbo.getString("TMG_ISSUELOGIC").equals("REJECT"))):
    is_rerun_required = False

if is_rerun_required:
    run_issue_logic()
```

#### ✅ CORRECT - Direct Returns
```python
issue_logic_status = mbo.getString("TMG_ISSUELOGIC")

if issue_logic_status in ["ONE-TIME", "REJECT"]:
    logger.debug("Issue logic is " + issue_logic_status + ", skipping rerun")
    return

run_issue_logic()
```

**Benefits:**
- Less code to maintain
- Clearer logic flow
- No intermediate state
- Easier to understand

---

### 5. Cache Repeated Method Calls

#### ❌ WRONG - Multiple Identical Calls
```python
if mbo.getString("ITEMNUM") is not None:
    logger.debug("Processing item: " + mbo.getString("ITEMNUM"))
    TMG_IssueLogicAlgo.runIssueLogic(mbo, asset, None, mbo.getString("ITEMNUM"), storeloc)
    
if inventory_check.getString("tmg_evaluationcode").upper() in ["T", "J", "G"]:
    logger.debug("Eval code: " + inventory_check.getString("tmg_evaluationcode"))
```

#### ✅ CORRECT - Cache Values
```python
item_num = mbo.getString("ITEMNUM")
if item_num:
    logger.debug("Processing item: " + item_num)
    TMG_IssueLogicAlgo.runIssueLogic(mbo, asset, None, item_num, storeloc)

eval_code = inventory_check.getString("tmg_evaluationcode").upper()
if eval_code in AUTO_APPROVE_CODES:
    logger.debug("Eval code: " + eval_code)
```

**Benefits:**
- Performance improvement
- Avoids repeated MBO lookups
- More readable
- Consistent values

---

### 6. Simplify String Operations

#### ❌ WRONG - Verbose Null/Empty Checks
```python
memo_value = mbo.getString("TMG_MEMO")
if memo_value is not None and memo_value != "" and len(memo_value) > 30:
    pr.setValue("TMG_INTERNALCOMMENT", memo_value[0:30], MboConstants.NOACCESSCHECK)
else:
    pr.setValue("TMG_INTERNALCOMMENT", memo_value, MboConstants.NOACCESSCHECK)
```

#### ✅ CORRECT - Pythonic Checks
```python
memo_value = mbo.getString("TMG_MEMO")
if memo_value and len(memo_value) > MEMO_MAX_LENGTH:
    memo_value = memo_value[:MEMO_MAX_LENGTH]
pr.setValue("TMG_INTERNALCOMMENT", memo_value, MboConstants.NOACCESSCHECK)
```

**Benefits:**
- Pythonic truthiness check
- Cleaner slicing syntax
- Single setValue call
- Less code

---

### 7. Use List Membership for Multiple OR Conditions

#### ❌ WRONG - Chained OR Conditions
```python
if (app.equalsIgnoreCase("PLUSWOTR") or 
    app.equalsIgnoreCase("WOTRACK") or 
    app.equalsIgnoreCase("PLUSVWO")):
    process()

if (status.equalsIgnoreCase("CLOSE") or 
    status.equalsIgnoreCase("CAN")):
    skip()
```

#### ✅ CORRECT - List Membership
```python
VALID_APPS = ["PLUSWOTR", "WOTRACK", "PLUSVWO"]
CLOSED_STATUSES = ["CLOSE", "CAN"]

if app.upper() in VALID_APPS:
    process()

if status.upper() in CLOSED_STATUSES:
    skip()
```

**Benefits:**
- O(1) lookup for small lists
- Easy to add/remove values
- More maintainable
- Self-documenting

---

### 8. Consistent Error Handling

#### ❌ WRONG - Silent Failures or Generic Catch
```python
try:
    process_data()
except:
    pass  # Silent failure

try:
    other_process()
except Exception:
    print("Error")  # No context
```

#### ✅ CORRECT - Proper Logging and Re-raise
```python
try:
    process_data()
except Exception as e:
    logger.error(className + ": Error processing data", e)
    raise

try:
    other_process()
except Exception as e:
    logger.error(className + ": Error in other_process: " + str(e), e)
    raise
```

**Benefits:**
- Maximo marks script as failed
- Detailed error context
- Stack trace preserved
- Easier debugging

---

## Performance Best Practices

### 1. Minimize MboSet Reopening

#### ❌ WRONG - Multiple Set Opens
```python
for i in range(10):
    asset_set = mbo.getMboSet("ASSET")
    asset = asset_set.getMbo(0)
    process(asset)
    asset_set.close()
```

#### ✅ CORRECT - Open Once
```python
asset_set = None
try:
    asset_set = mbo.getMboSet("ASSET")
    for i in range(10):
        asset = asset_set.getMbo(0)
        process(asset)
finally:
    if asset_set is not None:
        asset_set.close()
```

---

### 2. Use Shared MboSets for Lookups

#### ❌ WRONG - Individual Lookups
```python
for mrline in mrline_set:
    # Creates new set for each line
    prline_set = mbo.getMboSet("PRLINE", "mrlinenum=:mrlinenum")
```

#### ✅ CORRECT - Shared Set
```python
for mrline in mrline_set:
    where_clause = "orgid=:orgid and siteid=:siteid and mrnum=:mrnum and mrlinenum=:mrlinenum"
    prline_set = mrline.getThisMboSet().getSharedMboSet("PRLINE", where_clause)
```

---

### 3. Early Exit on Empty Sets

#### ❌ WRONG - Process Empty Sets
```python
mrline_set = mbo.getMboSet("MRLINE")
for i in range(mrline_set.count()):
    mrline = mrline_set.getMbo(i)
    process(mrline)
```

#### ✅ CORRECT - Check First
```python
mrline_set = mbo.getMboSet("MRLINE")

if mrline_set.isEmpty():
    logger.debug("No MR lines to process")
    return

for i in range(mrline_set.count()):
    mrline = mrline_set.getMbo(i)
    process(mrline)
```

---

## Maintainability Improvements

### 1. Function Naming

Use descriptive, action-oriented names:

```python
# ❌ WRONG
def check():
def do_logic():
def process():

# ✅ CORRECT
def check_issue_logic_enabled():
def calculate_evaluation_requirement():
def process_feedback_details():
```

---

### 2. Comments Explain Why, Not What

```python
# ❌ WRONG - Stating the obvious
# Get the item number
item_num = mbo.getString("ITEMNUM")

# ✅ CORRECT - Explain business logic
# PPM33237: Cache item number for Issue Logic algorithm
# to avoid multiple MBO lookups during processing
item_num = mbo.getString("ITEMNUM")
```

---

### 3. Group Related Constants

```python
# ✅ CORRECT
# Status Constants
WAPPR_STATUS = "WAPPR"
DRAFT_STATUS = "DRAFT"
REVIEW_STATUS = "REVIEW"
APPR_STATUS = "APPR"

# Evaluation Code Constants (PPM33237)
AUTO_APPROVE_CODES = ["T", "J", "G"]

# Organization Constants
SNC_ORG = "ORG1"

# Field Length Limits
MEMO_MAX_LENGTH = 30
COMMENT_MAX_LENGTH = 100
```

---

## Before/After Examples

### Example 1: WPMaterial Issue Logic Check

#### Before (Java Style)
```python
def call_issue_logic(site):
    wo_mbo = mbo.getOwner().getOwner()
    
    if wo_mbo is None:
        wo_mbo = mbo.getOwner()
    
    if wo_mbo is None:
        return
    
    asset_set = wo_mbo.getMboSet("ASSET")
    status = wo_mbo.getTranslator().toInternalString("WOSTATUS", wo_mbo.getString("status"))
    
    if not asset_set.isEmpty():
        asset_remote = asset_set.getMbo(0)
    else:
        if status.equalsIgnoreCase("WAPPR") and mbo.getString("TMG_ISSUELOGIC").equalsIgnoreCase(""):
            mbo.setValue("TMG_ISSUELOGIC", "REVIEW", 2)
            return
    
    if status.equalsIgnoreCase("WAPPR") and asset_remote is not None:
        if not mbo.getString("TMG_ISSUELOGIC").equalsIgnoreCase(""):
            return
        
        is_rerun_required = True
        
        if (not mbo.isNull("TMG_ISSUELOGIC") and 
            (mbo.getString("TMG_ISSUELOGIC").equals("ONE-TIME") or
             mbo.getString("TMG_ISSUELOGIC").equals("REJECT"))):
            is_rerun_required = False
        
        if is_rerun_required:
            TMG_IssueLogicAlgo.runIssueLogic(mbo, asset_remote, None, item_num, storeloc)
```

#### After (Optimized Python)
```python
# Constants
WAPPR_STATUS = "WAPPR"
REVIEW_STATUS = "REVIEW"

def call_issue_logic(site):
    # Get work order (may be nested for tasks)
    wo_mbo = mbo.getOwner().getOwner() or mbo.getOwner()
    
    if wo_mbo is None:
        logger.debug(className + ": No work order found")
        return
    
    asset_set = None
    
    try:
        asset_set = wo_mbo.getMboSet("ASSET")
        status = wo_mbo.getTranslator().toInternalString("WOSTATUS", wo_mbo.getString("status"))
        
        # Early exit: No asset, set to REVIEW if WAPPR
        if asset_set.isEmpty():
            if status.upper() == WAPPR_STATUS and mbo.getString("TMG_ISSUELOGIC") == "":
                mbo.setValue("TMG_ISSUELOGIC", REVIEW_STATUS, MboConstants.NOACCESSCHECK)
            return
        
        asset_remote = asset_set.getMbo(0)
        
        # Early exit: Not WAPPR status
        if status.upper() != WAPPR_STATUS:
            return
        
        # Early exit: Issue logic already set
        issue_logic_status = mbo.getString("TMG_ISSUELOGIC")
        if issue_logic_status != "":
            logger.debug(className + ": Issue logic already set, skipping")
            return
        
        # Early exit: Status is ONE-TIME or REJECT (no rerun)
        if issue_logic_status in ["ONE-TIME", "REJECT"]:
            logger.debug(className + ": Status is " + issue_logic_status + ", skipping rerun")
            return
        
        # Run Issue Logic algorithm
        item_num = mbo.getString("ITEMNUM")
        TMG_IssueLogicAlgo.runIssueLogic(mbo, asset_remote, None, item_num, storeloc)
    
    finally:
        if asset_set is not None:
            asset_set.close()
```

**Improvements:**
- ✅ Constants for status values
- ✅ Early returns reduce nesting
- ✅ Cached `issue_logic_status`
- ✅ Eliminated `is_rerun_required` flag
- ✅ Python `or` operator for null coalescing
- ✅ Proper try/finally for resource cleanup
- ✅ Better logging

---

### Example 2: MR Approval Evaluation Code Check

#### Before (Java Style)
```python
if inventory_check.getMboValueData("TMG_EVALUATIONCODE").isNull():
    mrline_remote.setValue("TMG_ISSUELOGIC", "REVIEW", 2)
    return
elif (inventory_check.getString("tmg_evaluationcode").equalsIgnoreCase("T") or 
      inventory_check.getString("tmg_evaluationcode").equalsIgnoreCase("J") or 
      inventory_check.getString("tmg_evaluationcode").equalsIgnoreCase("G")):
    mrline_remote.setValue("TMG_ISSUELOGIC", "APPR", 2)
    return
```

#### After (Optimized Python)
```python
# Constants at top of file
AUTO_APPROVE_CODES = ["T", "J", "G"]  # PPM33237
REVIEW_STATUS = "REVIEW"
APPR_STATUS = "APPR"

# In function
if inventory_check.getMboValueData("TMG_EVALUATIONCODE").isNull():
    mrline_remote.setValue("TMG_ISSUELOGIC", REVIEW_STATUS, MboConstants.NOACCESSCHECK)
    return

eval_code = inventory_check.getString("tmg_evaluationcode").upper()
if eval_code in AUTO_APPROVE_CODES:
    mrline_remote.setValue("TMG_ISSUELOGIC", APPR_STATUS, MboConstants.NOACCESSCHECK)
    return
```

**Improvements:**
- ✅ Constants for codes and statuses
- ✅ Cached `eval_code` (single lookup)
- ✅ List membership instead of OR chain
- ✅ Named constant `MboConstants.NOACCESSCHECK`
- ✅ Self-documenting with PPM reference

---

## Summary Checklist

When converting Java to Python, always:

- [ ] Replace `.equalsIgnoreCase()` with `.upper() ==`
- [ ] Replace `.equals()` with `==`
- [ ] Replace `isinstance()` with `getClass().getName()`
- [ ] Define constants for magic strings/numbers
- [ ] Use early returns to reduce nesting
- [ ] Extract complex conditions to named variables
- [ ] Eliminate unnecessary boolean flags
- [ ] Cache repeated method calls
- [ ] Use Pythonic string operations
- [ ] Use list membership for multiple OR conditions
- [ ] Implement proper error handling (log + re-raise)
- [ ] Add try/finally blocks for MboSet cleanup
- [ ] Use descriptive function names
- [ ] Comment business logic, not obvious code
- [ ] Group related constants together

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-12-01  
**Next Review**: After next 5 MBO conversions
