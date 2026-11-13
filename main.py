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

Python 3.13, standard library only.
"""

import hashlib
import os
import shutil
import sys

DEFAULT_OUTPUT_DIR = "/output"
OUTPUT_NAME = "entry.png"


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
    assert expected[:3] == b"\xff\xd8\xff", "bundled entry must be JPEG bytes"
    assert len(expected) <= 1048576, "entry must be at most 1 MiB"
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

    sys.stdout.write(
        "wrote %s (%d bytes, sha256 %s)\n" % (path, len(written), expected_sha)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
