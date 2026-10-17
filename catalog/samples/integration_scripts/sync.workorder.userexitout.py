# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_SYNC_WORKORDER_USEREXITOUT
# Launch Point Name: TMG_SYNC_WORKORDER_USEREXITOUT
# Launch Point Type: SUBSCRIBE (User Exit Out)
# Service: TMG_WORKORDER_IN
# Exit: USEREXITOUT
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# User Exit Out (post-processing) — runs AFTER the inbound MBO has been
# saved. Use this for side-effects that depend on the MBO existing
# (audit log, downstream notifications, queueing follow-on work).
#
# Action: write a row to TMG_INBOUND_AUDIT capturing the source system
# and timestamp.
#
# Demonstrates:
#   - User Exit Out pattern (post-save)
#   - Reading inbound metadata via irData.getCurrentData
#   - Writing to a side-table in same transaction
#
# =============================================================================
# Imports
# =============================================================================
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory

from java.util import Date


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_sync_workorder_userexitout")


# =============================================================================
# Main
# =============================================================================
def write_inbound_audit():
    if mbo is None:                                          # noqa: F821
        return

    source_sys = ""
    try:
        source_sys = irData.getCurrentData("EXTSYSNAME") or ""   # noqa: F821
    except Exception:
        pass

    mxs = MXServer.getMXServer()
    audit_set = None
    try:
        audit_set = mxs.getMboSet("TMG_INBOUND_AUDIT", mbo.getUserInfo())   # noqa: F821
        row = audit_set.add()
        row.setValue("OBJECTNAME",  "WORKORDER")
        row.setValue("RECORDKEY",   mbo.getString("WONUM"))   # noqa: F821
        row.setValue("SITEID",      mbo.getString("SITEID"))  # noqa: F821
        row.setValue("EXTSYSNAME",  source_sys)
        row.setValue("RECEIVEDDATE", Date())
        row.setValue("STATUS",      "PROCESSED")
        audit_set.save()
        _LOGGER.debug("Audit row written for inbound WONUM=%s from %s" %
                      (mbo.getString("WONUM"), source_sys))   # noqa: F821
    except Exception as e:                                    # noqa
        _LOGGER.error("Failed to write inbound audit row: %s" % str(e))
        raise
    finally:
        if audit_set is not None:
            try:
                audit_set.close()
            except Exception:
                pass


write_inbound_audit()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_SYNC_WORKORDER_USEREXITOUT",
    "description": "Post-save audit row for inbound WORKORDER messages.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_SYNC_WORKORDER_USEREXITOUT",
        "launchPointType": "SUBSCRIBE",
        "active": True,
        "enterpriseService": "TMG_WORKORDER_IN",
        "exitType": "USEREXITOUT",
        "description": "Inbound WO post-processing exit."
    }]
}
