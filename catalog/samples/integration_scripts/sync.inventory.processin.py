# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_SYNC_INVENTORY_PROCESSIN
# Launch Point Name: TMG_SYNC_INVENTORY_PROCESSIN
# Launch Point Type: SUBSCRIBE (Process In)
# Service: TMG_INVENTORY_IN
# Exit: PROCESSIN
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Inbound INVENTORY adjustment processing. Inbound message represents a
# physical-count result. Compute the variance against current CURBAL and,
# if non-zero, write an INVADJUSTMENT row capturing the count difference.
#
# Demonstrates:
#   - Inbound exit that triggers a side-effect record
#   - Numeric variance computation
#   - Defensive null handling on count fields
#
# =============================================================================
# Imports
# =============================================================================
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory

from java.util import Date


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_sync_inventory_processin")


# =============================================================================
# Main
# =============================================================================
def process_inventory_in():
    if mbo is None:                                          # noqa: F821
        return

    if mbo.isNull("PHYSCNT"):                                # noqa: F821
        return  # nothing to reconcile

    new_count = mbo.getDouble("PHYSCNT")                     # noqa: F821
    current   = mbo.getDouble("CURBAL") if not mbo.isNull("CURBAL") else 0.0   # noqa: F821
    variance = new_count - current

    if variance == 0:
        return

    mxs = MXServer.getMXServer()
    adj_set = None
    try:
        adj_set = mxs.getMboSet("INVADJUSTMENT", mbo.getUserInfo())   # noqa: F821
        adj = adj_set.add()
        adj.setValue("ITEMNUM",     mbo.getString("ITEMNUM"))   # noqa: F821
        adj.setValue("LOCATION",    mbo.getString("LOCATION"))  # noqa: F821
        adj.setValue("SITEID",      mbo.getString("SITEID"))    # noqa: F821
        adj.setValue("ADJUSTQTY",   variance)
        adj.setValue("ADJDATE",     Date())
        adj.setValue("MEMO",        "Physical count via TMG_INVENTORY_IN")
        adj_set.save()
        _LOGGER.info("INVADJUSTMENT written: ITEM=%s LOC=%s variance=%s" %
                     (mbo.getString("ITEMNUM"),               # noqa: F821
                      mbo.getString("LOCATION"),              # noqa: F821
                      variance))
    finally:
        if adj_set is not None:
            try:
                adj_set.close()
            except Exception:
                pass


process_inventory_in()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_SYNC_INVENTORY_PROCESSIN",
    "description": "Inbound INVENTORY: physical-count variance → INVADJUSTMENT row.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_SYNC_INVENTORY_PROCESSIN",
        "launchPointType": "SUBSCRIBE",
        "active": True,
        "enterpriseService": "TMG_INVENTORY_IN",
        "exitType": "PROCESSIN",
        "description": "Inbound INVENTORY count variance handler."
    }]
}
