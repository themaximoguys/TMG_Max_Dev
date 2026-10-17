# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PUBLISH_INVENTORY_PROCESSOUT
# Launch Point Name: TMG_PUBLISH_INVENTORY_PROCESSOUT
# Launch Point Type: PUBLISH (Process Out)
# Channel: TMG_INVENTORY_OUT
# Exit: PROCESSOUT
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Outbound INVENTORY balance feed.
#   - Skip rows where CURBAL <= 0 (don't bother external system with empties)
#   - Round CURBAL to whole units when ITEM.ORDERUNIT is 'EA' (each)
#   - Append a stockout flag = 1 if CURBAL == 0 else 0 (informational)
#
# Demonstrates:
#   - Conditional skip + numeric rounding on outbound payload
#   - Cross-MBO lookup to ITEM for unit-of-measure
#   - Computed boolean field
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory

import math


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_publish_inventory_processout")


# =============================================================================
# Helpers
# =============================================================================
def _order_unit(itemnum):
    if itemnum is None or len(itemnum.strip()) == 0:
        return None
    mxs = MXServer.getMXServer()
    s = None
    try:
        s = mxs.getMboSet("ITEM", mbo.getUserInfo())         # noqa: F821
        sf = SqlFormat(None, "itemnum = :1")
        sf.setObject(1, "ITEM", "ITEMNUM", itemnum)
        s.setWhere(sf.format())
        item = s.getMbo(0)
        if item is None or item.isNull("ORDERUNIT"):
            return None
        return item.getString("ORDERUNIT")
    finally:
        if s is not None:
            try:
                s.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def process_inventory_out():
    if mbo is None:                                          # noqa: F821
        return

    curbal = mbo.getDouble("CURBAL") if not mbo.isNull("CURBAL") else 0.0   # noqa: F821

    if curbal <= 0:
        _LOGGER.debug("Skip INVENTORY publish — CURBAL %s for ITEMNUM=%s" %
                      (curbal, mbo.getString("ITEMNUM")))    # noqa: F821
        try:
            irData.setStop(True)                             # noqa: F821
        except Exception:
            pass
        return

    itemnum = mbo.getString("ITEMNUM")                       # noqa: F821
    unit = _order_unit(itemnum)
    if unit is not None and unit.upper() == "EA":
        rounded = float(math.floor(curbal))
        try:
            irData.setAsString("CURBAL", "%.0f" % rounded)   # noqa: F821
        except Exception:
            pass

    try:
        irData.setAsString("TMG_STOCKOUT", "1" if curbal == 0 else "0")   # noqa: F821
    except Exception:
        pass


process_inventory_out()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_PUBLISH_INVENTORY_PROCESSOUT",
    "description": "Outbound INVENTORY: skip empty balances, round EA units, add stockout flag.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PUBLISH_INVENTORY_PROCESSOUT",
        "launchPointType": "PUBLISH",
        "active": True,
        "publishChannel": "TMG_INVENTORY_OUT",
        "exitType": "PROCESSOUT",
        "description": "Outbound INVENTORY processing exit."
    }]
}
