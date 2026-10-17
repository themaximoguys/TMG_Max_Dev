################
# Script: {OBJECT_DESC} {FIELD} Field Action Handler
# Object/Field: {OBJECT}.{FIELD}
# Event: ACTION (Run Action)
#
# Author: {AUTHOR}
#
# Naming Convention: {object}.{field}.action.py
#
# Conversion: Converted from {JAVA_CLASS}.java
# Original: TMGMaximo/businessobjects/tmg/{MODULE_PATH}/{JAVA_CLASS}.java
#
# Purpose: {PURPOSE_DESCRIPTION}
#
# Business Logic:
# - {BUSINESS_RULE_1}
# - {BUSINESS_RULE_2}
#
# Launch Points: {NUM_LAUNCH_POINTS}
# - {LP_NAME} ({OBJECT}.{FIELD}, ACTION event)
#
# Dependencies:
# - {DEPENDENCY_1}
#
# Revision:
# Date        User                        Comment
# {DATE}      {AUTHOR}                    Initial Python conversion from Java
# {ORIG_DATE} {ORIG_AUTHOR}               Original Java implementation ({TICKET})
################

from psdi.util.logging import MXLoggerFactory
from psdi.mbo import MboConstants

logger = MXLoggerFactory.getLogger("maximo.script.{object}.{field}.action")

try:
    # Get the current Mbo and field value
    current_mbo = mbo
    field_value = current_mbo.getString("{FIELD}")

    # ==========================================
    # ACTION LOGIC HERE
    # Runs when user changes the field value
    # ==========================================

    # Example: Set related fields based on new value
    # if field_value == "SOME_VALUE":
    #     current_mbo.setValue("TARGET_FIELD", "new_value", MboConstants.NOACCESSCHECK)

    logger.debug("{FIELD} action completed for {OBJECT}: " +
                str(current_mbo.getString("{KEY_FIELD}")))

except Exception as e:
    logger.error("Error in {FIELD} action: " + str(e))
    raise

# Script Configuration for Launch Point Creation
scriptConfig = {
    "autoscript": "{object}.{field}.action",
    "description": "{SCRIPT_DESCRIPTION}",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "SC{OBJECT}{FIELD}_ACTION",
            "launchPointType": "ATTRIBUTE",
            "objectName": "{OBJECT}",
            "attributeName": "{FIELD}",
            "description": "{LP_DESCRIPTION}",
            "runAction": True
        }
    ]
}
