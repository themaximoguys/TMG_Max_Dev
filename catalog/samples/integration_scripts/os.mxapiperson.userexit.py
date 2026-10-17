# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_OS_MXAPIPERSON_USEREXIT
# Launch Point Name: TMG_OS_MXAPIPERSON_USEREXIT
# Launch Point Type: OBJECTSTRUCTURE (User Exit)
# Object Structure: MXAPIPERSON
# Exit: USEREXIT
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Object Structure user-exit pattern. Runs in the data-flow boundary
# between REST and the MBO layer. This script demonstrates a "single exit
# that handles both directions" idiom — the script branches on whether
# the call is inbound (creating/updating) or outbound (returning a row).
#
# Direction is detected by checking irData.isProcessInBound().
#
# Behavior:
#   - INBOUND: lowercase email; reject if employeeId is missing
#   - OUTBOUND: redact TMG_SSN; never expose in REST response
#
# Demonstrates:
#   - Direction-aware OS user exit
#   - Combined inbound + outbound logic in one script
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_os_mxapiperson_userexit")


# =============================================================================
# Direction-aware handlers
# =============================================================================
def _handle_inbound():
    if mbo is None:                                          # noqa: F821
        return

    if not mbo.isNull("PRIMARYEMAIL"):                       # noqa: F821
        em = mbo.getString("PRIMARYEMAIL")                   # noqa: F821
        if em is not None and em != em.lower():
            mbo.setValue("PRIMARYEMAIL", em.lower())         # noqa: F821

    if mbo.toBeAdded() and mbo.isNull("EMPLOYEEID"):         # noqa: F821
        _LOGGER.warn("REST PERSON create missing EMPLOYEEID")
        raise MXApplicationException("tmg", "personrequiresemployeeid")


def _handle_outbound():
    try:
        irData.setAsString("TMG_SSN", "REDACTED")            # noqa: F821
    except Exception:
        pass


# =============================================================================
# Main
# =============================================================================
def process():
    inbound = True
    try:
        inbound = bool(irData.isProcessInBound())            # noqa: F821
    except Exception:
        # If detection fails, default to inbound logic which is safer
        inbound = True

    if inbound:
        _handle_inbound()
    else:
        _handle_outbound()


process()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_OS_MXAPIPERSON_USEREXIT",
    "description": "Object Structure PERSON user exit: direction-aware (lowercase email in, redact SSN out).",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_OS_MXAPIPERSON_USEREXIT",
        "launchPointType": "OBJECTSTRUCTURE",
        "active": True,
        "objectStructure": "MXAPIPERSON",
        "exitType": "USEREXIT",
        "description": "MXAPIPERSON bidirectional user exit."
    }]
}
