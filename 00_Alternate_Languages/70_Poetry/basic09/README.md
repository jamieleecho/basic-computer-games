# Poetry in BASIC09

[BASIC09](https://en.wikipedia.org/wiki/BASIC09) ports, for OS-9 on the TRS-80 Color Computer.

These are not hand-written. Each one was translated from the BASIC in
this repository by [decb-to-b09](https://github.com/jamieleecho/coco-tools), so it keeps the
structure and the wording of the original.

## `poetry.b09`

Converted from [`poetry.bas`](../poetry.bas) with:

```sh
decb-to-b09 -l -O -t --basic09-for-loops poetry.bas poetry.b09
```

## Running one

Put the file on an OS-9 disk, then from BASIC09:

```text
B: load poetry.b09
B: run poetry
```

`load` also reports anything BASIC09 rejects, so it doubles as a
syntax check. The converter emits a few small helper procedures ahead
of the program itself; the program is the last one `load` lists.

See [`00_Utilities/basic09`](../../../00_Utilities/basic09) for how
these are built and checked.
