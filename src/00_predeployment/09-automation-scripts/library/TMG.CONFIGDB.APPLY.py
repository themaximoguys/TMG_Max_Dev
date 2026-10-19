# =============================================================================
# Script Name: TMG.CONFIGDB.APPLY
# Type: REST script handler (no launch point) - /maximo/api/script/TMG.CONFIGDB.APPLY
# Used by: maxdev dbconfig status / apply
#
# Stage 1 (this version): READ-ONLY discovery.
#   GET  ?mode=info  -> pending MAXOBJECTCFG rows, admin mode state, and the
#                       methods the CONFIGURE service exposes on this tenant.
# The apply step is added only after the tenant's real API is confirmed,
# so nothing here changes the database.
# Jython: no Python stdlib (Maximo ships none); java.* only.
# =============================================================================
from psdi.server import MXServer
from com.ibm.json.java import JSONObject, JSONArray

mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()
out = JSONObject()

mode = "info"
try:
    q = request.getQueryParam("mode")
    if q:
        mode = q
except:
    pass
out.put("mode", mode)

# Pending Database Configuration changes
pending = JSONArray()
cfg = mx.getMboSet("MAXOBJECTCFG", ui)
try:
    cfg.setWhere("changed != 'N'")
    cfg.reset()
    m = cfg.moveFirst()
    while m is not None:
        row = JSONObject()
        row.put("objectname", m.getString("OBJECTNAME"))
        row.put("changed", m.getString("CHANGED"))
        pending.add(row)
        m = cfg.moveNext()
finally:
    cfg.close()
out.put("pending", pending)
out.put("pending_count", pending.size())

# Admin mode state
try:
    out.put("adminmode", str(mx.isAdminModeOn(True)))
except Exception, e:
    out.put("adminmode", "unknown: " + str(e))

# What the CONFIGURE service offers on this release (names only; nothing is invoked)
methods = JSONArray()
try:
    svc = mx.lookup("CONFIGURE")
    out.put("configure_class", svc.getClass().getName())
    for meth in svc.getClass().getMethods():
        n = meth.getName()
        low = n.lower()
        if "config" in low or "apply" in low or "admin" in low or "struct" in low:
            methods.add(n + "(" + str(len(meth.getParameterTypes())) + ")")
except Exception, e:
    out.put("configure_error", str(e))
out.put("configure_methods", methods)

if mode != "info":
    out.put("error", "only mode=info is implemented; apply is added after discovery")

responseBody = out.serialize(True)

# Script Configuration (maxdev reads this block on deploy; keep it last)
scriptConfig = {
    "autoscript": "TMG.CONFIGDB.APPLY",
    "description": "maxdev DB Config helper: stage 1 read-only discovery (mode=info)",
    "version": "0.1.0",
    "active": True,
    "logLevel": "ERROR",
    "scriptLanguage": "python",
    "scriptLaunchPoints": []
}
