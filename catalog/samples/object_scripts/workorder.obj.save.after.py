# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_WORKORDER_OBJ_SAVE_AFTER
# Launch Point Name: TMG_WORKORDER_OBJ_SAVE_AFTER
# Launch Point Type: OBJECT
# Object: WORKORDER
# Event: SAVE (after)
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Audit-trail handler for WORKORDER. After every successful save, append a
# row to a custom TMG_WO_AUDIT table summarizing the change. Pure side-effect
# logging — never modifies the parent WORKORDER MBO (already saved).
#
# Demonstrates:
#   - OBJECT SAVE after-event pattern
#   - Adding records to a separate object via getMboServer().getMboSet()
#   - Proper try/finally on MboSet
#   - Detecting NEW vs UPDATE via mbo.toBeAdded()
#
# =============================================================================
# Imports
# =============================================================================
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_workorder_obj_save_after")


# =============================================================================
# Main
# =============================================================================
def write_audit_row():
    if mbo is None:                                          # noqa: F821
        return

    mxs = MXServer.getMXServer()
    user_info = mbo.getUserInfo()                            # noqa: F821
    user_id = user_info.getUserName() if user_info is not None else ""
    action = "ADD" if mbo.toBeAdded() else "UPDATE"          # noqa: F821

    audit_set = None
    try:
        audit_set = mxs.getMboSet("TMG_WO_AUDIT", user_info)
        audit = audit_set.add()
        audit.setValue("WONUM",     mbo.getString("WONUM"))   # noqa: F821
        audit.setValue("SITEID",    mbo.getString("SITEID"))  # noqa: F821
        audit.setValue("ACTIONCD",  action)
        audit.setValue("CHANGEBY",  user_id)
        if not mbo.isNull("STATUS"):                          # noqa: F821
            audit.setValue("WOSTATUS", mbo.getString("STATUS"))  # noqa: F821
        audit_set.save()
        _LOGGER.debug("Wrote TMG_WO_AUDIT row for WONUM=%s action=%s" %
                      (mbo.getString("WONUM"), action))       # noqa: F821
    except Exception as e:                                      # noqa
        _LOGGER.error("Failed to write TMG_WO_AUDIT row: %s" % str(e))
        raise
    finally:
        if audit_set is not None:
            try:
                audit_set.close()
            except Exception as ce:                             # noqa
                _LOGGER.warn("Failed to close audit_set: %s" % str(ce))


write_audit_row()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_WORKORDER_OBJ_SAVE_AFTER",
    "description": "Append audit row to TMG_WO_AUDIT after every WORKORDER save.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_WORKORDER_OBJ_SAVE_AFTER",
        "launchPointType": "OBJECT",
        "active": True,
        "objectName": "WORKORDER",
        "events": {"save": True, "aftersave": True},
        "description": "Write audit log row after WORKORDER save."
    }]
}
