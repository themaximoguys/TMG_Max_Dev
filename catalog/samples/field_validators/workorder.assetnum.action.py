# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_WORKORDER_ASSETNUM_ACTION
# Launch Point Name: TMG_WORKORDER_ASSETNUM_ACTION
# Launch Point Type: ATTRIBUTE
# Object: WORKORDER
# Field: ASSETNUM
# Event: ACTION
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# When the user selects an ASSETNUM on a WORKORDER, cascade default values
# from the asset onto the work order, but never overwrite a value the user
# has already entered:
#   - LOCATION   ← ASSET.LOCATION (when blank)
#   - FAILURECODE ← ASSET.FAILURECODE (when blank)
#   - GLACCOUNT  ← LOCATIONS.GLACCOUNT for the asset's location (when blank)
#
# Demonstrates:
#   - Cross-MBO cascade with a chain (ASSET → LOCATIONS)
#   - Idempotent default-fill (only when target is null)
#   - Defensive close on every MboSet open
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import MboConstants, SqlFormat
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_workorder_assetnum_action")


# =============================================================================
# Helpers
# =============================================================================
def _fetch_asset(assetnum, siteid):
    mxs = MXServer.getMXServer()
    asset_set = None
    try:
        asset_set = mxs.getMboSet("ASSET", mbo.getUserInfo())   # noqa: F821
        sf = SqlFormat(None, "assetnum = :1 and siteid = :2")
        sf.setObject(1, "ASSET", "ASSETNUM", assetnum)
        sf.setObject(2, "ASSET", "SITEID",   siteid)
        asset_set.setWhere(sf.format())
        a = asset_set.getMbo(0)
        if a is None:
            return None, None, None
        loc = a.getString("LOCATION") if not a.isNull("LOCATION") else None
        fc  = a.getString("FAILURECODE") if not a.isNull("FAILURECODE") else None
        return a, loc, fc
    finally:
        if asset_set is not None:
            try:
                asset_set.close()
            except Exception:
                pass


def _glaccount_for_location(location, siteid):
    if location is None:
        return None
    mxs = MXServer.getMXServer()
    loc_set = None
    try:
        loc_set = mxs.getMboSet("LOCATIONS", mbo.getUserInfo())   # noqa: F821
        sf = SqlFormat(None, "location = :1 and siteid = :2")
        sf.setObject(1, "LOCATIONS", "LOCATION", location)
        sf.setObject(2, "LOCATIONS", "SITEID",   siteid)
        loc_set.setWhere(sf.format())
        loc = loc_set.getMbo(0)
        if loc is None or loc.isNull("GLACCOUNT"):
            return None
        return loc.getString("GLACCOUNT")
    finally:
        if loc_set is not None:
            try:
                loc_set.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def cascade_from_asset():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.isNull("ASSETNUM"):                               # noqa: F821
        return

    assetnum = mbo.getString("ASSETNUM")                     # noqa: F821
    siteid   = mbo.getString("SITEID")                       # noqa: F821

    asset, loc, fc = _fetch_asset(assetnum, siteid)
    if asset is None:
        return

    if mbo.isNull("LOCATION") and loc:                       # noqa: F821
        mbo.setValue("LOCATION", loc, MboConstants.NOACCESSCHECK)   # noqa: F821

    if mbo.isNull("FAILURECODE") and fc:                     # noqa: F821
        mbo.setValue("FAILURECODE", fc, MboConstants.NOACCESSCHECK)  # noqa: F821

    if mbo.isNull("GLACCOUNT"):                              # noqa: F821
        gl = _glaccount_for_location(loc, siteid)
        if gl is not None:
            mbo.setValue("GLACCOUNT", gl, MboConstants.NOACCESSCHECK)  # noqa: F821

    _LOGGER.debug("Cascaded ASSET %s defaults onto WORKORDER %s" %
                  (assetnum, mbo.getString("WONUM")))         # noqa: F821


cascade_from_asset()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_WORKORDER_ASSETNUM_ACTION",
    "description": "On ASSETNUM change, cascade LOCATION/FAILURECODE/GLACCOUNT defaults.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_WORKORDER_ASSETNUM_ACTION",
        "launchPointType": "ATTRIBUTE",
        "active": True,
        "objectName": "WORKORDER",
        "attributeName": "ASSETNUM",
        "events": {"action": True},
        "description": "Cascade defaults from ASSET to WORKORDER."
    }]
}
