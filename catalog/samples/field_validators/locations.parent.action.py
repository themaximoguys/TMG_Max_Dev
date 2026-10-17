# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_LOCATIONS_PARENT_ACTION
# Launch Point Name: TMG_LOCATIONS_PARENT_ACTION
# Launch Point Type: ATTRIBUTE
# Object: LOCATIONS
# Field: PARENT
# Event: ACTION
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# When the user picks a PARENT location, cascade missing default values from
# the parent (failure class, GL account) to the child location — but never
# overwrite values the user has already typed.
#
# Demonstrates:
#   - ACTION event with related-object lookup
#   - Defensive MboSet open / close in finally
#   - Idempotent default-fill (only sets when child is null)
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import MboConstants
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_locations_parent_action")


# =============================================================================
# Main
# =============================================================================
def cascade_parent_defaults():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.isNull("PARENT"):                                 # noqa: F821
        return

    parent_set = None
    try:
        parent_set = mbo.getMboSet("$tmg_parent_lookup",     # noqa: F821
                                   "LOCATIONS",
                                   "location = :1 and siteid = :2")
        parent_set.setQbe("LOCATION", mbo.getString("PARENT"))           # noqa: F821
        parent_set.setQbe("SITEID", mbo.getString("SITEID"))             # noqa: F821

        parent = parent_set.getMbo(0)
        if parent is None:
            return

        # Cascade only fields the user hasn't already set
        if mbo.isNull("FAILURECODE") and not parent.isNull("FAILURECODE"):    # noqa: F821
            mbo.setValue("FAILURECODE",                                       # noqa: F821
                         parent.getString("FAILURECODE"),
                         MboConstants.NOACCESSCHECK)

        if mbo.isNull("GLACCOUNT") and not parent.isNull("GLACCOUNT"):        # noqa: F821
            mbo.setValue("GLACCOUNT",                                         # noqa: F821
                         parent.getString("GLACCOUNT"),
                         MboConstants.NOACCESSCHECK)

        _LOGGER.debug("Cascaded parent defaults to LOCATIONS %s" %
                      mbo.getString("LOCATION"))                              # noqa: F821
    finally:
        if parent_set is not None:
            try:
                parent_set.close()
            except Exception as ce:                                             # noqa
                _LOGGER.warn("Failed to close parent_set: %s" % str(ce))


cascade_parent_defaults()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_LOCATIONS_PARENT_ACTION",
    "description": "Cascade FAILURECODE and GLACCOUNT defaults from parent location.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_LOCATIONS_PARENT_ACTION",
        "launchPointType": "ATTRIBUTE",
        "active": True,
        "objectName": "LOCATIONS",
        "attributeName": "PARENT",
        "events": {"action": True},
        "description": "Cascade default values from parent location."
    }]
}
