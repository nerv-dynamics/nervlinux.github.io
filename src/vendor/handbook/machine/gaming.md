# Gaming

Steam, titles built for x86, and borrowing a faster GPU from across the room.

## Not ready yet

Gaming on Nerv is in active development. The pieces below exist and are being proven one by one; Steam itself is not yet something to rely on. This chapter is written out in full once a Steam game runs from start to finish.

## What is there

```
$ doas dnf install nerv-gaming
$ steam
```

`nerv-gaming` brings Steam's launcher, FEX, which runs x86 programs on the GB10's Arm processors, and the x86 system FEX runs them on. The first `steam` fetches Valve's signed Steam client, checks it, and starts it under FEX.

Windows games run through Proton, Nerv's build of it for Arm: Wine itself is native, the graphics translation is native Arm code, and only the game's own code is translated by FEX. An x86 Direct3D 11 program already draws on the GB10 this way, through the compute fabric. It registers in Steam as `nerv-proton-preview`, not yet as the default.

## What does not work yet

- Logging in to Steam and running a game from start to finish has not been shown.
- Games that use Steam's own API do not start yet.
- Remapping a controller in Steam Input is refused; a plain gamepad works.
- Linux games built for x86 are not part of the first release.
- DLSS has no path on Arm yet.

## Quake

Quake runs today, natively, and doubles as the proof that the GPU path works:

```
$ doas dnf install nerv-librequake
$ librequake
```

`librequake` is vkQuake with LibreQuake's free content. `nerv-quake` installs `quake`, Nerv's own vkQuake, with ray-traced shadows and ambient occlusion under Options › nQuake; more of its ray-traced lighting is to come.

## Borrowing a faster GPU

A game is a Vulkan program, and Vulkan is the compute fabric's ([Graphics](compute-fabric.md#graphics)), so a game can draw on a GPU in another machine. Playing that way, with the frames rendered across the room and shown here, and splitting a game's rendering across two GB10s, are on the roadmap.
