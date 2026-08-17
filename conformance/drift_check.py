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
    """อ่านไฟล์จาก repo ต้นทาง — local เมื่อรัน offline · raw.githubusercontent เมื่อรันใน CI"""
    if local:
        p = local / path
        if not p.exists():
            raise FileNotFoundError(f"{local}/{path}")
        return yaml.safe_load(p.read_text(encoding="utf-8"))
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

    ours = (doc.get("guarantees") or {}).get("rules") or []
    theirs = frozen.get("guarantees") or []
    if theirs and len(ours) < len(theirs):
        fail("frozen", f"{name}.guarantees: schema มี {len(ours)} ข้อ ต้นทางบังคับ {len(theirs)}")
    elif theirs:
        ok("frozen", f"{name}.guarantees: {len(ours)} ข้อ ครอบคลุมของต้นทาง {len(theirs)}")


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
        elif status and status not in reg:
            warn("registry", f"{repo}: manifest status={status} แต่ consumers.md ไม่ได้สะท้อน")
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
