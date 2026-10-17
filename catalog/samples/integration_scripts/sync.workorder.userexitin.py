# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_SYNC_WORKORDER_USEREXITIN
# Launch Point Name: TMG_SYNC_WORKORDER_USEREXITIN
# Launch Point Type: SUBSCRIBE (User Exit In)
# Service: TMG_WORKORDER_IN
# Exit: USEREXITIN
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# User Exit In — runs early in inbound processing, before MBO mapping
# applies. Inspect/modify the structuredData payload before Maximo writes
# it onto the WORKORDER MBO. Useful for translating external code values
# into internal Maximo codes.
#
# Translates:
#   - External work-type codes ("EMERGENCY","CORRECTIVE",...) → Maximo (EM,CM,...)
#   - Trims whitespace from DESCRIPTION
#
# Demonstrates:
#   - User Exit In pattern
#   - irData.getCurrentData / setAsString for payload manipulation
#
# =============================================================================
# Imports
# =============================================================================
from psdi.iface.mic import MaxIfaceConstants
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_sync_workorder_userexitin")

_WORKTYPE_REVERSE_MAP = {
    "EMERGENCY":  "EM",
    "CORRECTIVE": "CM",
    "PREVENTIVE": "PM",
    "CAPITAL":    "CP",
    "PROJECT":    "PR",
}


# =============================================================================
# Main
# =============================================================================
def translate_inbound():
    try:
        wt = irData.getCurrentData("WORKTYPE")               # noqa: F821
        if wt is not None:
            mapped = _WORKTYPE_REVERSE_MAP.get(wt.upper(), wt)
            if mapped != wt:
                irData.setAsString("WORKTYPE", mapped)       # noqa: F821
                _LOGGER.debug("Translated inbound WORKTYPE %s -> %s" % (wt, mapped))
    except Exception:
        pass

    try:
        desc = irData.getCurrentData("DESCRIPTION")          # noqa: F821
        if desc is not None and desc != desc.strip():
            irData.setAsString("DESCRIPTION", desc.strip())  # noqa: F821
    except Exception:
        pass


translate_inbound()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_SYNC_WORKORDER_USEREXITIN",
    "description": "Pre-mapping inbound WORKORDER payload normalization (worktype codes, whitespace).",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_SYNC_WORKORDER_USEREXITIN",
        "launchPointType": "SUBSCRIBE",
        "active": True,
        "enterpriseService": "TMG_WORKORDER_IN",
        "exitType": "USEREXITIN",
        "description": "Inbound WO user exit (pre-mapping)."
    }]
}
