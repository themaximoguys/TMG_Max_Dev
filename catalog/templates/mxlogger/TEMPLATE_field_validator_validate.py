################
# Script: {OBJECT_DESC} {FIELD} Field Validation Handler
# Object/Field: {OBJECT}.{FIELD}
# Event: VALIDATE
#
# Author: {AUTHOR}
#
# Naming Convention: {object}.{field}.validate.py
#
# Conversion: Converted from {JAVA_CLASS}.java
# Original: TMGMaximo/businessobjects/tmg/{MODULE_PATH}/{JAVA_CLASS}.java
#
# Purpose: {PURPOSE_DESCRIPTION}
#
# Business Logic:
# - {BUSINESS_RULE_1}
# - {BUSINESS_RULE_2}
# - {BUSINESS_RULE_3}
#
# Launch Points: {NUM_LAUNCH_POINTS}
# - {LP_NAME} ({OBJECT}.{FIELD}, VALIDATE event)
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
from psdi.util import MXApplicationException
from psdi.mbo import MboConstants

logger = MXLoggerFactory.getLogger("maximo.script.{object}.{field}.validate")

try:
    # Get the current Mbo and field value
    current_mbo = mbo
    field_value = current_mbo.getString("{FIELD}")

    if field_value is not None and field_value != "":
        # ==========================================
        # VALIDATION LOGIC HERE
        # ==========================================

        # Example: Check a condition and throw error if invalid
        # if invalid_condition:
        #     params = [field_value]
        #     raise MXApplicationException("{error_group}", "{error_key}", params)

        pass

    logger.debug("{FIELD} validation completed for {OBJECT}: " +
                str(current_mbo.getString("{KEY_FIELD}")))

except MXApplicationException as mxe:
    # Re-raise Maximo exceptions (validation errors shown to user)
    logger.warn("{FIELD} validation failed: " + str(mxe))
    raise
except Exception as e:
    logger.error("Error in {FIELD} validation: " + str(e))
    raise

# Script Configuration for Launch Point Creation
scriptConfig = {
    "autoscript": "{object}.{field}.validate",
    "description": "{SCRIPT_DESCRIPTION}",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "SC{OBJECT}{FIELD}_VALIDATE",
            "launchPointType": "ATTRIBUTE",
            "objectName": "{OBJECT}",
            "attributeName": "{FIELD}",
            "description": "{LP_DESCRIPTION}",
            "validate": True
        }
    ]
}
