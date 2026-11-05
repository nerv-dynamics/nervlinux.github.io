# Plexus

Reaching your machines from anywhere: one authority you run yourself, machines that enrol with it, and access that exists only where you grant it.

## What Plexus does

Plexus joins your machines into one private network over the kernel's WireGuard, wherever each of them is, and decides who may reach what across it. Each machine's WireGuard key is kept by its TPM. The authority hands each machine a signed policy that runs out after an hour unless renewed, so a grant you revoke stops working within minutes even on a machine that never hears about it.

Being enrolled grants nothing on its own. A machine or a person reaches a service on another machine only through a grant you made, for as long as you made it for.

Plexus is in active development. What follows is how it works today; details will change as it settles.

## The authority

The authority is a small service you run on a machine you control, reachable by your machines over HTTPS: `plexus-host`, from the `plexus-host` package. It keeps its state in `/var/lib/plexus-host/state` and listens on `127.0.0.1:18443`, behind a TLS reverse proxy you put in front of it.

Setting it up makes the organisation, asks your root key to certify the authority, and starts it:

```
$ doas systemd-run --uid=plexus-host --pipe --wait plexus-host init /var/lib/plexus-host/state ORG DOMAIN OWNER https://plexus.example.org ROOT_PUBLIC_HEX
$ doas systemd-run --uid=plexus-host --pipe --wait plexus-host issuer-request /var/lib/plexus-host/state request.bin
$ doas systemd-run --uid=plexus-host --pipe --wait plexus-host issuer-install /var/lib/plexus-host/state issuer.cert
$ doas systemctl enable --now plexus-host.service
```

The first owner signs in with a one-time credential the authority writes to `/var/lib/plexus-host/state/owner-token`, good for fifteen minutes, and registers a security key or a signing key for every login after.

## Your organisation's root

The organisation's root key is yours, and the authority never holds it: the root certifies the authority, and the authority certifies everything else. Keep it in an SSH key on a YubiKey, with its PIN and a touch, or on a FIDO2 key, or as a software SSH key:

```
$ plexus create-root
$ plexus issuer-certify request.bin issuer.cert
```

There is no recovering a lost root. Keep it as you would keep the keys to the building.

## Enrolling a machine

On the new machine:

```
$ plexus join plexus.example.org --name gpu2
```

prints a code. On a machine where you are an owner, approve it:

```
$ plexus approve CODE
```

The new machine is a member from then on, and reaches nothing until you grant it something.

## Granting access

```
$ plexus grant ID SOURCE UID SERVICE TARGET TTL_SECONDS
$ plexus revoke ID
```

A grant names who may reach which service on which machine, and for how long, from a second to thirty days. `plexus fleet on` lets the fleet's machines reach one another for the fabric, `plexus retire` takes a machine out for good, and `plexus audit` shows what was granted and when.

## The plexus command

`plexus` on a terminal opens the owner console: your machines, their state, grants and relays, with every change confirmed before it is made. Every action in it is also a command, for scripts; `plexus help` lists them, and `plexus status --json` reports this machine's state. A command that changes something refuses to run without a terminal unless given `--yes`.

## More than one organisation

`plexus` keeps a context for each organisation you belong to, up to 32, in `~/.config/plexus/owner`. `plexus use NAME`, or `--org NAME` on any command, chooses one. A machine is connected to one organisation's network at a time; switching disconnects the old one first.
