# Agent Prompts - Maximo Automation Scripts

## Overview

This file provides structured prompts for coding agents to create different types of Maximo automation scripts. Each prompt includes clear instructions, required information, and examples for various script types.

**Purpose**: Standardized prompts for AI coding agents to build consistent, high-quality Maximo automation scripts  
**Usage**: Use these prompts as templates when requesting automation script creation  
**Version**: 1.0.0

---

## General Instructions for All Script Types

### Before Creating Any Script

1. **Gather Requirements**:
   - Object name (e.g., WORKORDER, ASSET, PO, INVENTORY)
   - Launch point type (Object, Attribute, Action, Cron, Integration)
   - Event type (save.before, validate, action, init, etc.)
   - Business logic requirements
   - Field names (for Attribute launch points)
   - Error messages (if applicable)

2. **Follow Standards**:
   - Use naming convention from `NAMING_CONVENTIONS.md`
   - Include standard header from `script_header_template.py`
   - Use `MboConstants` (never numeric constants)
   - Use `service.error()` for errors
   - Close MBO sets when done

3. **Reference Files**:
   - `AGENT_CONTEXT_GUIDE.md` - Complete workflow
   - `maximo_script_patterns_reference.md` - Code patterns
   - `maximo_utility_library.py` - Utility functions
   - `CLAUDE_CONTEXT.md` - Quick reference

---

## Prompt Templates

### 1. Object Launch Point - Save Before Script

**Prompt Template**:

```
Create a Maximo automation script for [OBJECT_NAME] object with the following requirements:

**Script Type**: Object Launch Point - Save Before
**Object**: [OBJECT_NAME]
**Event**: Save Before
**Business Logic**: [Describe what the script should do]

**Requirements**:
- Validate [condition/field] before saving
- Set [field] to [value] if [condition]
- Prevent save if [error condition]
- [Additional requirements]

**Error Messages**:
- [Error message 1]
- [Error message 2]

**Follow these standards**:
- Script name: [objectname].obj.save.before.py
- Include standard header template
- Use MboConstants (never numeric constants)
- Use service.error() for errors
- Close all MBO sets when done

**Reference**: 
- Naming: NAMING_CONVENTIONS.md
- Patterns: maximo_script_patterns_reference.md
- Utilities: maximo_utility_library.py
```

**Example**:

```
Create a Maximo automation script for WORKORDER object with the following requirements:

**Script Type**: Object Launch Point - Save Before
**Object**: WORKORDER
**Event**: Save Before
**Business Logic**: 
- Validate that work order status is valid before saving
- Auto-populate site ID if not provided
- Set reported date to current date if not provided
- Prevent save if work order type is missing

**Error Messages**:
- "Work order type is required"
- "Invalid work order status"

**Follow these standards**:
- Script name: workorder.obj.save.before.py
- Include standard header template
- Use MboConstants (never numeric constants)
- Use service.error() for errors
- Close all MBO sets when done
```

---

### 2. Object Launch Point - Save After Script

**Prompt Template**:

```
Create a Maximo automation script for [OBJECT_NAME] object with the following requirements:

**Script Type**: Object Launch Point - Save After
**Object**: [OBJECT_NAME]
**Event**: Save After
**Business Logic**: [Describe what the script should do after save]

**Requirements**:
- Create related records in [related_object]
- Update [field] in [related_object] based on [condition]
- Send notification/email if [condition]
- [Additional requirements]

**Follow these standards**:
- Script name: [objectname].obj.save.after.py
- Include standard header template
- Use MboConstants (never numeric constants)
- Close all MBO sets when done
```

**Example**:

```
Create a Maximo automation script for PO object with the following requirements:

**Script Type**: Object Launch Point - Save After
**Object**: PO
**Event**: Save After
**Business Logic**: 
- Create activity log entry when PO is saved
- Update related inventory records if PO is approved
- Send email notification to receiving manager if PO status is APPR

**Follow these standards**:
- Script name: po.obj.save.after.py
- Include standard header template
- Use MboConstants (never numeric constants)
- Close all MBO sets when done
```

---

### 3. Object Launch Point - Init Script

**Prompt Template**:

```
Create a Maximo automation script for [OBJECT_NAME] object with the following requirements:

**Script Type**: Object Launch Point - Init
**Object**: [OBJECT_NAME]
**Event**: Initialize
**Business Logic**: [Describe initialization logic]

**Requirements**:
- Set default values for [field1], [field2]
- Initialize [field] based on [condition]
- Set [field] to readonly if [condition]
- [Additional requirements]

**Follow these standards**:
- Script name: [objectname].obj.init.py
- Include standard header template
- Use MboConstants (never numeric constants)
- Use MboConstants.READONLY for readonly fields
```

**Example**:

```
Create a Maximo automation script for INVENTORY object with the following requirements:

**Script Type**: Object Launch Point - Init
**Object**: INVENTORY
**Event**: Initialize
**Business Logic**: 
- Set default site ID from user context
- Initialize bin number based on storeroom
- Set location field readonly if inventory is issued

**Follow these standards**:
- Script name: inventory.obj.init.py
- Include standard header template
- Use MboConstants (never numeric constants)
- Use MboConstants.READONLY for readonly fields
```

---

### 4. Attribute Launch Point - Validate Script

**Prompt Template**:

```
Create a Maximo automation script for [OBJECT_NAME] object with the following requirements:

**Script Type**: Attribute Launch Point - Validate
**Object**: [OBJECT_NAME]
**Field**: [FIELD_NAME]
**Event**: Validate
**Business Logic**: [Describe validation logic]

**Requirements**:
- Validate that [field] meets [condition]
- Check [field] against [related_object] for [validation]
- Prevent save if [field] is [invalid_value]
- [Additional requirements]

**Error Messages**:
- [Error message if validation fails]

**Follow these standards**:
- Script name: [objectname].fld.[fieldname].validate.py
- Include standard header template
- Use MboConstants (never numeric constants)
- Use service.error() for validation errors
```

**Example**:

```
Create a Maximo automation script for WORKORDER object with the following requirements:

**Script Type**: Attribute Launch Point - Validate
**Object**: WORKORDER
**Field**: STATUS
**Event**: Validate
**Business Logic**: 
- Validate that work order status transition is allowed
- Check if work order can be moved from current status to new status
- Prevent invalid status transitions

**Error Messages**:
- "Invalid status transition from {current_status} to {new_status}"

**Follow these standards**:
- Script name: workorder.fld.status.validate.py
- Include standard header template
- Use MboConstants (never numeric constants)
- Use service.error() for validation errors
```

---

### 5. Attribute Launch Point - Action Script

**Prompt Template**:

```
Create a Maximo automation script for [OBJECT_NAME] object with the following requirements:

**Script Type**: Attribute Launch Point - Action
**Object**: [OBJECT_NAME]
**Field**: [FIELD_NAME]
**Event**: Action (field change)
**Business Logic**: [Describe action logic]

**Requirements**:
- When [field] changes to [value], update [related_field]
- When [field] changes, populate [field] based on [condition]
- When [field] changes, clear [field] if [condition]
- [Additional requirements]

**Follow these standards**:
- Script name: [objectname].fld.[fieldname].action.py
- Include standard header template
- Use MboConstants (never numeric constants)
- Use MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION for programmatic updates
```

**Example**:

```
Create a Maximo automation script for INVENTORY object with the following requirements:

**Script Type**: Attribute Launch Point - Action
**Object**: INVENTORY
**Field**: STOREROOM
**Event**: Action (when storeroom changes)
**Business Logic**: 
- When storeroom changes, update default bin number
- Clear location field when storeroom changes
- Update related inventory balances

**Follow these standards**:
- Script name: inventory.fld.storeroom.action.py
- Include standard header template
- Use MboConstants (never numeric constants)
- Use MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION for programmatic updates
```

---

### 6. Attribute Launch Point - Init Script

**Prompt Template**:

```
Create a Maximo automation script for [OBJECT_NAME] object with the following requirements:

**Script Type**: Attribute Launch Point - Init
**Object**: [OBJECT_NAME]
**Field**: [FIELD_NAME]
**Event**: Initialize (default value)
**Business Logic**: [Describe initialization logic]

**Requirements**:
- Set default value for [field] based on [condition]
- Initialize [field] from [related_object].[related_field]
- Set [field] to [value] if [condition]
- [Additional requirements]

**Follow these standards**:
- Script name: [objectname].fld.[fieldname].init.py
- Include standard header template
- Use MboConstants (never numeric constants)
- Use MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION for programmatic updates
```

**Example**:

```
Create a Maximo automation script for INVENTORY object with the following requirements:

**Script Type**: Attribute Launch Point - Init
**Object**: INVENTORY
**Field**: BINNUM
**Event**: Initialize (default bin number)
**Business Logic**: 
- Set default bin number based on storeroom
- Initialize bin number from storeroom default bin
- Use first available bin if default not available

**Follow these standards**:
- Script name: inventory.fld.binnum.init.py
- Include standard header template
- Use MboConstants (never numeric constants)
- Use MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION for programmatic updates
```

---

### 7. Action Launch Point Script

**Prompt Template**:

```
Create a Maximo automation script for [OBJECT_NAME] object with the following requirements:

**Script Type**: Action Launch Point
**Object**: [OBJECT_NAME]
**Action**: [ACTION_NAME]
**Business Logic**: [Describe action logic]

**Requirements**:
- When [action] is executed, perform [operations]
- Create [related_object] records based on [condition]
- Update [field] in [related_object] if [condition]
- [Additional requirements]

**Follow these standards**:
- Script name: [objectname].action.[actionname].py
- Include standard header template
- Use MboConstants (never numeric constants)
- Close all MBO sets when done
```

**Example**:

```
Create a Maximo automation script for WORKORDER object with the following requirements:

**Script Type**: Action Launch Point
**Object**: WORKORDER
**Action**: DUPLICATE
**Business Logic**: 
- When duplicate action is executed, create copy of work order
- Copy all related records (activities, materials, etc.)
- Update work order number and status to new
- Clear completion dates and reset status

**Follow these standards**:
- Script name: workorder.action.duplicate.py
- Include standard header template
- Use MboConstants (never numeric constants)
- Close all MBO sets when done
```

---

### 8. Cron Task Script

**Prompt Template**:

```
Create a Maximo automation script for cron task with the following requirements:

**Script Type**: Cron Task Script
**Cron Task Name**: [CRON_TASK_NAME]
**Business Logic**: [Describe cron task logic]

**Requirements**:
- Run scheduled task to [perform operation]
- Process [object] records based on [condition]
- Update [field] in [object] if [condition]
- Send notifications/emails if [condition]
- [Additional requirements]

**Schedule**: [Describe when cron should run]

**Follow these standards**:
- Script name: cron.[description].py
- Include standard header template
- Use MboConstants (never numeric constants)
- Close all MBO sets when done
- Add proper logging for cron execution
```

**Example**:

```
Create a Maximo automation script for cron task with the following requirements:

**Script Type**: Cron Task Script
**Cron Task Name**: Update Asset Serial Numbers
**Business Logic**: 
- Run daily to update asset serial numbers from external system
- Process ASSET records that need serial number updates
- Update SERIALNUM field based on external data
- Log all updates for audit trail

**Schedule**: Run daily at 2:00 AM

**Follow these standards**:
- Script name: cron.rss.asset.update.serial.py
- Include standard header template
- Use MboConstants (never numeric constants)
- Close all MBO sets when done
- Add proper logging for cron execution
```

---

### 9. Integration Script - Publish Channel

**Prompt Template**:

```
Create a Maximo automation script for integration publish channel with the following requirements:

**Script Type**: Integration Script - Publish Channel
**Object**: [OBJECT_NAME]
**Publish Channel**: [CHANNEL_NAME]
**Business Logic**: [Describe integration logic]

**Requirements**:
- Transform [object] data before publishing
- Add/remove fields from publish payload
- Format data for external system
- [Additional requirements]

**Follow these standards**:
- Script name: publish.[description].extexit.out.py
- Include standard header template
- Use MboConstants (never numeric constants)
- Handle integration errors gracefully
```

**Example**:

```
Create a Maximo automation script for integration publish channel with the following requirements:

**Script Type**: Integration Script - Publish Channel
**Object**: WORKORDER
**Publish Channel**: WorkOrderPublish
**Business Logic**: 
- Transform work order data before publishing to external system
- Add calculated fields (total cost, estimated hours)
- Format dates for external system format
- Remove internal-only fields from payload

**Follow these standards**:
- Script name: publish.workorder.extexit.out.py
- Include standard header template
- Use MboConstants (never numeric constants)
- Handle integration errors gracefully
```

---

## Complete Prompt Checklist

### For Any Script Type

**Information to Gather**:
- [ ] Object name
- [ ] Launch point type
- [ ] Event type (if applicable)
- [ ] Field name (if Attribute launch point)
- [ ] Business logic requirements
- [ ] Error messages (if applicable)
- [ ] Related objects (if applicable)
- [ ] Conditions/validations
- [ ] Default values (if applicable)

**Standards to Follow**:
- [ ] Script naming convention
- [ ] Standard header template
- [ ] MboConstants usage (no numeric constants)
- [ ] service.error() for errors
- [ ] Close MBO sets when done
- [ ] Proper error handling
- [ ] Logging (for cron tasks)

**Files to Reference**:
- [ ] `NAMING_CONVENTIONS.md` - For naming
- [ ] `script_header_template.py` - For header
- [ ] `maximo_script_patterns_reference.md` - For patterns
- [ ] `maximo_utility_library.py` - For utilities
- [ ] `CLAUDE_CONTEXT.md` - For quick reference

---

## Quick Reference: Prompt Structure

### Standard Prompt Format

```
1. Script Type: [Type]
2. Object: [Object Name]
3. Event/Field: [Event or Field Name]
4. Business Logic: [Detailed description]
5. Requirements: [List of requirements]
6. Error Messages: [If applicable]
7. Standards: [Reference to standards]
8. References: [Files to reference]
```

### Example Prompt (Complete)

```
Create a Maximo automation script with the following requirements:

**Script Type**: Object Launch Point - Save Before
**Object**: WORKORDER
**Event**: Save Before
**Business Logic**: 
Validate work order before saving to ensure:
1. Work order type is required
2. Site ID is populated
3. Status transition is valid
4. Reported date is set if missing

**Requirements**:
- Validate work order type is not null
- Auto-populate site ID from user context if missing
- Validate status transition is allowed
- Set reported date to current date if not provided
- Prevent save with error if validation fails

**Error Messages**:
- "Work order type is required"
- "Invalid status transition from {current} to {new}"
- "Site ID is required"

**Conditions**:
- Only validate status transition if status is being changed
- Only set reported date if work order is new (onadd)
- Only auto-populate site ID if not already set

**Follow these standards**:
- Script name: workorder.obj.save.before.py
- Include standard header from script_header_template.py
- Use MboConstants (never numeric constants like 2L, 11L)
- Use service.error() for errors (not deprecated methods)
- Close all MBO sets when done
- Use utility functions from maximo_utility_library.py where applicable

**Reference Files**:
- Naming: NAMING_CONVENTIONS.md
- Patterns: maximo_script_patterns_reference.md
- Utilities: maximo_utility_library.py
- Context: CLAUDE_CONTEXT.md
```

---

## Prompt Variations by Use Case

### Simple Validation Script

```
Create a simple validation script for [OBJECT].[FIELD] that:
- Validates [condition]
- Returns error "[error message]" if validation fails
- Uses standard naming and header
```

### Complex Business Logic Script

```
Create a complex automation script for [OBJECT] that:
- Performs multiple validations
- Creates related records
- Updates related objects
- Sends notifications
- Includes proper error handling
- Uses utility functions where applicable
```

### Integration Script

```
Create an integration script for [OBJECT] that:
- Transforms data for external system
- Handles integration errors
- Logs all operations
- Follows integration best practices
```

---

## Best Practices for Using Prompts

### 1. Be Specific
- Provide detailed business logic requirements
- Include all conditions and validations
- Specify error messages exactly as needed

### 2. Reference Standards
- Always reference naming conventions
- Include header template requirement
- Mention MboConstants usage

### 3. Include Context
- Provide related object information
- Include field names and types
- Specify conditions and business rules

### 4. Request Best Practices
- Ask for proper error handling
- Request MBO set cleanup
- Include utility function usage

### 5. Provide Examples
- Include sample data if applicable
- Reference similar scripts if available
- Provide expected behavior examples

---

## Common Prompt Patterns

### Pattern 1: Validation Script
```
Create a validation script that validates [field] meets [condition] 
and returns error "[message]" if validation fails.
```

### Pattern 2: Auto-Populate Script
```
Create an auto-populate script that sets [field] to [value] 
based on [condition] when [event] occurs.
```

### Pattern 3: Related Record Script
```
Create a script that creates/updates [related_object] records 
when [object] is saved with [condition].
```

### Pattern 4: Status Change Script
```
Create a script that handles [object] status change from [status1] 
to [status2] by performing [operations].
```

### Pattern 5: Integration Script
```
Create an integration script that transforms [object] data 
for [external_system] by [transformation_logic].
```

---

## Prompt Template Library

### Template: Object Save Before
```
Create Object Launch Point - Save Before script for [OBJECT] 
that validates [conditions] and prevents save with errors 
if [error_conditions].
```

### Template: Object Save After
```
Create Object Launch Point - Save After script for [OBJECT] 
that creates/updates [related_objects] when [conditions].
```

### Template: Attribute Validate
```
Create Attribute Launch Point - Validate script for [OBJECT].[FIELD] 
that validates [condition] and returns error "[message]" if invalid.
```

### Template: Attribute Action
```
Create Attribute Launch Point - Action script for [OBJECT].[FIELD] 
that updates [fields] when field changes to [value].
```

### Template: Action Launch Point
```
Create Action Launch Point script for [OBJECT].[ACTION] 
that performs [operations] when action is executed.
```

### Template: Cron Task
```
Create Cron Task script that processes [object] records 
based on [condition] and performs [operations] [schedule].
```

---

## Summary

This prompt file provides:

✅ **Structured Templates** - Ready-to-use prompts for all script types  
✅ **Clear Instructions** - Step-by-step guidance for agents  
✅ **Standards Integration** - References to all required standards  
✅ **Examples** - Real-world examples for each script type  
✅ **Best Practices** - Guidelines for creating effective prompts  
✅ **Quick Reference** - Common patterns and templates  

**Usage**: Copy and customize these prompts when requesting automation script creation from coding agents.

---

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: Based on IBM Maximo Automation Script best practices

