---
name: convert-java-to-script
description: "Use when converting IBM Maximo Java customization classes or methods into MAS 9 Jython automation scripts. Applies TMG launch point selection, Jython 2.7 constraints, Java-to-Maximo API mappings, script consolidation rules, and required source-traceable headers."
---

# Convert Java To Script

Convert a Java customization into a Maximo automation script that matches TMG standards.

## Use This Skill For

- Converting MBO or listener classes to object scripts
- Converting validation logic to field validators
- Converting Java business rules into workflow or cron scripts
- Replacing legacy Java customizations with automation scripts for MAS 9

## Read First

1. `docs/standards/TMG_AUTOSCRIPT_STANDARDS.md`
2. `docs/autoscript/JAVA_TO_PYTHON.md`
3. `AGENTS.md`
4. Existing scripts for the same object or business area

## Required Inputs

- Source Java class or relevant method bodies
- Source class name and method name
- Target object and event if already known
- Any related Java dependencies or helper classes
- Any known deployment or launch point constraints

## Workflow

1. Identify the source behavior.
   Determine whether the Java logic belongs in an object, attribute, action, cron, or integration script.

2. Map lifecycle to launch point.
   Translate Java lifecycle methods such as init, save, validate, delete, or custom handlers into the correct Maximo launch point and event.

3. Check for consolidation.
   If the target MBO and event already have a script, merge the new logic into that existing file rather than creating a duplicate event owner.

4. Replace Java implementation patterns.
   Convert inheritance, method overrides, loops, exception handling, related record access, and constants into Jython equivalents that work inside Maximo scripts.

5. Remove unsupported or obsolete APIs.
   Replace `sun.misc.*`, `javax.xml.bind.*`, manual commits, reflection hacks, and threading patterns with MAS 9 compatible alternatives.

6. Add source traceability.
   Record the Java source artifact in the header so the conversion remains auditable.

## Guardrails

- Write Jython 2.7 syntax only.
- Do not carry Java class structure into the final script.
- Use `SqlFormat` for query filtering.
- Always close related `MboSet` objects.
- Preserve business exceptions with `MXApplicationException` or `service.error()` patterns.
- Use Maximo implicit variables instead of inventing wrapper objects.

## Core Mapping Rules

- Java `init()` typically maps to object `init`, but `INIT` must remain read-only.
- Java pre-save validation usually maps to object `save.before` or attribute `validate`.
- Java loops over `MboSet` convert to indexed Jython loops.
- Java helper methods should become local helper functions inside the script when needed.
- Java logger usage should become either `MXLoggerFactory` or `service` logging, not both.

## Expected Output

Produce:

- A standards-compliant Jython script
- A header that names the converted Java source
- Correct launch point metadata in `scriptConfig`
- Minimal conversion notes only when needed to explain a non-obvious mapping

## Validation Checklist

- Confirm source lifecycle mapping is correct.
- Confirm no unsupported Java APIs remain.
- Confirm any existing script for the same MBO and event was reused or updated.
- Confirm all queries use safe filtering.
- Confirm the script remains Jython 2.7 compatible.
- Confirm header and `scriptConfig` capture the source conversion context.
