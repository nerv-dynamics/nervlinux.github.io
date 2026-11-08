# Gaming

Steam, titles built for x86, and borrowing a faster GPU from across the room.

## Not ready yet

Gaming on Nerv is in active development. The pieces below exist and are being proven one by one; Steam itself is not yet something to rely on. This chapter is written out in full once a Steam game runs from start to finish.

## What is there

```
$ doas dnf install nerv-gaming
$ steam
```

`nerv-gaming` brings Steam's launcher, FEX, which runs x86 programs on the GB10's Arm processors, the x86 system FEX runs them on, and the desktop Steam draws on, so a machine installed without one boots to the login screen afterwards. The first `steam` fetches Valve's signed Steam client, checks it, and starts it under FEX.

Windows games run through Proton, Nerv's build of it for Arm: Wine itself is native, the graphics translation is native Arm code, and only the game's own code is translated by FEX. An x86 Direct3D 11 program already draws on the GB10 this way, through the compute fabric. It registers in Steam as `nerv-proton-preview`, not yet as the default.

## What does not work yet

- Logging in to Steam and running a game from start to finish has not been shown.
- Games that use Steam's own API do not start yet.
- Remapping a controller in Steam Input is refused; a plain gamepad works.
- Linux games built for x86 are not part of the first release.
- DLSS has no path on Arm yet.

## Quake

Quake comes with the desktop and runs today, natively, doubling as the proof that the GPU path works: nQuake, in the launcher, or

```
$ quake
```

nQuake is Nerv's own Quake renderer, playing LibreQuake's free content, with ray-traced shadows and ambient occlusion under Options › nQuake. Its ReSTIR direct row relights every surface per pixel, ray-traced, from every light the map describes: its light entities, its sun, and every surface that glows, in that surface's own colour; muzzle flashes and explosions are lit exactly, and with nQuake particles, explosions, spikes and tracers cast their own light while smoke and blood take the light of the room they drift through; the ReSTIR GI row adds the light that bounces off every surface, and the sky's own light, so nothing of the map's baked lighting is used. Volumetric fog makes a map's fog a lit medium, with light falling through it in shafts. No preset turns them on yet, and while they are on the scene is drawn without anti-aliasing; both wait for the upscaler of a later stage. More of its ray-traced lighting is to come. On a machine without the desktop, `doas dnf install nerv-quake` brings it.

## Borrowing a faster GPU

A game is a Vulkan program, and Vulkan is the compute fabric's ([Graphics](compute-fabric.md#graphics)), so a game can draw on a GPU in another machine. Playing that way, with the frames rendered across the room and shown here, and splitting a game's rendering across two GB10s, are on the roadmap.
