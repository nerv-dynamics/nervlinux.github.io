# Networking

Getting on the network and letting others reach you: wired and Wi-Fi, names, the ConnectX ports, WireGuard, the firewall and SSH.

## How the machine is configured

One system configures every link: `systemd-networkd`, from `.network` files. iwd joins Wi-Fi networks and does nothing else, `systemd-resolved` answers names, and nftables is the firewall. Nerv's own files are in `/usr/lib/systemd/network/`; yours go in `/etc/systemd/network/`, where a file of the same name replaces Nerv's, and an update keeps them.

```
$ networkctl
$ networkctl status enP7s7
```

## Wired

A cable is enough: every Ethernet port asks for an address over DHCP as soon as it has a link. Wired is preferred over Wi-Fi when both are up.

The machine takes no global IPv6 address of its own accord. It keeps an IPv6 link-local address on every port, which is what netboot and the machine's own fabric use, but it ignores router advertisements, so a network whose IPv6 route goes nowhere cannot make every connection wait for a timeout first. To take IPv6 from your router, replace Nerv's file with your own copy that accepts them:

```
$ doas cp /usr/lib/systemd/network/90-nerv-wired.network /etc/systemd/network/
$ doas sed -i 's/^IPv6AcceptRA=no/IPv6AcceptRA=yes/' /etc/systemd/network/90-nerv-wired.network
$ doas networkctl reload
```

A fixed address is a file of your own, named to sort before Nerv's so it is the one that matches:

```
$ cat /etc/systemd/network/10-office.network
[Match]
Name=enP7s7

[Network]
Address=192.168.1.20/24
Gateway=192.168.1.1
DNS=192.168.1.1
$ doas networkctl reload
```

## Wi-Fi

`iwctl` is iwd's own tool. Find the networks in range and join one; iwd asks for the passphrase and remembers it:

```
$ iwctl station wlan0 scan
$ iwctl station wlan0 get-networks
$ iwctl station wlan0 connect "Office"
```

From then on the machine joins that network by itself whenever it is in range. `iwctl known-networks list` shows what it remembers, and `iwctl known-networks "Office" forget` removes one. The address and the name servers come from `systemd-networkd`, as on a cable.

## Names

Every program asks `systemd-resolved`, which caches answers and uses the name servers each network offers. A network that offers none falls back to public resolvers, so names work out of the box. `resolvectl` shows what the machine uses and asks the way a program would:

```
$ resolvectl status
$ resolvectl query nervlinux.org
```

`dns`, `resolve` and `recurse`, from `nerv-hickory-dns`, go around the system resolver, which makes them the tools for asking one server directly or walking a name down from the root, and the wrong ones for asking what a program will see.

## The ConnectX ports

The GB10's ConnectX ports are the fabric between machines: the GPU of one machine reaching another's, and memory written from one to the other over RDMA. They are configured for it out of the box, with jumbo frames so RDMA can use its full packet size, link-local addresses derived from each port's hardware address, which RDMA needs to find its peer, and a DHCP address if the network offers one. A cable between two machines' ports is all the setup there is.

They come up a moment after the login screen does, so an unplugged fabric cable never holds up boot.

## WireGuard

The kernel's WireGuard is configured through `systemd-networkd` like any other link, with a `.netdev` file for the interface and a `.network` file for its address. `wg` sets and shows keys and peers; there is no `wg-quick`.

```
$ wg genkey | doas tee /etc/systemd/network/wg1.key | wg pubkey
$ doas chown root:systemd-network /etc/systemd/network/wg1.key
$ doas chmod 640 /etc/systemd/network/wg1.key
```

```
$ cat /etc/systemd/network/50-wg1.netdev
[NetDev]
Name=wg1
Kind=wireguard

[WireGuard]
PrivateKeyFile=/etc/systemd/network/wg1.key
ListenPort=51820

[WireGuardPeer]
PublicKey=<the other end's public key>
Endpoint=vpn.example.org:51820
AllowedIPs=10.8.0.0/24
$ cat /etc/systemd/network/50-wg1.network
[Match]
Name=wg1

[Network]
Address=10.8.0.2/24
$ doas networkctl reload
$ doas wg show wg1
```

Plexus drives a WireGuard interface of its own, `wg0`, to reach the other machines in your fleet; leave that one to it.

## The firewall

Nothing reaches the machine that it did not ask for. Replies to its own connections come back, ping and the IPv6 housekeeping work, and every other incoming packet is dropped. Outgoing traffic is not filtered, and the machine forwards nothing.

A port opens with the package that listens on it: installing `nerv-ssh` opens 22, and removing it closes 22 again. To open a port of your own, add a rule to the `services` chain in a file under `/etc/nerv-firewall.d/` and reload:

```
$ cat /etc/nerv-firewall.d/web.nft
add rule inet nerv services tcp dport 8080 accept
$ doas systemctl reload nerv-firewall
```

Open it to one network only by naming it in the rule:

```
add rule inet nerv services ip saddr 192.168.1.0/24 tcp dport 8080 accept
```

Your files are loaded after the packages' and an update keeps them. The firewall is the `inet nerv` table and nothing else, so a container runtime or a VPN can add tables of its own beside it; `doas nft list table inet nerv` shows what is open.

## Logging in over SSH

`sshd` runs on port 22, and the firewall lets it through. Log in with a key:

```
$ ssh-copy-id you@192.168.1.20
$ ssh you@192.168.1.20
```

`root` cannot log in over SSH; log in as yourself and use `doas`. A password works too, and five wrong ones in a row lock the account for fifteen minutes, but a key is what to use. Port forwarding, agent forwarding and X11 forwarding are off, so a service on the machine is reached through a port opened in the firewall rather than a tunnel through SSH.

Your own settings go in `/etc/ssh/sshd_config.d/`, which `sshd` reads first, so a setting there wins over Nerv's:

```
$ cat /etc/ssh/sshd_config.d/10-keys-only.conf
PasswordAuthentication no
$ doas systemctl reload sshd
```
