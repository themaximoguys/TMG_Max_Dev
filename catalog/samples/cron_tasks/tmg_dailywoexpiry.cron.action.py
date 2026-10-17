# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_DAILYWOEXPIRY.CRON.ACTION
# Launch Point Name: TMG_DAILYWOEXPIRY.CRON.ACTION
# Launch Point Type: CRONTASK
# Cron Task Name: TMG_DAILYWOEXPIRY
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Daily cron task that scans WORKORDERs whose target completion date is
# within the next 7 days and writes a notification row per work order.
#
# Cron tasks have NO `mbo` implicit variable — open MboSets via MXServer.
# Use the user info attached to the cron task instance.
#
# Demonstrates:
#   - CRONTASK pattern (no `mbo` variable)
#   - SqlFormat with date arithmetic
#   - Iterating large MboSets with moveFirst/moveNext
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.security import UserInfo
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory

from java.util import Calendar


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_dailywoexpiry")
_LOOKAHEAD_DAYS = 7


# =============================================================================
# Helpers
# =============================================================================
def _user_info():
    mxs = MXServer.getMXServer()
    return mxs.getSystemUserInfo()


def _cutoff_date():
    cal = Calendar.getInstance()
    cal.add(Calendar.DAY_OF_MONTH, _LOOKAHEAD_DAYS)
    return cal.getTime()


# =============================================================================
# Main
# =============================================================================
def run():
    mxs = MXServer.getMXServer()
    user = _user_info()
    wo_set = None
    notif_set = None
    written = 0
    try:
        wo_set = mxs.getMboSet("WORKORDER", user)
        wo_set.setWhere(
            "status not in ('CLOSE','CAN','COMP') "
            "and targcompdate is not null "
            "and targcompdate <= sysdate + " + str(_LOOKAHEAD_DAYS)
        )

        notif_set = mxs.getMboSet("TMG_WO_NOTIFICATION", user)

        wo = wo_set.moveFirst()
        while wo is not None:
            row = notif_set.add()
            row.setValue("WONUM",       wo.getString("WONUM"))
            row.setValue("SITEID",      wo.getString("SITEID"))
            row.setValue("DUEDATE",     wo.getDate("TARGCOMPDATE"))
            row.setValue("NOTIFYTYPE",  "EXPIRY7D")
            row.setValue("STATUS",      "PENDING")
            written += 1
            wo = wo_set.moveNext()

        if written > 0:
            notif_set.save()
        _LOGGER.info("TMG_DAILYWOEXPIRY: wrote %d notification rows" % written)
    except Exception as e:                                     # noqa
        _LOGGER.error("TMG_DAILYWOEXPIRY failed: %s" % str(e))
        raise
    finally:
        if wo_set is not None:
            try:
                wo_set.close()
            except Exception:
                pass
        if notif_set is not None:
            try:
                notif_set.close()
            except Exception:
                pass


run()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_DAILYWOEXPIRY.CRON.ACTION",
    "description": "Daily scan: write expiry notifications for WOs due within 7 days.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_DAILYWOEXPIRY.CRON.ACTION",
        "launchPointType": "CRONTASK",
        "active": True,
        "cronTaskName": "TMG_DAILYWOEXPIRY",
        "description": "Daily WO expiry notifier."
    }]
}
