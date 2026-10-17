# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_WORKORDER_DESCRIPTION_ACTION
# Launch Point Name: TMG_WORKORDER_DESCRIPTION_ACTION
# Launch Point Type: ATTRIBUTE
# Object: WORKORDER
# Field: DESCRIPTION
# Event: ACTION
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Trim whitespace and normalize capitalization on WORKORDER.DESCRIPTION.
# Runs on the ACTION event (after the user types and before save), so the
# value is committed in canonical form.
#
# Demonstrates:
#   - ACTION event pattern (writable, fires on field change)
#   - String normalization
#   - Idempotent setValue() call (safe to re-run)
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import MboConstants
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_workorder_description_action")


# =============================================================================
# Main
# =============================================================================
def normalize_description():
    if mbo is None:                                         # noqa: F821
        return
    if mbo.isNull("DESCRIPTION"):                           # noqa: F821
        return

    raw = mbo.getString("DESCRIPTION")                      # noqa: F821
    cleaned = raw.strip()
    if len(cleaned) == 0:
        return

    # Capitalize first letter, leave the rest as the user typed it
    if not cleaned[0].isupper():
        cleaned = cleaned[0].upper() + cleaned[1:]

    if cleaned != raw:
        mbo.setValue("DESCRIPTION", cleaned, MboConstants.NOACCESSCHECK)  # noqa: F821
        _LOGGER.debug("Normalized DESCRIPTION on WORKORDER %s" % mbo.getString("WONUM"))  # noqa: F821


normalize_description()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_WORKORDER_DESCRIPTION_ACTION",
    "description": "Trim and capitalize WORKORDER.DESCRIPTION on field change.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_WORKORDER_DESCRIPTION_ACTION",
        "launchPointType": "ATTRIBUTE",
        "active": True,
        "objectName": "WORKORDER",
        "attributeName": "DESCRIPTION",
        "events": {"action": True},
        "description": "Normalize DESCRIPTION format on field change."
    }]
}
