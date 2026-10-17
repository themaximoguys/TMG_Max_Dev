# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PUBLISH_PO_EVENTFILTER
# Launch Point Name: TMG_PUBLISH_PO_EVENTFILTER
# Launch Point Type: PUBLISH (Event Filter)
# Channel: TMG_PO_OUT
# Exit: EVENTFILTER
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Event filter for PO. Only publish on status transitions: WAPPR→APPR,
# APPR→CLOSE, APPR→CAN. Suppresses every other PO change (line edits,
# description tweaks, etc.) so the external system only sees lifecycle
# milestones.
#
# Demonstrates:
#   - Event filter using STATUS old→new comparison
#   - Allowlist of meaningful transitions
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_publish_po_eventfilter")

_MEANINGFUL_TRANSITIONS = {
    ("WAPPR", "APPR"),
    ("APPR",  "CLOSE"),
    ("APPR",  "CAN"),
}


# =============================================================================
# Helpers
# =============================================================================
def _old_status():
    attr = mbo.getMboValue("STATUS")                         # noqa: F821
    if attr is None:
        return None
    try:
        ov = attr.getOriginalValue()
        return ov.asString() if ov is not None else None
    except Exception:
        return None


# =============================================================================
# Main
# =============================================================================
def filter_event():
    if mbo is None:                                          # noqa: F821
        return False
    if mbo.toBeAdded():                                      # noqa: F821
        return True  # never publish raw drafts
    if mbo.isNull("STATUS"):                                 # noqa: F821
        return True

    new = mbo.getString("STATUS")                            # noqa: F821
    old = _old_status()
    if old is None or old == new:
        return True  # no status change → suppress

    if (old, new) in _MEANINGFUL_TRANSITIONS:
        _LOGGER.debug("Publish PO: %s -> %s on PONUM=%s" %
                      (old, new, mbo.getString("PONUM")))    # noqa: F821
        return False

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
    "autoscript": "TMG_PUBLISH_PO_EVENTFILTER",
    "description": "Only publish PO on lifecycle transitions (WAPPR→APPR, APPR→CLOSE, APPR→CAN).",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PUBLISH_PO_EVENTFILTER",
        "launchPointType": "PUBLISH",
        "active": True,
        "publishChannel": "TMG_PO_OUT",
        "exitType": "EVENTFILTER",
        "description": "Status-transition gated PO publication."
    }]
}
