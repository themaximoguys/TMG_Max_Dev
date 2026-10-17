# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_{NAME}.CRON.ACTION
# Launch Point Type: OBJECT (via SCRIPTCRONTASK)
# Active: True
# Debug Mode: False
# Logging: service implicit variable (no Java imports)
#
# =============================================================================
# Description:
# =============================================================================
# {PURPOSE_DESCRIPTION}
#
# Key Features:
# 1. {FEATURE_1}
# 2. {FEATURE_2}
# 3. {FEATURE_3}
#
# Cron Parameters (configured in Cron Task Setup):
# - {PARAM_1}: {PARAM_1_DESC}
# - {PARAM_2}: {PARAM_2_DESC}
#
# =============================================================================
# Author: Converted from {JAVA_CLASS}.java
# Naming Convention: {JAVA_CLASS}.java
#
# =============================================================================
# Revision History:
# =============================================================================
# Date         Author     Description
# {DATE}       {AUTHOR}   Converted from Java to Python automation script
# {ORIG_DATE}  {ORIG_AUTHOR} Original Java implementation
# =============================================================================

from psdi.server import MXServer
from psdi.util import MXApplicationException

SCRIPT_NAME = "tmg_{name}.cron.action"


def main():
    """
    Main cron task execution function.
    """
    service.log(SCRIPT_NAME + ": Starting execution")
    mxserver = MXServer.getMXServer()
    userInfo = mbo.getUserInfo()

    try:
        # Get cron task parameters
        # param1 = croninstance.getParamAsString("{PARAM_1}")
        # param2 = croninstance.getParamAsInt("{PARAM_2}")

        # ==========================================
        # CRON TASK LOGIC HERE
        # ==========================================

        # Example: Process records across sites
        # site_set = mxserver.getMboSet("SITE", userInfo)
        # site_set.setWhere("active=1")
        # site_set.reset()
        #
        # index = 0
        # while True:
        #     site_mbo = site_set.getMbo(index)
        #     if site_mbo is None:
        #         break
        #     site_id = site_mbo.getString("SITEID")
        #     process_site(site_id, mxserver, userInfo)
        #     index += 1

        service.log(SCRIPT_NAME + ": Execution completed successfully")

    except MXApplicationException as mxe:
        service.log_error(SCRIPT_NAME + ": Maximo error: " + str(mxe))
        raise
    except Exception as e:
        service.log_error(SCRIPT_NAME + ": Error: " + str(e))
        raise


def process_site(site_id, mxserver, userInfo):
    """
    Process records for a specific site.

    Args:
        site_id: Site ID to process
        mxserver: MXServer instance
        userInfo: UserInfo instance
    """
    service.log(SCRIPT_NAME + ": Processing site: " + site_id)

    # record_set = mxserver.getMboSet("{OBJECT}", userInfo)
    # record_set.setWhere("siteid = '" + site_id + "' and {ADDITIONAL_WHERE}")
    # record_set.reset()
    #
    # if not record_set.isEmpty():
    #     # Process records
    #     pass

    service.log(SCRIPT_NAME + ": Site " + site_id + " processing complete")


# Entry point
main()


# =============================================================================
# SCRIPT CONFIGURATION
# =============================================================================
# NOTE: Cron task scripts are bound via SCRIPTCRONTASK cron task instance,
# not via standard launch points. Create the cron task setup as follows:
#
# 1. Go to System Configuration > Platform Configuration > Cron Task Setup
# 2. Find or create cron task instance of type SCRIPTCRONTASK
# 3. Set the SCRIPTNAME parameter to this script's autoscript name
# 4. Configure schedule (e.g., every 15 min, daily, etc.)
# 5. Add any custom parameters needed
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_{NAME}.CRON.ACTION",
    "description": "{SCRIPT_DESCRIPTION}",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "cronSetup": {
        "cronTaskName": "SCRIPTCRONTASK",
        "instanceName": "TMG_{NAME}",
        "schedule": "{SCHEDULE}",
        "description": "{CRON_DESCRIPTION}",
        "parameters": [
            {"name": "SCRIPTNAME", "value": "TMG_{NAME}.CRON.ACTION"}
        ]
    }
}
