# designs

CAD for furniture designs worked out on paper first. Each model is a plain
Python script built with [cadgen](https://www.texttocad.dev); running the script
writes its own STEP and meshes.

## Designs

| Design | Entrypoint | Summary |
| --- | --- | --- |
| [drinks_table](drinks_table/) | `drinks_table/src/drinks_table.py` | Open ring top on a spoke fan rising from a standing dome |

Still on paper, from the same sketch pages: a hyperboloid pedestal of straight
members between two rims, a slatted drum, and the ring top on two splayed legs
from the paper maquette. All three reuse the helpers in `lib/`.

## Layout

One directory per design, each self-contained apart from the shared factories:

```
lib/                    shared geometry factories (rod, spoke fan, ring, dome)
<design>/
  README.md             the design, its dimensions, and what was measured
  src/                  model scripts, one decorated model per file
  checks/               measured checks, rerun after any model change
  STEP/ GLB/ STL/       generated artifacts (ignored; rebuild by running the model)
  tmp/                  scratch renders and throwaway scripts (ignored)
```

## Build

From a design's own directory:

```bash
cd drinks_table
PYTHONPATH=.. python src/drinks_table.py
python checks/drinks_table_geometry.py
```

`PYTHONPATH=..` puts this directory on the import path so `lib/` resolves.
Decorator `out=` paths are relative to the model script, so a design's outputs
land inside its own folder whatever directory you run from.

Review everything at once with the CAD Viewer from this directory, which
catalogs every design's artifacts:

```bash
cadgen viewer
```

## Conventions

- Millimetres, +Z up, z=0 is the floor, so a model's height is the z of its
  working surface.
- One decorated model per entrypoint file, its outputs sharing the file stem.
- Design intent that is measurable belongs in `checks/`, not in a comment. The
  checks separate faults (the geometry is wrong) from findings (a design
  criterion to rule on).
