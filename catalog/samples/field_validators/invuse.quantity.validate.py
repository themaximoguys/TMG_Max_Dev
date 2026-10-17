# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_INVUSE_QUANTITY_VALIDATE
# Launch Point Name: TMG_INVUSE_QUANTITY_VALIDATE
# Launch Point Type: ATTRIBUTE
# Object: INVUSELINE
# Field: QUANTITY
# Event: VALIDATE
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Reject INVUSELINE.QUANTITY values that would draw INVENTORY.CURBAL below
# the configured TMG_SAFETYSTOCK level for the item at that storeroom.
# Standard CURBAL >= 0 is enforced elsewhere; this rule enforces the
# *safety* threshold separately so operations don't silently exhaust a
# stocking buffer.
#
# Demonstrates:
#   - VALIDATE on a child object (INVUSELINE) that affects INVENTORY
#   - Cross-MBO lookup via SqlFormat with three-key join
#   - Reject with a contextual log line
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_invuse_quantity_validate")


# =============================================================================
# Helpers
# =============================================================================
def _lookup_inventory(itemnum, location, siteid):
    mxs = MXServer.getMXServer()
    inv_set = None
    try:
        inv_set = mxs.getMboSet("INVENTORY", mbo.getUserInfo())   # noqa: F821
        sf = SqlFormat(None, "itemnum = :1 and location = :2 and siteid = :3")
        sf.setObject(1, "INVENTORY", "ITEMNUM",  itemnum)
        sf.setObject(2, "INVENTORY", "LOCATION", location)
        sf.setObject(3, "INVENTORY", "SITEID",   siteid)
        inv_set.setWhere(sf.format())
        inv = inv_set.getMbo(0)
        if inv is None:
            return None, None
        curbal = inv.getDouble("CURBAL") if not inv.isNull("CURBAL") else 0.0
        safety = inv.getDouble("TMG_SAFETYSTOCK") if not inv.isNull("TMG_SAFETYSTOCK") else 0.0
        return curbal, safety
    finally:
        if inv_set is not None:
            try:
                inv_set.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def validate_quantity_against_safety_stock():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.isNull("QUANTITY"):                               # noqa: F821
        return
    if mbo.isNull("ITEMNUM") or mbo.isNull("LOCATION"):      # noqa: F821
        return

    qty      = mbo.getDouble("QUANTITY")                     # noqa: F821
    itemnum  = mbo.getString("ITEMNUM")                      # noqa: F821
    location = mbo.getString("LOCATION")                     # noqa: F821
    siteid   = mbo.getString("SITEID")                       # noqa: F821

    if qty <= 0:
        return  # negative/zero handled by other rules

    curbal, safety = _lookup_inventory(itemnum, location, siteid)
    if curbal is None:
        return  # no inventory row — let other validation catch it

    projected = curbal - qty
    if projected < safety:
        _LOGGER.warn(
            "INVUSELINE rejected: ITEM=%s LOC=%s qty=%s would drop CURBAL %s -> %s < safety %s" %
            (itemnum, location, qty, curbal, projected, safety)
        )
        raise MXApplicationException("tmg", "invusesafetystock")


validate_quantity_against_safety_stock()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_INVUSE_QUANTITY_VALIDATE",
    "description": "Reject inventory issue that would drop CURBAL below TMG_SAFETYSTOCK.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_INVUSE_QUANTITY_VALIDATE",
        "launchPointType": "ATTRIBUTE",
        "active": True,
        "objectName": "INVUSELINE",
        "attributeName": "QUANTITY",
        "events": {"validate": True},
        "description": "Enforce safety-stock floor on inventory issue."
    }]
}
