# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PUBLISH_WORKORDER_SETUSERVALUE
# Launch Point Name: TMG_PUBLISH_WORKORDER_SETUSERVALUE
# Launch Point Type: PUBLISH (setUserValue)
# Channel: TMG_WORKORDER_OUT
# Exit: SETUSERVALUE
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# setUserValue exit — invoked once per attribute to allow per-field
# transformation just before the value is written into the outbound
# message. Receives the attribute name and current value, returns the
# transformed value.
#
# Use cases:
#   - Per-field formatting (dates, currency, codes)
#   - Code translation (Maximo internal code -> external system code)
#   - Conditional null-out for fields you never want to expose
#
# Demonstrates:
#   - setUserValue exit pattern (per-attribute transformation)
#   - Per-field branching by attribute name
#   - Returning a transformed value via the userValue mechanism
#
# Implicit variables on this exit:
#   - mbo:        the source MBO row
#   - attrName:   the attribute being processed (string)
#   - userValue:  current outbound value (read/write)
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util.logging import MXLoggerFactory

from java.text import SimpleDateFormat


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_publish_workorder_setuservalue")
_ISO_DATE = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss")

# Translate Maximo work types to external system codes
_WORKTYPE_MAP = {
    "EM": "EMERGENCY",
    "CM": "CORRECTIVE",
    "PM": "PREVENTIVE",
    "CP": "CAPITAL",
    "PR": "PROJECT",
}


# =============================================================================
# Main
# =============================================================================
def transform_value():
    try:
        name = attrName.upper()                              # noqa: F821
    except NameError:
        return  # exit not bound — nothing to do

    # Date fields → ISO 8601
    if name in ("REPORTDATE", "TARGSTARTDATE", "TARGCOMPDATE", "ACTSTART", "ACTFINISH"):
        try:
            if mbo is not None and not mbo.isNull(name):     # noqa: F821
                d = mbo.getDate(name)                        # noqa: F821
                if d is not None:
                    irData.setAsString("USERVALUE", _ISO_DATE.format(d))   # noqa: F821
                    return
        except Exception:
            pass

    # WORKTYPE → external code
    if name == "WORKTYPE" and mbo is not None and not mbo.isNull("WORKTYPE"):    # noqa: F821
        code = mbo.getString("WORKTYPE")                     # noqa: F821
        translated = _WORKTYPE_MAP.get(code, code)
        if translated != code:
            try:
                irData.setAsString("USERVALUE", translated)  # noqa: F821
                return
            except Exception:
                pass

    # Sensitive fields — null out
    if name in ("LEAD",):
        try:
            irData.setAsString("USERVALUE", "")              # noqa: F821
            return
        except Exception:
            pass


transform_value()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_PUBLISH_WORKORDER_SETUSERVALUE",
    "description": "Per-attribute value transformer for outbound WORKORDER (dates, codes, redaction).",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PUBLISH_WORKORDER_SETUSERVALUE",
        "launchPointType": "PUBLISH",
        "active": True,
        "publishChannel": "TMG_WORKORDER_OUT",
        "exitType": "SETUSERVALUE",
        "description": "Per-attribute value transformer."
    }]
}
