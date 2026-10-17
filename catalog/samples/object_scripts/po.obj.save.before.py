# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PO_OBJ_SAVE_BEFORE
# Launch Point Name: TMG_PO_OBJ_SAVE_BEFORE
# Launch Point Type: OBJECT
# Object: PO
# Event: SAVE (before)
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Pre-save validation for Purchase Orders. Aggregates POLINE totals and
# rejects when total exceeds the company-level approval threshold defined
# in TMG_COMPANYLIMITS.
#
# Demonstrates:
#   - OBJECT SAVE before-event
#   - Iterating a child relationship (POLINE)
#   - Cross-MBO lookup via SqlFormat
#   - Proper MboSet close in finally
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_po_obj_save_before")


# =============================================================================
# Helpers
# =============================================================================
def _sum_poline_totals():
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
            except Exception as ce:                            # noqa
                _LOGGER.warn("Failed to close poline_set: %s" % str(ce))
    return total


def _get_company_limit(company, siteid):
    mxs = MXServer.getMXServer()
    limits_set = None
    try:
        limits_set = mxs.getMboSet("TMG_COMPANYLIMITS",
                                   mbo.getUserInfo())        # noqa: F821
        sf = SqlFormat(mbo, "company = :1 and siteid = :2")  # noqa: F821
        sf.setObject(1, "TMG_COMPANYLIMITS", "COMPANY", company)
        sf.setObject(2, "TMG_COMPANYLIMITS", "SITEID",  siteid)
        limits_set.setWhere(sf.format())
        first = limits_set.getMbo(0)
        if first is None or first.isNull("MAXAMOUNT"):
            return None
        return first.getDouble("MAXAMOUNT")
    finally:
        if limits_set is not None:
            try:
                limits_set.close()
            except Exception as ce:                            # noqa
                _LOGGER.warn("Failed to close limits_set: %s" % str(ce))


# =============================================================================
# Main
# =============================================================================
def validate_po_save():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.isNull("VENDOR"):                                 # noqa: F821
        return  # company-limit lookup needs VENDOR

    total = _sum_poline_totals()
    company = mbo.getString("VENDOR")                        # noqa: F821
    siteid  = mbo.getString("SITEID")                        # noqa: F821

    limit = _get_company_limit(company, siteid)
    if limit is None:
        _LOGGER.debug("No TMG_COMPANYLIMITS row for %s/%s — skipping check" %
                      (company, siteid))
        return

    if total > limit:
        _LOGGER.warn("PO total %s exceeds company limit %s for vendor=%s" %
                     (total, limit, company))
        raise MXApplicationException("tmg", "poexceedscompanylimit")


validate_po_save()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_PO_OBJ_SAVE_BEFORE",
    "description": "Reject PO when total exceeds vendor's TMG_COMPANYLIMITS.MAXAMOUNT.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PO_OBJ_SAVE_BEFORE",
        "launchPointType": "OBJECT",
        "active": True,
        "objectName": "PO",
        "events": {"save": True, "beforesave": True},
        "description": "Cap PO total against vendor limit."
    }]
}
