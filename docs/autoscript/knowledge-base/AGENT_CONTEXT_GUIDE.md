# Agent Context Guide - Maximo Automation Scripts

## Overview

This folder (`GENERAL`) serves as the **master context and reference library** for building IBM Maximo automation scripts and converting Java code to automation scripts. Use this guide when working with AI coding agents to ensure consistent, high-quality script development.

---

## Quick Start for AI Agents

**When working on Maximo automation scripts, always reference these files in priority order:**

1. **`AGENT_CONTEXT_GUIDE.md`** (this file) - Start here for context
2. **`NAMING_CONVENTIONS.md`** - Always follow naming standards
3. **`script_header_template.py`** - Always include standard header
4. **`maximo_script_patterns_reference.md`** - Use patterns from this reference
5. **`maximo_utility_library.py`** - Reuse functions from utility library
6. **`OFFICIAL_DOCUMENTATION.md`** - Refer to official IBM patterns

---

## Purpose of This Folder

This folder contains:
- **Standard naming conventions** for all automation scripts
- **Reusable code patterns** based on IBM best practices
- **Utility functions** for common operations
- **Official IBM documentation** (local copy for offline reference)
- **Best practices** and guidelines
- **Templates** for consistent script structure

**Use these resources to:**
- Build new automation scripts from scratch
- Convert existing Java code to automation scripts
- Maintain consistency across all scripts
- Ensure best practices are followed
- Reuse proven patterns and functions

---

## File Structure and Usage

### 1. Core Reference Files

#### `AGENT_CONTEXT_GUIDE.md` (This File)
**Purpose**: Master guide for AI agents working on Maximo automation scripts
**When to Use**: Always start here when beginning a new script or conversion task

#### `NAMING_CONVENTIONS.md`
**Purpose**: Complete naming standards for all automation scripts
**When to Use**: 
- Creating new scripts (must follow naming conventions)
- Renaming existing scripts
- Converting Java class names to script names

**Key Rules**:
- Format: `[objectname].[launchpointtype].[event].[optional].py`
- Always lowercase with dots
- Use standard abbreviations: `obj`, `fld`, `wo`, `po`
- Include field names for attribute launch points

**Quick Reference**: See the "Quick Reference Section" in `NAMING_CONVENTIONS.md` for condensed version

#### `script_header_template.py`
**Purpose**: Standard script header template
**When to Use**: 
- Every new script must include this header
- Document launch point, object, author, revisions

**Requirements**:
- Always include standard header at top of script
- Document launch point type and name
- Include revision history
- Reference naming conventions

#### `maximo_script_patterns_reference.md`
**Purpose**: Comprehensive code patterns extracted from production scripts
**When to Use**:
- Need specific code patterns (error handling, relationships, loops, etc.)
- Converting Java code to Python patterns
- Looking for examples of common operations

**Contains**:
- Error handling patterns
- Relationship calling patterns
- MBO set operations
- Field value setting patterns
- Validation patterns
- Exception handling
- Logging patterns
- All using `MboConstants` (never numeric constants)

#### `maximo_utility_library.py`
**Purpose**: Reusable utility functions for common operations
**When to Use**:
- Need common functions (user/group checks, type conversions, validations)
- Don't duplicate code - import from utility library
- Extend utility library with new generic functions

**Key Functions**:
- User/Group operations
- Type conversions
- Validations
- Date/Time utilities
- MBO operations
- Error handling
- SQL utilities

**Documentation**: See `UTILITY_LIBRARY_README.md` for complete function reference

### 2. Documentation Files

#### `OFFICIAL_DOCUMENTATION.md`
**Purpose**: Local copy of IBM Maximo Automation Script documentation
**When to Use**:
- Need official IBM patterns and best practices
- Understanding implicit variables
- Understanding launch points and events
- Reference for official API usage

#### `REFERENCES.md`
**Purpose**: Links to official IBM documentation and quick reference tables
**When to Use**:
- Need links to official documentation
- Quick reference for implicit variables
- Launch point quick reference

#### `README.md`
**Purpose**: Overview of all files in GENERAL folder
**When to Use**:
- Understanding the structure of this folder
- Finding specific resources

---

## Workflow for AI Agents

### Building New Automation Scripts

1. **Read `AGENT_CONTEXT_GUIDE.md`** (this file) - Understand context
2. **Check `NAMING_CONVENTIONS.md`** - Determine correct script name
3. **Copy `script_header_template.py`** - Start with standard header
4. **Reference `maximo_script_patterns_reference.md`** - Use appropriate patterns
5. **Import from `maximo_utility_library.py`** - Use existing functions
6. **Follow best practices** from `OFFICIAL_DOCUMENTATION.md`

### Converting Java to Automation Scripts

1. **Analyze Java code**:
   - Identify launch point type (Object, Attribute, Action, etc.)
   - Identify object and field names
   - Identify events (save, init, validate, etc.)

2. **Determine script name**:
   - Use `NAMING_CONVENTIONS.md` to create proper name
   - Format: `[objectname].[launchpointtype].[event].[optional].py`

3. **Convert Java patterns**:
   - Use `maximo_script_patterns_reference.md` for equivalent Python patterns
   - Replace Java MBO operations with Python equivalents
   - Use `MboConstants` instead of numeric constants
   - Convert Java error handling to Python patterns

4. **Use utility functions**:
   - Check `maximo_utility_library.py` for existing functions
   - Don't duplicate code - import and reuse

5. **Add standard header**:
   - Use `script_header_template.py`
   - Document conversion from Java

6. **Follow best practices**:
   - Reference `OFFICIAL_DOCUMENTATION.md` for best practices
   - Ensure proper error handling
   - Use appropriate logging
   - Follow performance guidelines

---

## Critical Rules for All Scripts

### 1. Naming Conventions (MANDATORY)

**Always follow** `NAMING_CONVENTIONS.md`:
- Format: `[objectname].[launchpointtype].[event].[optional].py`
- Lowercase with dots only
- Include field names for attribute launch points
- Use standard abbreviations

**Examples**:
- Object Launch Point: `workorder.obj.save.before.py`
- Attribute Launch Point: `inventory.fld.binnum.init.py`
- Action Launch Point: `workorder.action.duplicate.py`

### 2. Standard Header (MANDATORY)

**Always include** header from `script_header_template.py`:
- Document launch point type and name
- Document object name
- Document author
- Include revision history
- Reference naming conventions

### 3. MboConstants (MANDATORY)

**Never use numeric constants**. Always use `MboConstants`:

```python
# ✅ CORRECT
from psdi.mbo import MboConstants
mbo.setValue("FIELD", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

# ❌ WRONG - Never use numeric constants like 2L, 11L
mbo.setValue("FIELD", value, 2L)
```

### 4. Error Handling (MANDATORY)

**Always use proper error handling**:

```python
# ✅ RECOMMENDED - Use service.error()
service.error('Field Name', 'error message')
service.error('Field Name', 'error message', ['param1', 'param2'])

# ❌ DEPRECATED - Don't use errorkey/errorgroup
errorkey = 'ErrorKey'
errorgroup = 'ErrorGroup'
```

### 5. Utility Functions (MANDATORY)

**Always check utility library first**:
- Don't duplicate code
- Import from `maximo_utility_library.py`
- Extend library with new generic functions

### 6. Best Practices (MANDATORY)

**Always follow** best practices from `OFFICIAL_DOCUMENTATION.md`:
- Choose appropriate launch points
- Avoid costly operations in List tab
- Close MBO sets properly
- Check logging before logging
- Store `count()` results in variables
- Use try-finally for cleanup

---

## Common Conversion Patterns

### Java to Python - MBO Operations

**Java**:
```java
mbo.setValue("FIELDNAME", value, 2L);
```

**Python** (Correct):
```python
from psdi.mbo import MboConstants
mbo.setValue("FIELDNAME", value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)
```

### Java to Python - Error Handling

**Java**:
```java
MXException mxException = new MXException("AUTOSCRIPT", "errorKey", params);
throw mxException;
```

**Python** (Correct):
```python
service.error('Field Name', 'error message')
# or
service.error('Field Name', 'error message', ['param1', 'param2'])
```

### Java to Python - MBO Set Operations

**Java**:
```java
MboSet mboSet = mbo.getMboSet("RELATIONSHIP");
for (int i = 0; i < mboSet.count(); i++) {
    Mbo mbo = mboSet.getMbo(i);
    // Process
}
```

**Python** (Correct):
```python
mboSet = mbo.getMboSet("RELATIONSHIP")
mboSet.reset()
cnt = mboSet.count()  # Store count to avoid multiple calls
for i in range(cnt):
    mbo = mboSet.getMbo(i)
    # Process
```

### Java to Python - Relationships

**Java**:
```java
MboSet mboSet = mbo.getMboSet("$TEMPREL", "OBJECTNAME", "WHERE_CLAUSE");
```

**Python** (Correct):
```python
mboSet = mbo.getMboSet("$TEMPREL", "OBJECTNAME", "WHERE_CLAUSE")
mboSet.reset()
```

---

## Quick Reference for Common Tasks

### Creating a New Object Launch Point Script

1. **Name**: `[objectname].obj.[event].[optional].py`
   - Example: `workorder.obj.save.before.py`

2. **Header**: Copy from `script_header_template.py`

3. **Imports**: 
   ```python
   from psdi.mbo import MboConstants
   from psdi.server import MXServer
   ```

4. **Patterns**: Use patterns from `maximo_script_patterns_reference.md`

5. **Utility Functions**: Import from `maximo_utility_library.py`

### Creating a New Attribute Launch Point Script

1. **Name**: `[objectname].fld.[fieldname].[event].py`
   - Example: `inventory.fld.binnum.init.py`

2. **Header**: Copy from `script_header_template.py`

3. **Imports**: Same as Object Launch Point

4. **Patterns**: Use attribute-specific patterns from reference

5. **Field Name**: Must include field name in script name

### Converting Java Class to Script

1. **Identify Launch Point**: Determine type from Java code
2. **Name Script**: Use `NAMING_CONVENTIONS.md` to create name
3. **Convert Patterns**: Use `maximo_script_patterns_reference.md` for Python equivalents
4. **Replace Constants**: Replace numeric constants with `MboConstants`
5. **Add Header**: Include standard header with conversion notes

---

## File Priority Order for Context

When providing context to AI agents, use this priority order:

1. **`AGENT_CONTEXT_GUIDE.md`** (this file) - Master context
2. **`NAMING_CONVENTIONS.md`** - Naming standards (critical)
3. **`script_header_template.py`** - Header template (required)
4. **`maximo_script_patterns_reference.md`** - Code patterns (essential)
5. **`maximo_utility_library.py`** - Reusable functions (important)
6. **`OFFICIAL_DOCUMENTATION.md`** - Official patterns (reference)
7. **`UTILITY_LIBRARY_README.md`** - Function documentation (reference)
8. **`REFERENCES.md`** - Links and quick reference (supplementary)

---

## Agent Instructions

### For AI Agents Building New Scripts

1. **Always start with** `AGENT_CONTEXT_GUIDE.md` (this file)
2. **Check naming conventions** in `NAMING_CONVENTIONS.md`
3. **Use standard header** from `script_header_template.py`
4. **Reference patterns** from `maximo_script_patterns_reference.md`
5. **Import utility functions** from `maximo_utility_library.py`
6. **Follow best practices** from `OFFICIAL_DOCUMENTATION.md`

### For AI Agents Converting Java to Scripts

1. **Analyze Java code** to determine launch point type
2. **Create proper name** using `NAMING_CONVENTIONS.md`
3. **Convert Java patterns** using `maximo_script_patterns_reference.md`
4. **Replace numeric constants** with `MboConstants`
5. **Use utility functions** from `maximo_utility_library.py`
6. **Add standard header** with conversion notes

### For AI Agents Reviewing Scripts

1. **Verify naming** follows `NAMING_CONVENTIONS.md`
2. **Check header** matches `script_header_template.py`
3. **Verify no numeric constants** - only `MboConstants`
4. **Check error handling** uses `service.error()` not deprecated methods
5. **Verify utility functions** are used instead of duplicated code
6. **Check best practices** from `OFFICIAL_DOCUMENTATION.md`

---

## Context Injection for AI Agents

### System Prompt Addition

When working with Maximo automation scripts, use this context:

```
You are working with IBM Maximo automation scripts. Always reference the GENERAL folder context:

1. Naming Conventions: Follow NAMING_CONVENTIONS.md
2. Script Header: Always include header from script_header_template.py
3. Code Patterns: Use patterns from maximo_script_patterns_reference.md
4. Utility Functions: Import from maximo_utility_library.py
5. Best Practices: Follow OFFICIAL_DOCUMENTATION.md

CRITICAL RULES:
- Always use MboConstants, never numeric constants (2L, 11L, etc.)
- Always use service.error() not deprecated errorkey/errorgroup
- Always follow naming conventions
- Always include standard header
- Always check utility library before writing new functions
```

### File Context Priority

When providing file context, prioritize in this order:
1. `AGENT_CONTEXT_GUIDE.md` (this file)
2. `NAMING_CONVENTIONS.md`
3. `script_header_template.py`
4. Relevant sections from `maximo_script_patterns_reference.md`
5. Relevant functions from `maximo_utility_library.py`

---

## Maintenance and Updates

### Adding New Patterns

When adding new patterns:
1. Add to `maximo_script_patterns_reference.md`
2. Update examples and documentation
3. Ensure patterns use `MboConstants`

### Adding New Utility Functions

When adding new utility functions:
1. Add to `maximo_utility_library.py`
2. Document in `UTILITY_LIBRARY_README.md`
3. Follow existing function patterns
4. Make functions generic and reusable

### Updating Naming Conventions

When updating naming conventions:
1. Update `NAMING_CONVENTIONS.md` (including quick reference section)
2. Update examples throughout documentation

---

## Summary

This `GENERAL` folder is your **complete reference library** for:
- Building new Maximo automation scripts
- Converting Java code to automation scripts
- Maintaining consistency across all scripts
- Following best practices and standards
- Reusing proven patterns and functions

**Always reference these files when working on Maximo automation scripts.**

---

---

## Usage Instructions for AI Assistants

### For Cursor IDE
The `.cursorrules` file in the project root automatically provides context. The rules include:
- Critical rules and requirements
- File priority order
- Common patterns
- Workflow instructions

### For VSCode
- Use `.vscode/CONTEXT.md` in project root
- Use `.github/copilot-instructions.md` for GitHub Copilot
- Use `AI_CONTEXT.md` in project root for general AI assistants

### For Other AI Agents
1. **Include `AGENT_CONTEXT_GUIDE.md`** in your system prompt or context
2. **Reference specific files** based on task:
   - Naming: `NAMING_CONVENTIONS.md`
   - Patterns: `maximo_script_patterns_reference.md`
   - Functions: `maximo_utility_library.py`
   - Documentation: `OFFICIAL_DOCUMENTATION.md`

### For Manual Reference
1. **Start with**: `README.md` - Overview of all files
2. **Then reference**: Specific files based on your need
3. **Quick reference**: Use "Quick Reference Section" in `NAMING_CONVENTIONS.md`

---

## Context Injection Examples

### Example 1: Building New Script
```
Context: AGENT_CONTEXT_GUIDE.md, NAMING_CONVENTIONS.md, script_header_template.py, relevant patterns from maximo_script_patterns_reference.md

Task: Create a new Object Launch Point script for WORKORDER save before event
```

### Example 2: Converting Java
```
Context: AGENT_CONTEXT_GUIDE.md, NAMING_CONVENTIONS.md, maximo_script_patterns_reference.md, maximo_utility_library.py

Task: Convert Java class WorkOrderSaveBefore to automation script
```

### Example 3: Reviewing Script
```
Context: AGENT_CONTEXT_GUIDE.md, NAMING_CONVENTIONS.md, OFFICIAL_DOCUMENTATION.md (best practices section)

Task: Review script for compliance with standards and best practices
```

---

## Integration with Development Tools

### Cursor IDE
- `.cursorrules` file in project root automatically provides context
- AI suggestions follow GENERAL folder rules

### VSCode
- Include GENERAL folder in project context
- Reference `AGENT_CONTEXT_GUIDE.md` in AI assistant prompts

### CI/CD Pipelines
- Reference `NAMING_CONVENTIONS.md` for validation
- Use `script_header_template.py` for header validation
- Check for MboConstants usage (no numeric constants)

---

**Last Updated**: Based on IBM Maximo Automation Script documentation and best practices

**Status**: Production Ready - Generic and reusable across any Maximo project

