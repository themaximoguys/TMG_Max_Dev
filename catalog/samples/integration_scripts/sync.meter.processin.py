# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_SYNC_METER_PROCESSIN
# Launch Point Name: TMG_SYNC_METER_PROCESSIN
# Launch Point Type: SUBSCRIBE (Process In)
# Service: TMG_METER_IN
# Exit: PROCESSIN
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Inbound METERREADING processing. Flag readings that are out of expected
# tolerance against the prior reading on the same ASSET+METERNAME. Out-of-
# tolerance readings are accepted but flagged TMG_OUT_OF_TOLERANCE = true
# so a downstream cron / dashboard can surface them.
#
# Demonstrates:
#   - Inbound time-series anomaly flagging (no rejection)
#   - Lookup of the latest prior reading
#   - Tolerance percentage configuration
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.server import MXServer
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_sync_meter_processin")
_TOLERANCE_PCT = 0.30  # 30% jump from prior reading flags as out-of-tolerance


# =============================================================================
# Helpers
# =============================================================================
def _previous_reading(assetnum, meter):
    mxs = MXServer.getMXServer()
    s = None
    try:
        s = mxs.getMboSet("METERREADING", mbo.getUserInfo())   # noqa: F821
        sf = SqlFormat(None,
                       "assetnum = :1 and metername = :2")
        sf.setObject(1, "METERREADING", "ASSETNUM",  assetnum)
        sf.setObject(2, "METERREADING", "METERNAME", meter)
        s.setWhere(sf.format())
        s.setOrderBy("READINGDATE desc")
        prior = s.getMbo(0)
        if prior is None or prior.isNull("READING"):
            return None
        return prior.getDouble("READING")
    finally:
        if s is not None:
            try:
                s.close()
            except Exception:
                pass


# =============================================================================
# Main
# =============================================================================
def process_meter_in():
    if mbo is None:                                          # noqa: F821
        return
    if mbo.isNull("READING") or mbo.isNull("ASSETNUM") or mbo.isNull("METERNAME"):   # noqa: F821
        return

    new_reading = mbo.getDouble("READING")                   # noqa: F821
    assetnum    = mbo.getString("ASSETNUM")                  # noqa: F821
    meter       = mbo.getString("METERNAME")                 # noqa: F821

    prior = _previous_reading(assetnum, meter)
    if prior is None or prior == 0:
        return

    deviation = abs(new_reading - prior) / prior
    if deviation > _TOLERANCE_PCT:
        mbo.setValue("TMG_OUT_OF_TOLERANCE", True)           # noqa: F821
        _LOGGER.warn("Out-of-tolerance reading: ASSET=%s METER=%s prior=%s new=%s (%.1f%%)" %
                     (assetnum, meter, prior, new_reading, deviation * 100))


process_meter_in()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_SYNC_METER_PROCESSIN",
    "description": "Inbound METERREADING: flag out-of-tolerance vs prior reading.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_SYNC_METER_PROCESSIN",
        "launchPointType": "SUBSCRIBE",
        "active": True,
        "enterpriseService": "TMG_METER_IN",
        "exitType": "PROCESSIN",
        "description": "Inbound METER reading exit."
    }]
}
