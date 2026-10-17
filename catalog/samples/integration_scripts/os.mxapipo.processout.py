# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_OS_MXAPIPO_PROCESSOUT
# Launch Point Name: TMG_OS_MXAPIPO_PROCESSOUT
# Launch Point Type: OBJECTSTRUCTURE (Process Out)
# Object Structure: MXAPIPO
# Exit: PROCESSOUT
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# REST-API outbound exit for MXAPIPO. Removes sensitive financial fields
# (TMG_PAYMENTTERMS, TMG_DISCOUNT_PCT) and adds a TMG_LINE_COUNT computed
# field summarizing how many POLINEs the PO has — useful for clients
# that want to render summary widgets without re-fetching child rows.
#
# Demonstrates:
#   - REST response field redaction
#   - Child-row aggregation as a derived response field
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_os_mxapipo_processout")
_REDACT_FIELDS = ("TMG_PAYMENTTERMS", "TMG_DISCOUNT_PCT")


# =============================================================================
# Helpers
# =============================================================================
def _line_count():
    poline_set = None
    try:
        poline_set = mbo.getMboSet("POLINE")                 # noqa: F821
        return poline_set.count()
    finally:
        if poline_set is not None:
            try:
                poline_set.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def process():
    if mbo is None:                                          # noqa: F821
        return

    for fld in _REDACT_FIELDS:
        try:
            irData.setAsString(fld, "REDACTED")              # noqa: F821
        except Exception:
            continue

    try:
        irData.setAsString("TMG_LINE_COUNT", str(_line_count()))   # noqa: F821
    except Exception:
        _LOGGER.debug("TMG_LINE_COUNT not in OS schema")


process()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_OS_MXAPIPO_PROCESSOUT",
    "description": "Object Structure PO REST response: redact financial fields, add line count.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_OS_MXAPIPO_PROCESSOUT",
        "launchPointType": "OBJECTSTRUCTURE",
        "active": True,
        "objectStructure": "MXAPIPO",
        "exitType": "PROCESSOUT",
        "description": "MXAPIPO outbound REST processing exit."
    }]
}
