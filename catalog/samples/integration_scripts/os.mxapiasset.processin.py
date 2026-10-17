# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_OS_MXAPIASSET_PROCESSIN
# Launch Point Name: TMG_OS_MXAPIASSET_PROCESSIN
# Launch Point Type: OBJECTSTRUCTURE (Process In)
# Object Structure: MXAPIASSET
# Exit: PROCESSIN
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# REST-API inbound exit for MXAPIASSET. Validates that the caller has
# permission to create/update assets at the requested SITEID by checking
# the user's TMG_SITE_ACCESS table.
#
# Demonstrates:
#   - Authorization check at REST boundary
#   - User-info access from the OS context
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_os_mxapiasset_processin")


# =============================================================================
# Helpers
# =============================================================================
def _user_has_site_access(user_id, siteid):
    if not user_id or not siteid:
        return False
    mxs = MXServer.getMXServer()
    s = None
    try:
        s = mxs.getMboSet("TMG_SITE_ACCESS", mbo.getUserInfo())   # noqa: F821
        sf = SqlFormat(None, "userid = :1 and siteid = :2 and granted = 1")
        sf.setObject(1, "TMG_SITE_ACCESS", "USERID", user_id)
        sf.setObject(2, "TMG_SITE_ACCESS", "SITEID", siteid)
        s.setWhere(sf.format())
        return s.count() > 0
    finally:
        if s is not None:
            try:
                s.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def process():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.isNull("SITEID"):                                 # noqa: F821
        return

    user_info = mbo.getUserInfo()                            # noqa: F821
    if user_info is None:
        return
    user_id = user_info.getUserName()
    siteid  = mbo.getString("SITEID")                        # noqa: F821

    if not _user_has_site_access(user_id, siteid):
        _LOGGER.warn("REST ASSET write rejected — user=%s no access to site=%s" %
                     (user_id, siteid))
        raise MXApplicationException("tmg", "nositeaccess")


process()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_OS_MXAPIASSET_PROCESSIN",
    "description": "Object Structure ASSET REST inbound: site-access authorization check.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_OS_MXAPIASSET_PROCESSIN",
        "launchPointType": "OBJECTSTRUCTURE",
        "active": True,
        "objectStructure": "MXAPIASSET",
        "exitType": "PROCESSIN",
        "description": "MXAPIASSET inbound REST authorization."
    }]
}
