"""Offline tests: python3 -m unittest discover -s tests -v"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import license_fixture  # noqa: E402,F401
from fake_maximo import FakeMaximo, Resp  # noqa: E402

from maxdev import appxml, engine, ibm_mcp, registry, store  # noqa: E402
from maxdev.client import MaximoClient, Target, resource_id  # noqa: E402

LIVE_XML = ('<?xml version="1.0" encoding="UTF-8"?>\n<presentation id="WOTRACK" xmlns:x="urn:x">'
            '<page id="p"><tab id="main"><textbox id="t1" dataattribute="WONUM"/>'
            '<textbox id="t_ui" dataattribute="ADDEDINUI"/></tab></page></presentation>')
REPO_XML = ('<?xml version="1.0" encoding="UTF-8"?>\n<presentation id="WOTRACK">'
            '<page id="p"><tab id="main"><textbox id="t1" dataattribute="WONUM" label="Work Order"/>'
            '<textbox id="t_new" dataattribute="CUSTOMER_EMAIL"/></tab></page></presentation>')


class Base(unittest.TestCase):
    STRUCTS = ("MHDOMAIN", "MXAPIDOMAIN", "MXAPIATTRFORMULA", "MXAPIAUTOSCRIPT", "MXAPIPRESENTATION",
               "MXAPIACTION", "MXOBJECTCFG", "MXAPIASSET")

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self._saved = (registry.SRC, list(registry.ROOTS), engine.STATE)
        registry.SRC = self.tmp / "src"
        registry.ROOTS[:] = [registry.SRC]
        engine.STATE = self.tmp / ".maxdev"
        registry._os_cache.clear()
        os.environ.update({"MAXIMO_BASE_URL": FakeMaximo.base, "MAXIMO_API_KEY": "k", "MAXIMO_PROTECTED": "false"})
        self.fake = FakeMaximo(self.STRUCTS)
        self.s = engine.Session("unittest", client=MaximoClient(Target("unittest", FakeMaximo.base, "k"), self.fake))

    def tearDown(self):
        registry.SRC, registry.ROOTS[:], engine.STATE = self._saved[0], self._saved[1], self._saved[2]
        shutil.rmtree(self.tmp)
        for k in ("MAXIMO_BASE_URL", "MAXIMO_API_KEY", "MAXIMO_PROTECTED"):
            os.environ.pop(k, None)


class RegistryTests(unittest.TestCase):
    def test_every_type_valid(self):
        ts = registry.types()
        self.assertGreaterEqual(len(ts), 40)
        folders = [t.folder for t in ts.values()]
        self.assertEqual(len(folders), len(set(folders)), "two types share a folder")
        for t in ts.values():
            self.assertTrue(t.key, t.id)

    def test_layer_order(self):
        order = [t.id for t in registry.ordered()]
        self.assertLess(order.index("sigoption"), order.index("appxml"))
        self.assertLess(order.index("object"), order.index("autoscript"))
        self.assertLess(order.index("persongroup"), order.index("workflow"))

    def test_resource_id_padding(self):
        self.assertEqual(resource_id("AB"), "_QUI-")      # '=' must be written as '-'


class StoreTests(unittest.TestCase):
    def test_script_roundtrip(self):
        rec = {"autoscript": "WO.SAVE", "scriptlanguage": "python", "active": True,
               "source": "x = 1\nprint(x)\n",
               "scriptlaunchpoint": [{"launchpointname": "WO_SAVE", "launchpointtype": "OBJECT", "objectname": "WORKORDER"}]}
        text = store.render_script(rec)
        p = Path(tempfile.mkdtemp()) / "WO.SAVE.py"
        p.write_text(text)
        back = store.parse_script(p)
        self.assertEqual(back["source"], rec["source"])
        self.assertEqual(back["scriptlaunchpoint"], rec["scriptlaunchpoint"])
        self.assertEqual(store.render_script(back), text, "render(parse(x)) must be byte-identical")
        self.assertEqual(store.script_folder(rec), "object")

    def test_js_roundtrip(self):
        rec = {"autoscript": "LIB.JS", "scriptlanguage": "javascript", "source": "var a = 1;\n"}
        p = Path(tempfile.mkdtemp()) / "LIB.JS.js"
        p.write_text(store.render_script(rec))
        self.assertEqual(store.parse_script(p)["source"], "var a = 1;\n")

    def test_filename_composite(self):
        t = registry.get("relationship")
        self.assertEqual(store.filename(t, {"parent": "ASSET", "name": "OPEN WO"}), "ASSET__OPEN_WO")


class AppXmlTests(unittest.TestCase):
    def test_loss_detected(self):
        c = appxml.compare(LIVE_XML, REPO_XML)
        self.assertEqual(c["verdict"], "DESTRUCTIVE")
        self.assertEqual(c["loss_sample"], ["textbox|t_ui"])
        self.assertEqual(c["changed"], 1)

    def test_pretty_is_lossless_and_idempotent(self):
        one_line = LIVE_XML.replace("\n", " ")
        out = appxml.pretty(one_line)
        self.assertGreater(out.count("\n"), 4)
        self.assertEqual(appxml.fingerprints(out), appxml.fingerprints(one_line))
        self.assertEqual(appxml.pretty(out), out)
        self.assertIn('xmlns:x="urn:x"', out)

    def test_merge_keeps_live_and_adds_repo(self):
        out, stats = appxml.merge(LIVE_XML, REPO_XML)
        self.assertIn("ADDEDINUI", out)          # kept
        self.assertIn("CUSTOMER_EMAIL", out)     # added
        self.assertIn('label="Work Order"', out) # modified
        self.assertIn('xmlns:x="urn:x"', out)    # unused namespace re-injected
        self.assertEqual(appxml.compare(LIVE_XML, out)["loss"], 0)


class EngineTests(Base):
    def test_extract_requires_filter(self):
        with self.assertRaises(ValueError):
            engine.extract(self.s, "domain")

    def test_extract_then_deploy_roundtrip(self):
        self.fake.seed("mhdomain", {"domainid": "TMGPRIO", "domaintype": "ALN", "_rowstamp": "9",
                                    "alndomain": [{"value": "1"}]},
                       {"domainid": "OTHER", "domaintype": "ALN"})
        r = engine.extract(self.s, "domain", like="TMG")
        self.assertEqual(r["os"], "MHDOMAIN")                 # first existing structure wins
        self.assertEqual(r["records"], 1)
        f = registry.SRC / "03-domains/TMGPRIO.json"
        rec = json.loads(f.read_text())
        self.assertNotIn("href", rec)
        self.assertNotIn("_rowstamp", rec)
        again = engine.extract(self.s, "domain", like="TMG")
        self.assertEqual(again["written"], 0, "re-extract of unchanged record must not rewrite the file")

        rec["description"] = "Priority"
        f.write_text(store.dumps(rec))
        dry = engine.deploy(self.s, engine.resolve_files("domain", ["TMGPRIO"], None))
        self.assertEqual(dry["results"][0]["action"], "would-update")
        self.assertFalse(any(c[2] == "PATCH" for c in self.fake.calls), "dry run must not write")
        live = engine.deploy(self.s, engine.resolve_files("domain", ["TMGPRIO"], None), apply=True)
        self.assertEqual(live["results"][0]["action"], "updated")
        self.assertTrue(Path(engine.STATE / "receipts/unittest").exists())
        d = engine.diff(self.s, engine.resolve_files("domain", ["TMGPRIO"], None))
        self.assertEqual(d["results"][0]["status"], "same")

    def test_protected_env_refuses(self):
        self.s.protected = True
        with self.assertRaises(PermissionError):
            engine.deploy(self.s, [], apply=True)

    def test_ambiguous_key_refused(self):
        self.fake.seed("mhdomain", {"domainid": "DUP"}, {"domainid": "DUP"})
        t = registry.get("domain")
        store.save_json(t, {"domainid": "DUP", "description": "x"})
        r = engine.deploy(self.s, engine.resolve_files("domain", ["DUP"], None), apply=True)
        self.assertEqual(r["results"][0]["action"], "FAILED")
        self.assertIn("refusing to guess", r["results"][0]["error"])

    def test_replace_rolls_back_on_failure(self):
        self.fake.seed("mxapiattrformula", {"objectname": "ASSET", "attributename": "CNT", "formula": "OLD"})
        t = registry.get("formula")
        store.save_json(t, {"objectname": "ASSET", "attributename": "CNT", "formula": "NEW"})
        self.fake.fail_create.add("mxapiattrformula")
        # rollback re-POST also fails in the fake, so allow it once by failing only first create
        orig = self.fake.request
        state = {"n": 0}

        def flaky(method, url, **kw):
            if method == "POST" and url.endswith("/mxapiattrformula") and not kw.get("headers", {}).get("x-method-override"):
                state["n"] += 1
                if state["n"] > 1:
                    self.fake.fail_create.discard("mxapiattrformula")
            return orig(method, url, **kw)
        self.fake.request = flaky
        r = engine.deploy(self.s, engine.resolve_files("formula", ["ASSET__CNT"], None), apply=True)
        self.assertEqual(r["results"][0]["action"], "FAILED")
        rows = self.fake.db["mxapiattrformula"]
        self.assertEqual([x["formula"] for x in rows], ["OLD"], "old row must be restored")

    def test_action_groups_after_members(self):
        t = registry.get("action")
        store.save_json(t, {"action": "AGRP", "type": "GROUP"})
        store.save_json(t, {"action": "ZSINGLE", "type": "SETVALUE"})
        names = [f.stem for _, f in engine.resolve_files("action", None, None)]
        self.assertEqual(names, ["ZSINGLE", "AGRP"])

    def test_autoscript_deploy_sends_source_without_config_block(self):
        t = registry.get("autoscript")
        path, _ = store.save_script(t, {"autoscript": "TMG.LIB", "scriptlanguage": "python", "source": "a = 1\n"})
        engine.deploy(self.s, [(t, path)], apply=True)
        live = self.fake.db["mxapiautoscript"][0]
        self.assertEqual(live["source"], "a = 1\n")

    def test_appxml_deploy_merges_and_backs_up(self):
        self.fake.seed("mxapipresentation", {"app": "WOTRACK", "presentation": LIVE_XML})
        t = registry.get("appxml")
        path, _ = store.save_appxml(t, "WOTRACK", REPO_XML)
        dry = engine.deploy(self.s, [(t, path)])
        self.assertEqual(dry["results"][0]["action"], "would-merge")
        r = engine.deploy(self.s, [(t, path)], apply=True)
        self.assertEqual(r["results"][0]["action"], "merged", r)
        live = self.fake.db["mxapipresentation"][0]["presentation"]
        self.assertIn("ADDEDINUI", live)
        self.assertIn("CUSTOMER_EMAIL", live)
        self.assertTrue(Path(engine.STATE / ".." / r["results"][0]["backup"]).exists() or
                        Path(r["results"][0]["backup"]).exists())

    def test_appxml_silent_drop_detected(self):
        self.fake.seed("mxapipresentation", {"app": "WOTRACK", "presentation": LIVE_XML})
        self.fake.drop_writes.add("mxapipresentation")
        t = registry.get("appxml")
        path, _ = store.save_appxml(t, "WOTRACK", REPO_XML)
        r = engine.deploy(self.s, [(t, path)], apply=True)
        self.assertEqual(r["results"][0]["action"], "FAILED")
        self.assertIn("read-back", r["results"][0]["error"])

    def test_stop_on_first_failure(self):
        t = registry.get("domain")
        store.save_json(t, {"domainid": "A1"})
        store.save_json(t, {"domainid": "B1"})
        self.fake.fail_create.add("mhdomain")
        r = engine.deploy(self.s, engine.resolve_files("domain", None, None), apply=True)
        self.assertEqual([x["action"] for x in r["results"]], ["FAILED", "not-attempted"])

    def test_bulk_data_load(self):
        from maxdev import data
        self.fake.seed("mxapiasset", {"assetnum": "A1", "siteid": "S", "description": "old"})
        f = self.tmp / "assets.csv"
        f.write_text("assetnum,siteid,description\nA1,S,new\nA2,S,added\n")
        r = data.load(self.s, "MXAPIASSET", f, ["assetnum", "siteid"], apply=True)
        self.assertEqual((r["ok"], r["failed"]), (2, 0))
        self.assertEqual(sorted(x["description"] for x in self.fake.db["mxapiasset"]), ["added", "new"])


class TmgFormatTests(unittest.TestCase):
    SAMPLES = Path(__file__).resolve().parents[1] / "catalog" / "samples"

    def test_every_tmg_sample_parses(self):
        files = sorted(self.SAMPLES.rglob("*.py"))
        self.assertGreaterEqual(len(files), 60)
        for f in files:
            rec = store.parse_script(f)
            self.assertTrue(rec["autoscript"], f.name)
            self.assertNotIn("scriptConfig", rec["source"], f"{f.name}: config block leaked into deployed source")

    def test_tmg_object_events_to_flags(self):
        from maxdev import scriptconfig as sc
        rec, _ = sc.tmg_to_record({"autoscript": "X", "logLevel": "INFO", "scriptLaunchPoints": [
            {"launchPointName": "X", "launchPointType": "OBJECT", "objectName": "WORKORDER",
             "events": {"save": True, "beforesave": True}}]})
        lp = rec["scriptlaunchpoint"][0]
        self.assertEqual((lp["addaction"], lp["saveaction"], lp["beforesave"]), (True, True, True))
        self.assertEqual(rec["loglevel"], "INFO")

    def test_cron_and_integration_not_sent_as_launch_points(self):
        from maxdev import scriptconfig as sc
        rec, notes = sc.tmg_to_record({"autoscript": "P", "cronSetup": {"x": 1}, "scriptLaunchPoints": [
            {"launchPointName": "P", "launchPointType": "PUBLISH"}]})
        self.assertEqual(rec["scriptlaunchpoint"], [])
        self.assertNotIn("cronSetup", rec)
        self.assertTrue(notes)

    def test_tmg_roundtrip_stable(self):
        f = next(self.SAMPLES.rglob("*.obj.save.before.py"))
        rec = store.parse_script(f)
        rec.pop("_notes", None)
        tmp = Path(tempfile.mkdtemp()) / "a.py"
        tmp.write_text(store.render_script(rec, "tmg"))
        again = store.parse_script(tmp)
        again.pop("_notes", None)
        self.assertEqual(again, rec)


class BuilderTests(unittest.TestCase):
    def test_lint_catches_hard_rules(self):
        from maxdev import builder
        bad = ('from psdi.util.logging import MXLoggerFactory\nx = f"{1}"\nprint("x")\n'
               'mbo.getMboSet("A").setWhere("a=\'" + v + "\'")\nservice.log("x")\nscriptConfig = {}\n')
        rules = {i["rule"] for i in builder.lint_text(bad, "T.py") if i["level"] == "error"}
        self.assertTrue({"no-fstring", "no-print", "sql-concat", "one-logging-style"} <= rules, rules)

    def test_templates_exist_for_every_kind(self):
        from maxdev import builder
        for kind in builder.KINDS:
            self.assertTrue(builder.template_path(kind).exists(), kind)

    def test_java_analysis(self):
        from maxdev import builder
        j = Path(tempfile.mkdtemp()) / "WOMbo.java"
        j.write_text("public class WOMbo extends WO { public void save() {} public void init() {} }")
        r = builder.analyze_java(j)
        self.assertEqual(r["family"], "object")
        self.assertEqual(r["method_to_template"]["save"], "object_save_before")


class DashboardTests(Base):
    STRUCTS = Base.STRUCTS + ("MXAPIQUERY", "MXAPIKPIMAIN", "MXAPIWORKQUEUE", "TMGMXSCTEMPLATE",
                              "MXAPIVIEWMANAGER", "MXAPIGROUP")

    def setUp(self):
        super().setUp()
        from maxdev import dashboard
        self.dash = dashboard
        self._manifests = dashboard.MANIFESTS
        dashboard.MANIFESTS = self.tmp / "manifests"

    def tearDown(self):
        self.dash.MANIFESTS = self._manifests
        super().tearDown()

    def test_sample_spec_is_valid(self):
        spec = self.dash.load_spec("maintenance_supervisor")
        self.assertEqual(self.dash.validate(spec), [])

    def test_validate_reports_every_problem(self):
        errs = self.dash.validate({"name": "bad name", "queries": [{"name": "Q", "app": "WOTRACK"}],
                                   "portlets": [{"type": "resultset", "query": "NOPE", "columns": ["A"], "chart": "B"},
                                                {"type": "kpilist", "kpis": ["MISSING"]}, {"type": "clock"}]})
        text = "\n".join(errs)
        for want in ("name:", "description:", "missing where", "'NOPE' is not in queries",
                     "chart column 'B'", "['MISSING'] are not in kpis", "type must be one of"):
            self.assertIn(want, text)
        now = self.dash.validate({"queries": [{"name": "Q", "app": "A", "where": "d < {now} or e < :SYSDATE"}]})
        self.assertTrue(any(e.startswith("database:") for e in now))
        self.assertTrue(any(":sysdate" in e for e in now))

    def test_build_writes_records_and_manifest(self):
        r = self.dash.build("maintenance_supervisor")
        types = [f["type"] for f in r["files"]]
        self.assertEqual(types.count("query"), 3)
        self.assertEqual(types.count("kpi"), 3)
        self.assertEqual(types.count("workqueue"), 2)
        self.assertEqual(types[:2], ["securitygroup", "apprights"])
        self.assertNotIn("grant", types, "APPLICATIONAUTH rejects OPDASHBOARD/OS apps; apprights uses MXAPIGROUP")
        self.assertEqual(types[-2:], ["view", "startcenter"])
        q = json.loads((registry.SRC / "07-app-designer/_queries/WOTRACK__TMG_OPS_OVERDUE_WO.json").read_text())
        self.assertEqual((q["app"], q["owner"]), ("WOTRACK", "MAXADMIN"))
        self.assertNotIn("queryid", q)
        k = json.loads((registry.SRC / "19-kpi/TMGOPSBACKLOG.json").read_text())
        self.assertTrue(k["clause"].startswith("where "))
        self.assertNotIn("kpivalue", k)
        self.assertNotIn("langcode", k)
        self.assertIn("targcompdate < GETDATE()", json.loads(
            (registry.SRC / "19-kpi/TMGOPSOVERDUE.json").read_text())["clause"])
        wq = json.loads((registry.SRC / "07-app-designer/_workqueues/TMG_OPS_OVERDUE_WO.json").read_text())
        order = {c["attributename"]: c["columnorder"] for c in wq["workqueuecols"]}
        self.assertEqual(order, {"WONUM": 1, "DESCRIPTION": 2, "STATUS": 3, "WOPRIORITY": 4, "TARGCOMPDATE": 5})
        self.assertEqual(list(order), sorted(order), "children sorted as Maximo returns them")
        self.assertEqual(wq["clausename"], "WOTRACK:TMG OPS OVERDUE WO")
        m = yaml_load(self.dash.MANIFESTS / "TMG_OPS_SUPERVISOR.yaml")
        self.assertEqual(len(m["items"][0]["path"]), len(r["files"]))
        self.assertTrue(any("Start Center Template" in x for x in m["manual"]))
        self.assertTrue(any("Operational Dashboard tab" in x for x in m["manual"]))
        self.assertFalse(any("Applications: grant" in x for x in m["manual"]), "rights are deployed, not manual")
        r = json.loads((registry.SRC / "02-security/app-rights/TMGOPSSUP.json").read_text())["rights"]
        self.assertEqual(r["OPDASHBOARD"], ["READ", "INSERT_PRIVATE"])
        self.assertEqual(r["MXAPIVIEWMANAGER"], ["READ", "SAVE", "INSERT"])
        self.assertTrue(any("KPICronTask" in x for x in m["manual"]), "trend KPI needs the cron step")
        again = self.dash.build("maintenance_supervisor")
        self.assertFalse(any(f["changed"] for f in again["files"]), "rebuild of an unchanged spec must not rewrite")

    def test_startcenter_xml_references_queries_and_kpis(self):
        import xml.etree.ElementTree as ET
        self.dash.build("maintenance_supervisor", write_manifest=False)
        sc = json.loads((registry.SRC / "07-app-designer/_startcenters/TMG_OPS_SUPERVISOR.json").read_text())
        root = ET.fromstring(sc["presentation"].split("?>", 1)[1])
        self.assertEqual(root.get("contentuid"), "TMG_OPS_SUPERVISOR")
        rs = root.findall("resultset")
        self.assertEqual({r.get("queryclausename") for r in rs},
                         {"TMG OPS OVERDUE WO", "TMG OPS EMERGENCY WO", "TMG OPS WAITING MATERIAL"})
        overdue = next(r for r in rs if r.get("queryclausename") == "TMG OPS OVERDUE WO")
        prio = next(a for a in overdue.findall("attribute") if a.get("querycolumn") == "WOPRIORITY")
        self.assertEqual((prio.get("isgraphon"), prio.get("isconditionset")), ("1", "1"))
        self.assertEqual(overdue.get("showchart"), "1")
        self.assertEqual([k.get("kpiname") for k in root.find("kpilist")],
                         ["TMGOPSBACKLOG", "TMGOPSOVERDUE", "TMGOPSEMERG"])
        uids = [e.get("contentuid") for e in root.iter() if e.get("contentuid")]
        self.assertEqual(len(uids), len(set(uids)), "contentuids must be unique within a template")
        for col in ("0", "1"):
            orders = [int(e.get("ordernum")) for e in root if e.get("columnnum") == col]
            self.assertEqual(orders, list(range(1, len(orders) + 1)))

    def test_deploy_order_puts_startcenter_after_its_sources(self):
        self.dash.build("maintenance_supervisor")
        from maxdev import manifest
        m = manifest.load(str(self.dash.MANIFESTS / "TMG_OPS_SUPERVISOR.yaml"))
        order = [t.id for t, _ in manifest.items(m)]
        self.assertEqual(order[0], "securitygroup")
        self.assertLess(max(i for i, t in enumerate(order) if t == "query"), order.index("workqueue"))
        self.assertLess(max(i for i, t in enumerate(order) if t == "kpi"), order.index("startcenter"))
        self.assertLess(max(i for i, t in enumerate(order) if t == "workqueue"), order.index("view"))
        dry = engine.deploy(self.s, manifest.items(m))
        self.assertEqual({r["action"] for r in dry["results"] if r["type"] != "apprights"}, {"would-create"})
        self.assertEqual(next(r for r in dry["results"] if r["type"] == "apprights")["action"], "would-grant")
        keys = {r["type"]: r["key"] for r in dry["results"]}
        self.assertEqual(keys["startcenter"], {"contentuid": "TMG_OPS_SUPERVISOR"})
        self.assertEqual(keys["view"]["viewid"], "TMGOPSSUPERVISOR")

    def test_opdashboard_view_matches_ootb_shape(self):
        spec = self.dash.load_spec("maintenance_supervisor")
        v = self.dash.view_record(spec)
        self.assertEqual((v["app"], v["componentid"], v["viewtype"]), ("OPDASHBOARD", "NX_PV", "DASHBOARD"))
        self.assertEqual(list(json.loads(v["content"])), ["delta", "viewName", "isDefault", "isPublic", "description"])
        self.assertNotIn(" ", v["content"].split('"viewName"')[0], "compact JSON, as Maximo stores it")

    def test_cards_from_carries_extracted_cards(self):
        card = {"id": "c1", "type": "kpi-value", "kpi": "TMGOPSBACKLOG"}
        ext = self.tmp / "view.json"
        ext.write_text(json.dumps({"app": "OPDASHBOARD", "content": json.dumps(
            {"delta": {"cards": [card], "layouts": {"lg": [{"i": "c1"}]}}})}))
        spec = self.dash.load_spec("maintenance_supervisor")
        spec["opdashboard"]["cards_from"] = str(ext)
        delta = json.loads(self.dash.view_record(spec)["content"])["delta"]
        self.assertEqual(delta, {"cards": [card], "layouts": {"lg": [{"i": "c1"}]}})
        ext.write_text(json.dumps({"app": "WOTRACK", "content": "{}"}))
        self.assertTrue(any("cards_from" in e for e in self.dash.validate(spec)))

    def test_dashboard_rights_cover_card_sources(self):
        r = self.dash.dashboard_rights(["READ", "INSERT_PUBLIC", "INSERT_PRIVATE"])
        self.assertEqual(r["OPDASHBOARD"], ["READ", "INSERT_PUBLIC", "INSERT_PRIVATE"])
        self.assertEqual(r["MXAPIVIEWMANAGER"], ["READ", "SAVE", "INSERT"], "SAVE before INSERT, no duplicates")
        for app in self.dash.CARD_SOURCES:
            self.assertIn("READ", r[app])

    def test_rebuild_keeps_rights_added_by_hand(self):
        self.dash.build("maintenance_supervisor", write_manifest=False)
        f = registry.SRC / "02-security/app-rights/TMGOPSSUP.json"
        rec = json.loads(f.read_text())
        rec["rights"]["WOTRACK"] = ["READ"]
        f.write_text(json.dumps(rec))
        self.dash.build("maintenance_supervisor", write_manifest=False)
        self.assertEqual(json.loads(f.read_text())["rights"]["WOTRACK"], ["READ"])

    def test_opdashboard_only_spec_needs_no_portlets(self):
        spec = self.dash.load_spec("maintenance_supervisor")
        spec.pop("portlets")
        self.assertEqual(self.dash.validate(spec), [])
        spec["opdashboard"]["kpis"] = ["NOPE"]
        self.assertTrue(any("opdashboard.kpis" in e for e in self.dash.validate(spec)))


class SigauthTests(unittest.TestCase):
    """Grant-only rights through MXAPIGROUP maxapps: one MERGE for what is missing, read back, never revoke."""

    class Client:
        def __init__(self, held):
            self.held = held                    # {app: {option: authorized}}
            self.merges = []

        def find(self, os_name, key, select=""):
            return [{"href": "G"}] if key["groupname"] == "TMGOPSSUP" else []

        def request(self, method, href, params=None, **kw):
            app = params["oslc.where"].split('"')[1]
            return {"member": [{"sigoption": [{"optionname": o, "authorized": a}
                                              for o, a in self.held.get(app, {}).items()]}]}

        def merge(self, href, body):
            self.merges.append(body)
            for m in body["maxapps"]:
                for so in m["sigoption"]:
                    self.held[m["app"]][so["optionname"]] = True

    REC = {"groupname": "TMGOPSSUP", "rights": {"OPDASHBOARD": ["READ", "INSERT_PRIVATE"]}}

    def session(self, held):
        return type("S", (), {"client": self.Client(held), "env": "t"})()

    def test_dry_run_reports_missing_only(self):
        s = self.session({"OPDASHBOARD": {"READ": True, "INSERT_PRIVATE": False, "DELETE_PUBLIC": True}})
        r = engine._deploy_sigauth(s, "MXAPIGROUP", self.REC, apply=False)
        self.assertEqual((r["action"], r["missing"]), ("would-grant", {"OPDASHBOARD": ["INSERT_PRIVATE"]}))
        self.assertEqual(s.client.merges, [])

    def test_apply_grants_missing_and_never_revokes(self):
        s = self.session({"OPDASHBOARD": {"READ": False, "INSERT_PRIVATE": False, "DELETE_PUBLIC": True}})
        r = engine._deploy_sigauth(s, "MXAPIGROUP", self.REC, apply=True)
        self.assertEqual(r["action"], "granted")
        sent = s.client.merges[0]["maxapps"][0]["sigoption"]
        self.assertEqual({x["optionname"] for x in sent}, {"READ", "INSERT_PRIVATE"})
        self.assertTrue(all(x["authorized"] is True for x in sent))
        self.assertTrue(s.client.held["OPDASHBOARD"]["DELETE_PUBLIC"], "unlisted rights untouched")
        self.assertEqual(engine._deploy_sigauth(s, "MXAPIGROUP", self.REC, apply=True)["action"], "unchanged")

    def test_unknown_option_and_missing_group_refused(self):
        s = self.session({"OPDASHBOARD": {"READ": False}})
        with self.assertRaisesRegex(Exception, "no sig option"):
            engine._deploy_sigauth(s, "MXAPIGROUP", self.REC, apply=False)
        new = {"groupname": "NOPE", "rights": {"OPDASHBOARD": ["READ"]}}
        self.assertEqual(engine._deploy_sigauth(s, "MXAPIGROUP", new, apply=False)["action"], "would-grant",
                         "dry run: group is created earlier in the same deploy")
        with self.assertRaisesRegex(Exception, "not found"):
            engine._deploy_sigauth(s, "MXAPIGROUP", new, apply=True)


def yaml_load(path):
    import yaml
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


class IbmMcpTests(unittest.TestCase):
    def test_sse_and_session(self):
        c = ibm_mcp.IbmMcpClient("https://fake-mcp/mcp", api_key="k")
        sent = []

        def post(url, data=None, timeout=None):
            msg = json.loads(data)
            sent.append(msg)
            if msg["method"] == "initialize":
                return Resp(200, {"jsonrpc": "2.0", "id": msg["id"], "result": {"serverInfo": {"name": "maximo"}}},
                            url, {"Content-Type": "application/json", "Mcp-Session-Id": "abc"})
            if "id" not in msg:
                return Resp(202, None, url)
            if msg["method"] == "tools/list":
                return Resp(200, {"jsonrpc": "2.0", "id": msg["id"], "result": {"tools": [
                    {"name": "getAsset", "annotations": {"readOnlyHint": True}}, {"name": "createWorkOrder"}]}}, url)
            sse = "event: message\ndata: " + json.dumps({"jsonrpc": "2.0", "id": msg["id"],
                                                         "result": {"content": [{"type": "text", "text": "ok"}]}}) + "\n\n"
            return Resp(200, sse, url, {"Content-Type": "text/event-stream"})
        c.s.post = post
        tools = c.list_tools()
        self.assertEqual(c.s.headers["Mcp-Session-Id"], "abc")
        self.assertEqual([ibm_mcp.is_read_only(t) for t in tools], [True, False])
        self.assertEqual(c.call_tool("getAsset", {"assetnum": "1"})["content"][0]["text"], "ok")
        self.assertEqual(c.s.headers["apikey"], "k")


if __name__ == "__main__":
    unittest.main()
