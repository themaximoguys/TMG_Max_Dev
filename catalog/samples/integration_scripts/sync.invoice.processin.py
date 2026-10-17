# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_SYNC_INVOICE_PROCESSIN
# Launch Point Name: TMG_SYNC_INVOICE_PROCESSIN
# Launch Point Type: SUBSCRIBE (Process In)
# Service: TMG_INVOICE_IN
# Exit: PROCESSIN
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Inbound enterprise-service exit for INVOICE. Performs:
#   1. Reject the message (raise MXApplicationException) if VENDOR is not
#      registered in COMPANIES.
#   2. Set TMG_RECEIVEDDATE to the current timestamp.
#   3. If TOTALPRECTAX is missing, compute it from INVOICELINE rows.
#
# Demonstrates:
#   - Enterprise service inbound exit pattern
#   - Validation -> rejection via exception
#   - Aggregation across child object set
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory

from java.util import Date


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_sync_invoice_inbound")


# =============================================================================
# Helpers
# =============================================================================
def _vendor_exists(vendor):
    if vendor is None or len(vendor.strip()) == 0:
        return False
    mxs = MXServer.getMXServer()
    comp_set = None
    try:
        comp_set = mxs.getMboSet("COMPANIES", mbo.getUserInfo())   # noqa: F821
        sf = SqlFormat(None, "company = :1")
        sf.setObject(1, "COMPANIES", "COMPANY", vendor)
        comp_set.setWhere(sf.format())
        return comp_set.count() > 0
    finally:
        if comp_set is not None:
            try:
                comp_set.close()
            except Exception:
                pass


def _compute_pretax_total():
    line_set = None
    total = 0.0
    try:
        line_set = mbo.getMboSet("INVOICELINE")              # noqa: F821
        ln = line_set.moveFirst()
        while ln is not None:
            if not ln.isNull("LINECOST"):
                total += ln.getDouble("LINECOST")
            ln = line_set.moveNext()
    finally:
        if line_set is not None:
            try:
                line_set.close()
            except Exception:
                pass
    return total


# =============================================================================
# Main
# =============================================================================
def process_inbound_invoice():
    if mbo is None:                                          # noqa: F821
        return

    vendor = mbo.getString("VENDOR") if not mbo.isNull("VENDOR") else ""   # noqa: F821
    if not _vendor_exists(vendor):
        _LOGGER.warn("Inbound invoice rejected — unknown VENDOR=%s" % vendor)
        raise MXApplicationException("tmg", "invoiceunknownvendor")

    mbo.setValue("TMG_RECEIVEDDATE", Date())                 # noqa: F821

    if mbo.isNull("TOTALPRECTAX"):                           # noqa: F821
        total = _compute_pretax_total()
        if total > 0:
            mbo.setValue("TOTALPRECTAX", total)              # noqa: F821
            _LOGGER.info("Computed TOTALPRECTAX=%s for inbound INVOICE" % total)


process_inbound_invoice()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_SYNC_INVOICE_PROCESSIN",
    "description": "Validate vendor + compute pretax total on inbound INVOICE messages.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_SYNC_INVOICE_PROCESSIN",
        "launchPointType": "SUBSCRIBE",
        "active": True,
        "enterpriseService": "TMG_INVOICE_IN",
        "exitType": "PROCESSIN",
        "description": "Inbound INVOICE enterprise service processing exit."
    }]
}
