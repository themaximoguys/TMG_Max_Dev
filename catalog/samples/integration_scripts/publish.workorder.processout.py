# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PUBLISH_WORKORDER_PROCESSOUT
# Launch Point Name: TMG_PUBLISH_WORKORDER_PROCESSOUT
# Launch Point Type: PUBLISH (Process Out)
# Channel: TMG_WORKORDER_OUT
# Exit: PROCESSOUT
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Outbound publish-channel exit. Decides whether to publish the WORKORDER
# message and applies field masking before transmission.
#
# Rules:
#   1. Skip publication if STATUS in ('CAN','WAPPR') — only published once
#      the work order has progressed past initial draft.
#   2. Skip if HISTORYFLAG = true (historical archives are not republished).
#   3. Mask the LEAD field to "REDACTED" for external systems.
#
# Returning False from this script causes the integration framework to
# skip the message. Returning True (or no explicit return) lets it flow.
#
# Implicit variable for publish channels:
#   - irData (psdi.iface.mic.MaxIfaceConstants.IRDATA): provides
#     getCurrentMbo(), setStop(...) etc.
#   - mbo: when available, the current WORKORDER row being published.
#
# Demonstrates:
#   - Publish channel processing exit pattern
#   - Conditional skip via irData.setStop
#   - Field masking
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_publish_workorder_outbound")
_SKIP_STATUSES = ("CAN", "WAPPR")


# =============================================================================
# Main
# =============================================================================
def process_outbound():
    if mbo is None:                                          # noqa: F821
        return

    status = mbo.getString("STATUS") if not mbo.isNull("STATUS") else ""   # noqa: F821
    if status in _SKIP_STATUSES:
        _LOGGER.info("Skipping publish for WONUM=%s status=%s" %
                     (mbo.getString("WONUM"), status))       # noqa: F821
        try:
            irData.setStop(True)                             # noqa: F821
        except Exception:
            pass
        return

    if not mbo.isNull("HISTORYFLAG") and mbo.getBoolean("HISTORYFLAG"):    # noqa: F821
        _LOGGER.info("Skipping publish for HISTORYFLAG WONUM=%s" %
                     mbo.getString("WONUM"))                 # noqa: F821
        try:
            irData.setStop(True)                             # noqa: F821
        except Exception:
            pass
        return

    # Mask LEAD before transmission
    if not mbo.isNull("LEAD"):                               # noqa: F821
        try:
            irData.setAsString("LEAD", "REDACTED")           # noqa: F821
        except Exception:
            # fallback: set on mbo, knowing it's already in flight
            pass


process_outbound()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_PUBLISH_WORKORDER_PROCESSOUT",
    "description": "Filter and mask outbound WORKORDER publish messages.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PUBLISH_WORKORDER_PROCESSOUT",
        "launchPointType": "PUBLISH",
        "active": True,
        "publishChannel": "TMG_WORKORDER_OUT",
        "exitType": "PROCESSOUT",
        "description": "Outbound WORKORDER processing exit."
    }]
}
