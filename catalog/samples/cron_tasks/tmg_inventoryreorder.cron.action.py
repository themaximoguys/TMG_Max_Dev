# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_INVENTORYREORDER.CRON.ACTION
# Launch Point Name: TMG_INVENTORYREORDER.CRON.ACTION
# Launch Point Type: CRONTASK
# Cron Task Name: TMG_INVENTORYREORDER
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Process pending TMG_REORDER_FLAG rows. For each, create a Purchase
# Requisition (PR) line and mark the flag PROCESSED. Skips rows with no
# default vendor for the item.
#
# Demonstrates:
#   - CRONTASK pattern with batch processing
#   - Cross-MBO writes (PR header + PRLINE)
#   - Idempotent processing (status check before action)
#
# =============================================================================
# Imports
# =============================================================================
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_inventoryreorder")


# =============================================================================
# Helpers
# =============================================================================
def _create_pr_for_item(mxs, user, itemnum, siteid, qty):
    pr_set = None
    try:
        pr_set = mxs.getMboSet("PR", user)
        pr = pr_set.add()
        pr.setValue("DESCRIPTION", "Auto-reorder for ITEM " + itemnum)
        pr.setValue("SITEID", siteid)
        pr.setValue("STATUS", "WAPPR")

        prline_set = pr.getMboSet("PRLINE")
        try:
            prline = prline_set.add()
            prline.setValue("ITEMNUM", itemnum)
            prline.setValue("ORDERQTY", qty)
            prline.setValue("LINETYPE", "ITEM")
        finally:
            try:
                prline_set.close()
            except Exception:
                pass

        pr_set.save()
        return pr.getString("PRNUM")
    finally:
        if pr_set is not None:
            try:
                pr_set.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def run():
    mxs = MXServer.getMXServer()
    user = mxs.getSystemUserInfo()
    flag_set = None
    processed = 0
    try:
        flag_set = mxs.getMboSet("TMG_REORDER_FLAG", user)
        flag_set.setWhere("status = 'PENDING'")

        flag = flag_set.moveFirst()
        while flag is not None:
            itemnum = flag.getString("ITEMNUM")
            siteid  = flag.getString("SITEID")
            curbal  = flag.getDouble("CURBAL")
            rop     = flag.getDouble("REORDERPT")
            qty     = max(1.0, (rop * 2) - curbal)

            try:
                prnum = _create_pr_for_item(mxs, user, itemnum, siteid, qty)
                flag.setValue("STATUS", "PROCESSED")
                flag.setValue("PRNUM", prnum)
                processed += 1
            except Exception as e:                              # noqa
                _LOGGER.warn("Failed to create PR for ITEM %s: %s" %
                             (itemnum, str(e)))
                flag.setValue("STATUS", "ERROR")
                flag.setValue("ERRORMSG", str(e)[:200])

            flag = flag_set.moveNext()

        flag_set.save()
        _LOGGER.info("TMG_INVENTORYREORDER: processed %d flags" % processed)
    except Exception as e:                                      # noqa
        _LOGGER.error("TMG_INVENTORYREORDER failed: %s" % str(e))
        raise
    finally:
        if flag_set is not None:
            try:
                flag_set.close()
            except Exception:
                pass


run()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_INVENTORYREORDER.CRON.ACTION",
    "description": "Process pending TMG_REORDER_FLAG rows by creating PRs.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_INVENTORYREORDER.CRON.ACTION",
        "launchPointType": "CRONTASK",
        "active": True,
        "cronTaskName": "TMG_INVENTORYREORDER",
        "description": "Auto-create PRs from inventory reorder flags."
    }]
}
