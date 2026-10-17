# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PUBLISH_WORKORDER_EVENTFILTER
# Launch Point Name: TMG_PUBLISH_WORKORDER_EVENTFILTER
# Launch Point Type: PUBLISH (Event Filter)
# Channel: TMG_WORKORDER_OUT
# Exit: EVENTFILTER
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Event Filter exit — runs when a WORKORDER row is changed and the publish
# channel must decide whether to enqueue an outbound message at all. Returns
# True (filter the event = SUPPRESS publication) or False (let it publish).
#
# Rules:
#   - Suppress when the change is only to non-publishable fields
#     (LASTUPDATEBY, CHANGEDATE, ROWSTAMP).
#   - Suppress when STATUS == 'WAPPR' (drafts shouldn't reach external systems).
#   - Otherwise, publish.
#
# Demonstrates:
#   - Event filter pattern (return-value driven)
#   - Inspecting changed fields via mbo.isModified() per attribute
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_publish_workorder_eventfilter")
_NON_PUBLISH_FIELDS = ("LASTUPDATEBY", "CHANGEDATE", "ROWSTAMP")


# =============================================================================
# Main
# =============================================================================
def filter_event():
    if mbo is None:                                          # noqa: F821
        return False  # publish

    # Drafts never publish
    if not mbo.isNull("STATUS") and mbo.getString("STATUS") == "WAPPR":   # noqa: F821
        _LOGGER.debug("Suppress publish: WAPPR status WONUM=%s" %
                      mbo.getString("WONUM"))                # noqa: F821
        return True  # suppress

    # If only non-publishable fields changed, suppress
    any_meaningful_change = False
    for attr in mbo.getThisMboSet().getMboSetInfo().getAttributes():
        name = attr.getName().upper()
        if name in _NON_PUBLISH_FIELDS:
            continue
        try:
            if mbo.isModified(name):
                any_meaningful_change = True
                break
        except Exception:
            continue

    if not any_meaningful_change:
        _LOGGER.debug("Suppress publish: only non-publishable fields modified")
        return True

    return False


# Event filter scripts return their decision via the implicit `eventResponse`
# variable (or by setting result on irData). Maximo expects the filter
# script to populate this.
try:
    eventResponse = filter_event()                           # noqa: F821, F841
except NameError:
    # Some Maximo runtimes use a different signaling mechanism; fall back
    # to setting on irData.
    try:
        irData.setStop(filter_event())                       # noqa: F821
    except Exception:
        pass


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_PUBLISH_WORKORDER_EVENTFILTER",
    "description": "Event filter — suppress publication of WAPPR or no-op WORKORDER changes.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PUBLISH_WORKORDER_EVENTFILTER",
        "launchPointType": "PUBLISH",
        "active": True,
        "publishChannel": "TMG_WORKORDER_OUT",
        "exitType": "EVENTFILTER",
        "description": "Decide whether WORKORDER change triggers a publish."
    }]
}
