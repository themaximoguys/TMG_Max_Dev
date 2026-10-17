# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_WORKORDER_OBJ_INIT
# Launch Point Name: TMG_WORKORDER_OBJ_INIT
# Launch Point Type: OBJECT
# Object: WORKORDER
# Event: INIT
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Object-level INIT handler for WORKORDER. Sets read-only / required UI flags
# based on the work-order type. INIT is read-only setup — setValue() must NOT
# be called here; use ADD or SAVE_BEFORE for value initialization.
#
# Demonstrates:
#   - OBJECT INIT pattern
#   - setFieldFlag for conditional UI behavior
#   - Branching by WORKORDER.WORKTYPE
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import MboConstants
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_workorder_obj_init")


# =============================================================================
# Main
# =============================================================================
def init_workorder():
    if mbo is None:                                          # noqa: F821
        return

    worktype = ""
    if not mbo.isNull("WORKTYPE"):                           # noqa: F821
        worktype = mbo.getString("WORKTYPE")                 # noqa: F821

    # Emergency work orders cannot be downgraded in priority field
    if worktype == "EM":
        mbo.setFieldFlag("WOPRIORITY", MboConstants.READONLY, True)   # noqa: F821
    else:
        mbo.setFieldFlag("WOPRIORITY", MboConstants.READONLY, False)  # noqa: F821

    # Capital Project work types require a project number
    if worktype == "CP":
        mbo.setFieldFlag("PROJECTID", MboConstants.REQUIRED, True)    # noqa: F821
    else:
        mbo.setFieldFlag("PROJECTID", MboConstants.REQUIRED, False)   # noqa: F821


init_workorder()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_WORKORDER_OBJ_INIT",
    "description": "Apply UI flags on WORKORDER based on WORKTYPE.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_WORKORDER_OBJ_INIT",
        "launchPointType": "OBJECT",
        "active": True,
        "objectName": "WORKORDER",
        "events": {"initialize": True},
        "description": "Initialize WORKORDER UI flags by WORKTYPE."
    }]
}
