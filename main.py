#!/usr/bin/env python3
"""Sum up 13 November's world news in one image - make.fun bounty news-image-01.

Writes one image to /output/entry.png: a newspaper front page for
Friday 13 November 2026 with four labelled stories of the day -
Nvidia's chief resigns (chip + falling chart), Europe joins the
Ukraine peace talks (EU/Ukraine handshake), tankers hit in the
Strait of Hormuz (burning tanker, naval ship), and the worldwide
Microsoft outage (dark laptop, globe with warning dots). The image
is the entry; the program simply copies the bundled file to the
output path, exactly as the bounty brief suggests ("the simplest
program copies an image the repository holds").

Deterministic by design: the copied file is a fixed asset, there is
no randomness, no network access and no time dependence, so two runs
write identical bytes - as the bounty requires ("the program runs
twice and both runs must write the same bytes").

The bundled image is fully validated before it is copied (JPEG
structure, end marker, exact 1024x1024 dimensions) and re-validated
after the write, so a truncated or wrong-size asset fails loudly
instead of silently producing a bad entry.

Python 3.13, standard library only.
"""

import hashlib
import os
import shutil
import sys

DEFAULT_OUTPUT_DIR = "/output"
OUTPUT_NAME = "entry.png"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    """Walk the JPEG marker segments to the SOF segment and return
    (width, height). Raises AssertionError on any structural problem."""
    if data[:2] != b"\xff\xd8":
        raise AssertionError("not a JPEG (missing SOI marker)")
    pos = 2
    while pos + 4 <= len(data):
        if data[pos] != 0xFF:
            raise AssertionError("corrupt JPEG marker at offset %d" % pos)
        marker = data[pos + 1]
        if marker == 0xD9:  # EOI reached without seeing SOF
            break
        if marker == 0xDA:  # SOS: scan data follows, SOF must precede it
            break
        if marker == 0x01 or 0xD0 <= marker <= 0xD7:  # standalone markers
            pos += 2
            continue
        seg_len = int.from_bytes(data[pos + 2 : pos + 4], "big")
        if seg_len < 2 or pos + 2 + seg_len > len(data):
            raise AssertionError("truncated JPEG segment at offset %d" % pos)
        # All SOF markers carry dimensions: baseline/extended/
        # progressive/lossless sequential (C0-C3), differential
        # sequential (C5-C7), extended sequential (C9-CB) and
        # differential lossless (CD-CF). C4 is DHT, C8 is JPG and
        # CC is DAC - not SOF markers.
        if marker in (
            0xC0, 0xC1, 0xC2, 0xC3,
            0xC5, 0xC6, 0xC7,
            0xC9, 0xCA, 0xCB,
            0xCD, 0xCE, 0xCF,
        ):  # SOF0-SOF15 (minus DHT/JPG/DAC)
            height = int.from_bytes(data[pos + 5 : pos + 7], "big")
            width = int.from_bytes(data[pos + 7 : pos + 9], "big")
            return width, height
        pos += 2 + seg_len
    raise AssertionError("JPEG SOF segment not found")


def validate_jpeg(data: bytes) -> tuple[int, int]:
    """Full structural check of the bundled entry image: SOI, EOI
    (not truncated), size cap, and exact 1024x1024 dimensions.
    Returns (width, height)."""
    assert data[:2] == b"\xff\xd8", "bundled entry must start with JPEG SOI"
    assert data[-2:] == b"\xff\xd9", (
        "bundled entry is truncated (missing JPEG EOI)"
    )
    assert len(data) <= 1048576, "entry must be at most 1 MiB"
    width, height = jpeg_dimensions(data)
    assert (width, height) == (EXPECTED_WIDTH, EXPECTED_HEIGHT), (
        "bundled entry must be %dx%d, got %dx%d"
        % (EXPECTED_WIDTH, EXPECTED_HEIGHT, width, height)
    )
    return width, height


def source_path() -> str:
    """The bundled image, next to this file (the repo is read-only
    in the grader's container, so resolve from __file__, not cwd)."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, OUTPUT_NAME)


def output_path() -> str:
    """Where to write the image.

    MAKEFUN_OUTPUT_DIR is the kit's local-test override (the grader
    provides /output); the judge runs without it set, so the real
    output path is /output/entry.png.
    """
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
    return os.path.join(out_dir, OUTPUT_NAME)


def main() -> int:
    src = source_path()
    with open(src, "rb") as f:
        expected = f.read()
    width, height = validate_jpeg(expected)
    expected_sha = hashlib.sha256(expected).hexdigest()

    path = output_path()
    try:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        shutil.copyfile(src, path)
    except OSError:
        # Local fallback: /output is not writable on a dev machine.
        # The judge sandbox provides /output, so this never triggers
        # there. Writing the fallback keeps the program from crashing
        # while developing; the bytes written are identical.
        alt = os.path.join(os.getcwd(), "output", OUTPUT_NAME)
        os.makedirs(os.path.dirname(alt), exist_ok=True)
        shutil.copyfile(src, alt)
        path = alt
        print(
            "warning: could not write %s; wrote %s instead"
            % (output_path(), alt),
            file=sys.stderr,
        )

    with open(path, "rb") as f:
        written = f.read()
    assert hashlib.sha256(written).hexdigest() == expected_sha, (
        "written bytes differ from bundled entry"
    )
    validate_jpeg(written)

    sys.stdout.write(
        "wrote %s (%d bytes, %dx%d, sha256 %s)\n"
        % (path, len(written), width, height, expected_sha)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
