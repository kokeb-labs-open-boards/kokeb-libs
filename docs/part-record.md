# Part record

One YAML file per part in `parts/`, named `<id>.yml`. See [`parts/bmp581.yml`](../parts/bmp581.yml).

## Fields

| Field | Meaning |
| --- | --- |
| `schema` | `1` |
| `id` | Lowercase slug, equal to the file name |
| `manufacturer`, `mpn`, `description`, `package` | What the part is. One record per manufacturer and part number |
| `datasheet` | Where the datasheet is identified: `repo` and `file` (the driver's `docs/datasheets.yml`) or a vendor `url`. Never a PDF in this repository |
| `hardware_record` | The driver's `docs/hardware.yml` with the pins and reference circuits |
| `driver` | The Kokeb Labs driver for the part, if any |
| `assets` | `symbol`, `footprint`, `model3d`, each with a `state` (below) |
| `lifecycle` | `status`: active, nrnd, eol or unknown; `checked`: the date of the last check |
| `classification` | `public` |

An asset past `none` also has `path` (a file in this repository), `origin` (`original`, `vendor-redistributable` or
`community`, with `licence` for the last two) and, once reviewed, `reviewer` and `review` (a pull request or issue
link).

## Rules the check enforces

| Code | Rule |
| --- | --- |
| P001 | The file is valid YAML holding one mapping |
| P002 | `id` is a lowercase slug equal to the file name |
| P003 | Required fields are present, and the datasheet has a source |
| P004 | Every asset has a state from the list |
| P005 | An asset past `none` has a `path` that exists |
| P006 | A reviewed or released asset names its reviewer and review |
| P007 | A part with `status: released` has all three assets reviewed or released |
| P008 | An asset past `none` has an `origin` |
| P009 | No two records share a manufacturer and part number |
| P010 | `lifecycle.status` is from the list |
| P011 | `classification` is `public` |

Run `python3 tools/check_parts.py`; add `--index build` for the browsable table.
