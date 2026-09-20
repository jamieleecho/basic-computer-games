#!/usr/bin/env python3
"""Write the README.md for one game's basic09 folder.

The makefile records, for every program it converts, the source it came from
and the flags it used. This turns those records into a README that quotes the
exact command, so the folder documents itself and cannot drift from the build.
"""

import argparse
import os
import shlex

TITLE_FIXUPS = {"Iq": "IQ", "Lem": "LEM", "3 D": "3-D"}

BASIC09 = "https://en.wikipedia.org/wiki/BASIC09"
COCO_TOOLS = "https://github.com/jamieleecho/coco-tools"


def game_title(game):
    """Turn a folder name like 48_High_IQ into "High IQ"."""
    name = game.split("_", 1)[1] if "_" in game else game
    title = name.replace("_", " ")
    for wrong, right in TITLE_FIXUPS.items():
        title = title.replace(wrong, right)
    return title


def read_records(records_dir, game):
    """Each record is one program: its source file, then one flag per line."""
    programs = []
    prefix = game + "__"
    for entry in sorted(os.listdir(records_dir)):
        if not entry.startswith(prefix) or not entry.endswith(".rec"):
            continue
        name = entry[len(prefix) : -len(".rec")]
        with open(os.path.join(records_dir, entry)) as f:
            lines = [l.rstrip("\n") for l in f if l.strip()]
        programs.append((name, lines[0], lines[1:]))
    return programs


def render(game, programs):
    title = game_title(game)
    out = [
        f"# {title} in BASIC09",
        "",
        f"[BASIC09]({BASIC09}) ports, for OS-9 on the TRS-80 Color Computer.",
        "",
        "These are not hand-written. Each one was translated from the BASIC in",
        f"this repository by [decb-to-b09]({COCO_TOOLS}), so it keeps the",
        "structure and the wording of the original.",
        "",
    ]

    for name, source, flags in programs:
        out += [
            f"## `{name}.b09`",
            "",
            f"Converted from [`{source}`](../{source}) with:",
            "",
            "```sh",
            f"decb-to-b09 {shlex.join(flags)} {source} {name}.b09",
            "```",
            "",
        ]
        if name != os.path.splitext(source)[0]:
            out += [
                f"The file is named `{name}.b09` rather than after `{source}`"
                " because OS-9 file names cannot contain `-`.",
                "",
            ]

    out += [
        "## Running one",
        "",
        "Put the file on an OS-9 disk, then from BASIC09:",
        "",
        "```text",
        f"B: load {programs[0][0]}.b09",
        f"B: run {programs[0][0]}",
        "```",
        "",
        "`load` also reports anything BASIC09 rejects, so it doubles as a",
        "syntax check. The converter emits a few small helper procedures ahead",
        "of the program itself; the program is the last one `load` lists.",
        "",
        "See [`00_Utilities/basic09`](../../../00_Utilities/basic09) for how",
        "these are built and checked.",
    ]
    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", required=True, help="the game folder name")
    parser.add_argument("--records", required=True, help="directory of .rec files")
    parser.add_argument("--out", required=True, help="README.md to write")
    args = parser.parse_args()

    programs = read_records(args.records, args.game)
    if not programs:
        raise SystemExit(f"no conversion records for {args.game} in {args.records}")
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        f.write(render(args.game, programs))


if __name__ == "__main__":
    main()
