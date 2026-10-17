# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_OS_MXAPIWO_PROCESSOUT
# Launch Point Name: TMG_OS_MXAPIWO_PROCESSOUT
# Launch Point Type: OBJECTSTRUCTURE (Process Out)
# Object Structure: MXAPIWO
# Exit: PROCESSOUT
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Object Structure outbound exit for MXAPIWO. Triggered when a REST GET
# returns a WORKORDER. Computes a derived field (TMG_AGE_DAYS) for each
# returned WO and surfaces it in the response payload. This computed
# field is not persisted on the MBO — it's added to the API response only.
#
# Demonstrates:
#   - REST response enrichment (derived/computed fields on the API boundary)
#   - irData.setAsString to add fields to the response payload
#   - Date arithmetic in the OS context
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util.logging import MXLoggerFactory

from java.util import Date


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_os_mxapiwo_processout")
_MS_PER_DAY = 86400000.0


# =============================================================================
# Main
# =============================================================================
def enrich_response():
    if mbo is None:                                          # noqa: F821
        return

    if mbo.isNull("REPORTDATE"):                             # noqa: F821
        return
    reported = mbo.getDate("REPORTDATE")                     # noqa: F821
    age_ms = Date().getTime() - reported.getTime()
    age_days = max(0, int(age_ms / _MS_PER_DAY))

    try:
        irData.setAsString("TMG_AGE_DAYS", str(age_days))    # noqa: F821
    except Exception:
        _LOGGER.debug("TMG_AGE_DAYS not in OS schema — cannot enrich")


enrich_response()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_OS_MXAPIWO_PROCESSOUT",
    "description": "Object Structure WO REST response: add derived TMG_AGE_DAYS field.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_OS_MXAPIWO_PROCESSOUT",
        "launchPointType": "OBJECTSTRUCTURE",
        "active": True,
        "objectStructure": "MXAPIWO",
        "exitType": "PROCESSOUT",
        "description": "MXAPIWO outbound REST processing exit."
    }]
}
