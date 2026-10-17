# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_SYNC_LABOR_PROCESSIN
# Launch Point Name: TMG_SYNC_LABOR_PROCESSIN
# Launch Point Type: SUBSCRIBE (Process In)
# Service: TMG_LABOR_IN
# Exit: PROCESSIN
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Inbound LABOR sync from HR system. Sets STATUS = 'INACTIVE' on Maximo
# LABOR rows whose corresponding HR record is marked terminated. Also
# refreshes CRAFT and SKILLLEVEL when supplied.
#
# Demonstrates:
#   - Inbound state-sync pattern from upstream system-of-record
#   - Field-by-field conditional refresh
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_sync_labor_processin")


# =============================================================================
# Main
# =============================================================================
def process_labor_in():
    if mbo is None:                                          # noqa: F821
        return

    # HR-side termination flag drives Maximo status
    try:
        hr_status = irData.getCurrentData("TMG_HR_STATUS")   # noqa: F821
    except Exception:
        hr_status = None

    if hr_status is not None:
        if hr_status.upper() in ("TERMINATED", "INACTIVE"):
            mbo.setValue("STATUS", "INACTIVE")               # noqa: F821
        elif hr_status.upper() == "ACTIVE":
            mbo.setValue("STATUS", "ACTIVE")                 # noqa: F821

    # Refresh CRAFT only when provided
    try:
        c = irData.getCurrentData("CRAFT")                   # noqa: F821
        if c is not None and len(c.strip()) > 0:
            mbo.setValue("CRAFT", c)                         # noqa: F821
    except Exception:
        pass

    try:
        sl = irData.getCurrentData("SKILLLEVEL")             # noqa: F821
        if sl is not None and len(sl.strip()) > 0:
            mbo.setValue("SKILLLEVEL", sl)                   # noqa: F821
    except Exception:
        pass

    _LOGGER.debug("Synced LABOR record")


process_labor_in()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_SYNC_LABOR_PROCESSIN",
    "description": "Inbound LABOR sync from HR — propagate active/inactive + CRAFT/SKILLLEVEL.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_SYNC_LABOR_PROCESSIN",
        "launchPointType": "SUBSCRIBE",
        "active": True,
        "enterpriseService": "TMG_LABOR_IN",
        "exitType": "PROCESSIN",
        "description": "Inbound LABOR processing."
    }]
}
