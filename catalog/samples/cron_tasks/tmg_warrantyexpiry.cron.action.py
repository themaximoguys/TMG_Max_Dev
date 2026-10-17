# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_WARRANTYEXPIRY.CRON.ACTION
# Launch Point Name: TMG_WARRANTYEXPIRY.CRON.ACTION
# Launch Point Type: CRONTASK
# Cron Task Name: TMG_WARRANTYEXPIRY
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Daily scan: flag ASSETs whose TMG_WARRANTYEXPDATE falls within the
# warning window (default 30 days). Writes a row to TMG_ASSET_NOTIFICATION
# so a downstream digest job can email the asset owner.
#
# Demonstrates:
#   - CRONTASK pattern
#   - Date-window filter via SqlFormat / inline SQL date arithmetic
#   - Avoid duplicate notifications by checking already-pending rows
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_warrantyexpiry")
_WARN_DAYS = 30


# =============================================================================
# Helpers
# =============================================================================
def _already_notified(notif_set, assetnum, siteid):
    notif_set.reset()
    sf = SqlFormat(None,
                   "assetnum = :1 and siteid = :2 "
                   "and notifytype = :3 and status = :4")
    sf.setObject(1, "TMG_ASSET_NOTIFICATION", "ASSETNUM",   assetnum)
    sf.setObject(2, "TMG_ASSET_NOTIFICATION", "SITEID",     siteid)
    sf.setObject(3, "TMG_ASSET_NOTIFICATION", "NOTIFYTYPE", "WARRANTY")
    sf.setObject(4, "TMG_ASSET_NOTIFICATION", "STATUS",     "PENDING")
    notif_set.setWhere(sf.format())
    return notif_set.count() > 0


# =============================================================================
# Main
# =============================================================================
def run():
    mxs = MXServer.getMXServer()
    user = mxs.getSystemUserInfo()
    asset_set = None
    notif_set = None
    flagged = 0
    skipped = 0
    try:
        asset_set = mxs.getMboSet("ASSET", user)
        asset_set.setWhere(
            "status not in ('DECOMMISSIONED','RETIRED') "
            "and tmg_warrantyexpdate is not null "
            "and tmg_warrantyexpdate <= sysdate + " + str(_WARN_DAYS) + " "
            "and tmg_warrantyexpdate >= sysdate"
        )

        notif_set = mxs.getMboSet("TMG_ASSET_NOTIFICATION", user)

        a = asset_set.moveFirst()
        while a is not None:
            assetnum = a.getString("ASSETNUM")
            siteid   = a.getString("SITEID")

            if _already_notified(notif_set, assetnum, siteid):
                skipped += 1
            else:
                row = notif_set.add()
                row.setValue("ASSETNUM",   assetnum)
                row.setValue("SITEID",     siteid)
                row.setValue("EXPDATE",    a.getDate("TMG_WARRANTYEXPDATE"))
                row.setValue("NOTIFYTYPE", "WARRANTY")
                row.setValue("STATUS",     "PENDING")
                flagged += 1

            a = asset_set.moveNext()

        if flagged > 0:
            notif_set.save()
        _LOGGER.info("TMG_WARRANTYEXPIRY: flagged=%d skipped=%d (already pending)" %
                     (flagged, skipped))
    except Exception as e:                                    # noqa
        _LOGGER.error("TMG_WARRANTYEXPIRY failed: %s" % str(e))
        raise
    finally:
        if asset_set is not None:
            try:
                asset_set.close()
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
    "autoscript": "TMG_WARRANTYEXPIRY.CRON.ACTION",
    "description": "Flag assets within warranty-expiration warning window.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_WARRANTYEXPIRY.CRON.ACTION",
        "launchPointType": "CRONTASK",
        "active": True,
        "cronTaskName": "TMG_WARRANTYEXPIRY",
        "description": "Asset warranty expiry watcher."
    }]
}
