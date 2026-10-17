# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_ARCHIVEOLDRECORDS.CRON.ACTION
# Launch Point Name: TMG_ARCHIVEOLDRECORDS.CRON.ACTION
# Launch Point Type: CRONTASK
# Cron Task Name: TMG_ARCHIVEOLDRECORDS
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Archive WORKORDERs that have been CLOSED for more than the retention
# window (default 365 days) by copying them to TMG_WO_ARCHIVE and flagging
# the source row as ARCHIVED. Does NOT delete source rows — that is a
# separate operational concern.
#
# Demonstrates:
#   - CRONTASK with retention window logic
#   - Copy-to-archive pattern across two MBOs
#   - Batched commit every N rows to avoid long-running transactions
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_archiveoldrecords")
_RETENTION_DAYS = 365
_BATCH_SIZE = 200


# =============================================================================
# Helpers
# =============================================================================
def _copy_to_archive(wo, archive_set):
    arc = archive_set.add()
    arc.setValue("WONUM",       wo.getString("WONUM"))
    arc.setValue("SITEID",      wo.getString("SITEID"))
    arc.setValue("DESCRIPTION", wo.getString("DESCRIPTION"))
    arc.setValue("WOSTATUS",    wo.getString("STATUS"))
    if not wo.isNull("STATUSDATE"):
        arc.setValue("STATUSDATE", wo.getDate("STATUSDATE"))
    if not wo.isNull("REPORTDATE"):
        arc.setValue("REPORTDATE", wo.getDate("REPORTDATE"))
    arc.setValue("ARCHIVED",    True)


# =============================================================================
# Main
# =============================================================================
def run():
    mxs = MXServer.getMXServer()
    user = mxs.getSystemUserInfo()
    wo_set = None
    archive_set = None
    archived = 0
    try:
        wo_set = mxs.getMboSet("WORKORDER", user)
        wo_set.setWhere(
            "status = 'CLOSE' "
            "and statusdate < sysdate - " + str(_RETENTION_DAYS) + " "
            "and (tmg_archived is null or tmg_archived = 0)"
        )
        archive_set = mxs.getMboSet("TMG_WO_ARCHIVE", user)

        wo = wo_set.moveFirst()
        batch = 0
        while wo is not None:
            _copy_to_archive(wo, archive_set)
            wo.setValue("TMG_ARCHIVED", True)
            archived += 1
            batch += 1
            if batch >= _BATCH_SIZE:
                archive_set.save()
                wo_set.save()
                batch = 0
            wo = wo_set.moveNext()

        if batch > 0:
            archive_set.save()
            wo_set.save()

        _LOGGER.info("TMG_ARCHIVEOLDRECORDS: archived %d work orders" % archived)
    except Exception as e:                                     # noqa
        _LOGGER.error("TMG_ARCHIVEOLDRECORDS failed: %s" % str(e))
        raise
    finally:
        if wo_set is not None:
            try:
                wo_set.close()
            except Exception:
                pass
        if archive_set is not None:
            try:
                archive_set.close()
            except Exception:
                pass


run()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_ARCHIVEOLDRECORDS.CRON.ACTION",
    "description": "Archive WORKORDERs closed > retention window into TMG_WO_ARCHIVE.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_ARCHIVEOLDRECORDS.CRON.ACTION",
        "launchPointType": "CRONTASK",
        "active": True,
        "cronTaskName": "TMG_ARCHIVEOLDRECORDS",
        "description": "Archive old closed work orders."
    }]
}
