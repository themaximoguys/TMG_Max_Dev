# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_INVENTORY_OBJ_SAVE_AFTER
# Launch Point Name: TMG_INVENTORY_OBJ_SAVE_AFTER
# Launch Point Type: OBJECT
# Object: INVENTORY
# Event: SAVE (after)
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# After save, if INVENTORY.CURBAL falls at or below REORDERPOINT, log a
# warning and write a TMG_REORDER_FLAG row so a downstream cron task can
# pick it up and create a Purchase Requisition.
#
# Demonstrates:
#   - OBJECT SAVE after-event
#   - Conditional side-effect (no modifications to the parent MBO)
#   - Adding to a separate object set
#
# =============================================================================
# Imports
# =============================================================================
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_inventory_obj_save_after")


# =============================================================================
# Main
# =============================================================================
def flag_reorder_if_below_threshold():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.isNull("CURBAL") or mbo.isNull("REORDERPOINT"):   # noqa: F821
        return

    curbal = mbo.getDouble("CURBAL")                         # noqa: F821
    rop = mbo.getDouble("REORDERPOINT")                      # noqa: F821
    if curbal > rop:
        return

    mxs = MXServer.getMXServer()
    flag_set = None
    try:
        flag_set = mxs.getMboSet("TMG_REORDER_FLAG", mbo.getUserInfo())   # noqa: F821
        flag = flag_set.add()
        flag.setValue("ITEMNUM",  mbo.getString("ITEMNUM"))   # noqa: F821
        flag.setValue("SITEID",   mbo.getString("SITEID"))    # noqa: F821
        flag.setValue("CURBAL",   curbal)
        flag.setValue("REORDERPT", rop)
        flag.setValue("STATUS",   "PENDING")
        flag_set.save()
        _LOGGER.info("Reorder flag created for ITEMNUM=%s curbal=%s rop=%s" %
                     (mbo.getString("ITEMNUM"), curbal, rop))   # noqa: F821
    except Exception as e:                                       # noqa
        _LOGGER.error("Failed to create reorder flag: %s" % str(e))
        raise
    finally:
        if flag_set is not None:
            try:
                flag_set.close()
            except Exception as ce:                              # noqa
                _LOGGER.warn("Failed to close flag_set: %s" % str(ce))


flag_reorder_if_below_threshold()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_INVENTORY_OBJ_SAVE_AFTER",
    "description": "Flag for reorder when INVENTORY.CURBAL <= REORDERPOINT.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_INVENTORY_OBJ_SAVE_AFTER",
        "launchPointType": "OBJECT",
        "active": True,
        "objectName": "INVENTORY",
        "events": {"save": True, "aftersave": True},
        "description": "Trigger reorder flag when stock falls to threshold."
    }]
}
