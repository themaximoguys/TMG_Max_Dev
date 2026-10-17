# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_WORKORDER_STATUS_HANDLER
# Launch Point Name: TMG_WORKORDER_STATUS_HANDLER
# Launch Point Type: OBJECT
# Object: WORKORDER
# Event: validate (status-change validation)
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Status-handler pattern: validates allowed WORKORDER status transitions
# and prevents disallowed jumps. Maximo invokes the WORKORDER object's
# status-change pipeline; this script wires into the validate event and
# inspects the proposed new status.
#
# Allowed transitions (simplified; production rules typically extend this):
#   WAPPR  -> APPR | CAN
#   APPR   -> INPRG | CAN
#   INPRG  -> COMP | CAN
#   COMP   -> CLOSE
#   CLOSE  -> (terminal)
#   CAN    -> (terminal)
#
# Demonstrates:
#   - Status-handler pattern via OBJECT validate event
#   - Reading proposed status from mbo (already updated at validate time)
#   - Comparing old vs new via getMboValue().getOldValue()
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_workorder_status_handler")

_ALLOWED = {
    "WAPPR": ("APPR", "CAN"),
    "APPR":  ("INPRG", "CAN"),
    "INPRG": ("COMP", "CAN"),
    "COMP":  ("CLOSE",),
    "CLOSE": (),
    "CAN":   (),
}


# =============================================================================
# Main
# =============================================================================
def validate_status_transition():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.isNull("STATUS"):                                 # noqa: F821
        return

    new_status = mbo.getString("STATUS")                     # noqa: F821
    status_attr = mbo.getMboValue("STATUS")                  # noqa: F821
    old_status = None
    if status_attr is not None:
        try:
            ov = status_attr.getOriginalValue()
            old_status = ov.asString() if ov is not None else None
        except Exception:
            old_status = None

    if old_status is None or old_status == new_status:
        return  # initial set or unchanged

    allowed_set = _ALLOWED.get(old_status, None)
    if allowed_set is None:
        _LOGGER.warn("Unknown source status %s on WORKORDER %s" %
                     (old_status, mbo.getString("WONUM")))   # noqa: F821
        return

    if new_status not in allowed_set:
        _LOGGER.warn("Disallowed transition WORKORDER %s: %s -> %s" %
                     (mbo.getString("WONUM"), old_status, new_status))   # noqa: F821
        raise MXApplicationException("tmg", "wostatusnotallowed")


validate_status_transition()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_WORKORDER_STATUS_HANDLER",
    "description": "Reject disallowed WORKORDER status transitions.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_WORKORDER_STATUS_HANDLER",
        "launchPointType": "OBJECT",
        "active": True,
        "objectName": "WORKORDER",
        "events": {"validate": True},
        "description": "Validate WO status transitions."
    }]
}
