# ============================================================================
# Script: PUBLISH.{CHANNEL}.{EXITTYPE}.OUT
# Component: Publish Channel
# Channel: {CHANNEL}
# Processing Point: {EXIT_DESC}
# Direction: Outbound
# Logging: service implicit variable (no Java imports)
#
# Description:
# {PURPOSE_DESCRIPTION}
#
# Binding: Name-based (NO launch point)
# Auto-populates: Script{EXIT_CLASS} in Processing Class field
#
# Wizard Path:
# Automation Scripts > Create > Script for Integration
#   Component Type: Publish Channel
#   Publish Channel: {CHANNEL}
#   Processing Point: {EXIT_DESC} (radio)
#
# Implicit Variables:
#   irData  - Internal (Maximo) StructureData
#   erData  - External StructureData (being built for destination)
#   mbo     - Current MBO being published (available in Publish Channel exits)
#   service - MicService for logging/errors
#
# Converted From: tmg/iface/{MODULE}/{JAVA_CLASS}.java
#
# History:
# Date       Developer  Description
# ---------- ---------- ---------------------------------------------------
# {DATE}     {AUTHOR}   Converted from Java to Python automation script
# {ORIG_DATE} {ORIG_AUTHOR} Original Java implementation
# ============================================================================

from psdi.server import MXServer

SCRIPT_NAME = "PUBLISH.{CHANNEL}.{EXITTYPE}.OUT"


# ==========================================
# USER EXIT: Modify data before/after publish
# EXTERNAL EXIT: Transform data for external system
# ==========================================

def process_outbound():
    """
    Process outbound integration data.

    For User Exit (USEREXIT):
        - Modify irData (internal) before it reaches the external exit
        - Set TMG_EVENTTYPE, filter records, add/remove elements

    For External Exit (EXTEXIT):
        - Transform irData to erData for the external system
        - Map statuses, enrich fields, filter attributes
    """
    service.log(SCRIPT_NAME + ": Processing outbound data")

    # Get key information from the MBO
    # key_value = mbo.getString("{KEY_FIELD}")
    # status = mbo.getString("STATUS")
    # siteid = mbo.getString("SITEID")

    # ==========================================
    # OUTBOUND PROCESSING LOGIC HERE
    # ==========================================

    # --- USER EXIT Example ---
    # Set event type based on MBO state
    # if mbo.toBeAdded():
    #     event_type = "ADD"
    # elif mbo.toBeDeleted():
    #     event_type = "DELETE"
    # else:
    #     event_type = "UPDATE"
    #
    # irData.getCurrentData("{OBJECT}").setValue("TMG_EVENTTYPE", event_type)

    # --- EXTERNAL EXIT Example ---
    # Map internal status to external code
    # internal_status = irData.getCurrentData("{OBJECT}").getString("STATUS")
    # external_status = STATUS_MAP.get(internal_status, internal_status)
    # erData.getCurrentData("{OBJECT}").setValue("EXTSTATUS", external_status)

    service.log(SCRIPT_NAME + ": Outbound processing completed")


# Entry point
try:
    process_outbound()
except Exception as e:
    service.log_error(SCRIPT_NAME + ": Error in outbound processing: " + str(e))
    raise


# ============================================================================
# SCRIPT CONFIGURATION
# ============================================================================
# NOTE: Integration scripts do NOT use launch points.
# They are bound by name via the Integration wizard.
# The script name must match what Maximo expects for the exit type.
# ============================================================================
scriptConfig = {
    "autoscript": "PUBLISH.{CHANNEL}.{EXITTYPE}.OUT",
    "description": "{SCRIPT_DESCRIPTION}",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "integrationBinding": {
        "componentType": "PUBLISH_CHANNEL",
        "channelName": "{CHANNEL}",
        "processingPoint": "{EXIT_DESC}",
        "direction": "OUTBOUND"
    }
}
