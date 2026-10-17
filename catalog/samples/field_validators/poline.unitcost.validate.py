# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_POLINE_UNITCOST_VALIDATE
# Launch Point Name: TMG_POLINE_UNITCOST_VALIDATE
# Launch Point Type: ATTRIBUTE
# Object: POLINE
# Field: UNITCOST
# Event: VALIDATE
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Reject save when UNITCOST on a Purchase Order line is negative or exceeds
# a configurable maximum threshold (default: 1,000,000).
#
# Demonstrates:
#   - VALIDATE event pattern
#   - Numeric range checking
#   - errorgroup / errormsg implicit variables for user-facing validation errors
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_poline_unitcost_validate")
_MAX_UNIT_COST = 1000000.0


# =============================================================================
# Main
# =============================================================================
def validate_unit_cost():
    if mbo is None:                                         # noqa: F821 (implicit)
        return
    if mbo.isNull("UNITCOST"):                              # noqa: F821
        return

    unit_cost = mbo.getDouble("UNITCOST")                   # noqa: F821

    if unit_cost < 0:
        errorgroup = "tmg"                                  # noqa: F841
        errormsg = "negativeunitcost"                       # noqa: F841
        raise MXApplicationException("tmg", "negativeunitcost")

    if unit_cost > _MAX_UNIT_COST:
        _LOGGER.warn("UNITCOST %s exceeds threshold %s on POLINE %s" % (
            unit_cost, _MAX_UNIT_COST, mbo.getString("PONUM")))  # noqa: F821
        raise MXApplicationException("tmg", "unitcostexceedsmax")


validate_unit_cost()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_POLINE_UNITCOST_VALIDATE",
    "description": "Reject negative UNITCOST and values exceeding configured maximum on POLINE.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_POLINE_UNITCOST_VALIDATE",
        "launchPointType": "ATTRIBUTE",
        "active": True,
        "objectName": "POLINE",
        "attributeName": "UNITCOST",
        "events": {"validate": True},
        "description": "Validate UNITCOST is non-negative and within range."
    }]
}
