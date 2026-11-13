# Sum up 13 November's world news in one image

make.fun bounty **news-image-01** ($250, 100 places paid, 1st $50).
Opens Sat 2026-11-14 03:00 WIB, ends Sun 2026-11-15 03:00 WIB.

## The entry

`main.py` (Python 3.13, stdlib only) copies the bundled `entry.png` to
`/output/entry.png`. The image is a newspaper front page for Friday
13 November 2026 with the day's four biggest stories, each as a
photo panel with a crisp headline bar:

1. **NVIDIA CHIEF RESIGNS** — Jensen Huang resigned as Nvidia CEO;
   shares fell 16%. (chip + plunging red chart)
2. **EU JOINS UKRAINE TALKS** — Europe wins a seat at the next round
   of Ukraine peace talks; the war's largest prisoner exchange is
   being prepared. (EU/Ukraine handshake)
3. **TANKERS HIT IN HORMUZ** — four oil tankers hit by explosions in
   the Strait of Hormuz; Iran says it destroyed a US radar in Bahrain.
   (burning tanker, naval ship)
4. **MICROSOFT DOWN WORLDWIDE** — global Microsoft 365 outage hits
   Outlook and Teams. (dark laptop, globe with warning dots)

The four panels were generated as separate clean scenes (no baked-in
text), then composed with PIL (`compose.py`, kept out of the repo):
masthead "FRIDAY 13 NOVEMBER 2026 — WORLD NEWS" and white-on-black
headline bars drawn with DejaVu Sans Bold, so no text is ever garbled.
Every headline is faithful to the day's reporting; nothing is
invented or hyped.

## Files

- `main.py` — the entry program (copies `entry.png` to the output path)
- `entry.png` — the image (JPEG bytes, 1024×1024, 227,860 bytes)
- `LICENSE` — MIT
- `BUILD_TRANSCRIPT.md` — how this entry was built and tested

## Test

```sh
mkdir -p /tmp/o1 /tmp/o2
MAKEFUN_OUTPUT_DIR=/tmp/o1 python3 main.py
MAKEFUN_OUTPUT_DIR=/tmp/o2 python3 main.py
# both runs write byte-identical output (sha256 3c08632a…)
```
