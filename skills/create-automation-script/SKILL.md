---
name: create-automation-script
description: "Use when creating a new IBM Maximo MAS 9 Jython automation script from business requirements, including field validators, object scripts, cron tasks, workflow actions, or integration exits. Applies TMG naming, headers, scriptConfig metadata, consolidation rules, logging patterns, and Maximo runtime constraints."
---

# Create Automation Script

Create a new Maximo MAS 9 automation script that matches TMG standards and existing repository patterns.

## Use This Skill For

- New field validators
- New object scripts
- New cron task scripts
- New workflow action scripts
- New integration scripts or exits
- Adding new logic to an existing object event script when consolidation is required

## Read First

1. `docs/standards/TMG_AUTOSCRIPT_STANDARDS.md`
2. `AGENTS.md`
3. Relevant examples under `catalog/samples/`

## Required Inputs

- Script type
- Target object name
- Target field name if the script is attribute-based
- Event and timing
- Business requirements
- Dependencies on related objects or integration artifacts
- Whether the logic belongs in an existing script for the same MBO and event

## Workflow

1. Identify the script family.
   Field validator, object script, cron task, workflow action, or integration exit.

2. Check for an existing owner script.
   If an object event script already exists for the same MBO and event, add the new rule to that file instead of creating a duplicate script.

3. Choose the canonical name.
   Follow `docs/standards/TMG_AUTOSCRIPT_STANDARDS.md` exactly for filename, autoscript, and launch point naming.

4. Select one logging style.
   Use either `MXLoggerFactory` or the implicit `service` variable for the entire script.

5. Implement Maximo-safe logic.
   Use implicit variables, null checks, `SqlFormat`, and `try/finally` cleanup for `MboSet` usage.

6. Finish with the required metadata.
   Add a correct `scriptConfig` block and the script-type-specific header.

## Guardrails

- Write Jython 2.7 compatible syntax only.
- Do not use f-strings.
- Do not use `print()` or `System.out`.
- Do not use `setValue()` in `INIT` handlers.
- Do not build SQL with string concatenation.
- Always close `MboSet` objects.
- Do not hardcode org or site values unless explicitly required and documented.
- Re-raise `MXApplicationException` directly.

## Naming Summary

- Field validator: `[object].fld.[field].[event].py` or existing compatible `[object].[field].[event].py`
- Object script: `[object].obj.[event].py`
- Cron task: `tmg_[name].cron.action.py`
- Workflow action: `[object].action.[actionname].py`
- Integration publish exit: `PUBLISH.[CHANNEL].[EXITTYPE].OUT.py`
- Integration sync exit: `SYNC.[SERVICE].[EXITTYPE].IN.py`

## Expected Output

Produce a script that includes:

- A correct header for the script type
- Minimal imports
- Business logic using Maximo runtime APIs
- Helper functions when multiple business rules are present
- `scriptConfig` metadata at the bottom

## Validation Checklist

- Confirm the target object and event are correct.
- Confirm the file does not duplicate an existing object event script.
- Confirm header format matches the script type.
- Confirm logging style is consistent.
- Confirm all `MboSet` resources are closed.
- Confirm `scriptConfig` values match filename and launch point naming.
- Confirm the implementation follows repository examples for the same module or object.
