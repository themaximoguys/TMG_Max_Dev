# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PUBLISH_PO_PROCESSOUT
# Launch Point Name: TMG_PUBLISH_PO_PROCESSOUT
# Launch Point Type: PUBLISH (Process Out)
# Channel: TMG_PO_OUT
# Exit: PROCESSOUT
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Outbound processing exit for Purchase Orders.
#   - Skip publication unless STATUS in ('APPR','CLOSE')
#   - Mask payment terms (TMG_PAYMENTTERMS) — not all external systems
#     should see contractual terms
#   - Skip when VENDOR is internal (transfer orders)
#
# Demonstrates:
#   - Multi-condition skip logic via irData.setStop
#   - Field redaction on outbound payload
#   - Cross-MBO check (vendor type)
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_publish_po_processout")
_PUBLISHABLE_STATUSES = ("APPR", "CLOSE")


# =============================================================================
# Helpers
# =============================================================================
def _is_internal_vendor(vendor):
    if vendor is None or len(vendor.strip()) == 0:
        return False
    mxs = MXServer.getMXServer()
    cs = None
    try:
        cs = mxs.getMboSet("COMPANIES", mbo.getUserInfo())   # noqa: F821
        sf = SqlFormat(None, "company = :1")
        sf.setObject(1, "COMPANIES", "COMPANY", vendor)
        cs.setWhere(sf.format())
        c = cs.getMbo(0)
        if c is None or c.isNull("TYPE"):
            return False
        return c.getString("TYPE").upper() == "INTERNAL"
    finally:
        if cs is not None:
            try:
                cs.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def process_po_outbound():
    if mbo is None:                                          # noqa: F821
        return

    status = mbo.getString("STATUS") if not mbo.isNull("STATUS") else ""   # noqa: F821
    if status not in _PUBLISHABLE_STATUSES:
        _LOGGER.info("Skip PO publish PONUM=%s status=%s" %
                     (mbo.getString("PONUM"), status))       # noqa: F821
        try:
            irData.setStop(True)                             # noqa: F821
        except Exception:
            pass
        return

    vendor = mbo.getString("VENDOR") if not mbo.isNull("VENDOR") else ""   # noqa: F821
    if _is_internal_vendor(vendor):
        _LOGGER.info("Skip PO publish — internal vendor=%s" % vendor)
        try:
            irData.setStop(True)                             # noqa: F821
        except Exception:
            pass
        return

    # Mask payment terms
    try:
        irData.setAsString("TMG_PAYMENTTERMS", "REDACTED")   # noqa: F821
    except Exception:
        pass


process_po_outbound()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_PUBLISH_PO_PROCESSOUT",
    "description": "Outbound PO processing — gate by status, skip internal vendors, mask payment terms.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PUBLISH_PO_PROCESSOUT",
        "launchPointType": "PUBLISH",
        "active": True,
        "publishChannel": "TMG_PO_OUT",
        "exitType": "PROCESSOUT",
        "description": "Outbound PO main processing exit."
    }]
}
