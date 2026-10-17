################
# Script: {OBJECT_DESC} {FIELD} List Filter Handler
# Object/Field: {OBJECT}.{FIELD}
# Event: VALIDATE (list filtering via validation)
# Logging: service implicit variable (no Java imports)
#
# Author: {AUTHOR}
#
# Naming Convention: {object}.{field}.listfilter.py
#
# Conversion: Converted from {JAVA_CLASS}.java
# Original: TMGMaximo/businessobjects/tmg/{MODULE_PATH}/{JAVA_CLASS}.java
#
# Purpose: {PURPOSE_DESCRIPTION}
#
# IMPORTANT NOTE:
# Maximo automation scripts cannot override getList() directly.
# This script uses VALIDATE event as an alternative approach:
# - Validates the selected value against allowed criteria
# - Rejects values that would have been filtered from the list
# - For true list filtering, use Application Designer domain configuration
#
# Business Logic:
# - {BUSINESS_RULE_1}
# - {BUSINESS_RULE_2}
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

SCRIPT_NAME = "{object}.{field}.listfilter"

try:
    # Get the current Mbo and field value
    current_mbo = mbo
    field_value = current_mbo.getString("{FIELD}")

    if field_value is not None and field_value != "":
        # ==========================================
        # LIST FILTER LOGIC HERE
        # Validate that the selected value is allowed
        # ==========================================

        # Example: Reject items with certain statuses
        # item_set = current_mbo.getMboSet("$itemcheck", "ITEM",
        #     "itemnum = '" + field_value + "' and status in ('PENDING', 'OBSOLETE')")
        # try:
        #     if not item_set.isEmpty():
        #         service.error("{FIELD}", "Selected value is not allowed (status is inactive)")
        # finally:
        #     item_set.close()

        pass

    service.log(SCRIPT_NAME + ": List filter validation completed for {OBJECT}")

except Exception as e:
    service.log_error(SCRIPT_NAME + ": Error in list filter: " + str(e))
    raise

# Script Configuration for Launch Point Creation
scriptConfig = {
    "autoscript": "{object}.{field}.listfilter",
    "description": "{SCRIPT_DESCRIPTION}",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "SC{OBJECT}{FIELD}_LISTFILTER",
            "launchPointType": "ATTRIBUTE",
            "objectName": "{OBJECT}",
            "attributeName": "{FIELD}",
            "description": "{LP_DESCRIPTION}",
            "validate": True
        }
    ]
}
