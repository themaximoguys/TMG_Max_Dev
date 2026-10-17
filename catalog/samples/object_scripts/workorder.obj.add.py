# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_WORKORDER_OBJ_ADD
# Launch Point Name: TMG_WORKORDER_OBJ_ADD
# Launch Point Type: OBJECT
# Object: WORKORDER
# Event: ADD
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Initialize default values on a newly created WORKORDER. ADD fires when a
# new MBO is added to the set — this is the correct place for default
# values (NOT INIT). setValue() is permitted here.
#
# Demonstrates:
#   - OBJECT ADD pattern
#   - Reading user info via mbo.getUserInfo()
#   - Setting defaults with NOACCESSCHECK
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import MboConstants
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_workorder_obj_add")


# =============================================================================
# Main
# =============================================================================
def initialize_defaults():
    if mbo is None:                                          # noqa: F821
        return

    user_info = mbo.getUserInfo()                            # noqa: F821
    user_id = user_info.getUserName() if user_info is not None else ""

    # Default reportedby = current user when blank
    if mbo.isNull("REPORTEDBY") and user_id:                 # noqa: F821
        mbo.setValue("REPORTEDBY", user_id, MboConstants.NOACCESSCHECK)   # noqa: F821

    # Default WOPRIORITY = 3 when blank (1=highest, 5=lowest)
    if mbo.isNull("WOPRIORITY"):                             # noqa: F821
        mbo.setValue("WOPRIORITY", 3, MboConstants.NOACCESSCHECK)         # noqa: F821

    # Default WORKTYPE = "CM" (corrective maintenance) when blank
    if mbo.isNull("WORKTYPE"):                               # noqa: F821
        mbo.setValue("WORKTYPE", "CM", MboConstants.NOACCESSCHECK)        # noqa: F821

    _LOGGER.debug("Initialized defaults on new WORKORDER for user %s" % user_id)


initialize_defaults()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_WORKORDER_OBJ_ADD",
    "description": "Set default values on new WORKORDER (REPORTEDBY, WOPRIORITY, WORKTYPE).",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_WORKORDER_OBJ_ADD",
        "launchPointType": "OBJECT",
        "active": True,
        "objectName": "WORKORDER",
        "events": {"add": True},
        "description": "Initialize default values on new WORKORDER."
    }]
}
