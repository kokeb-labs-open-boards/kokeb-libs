#!/usr/bin/env python3
"""Check the part records of the Kokeb Labs library (Python 3.9+, PyYAML).

    python3 tools/check_parts.py                 # check parts/*.yml
    python3 tools/check_parts.py --index build   # also write build/library-index.json and library-index.md

A part record (docs/part-record.md) names a part, where its datasheet and chip facts live, and the review state of
its three library assets: symbol, footprint and 3D model. The check keeps a record honest: an asset that is past
`none` must exist, say where it came from and, once reviewed, say who reviewed it and where.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("check_parts.py needs PyYAML: python3 -m pip install pyyaml")

ASSETS = ("symbol", "footprint", "model3d")
STATES = ("none", "draft", "checked", "reviewed", "released")
ORIGINS = ("original", "vendor-redistributable", "community")
LIFECYCLE = ("active", "nrnd", "eol", "unknown")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REQUIRED = ("schema", "id", "manufacturer", "mpn", "description", "package", "datasheet", "assets", "lifecycle",
            "classification")


def check_record(path: Path, root: Path, data: Any) -> tuple[list[tuple[str, str]], dict[str, Any] | None]:
    """Findings (code, message) for one record file."""
    out: list[tuple[str, str]] = []
    if not isinstance(data, dict):
        return [("P001", "the file must hold one mapping")], None
    for field in REQUIRED:
        if data.get(field) in (None, "", [], {}):
            out.append(("P003", f"missing required field '{field}'"))
    pid = str(data.get("id", ""))
    if pid and (not SLUG_RE.match(pid) or pid != path.stem):
        out.append(("P002", f"id '{pid}' must be a lowercase slug equal to the file name '{path.stem}'"))
    if data.get("classification") not in (None, "public"):
        out.append(("P011", "classification must be public in an open library"))
    life = data.get("lifecycle")
    if isinstance(life, dict) and life.get("status") not in LIFECYCLE:
        out.append(("P010", f"lifecycle.status must be one of {', '.join(LIFECYCLE)}"))
    ds = data.get("datasheet")
    if isinstance(ds, dict) and not (ds.get("repo") or ds.get("url")):
        out.append(("P003", "datasheet needs a repo (a driver's docs/datasheets.yml) or a vendor url, never a file"))
    assets = data.get("assets") if isinstance(data.get("assets"), dict) else {}
    for name in ASSETS:
        asset = assets.get(name)
        if not isinstance(asset, dict) or asset.get("state") not in STATES:
            out.append(("P004", f"assets.{name}.state must be one of {', '.join(STATES)}"))
            continue
        state = asset["state"]
        if state == "none":
            continue
        rel = asset.get("path")
        if not rel or not (root / str(rel)).exists():
            out.append(("P005", f"assets.{name} is {state} but its path '{rel}' does not exist"))
        if asset.get("origin") not in ORIGINS:
            out.append(("P008", f"assets.{name} needs an origin: {', '.join(ORIGINS)}"))
        if state in ("reviewed", "released") and not (asset.get("reviewer") and asset.get("review")):
            out.append(("P006", f"assets.{name} is {state}: name the reviewer and the review (a pull request or "
                                "issue link)"))
    if data.get("status") == "released" and not all(
            isinstance(assets.get(n), dict) and assets[n].get("state") in ("reviewed", "released") for n in ASSETS):
        out.append(("P007", "a released part needs all three assets reviewed or released"))
    return out, data


def run(root: Path) -> tuple[list[dict[str, Any]], list[tuple[str, str, str]]]:
    findings: list[tuple[str, str, str]] = []
    records: list[dict[str, Any]] = []
    seen: dict[tuple[str, str], str] = {}
    for path in sorted((root / "parts").glob("*.yml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            findings.append(("P001", path.name, f"not valid YAML: {exc}"))
            continue
        found, rec = check_record(path, root, data)
        findings += [(code, path.name, msg) for code, msg in found]
        if rec:
            records.append(rec)
            key = (str(rec.get("manufacturer", "")).lower(), str(rec.get("mpn", "")).lower())
            if key in seen:
                findings.append(("P009", path.name, f"same manufacturer and part number as {seen[key]}"))
            seen[key] = path.name
    return records, findings


def write_index(out: Path, records: list[dict[str, Any]]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "library-index.json").write_text(json.dumps(records, indent=2, default=str) + "\n", encoding="utf-8")
    lines = ["# Library index", "", f"{len(records)} part(s).", "",
             "| Part | Manufacturer | Package | Symbol | Footprint | 3D model | Lifecycle |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in records:
        a = r.get("assets", {})
        st = [str((a.get(n) or {}).get("state", "?")) for n in ASSETS]
        life = (r.get("lifecycle") or {}).get("status", "?")
        lines.append(f"| {r.get('mpn')} | {r.get('manufacturer')} | {r.get('package')} | {st[0]} | {st[1]} | {st[2]} "
                     f"| {life} |")
    (out / "library-index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path("."), help="repository root (default: current directory)")
    ap.add_argument("--index", type=Path, help="write library-index.json and library-index.md to this folder")
    args = ap.parse_args(argv)
    records, findings = run(args.root)
    for code, name, msg in findings:
        print(f"ERROR   {code} {name}: {msg}")
    print(f"\n{len(records)} part record(s); {len(findings)} error(s).")
    if args.index:
        write_index(args.index, records)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
