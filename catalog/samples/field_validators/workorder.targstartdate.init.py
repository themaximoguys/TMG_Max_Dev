# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_WORKORDER_TARGSTARTDATE_INIT
# Launch Point Name: TMG_WORKORDER_TARGSTARTDATE_INIT
# Launch Point Type: ATTRIBUTE
# Object: WORKORDER
# Field: TARGSTARTDATE
# Event: INITIALIZE_VALUE (INIT)
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Compute a default TARGSTARTDATE on a new WORKORDER based on its WOPRIORITY:
#   Priority 1 (Emergency)  → now + 4 hours
#   Priority 2 (Urgent)     → now + 24 hours
#   Priority 3 (Normal)     → now + 72 hours
#   Priority 4 (Low)        → now + 7 days
#   Priority 5+ (Backlog)   → now + 14 days
#
# INIT only — but here we DO call setValue because INIT for a brand-new
# work order is the conventional point for default-value computation when
# the value depends on another field (WOPRIORITY) just initialized.
#
# Demonstrates:
#   - Time-based default computation
#   - java.util.Calendar for date arithmetic
#   - Map-based priority dispatch
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import MboConstants
from psdi.util.logging import MXLoggerFactory

from java.util import Calendar


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_workorder_targstartdate_init")

# Hours offset by priority
_OFFSET_HOURS_BY_PRIORITY = {
    1: 4,
    2: 24,
    3: 72,
    4: 168,    # 7 days
    5: 336,    # 14 days
}


# =============================================================================
# Main
# =============================================================================
def init_targstartdate():
    if mbo is None:                                          # noqa: F821
        return
    if not mbo.toBeAdded():                                  # noqa: F821
        return  # only on new records
    if not mbo.isNull("TARGSTARTDATE"):                      # noqa: F821
        return  # user already supplied one

    priority = 5
    if not mbo.isNull("WOPRIORITY"):                         # noqa: F821
        priority = mbo.getInt("WOPRIORITY")                  # noqa: F821

    hours = _OFFSET_HOURS_BY_PRIORITY.get(priority, 336)
    cal = Calendar.getInstance()
    cal.add(Calendar.HOUR, hours)

    mbo.setValue("TARGSTARTDATE", cal.getTime(),             # noqa: F821
                 MboConstants.NOACCESSCHECK)
    _LOGGER.debug("Defaulted TARGSTARTDATE for WO priority %d (+%d hours)" %
                  (priority, hours))


init_targstartdate()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_WORKORDER_TARGSTARTDATE_INIT",
    "description": "Default TARGSTARTDATE on new WORKORDER based on WOPRIORITY.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_WORKORDER_TARGSTARTDATE_INIT",
        "launchPointType": "ATTRIBUTE",
        "active": True,
        "objectName": "WORKORDER",
        "attributeName": "TARGSTARTDATE",
        "events": {"initializevalue": True},
        "description": "Auto-compute target start date from priority on new WO."
    }]
}
