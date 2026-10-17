# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_ASSET_PARENT_VALIDATE
# Launch Point Name: TMG_ASSET_PARENT_VALIDATE
# Launch Point Type: ATTRIBUTE
# Object: ASSET
# Field: PARENT
# Event: VALIDATE
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Prevent circular asset hierarchies. When an asset's PARENT is set, walk
# up the parent chain — if the chain ever lands on this asset, the user
# has created a cycle. Reject the save.
#
# Also rejects self-reference (PARENT == self ASSETNUM).
#
# Demonstrates:
#   - VALIDATE event with traversal of a self-referencing hierarchy
#   - Cycle detection with a visited-set guard against pathological data
#   - Bounded loop (max 100 hops) so misconfigured data doesn't hang
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_asset_parent_validate")
_MAX_DEPTH = 100


# =============================================================================
# Helpers
# =============================================================================
def _parent_of(assetnum, siteid):
    if assetnum is None:
        return None
    mxs = MXServer.getMXServer()
    asset_set = None
    try:
        asset_set = mxs.getMboSet("ASSET", mbo.getUserInfo())   # noqa: F821
        sf = SqlFormat(None, "assetnum = :1 and siteid = :2")
        sf.setObject(1, "ASSET", "ASSETNUM", assetnum)
        sf.setObject(2, "ASSET", "SITEID",   siteid)
        asset_set.setWhere(sf.format())
        a = asset_set.getMbo(0)
        if a is None or a.isNull("PARENT"):
            return None
        return a.getString("PARENT")
    finally:
        if asset_set is not None:
            try:
                asset_set.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def validate_no_cycle():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.isNull("PARENT"):                                 # noqa: F821
        return

    self_num = mbo.getString("ASSETNUM") if not mbo.isNull("ASSETNUM") else ""   # noqa: F821
    proposed = mbo.getString("PARENT")                       # noqa: F821
    siteid = mbo.getString("SITEID")                         # noqa: F821

    if proposed == self_num:
        _LOGGER.warn("ASSET %s cannot be its own parent" % self_num)
        raise MXApplicationException("tmg", "assetparentselfreference")

    visited = set()
    current = proposed
    depth = 0
    while current is not None and depth < _MAX_DEPTH:
        if current == self_num:
            _LOGGER.warn("ASSET %s parent chain creates cycle through %s" %
                         (self_num, proposed))
            raise MXApplicationException("tmg", "assetparentcycle")
        if current in visited:
            _LOGGER.warn("Pre-existing cycle detected at ASSET %s — rejecting save" % current)
            raise MXApplicationException("tmg", "assetparentcycle")
        visited.add(current)
        current = _parent_of(current, siteid)
        depth += 1

    if depth >= _MAX_DEPTH:
        _LOGGER.warn("ASSET parent chain exceeded depth limit %d" % _MAX_DEPTH)
        raise MXApplicationException("tmg", "assetparentchaintoodeep")


validate_no_cycle()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_ASSET_PARENT_VALIDATE",
    "description": "Reject circular ASSET parent hierarchies and self-references.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_ASSET_PARENT_VALIDATE",
        "launchPointType": "ATTRIBUTE",
        "active": True,
        "objectName": "ASSET",
        "attributeName": "PARENT",
        "events": {"validate": True},
        "description": "Prevent ASSET parent cycles."
    }]
}
