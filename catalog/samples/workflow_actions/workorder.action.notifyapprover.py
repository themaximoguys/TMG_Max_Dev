# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_WORKORDER_ACTION_NOTIFYAPPROVER
# Launch Point Name: TMG_WORKORDER_ACTION_NOTIFYAPPROVER
# Launch Point Type: ACTION
# Object: WORKORDER
# Action: TMG_NOTIFYAPPROVER
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Workflow action: when WORKORDER reaches the approval node in a workflow
# process, send a notification to the configured approver group leader.
# Invoked by a Workflow Action node referencing TMG_NOTIFYAPPROVER.
#
# Demonstrates:
#   - ACTION launch point invoked from a Workflow node
#   - Lookup of approver group via SqlFormat
#   - Defensive null handling for missing config
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_workorder_action_notifyapprover")


# =============================================================================
# Main
# =============================================================================
def notify_approver():
    if mbo is None:                                          # noqa: F821
        return

    mxs = MXServer.getMXServer()
    user_info = mbo.getUserInfo()                            # noqa: F821

    grp = None
    grp_set = None
    try:
        grp_set = mxs.getMboSet("PERSONGROUP", user_info)
        sf = SqlFormat(None, "persongroup = :1")
        sf.setObject(1, "PERSONGROUP", "PERSONGROUP", "TMG_WO_APPROVERS")
        grp_set.setWhere(sf.format())
        grp = grp_set.getMbo(0)
        if grp is None:
            _LOGGER.warn("TMG_WO_APPROVERS group missing — cannot notify")
            return
    finally:
        if grp_set is not None:
            try:
                grp_set.close()
            except Exception:
                pass

    notif_set = None
    try:
        notif_set = mxs.getMboSet("TMG_WO_NOTIFICATION", user_info)
        row = notif_set.add()
        row.setValue("WONUM",      mbo.getString("WONUM"))    # noqa: F821
        row.setValue("SITEID",     mbo.getString("SITEID"))   # noqa: F821
        row.setValue("PERSONGROUP", grp.getString("PERSONGROUP"))
        row.setValue("NOTIFYTYPE", "WFAPPROVE")
        row.setValue("STATUS",     "PENDING")
        notif_set.save()
        _LOGGER.info("Workflow approver notification added for WONUM=%s" %
                     mbo.getString("WONUM"))                  # noqa: F821
    finally:
        if notif_set is not None:
            try:
                notif_set.close()
            except Exception:
                pass


notify_approver()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_WORKORDER_ACTION_NOTIFYAPPROVER",
    "description": "Workflow-invoked: notify TMG_WO_APPROVERS group on WO at approval node.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_WORKORDER_ACTION_NOTIFYAPPROVER",
        "launchPointType": "ACTION",
        "active": True,
        "objectName": "WORKORDER",
        "actionName": "TMG_NOTIFYAPPROVER",
        "description": "Workflow approval-node notification."
    }]
}
