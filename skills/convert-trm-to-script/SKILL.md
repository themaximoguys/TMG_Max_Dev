---
name: convert-trm-to-script
description: "Use when converting IBM Maximo TRM rules, XML definitions, JavaScript, or SCL logic into MAS 9 Jython automation scripts. Applies TRM event-to-launch-point mapping, TMG naming rules, script consolidation, and Maximo-safe replacements for unsupported UI-only behaviors."
---

# Convert TRM To Script

Convert a TRM rule or XML-based business rule into a Maximo automation script that matches TMG standards.

## Use This Skill For

- TRM rule migration
- XML event handler conversion
- TRM JavaScript or SCL logic migration
- Modernizing legacy TRM customizations for MAS 9

## Read First

1. `docs/standards/TMG_AUTOSCRIPT_STANDARDS.md`
2. `docs/autoscript/TRM_TO_PYTHON.md`
3. `AGENTS.md`
4. Existing converted examples under `catalog/samples/trm_converted/`

## Required Inputs

- TRM rule name or identifier
- TRM XML or rule logic summary
- Target object and attribute if known
- Original event type
- Any referenced tables, relationships, or helper logic

## Workflow

1. Identify the TRM event.
   Map the rule to the correct Maximo launch point such as object `init`, object `save.before`, attribute `validate`, attribute `action`, or workflow/action equivalents.

2. Determine the script owner.
   Reuse any existing script that already owns the same MBO and event.

3. Convert conditions and actions.
   Translate TRM conditions into explicit Jython branching and convert actions into Maximo API calls.

4. Replace TRM-specific helpers.
   Convert JavaScript and SCL constructs into supported Maximo Jython patterns.

5. Resolve unsupported UI behaviors.
   If a TRM rule relies on direct visibility manipulation or other UI-only behaviors, use the nearest supported script alternative and document the limitation briefly.

6. Preserve source traceability.
   Record the TRM source rule in the script header.

## Guardrails

- Write Jython 2.7 syntax only.
- Do not build SQL with string concatenation.
- Always close `MboSet` resources.
- Keep `INIT` logic read-only.
- Use field-level validation patterns when the rule is attribute-scoped.
- Do not silently drop unsupported TRM behavior without documenting the replacement approach.

## Event Mapping Reminders

- `onInit` -> object `init`
- `onNew` -> object `add`
- `beforeSave` -> object `save.before`
- `afterSave` -> object `save.after`
- `afterCommit` -> object `save.aftercommit`
- `onValidate` -> attribute `validate`
- `onChange` -> attribute `action`
- `initValue` -> attribute `init`
- `listValuesProvider` -> attribute `listfilter`
- `customAction` -> action script

## Expected Output

Produce:

- A standards-compliant Jython automation script
- Correct launch point and filename selection
- Header traceability back to the TRM rule
- A valid `scriptConfig` block

## Validation Checklist

- Confirm TRM event mapping is correct.
- Confirm the generated script type matches the rule scope.
- Confirm no duplicate event-owner script was introduced.
- Confirm unsupported TRM-only behaviors were handled explicitly.
- Confirm the script follows repository naming, header, logging, and cleanup rules.
