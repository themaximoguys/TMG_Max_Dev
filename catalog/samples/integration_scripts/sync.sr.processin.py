# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_SYNC_SR_PROCESSIN
# Launch Point Name: TMG_SYNC_SR_PROCESSIN
# Launch Point Type: SUBSCRIBE (Process In)
# Service: TMG_SR_IN
# Exit: PROCESSIN
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Inbound Service Request processing from a public chatbot/email-to-ticket
# pipeline. Auto-classify the SR by scanning DESCRIPTION + LONGDESCRIPTION
# for keywords; set CLASSSTRUCTUREID + INTERNALPRIORITY accordingly.
#
# Demonstrates:
#   - Inbound classification + priority assignment via keyword scan
#   - Concatenating DESCRIPTION and LONGDESCRIPTION before scan
#   - Defaults applied only when upstream didn't provide them
#
# =============================================================================
# Imports
# =============================================================================
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_sync_sr_processin")

# (CLASSSTRUCTUREID, priority, [keywords])
_RULES = [
    ("TMG_SAFETY_INCIDENT",   1, ["injury", "fire", "leak", "spill", "shock"]),
    ("TMG_OUTAGE",            2, ["down", "outage", "no power", "broken", "stopped"]),
    ("TMG_SLOW_PERFORMANCE",  3, ["slow", "intermittent", "lag", "delay"]),
    ("TMG_GENERAL_REQUEST",   4, ["request", "question", "info"]),
]


# =============================================================================
# Helpers
# =============================================================================
def _full_text():
    parts = []
    if not mbo.isNull("DESCRIPTION"):                        # noqa: F821
        parts.append(mbo.getString("DESCRIPTION"))           # noqa: F821
    try:
        if not mbo.isNull("DESCRIPTION_LONGDESCRIPTION"):    # noqa: F821
            parts.append(mbo.getString("DESCRIPTION_LONGDESCRIPTION"))   # noqa: F821
    except Exception:
        pass
    return " ".join(parts).lower()


def _classify(text):
    for cls, priority, keywords in _RULES:
        for kw in keywords:
            if kw in text:
                return cls, priority
    return None, None


# =============================================================================
# Main
# =============================================================================
def process_sr_in():
    if mbo is None:                                          # noqa: F821
        return

    text = _full_text()
    if len(text) == 0:
        return

    cls, priority = _classify(text)
    if cls is None:
        return

    if mbo.isNull("CLASSSTRUCTUREID"):                       # noqa: F821
        mbo.setValue("CLASSSTRUCTUREID", cls)                # noqa: F821
    if mbo.isNull("INTERNALPRIORITY"):                       # noqa: F821
        mbo.setValue("INTERNALPRIORITY", priority)           # noqa: F821

    _LOGGER.info("Auto-classified SR — class=%s priority=%s" % (cls, priority))


process_sr_in()


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_SYNC_SR_PROCESSIN",
    "description": "Inbound SR: keyword-based classification + INTERNALPRIORITY assignment.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": [{
        "launchPointName": "TMG_SYNC_SR_PROCESSIN",
        "launchPointType": "SUBSCRIBE",
        "active": True,
        "enterpriseService": "TMG_SR_IN",
        "exitType": "PROCESSIN",
        "description": "Inbound SR auto-classifier."
    }]
}
