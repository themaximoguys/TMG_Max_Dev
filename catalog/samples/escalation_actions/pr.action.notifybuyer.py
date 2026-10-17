# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PR_ACTION_NOTIFYBUYER
# Launch Point Name: TMG_PR_ACTION_NOTIFYBUYER
# Launch Point Type: ACTION
# Object: PR
# Action: TMG_NOTIFYBUYER
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Escalation-invoked action: when a Purchase Requisition has been in
# WAPPR (Waiting on Approval) state for more than the SLA window, write a
# notification row addressed to the buyer of record and a comm log entry.
#
# Demonstrates:
#   - ACTION launch point on PR
#   - Lookup + side-effect-write pattern (no parent MBO modification)
#
# =============================================================================
# Imports
# =============================================================================
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_pr_action_notifybuyer")


# =============================================================================
# Main
# =============================================================================
def notify_buyer():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.isNull("BUYER"):                                  # noqa: F821
        _LOGGER.debug("PR %s has no BUYER — skipping notification" %
                      mbo.getString("PRNUM"))                # noqa: F821
        return

    mxs = MXServer.getMXServer()
    notif_set = None
    try:
        notif_set = mxs.getMboSet("TMG_PR_NOTIFICATION", mbo.getUserInfo())  # noqa: F821
        row = notif_set.add()
        row.setValue("PRNUM",      mbo.getString("PRNUM"))    # noqa: F821
        row.setValue("SITEID",     mbo.getString("SITEID"))   # noqa: F821
        row.setValue("BUYER",      mbo.getString("BUYER"))    # noqa: F821
        row.setValue("NOTIFYTYPE", "WAPPR_SLA")
        row.setValue("STATUS",     "PENDING")
        notif_set.save()
        _LOGGER.info("Buyer-notify row added for PRNUM=%s buyer=%s" %
                     (mbo.getString("PRNUM"), mbo.getString("BUYER")))   # noqa: F821
    except Exception as e:                                      # noqa
        _LOGGER.error("notify_buyer failed: %s" % str(e))
        raise
    finally:
        if notif_set is not None:
            try:
                notif_set.close()
            except Exception:
                pass


notify_buyer()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_PR_ACTION_NOTIFYBUYER",
    "description": "Notify buyer when PR has aged past SLA in WAPPR.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PR_ACTION_NOTIFYBUYER",
        "launchPointType": "ACTION",
        "active": True,
        "objectName": "PR",
        "actionName": "TMG_NOTIFYBUYER",
        "description": "Action invoked by TMG_PR_AGING escalation."
    }]
}
