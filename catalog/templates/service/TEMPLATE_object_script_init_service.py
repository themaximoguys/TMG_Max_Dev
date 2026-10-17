# ============================================================================
# Script: {object}.obj.init.py
# Object: {OBJECT}
# Launch Point: Object (INIT)
# Logging: service implicit variable (no Java imports)
#
# Description:
# {PURPOSE_DESCRIPTION}
#
# Converted From:
# Java Class: tmg/{MODULE_PATH}/{JAVA_CLASS}.java
# Method: init()
#
# Conversion Review:
# - Business Area: {BUSINESS_AREA}
#
# History:
# Date       Developer  Description
# ---------- ---------- ---------------------------------------------------
# {DATE}     {AUTHOR}   Converted from Java to Python automation script
# {ORIG_DATE} {ORIG_AUTHOR} Original Java implementation
# ============================================================================

from psdi.mbo import MboConstants

# Script identifier for log messages
SCRIPT_NAME = "{object}.obj.init"


def initialize_mbo():
    """Initialize MBO after loading from database."""
    service.log(SCRIPT_NAME + ": Initializing MBO")

    # ==========================================
    # INIT LOGIC HERE
    # Runs when MBO is loaded from DB (not on new/add)
    # ==========================================

    # Example: Set field readonly based on status
    # status = mbo.getString("STATUS")
    # if status in ["CLOSE", "CAN"]:
    #     mbo.setFieldFlag("TMG_CUSTOM_FIELD", MboConstants.READONLY, True)

    # Example: Set field readonly based on org
    # orgid = mbo.getString("ORGID")
    # if orgid == "ORG1":
    #     mbo.setFieldFlag("TMG_SPECIAL_FIELD", MboConstants.READONLY, False)

    service.log(SCRIPT_NAME + ": MBO initialization completed")


# ==========================================================================================
# MAIN EXECUTION
# ==========================================================================================

try:
    initialize_mbo()
    service.log(SCRIPT_NAME + ": Init completed successfully")

except Exception as e:
    service.log_error(SCRIPT_NAME + ": Error in init: " + str(e))
    raise


# ==========================================================================================
# SCRIPT CONFIGURATION
# ==========================================================================================
scriptConfig = {
    "autoscript": "TMG_{OBJECT}.OBJ.INIT",
    "description": "{SCRIPT_DESCRIPTION}",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "TMG_{OBJECT}_OBJ_INIT",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Init: {LP_DESCRIPTION}",
            "objectName": "{OBJECT}",
            "init": True,
            "add": False,
            "update": False,
            "delete": False,
            "save": False,
            "afterSave": False,
            "afterCommit": False
        }
    ]
}
