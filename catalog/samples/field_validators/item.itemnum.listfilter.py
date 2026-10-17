# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_ITEM_ITEMNUM_LISTFILTER
# Launch Point Name: TMG_ITEM_ITEMNUM_LISTFILTER
# Launch Point Type: ATTRIBUTE
# Object: ITEM
# Field: ITEMNUM
# Event: LIST (listfilter)
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Restrict ITEMNUM lookup to items in stock (current balance > 0) and matching
# the user's site context.
#
# Demonstrates:
#   - LISTFILTER event pattern
#   - SqlFormat with parameterized values (NEVER concatenate)
#   - Returning a where clause via setQbe / setWhere
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_item_itemnum_listfilter")


# =============================================================================
# Main
# =============================================================================
def filter_item_lookup():
    if mboset is None or mbo is None:                       # noqa: F821
        return

    user_site = ""
    try:
        if not mbo.isNull("SITEID"):                        # noqa: F821
            user_site = mbo.getString("SITEID")             # noqa: F821
    except Exception:
        user_site = ""

    sf = SqlFormat(mbo, "status = :status and exists "      # noqa: F821
                   "(select 1 from inventory inv where inv.itemnum = item.itemnum "
                   "and inv.siteid = :siteid and inv.curbal > 0)")
    sf.setObject(1, "ITEM", "STATUS", "ACTIVE")
    sf.setObject(2, "INVENTORY", "SITEID", user_site)
    mboset.setWhere(sf.format())                            # noqa: F821


filter_item_lookup()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_ITEM_ITEMNUM_LISTFILTER",
    "description": "Restrict ITEMNUM lookup to active items with stock at user's site.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_ITEM_ITEMNUM_LISTFILTER",
        "launchPointType": "ATTRIBUTE",
        "active": True,
        "objectName": "ITEM",
        "attributeName": "ITEMNUM",
        "events": {"list": True},
        "description": "Filter ITEM lookup to in-stock items at user's site."
    }]
}
