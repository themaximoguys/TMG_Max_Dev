# ============================================================================
# Script: SYNC.{SERVICE}.{EXITTYPE}.IN
# Component: Enterprise Service
# Service: {SERVICE}
# Processing Point: {EXIT_DESC}
# Direction: Inbound
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
#   Component Type: Enterprise Service
#   Enterprise Service: {SERVICE}
#   Processing Point: {EXIT_DESC} (radio)
#
# Implicit Variables:
#   irData  - Internal (Maximo) StructureData (being built from external data)
#   erData  - External StructureData (received from source system)
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

SCRIPT_NAME = "SYNC.{SERVICE}.{EXITTYPE}.IN"


def process_inbound():
    """
    Process inbound integration data.

    For User Exit (USEREXIT):
        - Modify erData before it reaches the processing logic
        - Validate, transform, or filter incoming data

    For External Exit (EXTEXIT):
        - Transform erData to irData for Maximo consumption
        - Map external codes to Maximo values
        - Handle data enrichment and validation
    """
    service.log(SCRIPT_NAME + ": Processing inbound data")

    # ==========================================
    # INBOUND PROCESSING LOGIC HERE
    # ==========================================

    # --- USER EXIT Example ---
    # Trim whitespace from incoming fields
    # field_value = erData.getCurrentData("{OBJECT}").getString("FIELDNAME")
    # if field_value is not None:
    #     erData.getCurrentData("{OBJECT}").setValue("FIELDNAME", field_value.strip())

    # --- EXTERNAL EXIT Example ---
    # Transform external data to Maximo format
    # ext_status = erData.getCurrentData("{OBJECT}").getString("EXT_STATUS")
    # maximo_status = STATUS_MAP.get(ext_status, "WAPPR")
    # irData.getCurrentData("{OBJECT}").setValue("STATUS", maximo_status)

    # --- IN PROCESS Example ---
    # Custom validation before record creation/update
    # meter_value = erData.getCurrentData("METER").getDouble("READING")
    # last_reading = get_last_reading(meter_id)
    # if meter_is_continuous and meter_value < last_reading:
    #     service.log_warn("Continuous meter reading decreased - adjusting")
    #     # Handle rollover or error

    service.log(SCRIPT_NAME + ": Inbound processing completed")


# Entry point
try:
    process_inbound()
except Exception as e:
    service.log_error(SCRIPT_NAME + ": Error in inbound processing: " + str(e))
    raise


# ============================================================================
# SCRIPT CONFIGURATION
# ============================================================================
# NOTE: Integration scripts do NOT use launch points.
# They are bound by name via the Integration wizard.
# ============================================================================
scriptConfig = {
    "autoscript": "SYNC.{SERVICE}.{EXITTYPE}.IN",
    "description": "{SCRIPT_DESCRIPTION}",
    "version": "1.0.0",
    "active": True,
    "logLevel": "ERROR",
    "integrationBinding": {
        "componentType": "ENTERPRISE_SERVICE",
        "serviceName": "{SERVICE}",
        "processingPoint": "{EXIT_DESC}",
        "direction": "INBOUND"
    }
}
