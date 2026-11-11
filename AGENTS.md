# AGENTS.md

Agents working in `kokeb-libs` follow the Kokeb Labs
[agent rules](https://github.com/kokeb-labs/.github/blob/main/standards/agents.md). Read them first.

## This repository

- Parts are records in `parts/` plus library files. Chip facts are never copied into a record: they stay in the
  driver's `docs/hardware.yml`.
- An agent may draft a symbol, footprint or model and prepare the review checks. It never sets an asset state past
  `draft`; a person who did not draw it reviews against the datasheet.
- Never invent a pin, a dimension or a datasheet value. Cite the datasheet section and page, or leave it open.
- Never commit vendor datasheets or vendor library files you may not redistribute.

## Checks before pushing

- `python3 tools/check_parts.py` and `python3 -m unittest discover -s tests`.
- Markdown: markdownlint with line length 120 (tables and code blocks exempt). YAML: yamllint.
- Commits are signed off (`git commit -s`).
