# Prompt Library

## Object Script Conversion Prompt

### Context
Use the prompt guidance from `docs\prompts\prompt_objectscripts_COMPACT.md` as the conversion methodology reference.

### Task
Convert the remaining or not completed Java files documented in `automation-scripts\object_scripts\OBJECT_INVENTORY.md` to Python automation scripts.

### Requirements

1. **Conversion Scope**: Convert at least the next 5 modules from the inventory
2. **Format Validation**: Validate each converted automation script to match the format of `automation-scripts\object_scripts\wpmaterial\wpmaterial.obj.add.py`
3. **Inventory Update**: Post-conversion, update the inventory file to reflect the completed modules and script counts

### Deliverables
- Python automation scripts following the wpmaterial.obj.add.py template
- Updated OBJECT_INVENTORY.md with new module entries
