# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_ASSET_LOCATION_ACTION
# Launch Point Name: TMG_ASSET_LOCATION_ACTION
# Launch Point Type: ATTRIBUTE
# Object: ASSET
# Field: LOCATION
# Event: ACTION
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# When an ASSET's LOCATION is changed, write a row to ASSETTRANS so the
# move is tracked in asset history. Skips the case where the ASSET is
# brand-new (no original LOCATION) — that's not a "move".
#
# Demonstrates:
#   - ACTION event reading old vs new value via getMboValue().getOriginalValue()
#   - Side-effect insert into a separate object set
#   - Idempotency check: only on actual change, not initial set
#
# =============================================================================
# Imports
# =============================================================================
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory

from java.util import Date


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_asset_location_action")


# =============================================================================
# Helpers
# =============================================================================
def _get_old_location():
    attr = mbo.getMboValue("LOCATION")                       # noqa: F821
    if attr is None:
        return None
    try:
        ov = attr.getOriginalValue()
        if ov is None:
            return None
        return ov.asString()
    except Exception:
        return None


# =============================================================================
# Main
# =============================================================================
def write_asset_move():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.toBeAdded():                                      # noqa: F821
        return  # initial placement is not a move

    old_loc = _get_old_location()
    if old_loc is None:
        return  # had no prior location
    new_loc = mbo.getString("LOCATION") if not mbo.isNull("LOCATION") else None  # noqa: F821
    if new_loc == old_loc:
        return  # no change

    mxs = MXServer.getMXServer()
    user_info = mbo.getUserInfo()                            # noqa: F821
    trans_set = None
    try:
        trans_set = mxs.getMboSet("ASSETTRANS", user_info)
        row = trans_set.add()
        row.setValue("ASSETNUM",      mbo.getString("ASSETNUM"))   # noqa: F821
        row.setValue("SITEID",        mbo.getString("SITEID"))     # noqa: F821
        row.setValue("FROMLOCATION",  old_loc)
        row.setValue("TOLOCATION",    new_loc if new_loc is not None else "")
        row.setValue("MOVEDATE",      Date())
        row.setValue("TRANSTYPE",     "MOVE")
        if user_info is not None:
            row.setValue("MOVEDBY",   user_info.getUserName())
        trans_set.save()
        _LOGGER.info("ASSETTRANS row added: ASSETNUM=%s %s -> %s" %
                     (mbo.getString("ASSETNUM"), old_loc, new_loc))   # noqa: F821
    except Exception as e:                                    # noqa
        _LOGGER.error("Failed to record ASSETTRANS: %s" % str(e))
        raise
    finally:
        if trans_set is not None:
            try:
                trans_set.close()
            except Exception:
                pass


write_asset_move()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_ASSET_LOCATION_ACTION",
    "description": "Write ASSETTRANS history row when an ASSET is moved between locations.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_ASSET_LOCATION_ACTION",
        "launchPointType": "ATTRIBUTE",
        "active": True,
        "objectName": "ASSET",
        "attributeName": "LOCATION",
        "events": {"action": True},
        "description": "Record ASSETTRANS row on location change."
    }]
}
