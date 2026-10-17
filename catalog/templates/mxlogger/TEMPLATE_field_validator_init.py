################
# Script: {OBJECT_DESC} {FIELD} Field Initialization Handler
# Object/Field: {OBJECT}.{FIELD}
# Event: INIT (Initialize Value)
#
# Author: {AUTHOR}
#
# Naming Convention: {object}.{field}.init.py
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
# - {LP_NAME} ({OBJECT}.{FIELD}, INIT event)
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

logger = MXLoggerFactory.getLogger("maximo.script.{object}.{field}.init")

try:
    # Get the current Mbo
    current_mbo = mbo

    # ==========================================
    # INITIALIZATION LOGIC HERE
    # Sets initial/default value for the field
    # ==========================================

    # Example: Compute a default value
    # default_value = current_mbo.getString("SOME_SOURCE_FIELD")
    # current_mbo.setValue("{FIELD}", default_value, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

    logger.debug("{FIELD} init completed for {OBJECT}")

except Exception as e:
    logger.error("Error in {FIELD} initialization: " + str(e))
    raise

# Script Configuration for Launch Point Creation
scriptConfig = {
    "autoscript": "{object}.{field}.init",
    "description": "{SCRIPT_DESCRIPTION}",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLaunchPoints": [
        {
            "launchPointName": "SC{OBJECT}{FIELD}_INIT",
            "launchPointType": "ATTRIBUTE",
            "objectName": "{OBJECT}",
            "attributeName": "{FIELD}",
            "description": "{LP_DESCRIPTION}",
            "initValue": True
        }
    ]
}
