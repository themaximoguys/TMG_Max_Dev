# TMG_EXPORT_PRES — REST script handler: GET /maximo/api/script/TMG_EXPORT_PRES?app=WOTRACK
# Returns the App Designer presentation XML for one app, or the list of app names when
# no app is given. Used by maxdev extract/diff for appxml when MXAPIPRESENTATION does not
# return the PRESENTATION CLOB. Read-only.
import re
from psdi.server import MXServer

mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()

app = None
try:
    app = request.getQueryParam("app")
except:
    app = None

# App names are [A-Z0-9_]; reject anything else instead of building SQL from it.
if app and not re.match(r"^[A-Za-z0-9_]{1,30}$", app):
    responseBody = "INVALID APP NAME"
else:
    pset = mx.getMboSet("MAXPRESENTATION", ui)
    try:
        if app:
            pset.setWhere("app = '%s'" % app.upper())
            pset.reset()
            m = pset.getMbo(0)
            if m is None:
                responseBody = "NOT FOUND: " + app
            else:
                responseBody = m.getString("PRESENTATION")
        else:
            pset.setOrderBy("app")
            pset.reset()
            names = []
            m = pset.moveFirst()
            while m is not None:
                names.append(m.getString("APP"))
                m = pset.moveNext()
            responseBody = "\n".join(names)
    finally:
        pset.close()

# ── maxdev scriptConfig (managed: edit values, keep the block last) ──
scriptConfig = """{
  "active": true,
  "autoscript": "TMG_EXPORT_PRES",
  "description": "REST handler: export App Designer presentation XML (read-only)",
  "loglevel": "ERROR",
  "scriptlanguage": "python"
}"""
