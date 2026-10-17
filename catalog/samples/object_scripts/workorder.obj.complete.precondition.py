# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_WORKORDER_OBJ_COMPLETE_PRECONDITION
# Launch Point Name: TMG_WORKORDER_OBJ_COMPLETE_PRECONDITION
# Launch Point Type: OBJECT
# Object: WORKORDER
# Event: validate (status-change validation)
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Block transition to status COMP when the WORKORDER has unresolved WORKLOG
# entries — specifically log entries with TMG_RESOLUTION = 'OPEN' and a
# logtype of SAFETY or ISSUE. Forces the technician to close out safety
# observations before the WO can be marked complete.
#
# Demonstrates:
#   - Status-change precondition pattern (object validate event)
#   - Comparing old vs new status via getMboValue().getOriginalValue()
#   - Counting child rows with SqlFormat
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_workorder_obj_complete_precondition")


# =============================================================================
# Helpers
# =============================================================================
def _has_open_safety_or_issue_logs():
    log_set = None
    try:
        log_set = mbo.getMboSet("WORKLOG")                   # noqa: F821
        sf = SqlFormat(mbo,                                  # noqa: F821
                       "logtype in ('SAFETY','ISSUE') "
                       "and (tmg_resolution is null or tmg_resolution = :1)")
        sf.setObject(1, "WORKLOG", "TMG_RESOLUTION", "OPEN")
        log_set.setWhere(sf.format())
        return log_set.count() > 0
    finally:
        if log_set is not None:
            try:
                log_set.close()
            except Exception as ce:                          # noqa
                _LOGGER.warn("close worklog set: %s" % str(ce))


def _is_transition_to_comp():
    if mbo.isNull("STATUS"):                                 # noqa: F821
        return False
    if mbo.getString("STATUS") != "COMP":                    # noqa: F821
        return False

    status_attr = mbo.getMboValue("STATUS")                  # noqa: F821
    if status_attr is None:
        return False
    try:
        ov = status_attr.getOriginalValue()
        old = ov.asString() if ov is not None else None
    except Exception:
        old = None
    return old is not None and old != "COMP"


# =============================================================================
# Main
# =============================================================================
def validate_complete_precondition():
    if mbo is None:                                          # noqa: F821
        return
    if not _is_transition_to_comp():
        return

    if _has_open_safety_or_issue_logs():
        _LOGGER.warn("WONUM=%s cannot be COMPleted — open safety/issue worklog entries" %
                     mbo.getString("WONUM"))                 # noqa: F821
        raise MXApplicationException("tmg", "openworklogentries")


validate_complete_precondition()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_WORKORDER_OBJ_COMPLETE_PRECONDITION",
    "description": "Block WO -> COMP when open SAFETY/ISSUE worklog entries exist.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_WORKORDER_OBJ_COMPLETE_PRECONDITION",
        "launchPointType": "OBJECT",
        "active": True,
        "objectName": "WORKORDER",
        "events": {"validate": True},
        "description": "Precondition for COMP status."
    }]
}
