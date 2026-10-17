# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_WORKORDER_OBJ_SAVE_BEFORE
# Launch Point Name: TMG_WORKORDER_OBJ_SAVE_BEFORE
# Launch Point Type: OBJECT
# Object: WORKORDER
# Event: SAVE (before)
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Pre-save validation hub for WORKORDER. Enforces:
#   1. DESCRIPTION must not be empty.
#   2. ESTLABHRS must be non-negative.
#   3. If WORKTYPE='EM' (emergency), REPORTEDPRIORITY must be 1.
#
# Demonstrates:
#   - OBJECT SAVE before-event
#   - Multiple business rules in helper functions
#   - Proper exception re-raise without swallowing
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util import MXApplicationException
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_workorder_obj_save_before")


# =============================================================================
# Helpers
# =============================================================================
def _check_description():
    if mbo.isNull("DESCRIPTION"):                            # noqa: F821
        raise MXApplicationException("tmg", "wodescriptionrequired")
    desc = mbo.getString("DESCRIPTION")                      # noqa: F821
    if desc is None or len(desc.strip()) == 0:
        raise MXApplicationException("tmg", "wodescriptionrequired")


def _check_estlabhrs():
    if mbo.isNull("ESTLABHRS"):                              # noqa: F821
        return
    estlabhrs = mbo.getDouble("ESTLABHRS")                   # noqa: F821
    if estlabhrs < 0:
        raise MXApplicationException("tmg", "negativeestlabhrs")


def _check_emergency_priority():
    if mbo.isNull("WORKTYPE"):                               # noqa: F821
        return
    if mbo.getString("WORKTYPE") != "EM":                    # noqa: F821
        return
    if mbo.isNull("REPORTEDPRIORITY"):                       # noqa: F821
        raise MXApplicationException("tmg", "emrequirespriority")
    if mbo.getInt("REPORTEDPRIORITY") != 1:                  # noqa: F821
        raise MXApplicationException("tmg", "empriorityone")


# =============================================================================
# Main
# =============================================================================
def validate_workorder_save():
    if mbo is None:                                          # noqa: F821
        return
    try:
        _check_description()
        _check_estlabhrs()
        _check_emergency_priority()
    except MXApplicationException:
        # propagate — Maximo handles MXApplicationException natively
        raise
    except Exception as e:                                     # noqa
        _LOGGER.error("Unexpected error validating WORKORDER save: %s" % str(e))
        raise


validate_workorder_save()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_WORKORDER_OBJ_SAVE_BEFORE",
    "description": "Pre-save validations for WORKORDER (description, hours, emergency priority).",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_WORKORDER_OBJ_SAVE_BEFORE",
        "launchPointType": "OBJECT",
        "active": True,
        "objectName": "WORKORDER",
        "events": {"save": True, "beforesave": True},
        "description": "Validate WORKORDER fields before save."
    }]
}
