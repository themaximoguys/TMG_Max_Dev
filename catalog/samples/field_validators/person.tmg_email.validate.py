# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PERSON_EMAIL_VALIDATE
# Launch Point Name: TMG_PERSON_EMAIL_VALIDATE
# Launch Point Type: ATTRIBUTE
# Object: PERSON
# Field: TMG_EMAIL
# Event: VALIDATE
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Validate TMG_EMAIL on PERSON is a syntactically reasonable email address.
# Uses a permissive RFC-5322-ish pattern; perfect validation requires DNS,
# which is out of scope for synchronous save-time validation.
#
# Demonstrates:
#   - VALIDATE event with regex
#   - service.log() logging style (alternative to MXLoggerFactory)
#
# =============================================================================
# Imports
# =============================================================================
from java.util.regex import Pattern
from psdi.util import MXApplicationException


_EMAIL_PATTERN = Pattern.compile(
    "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
)


# =============================================================================
# Main
# =============================================================================
def validate_email():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.isNull("TMG_EMAIL"):                              # noqa: F821
        return

    email = mbo.getString("TMG_EMAIL")                       # noqa: F821
    if email is None or len(email.strip()) == 0:
        return

    if not _EMAIL_PATTERN.matcher(email.strip()).matches():
        try:
            service.log_warn(                                # noqa: F821
                "Invalid TMG_EMAIL format on PERSON %s: %s" %
                (mbo.getString("PERSONID"), email))          # noqa: F821
        except Exception:
            pass
        raise MXApplicationException("tmg", "invalidemail")


validate_email()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_PERSON_EMAIL_VALIDATE",
    "description": "Validate PERSON.TMG_EMAIL syntactic format.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PERSON_EMAIL_VALIDATE",
        "launchPointType": "ATTRIBUTE",
        "active": True,
        "objectName": "PERSON",
        "attributeName": "TMG_EMAIL",
        "events": {"validate": True},
        "description": "Reject malformed email addresses."
    }]
}
