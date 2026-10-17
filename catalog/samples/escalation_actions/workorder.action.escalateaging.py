# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_WORKORDER_ACTION_ESCALATEAGING
# Launch Point Name: TMG_WORKORDER_ACTION_ESCALATEAGING
# Launch Point Type: ACTION
# Object: WORKORDER
# Action: TMG_ESCALATEAGING
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Escalation action: bumps WOPRIORITY by 1 (toward higher priority — 1 is
# top) on each work order picked up by an Escalation that filters for
# WOs aging past their target start date.
#
# An Escalation is a scheduled query + action: the Escalation engine runs
# the query and invokes this action against each row. The implicit `mbo`
# variable is set to the current WORKORDER for each invocation.
#
# Demonstrates:
#   - ACTION launch point (Escalation-driven)
#   - Reading + writing on the implicit mbo
#   - Audit logging the bump
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import MboConstants
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_workorder_action_escalateaging")


# =============================================================================
# Main
# =============================================================================
def escalate_aging():
    if mbo is None:                                          # noqa: F821
        return

    current = 5
    if not mbo.isNull("WOPRIORITY"):                         # noqa: F821
        current = mbo.getInt("WOPRIORITY")                   # noqa: F821

    if current <= 1:
        _LOGGER.debug("WONUM=%s already top priority — skipping" %
                      mbo.getString("WONUM"))                # noqa: F821
        return

    new_priority = current - 1
    mbo.setValue("WOPRIORITY", new_priority,                 # noqa: F821
                 MboConstants.NOACCESSCHECK)
    _LOGGER.info("Escalated WONUM=%s priority %d -> %d" %
                 (mbo.getString("WONUM"), current, new_priority))   # noqa: F821


escalate_aging()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_WORKORDER_ACTION_ESCALATEAGING",
    "description": "Bump WOPRIORITY by one level when invoked by aging escalation.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_WORKORDER_ACTION_ESCALATEAGING",
        "launchPointType": "ACTION",
        "active": True,
        "objectName": "WORKORDER",
        "actionName": "TMG_ESCALATEAGING",
        "description": "Escalation action invoked by TMG_WO_AGING escalation."
    }]
}
