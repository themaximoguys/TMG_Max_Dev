# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_LOCATIONS_PARENT_VALIDATE
# Launch Point Name: TMG_LOCATIONS_PARENT_VALIDATE
# Launch Point Type: ATTRIBUTE
# Object: LOCATIONS
# Field: PARENT
# Event: VALIDATE
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Prevent circular LOCATIONS hierarchies. Same shape as the asset
# parent-cycle guard but applied to the LOCATIONS object's self-referencing
# PARENT field.
#
# Also enforces that PARENT.SITEID matches LOCATION.SITEID — locations
# cannot have parents in a different site.
#
# Demonstrates:
#   - VALIDATE event traversing a self-referencing hierarchy
#   - Multi-rule validation with early returns
#   - Cross-site precondition check
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_locations_parent_validate")
_MAX_DEPTH = 100


# =============================================================================
# Helpers
# =============================================================================
def _fetch_location(location, siteid):
    mxs = MXServer.getMXServer()
    loc_set = None
    try:
        loc_set = mxs.getMboSet("LOCATIONS", mbo.getUserInfo())   # noqa: F821
        sf = SqlFormat(None, "location = :1 and siteid = :2")
        sf.setObject(1, "LOCATIONS", "LOCATION", location)
        sf.setObject(2, "LOCATIONS", "SITEID",   siteid)
        loc_set.setWhere(sf.format())
        return loc_set.getMbo(0)
    finally:
        if loc_set is not None:
            try:
                loc_set.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def validate_parent():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.isNull("PARENT"):                                 # noqa: F821
        return

    self_loc = mbo.getString("LOCATION") if not mbo.isNull("LOCATION") else ""   # noqa: F821
    siteid   = mbo.getString("SITEID")                       # noqa: F821
    proposed = mbo.getString("PARENT")                       # noqa: F821

    # Self-reference
    if proposed == self_loc:
        raise MXApplicationException("tmg", "locparentselfreference")

    # Parent must exist in the same site
    parent = _fetch_location(proposed, siteid)
    if parent is None:
        _LOGGER.warn("LOCATIONS PARENT %s not found in site %s" % (proposed, siteid))
        raise MXApplicationException("tmg", "locparentnotfoundinsite")

    # Walk the chain
    visited = set()
    current = proposed
    depth = 0
    while current is not None and depth < _MAX_DEPTH:
        if current == self_loc:
            raise MXApplicationException("tmg", "locparentcycle")
        if current in visited:
            raise MXApplicationException("tmg", "locparentcycle")
        visited.add(current)

        next_loc = _fetch_location(current, siteid)
        if next_loc is None or next_loc.isNull("PARENT"):
            return
        current = next_loc.getString("PARENT")
        depth += 1

    if depth >= _MAX_DEPTH:
        raise MXApplicationException("tmg", "locparentchaintoodeep")


validate_parent()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_LOCATIONS_PARENT_VALIDATE",
    "description": "Reject circular LOCATIONS parents and cross-site parent links.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_LOCATIONS_PARENT_VALIDATE",
        "launchPointType": "ATTRIBUTE",
        "active": True,
        "objectName": "LOCATIONS",
        "attributeName": "PARENT",
        "events": {"validate": True},
        "description": "Prevent LOCATIONS parent cycles + enforce same-site rule."
    }]
}
