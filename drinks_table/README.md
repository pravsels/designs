# Drinks table

A coffee table you deliberately cannot work at. An open ring top sits on a fan
of 20 spokes that splay down and in to a dome standing on its own flat face —
the "weird wheel with outward spokes" from the sketch page, with the ring top
from the paper maquette.

| | |
| --- | --- |
| Overall | 440 mm diameter, 406 mm tall |
| Top | 440 mm ring around a 250 mm open centre, 95 mm band |
| Working surface | 400 mm, a 71 mm flat channel between two 6 mm lips |
| Footprint | 190 mm, the dome's own flat face |
| Spokes | 20 off, 12 mm, hub radius 55 mm out to rim radius 180 mm |

## The two functional ideas, as measured

The **open centre** means there is no surface in the middle, so nothing flat can
be kept on it. A 300x220 mm laptop has a 186 mm half-diagonal against a 125 mm
hole radius, so it spans the void resting only on the two lip crowns — it will
not lie flat. No flat ring can make a laptop actually fall through while still
being narrow enough to hold a glass, so the lips do that work.

The **two lips** make the band a channel. On a ring a glass can slide two ways,
off the rim or into the hole, and a lip at each edge stops both. A 65 mm tumbler
base stands flat in the 71 mm channel, captive between lips 6 mm proud.

The band width follows from that: at a 280 mm hole the channel drops to 56 mm
and a glass rides the lip crowns instead of sitting in the channel.

## Stability depends on the dome's material

The dome is the ballast, so the lever here is material choice rather than
geometry. Its 190 mm flat face gives a 23-29 degree tip angle, and the load at
the rim that tips the table is 27 kg all-steel but 9.4 kg with a light top and
a stone dome — under the 20 kg criterion the check applies. A denser or larger
dome buys it back. `checks/` reports the current numbers.

## Build

From this directory:

```bash
PYTHONPATH=.. python src/drinks_table.py
python checks/drinks_table_geometry.py
```

`PYTHONPATH=..` puts the shared `lib/` at the designs root on the import path;
cadgen adds no import roots of its own. An unchanged model is a no-op.
