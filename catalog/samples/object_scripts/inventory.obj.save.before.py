# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_INVENTORY_OBJ_SAVE_BEFORE
# Launch Point Name: TMG_INVENTORY_OBJ_SAVE_BEFORE
# Launch Point Type: OBJECT
# Object: INVENTORY
# Event: SAVE (before)
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Pre-save consistency rules for INVENTORY thresholds:
#   1. REORDERPOINT must not exceed MAXLEVEL (you can't reorder above max).
#   2. TMG_SAFETYSTOCK must be <= REORDERPOINT (safety floor sits below
#      the reorder trigger so the cron has time to react).
#   3. ORDERUNIT, when set, must be > 0.
#
# Demonstrates:
#   - OBJECT SAVE before-event with multi-rule validation
#   - Helper functions per rule for readability + isolated re-raise
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_inventory_obj_save_before")


# =============================================================================
# Helpers
# =============================================================================
def _check_reorderpoint_vs_max():
    if mbo.isNull("REORDERPOINT") or mbo.isNull("MAXLEVEL"):    # noqa: F821
        return
    rop = mbo.getDouble("REORDERPOINT")                         # noqa: F821
    mx  = mbo.getDouble("MAXLEVEL")                             # noqa: F821
    if rop > mx:
        _LOGGER.warn("REORDERPOINT %s > MAXLEVEL %s on ITEM=%s" %
                     (rop, mx, mbo.getString("ITEMNUM")))       # noqa: F821
        raise MXApplicationException("tmg", "reorderpointabovemax")


def _check_safety_vs_reorder():
    if mbo.isNull("TMG_SAFETYSTOCK") or mbo.isNull("REORDERPOINT"):   # noqa: F821
        return
    safety = mbo.getDouble("TMG_SAFETYSTOCK")                   # noqa: F821
    rop    = mbo.getDouble("REORDERPOINT")                      # noqa: F821
    if safety > rop:
        _LOGGER.warn("TMG_SAFETYSTOCK %s > REORDERPOINT %s on ITEM=%s" %
                     (safety, rop, mbo.getString("ITEMNUM")))   # noqa: F821
        raise MXApplicationException("tmg", "safetyabovereorder")


def _check_orderunit_positive():
    if mbo.isNull("ORDERUNIT"):                                 # noqa: F821
        return
    if mbo.getDouble("ORDERUNIT") <= 0:                         # noqa: F821
        raise MXApplicationException("tmg", "orderunitnotpositive")


# =============================================================================
# Main
# =============================================================================
def validate_inventory_save():
    if mbo is None:                                          # noqa: F821
        return
    try:
        _check_reorderpoint_vs_max()
        _check_safety_vs_reorder()
        _check_orderunit_positive()
    except MXApplicationException:
        raise
    except Exception as e:                                    # noqa
        _LOGGER.error("Unexpected INVENTORY validation error: %s" % str(e))
        raise


validate_inventory_save()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_INVENTORY_OBJ_SAVE_BEFORE",
    "description": "Enforce threshold consistency: REORDERPOINT<=MAXLEVEL, SAFETY<=REORDERPOINT.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_INVENTORY_OBJ_SAVE_BEFORE",
        "launchPointType": "OBJECT",
        "active": True,
        "objectName": "INVENTORY",
        "events": {"save": True, "beforesave": True},
        "description": "Validate INVENTORY threshold relationships."
    }]
}
