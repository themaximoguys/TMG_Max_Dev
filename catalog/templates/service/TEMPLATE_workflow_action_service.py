################################################################################
# Script: {object}.action.{actionname}.py
# Object: {OBJECT}
# Action: {ACTIONNAME}
# Logging: service implicit variable (no Java imports)
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

from psdi.util import MXApplicationException
from psdi.mbo import MboConstants

SCRIPT_NAME = "{object}.action.{actionname}"

try:
    service.log(SCRIPT_NAME + ": Starting workflow action")

    # Get the MBO (main object in workflow context)
    action_mbo = mbo

    # Get key fields for logging
    key_value = action_mbo.getString("{KEY_FIELD}")
    status = action_mbo.getString("STATUS")

    service.log(SCRIPT_NAME + ": {KEY_FIELD}=" + str(key_value) + ", Status=" + status)

    # ==========================================
    # WORKFLOW ACTION LOGIC HERE
    # ==========================================

    # Example: Only proceed if record is in expected status
    # if status != "APPR":
    #     service.log(SCRIPT_NAME + ": Record not in expected status, skipping")
    # else:
    #     # Perform the workflow action
    #     action_mbo.setValue("TMG_CUSTOM_FIELD", "VALUE", MboConstants.NOACCESSCHECK)
    #     service.log(SCRIPT_NAME + ": Action completed for " + str(key_value))

    service.log(SCRIPT_NAME + ": Workflow action completed")

except MXApplicationException as mxe:
    service.log_error(SCRIPT_NAME + ": Maximo error in workflow action: " + str(mxe))
    raise
except Exception as e:
    service.log_error(SCRIPT_NAME + ": Error in workflow action: " + str(e))
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
