# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_ABCCLASSIFY.CRON.ACTION
# Launch Point Name: TMG_ABCCLASSIFY.CRON.ACTION
# Launch Point Type: CRONTASK
# Cron Task Name: TMG_ABCCLASSIFY
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Standard ABC inventory classification — re-classify every INVENTORY row
# based on issued usage value (qty * AVGCOST) over the last 12 months:
#   A: top 70% of cumulative usage value
#   B: next 20%
#   C: bottom 10%
#
# Writes the result to INVENTORY.ABCTYPE. Items with zero usage are
# tagged 'C' by convention.
#
# Demonstrates:
#   - CRONTASK pattern with multi-pass aggregation
#   - Sorting / cumulative percentage calculation in Jython 2.7
#   - Bulk update with batched commits
#
# =============================================================================
# Imports
# =============================================================================
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_abcclassify")
_BATCH_SIZE = 250
_A_CUTOFF = 0.70
_B_CUTOFF = 0.90  # A+B together — anything beyond is C


# =============================================================================
# Helpers
# =============================================================================
def _gather_usage(mxs, user):
    """Sum (quantity * unitcost) per (itemnum, location, siteid) over last
    365 days from MATUSETRANS rows. Returns a dict keyed by tuple."""
    usage = {}
    set_ = None
    try:
        set_ = mxs.getMboSet("MATUSETRANS", user)
        set_.setWhere(
            "transdate >= sysdate - 365 "
            "and issuetype in ('ISSUE','RETURN','TRANSFER')"
        )
        row = set_.moveFirst()
        while row is not None:
            itemnum  = row.getString("ITEMNUM")
            location = row.getString("LOCATION") if not row.isNull("LOCATION") else ""
            siteid   = row.getString("SITEID")
            qty      = row.getDouble("QUANTITY") if not row.isNull("QUANTITY") else 0.0
            cost     = row.getDouble("UNITCOST") if not row.isNull("UNITCOST") else 0.0
            sign     = -1.0 if row.getString("ISSUETYPE") == "RETURN" else 1.0
            value    = sign * qty * cost
            key = (itemnum, location, siteid)
            usage[key] = usage.get(key, 0.0) + value
            row = set_.moveNext()
    finally:
        if set_ is not None:
            try:
                set_.close()
            except Exception:
                pass
    return usage


def _classify(usage):
    """Return dict key -> 'A'|'B'|'C' based on cumulative usage share."""
    items = [(k, max(v, 0.0)) for k, v in usage.iteritems()]
    items.sort(key=lambda kv: kv[1], reverse=True)
    total = sum(v for _, v in items) or 1.0
    classification = {}
    cumulative = 0.0
    for key, value in items:
        share = value / total
        cumulative += share
        if cumulative <= _A_CUTOFF:
            classification[key] = "A"
        elif cumulative <= _B_CUTOFF:
            classification[key] = "B"
        else:
            classification[key] = "C"
    return classification


def _apply(mxs, user, classification):
    inv_set = None
    written = 0
    try:
        inv_set = mxs.getMboSet("INVENTORY", user)
        inv = inv_set.moveFirst()
        batch = 0
        while inv is not None:
            key = (inv.getString("ITEMNUM"),
                   inv.getString("LOCATION") if not inv.isNull("LOCATION") else "",
                   inv.getString("SITEID"))
            new_class = classification.get(key, "C")
            current = inv.getString("ABCTYPE") if not inv.isNull("ABCTYPE") else ""
            if current != new_class:
                inv.setValue("ABCTYPE", new_class)
                written += 1
                batch += 1
                if batch >= _BATCH_SIZE:
                    inv_set.save()
                    batch = 0
            inv = inv_set.moveNext()
        if batch > 0:
            inv_set.save()
    finally:
        if inv_set is not None:
            try:
                inv_set.close()
            except Exception:
                pass
    return written


# =============================================================================
# Main
# =============================================================================
def run():
    mxs = MXServer.getMXServer()
    user = mxs.getSystemUserInfo()
    try:
        usage = _gather_usage(mxs, user)
        _LOGGER.info("TMG_ABCCLASSIFY: gathered usage for %d (item, location, site) groups" %
                     len(usage))
        classification = _classify(usage)
        written = _apply(mxs, user, classification)
        _LOGGER.info("TMG_ABCCLASSIFY: updated ABCTYPE on %d INVENTORY rows" % written)
    except Exception as e:                                    # noqa
        _LOGGER.error("TMG_ABCCLASSIFY failed: %s" % str(e))
        raise


run()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_ABCCLASSIFY.CRON.ACTION",
    "description": "Re-classify inventory ABCTYPE by trailing-12-month usage value (A=70/B=20/C=10).",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_ABCCLASSIFY.CRON.ACTION",
        "launchPointType": "CRONTASK",
        "active": True,
        "cronTaskName": "TMG_ABCCLASSIFY",
        "description": "Periodic ABC inventory classification."
    }]
}
