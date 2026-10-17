# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_INVENTORY_CURBAL_VALIDATE
# Launch Point Name: TMG_INVENTORY_CURBAL_VALIDATE
# Launch Point Type: ATTRIBUTE
# Object: INVENTORY
# Field: CURBAL
# Event: VALIDATE
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Reject saves where INVENTORY.CURBAL goes negative. Allows zero and positive
# values. Demonstrates how to halt a save via MXApplicationException with a
# Maximo message group key.
#
# Demonstrates:
#   - VALIDATE event with numeric guard
#   - Logging the failed condition before raising
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_inventory_curbal_validate")


# =============================================================================
# Main
# =============================================================================
def validate_curbal():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.isNull("CURBAL"):                                 # noqa: F821
        return

    curbal = mbo.getDouble("CURBAL")                         # noqa: F821
    if curbal < 0:
        item = "<unknown>"
        try:
            if not mbo.isNull("ITEMNUM"):                    # noqa: F821
                item = mbo.getString("ITEMNUM")              # noqa: F821
        except Exception:
            pass
        _LOGGER.warn("Negative CURBAL=%s on INVENTORY.ITEMNUM=%s — rejecting" % (curbal, item))
        raise MXApplicationException("tmg", "negativecurbal")


validate_curbal()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_INVENTORY_CURBAL_VALIDATE",
    "description": "Reject negative INVENTORY.CURBAL values.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_INVENTORY_CURBAL_VALIDATE",
        "launchPointType": "ATTRIBUTE",
        "active": True,
        "objectName": "INVENTORY",
        "attributeName": "CURBAL",
        "events": {"validate": True},
        "description": "Block negative inventory balance."
    }]
}
