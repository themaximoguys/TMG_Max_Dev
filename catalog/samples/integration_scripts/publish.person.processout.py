# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PUBLISH_PERSON_PROCESSOUT
# Launch Point Name: TMG_PUBLISH_PERSON_PROCESSOUT
# Launch Point Type: PUBLISH (Process Out)
# Channel: TMG_PERSON_OUT
# Exit: PROCESSOUT
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Outbound PERSON feed with privacy-aware redaction.
#   - Skip persons with STATUS != 'ACTIVE'
#   - Mask sensitive fields: TMG_SSN, TMG_BIRTHDATE, TMG_HOMEPHONE
#   - Force PRIMARYEMAIL to lowercase
#
# Demonstrates:
#   - Privacy redaction pattern (multi-field masking)
#   - Outbound payload normalization
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_publish_person_processout")
_MASK_FIELDS = ("TMG_SSN", "TMG_BIRTHDATE", "TMG_HOMEPHONE")


# =============================================================================
# Main
# =============================================================================
def process_person_out():
    if mbo is None:                                          # noqa: F821
        return

    status = mbo.getString("STATUS") if not mbo.isNull("STATUS") else ""   # noqa: F821
    if status != "ACTIVE":
        _LOGGER.info("Skip PERSON publish — status=%s for PERSONID=%s" %
                     (status, mbo.getString("PERSONID")))    # noqa: F821
        try:
            irData.setStop(True)                             # noqa: F821
        except Exception:
            pass
        return

    for fld in _MASK_FIELDS:
        try:
            irData.setAsString(fld, "REDACTED")              # noqa: F821
        except Exception:
            continue

    if not mbo.isNull("PRIMARYEMAIL"):                       # noqa: F821
        email = mbo.getString("PRIMARYEMAIL")                # noqa: F821
        try:
            irData.setAsString("PRIMARYEMAIL", email.lower())   # noqa: F821
        except Exception:
            pass


process_person_out()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_PUBLISH_PERSON_PROCESSOUT",
    "description": "Outbound PERSON: skip non-active, mask SSN/DOB/home phone, lowercase email.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PUBLISH_PERSON_PROCESSOUT",
        "launchPointType": "PUBLISH",
        "active": True,
        "publishChannel": "TMG_PERSON_OUT",
        "exitType": "PROCESSOUT",
        "description": "Outbound PERSON processing with privacy redaction."
    }]
}
