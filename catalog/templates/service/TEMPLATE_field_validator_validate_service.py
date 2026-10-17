################
# Script: {OBJECT_DESC} {FIELD} Field Validation Handler
# Object/Field: {OBJECT}.{FIELD}
# Event: VALIDATE
# Logging: service implicit variable (no Java imports)
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

from psdi.mbo import MboConstants

SCRIPT_NAME = "{object}.{field}.validate"

try:
    # Get the current Mbo and field value
    current_mbo = mbo
    field_value = current_mbo.getString("{FIELD}")

    if field_value is not None and field_value != "":
        # ==========================================
        # VALIDATION LOGIC HERE
        # ==========================================

        # Example: Check a condition and show field-level error
        # if invalid_condition:
        #     service.error("{FIELD}", "Invalid value: " + str(field_value))

        # Example: Warning without blocking save
        # if warning_condition:
        #     service.warning("Value may cause issues downstream")

        pass

    service.log(SCRIPT_NAME + ": Validation completed for " +
                str(current_mbo.getString("{KEY_FIELD}")))

except Exception as e:
    service.log_error(SCRIPT_NAME + ": Error in validation: " + str(e))
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
