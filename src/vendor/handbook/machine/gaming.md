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

nQuake is Nerv's own Quake renderer. It plays LibreQuake's free content, and your own copy of Quake too: install Quake through Steam, GOG or Epic and nQuake finds it. With more than one to choose from, it asks at start which to play, and an "Always" answer starts that one from then on; Options › Game › Game Data changes the choice or makes it ask again, from the next start. `quake -librequake` and `quake -nolibrequake` choose on the command line, and the launcher's right-click menu offers "Play LibreQuake" and "Play Quake". `-basedir` names a folder holding Quake outright.

Its renderer has ray-traced shadows and ambient occlusion under Options › nQuake. Its ReSTIR direct row relights every surface per pixel, ray-traced, from every light the map describes: its light entities, its sun, and every surface that glows, in that surface's own colour; muzzle flashes and explosions are lit exactly, and with nQuake particles, explosions, spikes and tracers cast their own light while smoke and blood take the light of the room they drift through, and explosions, bullets and blood leave marks on the walls that whatever lights the wall lights; the ReSTIR GI row adds the light that bounces off every surface, and the sky's own light, so nothing of the map's baked lighting is used. Volumetric fog makes a map's fog a lit medium, with light falling through it in shafts. Water, slime and lava reflect what is above them and show what is under them through a body of their own colour -- water clear for yards, slime for a foot or two, lava opaque and glowing -- and the light that reaches the bottom of a pool came through its waves, which focus it into caustics; seen from inside a liquid, everything is seen through it. A texture pack's normal and gloss maps (DarkPlaces' `_norm` and `_gloss`, beside the textures in `textures/`) bend the light on the walls and give them highlights. HDR & bloom keeps light brighter than a wall's own colour, adapts the exposure like an eye (or holds it at `nq_exposure`), puts a glow around the lights you can see, lets the brightest things bloom, and tone-maps the result. The High preset turns them on, all but the volumetric fog, and with them the anti-alias and upscale row: the scene is drawn with fewer pixels than the screen has, shifted a fraction of a pixel each frame, and its frames are gathered back into the screen's resolution, anti-aliased. On auto it draws about as many pixels as 1280×720 has on any screen, and fewer when the frame rate it aims for -- the lower of the display's refresh and `host_maxfps` -- is above 120: half as many at 240; TAA anti-aliases at the screen's own resolution, and quality, balanced and performance draw the scene 1.5, 2 and 3 times smaller each way. More of its ray-traced lighting is to come. On a machine without the desktop, `doas dnf install nerv-quake` brings it.

## Borrowing a faster GPU

A game is a Vulkan program, and Vulkan is the compute fabric's ([Graphics](compute-fabric.md#graphics)), so a game can draw on a GPU in another machine. Playing that way, with the frames rendered across the room and shown here, and splitting a game's rendering across two GB10s, are on the roadmap.
