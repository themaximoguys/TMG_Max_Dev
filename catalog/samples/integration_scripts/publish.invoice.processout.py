# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PUBLISH_INVOICE_PROCESSOUT
# Launch Point Name: TMG_PUBLISH_INVOICE_PROCESSOUT
# Launch Point Type: PUBLISH (Process Out)
# Channel: TMG_INVOICE_OUT
# Exit: PROCESSOUT
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Outbound INVOICE processing. Only ship invoices in APPR or PAID status.
# Redacts banking fields (TMG_BANKACCT, TMG_ROUTINGNUM) before transmission.
#
# Demonstrates:
#   - Status gating outbound traffic
#   - Multi-field redaction loop
#   - service.log style logging (alternative to MXLoggerFactory)
#
# =============================================================================
# Imports
# =============================================================================
_PUBLISHABLE_STATUSES = ("APPR", "PAID")
_REDACT_FIELDS = ("TMG_BANKACCT", "TMG_ROUTINGNUM")


# =============================================================================
# Main
# =============================================================================
def process_invoice_out():
    if mbo is None:                                          # noqa: F821
        return

    status = mbo.getString("STATUS") if not mbo.isNull("STATUS") else ""   # noqa: F821
    if status not in _PUBLISHABLE_STATUSES:
        try:
            service.log("Skip INVOICE publish status=%s" % status)         # noqa: F821
        except Exception:
            pass
        try:
            irData.setStop(True)                             # noqa: F821
        except Exception:
            pass
        return

    for field in _REDACT_FIELDS:
        try:
            irData.setAsString(field, "REDACTED")            # noqa: F821
        except Exception:
            continue


process_invoice_out()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_PUBLISH_INVOICE_PROCESSOUT",
    "description": "Gate INVOICE publish by status; redact banking fields.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PUBLISH_INVOICE_PROCESSOUT",
        "launchPointType": "PUBLISH",
        "active": True,
        "publishChannel": "TMG_INVOICE_OUT",
        "exitType": "PROCESSOUT",
        "description": "Outbound INVOICE processing exit."
    }]
}
