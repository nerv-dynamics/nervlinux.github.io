# Firmware

Updating the board's own firmware — the UEFI, the embedded controller, the USB power controller — from the vendor's releases on LVFS, as one step that is checked before it starts, applied by the firmware during a reboot you choose, and reported after it, including whether the update reset the machine's Secure Boot keys or its TPM.

## What the firmware reports

`cage firmware` lists every component the firmware can update, the version installed, the newest version LVFS offers this machine, and how the last update of it went:

```
$ doas cage firmware
board     gb10 — HP ZGX Nano G1n AI Station, BIOS 5.36_0ACUM026
delivery  capsule on disk; OsIndicationsSupported 0x1f; Secure Boot on
LVFS      metadata signed by fwupd.org 2025 at 2026-11-06 09:12:37 UTC, verified

NAME     GUID                                  TYPE    INSTALLED  LVFS       LAST ATTEMPT
UEFI     0f5bb700-74e8-4e13-a99e-bf9476fe157e  device  2.148.24   2.155.14 * 2.148.24 success
EC       65177e8c-f47b-4094-a5d9-4c8930287ea3  device  2.78.27    3.5.11 *   2.78.27 success
TPM      0eb9bda9-3010-493a-a6a8-b5e80eddf870  device  7.2.4.1    -          none
USB-PD   fcdb2933-d16b-406d-ae0a-b913d0c3e1bf  device  0.0.1      0.5.22 *   none

  * newer than installed: `cage firmware update` stages them

no update offered:
  TPM: none of LVFS's 7 components for it is for this machine
```

A release is offered only when LVFS says it is for this exact machine: its vendor and its hardware IDs, not only the component. Several vendors build on the same board and share component IDs, and each vendor's release goes to that vendor's machines alone. `--offline` answers from the copy of LVFS's list checked last time.

## Before an update

`cage firmware update` checks first and changes nothing unless every check passes:

- **A way back in without the TPM.** An update can reset the TPM, and the TPM is what unlocks the disk. The machine must have a fleet recovery key, as [A forgotten passphrase](recovery.md#a-forgotten-passphrase) sets up, or an unencrypted root.
- **One change per reboot.** The running slot must have completed a boot, and no new slot may be waiting to boot. If something goes wrong after the reboot, it was the firmware. [Generations](generations.md) explains slots and their first boot.
- **Secure Boot keys ready to go back in.** An update can reset the firmware's keys to the vendor's, and then the firmware refuses everything this machine signed. With Secure Boot on, the machine's own keys must be staged on the boot partition first, which takes one command:

```
$ doas nerv-install secureboot --stage-auth /efi/loader/keys/nerv
```

- **Mains power.** A machine with a battery must be plugged in and charged.

## Updating

Run it with no arguments to stage every update offered, or name the components by their GUID:

```
$ doas cage firmware update fcdb2933-d16b-406d-ae0a-b913d0c3e1bf
:: LVFS metadata verified: signed by fwupd.org 2025 at 2026-11-06 09:12:37 UTC
:: USB-PD: 0.0.1 -> 0.5.22 (high urgency, LVFS com.hp.usbpd.firmware "USB PD")
  ok   firmware reads capsules from disk (OsIndicationsSupported 0x1f)
  ok   a way back in without the TPM: escrowed to fleet age1… (keyslot 2)
  ok   booted slot @nerv is blessed and is what boots next
  ok   Secure Boot is off: there are no keys for the update to reset
  ok   power: mains-powered, no battery
:: USB-PD: UsbPd.cap verified (1051385 bytes, targets fcdb2933-d16b-406d-ae0a-b913d0c3e1bf)
:: staged firmware update 20261106T143144Z in /efi/EFI/UpdateCapsule

  Next: reboot when you are ready. cage does not reboot for you.
  The firmware applies the update during that boot. It takes about 11 minutes, the screen may stay dark,
  and the machine may restart on its own more than once. Do not power it off.
  Then run `cage firmware result`. To take the update back before rebooting: `cage firmware cancel`.
```

`--dry-run` does all of it, downloads included, and stages nothing. The reboot is yours: cage never reboots the machine.

## After the reboot

`cage firmware result`, or plain `cage firmware`, says what the reboot did:

```
$ doas cage firmware result
firmware update 20261106T143144Z (staged in slot @nerv):
  USB-PD  updated 0.0.1 -> 0.5.22
  Secure Boot keys unchanged (Secure Boot off).
  TPM unchanged (same storage root key).
```

When something was reset, the report says so and what to do:

- **Secure Boot keys reset.** In firmware setup, choose *Reset to Setup Mode* (or *Delete all keys*) under Secure Boot, boot, run `doas nerv-install secureboot --enrol --yes`, and turn Secure Boot on again. The staged keys also appear in the boot menu while the firmware is in setup mode.
- **TPM reset.** The disk asked for its recovery key at that boot. Seal it to the TPM again with `doas cage escrow rotate --ask --tpm`.

A component the firmware refused says why, in the firmware's own terms: a wrong version, a failed signature check, a lost power supply.

## Taking it back

Before the reboot, `cage firmware cancel` removes the staged update and tells the firmware not to look for one.

## Where updates come from

Releases come from LVFS, the Linux Vendor Firmware Service, where vendors publish them. cage believes LVFS's list of releases only once its signature checks against the LVFS certificate built into cage; each download must match the checksum in that signed list, and so must the update inside it. The update itself is signed by its vendor, and the firmware checks that signature before it applies anything.
