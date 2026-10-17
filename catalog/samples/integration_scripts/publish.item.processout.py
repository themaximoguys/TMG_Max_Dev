# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_PUBLISH_ITEM_PROCESSOUT
# Launch Point Name: TMG_PUBLISH_ITEM_PROCESSOUT
# Launch Point Type: PUBLISH (Process Out)
# Channel: TMG_ITEM_OUT
# Exit: PROCESSOUT
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Outbound ITEM master processing.
#   - Skip when STATUS == 'OBSOLETE'
#   - Skip when ITEM is internal-only (TMG_INTERNAL_ONLY = true)
#   - Force ITEMNUM to uppercase in the outbound payload
#   - Compute and set TMG_DISPLAY_NAME = "ITEMNUM — DESCRIPTION"
#
# Demonstrates:
#   - Multiple skip conditions
#   - Outbound field normalization
#   - Computed display field added at integration boundary
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_publish_item_processout")


# =============================================================================
# Main
# =============================================================================
def process_item_out():
    if mbo is None:                                          # noqa: F821
        return

    status = mbo.getString("STATUS") if not mbo.isNull("STATUS") else ""   # noqa: F821
    if status == "OBSOLETE":
        _LOGGER.info("Skip ITEM publish — obsolete: ITEMNUM=%s" %
                     mbo.getString("ITEMNUM"))               # noqa: F821
        try:
            irData.setStop(True)                             # noqa: F821
        except Exception:
            pass
        return

    if not mbo.isNull("TMG_INTERNAL_ONLY") and mbo.getBoolean("TMG_INTERNAL_ONLY"):   # noqa: F821
        _LOGGER.info("Skip ITEM publish — internal-only: ITEMNUM=%s" %
                     mbo.getString("ITEMNUM"))               # noqa: F821
        try:
            irData.setStop(True)                             # noqa: F821
        except Exception:
            pass
        return

    # Normalize ITEMNUM uppercase
    itemnum = mbo.getString("ITEMNUM") if not mbo.isNull("ITEMNUM") else ""   # noqa: F821
    if itemnum and itemnum != itemnum.upper():
        try:
            irData.setAsString("ITEMNUM", itemnum.upper())   # noqa: F821
        except Exception:
            pass

    # Compose display name
    desc = mbo.getString("DESCRIPTION") if not mbo.isNull("DESCRIPTION") else ""   # noqa: F821
    display = ("%s — %s" % (itemnum.upper(), desc)).strip(" —")
    try:
        irData.setAsString("TMG_DISPLAY_NAME", display)      # noqa: F821
    except Exception:
        pass


process_item_out()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_PUBLISH_ITEM_PROCESSOUT",
    "description": "Outbound ITEM master: skip obsolete/internal, normalize ITEMNUM, add display name.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_PUBLISH_ITEM_PROCESSOUT",
        "launchPointType": "PUBLISH",
        "active": True,
        "publishChannel": "TMG_ITEM_OUT",
        "exitType": "PROCESSOUT",
        "description": "Outbound ITEM processing exit."
    }]
}
