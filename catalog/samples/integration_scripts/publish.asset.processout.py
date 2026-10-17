# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PUBLISH_ASSET_PROCESSOUT
# Launch Point Name: TMG_PUBLISH_ASSET_PROCESSOUT
# Launch Point Type: PUBLISH (Process Out)
# Channel: TMG_ASSET_OUT
# Exit: PROCESSOUT
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Outbound publish-channel exit for ASSET. Skips DECOMMISSIONED assets and
# enriches the message with the parent location's GL account on the way
# out so downstream systems don't need to re-query Maximo.
#
# Demonstrates:
#   - Publish channel exit
#   - Enrichment via related-MBO lookup
#   - Conditional skip via irData
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_publish_asset_outbound")


# =============================================================================
# Helpers
# =============================================================================
def _lookup_glaccount_for_location(user_info, location, siteid):
    if location is None or len(location.strip()) == 0:
        return None
    mxs = MXServer.getMXServer()
    loc_set = None
    try:
        loc_set = mxs.getMboSet("LOCATIONS", user_info)
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
def process_asset_outbound():
    if mbo is None:                                          # noqa: F821
        return

    status = mbo.getString("STATUS") if not mbo.isNull("STATUS") else ""   # noqa: F821
    if status == "DECOMMISSIONED":
        _LOGGER.info("Skipping publish for decommissioned ASSETNUM=%s" %
                     mbo.getString("ASSETNUM"))              # noqa: F821
        try:
            irData.setStop(True)                             # noqa: F821
        except Exception:
            pass
        return

    location = mbo.getString("LOCATION") if not mbo.isNull("LOCATION") else ""   # noqa: F821
    siteid   = mbo.getString("SITEID")                       # noqa: F821

    glaccount = _lookup_glaccount_for_location(mbo.getUserInfo(),            # noqa: F821
                                               location, siteid)
    if glaccount is not None:
        try:
            irData.setAsString("LOC_GLACCOUNT", glaccount)   # noqa: F821
        except Exception:
            _LOGGER.debug("LOC_GLACCOUNT not in outbound schema — skipping enrichment")


process_asset_outbound()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_PUBLISH_ASSET_PROCESSOUT",
    "description": "Filter decommissioned ASSETs and enrich outbound messages with location GL.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PUBLISH_ASSET_PROCESSOUT",
        "launchPointType": "PUBLISH",
        "active": True,
        "publishChannel": "TMG_ASSET_OUT",
        "exitType": "PROCESSOUT",
        "description": "Outbound ASSET processing exit."
    }]
}
