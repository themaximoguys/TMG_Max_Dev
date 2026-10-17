# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_SYNC_WORKORDER_PROCESSIN
# Launch Point Name: TMG_SYNC_WORKORDER_PROCESSIN
# Launch Point Type: SUBSCRIBE (Process In)
# Service: TMG_WORKORDER_IN
# Exit: PROCESSIN
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Inbound WORKORDER processing exit.
#   - Default REPORTDATE to now if missing
#   - Reject inbound WO with status outside the allowed inbound set
#   - Auto-set SITEID from ORGID's primary site when SITEID missing
#
# Demonstrates:
#   - Inbound default-fill
#   - Allowlist validation
#   - Cross-MBO auto-resolution
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory

from java.util import Date


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_sync_workorder_processin")
_ALLOWED_INBOUND_STATUSES = ("WAPPR", "APPR", "INPRG")


# =============================================================================
# Helpers
# =============================================================================
def _primary_site_for_org(orgid):
    if orgid is None or len(orgid.strip()) == 0:
        return None
    mxs = MXServer.getMXServer()
    s = None
    try:
        s = mxs.getMboSet("SITE", mbo.getUserInfo())         # noqa: F821
        sf = SqlFormat(None, "orgid = :1 and active = 1")
        sf.setObject(1, "SITE", "ORGID", orgid)
        s.setWhere(sf.format())
        first = s.getMbo(0)
        if first is None:
            return None
        return first.getString("SITEID")
    finally:
        if s is not None:
            try:
                s.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def process_inbound():
    if mbo is None:                                          # noqa: F821
        return

    if mbo.isNull("REPORTDATE"):                             # noqa: F821
        mbo.setValue("REPORTDATE", Date())                   # noqa: F821

    status = mbo.getString("STATUS") if not mbo.isNull("STATUS") else "WAPPR"   # noqa: F821
    if status not in _ALLOWED_INBOUND_STATUSES:
        _LOGGER.warn("Inbound WO rejected — disallowed status=%s" % status)
        raise MXApplicationException("tmg", "wostatusnotallowedinbound")

    if mbo.isNull("SITEID") and not mbo.isNull("ORGID"):     # noqa: F821
        site = _primary_site_for_org(mbo.getString("ORGID")) # noqa: F821
        if site is not None:
            mbo.setValue("SITEID", site)                     # noqa: F821


process_inbound()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_SYNC_WORKORDER_PROCESSIN",
    "description": "Inbound WORKORDER: default REPORTDATE, validate status, auto-SITEID.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_SYNC_WORKORDER_PROCESSIN",
        "launchPointType": "SUBSCRIBE",
        "active": True,
        "enterpriseService": "TMG_WORKORDER_IN",
        "exitType": "PROCESSIN",
        "description": "Inbound WORKORDER main processing exit."
    }]
}
