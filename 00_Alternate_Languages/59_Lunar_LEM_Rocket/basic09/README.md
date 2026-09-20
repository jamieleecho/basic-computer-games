# Lunar LEM Rocket in BASIC09

[BASIC09](https://en.wikipedia.org/wiki/BASIC09) ports, for OS-9 on the TRS-80 Color Computer.

These are not hand-written. Each one was translated from the BASIC in
this repository by [decb-to-b09](https://github.com/jamieleecho/coco-tools), so it keeps the
structure and the wording of the original.

## `lem.b09`

Converted from [`lem.bas`](../lem.bas) with:

```sh
decb-to-b09 -l -O -t --basic09-for-loops lem.bas lem.b09
```

## `lunar.b09`

Converted from [`lunar.bas`](../lunar.bas) with:

```sh
decb-to-b09 -l -O -t --basic09-for-loops lunar.bas lunar.b09
```

## `rocket.b09`

Converted from [`rocket.bas`](../rocket.bas) with:

```sh
decb-to-b09 -l -O -t --basic09-for-loops rocket.bas rocket.b09
```

## Running one

Put the file on an OS-9 disk, then from BASIC09:

```text
B: load lem.b09
B: run lem
```

`load` also reports anything BASIC09 rejects, so it doubles as a
syntax check. The converter emits a few small helper procedures ahead
of the program itself; the program is the last one `load` lists.

See [`00_Utilities/basic09`](../../../00_Utilities/basic09) for how
these are built and checked.
