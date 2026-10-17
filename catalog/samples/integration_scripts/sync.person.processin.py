# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_SYNC_PERSON_PROCESSIN
# Launch Point Name: TMG_SYNC_PERSON_PROCESSIN
# Launch Point Type: SUBSCRIBE (Process In)
# Service: TMG_PERSON_IN
# Exit: PROCESSIN
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Inbound enterprise-service exit for PERSON sync from an external HR
# system. Normalizes incoming fields and prevents DELETE-flagged messages
# from removing PERSON records that still own active WORKORDERs.
#
# Demonstrates:
#   - Enterprise service inbound exit
#   - Action-code branching (Add/Change/Delete)
#   - Cross-MBO precondition check before honoring delete
#
# =============================================================================
# Imports
# =============================================================================
from psdi.iface.mic import MaxIfaceConstants
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_sync_person_inbound")


# =============================================================================
# Helpers
# =============================================================================
def _normalize_email():
    if mbo.isNull("PRIMARYEMAIL"):                           # noqa: F821
        return
    val = mbo.getString("PRIMARYEMAIL")                      # noqa: F821
    if val is None:
        return
    cleaned = val.strip().lower()
    if cleaned != val:
        mbo.setValue("PRIMARYEMAIL", cleaned)                # noqa: F821


def _person_has_open_wo(person_id):
    if person_id is None or len(person_id.strip()) == 0:
        return False
    mxs = MXServer.getMXServer()
    wo_set = None
    try:
        wo_set = mxs.getMboSet("WORKORDER", mbo.getUserInfo())   # noqa: F821
        sf = SqlFormat(None,
                       "(reportedby = :1 or owner = :1) "
                       "and status not in ('CLOSE','CAN','COMP')")
        sf.setObject(1, "WORKORDER", "REPORTEDBY", person_id)
        wo_set.setWhere(sf.format())
        return wo_set.count() > 0
    finally:
        if wo_set is not None:
            try:
                wo_set.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def process_inbound_person():
    if mbo is None:                                          # noqa: F821
        return

    action = ""
    try:
        action = irData.getCurrentData(MaxIfaceConstants.ACTION)   # noqa: F821
    except Exception:
        action = ""
    if action is None:
        action = ""

    if action.upper() == "DELETE":
        person_id = mbo.getString("PERSONID") if not mbo.isNull("PERSONID") else ""   # noqa: F821
        if _person_has_open_wo(person_id):
            _LOGGER.warn("Refusing DELETE for PERSON %s — open WORKORDERs exist" % person_id)
            raise MXApplicationException("tmg", "persondeleteblocked")
        return  # let normal delete flow proceed

    # Add / Change / null action
    _normalize_email()


process_inbound_person()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_SYNC_PERSON_PROCESSIN",
    "description": "Normalize email + block PERSON delete when open WOs exist.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_SYNC_PERSON_PROCESSIN",
        "launchPointType": "SUBSCRIBE",
        "active": True,
        "enterpriseService": "TMG_PERSON_IN",
        "exitType": "PROCESSIN",
        "description": "Inbound PERSON enterprise service processing exit."
    }]
}
