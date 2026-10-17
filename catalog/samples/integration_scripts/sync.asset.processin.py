# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_SYNC_ASSET_PROCESSIN
# Launch Point Name: TMG_SYNC_ASSET_PROCESSIN
# Launch Point Type: SUBSCRIBE (Process In)
# Service: TMG_ASSET_IN
# Exit: PROCESSIN
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Inbound ASSET processing.
#   - Reject when SERIALNUM is duplicated within the same site (rotating asset
#     serial uniqueness)
#   - Default STATUS = 'NOT READY' for new assets
#   - Reject when LOCATION is provided but doesn't exist in the site
#
# Demonstrates:
#   - Uniqueness validation via count
#   - Cross-MBO existence check
#   - Defaulting on Add only (toBeAdded guard)
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_sync_asset_processin")


# =============================================================================
# Helpers
# =============================================================================
def _serialnum_in_use(serialnum, siteid, current_assetnum):
    mxs = MXServer.getMXServer()
    s = None
    try:
        s = mxs.getMboSet("ASSET", mbo.getUserInfo())        # noqa: F821
        sf = SqlFormat(None,
                       "serialnum = :1 and siteid = :2 and assetnum != :3")
        sf.setObject(1, "ASSET", "SERIALNUM", serialnum)
        sf.setObject(2, "ASSET", "SITEID",    siteid)
        sf.setObject(3, "ASSET", "ASSETNUM",  current_assetnum or "")
        s.setWhere(sf.format())
        return s.count() > 0
    finally:
        if s is not None:
            try:
                s.close()
            except Exception:
                pass


def _location_exists(location, siteid):
    if location is None:
        return True  # nothing to check
    mxs = MXServer.getMXServer()
    s = None
    try:
        s = mxs.getMboSet("LOCATIONS", mbo.getUserInfo())    # noqa: F821
        sf = SqlFormat(None, "location = :1 and siteid = :2")
        sf.setObject(1, "LOCATIONS", "LOCATION", location)
        sf.setObject(2, "LOCATIONS", "SITEID",   siteid)
        s.setWhere(sf.format())
        return s.count() > 0
    finally:
        if s is not None:
            try:
                s.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def process_asset_in():
    if mbo is None:                                          # noqa: F821
        return

    if mbo.toBeAdded() and mbo.isNull("STATUS"):             # noqa: F821
        mbo.setValue("STATUS", "NOT READY")                  # noqa: F821

    siteid = mbo.getString("SITEID") if not mbo.isNull("SITEID") else ""   # noqa: F821

    if not mbo.isNull("SERIALNUM") and not mbo.isNull("ROTATING") \
            and mbo.getBoolean("ROTATING"):                  # noqa: F821
        sn = mbo.getString("SERIALNUM")                      # noqa: F821
        an = mbo.getString("ASSETNUM") if not mbo.isNull("ASSETNUM") else ""   # noqa: F821
        if _serialnum_in_use(sn, siteid, an):
            _LOGGER.warn("Inbound ASSET rejected — duplicate SERIALNUM=%s in site %s" %
                         (sn, siteid))
            raise MXApplicationException("tmg", "duplicateserialnum")

    if not mbo.isNull("LOCATION"):                           # noqa: F821
        loc = mbo.getString("LOCATION")                      # noqa: F821
        if not _location_exists(loc, siteid):
            _LOGGER.warn("Inbound ASSET rejected — LOCATION %s not found in site %s" %
                         (loc, siteid))
            raise MXApplicationException("tmg", "locationnotfound")


process_asset_in()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_SYNC_ASSET_PROCESSIN",
    "description": "Inbound ASSET: status default, serial uniqueness, location existence checks.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_SYNC_ASSET_PROCESSIN",
        "launchPointType": "SUBSCRIBE",
        "active": True,
        "enterpriseService": "TMG_ASSET_IN",
        "exitType": "PROCESSIN",
        "description": "Inbound ASSET main processing exit."
    }]
}
