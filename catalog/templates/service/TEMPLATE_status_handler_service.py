################################################################################
# Script: {object}.status.{statuscode}.py
# Object: {OBJECT}
# Status Transition: {FROM_STATUS} -> {TO_STATUS}
# Logging: service implicit variable (no Java imports)
#
# Author: Converted from Java {JAVA_CLASS}
# Date: {DATE}
#
# DESCRIPTION:
#   {PURPOSE_DESCRIPTION}
#
# STATUS TRANSITIONS HANDLED:
#   - {FROM_STATUS} -> {TO_STATUS}: {TRANSITION_DESC}
#
# BUSINESS REQUIREMENTS:
#   - {REQUIREMENT_1}
#   - {REQUIREMENT_2}
#
# IMPLEMENTATION NOTE:
#   Status handlers in Java use canChangeStatus() / changeStatus() methods.
#   In automation scripts, this is implemented as an OBJECT launch point on
#   the SAVE event, checking for status changes and applying business rules.
#
# CONVERTED FROM: tmg/{MODULE}/{JAVA_CLASS}.java
#   Method: canChangeStatus() / changeStatus()
################################################################################

from psdi.util import MXApplicationException
from psdi.mbo import MboConstants, SqlFormat
from psdi.server import MXServer

SCRIPT_NAME = "{object}.status.{statuscode}"

try:
    service.log(SCRIPT_NAME + ": Checking status change")

    status_mbo = mbo
    current_status = status_mbo.getString("STATUS")
    key_value = status_mbo.getString("{KEY_FIELD}")

    # Check if status actually changed (only process on real transitions)
    if not status_mbo.getMboValue("STATUS").isModified():
        # Status didn't change, skip processing
        pass
    else:
        previous_status = status_mbo.getMboValue("STATUS").getPreviousValue().asString()
        service.log(SCRIPT_NAME + ": Status changing from " + previous_status +
                    " to " + current_status + " for " + str(key_value))

        # ==========================================
        # CAN CHANGE STATUS LOGIC (validation)
        # Use service.error() to block transition with field-level error
        # ==========================================

        # Example: Prevent closing without required fields
        # if current_status == "CLOSE":
        #     if status_mbo.isNull("TMG_REQUIRED_FIELD"):
        #         service.error("TMG_REQUIRED_FIELD", "Field is required before closing")

        # Example: Only allow specific transitions
        # valid_transitions = {
        #     "WAPPR": ["APPR", "CAN"],
        #     "APPR": ["INPRG", "CAN"],
        #     "INPRG": ["COMP"],
        #     "COMP": ["CLOSE"]
        # }
        # if previous_status in valid_transitions:
        #     if current_status not in valid_transitions[previous_status]:
        #         service.error("STATUS", "Cannot change from " + previous_status + " to " + current_status)

        # ==========================================
        # CHANGE STATUS LOGIC (side effects)
        # Actions to perform when status changes
        # ==========================================

        # Example: Set fields on approval
        # if current_status == "APPR":
        #     status_mbo.setValue("TMG_APPROVEDBY", status_mbo.getUserInfo().getUserName(),
        #                        MboConstants.NOACCESSCHECK)
        #     status_mbo.setValue("TMG_APPROVEDDATE", MXServer.getMXServer().getDate(),
        #                        MboConstants.NOACCESSCHECK)

        # Example: Make fields readonly after completion
        # if current_status in ["COMP", "CLOSE"]:
        #     status_mbo.setFieldFlag("DESCRIPTION", MboConstants.READONLY, True)
        #     status_mbo.setFieldFlag("TMG_CUSTOM_FIELD", MboConstants.READONLY, True)

        service.log(SCRIPT_NAME + ": Status change processed: " + previous_status +
                   " -> " + current_status + " for " + str(key_value))

except MXApplicationException as mxe:
    service.log_warn(SCRIPT_NAME + ": Status change blocked: " + str(mxe))
    raise
except Exception as e:
    service.log_error(SCRIPT_NAME + ": Error processing status change: " + str(e))
    raise

################################################################################
# SCRIPT CONFIGURATION
################################################################################
# NOTE: Status handlers use OBJECT launch points on SAVE event.
# The script checks if STATUS field was modified and processes accordingly.
################################################################################
scriptConfig = {
    "autoscript": "TMG_{OBJECT}.STATUS.HANDLER",
    "description": "{SCRIPT_DESCRIPTION}",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "TMG_{OBJECT}_STATUS_HANDLER",
            "launchPointType": "OBJECT",
            "active": True,
            "description": "Status change handler: {LP_DESCRIPTION}",
            "objectName": "{OBJECT}",
            "init": False,
            "add": False,
            "update": True,
            "delete": False,
            "save": True,
            "beforeSave": True,
            "afterSave": False,
            "afterCommit": False
        }
    ]
}
