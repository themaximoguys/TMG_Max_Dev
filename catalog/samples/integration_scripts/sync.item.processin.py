# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_SYNC_ITEM_PROCESSIN
# Launch Point Name: TMG_SYNC_ITEM_PROCESSIN
# Launch Point Type: SUBSCRIBE (Process In)
# Service: TMG_ITEM_IN
# Exit: PROCESSIN
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Inbound ITEM master processing. Auto-classify ITEM by description keywords
# when COMMODITY is not provided in the inbound payload — useful when the
# upstream system doesn't speak Maximo's commodity codes.
#
# Demonstrates:
#   - Keyword-based auto-classification
#   - Default-fill on inbound
#   - Case-insensitive substring matching
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_sync_item_processin")

# Lowest-priority keyword wins → ordered list of (commodity_code, [keywords])
_KEYWORD_RULES = [
    ("ELECTRICAL",  ["wire", "cable", "switch", "breaker", "transformer", "motor"]),
    ("MECHANICAL",  ["bearing", "pump", "valve", "gasket", "seal", "shaft"]),
    ("HARDWARE",    ["bolt", "nut", "screw", "washer", "fastener"]),
    ("LUBRICANT",   ["oil", "grease", "lubricant"]),
    ("CONSUMABLE",  ["filter", "rag", "tape"]),
]


# =============================================================================
# Helpers
# =============================================================================
def _classify(description):
    if description is None:
        return None
    text = description.lower()
    for code, keywords in _KEYWORD_RULES:
        for kw in keywords:
            if kw in text:
                return code
    return None


# =============================================================================
# Main
# =============================================================================
def process_item_in():
    if mbo is None:                                          # noqa: F821
        return

    if not mbo.isNull("COMMODITY"):                          # noqa: F821
        return  # already set by upstream

    if mbo.isNull("DESCRIPTION"):                            # noqa: F821
        return

    code = _classify(mbo.getString("DESCRIPTION"))           # noqa: F821
    if code is not None:
        mbo.setValue("COMMODITY", code)                      # noqa: F821
        _LOGGER.info("Auto-classified ITEMNUM=%s as COMMODITY=%s" %
                     (mbo.getString("ITEMNUM"), code))       # noqa: F821


process_item_in()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_SYNC_ITEM_PROCESSIN",
    "description": "Inbound ITEM master: keyword-based COMMODITY auto-classification.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_SYNC_ITEM_PROCESSIN",
        "launchPointType": "SUBSCRIBE",
        "active": True,
        "enterpriseService": "TMG_ITEM_IN",
        "exitType": "PROCESSIN",
        "description": "Inbound ITEM auto-classification."
    }]
}
