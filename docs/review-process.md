# Review process

Each asset of a part (symbol, footprint, 3D model) moves through five states. A person moves it, in a pull request,
and the reviewer is never the author.

| State | Means | Who moves it |
| --- | --- | --- |
| `none` | No asset yet | |
| `draft` | Drawn, not checked; do not use on a board | Author |
| `checked` | The author has run the checks below and listed the results in the pull request | Author |
| `reviewed` | A second person has redone the checks against the datasheet and signed off | Reviewer |
| `released` | In a tagged release of this repository that boards can pin | Maintainer |

A part is `released` when all three assets are `reviewed` or `released`.

## What a reviewer checks

Redo each check from the datasheet, not from the author's notes. Write the result in the pull request and link it
in the part record as `review`.

### Symbol

- Pin count, numbers, names and electrical types match the pin table in the driver's `hardware.yml` and the
  datasheet section it cites.
- Power pins are marked as power inputs; unused-pin advice from the datasheet is in the symbol's description.
- Datasheet field carries the revision from `datasheets.yml`; the manufacturer and part number fields are set.

### Footprint

- Pad count, pitch, size and the courtyard follow the datasheet's recommended land pattern; cite the figure and
  page in the pull request.
- Pin 1 marking, the silkscreen and the fabrication layer outline are present.
- Pad numbers match the symbol's pin numbers, pin for pin.
- It passes the KiCad Library Convention checks that apply, and the footprint checker in CI once it exists.

### 3D model

- The package dimensions match the datasheet's mechanical drawing.
- It sits on the board correctly in the 3D viewer: orientation, offset and height against the footprint.
- The model's origin and licence are recorded.

## Lifecycle

`lifecycle.status` and `checked` are updated when a part is added and again at every release of this repository,
from the manufacturer's notices and a distributor check. A part marked `eol` or `nrnd` cannot be used in a new board
without an ADR in that board's repository.

## Agents

An agent may draft an asset or prepare the checks. It never sets a state past `draft`; a person reviewing against the
datasheet does.
