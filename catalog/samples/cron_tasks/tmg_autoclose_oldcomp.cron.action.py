# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_AUTOCLOSE_OLDCOMP.CRON.ACTION
# Launch Point Name: TMG_AUTOCLOSE_OLDCOMP.CRON.ACTION
# Launch Point Type: CRONTASK
# Cron Task Name: TMG_AUTOCLOSE_OLDCOMP
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Auto-CLOSE WORKORDERs that have been in COMP status longer than the
# auto-close window (default 30 days). Uses changeStatus() so any
# status-handler logic still fires. Skips WOs with open invoice or
# financial activity (TMG_HASOPENINV flag).
#
# Demonstrates:
#   - CRONTASK pattern with status transition
#   - changeStatus() invocation from cron context
#   - Per-row error containment so one bad row doesn't kill the batch
#
# =============================================================================
# Imports
# =============================================================================
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory

from java.util import Date


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_autoclose_oldcomp")
_AUTOCLOSE_DAYS = 30
_BATCH_SIZE = 100


# =============================================================================
# Main
# =============================================================================
def run():
    mxs = MXServer.getMXServer()
    user = mxs.getSystemUserInfo()
    wo_set = None
    closed = 0
    skipped = 0
    failed = 0
    try:
        wo_set = mxs.getMboSet("WORKORDER", user)
        wo_set.setWhere(
            "status = 'COMP' "
            "and statusdate < sysdate - " + str(_AUTOCLOSE_DAYS) + " "
            "and (tmg_hasopeninv is null or tmg_hasopeninv = 0)"
        )

        wo = wo_set.moveFirst()
        batch = 0
        while wo is not None:
            try:
                wo.changeStatus("CLOSE", Date(),
                                "Auto-closed by TMG_AUTOCLOSE_OLDCOMP after %d days in COMP" %
                                _AUTOCLOSE_DAYS)
                closed += 1
            except Exception as e:                            # noqa
                _LOGGER.warn("Could not auto-close WONUM=%s: %s" %
                             (wo.getString("WONUM"), str(e)))
                failed += 1

            batch += 1
            if batch >= _BATCH_SIZE:
                wo_set.save()
                batch = 0
            wo = wo_set.moveNext()

        if batch > 0:
            wo_set.save()

        _LOGGER.info("TMG_AUTOCLOSE_OLDCOMP: closed=%d skipped=%d failed=%d" %
                     (closed, skipped, failed))
    except Exception as e:                                    # noqa
        _LOGGER.error("TMG_AUTOCLOSE_OLDCOMP failed: %s" % str(e))
        raise
    finally:
        if wo_set is not None:
            try:
                wo_set.close()
            except Exception:
                pass


run()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_AUTOCLOSE_OLDCOMP.CRON.ACTION",
    "description": "Auto-CLOSE work orders that have been COMP > N days.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_AUTOCLOSE_OLDCOMP.CRON.ACTION",
        "launchPointType": "CRONTASK",
        "active": True,
        "cronTaskName": "TMG_AUTOCLOSE_OLDCOMP",
        "description": "Auto-close stale completed work orders."
    }]
}
