# Maximo Automation Script Launch Point Configuration Guide

**Project:** TMGMaximo MAS 9 Field Validator Migration  
**Purpose:** Launch Point configuration instructions for converted field validators  
**Date:** November 13, 2025

---

## Overview

This document provides step-by-step instructions for configuring Maximo Automation Script Launch Points for the converted field validators.

### Prerequisites
- Maximo MAS 9 environment
- Administrative access to Automation Scripts application
- Automation scripts deployed to environment
- Logging configured for troubleshooting

---

## Launch Point Configuration Steps

### General Process

1. Navigate to **System Configuration > Platform Configuration > Automation Scripts**
2. Create new script or import from file
3. Configure Launch Point
4. Set Launch Point variables (if needed)
5. Activate script
6. Test functionality

---

## Validator 1: TMG_FldWOAssetnum

### Script Details
- **Script Name:** `TMG.WOASSETNUM.VALIDATE`
- **Script File:** `workorder.assetnum.validate.py`
- **Description:** Sets GLACCOUNT readonly when asset is selected

### Launch Point Configuration
1. **Launch Point Name:** `TMG_WOASSETNUM_VALIDATE`
2. **Launch Point Type:** Attribute Launch Point
3. **Object:** `WORKORDER`
4. **Attribute:** `ASSETNUM`
5. **Event:** Run Action / Validate
6. **Active:** ✓ Yes

### Variables
None required

### Testing
1. Open Work Order application
2. Select an asset in ASSETNUM field
3. Verify GLACCOUNT field becomes readonly
4. Try to edit GLACCOUNT - should be prevented

---

## Validator 2: TMG_FldWOPersonGroup

### Script Details
- **Script Name:** `TMG.WOPERSONGROUP.VALIDATE`
- **Script File:** `workorder.persongroup.validate.py`
- **Description:** Populates department and lead from person group

### Launch Point Configuration
1. **Launch Point Name:** `TMG_WOPERSONGROUP_VALIDATE`
2. **Launch Point Type:** Attribute Launch Point
3. **Object:** `WORKORDER`
4. **Attribute:** `PERSONGROUP`
5. **Event:** Run Action / Validate
6. **Active:** ✓ Yes

### Variables
None required

### Testing
1. Open Work Order application
2. Select a person group
3. Verify TMG_DEPARTMENT is populated (non-ORG1 org)
4. Verify LEAD is populated from SITEDEFAULT or GROUPDEFAULT
5. Change person group - verify LEAD updates if not in new team

---

## Validator 3: TMG_FldWOSchedstart

### Script Details
- **Script Name:** `TMG.WOSCHEDSTART.VALIDATE`
- **Script File:** `workorder.schedstart.validate.py`
- **Description:** Clears support acknowledgments on schedule change

### Launch Point Configuration
1. **Launch Point Name:** `TMG_WOSCHEDSTART_ACTION`
2. **Launch Point Type:** Attribute Launch Point
3. **Object:** `WORKORDER`
4. **Attribute:** `SCHEDSTART`
5. **Event:** Run Action / Validate
6. **Active:** ✓ Yes

### Variables
None required

### Testing
1. Open Work Order with status APPR or SCHED
2. Verify work order has support records with acknowledgments
3. Change SCHEDSTART date
4. Verify support acknowledgments are cleared (non-ORG1 org)
5. Verify TMG_SNCPOD flag is cleared

---

## Validator 4: TMG_FldWpLaborVendor

### Script Details
- **Script Name:** `TMG.WPLABORVENDOR.VALIDATE`
- **Script File:** `wplabor.vendor.validate.py`
- **Description:** Placeholder for labor vendor validation

### Launch Point Configuration
1. **Launch Point Name:** `TMG_WPLABORVENDOR_VALIDATE`
2. **Launch Point Type:** Attribute Launch Point
3. **Object:** `WPLABOR`
4. **Attribute:** `VENDOR`
5. **Event:** Run Action / Validate
6. **Active:** ✓ Yes (or No if no validation needed)

### Variables
None required

### Testing
- Standard vendor lookup should work
- No additional restrictions applied (original logic was removed)

---

## Validator 5: TMG_FldWpMatItemNum

### Script Details
- **Script Name:** `TMG.WPMATITEMNUM.VALIDATE`
- **Script File:** `wpmaterial.itemnum.validate.py`
- **Description:** Validates item is not PENDING or OBSOLETE

### Launch Point Configuration
1. **Launch Point Name:** `TMG_WPMATITEMNUM_VALIDATE`
2. **Launch Point Type:** Attribute Launch Point
3. **Object:** `WPMATERIAL`
4. **Attribute:** `ITEMNUM`
5. **Event:** Validate
6. **Active:** ✓ Yes

### Variables
None required

### Testing
1. Open Work Order and add work plan material
2. Try to select item with PENDING status - should show error
3. Try to select item with OBSOLETE status - should show error
4. Select item with ACTIVE status - should work

---

## Validator 6: TMG_FldWpMatVendor

### Script Details
- **Script Name:** `TMG.WPMATVENDOR.VALIDATE`
- **Script File:** `wpmaterial.vendor.validate.py`
- **Description:** Validates vendor is type SUPPLIER

### Launch Point Configuration
1. **Launch Point Name:** `TMG_WPMATVENDOR_VALIDATE`
2. **Launch Point Type:** Attribute Launch Point
3. **Object:** `WPMATERIAL`
4. **Attribute:** `VENDOR`
5. **Event:** Validate
6. **Active:** ✓ Yes

### Variables
None required

### Testing
1. Open Work Order and add work plan material
2. Try to select vendor with type COURIER - should show error "InvalidCompany"
3. Select vendor with type SUPPLIER - should work

---

## Validator 7: TMG_FldTestResults

### Script Details
- **Script Name:** `TMG.TESTRESULTS.ACTION`
- **Script File:** `tmg_functest.tmg_testresults.validate.py`
- **Description:** Auto-populates test report date and user

### Launch Point Configuration
1. **Launch Point Name:** `TMG_TESTRESULTS_ACTION`
2. **Launch Point Type:** Attribute Launch Point
3. **Object:** `TMG_FUNCTEST`
4. **Attribute:** `TMG_TESTRESULTS`
5. **Event:** Run Action / Validate
6. **Active:** ✓ Yes

### Variables
None required

### Testing
1. Open Work Order functional test section
2. Enter value in TMG_TESTRESULTS field
3. Verify TMG_TESTREPORTDATE is set to current date
4. Verify TMG_TESTREPORTEDBY is set to current user
5. Clear TMG_TESTRESULTS - verify both fields are cleared

---

## Validator 8: TMG_FldWpMatLineType

### Script Details
- **Script Name:** `TMG.WPMATLINETYPE.LISTFILTER`
- **Script File:** `wpmaterial.linetype.listfilter.py`
- **Description:** Filters MATERIAL line type for ORG1 org

### Launch Point Configuration
⚠️ **Special Note:** This validator attempts to override getList() which is not fully supported in automation scripts. **Alternative implementation recommended.**

**Option A: Application Designer Configuration**
1. Modify WPMATERIAL object's LINETYPE domain
2. Add organization-based filtering

**Option B: Validation Script**
1. **Launch Point Name:** `TMG_WPMATLINETYPE_VALIDATE`
2. **Launch Point Type:** Attribute Launch Point
3. **Object:** `WPMATERIAL`
4. **Attribute:** `LINETYPE`
5. **Event:** Validate
6. **Active:** ✓ Yes

### Variables
None required

### Testing
1. Open Work Order for ORG1 organization
2. Add work plan material
3. Select line type - MATERIAL should not appear (Option A) or show error (Option B)
4. Other line types should be available

---

## Validator 9: TMG_FldWpSerItemNum

### Script Details
- **Script Name:** `TMG.WPSERITEMNUM.LISTFILTER`
- **Script File:** `wpservice.itemnum.listfilter.py`
- **Description:** Filters items by status for service items

### Launch Point Configuration
⚠️ **Special Note:** Similar to Validator 8, getList() override limitation applies.

**Recommended: Validation Script**
1. **Launch Point Name:** `TMG_WPSERITEMNUM_VALIDATE`
2. **Launch Point Type:** Attribute Launch Point
3. **Object:** `WPSERVICE`
4. **Attribute:** `ITEMNUM`
5. **Event:** Validate
6. **Active:** ✓ Yes

### Variables
None required

### Testing
- Same as Validator 5 (item status validation)

---

## Validator 10: TMG_FldWpToolNum

### Script Details
- **Script Name:** `TMG.WPTOOLITEMNUM.LISTFILTER`
- **Script File:** `wptool.itemnum.listfilter.py`
- **Description:** Filters items by status for tool items

### Launch Point Configuration
⚠️ **Special Note:** Similar to Validators 8-9, getList() override limitation applies.

**Recommended: Validation Script**
1. **Launch Point Name:** `TMG_WPTOOLITEMNUM_VALIDATE`
2. **Launch Point Type:** Attribute Launch Point
3. **Object:** `WPTOOL`
4. **Attribute:** `ITEMNUM`
5. **Event:** Validate
6. **Active:** ✓ Yes

### Variables
None required

### Testing
- Same as Validator 5 (item status validation)

---

## Bulk Import Script

For bulk import of all launch points, use the following SQL or Maximo Migration Manager script:

```sql
-- Sample Launch Point Insert (adjust for your environment)
INSERT INTO AUTOSCRIPT (
    AUTOSCRIPTID, AUTOSCRIPT, DESCRIPTION, SCRIPTLANGUAGE, 
    LOGLEVEL, ACTIVE, USERDEFINED
) VALUES (
    AUTOSCRIPTIDSEQ.NEXTVAL, 'TMG.WOASSETNUM.VALIDATE', 
    'WO Asset Number Validator', 'jython', 
    'ERROR', 1, 1
);

-- Insert Launch Point
INSERT INTO SCRIPTLAUNCHPOINT (
    LAUNCHPOINTID, LAUNCHPOINTNAME, LAUNCHPOINTTYPE, 
    OBJECTNAME, ATTRIBUTENAME, AUTOSCRIPT, ACTIVE
) VALUES (
    LAUNCHPOINTIDSEQ.NEXTVAL, 'TMG_WOASSETNUM_VALIDATE', 
    'ATTRIBUTE', 'WORKORDER', 'ASSETNUM', 
    'TMG.WOASSETNUM.VALIDATE', 1
);
```

---

## Troubleshooting

### Common Issues

**1. Script doesn't execute**
- Check script is Active
- Verify Launch Point is Active
- Check object/attribute names are correct (case-sensitive)
- Review Maximo logs for errors

**2. Error: "mbo is not defined"**
- This is a lint error only - ignore in production
- `mbo` is provided by Maximo runtime

**3. Performance issues**
- Check for unnecessary database queries
- Ensure MboSets are closed properly
- Review logging level (use ERROR not DEBUG in production)

**4. Validation not triggering**
- Verify Event type is correct (Validate vs Run Action)
- Check for conflicting validators
- Review field initialization order

**5. getList() override not working**
- Use validation approach instead
- OR configure filtering in Application Designer
- See notes for Validators 8, 9, 10

### Logging

Enable debug logging for troubleshooting:

1. Navigate to **Automation Scripts**
2. Select script
3. Set **Log Level** to DEBUG
4. Reproduce issue
5. Check **System Logs** or application server logs
6. Set back to ERROR when done

### Testing Checklist

For each validator:
- [ ] Script created and saved
- [ ] Launch Point configured
- [ ] Launch Point activated
- [ ] Script activated
- [ ] Basic functionality tested
- [ ] Error handling tested
- [ ] Performance verified
- [ ] Logging reviewed
- [ ] Documentation updated

---

## Deployment Process

### Development Environment
1. Create and test scripts
2. Document test results
3. Export automation script package

### Test Environment
1. Import automation script package
2. Configure launch points
3. Run regression tests
4. Document any issues

### Production Environment
1. Schedule maintenance window
2. Backup current configuration
3. Import automation script package
4. Activate launch points incrementally
5. Monitor logs closely
6. Have rollback plan ready

---

## Support

### Resources
- Maximo Automation Scripting Guide
- IBM Documentation: Automation Scripts
- Knowledge Base: `maximo_script_patterns_reference.py`
- Project Documentation: `docs/FIELD_VALIDATORS.md`

### Contact
For issues or questions, contact:
- Technical Lead: [Name]
- Development Team: [Email]
- Project Manager: [Name]

---

**Document Version:** 1.0  
**Last Updated:** November 13, 2025  
**Next Review:** Post-deployment validation
