# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PO_STATUS_HANDLER
# Launch Point Name: TMG_PO_STATUS_HANDLER
# Launch Point Type: OBJECT
# Object: PO
# Event: validate (status-change validation)
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Status-handler for Purchase Order. Allowed transitions:
#   WAPPR -> APPR | CAN
#   APPR  -> CLOSE | CAN
#   CLOSE -> (terminal)
#   CAN   -> (terminal)
#
# Additional rule: PO -> APPR requires at least one POLINE.
#
# Demonstrates:
#   - Status-handler with multi-rule validation
#   - Cross-rule precondition (POLINE existence) before status change
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_po_status_handler")

_ALLOWED = {
    "WAPPR": ("APPR", "CAN"),
    "APPR":  ("CLOSE", "CAN"),
    "CLOSE": (),
    "CAN":   (),
}


# =============================================================================
# Helpers
# =============================================================================
def _has_polines():
    poline_set = None
    try:
        poline_set = mbo.getMboSet("POLINE")                 # noqa: F821
        return poline_set.count() > 0
    finally:
        if poline_set is not None:
            try:
                poline_set.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def validate_status():
    if mbo is None or mbo.isNull("STATUS"):                  # noqa: F821
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
        return

    allowed = _ALLOWED.get(old_status, None)
    if allowed is None:
        return

    if new_status not in allowed:
        _LOGGER.warn("Disallowed PO transition %s -> %s on PONUM=%s" %
                     (old_status, new_status, mbo.getString("PONUM")))   # noqa: F821
        raise MXApplicationException("tmg", "postatusnotallowed")

    if new_status == "APPR" and not _has_polines():
        _LOGGER.warn("Cannot approve PONUM=%s with no POLINE rows" %
                     mbo.getString("PONUM"))                 # noqa: F821
        raise MXApplicationException("tmg", "porequirespolines")


validate_status()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_PO_STATUS_HANDLER",
    "description": "Validate PO status transitions and enforce POLINE precondition for APPR.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PO_STATUS_HANDLER",
        "launchPointType": "OBJECT",
        "active": True,
        "objectName": "PO",
        "events": {"validate": True},
        "description": "Validate PO status transitions."
    }]
}
