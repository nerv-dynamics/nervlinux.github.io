# Plexus

Reaching your machines from anywhere: an organisation whose root key only you hold, machines that join it with one code, and access that exists only where you grant it.

## What Plexus does

Plexus joins your machines into one private network over the kernel's WireGuard, wherever each of them is, and decides who may reach what across it. Each machine's WireGuard key is sealed by its TPM and never leaves it.

Being a member grants nothing on its own. A machine reaches another only through a rule or a grant you made, for as long as you made it for. The authority hands each machine its permissions as a signed policy that runs out after an hour unless renewed. A machine that is connected hears about a revocation at once and withdraws it; one that is not loses the access when its hour runs out, whether or not it ever hears.

Plexus adds addresses for your machines and routes to the ones you may reach, and nothing else: no DNS, no default route, no route into anyone's LAN. The network you are on is unchanged.

Plexus comes with the workstation. On any other machine it is the `plexus-client` package.

## The parts

| | |
| --- | --- |
| **the root** | your organisation's key, on your own computer or a security key. It certifies the authority and admits new admins, and nothing else ever holds it. |
| **the authority** | the service that keeps your organisation: its machines, rules and grants. You run it yourself or use a provider you trust, and it holds only a key your root certified, which your root can replace. |
| **a machine** | a member of the organisation, with a TPM-sealed key of its own |
| **an admin device** | a computer that can approve machines and grant access, with a login key of its own |
| **a relay** | an optional service that carries encrypted traffic between machines that cannot reach each other directly. It holds no key of yours. |

## Starting an organisation

Run `plexus` and choose **New organisation** (`+`). It asks for a name for the organisation on this computer, the organisation's ID, and the authority that will keep it. Then it asks where the root key lives:

- **a FIDO2 security key**, such as a YubiKey, with its PIN and a touch;
- **an SSH key already in your agent**, a YubiKey's included;
- **a protected software key**, encrypted with a passphrase you type into OpenSSH.

With the security key on this computer, setup runs the root ceremony here. With it on another computer, setup shows a request code to copy there and takes the approval code back, so no file moves and no path is typed. A setup interrupted at any point resumes with **Finish organisation setup** (`o`), with the same identities.

Setup also makes the login key this computer signs in with. It is separate from the root: the root is needed only to certify the authority's key and to admit another admin, and can stay in a drawer the rest of the time.

There is no recovering a lost root. Keep it as you would keep the keys to the building.

## Adding a machine

On the new machine, run `plexus` and choose **Join this computer**, then press enter. It uses the machine's hostname and your organisation's authority (`F4` changes either), asks `doas` once, makes a TPM-sealed key for this membership, and shows a code:

```
plx1-…
```

On an admin device, choose **Add machine** and paste the code, or:

```
$ plexus approve plx1-…
```

The review shows the machine's name and keys, and whether it joins your fleet network. Approve it, and the new machine connects by itself. Nothing else is copied between the two: no key files, no addresses, no paths.

A code lasts five minutes, and `r` renews it with the same keys. The authority never sees the code itself, and the joining machine checks that the approval came from the organisation it meant to join before it trusts anything.

From a script on the new machine, `plexus join` prints the code and waits for the approval, and running it again resumes where it stopped.

## Your fleet's network

A new organisation has a fleet network rule: every machine in it can reach every other's Plexus address, for SSH, for [axon](compute-fabric.md) and for anything else you run between them. Each machine you approve joins it, unless you switch it off for that machine in the review (space in the terminal).

`g` in `plexus`, or `plexus fleet on` and `plexus fleet off`, changes the rule for the whole organisation, after showing the machines it would cover. Turning it off removes what it allowed at once. The rule lets machines reach each other; it signs nobody in, and SSH still asks who you are.

## Granting one service

For anything narrower than the whole fleet, grant it:

```
$ plexus grant ID SOURCE UID SERVICE TARGET TTL_SECONDS
$ plexus revoke ID
```

A grant names who may reach which service on which machine, and for how long, from a second to thirty days. Grants and the fleet rule add up: turning the rule off leaves your grants in place. `plexus retire` takes a machine out for good, with every rule and grant that named it, and `plexus audit` shows what was changed and when.

## Connecting

A machine is connected to one organisation at a time. **Connect** and **Disconnect** in `plexus`, or `plexus connect` and `plexus disconnect`, bring the link up and down, and `plexus connect --org NAME` switches to another organisation: it takes the old one down and checks that it is gone before the new one comes up. Nothing reconnects on its own at boot.

`plexus status` shows what this machine has: the policy it holds, and separately what it has actually seen of each peer. Being granted a peer and having reached it are different things, and it never shows one as the other. **Peer addresses** copies a machine's address to paste into `ssh`.

## Machines that cannot see each other

Two machines behind different home routers usually reach each other directly: the authority tells each where the other can be found, and that changes as they move. When they cannot, a relay carries their traffic, already encrypted end to end by WireGuard. The relay sees which two endpoints it joins, never what passes between them, and holds no key of your organisation's.

A relay is used only if you approved it. **Approved relays** (`l`) in `plexus`, or:

```
$ plexus relay-add https://relay.example.org -
$ plexus relays
```

An organisation with no approved relay uses none. A relayed pair keeps trying the direct path and moves back to it when it opens. `z` in `plexus` shows the path each peer is actually using.

## More than one admin

Any computer can become an admin device. On it:

```
$ plexus admin-code
```

makes its own login key and shows a code. On an admin device already signed in, `plexus add-admin CODE --root ROOT_PUBLIC` reviews it and approves it with the root, so a stolen login can never make another admin. The new device then signs in with `plexus login`.

Commands sign in by themselves when the session has expired, using this device's login key through the SSH agent. If the key is locked, the command stops and asks you to run `plexus login`.

## The plexus command

`plexus` on a terminal opens the console. It shows only the steps that can come next: **Join this computer** before the machine is a member, **Sign in** before you are, then **Add machine**, **Machines** and **Fleet networking**. `m` lists everything else.

Every action in it is also a command, for scripts; `plexus help` lists them, and `plexus status --json` reports this machine's state. A command that changes the organisation shows what it will do and asks first; without a terminal it refuses unless given `--yes`.

`plexus` keeps each organisation you belong to, up to 32, in `~/.config/plexus/owner`, each with its own authority, root and session. `plexus use NAME` chooses the one commands act on, and `--org NAME` on any command chooses one for that command.

## Running the authority yourself

The authority is a small service, `plexus-host` from the package of the same name, on a machine you control and your machines can reach over HTTPS. It keeps its state in `/var/lib/plexus-host`, listens on `127.0.0.1:18443`, and sits behind a TLS reverse proxy you put in front of it. It runs as its own user, with no capabilities.

It runs one of two ways. **Standalone** keeps one organisation:

```
$ doas systemd-run --uid=plexus-host --pipe --wait plexus-host init /var/lib/plexus-host/state ORG DOMAIN OWNER https://plexus.example.org ROOT_PUBLIC_HEX
$ doas systemd-run --uid=plexus-host --pipe --wait plexus-host issuer-request /var/lib/plexus-host/state request.bin
$ doas systemd-run --uid=plexus-host --pipe --wait plexus-host issuer-install /var/lib/plexus-host/state issuer.cert
$ doas systemctl enable --now plexus-host.service
```

The request is certified on the computer that holds the root, with `plexus issuer-certify ROOT_PUBLIC request.bin issuer.cert`, and only the certificate comes back. The first owner signs in once with the one-time credential in `/var/lib/plexus-host/state/owner-token`, good for fifteen minutes, and registers a login key for every time after.

**As a provider** it keeps up to 32 organisations, each with its own root, and lets their owners create them with **New organisation**:

```
$ doas systemd-run --uid=plexus-host --pipe --wait plexus-host provider-init /var/lib/plexus-host/provider https://plexus.example.org --registration-open
$ doas systemctl enable --now plexus-provider.service
```

Without `--registration-open`, nobody can create an organisation on it. A provider publishes no list of the organisations it keeps.

A relay is a separate service, `plexus-relay`, and running one needs no organisation and no root.

## Windows

Plexus for Windows, from [Downloads](https://nervlinux.org/downloads/), joins a Windows PC to your organisation the same way, with its key sealed by the PC's TPM, and is a full admin app: creating an organisation with a security key, adding machines, the fleet network, grants and approvals. It remembers whether you were connected across a restart.
