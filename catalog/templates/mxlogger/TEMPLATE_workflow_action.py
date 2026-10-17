################################################################################
# Script: {object}.action.{actionname}.py
# Object: {OBJECT}
# Action: {ACTIONNAME}
#
# Author: Converted from Java {JAVA_CLASS}
# Date: {DATE}
#
# DESCRIPTION:
#   {PURPOSE_DESCRIPTION}
#
# BUSINESS REQUIREMENTS:
#   - {REQUIREMENT_1}
#   - {REQUIREMENT_2}
#
# CONVERTED FROM: tmg/workflow/{JAVA_CLASS}.applyCustomAction()
#   Original: Java workflow action class
#   History: Created {ORIG_DATE} ({TICKET})
################################################################################

from psdi.util.logging import MXLoggerFactory
from psdi.util import MXApplicationException
from psdi.mbo import MboConstants

logger = MXLoggerFactory.getLogger("maximo.workflow.action")
className = "{object}.action.{actionname}"

try:
    logger.debug(className + ": Starting workflow action")

    # Get the MBO (main object in workflow context)
    action_mbo = mbo

    # Get key fields for logging
    key_value = action_mbo.getString("{KEY_FIELD}")
    status = action_mbo.getString("STATUS")

    logger.debug(className + ": {KEY_FIELD}=" + str(key_value) + ", Status=" + status)

    # ==========================================
    # WORKFLOW ACTION LOGIC HERE
    # ==========================================

    # Example: Only proceed if record is in expected status
    # if status != "APPR":
    #     logger.info(className + ": Record not in expected status, skipping")
    # else:
    #     # Perform the workflow action
    #     action_mbo.setValue("TMG_CUSTOM_FIELD", "VALUE", MboConstants.NOACCESSCHECK)
    #     logger.info(className + ": Action completed for " + str(key_value))

    logger.info(className + ": Workflow action completed")

except MXApplicationException as mxe:
    logger.error(className + ": Maximo error in workflow action: " + str(mxe))
    raise
except Exception as e:
    logger.error(className + ": Error in workflow action", e)
    raise

################################################################################
# SCRIPT CONFIGURATION
################################################################################
scriptConfig = {
    "autoscript": "{OBJECT}.ACTION.{ACTIONNAME}",
    "description": "{SCRIPT_DESCRIPTION}",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [
        {
            "launchPointName": "TMG_{OBJECT}_ACTION_{ACTIONNAME}",
            "launchPointType": "ACTION",
            "objectName": "{OBJECT}",
            "action": "{ACTIONNAME}",
            "description": "{LP_DESCRIPTION}"
        }
    ]
}
