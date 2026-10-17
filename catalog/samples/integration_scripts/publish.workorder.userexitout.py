# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PUBLISH_WORKORDER_USEREXITOUT
# Launch Point Name: TMG_PUBLISH_WORKORDER_USEREXITOUT
# Launch Point Type: PUBLISH (User Exit — outbound)
# Channel: TMG_WORKORDER_OUT
# Exit: USEREXITOUT (after MBO → message structure, before queue)
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# User Exit Out — runs after the MBO has been transformed into the message
# structure but before it lands on the outbound queue. Use this hook to
# attach computed/cross-MBO fields that aren't part of the WORKORDER record
# but are required by the receiving system.
#
# Adds:
#   - TMG_TOTAL_LABOR_HOURS = sum of LABTRANS.REGULARHRS for this WO
#   - TMG_HAS_OPEN_TASKS    = 1 if any child WO is still open
#
# Demonstrates:
#   - User Exit Out pattern
#   - irData.setAsString / setAsInt to add fields to the outbound payload
#   - Aggregation across child relationships
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_publish_workorder_userexitout")


# =============================================================================
# Helpers
# =============================================================================
def _sum_labor_hours():
    lt_set = None
    total = 0.0
    try:
        lt_set = mbo.getMboSet("LABTRANS")                   # noqa: F821
        row = lt_set.moveFirst()
        while row is not None:
            if not row.isNull("REGULARHRS"):
                total += row.getDouble("REGULARHRS")
            row = lt_set.moveNext()
    finally:
        if lt_set is not None:
            try:
                lt_set.close()
            except Exception:
                pass
    return total


def _has_open_children():
    child_set = None
    try:
        child_set = mbo.getMboSet("CHILDREN")                # noqa: F821
        sf = "status not in ('CLOSE','COMP','CAN')"
        child_set.setWhere(sf)
        return child_set.count() > 0
    finally:
        if child_set is not None:
            try:
                child_set.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def enrich_outbound():
    if mbo is None:                                          # noqa: F821
        return

    try:
        total = _sum_labor_hours()
        irData.setAsString("TMG_TOTAL_LABOR_HOURS", "%.2f" % total)   # noqa: F821
    except Exception:
        _LOGGER.debug("TMG_TOTAL_LABOR_HOURS not in payload schema — skipping")

    try:
        irData.setAsString(                                  # noqa: F821
            "TMG_HAS_OPEN_TASKS",
            "1" if _has_open_children() else "0"
        )
    except Exception:
        _LOGGER.debug("TMG_HAS_OPEN_TASKS not in payload schema — skipping")


enrich_outbound()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_PUBLISH_WORKORDER_USEREXITOUT",
    "description": "Enrich outbound WO payload with computed labor totals and child-task flag.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PUBLISH_WORKORDER_USEREXITOUT",
        "launchPointType": "PUBLISH",
        "active": True,
        "publishChannel": "TMG_WORKORDER_OUT",
        "exitType": "USEREXITOUT",
        "description": "Add computed fields to outbound WORKORDER payload."
    }]
}
