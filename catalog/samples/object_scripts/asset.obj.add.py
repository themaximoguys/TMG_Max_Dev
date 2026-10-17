# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_ASSET_OBJ_ADD
# Launch Point Name: TMG_ASSET_OBJ_ADD
# Launch Point Type: OBJECT
# Object: ASSET
# Event: ADD
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Initialize TMG-prefixed custom fields when a new ASSET is created. Reads
# defaults from the parent CLASSSTRUCTURE record if present.
#
# Demonstrates:
#   - OBJECT ADD pattern
#   - Lookup against another MBO via fully-qualified relationship
#   - Idempotent default-fill
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import MboConstants
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_asset_obj_add")


# =============================================================================
# Main
# =============================================================================
def initialize_asset_defaults():
    if mbo is None:                                          # noqa: F821
        return

    # Default custom criticality flag if blank
    if mbo.isNull("TMG_CRITICALITY"):                        # noqa: F821
        mbo.setValue("TMG_CRITICALITY", "MEDIUM",            # noqa: F821
                     MboConstants.NOACCESSCHECK)

    # Default custom commission date to current date if not set
    if mbo.isNull("TMG_COMMISSIONDATE"):                     # noqa: F821
        from java.util import Date
        mbo.setValue("TMG_COMMISSIONDATE", Date(),           # noqa: F821
                     MboConstants.NOACCESSCHECK)

    _LOGGER.debug("Initialized TMG_ defaults on new ASSET")


initialize_asset_defaults()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_ASSET_OBJ_ADD",
    "description": "Initialize TMG-prefixed defaults on new ASSET records.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_ASSET_OBJ_ADD",
        "launchPointType": "OBJECT",
        "active": True,
        "objectName": "ASSET",
        "events": {"add": True},
        "description": "Set TMG_ defaults on new ASSET."
    }]
}
