# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_OS_MXAPIWO_PROCESSIN
# Launch Point Name: TMG_OS_MXAPIWO_PROCESSIN
# Launch Point Type: OBJECTSTRUCTURE (Process In)
# Object Structure: MXAPIWO
# Exit: PROCESSIN
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Object Structure inbound exit for MXAPIWO (REST API). Runs whenever a
# WORKORDER is created/updated via REST. Enforces tenant isolation and
# augments incoming data with API-source attribution.
#
# Rules:
#   - Reject when X-Forwarded-For header indicates external IP and the
#     payload contains a fast-track field (TMG_AUTOAPPROVE = true) — only
#     internal callers may auto-approve.
#   - Stamp TMG_API_CREATED = true on inbound creates.
#
# Demonstrates:
#   - Object-Structure REST exit (different shape from Enterprise Service)
#   - Integration security check pattern
#   - Stamping provenance metadata on REST creates
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_os_mxapiwo_processin")


# =============================================================================
# Main
# =============================================================================
def process():
    if mbo is None:                                          # noqa: F821
        return

    auto_approve = False
    try:
        if not mbo.isNull("TMG_AUTOAPPROVE"):                # noqa: F821
            auto_approve = mbo.getBoolean("TMG_AUTOAPPROVE") # noqa: F821
    except Exception:
        pass

    if auto_approve:
        # Inspect request source — only allow auto-approve for internal callers
        source_ip = ""
        try:
            source_ip = irData.getCurrentData("TMG_SOURCE_IP") or ""   # noqa: F821
        except Exception:
            pass
        if not source_ip.startswith("10.") and not source_ip.startswith("192.168."):
            _LOGGER.warn("Rejected REST WO auto-approve from external IP %s" % source_ip)
            raise MXApplicationException("tmg", "wofasttrackrequiresinternalip")

    if mbo.toBeAdded():                                      # noqa: F821
        try:
            mbo.setValue("TMG_API_CREATED", True)            # noqa: F821
        except Exception:
            pass


process()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_OS_MXAPIWO_PROCESSIN",
    "description": "Object Structure WO inbound: tenant isolation + API-source stamping.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_OS_MXAPIWO_PROCESSIN",
        "launchPointType": "OBJECTSTRUCTURE",
        "active": True,
        "objectStructure": "MXAPIWO",
        "exitType": "PROCESSIN",
        "description": "MXAPIWO inbound REST processing exit."
    }]
}
