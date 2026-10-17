# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_SYNC_PO_PROCESSIN
# Launch Point Name: TMG_SYNC_PO_PROCESSIN
# Launch Point Type: SUBSCRIBE (Process In)
# Service: TMG_PO_IN
# Exit: PROCESSIN
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Inbound PO processing.
#   - Reject when VENDOR is disabled
#   - Auto-assign BUYER from the per-site default PERSONGROUP if BUYER missing
#   - Default ORDERDATE = today when missing
#
# Demonstrates:
#   - Cross-MBO precondition check
#   - Auto-resolution from configuration table (PERSONGROUP defaults)
#   - Default-fill on inbound
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory

from java.util import Date


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_sync_po_processin")


# =============================================================================
# Helpers
# =============================================================================
def _vendor_disabled(vendor):
    if vendor is None or len(vendor.strip()) == 0:
        return False
    mxs = MXServer.getMXServer()
    s = None
    try:
        s = mxs.getMboSet("COMPANIES", mbo.getUserInfo())    # noqa: F821
        sf = SqlFormat(None, "company = :1")
        sf.setObject(1, "COMPANIES", "COMPANY", vendor)
        s.setWhere(sf.format())
        c = s.getMbo(0)
        if c is None:
            return False
        return not c.isNull("DISABLED") and c.getBoolean("DISABLED")
    finally:
        if s is not None:
            try:
                s.close()
            except Exception:
                pass


def _default_buyer_for_site(siteid):
    mxs = MXServer.getMXServer()
    s = None
    try:
        s = mxs.getMboSet("TMG_BUYER_DEFAULT", mbo.getUserInfo())   # noqa: F821
        sf = SqlFormat(None, "siteid = :1")
        sf.setObject(1, "TMG_BUYER_DEFAULT", "SITEID", siteid)
        s.setWhere(sf.format())
        d = s.getMbo(0)
        if d is None or d.isNull("BUYER"):
            return None
        return d.getString("BUYER")
    finally:
        if s is not None:
            try:
                s.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def process_po_in():
    if mbo is None:                                          # noqa: F821
        return

    vendor = mbo.getString("VENDOR") if not mbo.isNull("VENDOR") else ""   # noqa: F821
    if _vendor_disabled(vendor):
        _LOGGER.warn("Inbound PO rejected — vendor=%s is disabled" % vendor)
        raise MXApplicationException("tmg", "vendordisabled")

    if mbo.isNull("BUYER"):                                  # noqa: F821
        siteid = mbo.getString("SITEID") if not mbo.isNull("SITEID") else ""   # noqa: F821
        b = _default_buyer_for_site(siteid)
        if b is not None:
            mbo.setValue("BUYER", b)                         # noqa: F821

    if mbo.isNull("ORDERDATE"):                              # noqa: F821
        mbo.setValue("ORDERDATE", Date())                    # noqa: F821


process_po_in()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_SYNC_PO_PROCESSIN",
    "description": "Inbound PO: vendor active check, auto-BUYER, default ORDERDATE.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_SYNC_PO_PROCESSIN",
        "launchPointType": "SUBSCRIBE",
        "active": True,
        "enterpriseService": "TMG_PO_IN",
        "exitType": "PROCESSIN",
        "description": "Inbound PO main processing exit."
    }]
}
