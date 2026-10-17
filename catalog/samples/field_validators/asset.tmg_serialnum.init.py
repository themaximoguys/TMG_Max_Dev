# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_ASSET_SERIALNUM_INIT
# Launch Point Name: TMG_ASSET_SERIALNUM_INIT
# Launch Point Type: ATTRIBUTE
# Object: ASSET
# Field: TMG_SERIALNUM
# Event: INITIALIZE_VALUE (INIT)
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Sets the read-only flag on a custom serial-number field for non-rotating
# assets (which don't track unique serial numbers). Runs on INIT event ONLY
# — INIT events are read-only setup; setValue() must NOT be called here.
#
# Demonstrates:
#   - INIT event pattern (setReadOnly only, no setValue)
#   - Implicit `mbo` variable
#   - Conditional UI behavior via setFieldFlag
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import MboConstants
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_asset_serialnum_init")


# =============================================================================
# Main
# =============================================================================
def initialize_serialnum_flags():
    if mbo is None:                                          # noqa: F821
        return

    is_rotating = False
    if not mbo.isNull("ROTATING"):                           # noqa: F821
        is_rotating = bool(mbo.getBoolean("ROTATING"))       # noqa: F821

    if is_rotating:
        # Rotating assets need editable serial numbers
        mbo.setFieldFlag("TMG_SERIALNUM", MboConstants.READONLY, False)   # noqa: F821
        mbo.setFieldFlag("TMG_SERIALNUM", MboConstants.REQUIRED, True)    # noqa: F821
    else:
        # Non-rotating: serial number is irrelevant
        mbo.setFieldFlag("TMG_SERIALNUM", MboConstants.READONLY, True)    # noqa: F821
        mbo.setFieldFlag("TMG_SERIALNUM", MboConstants.REQUIRED, False)   # noqa: F821


initialize_serialnum_flags()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_ASSET_SERIALNUM_INIT",
    "description": "Initialize read-only / required flags on TMG_SERIALNUM based on ROTATING flag.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_ASSET_SERIALNUM_INIT",
        "launchPointType": "ATTRIBUTE",
        "active": True,
        "objectName": "ASSET",
        "attributeName": "TMG_SERIALNUM",
        "events": {"initializevalue": True},
        "description": "Toggle TMG_SERIALNUM read-only based on ASSET.ROTATING."
    }]
}
