# Tic-Tac-Toe in BASIC09

[BASIC09](https://en.wikipedia.org/wiki/BASIC09) ports, for OS-9 on the TRS-80 Color Computer.

These are not hand-written. Each one was translated from the BASIC in
this repository by [decb-to-b09](https://github.com/jamieleecho/coco-tools), so it keeps the
structure and the wording of the original.

## `tictactoe1.b09`

Converted from [`tictactoe1.bas`](../tictactoe1.bas) with:

```sh
decb-to-b09 -l -O -t --basic09-for-loops tictactoe1.bas tictactoe1.b09
```

## `tictactoe2.b09`

Converted from [`tictactoe2.bas`](../tictactoe2.bas) with:

```sh
decb-to-b09 -l -O -t --basic09-for-loops tictactoe2.bas tictactoe2.b09
```

## Running one

Put the file on an OS-9 disk, then from BASIC09:

```text
B: load tictactoe1.b09
B: run tictactoe1
```

`load` also reports anything BASIC09 rejects, so it doubles as a
syntax check. The converter emits a few small helper procedures ahead
of the program itself; the program is the last one `load` lists.

See [`00_Utilities/basic09`](../../../00_Utilities/basic09) for how
these are built and checked.
