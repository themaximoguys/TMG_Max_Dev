# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PUBLISH_ASSET_EVENTFILTER
# Launch Point Name: TMG_PUBLISH_ASSET_EVENTFILTER
# Launch Point Type: PUBLISH (Event Filter)
# Channel: TMG_ASSET_OUT
# Exit: EVENTFILTER
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Event Filter for ASSET — only allow outbound publication when one of these
# attributes changed: STATUS, LOCATION, PARENT, PRIORITY, ASSETTAG. All
# other field changes (description text edits, audit fields, etc.) are
# suppressed to keep external system traffic low.
#
# Demonstrates:
#   - Event filter pattern with allowlist of "publishable" fields
#   - mbo.isModified() per attribute
#
# Returns True to suppress, False to publish.
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_publish_asset_eventfilter")
_PUBLISHABLE_FIELDS = ("STATUS", "LOCATION", "PARENT", "PRIORITY", "ASSETTAG")


# =============================================================================
# Main
# =============================================================================
def filter_event():
    if mbo is None:                                          # noqa: F821
        return False

    # New asset → always publish
    if mbo.toBeAdded():                                      # noqa: F821
        return False

    for attr in _PUBLISHABLE_FIELDS:
        try:
            if mbo.isModified(attr):                         # noqa: F821
                return False
        except Exception:
            continue

    _LOGGER.debug("Suppress ASSET publish: no publishable field changed on ASSETNUM=%s" %
                  mbo.getString("ASSETNUM"))                 # noqa: F821
    return True


try:
    eventResponse = filter_event()                           # noqa: F821, F841
except NameError:
    try:
        irData.setStop(filter_event())                       # noqa: F821
    except Exception:
        pass


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_PUBLISH_ASSET_EVENTFILTER",
    "description": "Suppress ASSET publication unless STATUS/LOCATION/PARENT/PRIORITY/ASSETTAG changed.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PUBLISH_ASSET_EVENTFILTER",
        "launchPointType": "PUBLISH",
        "active": True,
        "publishChannel": "TMG_ASSET_OUT",
        "exitType": "EVENTFILTER",
        "description": "Allowlist-based ASSET event filter."
    }]
}
