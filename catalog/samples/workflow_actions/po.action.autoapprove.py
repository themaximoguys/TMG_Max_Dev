# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PO_ACTION_AUTOAPPROVE
# Launch Point Name: TMG_PO_ACTION_AUTOAPPROVE
# Launch Point Type: ACTION
# Object: PO
# Action: TMG_AUTOAPPROVE
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Workflow action: at the conditional auto-approve branch, advance PO
# status to APPR if total cost is under the configured threshold AND
# vendor is in good standing. Otherwise leaves status untouched (the
# workflow continues to the manual-approval branch).
#
# Demonstrates:
#   - ACTION launch point invoked from Workflow conditional node
#   - Conditional status change via psdi.app.po.PO.changeStatus
#   - Cross-MBO lookup
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.util.logging import MXLoggerFactory

from java.util import Date


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_po_action_autoapprove")
_AUTO_APPROVE_THRESHOLD = 5000.0


# =============================================================================
# Helpers
# =============================================================================
def _vendor_in_good_standing(vendor):
    if vendor is None or len(vendor.strip()) == 0:
        return False
    comp_set = None
    try:
        comp_set = mbo.getMboSet("$tmg_vendor_lookup",       # noqa: F821
                                 "COMPANIES",
                                 "company = :1")
        comp_set.setQbe("COMPANY", vendor)
        comp = comp_set.getMbo(0)
        if comp is None:
            return False
        if comp.isNull("DISABLED"):
            return True
        return not comp.getBoolean("DISABLED")
    finally:
        if comp_set is not None:
            try:
                comp_set.close()
            except Exception:
                pass


def _po_total():
    poline_set = None
    total = 0.0
    try:
        poline_set = mbo.getMboSet("POLINE")                 # noqa: F821
        line = poline_set.moveFirst()
        while line is not None:
            if not line.isNull("LINECOST"):
                total += line.getDouble("LINECOST")
            line = poline_set.moveNext()
    finally:
        if poline_set is not None:
            try:
                poline_set.close()
            except Exception:
                pass
    return total


# =============================================================================
# Main
# =============================================================================
def maybe_auto_approve():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.isNull("STATUS"):                                 # noqa: F821
        return
    if mbo.getString("STATUS") != "WAPPR":                   # noqa: F821
        return  # only apply at the approval gate

    total = _po_total()
    vendor = mbo.getString("VENDOR") if not mbo.isNull("VENDOR") else ""   # noqa: F821

    if total <= _AUTO_APPROVE_THRESHOLD and _vendor_in_good_standing(vendor):
        mbo.changeStatus("APPR", Date(), "Auto-approved by TMG_AUTOAPPROVE")  # noqa: F821
        _LOGGER.info("Auto-approved PONUM=%s total=%s vendor=%s" %
                     (mbo.getString("PONUM"), total, vendor))                 # noqa: F821
    else:
        _LOGGER.debug("PO %s left for manual approval (total=%s, vendor=%s)" %
                      (mbo.getString("PONUM"), total, vendor))                # noqa: F821


maybe_auto_approve()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_PO_ACTION_AUTOAPPROVE",
    "description": "Auto-approve PO when below threshold and vendor is active.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PO_ACTION_AUTOAPPROVE",
        "launchPointType": "ACTION",
        "active": True,
        "objectName": "PO",
        "actionName": "TMG_AUTOAPPROVE",
        "description": "Workflow conditional auto-approval."
    }]
}
