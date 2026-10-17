"""App Designer presentation XML: fingerprint diff + additive merge.

PRESENTATION is one CLOB per application, so any write replaces the entire
screen. Deploying a repo copy that is older than the live screen silently
destroys whatever someone added in the UI since. Two defences, both ported
from the reference repo's MAS 9 migration work:

  loss_set()  every live element (tag|id|sorted attrs) missing from the repo copy
  merge()     live XML is the skeleton; repo elements MODIFY matching ones and
              ADD new ones after their nearest preceding shared sibling; live-only
              elements are KEPT. Identity is (tag, id, ordinal) scoped to siblings.
"""
from __future__ import annotations

import copy
import re
import xml.etree.ElementTree as ET
from collections import Counter

DECL = '<?xml version="1.0" encoding="UTF-8"?>\n'
NSDECL = re.compile(r'xmlns(?::[\w.-]+)?="[^"]*"')


def _root(xml: str) -> ET.Element:
    return ET.fromstring(xml.encode("utf-8"))


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
    out = _reinject_ns(live, DECL + ET.tostring(base, encoding="unicode"))
    stats["merged_elements"] = sum(1 for _ in _root(out).iter())
    return out, stats
