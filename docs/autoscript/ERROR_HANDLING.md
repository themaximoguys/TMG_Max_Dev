# ERROR_HANDLING.md - Error Handling Patterns

**Standard error handling patterns for all Maximo automation scripts.**

---

## Core Principle

Every script must handle errors in a way that:
1. **Informs the user** with a clear, actionable message
2. **Logs the error** with enough context to debug
3. **Preserves the exception stack** for Maximo's error system
4. **Never silently swallows** exceptions

---

## Standard Error Handling Template

```python
from psdi.util.logging import MXLoggerFactory
from psdi.util import MXApplicationException

logger = MXLoggerFactory.getLogger("maximo.script.[scriptname]")

try:
    # --- script logic here ---
    pass

except MXApplicationException:
    raise  # Always re-raise Maximo exceptions unchanged

except Exception as e:
    logger.error("Error in [scriptname]: " + str(e))
    raise  # Re-raise to surface in Maximo UI
```

---

## MXApplicationException — User-Facing Errors

Use this to show a **clear message to the user** in the Maximo UI.

### Syntax

```python
raise MXApplicationException(bundle, key, params, cause)
```

| Parameter | Description | Example |
|-----------|-------------|---------|
| `bundle` | Message bundle name (usually the object name) | `"po"`, `"invoice"`, `"mbo"` |
| `key` | Message key in the bundle | `"vendorrequired"`, `"invalidstatus"` |
| `params` | List of substitution values for the message | `[vendor_code]` |
| `cause` | Original exception (usually `None`) | `None` |

### Examples

```python
# Simple message — no parameters
raise MXApplicationException("po", "vendorrequired", None, None)

# Message with substitution value
raise MXApplicationException("po", "invalidvendor", [vendor], None)

# Message with multiple values
raise MXApplicationException("invoice", "amountexceedslimit",
    [str(amount), str(limit)], None)
```

---

## Logging Levels

```python
logger = MXLoggerFactory.getLogger("maximo.script.po.vendor.validate")

# ERROR — something went wrong, needs investigation
logger.error("Failed to validate vendor: " + vendor)

# WARN — unexpected but recoverable situation
logger.warn("Vendor lookup returned no results for: " + vendor)

# INFO — significant business event
logger.info("PO " + po_num + " approved by: " + approver)

# DEBUG — detailed tracing for development
logger.debug("Checking vendor status: " + str(status))
```

**Production recommendation:** Use `ERROR` and `INFO` in production. Use `DEBUG` only during development.

---

## Pattern 1: Validation with User Message

```python
try:
    status = mbo.getString("STATUS")
    valid_statuses = ["WAPPR", "APPR", "CLOSE"]

    if status not in valid_statuses:
        raise MXApplicationException("workorder", "invalidstatus",
            [status], None)

    logger.debug("Status validation passed: " + status)

except MXApplicationException:
    raise
except Exception as e:
    logger.error("Error validating WO status: " + str(e))
    raise
```

---

## Pattern 2: MboSet Safety (Try/Finally)

Always use `try/finally` when working with MboSets to prevent memory leaks:

```python
vendor_set = mbo.getMboSet("VENDOR")
try:
    vendor = vendor_set.getMbo(0)
    if vendor is None:
        raise MXApplicationException("po", "vendornotfound",
            [mbo.getString("VENDOR")], None)
    # process vendor...
except MXApplicationException:
    raise
except Exception as e:
    logger.error("Error reading vendor: " + str(e))
    raise
finally:
    vendor_set.close()  # ALWAYS runs — even if exception thrown
```

---

## Pattern 3: Conditional Validation (Skip on Certain Conditions)

```python
try:
    # Only validate on new records
    if not mbo.isNew():
        return  # Exit early — skip validation

    # Only validate if field has a value
    vendor = mbo.getString("VENDOR")
    if not vendor:
        return  # Nothing to validate

    # Run validation
    if len(vendor) > 10:
        raise MXApplicationException("po", "vendortoolong", None, None)

except MXApplicationException:
    raise
except Exception as e:
    logger.error("Error in conditional validation: " + str(e))
    raise
```

---

## Pattern 4: Wrapping Java Exceptions

When calling Java APIs that throw Java exceptions:

```python
try:
    # Java API call that might throw
    result = some_java_api.call()

except Exception as e:
    error_msg = str(e)
    logger.error("Java API error: " + error_msg)
    # Wrap in MXApplicationException for user-friendly message
    raise MXApplicationException("mbo", "internalerror",
        [error_msg], None)
```

---

## Pattern 5: Nested MboSet Error Handling

When working with multiple nested MboSets:

```python
outer_set = mbo.getMboSet("POLINE")
try:
    i = 0
    while i < outer_set.count():
        line = outer_set.getMbo(i)
        inner_set = line.getMboSet("RECEIPT")
        try:
            # process inner_set
            pass
        except MXApplicationException:
            raise
        except Exception as e:
            logger.error("Error processing line " + str(i) + ": " + str(e))
            raise
        finally:
            inner_set.close()  # Inner close always runs
        i += 1

except MXApplicationException:
    raise
except Exception as e:
    logger.error("Error in PO line processing: " + str(e))
    raise
finally:
    outer_set.close()  # Outer close always runs
```

---

## Pattern 6: Cron Task Error Handling

Cron tasks need to handle errors without stopping the entire job:

```python
logger.info("Cron task starting")
error_count = 0
success_count = 0

record_set = mx_server.getMboSet("WORKORDER", user_info, "status = 'WAPPR'")
try:
    i = 0
    while i < record_set.count():
        record = record_set.getMbo(i)
        try:
            # Process each record
            process_record(record)
            success_count += 1
        except Exception as e:
            # Log but continue — don't stop the whole cron
            logger.error("Failed to process WO " +
                record.getString("WONUM") + ": " + str(e))
            error_count += 1
        i += 1
finally:
    record_set.close()

logger.info("Cron complete: " + str(success_count) +
    " succeeded, " + str(error_count) + " failed")
```

---

## Common Error Messages Reference

### Standard Error Keys

| Bundle | Key | When to Use |
|--------|-----|------------|
| `"mbo"` | `"requiredfields"` | Required field is empty |
| `"mbo"` | `"invalidvalue"` | Field value is not in allowed list |
| `"po"` | `"vendorrequired"` | PO vendor is missing |
| `"po"` | `"invalidvendor"` | Vendor does not exist |
| `"invoice"` | `"daterequired"` | Invoice date is missing |
| `"workorder"` | `"approverrequired"` | Approver is required |

**Tip:** Use existing bundle keys where possible. Only define new keys for custom messages.

---

## What NOT to Do

```python
# ❌ Silent catch — hides bugs
try:
    validate_vendor()
except:
    pass

# ❌ Catching MXApplicationException and not re-raising
try:
    raise MXApplicationException("po", "error", None, None)
except MXApplicationException:
    logger.error("Got error")  # Lost the user-facing message!

# ❌ Generic error message with no context
except Exception as e:
    raise MXApplicationException("mbo", "error", None, None)

# ❌ No finally on MboSet
vendor_set = mbo.getMboSet("VENDOR")
vendor = vendor_set.getMbo(0)  # If this throws, set never closes!
```

---

## Quick Checklist

Before deploying any script, verify:

- [ ] Every `getMboSet()` call has a `try/finally` with `.close()`
- [ ] `MXApplicationException` is always re-raised unchanged
- [ ] All `except Exception` blocks log `str(e)` before re-raising
- [ ] Logger name includes the script name: `"maximo.script.[name]"`
- [ ] INFO logged for significant business events
- [ ] No silent `except: pass` blocks anywhere

---

**Last Updated**: March 20, 2026
**See Also**: `SCRIPT_PATTERNS.md`, `LAUNCH_POINTS.md`, `NAMING_CONVENTIONS.md`
