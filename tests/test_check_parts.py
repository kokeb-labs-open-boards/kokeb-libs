"""Tests for tools/check_parts.py: run with `python3 -m unittest discover -s tests`."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_parts  # noqa: E402


def part(**over) -> dict:
    base = {
        "schema": 1, "id": "abc123", "manufacturer": "Acme", "mpn": "ABC123", "description": "d",
        "package": "LGA-10", "datasheet": {"url": "https://example.com/abc123"},
        "assets": {n: {"state": "none"} for n in check_parts.ASSETS},
        "lifecycle": {"status": "active"}, "classification": "public",
    }
    base.update(over)
    return base


class Repo:
    def __init__(self, *records: dict, files: tuple[str, ...] = ()):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / "parts").mkdir()
        for rec in records:
            (self.dir / "parts" / f"{rec['id']}.yml").write_text(yaml.safe_dump(rec))
        for rel in files:
            target = self.dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("x")

    def codes(self) -> list[str]:
        return sorted(code for code, _, _ in check_parts.run(self.dir)[1])


class CheckPartsTest(unittest.TestCase):
    def check(self, expected, *records, files=()):
        repo = Repo(*records, files=files)
        self.addCleanup(shutil.rmtree, repo.dir, True)
        self.assertEqual(sorted(expected), repo.codes())

    def test_shipped_records_pass(self):
        self.assertEqual(0, check_parts.main(["--root", str(ROOT)]))

    def test_minimal_record_passes(self):
        self.check([], part())

    def test_missing_field(self):
        rec = part()
        del rec["package"]
        self.check(["P003"], rec)

    def test_id_must_match_file(self):
        repo = Repo(part())
        self.addCleanup(shutil.rmtree, repo.dir, True)
        (repo.dir / "parts" / "abc123.yml").rename(repo.dir / "parts" / "other.yml")
        self.assertEqual(["P002"], repo.codes())

    def test_bad_state(self):
        rec = part()
        rec["assets"]["symbol"]["state"] = "maybe"
        self.check(["P004"], rec)

    def test_asset_needs_existing_path_and_origin(self):
        rec = part()
        rec["assets"]["symbol"] = {"state": "draft", "path": "symbols/x.kicad_sym"}
        self.check(["P005", "P008"], rec)
        rec["assets"]["symbol"]["origin"] = "original"
        self.check([], rec, files=("symbols/x.kicad_sym",))

    def test_reviewed_needs_reviewer_and_review(self):
        rec = part()
        rec["assets"]["footprint"] = {"state": "reviewed", "path": "footprints/x.kicad_mod", "origin": "original"}
        self.check(["P006"], rec, files=("footprints/x.kicad_mod",))

    def test_released_part_needs_all_assets_reviewed(self):
        self.check(["P007"], part(status="released"))

    def test_duplicate_manufacturer_and_mpn(self):
        self.check(["P009"], part(), part(id="abc123-b"))

    def test_lifecycle_and_classification(self):
        self.check(["P010", "P011"], part(lifecycle={"status": "gone"}, classification="restricted"))

    def test_datasheet_needs_a_source(self):
        self.check(["P003"], part(datasheet={"note": "see vendor"}))

    def test_invalid_yaml_and_non_mapping(self):
        repo = Repo(part())
        self.addCleanup(shutil.rmtree, repo.dir, True)
        (repo.dir / "parts" / "bad.yml").write_text("- id: [unclosed\n")
        (repo.dir / "parts" / "list.yml").write_text("- a\n")
        self.assertEqual(["P001", "P001"], repo.codes())

    def test_index_is_written(self):
        repo = Repo(part())
        self.addCleanup(shutil.rmtree, repo.dir, True)
        out = repo.dir / "out"
        self.assertEqual(0, check_parts.main(["--root", str(repo.dir), "--index", str(out)]))
        self.assertIn("| ABC123 | Acme |", (out / "library-index.md").read_text())


if __name__ == "__main__":
    unittest.main()
