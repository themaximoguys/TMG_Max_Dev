"""App Designer presentation XML: fingerprint diff + additive merge.

PRESENTATION is one CLOB per application, so any write replaces the entire
screen. Deploying a repo copy that is older than the live screen silently
destroys whatever someone added in the UI since. Two defences, both ported
from the reference repo's MAS 9 migration work:

  loss_set()  every live element (tag|id|sorted attrs) missing from the repo copy
  merge()     live XML is the skeleton; repo elements MODIFY matching ones and
              ADD new ones after their nearest preceding shared sibling; live-only
              elements are KEPT. Identity is (tag, id, ordinal) scoped to siblings.
  patch_text() when only attributes changed, rewrite just those start tags in the
              live text so Maximo keeps its own layout (tabs, blank lines) and a
              one-label edit stays a one-line change on the tenant.
"""
from __future__ import annotations

import copy
import re
import xml.etree.ElementTree as ET
from collections import Counter

DECL = '<?xml version="1.0" encoding="UTF-8"?>\n'
NSDECL = re.compile(r'xmlns(?::[\w.-]+)?="[^"]*"')


def _root(xml: str) -> ET.Element:
    _register_ns(xml)
    return ET.fromstring(xml.encode("utf-8"))


def _register_ns(xml: str) -> None:
    for m in re.finditer(r'xmlns:([\w.-]+)="([^"]*)"', xml[:4000]):
        ET.register_namespace(m.group(1), m.group(2))


def _content(xml: str):
    """Element tree content ignoring layout whitespace: (tag, attrs, stripped text, stripped tail)."""
    return [(e.tag, tuple(e.attrib.items()), (e.text or "").strip(), (e.tail or "").strip())
            for e in _root(xml).iter()]


def pretty(xml: str) -> str:
    """One element per line, 2-space indent, attribute order preserved. Raises if the
    reformatted document differs from the original in anything but whitespace."""
    _register_ns(xml)
    root = _root(xml)
    for e in root.iter():                      # drop layout-only whitespace before re-indenting
        if e.text is not None and not e.text.strip():
            e.text = None
        if e.tail is not None and not e.tail.strip():
            e.tail = None
    ET.indent(root, space="  ")
    out = _reinject_ns(xml, DECL + ET.tostring(root, encoding="unicode") + "\n")
    if _content(out) != _content(xml):
        raise ValueError("pretty-print changed XML content — refusing to rewrite")
    return out


def fingerprints(xml: str | None) -> Counter:
    fp: Counter = Counter()
    if not xml:
        return fp
    for e in _root(xml).iter():
        attrs = ",".join(f"{k}={e.attrib[k]}" for k in sorted(e.attrib))
        fp[f"{e.tag}|{e.attrib.get('id', '')}|{attrs}"] += 1
    return fp


def identities(xml: str | None) -> Counter:
    """Element identity: tag|id for elements with an id, full fingerprint otherwise."""
    ids: Counter = Counter()
    if not xml:
        return ids
    for e in _root(xml).iter():
        if e.attrib.get("id"):
            ids[f"{e.tag}|{e.attrib['id']}"] += 1
        else:
            attrs = ",".join(f"{k}={e.attrib[k]}" for k in sorted(e.attrib))
            ids[f"{e.tag}||{attrs}"] += 1
    return ids


def compare(live: str | None, repo: str) -> dict:
    """loss = live elements that the repo copy does not contain at all (a whole-CLOB
    write would delete them). changed = same element, different attributes (intended edits)."""
    lid, rid = identities(live), identities(repo)
    lfp, rfp = fingerprints(live), fingerprints(repo)
    loss, gain = lid - rid, rid - lid
    changed = sum((lfp - rfp).values()) - sum(loss.values())
    return {
        "live_elements": sum(lfp.values()), "repo_elements": sum(rfp.values()),
        "loss": sum(loss.values()), "added": sum(gain.values()), "changed": max(changed, 0),
        "loss_sample": [k[:160] for k in list(loss)[:15]],
        "verdict": "SAFE" if not loss else "DESTRUCTIVE",
    }


def _keys(parent):
    seen, out = {}, []
    for c in parent:
        k = (c.tag, c.attrib.get("id"))
        seen[k] = seen.get(k, -1) + 1
        out.append((c.tag, c.attrib.get("id"), seen[k]))
    return out


def _merge(base, over, stats):
    bmap = {k: i for i, k in enumerate(_keys(base))}
    anchor = -1
    for oi, k in enumerate(_keys(over)):
        ochild = over[oi]
        if k in bmap:
            bi = bmap[k]
            bchild = base[bi]
            if bchild.attrib != ochild.attrib:
                stats["modified"] += 1
                bchild.attrib.clear()
                bchild.attrib.update(ochild.attrib)
            if (ochild.text or "").strip():
                bchild.text = ochild.text
            _merge(bchild, ochild, stats)
            anchor = bi
        else:
            stats["added"] += sum(1 for _ in ochild.iter())
            base.insert(anchor + 1, copy.deepcopy(ochild))
            bmap = {kk: (i + 1 if i > anchor else i) for kk, i in bmap.items()}
            anchor += 1


def _reinject_ns(live_xml: str, out_xml: str) -> str:
    """ElementTree drops xmlns declarations that are declared but unused; put them back."""
    def root_tag(s):
        i = s.index("<", s.index("?>") + 2) if "?>" in s else s.index("<")
        return i, s[i: s.index(">", i) + 1]
    _, lroot = root_tag(live_xml)
    oi, oroot = root_tag(out_xml)
    missing = [d for d in NSDECL.findall(lroot) if d not in oroot]
    if not missing:
        return out_xml
    end = oi + len(oroot.split(None, 1)[0])
    return out_xml[:end] + " " + " ".join(missing) + out_xml[end:]


def merge(live: str, repo: str) -> tuple[str, dict]:
    base, over = _root(live), _root(repo)
    if base.tag != over.tag:
        raise ValueError(f"root element mismatch: live <{base.tag}> vs repo <{over.tag}>")
    stats = {"modified": 0, "added": 0, "live_elements": sum(1 for _ in base.iter())}
    if base.attrib != over.attrib:
        stats["modified"] += 1
        base.attrib.clear()
        base.attrib.update(over.attrib)
    _merge(base, over, stats)
    out = pretty(_reinject_ns(live, DECL + ET.tostring(base, encoding="unicode")))
    stats["merged_elements"] = sum(1 for _ in _root(out).iter())
    return out, stats


# ── minimal-diff write ────────────────────────────────────────────────────
_TOKEN = re.compile(
    r"<!--.*?-->|<!\[CDATA\[.*?\]\]>|<\?.*?\?>|<![^>]*>|</[^>]*>"
    r"|<([^\s/>!?]+)((?:\s+[^\s=/>]+\s*=\s*(?:\"[^\"]*\"|'[^']*'))*)\s*(/?)>", re.S)
_XMLNS_ATTR = re.compile(r'\s+xmlns(?::[\w.-]+)?\s*=\s*(?:"[^"]*"|\'[^\']*\')')


def _escape_attr(v: str) -> str:
    return (v.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
            .replace("\n", "&#10;").replace("\r", "&#13;").replace("\t", "&#09;"))


def _shape(root: ET.Element):
    return [(e.tag, (e.text or "").strip(), (e.tail or "").strip()) for e in root.iter()]


def patch_text(live: str, new: str) -> str | None:
    """Return `live` with only the start tags whose attributes differ in `new` rewritten.

    Applies only when both documents have the same elements in the same order with
    the same text (an attribute-only edit). Returns None otherwise, or if anything
    about the live text cannot be mapped safely; callers then send `new` as is."""
    try:
        lroot, nroot = _root(live), _root(new)
    except ET.ParseError:
        return None
    if _shape(lroot) != _shape(nroot):
        return None
    lels, nels = list(lroot.iter()), list(nroot.iter())
    if any("{" in e.tag or any("{" in k for k in e.attrib) for e in lels + nels):
        return None                                   # namespaced names: not worth the risk
    starts = [m for m in _TOKEN.finditer(live) if m.group(1)]
    if [m.group(1) for m in starts] != [e.tag for e in lels]:
        return None
    out, pos, changed = [], 0, 0
    for m, le, ne in zip(starts, lels, nels):
        if le.attrib == ne.attrib:
            continue
        xmlns = "".join(_XMLNS_ATTR.findall(m.group(2)))
        attrs = "".join(f' {k}="{_escape_attr(v)}"' for k, v in ne.attrib.items())
        out += [live[pos:m.start()], f"<{ne.tag}{xmlns}{attrs}{'/' if m.group(3) else ''}>"]
        pos, changed = m.end(), changed + 1
    out.append(live[pos:])
    patched = "".join(out)
    if fingerprints(patched) != fingerprints(new) or _shape(_root(patched)) != _shape(nroot):
        return None
    return patched
