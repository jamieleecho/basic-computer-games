#!/usr/bin/env python3
"""Load and run converted BASIC Computer Games programs under os9emu's BASIC09.

For each .b09 in the given directory this loads the program, runs it against a
canned stream of keystrokes and reports what happened.  BASIC09 writes its
errors to stderr, and it reports the end of the canned input as ERROR #211,
which is how a scripted run normally ends rather than a failure.

  python check.py ../../00_Alternate_Languages
  python check.py --load-only ../../00_Alternate_Languages
  python check.py ../../00_Alternate_Languages -v bounce   # one program's output
"""

import argparse
import os
import re
import subprocess
import sys
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

OS9EMU = os.environ.get("OS9EMU", os.path.expanduser("~/src/OS9Emu/build/os9emu"))
OS9ROOT = os.environ.get("OS9ROOT", os.path.expanduser("~/OS9"))
WORKDIR = "B09CHECK"
INPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs")

# Typing 1 answers most prompts: it is a valid number, a valid string and a
# valid menu choice.  Programs that need more have a file in bcg/inputs.
DEFAULT_INPUT = "1\n" * 60

OUTPUT_CAP = 400_000  # stop reading a program that will not stop printing
UNPRINTABLE = re.compile(rb"[^\t\n\r -~]")
PROMPT = re.compile(r"^(?:[BD]:)+")
PROCEDURE = re.compile(rb"(?:\A|[\r\n])procedure[ \t]+([A-Za-z_][A-Za-z0-9_.]*)")


def entry_procedure(source):
    """The converted program's own procedure is the last one in the file.

    The ones before it are the runtime helpers the converter emits.
    """
    names = PROCEDURE.findall(source)
    return names[-1].decode() if names else None


def canned_input(name):
    path = os.path.join(INPUT_DIR, name + ".txt")
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return DEFAULT_INPUT


def basic09(b09_path, name, do_run, timeout, mem="32k", stream=None):
    """Run one program and return its console output.

    stream overrides the keystrokes the program is fed; by default they come
    from bcg/inputs/<name>.txt, or DEFAULT_INPUT when there is no such file.
    """
    dest_dir = os.path.join(OS9ROOT, WORKDIR)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, name + ".b09")
    with open(b09_path, "rb") as f:
        source = f.read()
    with open(dest, "wb") as f:
        f.write(source)

    script = f"load {WORKDIR}/{name}.b09\r"
    if do_run:
        entry = entry_procedure(source) or name
        keys = canned_input(name) if stream is None else stream
        script += f"run {entry}\r" + keys.replace("\n", "\r")
    script += "bye\r"

    proc = subprocess.Popen(
        [OS9EMU, "--eol", "crlf", "--mem", mem, "basic09"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    out = bytearray()

    def read_output():
        while len(out) < OUTPUT_CAP:
            chunk = proc.stdout.read(256)
            if not chunk:
                break
            out.extend(chunk)
            # Once the canned input runs out BASIC09 sits in its debugger
            # answering "D:What?" forever.  Nothing after that is interesting.
            if out.count(b"D:What?") > 8:
                break
        proc.kill()

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()
    try:
        proc.stdin.write(script.encode())
        proc.stdin.flush()
        proc.stdin.close()
    except (BrokenPipeError, OSError):
        pass
    reader.join(timeout=timeout)
    timed_out = reader.is_alive()
    if timed_out:
        proc.kill()
        reader.join(timeout=5)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    try:
        os.remove(dest)
    except OSError:
        pass
    return UNPRINTABLE.sub(b"", bytes(out)).decode("ascii", "replace"), timed_out


def program_output(line):
    """Strip BASIC09's prompts and chatter, leaving what the program printed."""
    previous = None
    while previous != line:
        previous = line
        line = PROMPT.sub("", line).strip()
        for noise in ("Ready", "What?"):
            if line.startswith(noise):
                line = line[len(noise) :].strip()
    return line


def classify(text, timed_out, do_run):
    lines = text.replace("\r", "\n").split("\n")
    # Loading echoes one procedure name per line and ends at the next "Ready";
    # everything after that belongs to the run.
    readys = [i for i, l in enumerate(lines) if program_output(l) == "" and "Ready" in l]
    split = readys[1] if len(readys) > 1 else 0
    loading, running = lines[: split + 1], lines[split + 1 :]

    load_errors = sorted({l.strip() for l in loading if "ERROR #" in l})
    run_errors = sorted(
        {l.strip() for l in running if "ERROR #" in l and "#211" not in l}
    )
    printed = [l for l in map(program_output, running) if l]

    if load_errors:
        status = "LOAD-ERROR"
    elif not do_run:
        status = "LOADS"
    elif run_errors:
        status = "RUN-ERROR"
    elif timed_out:
        status = "TIMEOUT"
    elif len(printed) >= 3:
        status = "RUNS"
    else:
        status = "NO-OUTPUT"
    return status, load_errors, run_errors, len(printed)


def check(path, do_run, timeout, mem="32k"):
    name = os.path.basename(path)[: -len(".b09")]
    try:
        text, timed_out = basic09(path, name, do_run, timeout, mem)
    except Exception as exc:  # the emulator failed to start, or the file is unreadable
        return name, "HARNESS-ERROR", [], [str(exc)], 0, ""
    status, load_errors, run_errors, printed = classify(text, timed_out, do_run)
    return name, status, load_errors, run_errors, printed, text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "directory", help="directory searched for converted .b09 programs"
    )
    parser.add_argument("--load-only", action="store_true", help="do not run, only load")
    parser.add_argument("--timeout", type=int, default=60, help="seconds per program")
    parser.add_argument("--jobs", type=int, default=8, help="programs to run at once")
    parser.add_argument("--mem", default="32k", help="BASIC09 workspace size")
    parser.add_argument(
        "--known",
        action="append",
        default=[],
        metavar="NAME",
        help="a program whose failure is a known limitation; still reported, "
        "but does not fail the run. Repeat for each one.",
    )
    parser.add_argument("-v", "--verbose", metavar="NAME", help="print NAME's output")
    args = parser.parse_args()

    if not os.path.exists(OS9EMU):
        sys.exit(f"{OS9EMU} not found; set OS9EMU to the os9emu binary")

    # The programs sit one per game, in <game>/basic09/, so search the tree.
    paths = sorted(
        os.path.join(parent, f)
        for parent, _, files in os.walk(args.directory)
        for f in files
        if f.endswith(".b09")
    )
    if not paths:
        sys.exit(f"no .b09 programs under {args.directory}")
    if args.verbose:
        paths = [p for p in paths if os.path.basename(p)[:-4] == args.verbose]
        if not paths:
            sys.exit(f"no program named {args.verbose} in {args.directory}")

    do_run = not args.load_only
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(
            pool.map(lambda p: check(p, do_run, args.timeout, args.mem), paths)
        )

    ok = {"RUNS", "LOADS"}
    failed = []
    for name, status, load_errors, run_errors, printed, text in sorted(
        results, key=lambda r: (r[1] in ok, r[0])
    ):
        detail = ""
        if load_errors:
            detail += "  load: " + "; ".join(load_errors)
        if run_errors:
            detail += "  run: " + "; ".join(run_errors)
        if status not in ok:
            if name in args.known:
                detail += "  (known limitation)"
            else:
                failed.append(name)
        print(f"{status:11} {name:22} {printed:5} lines{detail}")
        if args.verbose:
            print(text)

    counts = Counter(r[1] for r in results)
    print("\n" + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    if failed:
        print("failed: " + ", ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
