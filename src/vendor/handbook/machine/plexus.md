# Plexus

Reaching your machines from anywhere: an organisation whose root key only you hold, machines that join it with one code, and access that exists only where you grant it. `plexus` is the program you do it with, and nearly all of it happens in its console.

## Synopsis

After reading this chapter, you will know:

- what an organisation, its root, its authority and its machines are, and which of them holds which key
- how to start an organisation and add a machine to it
- how your machines reach each other, and how to grant one service and take it back
- how machines behind different routers find each other, and when a relay carries them
- how to add another admin, and how to run the authority yourself

Before reading it, you should know:

- what WireGuard is, and how the machine's firewall treats it: [Networking](networking.md)
- how to use `doas`: [The first hour](the-first-hour.md)

## Why it works this way

Reaching your own machines from elsewhere usually means trusting a company's servers with the map of your network, or opening a port and hoping. Plexus does neither. Your machines form one private network over the kernel's WireGuard, wherever each of them is, and the only key that can say who belongs to it is yours.

That key is the **root**. It lives on your computer or on a security key, and it does two things only: it certifies the **authority**, the small service that keeps your organisation, and it admits a new admin. The authority then does the daily work, signing each machine's permissions, but its key can be replaced by your root at any time, and it never holds the root itself. You can run the authority on a machine of your own, or use a provider you trust; either way, what it can do is bounded by what your root certified.

Being a member grants nothing on its own. A machine reaches another only through a rule or a grant you made. Each machine receives its permissions as a signed policy that runs out after an hour unless renewed: a connected machine hears about a revocation at once and withdraws it, and one that is not loses the access when its hour runs out, whether or not it ever hears. Each machine's WireGuard key is sealed by its TPM and never leaves it.

Plexus adds addresses for your machines and routes to the ones you may reach, and nothing else: no DNS, no default route, no route into anyone's LAN. The network you are on is unchanged.

| | |
| --- | --- |
| **the root** | your organisation's key. It certifies the authority and admits admins, and nothing else ever holds it. |
| **the authority** | the service that keeps the organisation: its machines, rules and grants, under a key the root certified |
| **a machine** | a member, with a TPM-sealed key of its own |
| **an admin device** | a computer that approves machines and grants access, with a login key of its own |
| **a relay** | an optional service that carries already-encrypted traffic between machines that cannot reach each other directly, holding no key of yours |

## Opening plexus

Plexus comes with the workstation; on any other machine it is the `plexus-client` package. Run it as yourself, with no arguments:

```
$ plexus
```

- **Organisations**, on the left, lists every organisation this computer knows. `↑` and `↓` select one.
- **Selected organisation** shows its authority, the fingerprint of its root, and where its setup stands.
- **Connection** shows what this machine has of the selected organisation's network: the policy it holds, and separately what it has actually seen of each peer. `F5` refreshes it.
- **Actions** lists only the steps that can come next: **Join this computer** before the machine is a member, **Sign in** before you are, then **Add machine**, **Machines** and **Fleet networking**. `m` lists everything else, and every action keeps its key.

A step that changes the organisation shows what it will do and waits for you to confirm it. `F1` shows the trust details behind what is on screen, and `q` leaves.

## Starting an organisation

1. Choose **New organisation** (`+`).
2. Fill in the form: a name for the organisation on this computer, the organisation's ID, and the authority that will keep it. Each field says what it wants as you reach it.
3. Choose where the root key lives:
   - **a FIDO2 security key**, such as a YubiKey, with its PIN and a touch
   - **an SSH key already in your agent**, a YubiKey's included
   - **a protected software key**, encrypted with a passphrase you type into OpenSSH
4. Certify the authority with the root. With the security key on this computer, plexus runs the ceremony here. With it on another computer, plexus shows a request code to copy there, and takes back the approval code; no file moves and no path is typed.

When it worked, the organisation is selected in **Organisations**, **Selected organisation** shows its root, and **Actions** offers **Add machine**. Setup also made the login key this computer signs in with, separate from the root: the root is needed again only to certify a new authority key or admit another admin, and can stay in a drawer the rest of the time.

A setup interrupted at any point resumes with **Finish organisation setup** (`o`), with the same keys.

> **Warning.** There is no recovering a lost root. Keep it as you would keep the keys to the building.

## Adding a machine

On the new machine:

1. Run `plexus` and choose **Join this computer** (`j`), then press `enter`. It uses the machine's hostname and your organisation's authority; `F4` changes either.
2. Approve the `doas` prompt. It asks once, to start the service that holds this machine's membership.
3. plexus makes a TPM-sealed key for this membership and shows a code, `plx1-…`. `enter` copies it.

On an admin device:

4. Choose **Add machine** (`3`) and paste the code.
5. Read the review: the machine's name and keys, and **Fleet network: on**, which adds it to [your fleet's network](#your-fleets-network). `space` switches that off for this machine. Press `enter` to approve.

When it worked, the new machine connects by itself and its **Connection** panel shows the organisation's network. Nothing was copied between the two computers but the code: no key files, no addresses, no paths.

A code lasts five minutes, and `r` renews it with the same keys. The authority never sees the code itself, and the joining machine checks that the approval came from the organisation it meant to join before it trusts anything.

From a script: `plexus join` on the new machine prints the code and waits, and resumes if run again; `plexus approve plx1-…` approves it, and `--no-fleet-network` leaves it out of the fleet network.

## Your fleet's network

A new organisation has a fleet network rule: every machine in it can reach every other's Plexus address, for SSH, for axon and for anything else you run between them. axon, the program that shares each machine's GPU with the others, is the subject of [The GPU](compute-fabric.md).

To change the rule for the whole organisation, choose **Fleet networking** (`g`). The review lists the machines the rule would cover; confirm it once. Turning the rule off removes what it allowed at once.

The rule lets machines reach each other; it signs nobody in, and SSH still asks who you are.

From a script: `plexus fleet on`, `plexus fleet off`.

## Granting one service

For anything narrower than the whole fleet, grant it:

1. Choose **Grant access** (`4`).
2. Fill in who may reach which service on which machine, and for how long, from a second to thirty days.
3. Read the review, and confirm.

**Revoke access** (`5`) takes a grant back, and **Audit** (`6`) shows what was changed and when. Grants and the fleet rule add up: turning the rule off leaves your grants in place. **Retire machine** (`8`) takes a machine out for good, with every rule and grant that named it.

From a script:

```
$ plexus grant ID SOURCE UID SERVICE TARGET TTL_SECONDS
$ plexus revoke ID
$ plexus retire MACHINE
$ plexus audit
```

## Connecting

A machine is connected to one organisation at a time, and nothing connects on its own at boot.

- **Connect** (`t`) brings the selected organisation's network up, and **Disconnect** (`d`) takes it down.
- **Switch organisation** (`s`) moves to another: the old network is taken down and checked gone before the new one comes up.
- **Peer addresses** (`x`) copies a machine's address, to paste into `ssh`.

Being granted a peer and having reached it are different things, and the **Connection** panel never shows one as the other.

From a script: `plexus connect [--org NAME]`, `plexus disconnect`, and `plexus status --json` for this machine's state.

## Machines that cannot see each other

Two machines behind different home routers usually reach each other directly: the authority tells each where the other can be found, and keeps telling them as they move. When they cannot, a **relay** carries their traffic, already encrypted end to end by WireGuard. The relay sees which two endpoints it joins, never what passes between them, and holds no key of your organisation's.

A relay is used only if you approved it. Choose **Approved relays** (`l`) to see, add or remove them; an organisation with none uses none. A relayed pair keeps trying the direct path and moves back to it when it opens. **Inspect kernel paths** (`z`) shows the path each peer is actually using.

From a script: `plexus relays`, `plexus relay-add https://relay.example.org -`, `plexus relay-remove https://relay.example.org`.

## More than one admin

Any computer can become an admin device.

1. On it, choose **Become admin** (`k`). It makes the computer's own login key and shows a code.
2. On an admin device already signed in, run `plexus add-admin CODE --root ROOT_PUBLIC` and approve it with the root.
3. On the new device, choose **Sign in** (`2`).

Because a new admin needs the root, a stolen login can never make another. A command whose session has expired signs in again by itself with the device's login key, through the SSH agent; if the key is locked, it stops and asks you to sign in.

## Running the authority yourself

The authority is `plexus-host`, from the package of the same name, on a machine you control and your machines can reach over HTTPS. It keeps its state in `/var/lib/plexus-host`, listens on `127.0.0.1:18443` behind a TLS reverse proxy you put in front of it, and runs as its own user with no capabilities.

**Standalone**, it keeps one organisation:

```
$ doas systemd-run --uid=plexus-host --pipe --wait plexus-host init /var/lib/plexus-host/state ORG DOMAIN OWNER https://plexus.example.org ROOT_PUBLIC_HEX
$ doas systemd-run --uid=plexus-host --pipe --wait plexus-host issuer-request /var/lib/plexus-host/state request.bin
$ doas systemd-run --uid=plexus-host --pipe --wait plexus-host issuer-install /var/lib/plexus-host/state issuer.cert
$ doas systemctl enable --now plexus-host.service
```

The request is certified on the computer that holds the root, with `plexus issuer-certify ROOT_PUBLIC request.bin issuer.cert`, and only the certificate comes back. The first owner signs in once with the one-time credential in `/var/lib/plexus-host/state/owner-token`, good for fifteen minutes, and registers a login key for every time after.

**As a provider**, it keeps up to 32 organisations, each with its own root, whose owners create them with **New organisation**:

```
$ doas systemd-run --uid=plexus-host --pipe --wait plexus-host provider-init /var/lib/plexus-host/provider https://plexus.example.org --registration-open
$ doas systemctl enable --now plexus-provider.service
```

Without `--registration-open`, nobody can create an organisation on it, and a provider publishes no list of the organisations it keeps. A relay is a separate service, `plexus-relay`, and running one needs no organisation and no root.

## Windows

Plexus for Windows, from [Downloads](https://nervlinux.org/downloads/), joins a Windows PC the same way, with its key sealed by the PC's TPM, and is a full admin app: starting an organisation with a security key, adding machines, the fleet network, grants and approvals. It remembers whether you were connected across a restart.

## Reference

The keys in plexus:

| key | |
| --- | --- |
| `↑` `↓`, `enter` | select, open |
| `m` | every action, not only the next steps |
| `j` | Join this computer |
| `+`, `o` | New organisation; Finish organisation setup |
| `s` | Switch organisation |
| `t`, `d` | Connect; Disconnect |
| `x` | Peer addresses |
| `1` | Machines |
| `2`, `9` | Sign in; Sign out |
| `3` | Add machine |
| `g` | Fleet networking |
| `4`, `5` | Grant access; Revoke access |
| `6` | Audit |
| `8` | Retire machine |
| `l` | Approved relays |
| `z` | Inspect kernel paths |
| `k` | Become admin |
| `F1` | trust details |
| `F5` | refresh the connection |
| `q` | quit |

The commands, for scripts:

| command | |
| --- | --- |
| `plexus join [PROVIDER] [--name MACHINE]` | join this machine, and wait for approval |
| `plexus approve CODE [--no-fleet-network]` | approve a machine |
| `plexus connect [--org NAME]`, `plexus disconnect` | bring this machine's network up or down |
| `plexus status [--json]` | this machine's state |
| `plexus use NAME` | the organisation commands act on |
| `plexus fleet on\|off` | the fleet network rule |
| `plexus grant …`, `plexus revoke ID` | one service, and taking it back |
| `plexus retire MACHINE` | a machine out for good |
| `plexus audit` | what was changed, and when |
| `plexus relays`, `relay-add`, `relay-remove` | the relays you approved |
| `plexus admin-code`, `plexus add-admin CODE --root ROOT_PUBLIC` | another admin |
| `plexus login`, `plexus logout` | sign in and out |

A command that changes the organisation shows what it will do and asks first; without a terminal it refuses unless given `--yes`. `--org NAME` on any command chooses the organisation for that command. `plexus help` lists every command.
