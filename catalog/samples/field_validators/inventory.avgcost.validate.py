# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_INVENTORY_AVGCOST_VALIDATE
# Launch Point Name: TMG_INVENTORY_AVGCOST_VALIDATE
# Launch Point Type: ATTRIBUTE
# Object: INVENTORY
# Field: AVGCOST
# Event: VALIDATE
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Reject AVGCOST changes that deviate by more than 50% from the previous
# AVGCOST. Catches accidental decimal-point errors and cost-data-entry
# mistakes that can throw off financial reporting.
#
# Skips the check on first-time set (no prior value).
#
# Demonstrates:
#   - VALIDATE comparing new vs original via getMboValue().getOriginalValue()
#   - Configurable deviation threshold (constant)
#   - Allow legitimate large changes via mbo.setValue("TMG_AVGCOSTOVERRIDE", true)
#     prior to save (escape hatch for cost-correction scenarios)
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_inventory_avgcost_validate")
_MAX_DEVIATION = 0.50  # 50%


# =============================================================================
# Helpers
# =============================================================================
def _get_old_avgcost():
    attr = mbo.getMboValue("AVGCOST")                        # noqa: F821
    if attr is None:
        return None
    try:
        ov = attr.getOriginalValue()
        if ov is None:
            return None
        return ov.asDouble()
    except Exception:
        return None


# =============================================================================
# Main
# =============================================================================
def validate_avgcost_deviation():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.isNull("AVGCOST"):                                # noqa: F821
        return
    new_cost = mbo.getDouble("AVGCOST")                      # noqa: F821

    # Operator override flag
    if not mbo.isNull("TMG_AVGCOSTOVERRIDE"):                # noqa: F821
        if mbo.getBoolean("TMG_AVGCOSTOVERRIDE"):            # noqa: F821
            _LOGGER.info("AVGCOST deviation override flag set on ITEM=%s — skipping check" %
                         mbo.getString("ITEMNUM"))           # noqa: F821
            return

    old_cost = _get_old_avgcost()
    if old_cost is None or old_cost == 0:
        return  # initial set, no baseline to compare

    deviation = abs(new_cost - old_cost) / old_cost
    if deviation > _MAX_DEVIATION:
        _LOGGER.warn(
            "AVGCOST change rejected on ITEM=%s LOC=%s: %.4f -> %.4f (%.1f%% deviation)" %
            (mbo.getString("ITEMNUM"), mbo.getString("LOCATION"),    # noqa: F821
             old_cost, new_cost, deviation * 100)
        )
        raise MXApplicationException("tmg", "avgcostdeviationtoolarge")


validate_avgcost_deviation()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_INVENTORY_AVGCOST_VALIDATE",
    "description": "Reject AVGCOST changes deviating > 50% from prior, unless override flag set.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_INVENTORY_AVGCOST_VALIDATE",
        "launchPointType": "ATTRIBUTE",
        "active": True,
        "objectName": "INVENTORY",
        "attributeName": "AVGCOST",
        "events": {"validate": True},
        "description": "Catch large AVGCOST swings (decimal-point errors)."
    }]
}
