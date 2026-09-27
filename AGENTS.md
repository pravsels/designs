# AGENTS.md

Furniture design studies in CAD. Each design is a directory; `lib/` holds the
geometry factories they share. Read `README.md` for the layout and a design's
own `README.md` for what it is and what has been measured about it.

## This Is A Standalone Repo

It has no remote and it is not a submodule. It currently sits inside a
`text-to-cad` checkout at `models/designs`, which **ignores this path
entirely** (`/models/designs/` in that repo's `.gitignore`), so nothing here is
tracked by it and there is no submodule pointer to update. Commit here; never
expect the parent to see it.

## Environment

Models are plain Python built with [cadgen](https://www.texttocad.dev). Nothing
in this repo pins it, because the interpreter lives outside the repo — the one
external dependency, and the thing worth checking first.

The checkout this currently sits in has an editable cadgen in its venv:

```bash
../../.venv/bin/python --version      # from a design directory: ../../../
```

Confirm what you have before building anything. `cadgen doctor` reports the
install path and whether the CAD kernel loads:

```bash
../../.venv/bin/python -m cadgen.cli doctor
```

Standalone, a plain `pip install cadgen` in any Python 3.11+ venv is enough for
the models and the checks. `python -m cadgen.cli` is the PATH-independent form
of the `cadgen` console script.

## Build And Check

From a design's own directory, never from this root:

```bash
cd drinks_table
PYTHONPATH=.. python src/drinks_table.py
python checks/drinks_table_geometry.py
```

`PYTHONPATH=..` is what puts this root on the import path so `lib/` resolves;
cadgen adds no import roots of its own. Decorator `out=` paths are relative to
the model script, so outputs land in the design's own folders whatever
directory you run from. An unchanged model is a no-op; `cadgen store why
src/<model>.py` explains an unexpected rebuild.

## Verify By Measuring, Not By Looking

**This is the house rule.** A snapshot is for the human; a measurement is for
you. Reading a render tells you almost nothing reliable, and two real errors
here — a dome floating 47.5 mm off the floor, and a table that tipped under
2.4 kg — both looked completely fine in a rendered image and were caught only
by numbers.

So every design has a `checks/` script that measures the saved STEP with
`read_scene` and `cadgen.geometry` (`mass_properties`, `overlap_volume`,
`topology_errors`). Measure off the **saved document**, never by recomputing
the model's own constants, or the check just confirms its own assumptions.
Render for the human, after the numbers pass.

Checks separate two kinds of result, and the distinction matters:

- **FAULTS** — the geometry is wrong: it does not stand on z=0, a part breaches
  a surface, bodies interfere, topology is invalid. Fix these.
- **FINDINGS** — a measured design criterion is not met. **These are the
  designer's call. Report the number and stop.** Do not add geometry to make a
  finding go away: the base disc that once appeared under the drinks table was
  an agent fixing its own misreading of the design, not a real requirement.

## Toolchain Gotchas

These cost real time and none of them announce themselves clearly:

- **Mesh exports need Node modules when cadgen runs from a source checkout.**
  `@stl`/`@glb`/`@threemf` and DXF previews run the checkout's live builders,
  which import `three` from `packages/cadgen-js/node_modules`. A fresh clone or
  worktree has none and every mesh export fails until `npm install` runs there.
  cadgen's error names the fix.
- **Snapshots need a Chromium matching the installed Playwright.** Upgrading
  playwright silently invalidates the existing browser build; re-run
  `python -m playwright install chromium` or every snapshot dies inside
  Playwright's connection layer.
- **The CAD Viewer needs its client built when served from a checkout.**
  `cadgen viewer` serves `apps/viewer/dist`, which is not committed:
  `npm --prefix apps/viewer install && npm --prefix apps/viewer run build`.
  It serves **one directory — the one you run it from** — and there is no flag
  for it, so run it from this root to catalog every design at once.
- **The store at `~/.cache/cadgen` is derived data only.** Safe to delete at
  any time; it rebuilds. A sandbox that cannot write it fails the build with a
  message naming `CADGEN_CACHE_DIR`.

## Conventions

- Millimetres, +Z up, z=0 is the floor, so a model's height is the z of its
  working surface.
- One decorated model per entrypoint file, outputs sharing the file stem.
- A model takes no parameters. Parametric geometry goes in a `lib/` factory the
  model calls; a second configuration is a second entrypoint.
- Generated artifacts are ignored, not committed — the model script is the
  source of truth. Keep scratch scripts and renders in a design's `tmp/`.
- Design intent that can be measured belongs in `checks/`, not in a comment.
