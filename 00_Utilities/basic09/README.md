# BASIC09 ports

[BASIC09](https://en.wikipedia.org/wiki/BASIC09) is Microware's structured
BASIC for OS-9, and the version Tandy shipped for the TRS-80 Color Computer.
It is close enough to the BASIC in this repository to translate mechanically,
and far enough away — no line numbers, typed variables, fixed-size arrays,
procedures instead of `GOSUB` — to be worth translating rather than running
as-is.

So the ports in `00_Alternate_Languages/<game>/basic09/` are not hand-written.
Each is produced by [decb-to-b09](https://github.com/jamieleecho/coco-tools)
from the BASIC next to it, which keeps the structure and the wording of the
original. This directory is the build.

```sh
make -C 00_Utilities/basic09              # convert, and write each README
make -C 00_Utilities/basic09 check        # also load and run each one
make -C 00_Utilities/basic09 check-load   # load only, a syntax check
make -C 00_Utilities/basic09 clean
make -C 00_Utilities/basic09 help
```

The converter lives in a separate checkout. The makefile expects it beside this
one; point `COCO_TOOLS` somewhere else if it is not.

## Conversion flags

Nearly every program converts on the same four flags:

    -l -O -t --basic09-for-loops

which drop unreferenced line numbers, store integer-only variables as BASIC09
`INTEGER`, target a plain terminal rather than a CoCo screen, and use BASIC09's
own `FOR` semantics. Six programs need something more, and each carries a
`FLAGS_<name>` override in the makefile next to a comment naming what in the
program requires it. Every folder's README quotes the exact command its
programs were built with.

## What converts

100 of the 105 BASIC programs convert, and 99 of those load, run and print
output under real BASIC09. The rest:

| Program                              | Why not                                            |
| ------------------------------------ | -------------------------------------------------- |
| `awari`, `checkers`                  | a `NEXT` closes a `FOR` opened in another block, which BASIC09 cannot express |
| `checkers.annotated`                 | a commented listing, not a program                  |
| `king_variable_update`               | uses long variable names DECB rejects               |
| `splat`                              | the original branches to line 540, which is not there |
| `superstartrek`                      | converts, but is one procedure larger than BASIC09 can load |

`superstartrek` is a BASIC09 limit rather than a conversion defect: past about
27.7KB of source in a single procedure, adding any line at all — even a
comment — makes `load` spin forever instead of returning an error. Running it
would mean splitting it across procedures.

## Checking

`check.py` runs each converted program under
[os9emu](https://github.com/jamieleecho/OS9Emu)'s BASIC09. It loads the
program, which is a syntax check on its own, then runs it against a canned
stream of keystrokes and reports one of `RUNS`, `LOADS`, `LOAD-ERROR`,
`RUN-ERROR`, `NO-OUTPUT` or `TIMEOUT`.

BASIC09 reports the end of the canned input as `ERROR #211 - End of File`,
which is how a scripted run normally ends rather than a failure, so the check
ignores it. Set `OS9EMU` and `OS9ROOT` if they are not in their usual places.

Typing `1` answers most prompts, so that is the default. A program that needs
something else — a `YES`, a maze size, a Life pattern — has a file of its own
in `inputs/<name>.txt`, one answer per line.

This is not a correctness comparison against the original BASIC. It catches
programs that fail to load or blow up while running; it would not catch a
program that runs happily and prints the wrong thing.
