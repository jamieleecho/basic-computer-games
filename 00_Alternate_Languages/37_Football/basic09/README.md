# Football in BASIC09

[BASIC09](https://en.wikipedia.org/wiki/BASIC09) ports, for OS-9 on the TRS-80 Color Computer.

These are not hand-written. Each one was translated from the BASIC in
this repository by [decb-to-b09](https://github.com/jamieleecho/coco-tools), so it keeps the
structure and the wording of the original.

## `football.b09`

Converted from [`football.bas`](../football.bas) with:

```sh
decb-to-b09 -l -O -t --basic09-for-loops football.bas football.b09
```

## `ftball.b09`

Converted from [`ftball.bas`](../ftball.bas) with:

```sh
decb-to-b09 -l -O -t --basic09-for-loops ftball.bas ftball.b09
```

## Running one

Put the file on an OS-9 disk, then from BASIC09:

```text
B: load football.b09
B: run football
```

`load` also reports anything BASIC09 rejects, so it doubles as a
syntax check. The converter emits a few small helper procedures ahead
of the program itself; the program is the last one `load` lists.

See [`00_Utilities/basic09`](../../../00_Utilities/basic09) for how
these are built and checked.
