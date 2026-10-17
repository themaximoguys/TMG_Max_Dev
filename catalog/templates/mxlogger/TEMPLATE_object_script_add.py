# ============================================================================
# Script: {object}.obj.add.py
# Object: {OBJECT}
# Launch Point: Object (ADD)
#
# Description:
# {PURPOSE_DESCRIPTION}
#
# Converted From:
# Java Class: tmg/{MODULE_PATH}/{JAVA_CLASS}.java
# Method: add()
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

from psdi.util.logging import MXLoggerFactory
from psdi.mbo import MboConstants

# Initialize logger
logger = MXLoggerFactory.getLogger("maximo.application.{OBJECT}")
className = "{object}.obj.add"


def initialize_on_add():
    """Set default values when a new MBO record is created."""
    logger.debug(className + ": Initializing new record")

    # ==========================================
    # ADD/NEW RECORD INITIALIZATION LOGIC HERE
    # ==========================================

    # Example: Set defaults based on context
    # orgid = mbo.getString("ORGID")
    # if orgid == "ORG1":
    #     mbo.setValue("TMG_CUSTOM_FIELD", "SNC_DEFAULT", MboConstants.NOACCESSCHECK)
    # else:
    #     mbo.setValue("TMG_CUSTOM_FIELD", "DEFAULT", MboConstants.NOACCESSCHECK)

    logger.debug(className + ": New record defaults set")


# ==========================================================================================
# MAIN EXECUTION
# ==========================================================================================

try:
    initialize_on_add()
    logger.debug(className + ": Add initialization completed successfully")

except Exception as e:
    logger.error(className + ": Error initializing new record: " + str(e))
    raise


# ==========================================================================================
# SCRIPT CONFIGURATION
# ==========================================================================================
scriptConfig = {
    "autoscript": "TMG_{OBJECT}.OBJ.ADD",
    "description": "{SCRIPT_DESCRIPTION}",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "TMG_{OBJECT}_OBJ_ADD",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Add: {LP_DESCRIPTION}",
            "objectName": "{OBJECT}",
            "init": False,
            "add": True,
            "update": False,
            "delete": False,
            "save": False,
            "afterSave": False,
            "afterCommit": False
        }
    ]
}
