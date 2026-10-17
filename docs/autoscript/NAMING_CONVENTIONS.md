# Naming Conventions - IBM Maximo Automation Scripts

Complete naming standards for all automation script types in IBM Maximo.

---

## Standard Format

```
[objectname].[launchpointtype].[event].[optional].py
```

### Components Explained

**1. Object Name** (lowercase, no spaces)
- Single object name: `company`, `po`, `invoice`, `workorder`
- With modules: `tmg_invoice`, `tmg_ts`, `po_line`
- Use underscores for multi-word: `work_order` (less common than `workorder`)

**2. Launch Point Type** (mandatory)
- `fld` = Attribute/Field Launch Point (formerly "field")
- `obj` = Object Launch Point
- `action` = Action Launch Point
- `cron` = Cron Task Script
- Omit for workflow actions (use `action.workflowname`)

**3. Event** (mandatory)
- Object events: `init`, `save`, `add`, `delete`, `validate`, `candelete`, `duplicate`, `appvalidate`, `getorgforgl`
- Field events: `validate`, `valid`, `action`, `init`, `initvalue`, `list`, `listfilter`, `modify`, `readonly`
- Cron: `action`
- Workflow: workflow trigger name

**4. Optional Modifier** (timing or clarification)
- Timing: `before`, `after`, `aftercommit`
- Field name: `vendor`, `status`, `itemnum`
- Process name: `wfpofrompr`, `wfapproval`

---

## Examples by Category

### Field Validators (Attribute Launch Points)

**Format:** `objectname.fieldname.event.py`

#### Simple Field Validation
```
company.status.validate.py              # Validate company status field
po.vendor.validate.py                   # Validate PO vendor field
invoice.amount.validate.py              # Validate invoice amount
```

#### Field Action (onChange)
```
po.vendor.action.py                     # Update related fields when vendor changes
inventory.location.action.py            # Perform actions when location changes
contract.startdate.action.py            # Actions when start date changes
```

#### Field Initialization
```
workorder.priority.init.py              # Initialize work order priority
asset.status.initvalue.py               # Initialize asset status value
inventory.onhand.init.py                # Initialize on-hand quantity
```

#### List Filtering
```
company.type.listfilter.py              # Filter company type lookup values
po.vendor.listfilter.py                 # Filter vendor list to active vendors
location.type.list.py                   # Filter location types
```

#### Full Naming Examples
```
company.disabled.validate.py
po.vendor.action.py
workorder.priority.init.py
asset.assettype.listfilter.py
laborcraftrate.commoditygroup.readonly.py
```

### Object Scripts (Object Launch Points)

**Format:** `objectname.obj.event.py` or `objectname.obj.event.timing.py`

#### Object Initialization
```
po.obj.init.py                          # Initialize new PO record
invoice.obj.init.py                     # Initialize invoice
workorder.obj.init.py                   # Initialize work order
```

#### Object Save (Before/After)
```
po.obj.save.py                          # Save event processing
invoice.obj.save.before.py              # Before save validation
contract.obj.save.after.py              # After save processing
```

#### Specific Save Timing
```
po.obj.save.before.py                   # Pre-save validation
invoice.obj.save.after.py               # Post-save operations
workorder.obj.save.aftercommit.py       # After database commit
```

#### Object Creation
```
po.obj.add.py                           # When adding new document
invoice.obj.new.py                      # When creating new invoice
asset.obj.add.py                        # When adding new asset
```

#### Object Deletion
```
po.obj.delete.py                        # When deleting PO
invoice.obj.candelete.py                # Check if invoice can be deleted
contract.obj.candelete.py               # Check deletion eligibility
```

#### Complex Operations
```
invoice.obj.appvalidate.py              # Application validation
po.obj.duplicate.py                     # Handle record duplication
asset.obj.getorgforgl.py                # Determine GL organization
```

### Cron Tasks (Scheduled Scripts)

**Format:** `taskname.cron.action.py`

```
tmg_pmwogen.cron.action.py               # Generate PM work orders
tmg_datapurge.cron.action.py             # Archive/purge old data
tmg_addcimusers.cron.action.py           # Add CIM production users
tmg_geninv.cron.action.py                # Generate inventory reports
tmg_poclose.cron.action.py               # Close purchase orders
tmg_compinactive.cron.action.py          # Handle inactive companies
tmg_sttupdate.cron.action.py             # Update statements
tmg_valclrts.cron.action.py              # Validate CLR timesheets
tmg_measurepointwogen.cron.action.py     # Generate measurement points
```

### Workflow Actions

**Format:** `source.action.target.py` or `source.action.workflowname.py`

```
pr.action.wfpofrompr.py                 # Create PO from PR in workflow
invoice.action.wfapproval.py            # Workflow approval action
ticket.action.wfescalation.py           # Workflow escalation action
```

### Integration Scripts

**Format:** `parent.integration.subtype.py` or `integration.type.name.py`

```
mxwointerface.integration.exitexit.py   # Work order interface exit
mxasset.userexit.out.before.py          # Asset user exit before
tmg_invoice.publish.channel.py           # Invoice publish channel
```

---

## Naming Rules & Standards

### Must Follow (Non-Negotiable)

1. **All lowercase** - Never use uppercase
2. **No spaces** - Use underscores between words
3. **No special characters** - Only alphanumeric and underscore
4. **Object name first** - Always start with object
5. **File extension** - Always `.py`
6. **Dot notation** - Separate components with dots

### Best Practices (Strongly Recommended)

1. **Consistency** - Be consistent across all scripts
2. **Clarity** - Name should indicate what script does
3. **Launch point match** - Name must match launch point type
4. **Event match** - Event name must match configured event
5. **No duplication** - Don't repeat object name in event
6. **Field names** - Use actual field names for field scripts

### Avoid (Anti-Patterns)

```
❌ BAD NAMES:
Company_Status_Validate.py              (uppercase)
company script validate.py              (spaces)
company.validate.py                     (missing launchpointtype)
script_for_company_status.py            (unclear naming)
companystatusvalidate.py                (no separators)
company.fld.status.validate.v2.py       (version numbering)
```

```
✅ GOOD NAMES:
company.status.validate.py
company.fld.status.validate.py          (explicit launch point)
company.status.validate.before.py       (if needed for clarity)
company.status.validate.inactive.py     (specific variant)
```

---

## Quick Reference Tables

### Object Launch Point Events

| Event | Type | Purpose | Example |
|-------|------|---------|---------|
| `init` | Event | Initialize record on load | `po.obj.init.py` |
| `save` | Event | Triggered on save attempt | `invoice.obj.save.py` |
| `add` | Event | Add new record to set | `workorder.obj.add.py` |
| `delete` | Event | Delete record | `contract.obj.delete.py` |
| `candelete` | Event | Check if deletion allowed | `invoice.obj.candelete.py` |
| `validate` | Event | Validate record | `po.obj.validate.py` |
| `duplicate` | Event | Handle duplication | `asset.obj.duplicate.py` |
| `appvalidate` | Event | Application validation | `invoice.obj.appvalidate.py` |

### Attribute Launch Point Events

| Event | Type | Purpose | Example |
|-------|------|---------|---------|
| `validate` | Event | Validate field value | `po.vendor.validate.py` |
| `valid` | Alias | Same as validate | `po.vendor.valid.py` |
| `action` | Event | Field change action | `po.vendor.action.py` |
| `init` | Event | Initialize field | `workorder.priority.init.py` |
| `initvalue` | Event | Set initial value | `invoice.amount.initvalue.py` |
| `listfilter` | Event | Filter lookup list | `po.vendor.listfilter.py` |
| `list` | Alias | Same as listfilter | `po.vendor.list.py` |
| `readonly` | Flag | Make field readonly | `contract.status.readonly.py` |
| `modify` | Event | Intercept modifications | `inventory.onhand.modify.py` |

### Timing Modifiers for Save Events

| Timing | Purpose | Example |
|--------|---------|---------|
| `save` | Generic save | `invoice.obj.save.py` |
| `save.before` | Before database save | `invoice.obj.save.before.py` |
| `save.after` | After database save | `invoice.obj.save.after.py` |
| `save.aftercommit` | After commit (no rollback) | `invoice.obj.save.aftercommit.py` |

---

## Naming by Module/Domain

### Company & GL Accounting
```
company.disabled.validate.py
company.type.listfilter.py
glaccount.glacct.validate.py
```

### Inventory & Warehousing
```
inventory.itemnum.validate.py
invbalances.quantity.action.py
storeroom.location.init.py
```

### Purchase Orders
```
po.vendor.validate.py
po.vendor.action.py
poline.linetype.listfilter.py
poterm.terms.validate.py
```

### Sales & Service
```
invoice.vendor.validate.py
invoice.obj.save.py
asset.assettype.listfilter.py
```

### Work Management
```
workorder.obj.init.py
workorder.priority.action.py
laborcraftrate.obj.save.py
```

### Service Outage Management
```
tmg_outage.status.validate.py
tmg_outage.obj.save.py
```

### Timesheet & Labor
```
tmg_ts.obj.save.aftercommit.py
labortrans.costcode.validate.py
persongroup.person.listfilter.py
```

---

## Migration from Legacy Names

If migrating from old naming convention:

### Old Format
```
className_eventType.py
CustomPOValidator_onValidate.py
InvoiceCalc_onSave.py
```

### New Format
```
po.vendor.validate.py
invoice.obj.save.py
```

### Mapping Guide
- Remove class name prefix
- Use object name from class
- Replace camelCase with lowercase
- Use standard event names
- Include launch point type

---

## Frequently Asked Questions

**Q: Can I use object aliases (like MXWO for WORKORDER)?**
A: No, always use full object name: `workorder.obj.save.py` not `mxwo.obj.save.py`

**Q: What if field name has multiple words?**
A: Use underscore: `purchase_order.vendor_status.validate.py`

**Q: Should I include version numbers?**
A: No, use git for version control, not filename

**Q: Can I create nested subdirectories?**
A: No, keep flat structure under script type. Organize by module in documentation only.

**Q: What about custom objects?**
A: Use same naming: `custom_object.custom_field.validate.py`

**Q: Can I use abbreviations? (PO instead of purchaseorder)**
A: Use common abbreviations consistently: `po`, `mr`, `wo`, `po_line` are standard

---

## Validation Checklist

Before naming your script, verify:

- [ ] Object name is lowercase with underscores
- [ ] Launch point type is correct (fld, obj, action, cron)
- [ ] Event name matches actual event being handled
- [ ] No uppercase letters anywhere
- [ ] No spaces in filename
- [ ] File ends with `.py`
- [ ] Name is unique (no duplicates)
- [ ] Name accurately reflects purpose
- [ ] Follows the standard format pattern
- [ ] Timing modifier (before/after) is only if needed

---

## Related Documentation

- **Script Patterns**: `/docs/patterns/SCRIPT_PATTERNS.md`
- **Creating Scripts**: `/.github/skills/create-automation-script/SKILL.md`
- **Production Examples**: `/automation-scripts/`
- **Launch Points**: `/docs/patterns/LAUNCH_POINTS.md`
