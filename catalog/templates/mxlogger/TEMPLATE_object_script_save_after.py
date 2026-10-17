# ============================================================================
# Script: {object}.obj.save.after.py
# Object: {OBJECT}
# Launch Point: Object (SAVE - After Save)
#
# Description:
# {PURPOSE_DESCRIPTION}
#
# Converted From:
# Java Class: tmg/{MODULE_PATH}/{JAVA_CLASS}.java
# Method: save() (post-save logic)
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
className = "{object}.obj.save.after"


def process_after_save():
    """Execute business logic after MBO has been saved to database."""
    logger.debug(className + ": Processing after save")

    # ==========================================
    # POST-SAVE LOGIC HERE
    # Record is saved but transaction not committed yet
    # ==========================================

    # Example: Create related records after save
    # child_set = mbo.getMboSet("CHILD_RELATIONSHIP")
    # new_child = child_set.add()
    # new_child.setValue("PARENT_KEY", mbo.getString("KEY_FIELD"))

    # Example: Update counters or aggregates
    # parent_set = mbo.getMboSet("PARENT_RELATIONSHIP")
    # parent = parent_set.getMbo(0)
    # if parent is not None:
    #     parent.setValue("TMG_COUNT", parent.getInt("TMG_COUNT") + 1)

    logger.debug(className + ": After save processing completed")


# ==========================================================================================
# MAIN EXECUTION
# ==========================================================================================

try:
    process_after_save()
    logger.debug(className + ": After save completed successfully")

except Exception as e:
    logger.error(className + ": Error in after save: " + str(e))
    raise


# ==========================================================================================
# SCRIPT CONFIGURATION
# ==========================================================================================
scriptConfig = {
    "autoscript": "TMG_{OBJECT}.OBJ.SAVE.AFTER",
    "description": "{SCRIPT_DESCRIPTION}",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "TMG_{OBJECT}_OBJ_SAVE_AFTER",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "After Save: {LP_DESCRIPTION}",
            "objectName": "{OBJECT}",
            "init": False,
            "add": False,
            "update": False,
            "delete": False,
            "save": False,
            "afterSave": True,
            "afterCommit": False
        }
    ]
}
