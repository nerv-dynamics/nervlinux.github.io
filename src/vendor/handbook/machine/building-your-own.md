# Building your own

Packaging software for your machine, a repository to serve it from, systems of your own, and owning the stack from the source up.

## Not ready yet

The tools Nerv builds itself with ship in `nerv-dev`, and the repository server is ready to use. Building your own packages and systems with them is still shaped around Nerv's own build machines, and this chapter is written out in full once it is not. What follows is the shape of it.

```
$ doas dnf install nerv-dev
```

## Packaging a program

A package of your own is an RPM spec, built the way Nerv builds its own: `geofront` composes a clean musl build root with `dnf`, runs `rpmbuild` inside it, and publishes the result.

```
$ geofront build --no-publish packages/myprogram/myprogram.spec
```

`nerv-rpm-config` gives every build Nerv's hardened compiler flags and the `.nerv` release tag, and `nerv-musl-clang` is the compiler and linker for musl, which a Rust package names as its linker. Setting up the build root outside Nerv's own build machines is the part still in progress.

## A repository of your own

`nerv-repo` serves packages and systems to your machines, signed, from a host you run:

```
$ doas nerv-repo setup
```

sets a host up, with nginx in front of it. Builders push to it with `nerv-repo push`, the host signs and indexes what it accepts, `nerv-repo candidates` and `nerv-repo promote` move packages from testing to stable, and `nerv-repo mirror` copies the signed result, byte for byte, to mirrors. A machine pointed at your host installs from it as it does from Nerv's.

## Systems of your own

```
$ nerv-install generation --id my-2026-11 --out ./gen --profile workstation
```

composes a generation, a whole system ready to install or update to, from Nerv's repository or yours, and `nerv-repo publish-image` signs and publishes it. Composing systems is moving off individual machines: a machine receives its system and never composes it, and this section changes with that.

## Owning the stack

Nerv is open source under Apache-2.0, every package of it built from source with the tools above. Its source is on Codeberg, `codeberg.org/nerv-dynamics/nerv-linux`, with contributions under the Developer Certificate of Origin and no contributor agreement to sign.
