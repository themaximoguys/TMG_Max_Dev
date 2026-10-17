# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_EMAILNOTIFICATIONS.CRON.ACTION
# Launch Point Name: TMG_EMAILNOTIFICATIONS.CRON.ACTION
# Launch Point Type: CRONTASK
# Cron Task Name: TMG_EMAILNOTIFICATIONS
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Daily digest cron task. Reads PENDING TMG_WO_NOTIFICATION rows, groups by
# REPORTEDBY person, and sends one email per person via Maximo's CommHelper
# / CommTemplate API.
#
# Demonstrates:
#   - CRONTASK pattern
#   - Aggregation/grouping in Jython 2.7
#   - Email send via psdi.common.commlog.CommLogSetRemote (stubbed; users
#     should wire to a real CommTemplate per their environment)
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_emailnotifications")
_COMM_TEMPLATE = "TMG_WOEXPIRY"


# =============================================================================
# Helpers
# =============================================================================
def _resolve_email(user_info, person_id):
    if person_id is None or len(person_id.strip()) == 0:
        return None
    mxs = MXServer.getMXServer()
    person_set = None
    try:
        person_set = mxs.getMboSet("PERSON", user_info)
        sf = SqlFormat(None, "personid = :1")
        sf.setObject(1, "PERSON", "PERSONID", person_id)
        person_set.setWhere(sf.format())
        person = person_set.getMbo(0)
        if person is None or person.isNull("PRIMARYEMAIL"):
            return None
        return person.getString("PRIMARYEMAIL")
    finally:
        if person_set is not None:
            try:
                person_set.close()
            except Exception:
                pass


def _send_digest(user_info, person_id, wonum_list):
    """Stub: real implementation would invoke CommTemplate.sendMessage() with
    bound recipients. Leaving as a log line keeps the example portable across
    environments without a configured comm template."""
    email = _resolve_email(user_info, person_id)
    if not email:
        _LOGGER.info("Skipping digest for %s — no email on file" % person_id)
        return False
    _LOGGER.info("DIGEST [%s -> %s] WOs=%s" %
                 (person_id, email, ",".join(wonum_list)))
    return True


# =============================================================================
# Main
# =============================================================================
def run():
    mxs = MXServer.getMXServer()
    user = mxs.getSystemUserInfo()
    notif_set = None
    sent_for = 0
    try:
        notif_set = mxs.getMboSet("TMG_WO_NOTIFICATION", user)
        notif_set.setWhere("status = 'PENDING' and notifytype = 'EXPIRY7D'")

        # Group by REPORTEDBY (looked up from WORKORDER each row)
        groups = {}
        notif = notif_set.moveFirst()
        while notif is not None:
            wonum  = notif.getString("WONUM")
            siteid = notif.getString("SITEID")

            wo_set = mxs.getMboSet("WORKORDER", user)
            try:
                sf = SqlFormat(None, "wonum = :1 and siteid = :2")
                sf.setObject(1, "WORKORDER", "WONUM",  wonum)
                sf.setObject(2, "WORKORDER", "SITEID", siteid)
                wo_set.setWhere(sf.format())
                wo = wo_set.getMbo(0)
                rep = wo.getString("REPORTEDBY") if wo is not None and not wo.isNull("REPORTEDBY") else "UNKNOWN"
            finally:
                try:
                    wo_set.close()
                except Exception:
                    pass

            groups.setdefault(rep, []).append(wonum)
            notif.setValue("STATUS", "SENT")
            notif = notif_set.moveNext()

        for rep, wonums in groups.iteritems():
            if _send_digest(user, rep, wonums):
                sent_for += 1

        notif_set.save()
        _LOGGER.info("TMG_EMAILNOTIFICATIONS: dispatched digests to %d users" % sent_for)
    except Exception as e:                                     # noqa
        _LOGGER.error("TMG_EMAILNOTIFICATIONS failed: %s" % str(e))
        raise
    finally:
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
    "autoscript": "TMG_EMAILNOTIFICATIONS.CRON.ACTION",
    "description": "Group pending notifications by user and send daily email digests.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_EMAILNOTIFICATIONS.CRON.ACTION",
        "launchPointType": "CRONTASK",
        "active": True,
        "cronTaskName": "TMG_EMAILNOTIFICATIONS",
        "description": "Daily WO expiry digest dispatcher."
    }]
}
