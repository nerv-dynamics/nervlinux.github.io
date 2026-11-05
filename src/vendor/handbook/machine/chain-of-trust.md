# The chain of trust

What is verified between power-on and a prompt, what holds the machine to its rules once it is up, and precisely what all of that does not defend against.

## From power-on to a prompt

| step | what is checked | by |
| --- | --- | --- |
| the boot loader | its signature, against the machine's own Secure Boot keys | the firmware |
| the slot's boot image | its signature, which covers the kernel, the initrd and the kernel command line together | the firmware |
| the disk | that the image booting is one this machine's key signed a policy for | the TPM |
| the system | every module the kernel loads is signed | the kernel |

The boot loader shows no menu unless asked, and its command line cannot be edited at boot: the command line is part of the signed image, so a changed one is an unsigned one.

## The signed boot image

Each slot boots one file, a unified kernel image: the kernel, the initrd, the kernel command line and the policy that unlocks the disk, signed as one. The signature is made when the slot is sealed, by `cage update` or `cage seal`, with this machine's own key. `cage seal` refuses to seal a slot it cannot sign.

The keys are the machine's own. At install, Nerv makes a Secure Boot key hierarchy for the machine and enrols it in the firmware, so the firmware's database holds this machine's key and nothing else, Microsoft's included: the machine boots what it signed and nothing else. Secure Boot takes effect once you turn it on in the firmware's setup, as the last step of [Install](install.md). The keys are kept in `/etc/nerv/secureboot`, on the encrypted disk, readable only by root and, within root, only by the programs that sign.

The kernel command line carries the hardening that is always on, memory zeroed on allocation and on free and a randomised kernel stack among it, and it is signed with everything else.

## The disk and the TPM

The disk is LUKS2, encrypted with a key derived by argon2id. Its key is sealed in the TPM against a policy rather than a single image: the TPM unlocks the disk for any boot image whose policy this machine's key signed. An update therefore unlocks the disk as the old system did, with nothing to re-seal, and an image anyone else built does not.

The TPM refuses, and the machine asks for the disk's passphrase instead, when:

- the boot image carries no policy signed by this machine,
- the TPM has been reset or replaced, as a firmware update or a new board can do,
- the system has already booted past the point where the disk is unlocked. A running system cannot ask the TPM for the key again, so a program that takes over the machine later cannot either.

The passphrase is the way in when the TPM is not. [A forgotten passphrase](recovery.md#a-forgotten-passphrase) covers losing it, and the fleet recovery key that stands behind it.

## After the prompt

**SELinux enforces from the first boot, with a policy written for Nerv.** Every process runs in a domain, and there is no unconfined one to fall into. Some rules are promises the policy cannot be changed to break: nothing can switch enforcement off or load a new policy, only the signing programs read the Secure Boot keys, and only the processes that need them reach the password database, the GPU's device nodes and the raw disks.

A service you install, a database or a CI runner, runs in a domain for software Nerv does not ship. It keeps its own files, uses the network and builds what it builds, and it is kept from the machine's keys, the account secrets and the disks. A refusal is logged:

```
$ journalctl -g 'avc: +denied'
```

**The kernel is locked down.** It loads only modules signed by Nerv, root cannot write to kernel memory or replace the running kernel with an unsigned one, and the machine does not hibernate, which would write its memory to the disk. Landlock and Yama are on beside SELinux.

## A trust root of your own

Every machine already holds its own Secure Boot keys and its own TPM policy key, made on the machine at install. To use keys you hold instead, so that one key signs the boot images of every machine you run, give the installer your signing key and certificate with `--sb-key`.

Generations are signed by Nerv, and the installer checks each one against Nerv's key before it serves it. Signing generations with your own key, so that a fleet runs nothing you have not signed, is on the roadmap.

## What this does not defend against

- **The network during installation.** The first network boot runs with Secure Boot off, since the keys it would check against are what it installs, and the installer serves the system to the machine over your local network. Install on a network you trust.
- **Firmware and the TPM themselves.** The chain starts at the firmware. Firmware or a TPM that has been compromised can lie about everything after it.
- **A machine whose Secure Boot is off.** The keys are enrolled at install, but the firmware checks nothing until you turn Secure Boot on.
- **Files on the boot partition outside the boot image.** The GPU's firmware is loaded from the boot partition, which is not encrypted, and the image's signature does not cover it.
- **Someone with your passphrase,** or with the fleet recovery key.
- **Root on a running machine, beyond the policy.** SELinux limits what root's processes can reach, but an operator who is root can install software and change the system, which is what root is for.
- **A mirror that holds back an update.** A mirror cannot forge a generation, since each one is signed, but it can withhold a newer one or offer an older one.
