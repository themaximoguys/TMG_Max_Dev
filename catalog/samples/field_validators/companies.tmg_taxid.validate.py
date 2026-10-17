# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_COMPANIES_TAXID_VALIDATE
# Launch Point Name: TMG_COMPANIES_TAXID_VALIDATE
# Launch Point Type: ATTRIBUTE
# Object: COMPANIES
# Field: TMG_TAXID
# Event: VALIDATE
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Validate that TMG_TAXID matches a 9-digit numeric format (e.g. US EIN
# without dashes). Rejects malformed entries with a clear error.
#
# Demonstrates:
#   - VALIDATE event with regex pattern matching
#   - Importing Java regex from java.util.regex (Jython idiom)
#   - Re-raising MXApplicationException with errorgroup/errormsg keys
#
# =============================================================================
# Imports
# =============================================================================
from java.util.regex import Pattern
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_companies_taxid_validate")
_TAXID_PATTERN = Pattern.compile("^[0-9]{9}$")


# =============================================================================
# Main
# =============================================================================
def validate_taxid():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.isNull("TMG_TAXID"):                              # noqa: F821
        return

    raw = mbo.getString("TMG_TAXID")                         # noqa: F821
    if raw is None:
        return
    cleaned = raw.replace("-", "").replace(" ", "")

    if not _TAXID_PATTERN.matcher(cleaned).matches():
        _LOGGER.warn("Invalid TMG_TAXID format on COMPANY %s" % mbo.getString("COMPANY"))   # noqa: F821
        raise MXApplicationException("tmg", "invalidtaxid")


validate_taxid()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_COMPANIES_TAXID_VALIDATE",
    "description": "Validate TMG_TAXID is exactly 9 digits.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_COMPANIES_TAXID_VALIDATE",
        "launchPointType": "ATTRIBUTE",
        "active": True,
        "objectName": "COMPANIES",
        "attributeName": "TMG_TAXID",
        "events": {"validate": True},
        "description": "Enforce 9-digit numeric Tax ID format."
    }]
}
