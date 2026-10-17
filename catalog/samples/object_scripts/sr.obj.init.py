# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_SR_OBJ_INIT
# Launch Point Name: TMG_SR_OBJ_INIT
# Launch Point Type: OBJECT
# Object: SR
# Event: INIT
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Object-level INIT for Service Request. Toggles UI flags based on whether
# the SR was reported by an internal employee versus an external customer.
# INIT is read-only setup — no setValue() permitted.
#
# Demonstrates:
#   - OBJECT INIT pattern using `service.log` style logging
#   - Lookup against PERSON to detect employee vs external
#   - setFieldFlag for conditional required fields
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import MboConstants


# =============================================================================
# Helpers
# =============================================================================
def _is_employee(person_id):
    if person_id is None or len(person_id.strip()) == 0:
        return False
    person_set = None
    try:
        person_set = mbo.getMboSet("$tmg_person_lookup",     # noqa: F821
                                   "PERSON",
                                   "personid = :1")
        person_set.setQbe("PERSONID", person_id)
        person = person_set.getMbo(0)
        if person is None or person.isNull("EMPLOYEETYPE"):
            return False
        return person.getString("EMPLOYEETYPE") == "EMPLOYEE"
    finally:
        if person_set is not None:
            try:
                person_set.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def init_sr():
    if mbo is None:                                          # noqa: F821
        return

    person_id = ""
    if not mbo.isNull("REPORTEDBY"):                         # noqa: F821
        person_id = mbo.getString("REPORTEDBY")              # noqa: F821

    if _is_employee(person_id):
        # Employees auto-supply contact info; external customers must enter it
        mbo.setFieldFlag("AFFECTEDPHONE", MboConstants.REQUIRED, False)   # noqa: F821
        mbo.setFieldFlag("AFFECTEDEMAIL", MboConstants.REQUIRED, False)   # noqa: F821
    else:
        mbo.setFieldFlag("AFFECTEDPHONE", MboConstants.REQUIRED, True)    # noqa: F821
        mbo.setFieldFlag("AFFECTEDEMAIL", MboConstants.REQUIRED, True)    # noqa: F821

    try:
        service.log("TMG_SR_OBJ_INIT applied flags for SR REPORTEDBY=%s" % person_id)   # noqa: F821
    except Exception:
        pass


init_sr()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_SR_OBJ_INIT",
    "description": "Toggle SR contact-field requirements based on employee vs external reporter.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_SR_OBJ_INIT",
        "launchPointType": "OBJECT",
        "active": True,
        "objectName": "SR",
        "events": {"initialize": True},
        "description": "Apply flags to SR based on REPORTEDBY type."
    }]
}
