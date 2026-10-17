################################################################################
# Script: {object}.escalation.{name}.py
# Object: {OBJECT}
# Escalation: {ESCALATION_NAME}
# Action: {ACTION_NAME}
#
# Author: Converted from Java {JAVA_CLASS}
# Date: {DATE}
#
# DESCRIPTION:
#   {PURPOSE_DESCRIPTION}
#
# ESCALATION SETUP:
#   Escalation Point: {ESCALATION_NAME}
#   Condition: {CONDITION_SQL}
#   Schedule: {SCHEDULE}
#   Action: Run Automation Script
#
# BUSINESS REQUIREMENTS:
#   - {REQUIREMENT_1}
#   - {REQUIREMENT_2}
#
# CONVERTED FROM: tmg/{MODULE}/{JAVA_CLASS}.java
################################################################################

from psdi.util.logging import MXLoggerFactory
from psdi.util import MXApplicationException
from psdi.mbo import MboConstants
from psdi.server import MXServer

logger = MXLoggerFactory.getLogger("maximo.escalation.{name}")
className = "{object}.escalation.{name}"

try:
    logger.info(className + ": Starting escalation action")

    # Get the MBO matched by escalation condition
    esc_mbo = mbo

    # Get key fields for logging
    key_value = esc_mbo.getString("{KEY_FIELD}")
    status = esc_mbo.getString("STATUS")

    logger.debug(className + ": Processing {KEY_FIELD}=" + str(key_value))

    # ==========================================
    # ESCALATION ACTION LOGIC HERE
    # ==========================================

    # Example: Auto-close stale records
    # if status == "COMP":
    #     esc_mbo.changeStatus("CLOSE", mbo.getDate(), "Auto-closed by escalation")
    #     logger.info(className + ": Auto-closed " + str(key_value))

    # Example: Send notification
    # commSet = esc_mbo.getMboSet("COMMLOG")
    # newComm = commSet.add()
    # newComm.setValue("SENDTO", "admin@company.com")
    # newComm.setValue("SUBJECT", "Escalation: " + str(key_value))
    # newComm.setValue("MESSAGE", "Record requires attention")

    logger.info(className + ": Escalation action completed")

except MXApplicationException as mxe:
    logger.error(className + ": Maximo error: " + str(mxe))
    raise
except Exception as e:
    logger.error(className + ": Error in escalation action: " + str(e))
    raise

################################################################################
# SCRIPT CONFIGURATION
################################################################################
# NOTE: Escalation scripts are bound via ACTION launch point.
# The escalation point configuration triggers the action which runs this script.
#
# Setup:
# 1. Create Escalation Point with SQL condition
# 2. Add Action: type = Run Automation Script
# 3. Set script name to this autoscript
################################################################################
scriptConfig = {
    "autoscript": "{OBJECT}.ESCALATION.{NAME}",
    "description": "{SCRIPT_DESCRIPTION}",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [
        {
            "launchPointName": "TMG_{OBJECT}_ESC_{NAME}",
            "launchPointType": "ACTION",
            "objectName": "{OBJECT}",
            "action": "TMG_ESC_{NAME}",
            "description": "{LP_DESCRIPTION}"
        }
    ],
    "escalationSetup": {
        "escalationName": "{ESCALATION_NAME}",
        "condition": "{CONDITION_SQL}",
        "schedule": "{SCHEDULE}",
        "actionType": "RUNAUTOSCRIPT"
    }
}
