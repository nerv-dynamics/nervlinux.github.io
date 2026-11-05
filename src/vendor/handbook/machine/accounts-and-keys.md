# Accounts and keys

The people on a machine and how each proves who they are: accounts, the groups that grant the GPU, the desktop and root, security keys, the passwords you keep, and the disk's passphrase.

## Your account

The installer makes one account: yours, with `fish` as its shell, in the groups `wheel`, `seat` and `video`, and with the SSH keys you gave it in `~/.ssh/authorized_keys`. That is everything an operator needs: [becoming root](the-first-hour.md#becoming-root), a desktop, and the GPU.

## Adding a person

```
$ doas useradd --create-home --shell /usr/bin/fish --groups seat,video ada
$ doas passwd ada
```

A password needs at least twelve characters, with a digit, a capital, a small letter and something else among them, and it expires after a year. Five wrong passwords in a row lock the account for fifteen minutes.

Give a person only the groups they need, from the table below. Leave `wheel` to the people who run the machine.

To remove someone, and their home with them:

```
$ doas userdel --remove ada
```

## Groups

| group | grants |
| --- | --- |
| `wheel` | `doas`, and reading the whole journal |
| `seat` | starting a desktop session |
| `video` | the GPU, through the compute fabric |

```
$ doas usermod -aG video ada
```

A group takes effect at the next login. Nothing else is needed for a desktop: the seat manager opens the input and graphics devices and hands them to the session, so `input` and `render` are never granted. Never add a person to the `axon` group, which belongs to the GPU service itself and would let a program go around it. [Who may use the GPU](compute-fabric.md#who-may-use-the-gpu) has the rest.

## Security keys

A FIDO2 security key can stand in for your password when you become root. Register it once, touching it when it blinks:

```
$ mkdir -p ~/.config/Yubico
$ pamu2fcfg >> ~/.config/Yubico/u2f_keys
```

From then on, `doas` asks for a touch, or a fingerprint on a key that reads one, and falls back to your password when the key is not there. As installed, `doas` asks for neither, since your account is in `wheel`; the key comes into use once you [require a password for `doas`](the-first-hour.md#becoming-root).

For SSH, make a key that lives on the security key, so logging in needs the key in your hand:

```
$ ssh-keygen -t ed25519-sk
$ ssh-copy-id -i ~/.ssh/id_ed25519_sk.pub you@192.168.1.20
```

Logging in at the console or the greeter uses your password.

## Passwords you keep

`pass-cli` is Proton Pass on the command line: your vaults and their items, one-time codes, secrets written into a file or a program's environment, and an SSH agent that serves the keys you keep there.

```
$ doas dnf install nerv-pass-cli
$ pass-cli login
```

To use its SSH agent, start it once; every new shell then uses it, unless another agent is already answering:

```
$ systemctl --user enable --now pass-cli-ssh-agent.service
```

## The disk passphrase

The disk is unlocked by the TPM at every boot, and asks for its passphrase only when the TPM refuses. The installer made that passphrase and showed it to you once. What to do when it is needed is in [Recovery](recovery.md#a-forgotten-passphrase), with the fleet recovery key that stands behind it.

To replace the passphrase with one of your own, find the encrypted partition and change it there; `cryptsetup` asks for the current passphrase first:

```
$ lsblk -o NAME,FSTYPE | grep crypto_LUKS
$ doas cryptsetup luksChangeKey /dev/nvme0n1p2
```

`doas cryptsetup luksAddKey /dev/nvme0n1p2` adds a second passphrase beside the first, for a second person who may need to unlock the machine. Neither touches the TPM's own way in.
