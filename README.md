# kokeb-libs

KiCad symbols, footprints and 3D models for the parts on Kokeb Labs boards, each with a record that says where its
facts come from and how far its review has got. Boards use only parts that have passed review here, pinned by
release tag.

[![CI](https://github.com/kokeb-labs-open-boards/kokeb-libs/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kokeb-labs-open-boards/kokeb-libs/actions/workflows/ci.yml)

> **Status: concept.** There are no library files yet. The part record format, the review process and the checker
> exist; the first symbol, footprint and 3D model arrive with the first board's parts, each through its review.

## What is here

| Path | What it holds |
| --- | --- |
| [`parts/`](parts) | One record per part: manufacturer, part number, package, datasheet and chip-fact sources, lifecycle, and the review state of its symbol, footprint and 3D model |
| `symbols/`, `footprints/`, `3dmodels/` | The KiCad library files the records point at |
| [`docs/part-record.md`](docs/part-record.md) | The record format and the rules the checker enforces |
| [`docs/review-process.md`](docs/review-process.md) | The states an asset moves through and what a reviewer checks |
| `tools/check_parts.py` | Validates the records and writes a browsable index |

## One source for chip facts

Pins, supply ranges and reference circuits come from the driver's `docs/hardware.yml`, which cites the datasheet
revision, section and page for each fact. A part record points at it and never copies it, so a datasheet revision is
updated in one place. The symbol's pin table and the footprint's pads are checked against that record in review.

## See the library

```bash
python3 tools/check_parts.py --index build     # checks the records, writes build/library-index.md
```

CI prints the same table in the job summary of every pull request, so a reviewer sees which parts are at which
state without opening a file.

## Contributing

Read the [contributing guide](https://github.com/kokeb-labs-open-boards/.github/blob/main/CONTRIBUTING.md). Do not
commit vendor datasheets, or vendor symbol, footprint or model files that you may not redistribute: link the vendor
and draw the asset yourself, or record its licence and origin in the part record.

## Licence

The tooling and documentation are [MIT](LICENSE). The licence of the library files is decided with the hardware
licence ([ADR-0001](https://github.com/kokeb-labs-open-boards/.github/blob/main/docs/adr/0001-hardware-licence.md));
until then no library file is added.
