# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_OS_MXAPIITEM_PROCESSIN
# Launch Point Name: TMG_OS_MXAPIITEM_PROCESSIN
# Launch Point Type: OBJECTSTRUCTURE (Process In)
# Object Structure: MXAPIITEM
# Exit: PROCESSIN
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# REST-API inbound exit for MXAPIITEM. Enforces ITEMNUM uppercase + maximum
# length, and rejects creation of an item with the same UPC code as an
# existing item.
#
# Demonstrates:
#   - REST inbound normalization (uppercase + length cap)
#   - Cross-record duplicate-key check via SqlFormat
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_os_mxapiitem_processin")
_MAX_ITEMNUM_LEN = 30


# =============================================================================
# Main
# =============================================================================
def process():
    if mbo is None:                                          # noqa: F821
        return

    if not mbo.isNull("ITEMNUM"):                            # noqa: F821
        raw = mbo.getString("ITEMNUM")                       # noqa: F821
        cleaned = raw.strip().upper()[:_MAX_ITEMNUM_LEN]
        if cleaned != raw:
            mbo.setValue("ITEMNUM", cleaned)                 # noqa: F821

    if mbo.toBeAdded() and not mbo.isNull("TMG_UPC"):        # noqa: F821
        upc = mbo.getString("TMG_UPC")                       # noqa: F821
        mxs = MXServer.getMXServer()
        s = None
        try:
            s = mxs.getMboSet("ITEM", mbo.getUserInfo())     # noqa: F821
            sf = SqlFormat(None, "tmg_upc = :1")
            sf.setObject(1, "ITEM", "TMG_UPC", upc)
            s.setWhere(sf.format())
            if s.count() > 0:
                _LOGGER.warn("REST ITEM creation rejected — duplicate TMG_UPC=%s" % upc)
                raise MXApplicationException("tmg", "duplicateupc")
        finally:
            if s is not None:
                try:
                    s.close()
                except Exception:
                    pass


process()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_OS_MXAPIITEM_PROCESSIN",
    "description": "Object Structure ITEM REST inbound: normalize ITEMNUM, reject duplicate UPC.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_OS_MXAPIITEM_PROCESSIN",
        "launchPointType": "OBJECTSTRUCTURE",
        "active": True,
        "objectStructure": "MXAPIITEM",
        "exitType": "PROCESSIN",
        "description": "MXAPIITEM inbound REST validation."
    }]
}
