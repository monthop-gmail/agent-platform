#!/usr/bin/env python3
"""Ecosystem drift check for agent-platform.

ตรวจว่า contract ที่ derive มายังตรงกับ semantics ของ repo ต้นทาง และ registry
ยังตรงกับ manifest จริงของ consumer

ขอบเขตของไฟล์นี้ถูกจำกัดโดย ADR-0011 — ห้ามโตเกินการตรวจสอบ
ห้าม generate · ห้ามแก้ไฟล์ · ห้าม deploy · ห้ามเรียก service ที่ไม่ใช่ raw.githubusercontent.com

รันเองได้:  python3 conformance/drift_check.py
offline:    python3 conformance/drift_check.py --local /path/to/devfactory-core
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

import yaml
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = "https://raw.githubusercontent.com/{repo}/main/{path}"

findings: list[tuple[str, str, str]] = []
passed = 0


def ok(area: str, msg: str) -> None:
    global passed
    passed += 1
    print(f"  ok    {area}: {msg}")


def fail(area: str, msg: str) -> None:
    findings.append(("FAIL", area, msg))
    print(f"  FAIL  {area}: {msg}")


def warn(area: str, msg: str) -> None:
    findings.append(("WARN", area, msg))
    print(f"  warn  {area}: {msg}")


def load_yaml(path: pathlib.Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def fetch(repo: str, path: str, local: pathlib.Path | None):
    """อ่านไฟล์ของ repo หนึ่ง — จาก clone ในเครื่องถ้าหาได้ ไม่งั้นจาก raw.githubusercontent

    `--local` รับได้ทั้งโฟลเดอร์ของ repo เดียว และโฟลเดอร์แม่ที่มีหลาย clone
    ต้องแยกตาม repo เพราะถ้าอ่านไฟล์เดียวให้ทุก repo จะได้ผลของ repo ผิดคน
    ซึ่งเป็น false ✅ ที่มองไม่เห็นตอนมี consumer รายเดียว
    """
    if local:
        for candidate in (local / repo.split("/")[-1] / path, local / path):
            if candidate.exists():
                return yaml.safe_load(candidate.read_text(encoding="utf-8"))
        # ไม่มี clone ของ repo นี้ในเครื่อง — ดึงจาก network ต่อ ไม่ใช่เดาจากไฟล์ของ repo อื่น
    url = RAW.format(repo=repo, path=path)
    with urllib.request.urlopen(url, timeout=30) as r:  # noqa: S310 - fixed host
        return yaml.safe_load(r.read().decode("utf-8"))


def vocabulary(block):
    """semantics 1.0 ให้ list · 1.1 ให้ {closed, values|required_minimum}"""
    if isinstance(block, list):
        return block, None
    values = block.get("values") or block.get("required_minimum") or []
    return values, block.get("closed")


# ── 1. derived contracts ────────────────────────────────────────────────────
def check_derived(local: pathlib.Path | None) -> None:
    """auto-discover จากบล็อก derived_from — เพิ่ม derived contract ใหม่แล้วครอบคลุมเอง"""
    derived = {}
    for f in sorted((ROOT / "contracts").glob("**/*.schema.yaml")):
        doc = load_yaml(f)
        if isinstance(doc, dict) and doc.get("derived_from"):
            derived[f.parent.parent.name] = (f, doc)

    if not derived:
        warn("derived", "ไม่พบ contract ที่มี derived_from — ข้ามการตรวจกับต้นทาง")
        return

    sources: dict[str, dict] = {}
    for name, (f, doc) in sorted(derived.items()):
        df = doc["derived_from"]
        repo, manifest = df["repo"], df["manifest"]
        key = f"{repo}/{manifest}"
        if key not in sources:
            try:
                sources[key] = fetch(repo, manifest, local)
            except (urllib.error.URLError, FileNotFoundError) as exc:
                fail("derived", f"อ่าน {key} ไม่ได้: {exc}")
                return
        sem = sources[key]

        pin, src = str(df.get("semantics_version")), str(sem.get("semantics_version"))
        if pin != src:
            fail("derived", f"{name}: pin={pin} แต่ต้นทาง={src} → out of conformance (ADR-0006)")
        else:
            ok("derived", f"{name}: semantics_version={pin} ตรงกับ {repo}")

        if df.get("license") != sem.get("license"):
            warn("derived", f"{name}: license={df.get('license')} vs ต้นทาง={sem.get('license')}")

        frozen = (sem.get("contracts", {}).get(name) or {}).get("frozen")
        if not frozen:
            warn("derived", f"{name}: ต้นทางไม่มีบล็อก frozen สำหรับ contract นี้")
            continue
        check_frozen(name, doc, frozen)


def check_frozen(name: str, doc: dict, frozen: dict) -> None:
    defs = doc.get("$defs", {})
    enums = {k: v["enum"] for k, v in defs.items() if isinstance(v, dict) and "enum" in v}

    for key, block in frozen.items():
        if not (isinstance(block, (list, dict)) and key.endswith("_types")):
            continue
        expected, closed = vocabulary(block)
        if not expected:
            continue
        match = next((e for e in enums.values() if set(expected) <= set(e)), None)
        if match is None:
            missing = [v for v in expected if not any(v in e for e in enums.values())]
            fail("frozen", f"{name}.{key}: schema ขาดค่าที่ต้นทางบังคับ {missing}")
            continue
        extra = [v for v in match if v not in expected]
        if closed and extra:
            fail("frozen", f"{name}.{key}: ต้นทาง closed=true แต่ schema มีค่าเกิน {extra}")
        elif closed:
            ok("frozen", f"{name}.{key}: ตรงเป๊ะ {len(expected)} ค่า (closed)")
        elif extra:
            ok("frozen", f"{name}.{key}: ครบขั้นต่ำ {len(expected)} · เพิ่มเอง {extra} (additive)")
        else:
            ok("frozen", f"{name}.{key}: ครบขั้นต่ำ {len(expected)} ค่า (open)")

    check_binding(name, doc, frozen)

    ours = (doc.get("guarantees") or {}).get("rules") or []
    theirs = frozen.get("guarantees") or []
    if theirs and len(ours) < len(theirs):
        fail("frozen", f"{name}.guarantees: schema มี {len(ours)} ข้อ ต้นทางบังคับ {len(theirs)}")
    elif theirs:
        ok("frozen", f"{name}.guarantees: {len(ours)} ข้อ ครอบคลุมของต้นทาง {len(theirs)}")


def check_binding(name: str, doc: dict, frozen: dict) -> None:
    """field ผูกกับ enum ปิด/เปิด ตรงกับ `closed` ของต้นทางไหม

    จับ agent-platform#17: `EventType` มี 7 ค่าครบตามต้นทางที่ประกาศ `closed: false`
    แต่ field `event_type` ยัง $ref มาที่ enum นั้น ทำให้ค่านอกลิสต์ validate ไม่ผ่าน
    — เทียบเฉพาะ "ค่าที่มี" จับไม่ได้ เพราะค่าครบทุกตัว
    """
    defs = doc.get("$defs", {})

    def bound_to_enum(expected: set[str]) -> list[str]:
        """ชื่อ property ที่ $ref ไปยัง $defs ซึ่ง enum คลุม expected ทั้งชุด"""
        hits = []
        for prop, spec in (doc.get("properties") or {}).items():
            ref = spec.get("$ref") if isinstance(spec, dict) else None
            if not (isinstance(ref, str) and ref.startswith("#/$defs/")):
                continue
            target = defs.get(ref.split("/")[-1], {})
            if isinstance(target, dict) and expected <= set(target.get("enum") or []):
                hits.append(prop)
        return hits

    for key, block in frozen.items():
        if not (isinstance(block, (list, dict)) and key.endswith("_types")):
            continue
        expected, closed = vocabulary(block)
        if not expected or closed is None:
            continue
        bound = bound_to_enum(set(expected))
        if closed is False and bound:
            fail(
                "binding",
                f"{name}.{key}: ต้นทาง closed=false แต่ field {bound} ผูกกับ enum ปิด "
                f"— ค่านอกลิสต์จะ validate ไม่ผ่าน ขัดกับ ADR-0006 Rule 2",
            )
        elif closed is False:
            ok("binding", f"{name}.{key}: closed=false และไม่มี field ผูกกับ enum ปิด")
        elif closed is True and not bound:
            warn(
                "binding",
                f"{name}.{key}: ต้นทาง closed=true แต่ไม่มี field ไหนผูกกับ enum นี้ "
                f"— ความเป็นชุดปิดไม่ถูกบังคับที่ schema",
            )
        else:
            ok("binding", f"{name}.{key}: closed=true และ field {bound} ผูกกับ enum ปิด")


# ── 2. consumer registry ────────────────────────────────────────────────────
def check_registry(local: pathlib.Path | None) -> None:
    reg_path = ROOT / "architecture/consumers.md"
    reg = reg_path.read_text(encoding="utf-8")
    rows = [l for l in reg.splitlines() if l.startswith("| [`") and "platform-contract.yaml" in l]
    if not rows:
        warn("registry", "ไม่มี consumer ที่ประกาศ manifest ใน consumers.md")
        return

    version_table = reg[reg.index("## Version usage"):] if "## Version usage" in reg else ""
    for row in rows:
        m = re.search(r"github\.com/([\w.-]+/[\w.-]+)", row)
        if not m:
            warn("registry", f"แถวไม่มี repo URL: {row[:60]}")
            continue
        repo = m.group(1)
        try:
            man = fetch(repo, "platform-contract.yaml", local)
        except (urllib.error.URLError, FileNotFoundError) as exc:
            fail("registry", f"{repo}: อ่าน platform-contract.yaml ไม่ได้: {exc}")
            continue

        pins = man.get("contracts") or []
        missing_dir = [p for p in pins if not (ROOT / "contracts" / p).is_dir()]
        if missing_dir:
            fail("registry", f"{repo}: pin contract ที่ไม่มีอยู่จริง {missing_dir}")
        else:
            ok("registry", f"{repo}: pin {len(pins)} contract มีครบทุกตัว")

        not_in_row = [p for p in pins if f"`{p}`" not in row]
        if not_in_row:
            fail("registry", f"{repo}: consumers.md แถวนี้ขาด pin {not_in_row}")
        else:
            ok("registry", f"{repo}: แถวใน consumers.md ตรงกับ manifest")

        not_in_table = sorted({p.split("/")[0] for p in pins if f"`{p.split('/')[0]}`" not in version_table})
        if not_in_table:
            fail("registry", f"{repo}: ตาราง version usage ขาด {not_in_table} → อาจอ่านว่าปิด version ได้ทั้งที่มีคน pin")
        else:
            ok("registry", f"{repo}: ตาราง version usage ครอบคลุมครบ")

        status = (man.get("conformance") or {}).get("status")
        verified = (man.get("conformance") or {}).get("last_verified")
        if status == "passing" and not verified:
            fail("registry", f"{repo}: conformance passing แต่ไม่มี last_verified")
        elif status and f"`{status}`" not in row:
            # ต้องหาในแถวของ repo นั้น ไม่ใช่หาทั้งไฟล์ — คำว่า `passing` ของ repo อื่น
            # ทำให้แถวที่ยังเขียน `unknown` ได้ ✅ ปลอม ซึ่งเป็น false ✅ แบบเดียวกับที่
            # ADR-0011 เขียนขึ้นมาแก้ (เคสนั้นคือคำว่า `approval` โผล่ในย่อหน้าอื่น)
            fail(
                "registry",
                f"{repo}: manifest status={status} แต่แถวใน consumers.md ไม่ตรง "
                f"— ตารางกำลังรายงานสถานะ conformance ผิด",
            )
        else:
            ok("registry", f"{repo}: conformance status={status}")


# ── 3. internal integrity ───────────────────────────────────────────────────
def check_internal() -> None:
    ids: set[str] = set()
    refs: set[str] = set()
    docs = []

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "$ref" and isinstance(v, str):
                    refs.add(v)
                else:
                    walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    schemas = sorted((ROOT / "contracts").glob("**/*.schema.yaml"))
    for f in schemas:
        doc = load_yaml(f)
        docs.append((f, doc))
        if doc.get("$id"):
            ids.add(doc["$id"])
        try:
            Draft202012Validator.check_schema(doc)
        except Exception as exc:  # noqa: BLE001 - รายงานทุกชนิดเท่ากัน
            fail("schema", f"{f.relative_to(ROOT)} ไม่ใช่ JSON Schema ที่ถูกต้อง: {str(exc).splitlines()[0]}")
        walk(doc)

    dangling = sorted(r for r in refs if not r.startswith("#") and r.split("#")[0] not in ids)
    if dangling:
        fail("schema", f"$ref ที่ resolve ไม่ได้: {dangling}")
    else:
        cross = len([r for r in refs if not r.startswith("#")])
        ok("schema", f"{len(schemas)} schema ถูกต้อง · cross-ref {cross} จุด resolve ครบ")

    missing_changelog = [f.parent for f, _ in docs if not (f.parent / "CHANGELOG.md").exists()]
    if missing_changelog:
        fail("schema", f"contract ที่ไม่มี CHANGELOG.md: {[str(p.relative_to(ROOT)) for p in missing_changelog]}")
    else:
        ok("schema", "ทุก contract version มี CHANGELOG.md")


# ── 4. profiles ─────────────────────────────────────────────────────────────
def check_profiles() -> None:
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012

    registry = Registry()
    for f in sorted((ROOT / "contracts").glob("**/*.schema.yaml")):
        doc = load_yaml(f)
        if doc.get("$id"):
            registry = registry.with_resource(
                doc["$id"], Resource.from_contents(doc, default_specification=DRAFT202012)
            )

    schema_path = ROOT / "contracts/profile/v1/profile.schema.yaml"
    if not schema_path.exists():
        warn("profile", "ไม่มี contracts/profile/v1 — ข้าม")
        return
    validator = Draft202012Validator(load_yaml(schema_path), registry=registry)

    files = sorted((ROOT / "profiles").glob("*/profile.yaml"))
    bad = 0
    for f in files:
        errors = sorted(validator.iter_errors(load_yaml(f)), key=lambda e: list(e.path))
        if errors:
            bad += 1
            loc = "/".join(str(x) for x in errors[0].path) or "(root)"
            fail("profile", f"{f.relative_to(ROOT)} {loc}: {errors[0].message}")
    if not bad:
        ok("profile", f"{len(files)} profile ผ่าน contracts/profile/v1")


# ── 5. แถวที่อ้างว่ายังไม่มี repo ───────────────────────────────────────────
GHOST_ROW = re.compile(r"^\|\s*`([\w.-]+)`\s*\|.*ยังไม่มี repo")


def repo_visible(repo: str) -> bool:
    """เห็น README ของ repo นี้บน raw.githubusercontent ไหม

    ⚠️ **ตรวจได้ทางเดียวเท่านั้น** — True แปลว่า repo มีจริงแน่นอน
    แต่ False **ไม่ได้แปลว่าไม่มี repo** · repo ที่ไม่มี README หรือที่ default branch
    ชื่ออื่น (navi-ims ใช้ `master`) ก็ได้ False เหมือนกัน

    ที่ไม่ใช้ api.github.com ทั้งที่แม่นกว่า เพราะ ADR-0011 จำกัดขอบเขตของโฟลเดอร์นี้
    ไว้ที่ host เดียวคือ raw.githubusercontent.com — ขยายขอบเขตต้องแก้ ADR ไม่ใช่แก้เงียบ ๆ

    ยก URLError ขึ้นไปให้ผู้เรียกเมื่อเน็ตไม่ถึง เพื่อไม่ให้ "ออฟไลน์" อ่านเป็น "ไม่มี repo"
    """
    for branch in ("main", "master"):
        url = f"https://raw.githubusercontent.com/{repo}/{branch}/README.md"
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=15):  # noqa: S310 - fixed host
                return True
        except urllib.error.HTTPError:
            continue  # 404 — ยังตอบไม่ได้ ลอง branch ถัดไป
    return False


def check_ghost_rows() -> None:
    """แถวที่เขียนว่า "ยังไม่มี repo" — ตรวจว่ายังจริงอยู่ไหม

    `check_registry` เริ่มเดินจาก manifest ของ repo ที่ pin ไว้ · แถวพวกนี้ไม่มี manifest
    ให้เริ่มเดิน จึงไม่เคยมีอะไรมาเทียบ และค้างเป็นข้อมูลผิดได้จนกว่าจะมีคนเห็นด้วยตา
    (`enterprise-knowledge` ค้างอยู่หนึ่งวัน — เจอด้วยตาคน ไม่ใช่ด้วย check)
    """
    reg = (ROOT / "architecture/consumers.md").read_text(encoding="utf-8")
    lines = reg.splitlines()

    # owner เอาจากแถวที่มีลิงก์จริงในตาราง ไม่ใช่ hardcode และไม่ใช่ลิงก์ทั้งไฟล์
    owners = sorted({
        m.group(1)
        for line in lines if line.startswith("| [`")
        for m in [re.search(r"github\.com/([\w.-]+)/[\w.-]+", line)] if m
    })
    # ต้อง match ที่ต้นบรรทัด — แถวของ repo ที่มีจริงอาจ *พูดถึง* คำว่า "ยังไม่มี repo"
    # ในหมายเหตุได้ (แถว enterprise-knowledge เขียนว่าเคยถูกลงไว้แบบนั้น) ซึ่งไม่ใช่ ghost row
    ghosts = [m.group(1) for m in map(GHOST_ROW.match, lines) if m]

    if not ghosts:
        ok("ghost", "ไม่มีแถวที่อ้างว่ายังไม่มี repo")
        return
    if not owners:
        warn("ghost", "หา owner จากแถวที่มีลิงก์ไม่ได้ — ข้ามการตรวจ")
        return

    found = []
    try:
        for name in ghosts:
            for owner in owners:
                if repo_visible(f"{owner}/{name}"):
                    found.append(f"{owner}/{name}")
                    break
    except urllib.error.URLError as exc:
        warn("ghost", f"ตรวจไม่ได้ — เน็ตไม่ถึง raw.githubusercontent.com ({exc.reason})")
        return

    for repo in found:
        fail("ghost", f"{repo}: ทะเบียนเขียนว่า \"ยังไม่มี repo\" แต่ repo มีอยู่จริงแล้ว "
                      f"— ทะเบียนที่ผูกพันกำลังรายงานข้อเท็จจริงผิด")
    if not found:
        ok("ghost", f"ตรวจ {len(ghosts)} แถว × {len(owners)} owner — ยังไม่พบว่ามี repo "
                    f"(⚠️ พิสูจน์ได้ทางเดียว: ไม่เห็น README ไม่ได้แปลว่าไม่มี repo)")


def main() -> int:
    ap = argparse.ArgumentParser(description="ecosystem drift check")
    ap.add_argument("--local", type=pathlib.Path, help="โฟลเดอร์ของ repo ต้นทางเมื่อรันแบบ offline")
    ap.add_argument("--json", action="store_true", help="พิมพ์ผลเป็น JSON")
    args = ap.parse_args()

    print("=" * 70)
    print("ECOSYSTEM DRIFT CHECK")
    print("=" * 70)
    print("\n[1] derived contracts — semantics_version · frozen vocabulary · guarantees")
    check_derived(args.local)
    print("\n[2] consumer registry — consumers.md เทียบ manifest จริง")
    check_registry(args.local)
    print("\n[3] internal — schema ถูกต้อง · $ref resolve · CHANGELOG")
    check_internal()
    print("\n[4] profiles — validate กับ contracts/profile/v1")
    check_profiles()
    print("\n[5] ghost rows — แถวที่อ้างว่ายังไม่มี repo")
    check_ghost_rows()

    fails = [f for f in findings if f[0] == "FAIL"]
    warns = [f for f in findings if f[0] == "WARN"]
    print("\n" + "=" * 70)
    print(f"  passed={passed}  FAIL={len(fails)}  WARN={len(warns)}")
    print("=" * 70)

    if args.json:
        print(json.dumps({"passed": passed, "findings": findings}, ensure_ascii=False, indent=2))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
