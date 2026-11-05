# Containers

Running containers with podman, as yourself and without root: what every container gets by default, Nerv's two base images and how they arrive, building on them, time zones in a container, running a container as a service, tools that expect Docker, which registries a machine pulls from and how to allow one, Fedora's images, and the GPU inside a container.

## Rootless podman

`podman` runs containers as the user who asks, with no daemon and no root. The `nerv-containers` profile installs it with its runtime, its networking and Nerv's base images, and `nerv-dev` includes it.

Every container gets its own block of your subordinate IDs for as long as it runs. Root inside a container is an ID that owns nothing on the machine, and no two containers share one:

```
$ podman run -d --name one nerv-minimal sleep 30
48f1bc99e4a51e300f942c0c9b503b5b2fd74020c4c6e24cf0d5e80f4f8c6ff3
$ podman run -d --name two nerv-minimal sleep 30
d4bdda8686741a811162267b2337268022b0856560a43e32f2eb724baff3ec0d
$ podman top one user huser args
USER        HUSER       COMMAND
root        50431648    sleep 30
$ podman top two user huser args
USER        HUSER       COMMAND
root        50497181    sleep 30
```

No process in a container gains privileges it did not start with: a setuid program inside runs as its caller.

```
$ podman run --rm nerv-minimal grep NoNewPrivs /proc/self/status
NoNewPrivs:	1
```

## Nerv's images

Two base images ship with the `nerv-container-images` package, built from the same packages the machine installs:

| image | what it holds | runs as |
| --- | --- | --- |
| **nerv-static** | musl's C library and loader, libunwind, the CA certificates, os-release, and accounts for root, nobody and nonroot. No shell, no package manager and no time zones. | `nonroot` (65532) |
| **nerv-minimal** | nerv-static plus `sh`, the coreutils, busybox and `dnf`, so packages install inside it | `root` |

They are in your podman store already. The package loads them for every user at login, for root at boot, and again whenever an update brings new ones; nothing is downloaded from a registry.

```
$ podman images --format 'table {{.Repository}} {{.Tag}} {{.ID}} {{.Size}}'
REPOSITORY              TAG         IMAGE ID      SIZE
localhost/nerv-static   latest      496bab54349b  1.22 MB
localhost/nerv-minimal  latest      16b646f36990  84 MB
```

nerv-minimal is built on nerv-static and shares its first layer, so the two together take nerv-minimal's 84 MB.

## Which version you have

Each image is labelled with the package that shipped it and the packages it is made of:

```
$ podman image inspect --format '{{index .Labels "io.nervlinux.image.rpm"}}' nerv-minimal
nerv-container-images-1.0.0-1.nerv
$ podman image inspect --format '{{index .Labels "io.nervlinux.image.packages"}}' nerv-static
nerv-ca-certificates-2026.07.09-4.nerv.noarch nerv-filesystem-1.0.0-10.nerv.noarch nerv-libcxx-22.1.8-11.nerv.aarch64 nerv-musl-1.2.6-23.nerv.aarch64 nerv-release-44-12.nerv.noarch
```

## Building on nerv-minimal

`FROM nerv-minimal` installs Nerv packages with `dnf`, as on the machine:

```
FROM nerv-minimal
RUN dnf5 -y install nerv-jq && dnf5 clean all
USER nonroot
ENTRYPOINT ["jq"]
```

```
$ podman build -q -t jq .
...
649fcbc0ea6214758ff87e8cb142766657878f1fe96df24c71dd02ee7fc4ec79
$ podman run --rm jq --version
jq-1.8.1
$ podman run --rm --entrypoint id jq
uid=65532(nonroot) gid=65532(nonroot) groups=65532(nonroot)
```

## Building on nerv-static

nerv-static is the base for a single program built on Nerv: a Rust or C binary that needs only the C library and libunwind. Copy it in and run it:

```
FROM nerv-static
COPY rg /usr/bin/rg
ENTRYPOINT ["/usr/bin/rg"]
```

```
$ podman build -q -t rg .
40bd9e35fb384ae3b14d37e00578774b32450936fcec1ad101bd202654c9fdf2
$ podman run --rm rg -n nonroot /etc/passwd
3:nonroot:x:65532:65532:nonroot:/home/nonroot:/usr/sbin/nologin
$ podman run --rm --entrypoint /bin/sh rg
Error: crun: executable file `/bin/sh` not found: No such file or directory: OCI runtime attempted to invoke a command that was not found
```

## Time zones

Neither image carries time zones. A container keeps time in UTC unless `TZ` says otherwise, and a POSIX `TZ` string, which spells out the offset and the daylight-saving rule, needs no files at all:

```
$ podman run --rm nerv-minimal date
Sun Oct 18 22:36:35 UTC 2026
$ podman run --rm -e TZ='CET-1CEST,M3.5.0,M10.5.0/3' nerv-minimal date
Mon Oct 19 00:36:35 CEST 2026
```

A zone named by place, such as `Europe/Stockholm`, is read from `/usr/share/zoneinfo`, and without it the time stays UTC with no error:

```
$ podman run --rm -e TZ=Europe/Stockholm nerv-minimal date
Sun Oct 18 22:36:36 UTC 2026
```

On nerv-minimal, install `nerv-tzdata`, in the Containerfile for an image of your own:

```
FROM nerv-minimal
RUN dnf5 -y install nerv-tzdata && dnf5 clean all
```

```
$ podman run --rm -e TZ=Europe/Stockholm nerv-minimal sh -c 'dnf5 -y -q install nerv-tzdata && date'
...
[3/3] Installing nerv-tzdata-0:2026b-4. 100% |   7.5 KiB/s | 100.0   B |  00m00s
Mon Oct 19 00:35:29 CEST 2026
```

A program on nerv-static brings its zones with it. Go embeds them with `import _ "time/tzdata"` and Python with the `tzdata` package; anything else takes them from a stage that installed `nerv-tzdata`:

```
FROM nerv-minimal AS tz
RUN dnf5 -y install nerv-tzdata

FROM nerv-static
COPY --from=tz /usr/share/zoneinfo /usr/share/zoneinfo
COPY myprogram /usr/bin/myprogram
ENTRYPOINT ["/usr/bin/myprogram"]
```

## Running a container as a service

A container that should keep running is a systemd service, described in a `.container` file in `~/.config/containers/systemd/`. systemd starts it, restarts it when it fails, and keeps its output in the journal. This one serves a directory from your home over HTTP, from an image built on nerv-minimal:

```
FROM nerv-minimal
RUN dnf5 -y install nerv-python3 && dnf5 clean all
USER nonroot
CMD ["python3", "-m", "http.server", "8080", "--directory", "/srv"]
```

`~/.config/containers/systemd/hello-web.container`:

```
[Unit]
Description=A small web server

[Container]
Image=localhost/hello-web
UserNS=keep-id:uid=65532,gid=65532
Volume=%h/hello-web:/srv:ro
PublishPort=127.0.0.1:8080:8080
AutoUpdate=local

[Service]
Restart=on-failure

[Install]
WantedBy=default.target
```

`UserNS=keep-id:uid=65532,gid=65532` runs the container's `nonroot` as you, so it can read the files you mount and nothing else of yours. The service is named after the file:

```
$ podman build -q -t hello-web .
62a06a26b7da8e8b5b32acdd1e1c14e00eeeadb577c903a245d7a0313bdbbb6e
$ systemctl --user daemon-reload
$ systemctl --user start hello-web
$ curl http://127.0.0.1:8080/
hello from a service
$ systemctl --user status hello-web
● hello-web.service - A small web server
     Active: active (running) since Sun 2026-10-18 20:09:26 CEST; 4s ago
$ podman top systemd-hello-web user huser args
USER        HUSER       COMMAND
nonroot     1000        python3 -m http.server 8080 --directory /srv
```

A user's services start when the user logs in. To start them at boot and keep them running after logout, enable lingering once:

```
$ loginctl enable-linger
```

A service for the whole machine is the same file in `/etc/containers/systemd/`, run by root.

### Updating a service

`AutoUpdate=local` restarts the service on a newer image under the same name. Rebuild the image, and `podman auto-update` moves the service onto it:

```
$ podman auto-update
            UNIT               CONTAINER                         IMAGE                POLICY      UPDATED
            hello-web.service  348e30d8d76e (systemd-hello-web)  localhost/hello-web  local       true
```

The machine runs `podman auto-update` daily. A service built `FROM nerv-minimal` or `FROM nerv-static` is rebuilt by you; one that runs `nerv-minimal` or `nerv-static` directly moves to the new image the next day after an update brings one.

## Tools that expect Docker

On `nerv-dev`, `docker` is podman: the same commands, run rootless with the same defaults, against the same images.

```
$ docker run --rm nerv-minimal echo hi
hi
$ docker run --rm nerv-minimal grep NoNewPrivs /proc/self/status
NoNewPrivs:	1
```

### Compose files

A compose file runs with `podman compose`, `docker compose` or `docker-compose`, all three the same podman-compose. Services reach each other by name. Here `web` is a small HTTP server built on nerv-static, as in [Building on nerv-static](#building-on-nerv-static), and `client` fetches from it:

```
services:
  web:
    build: web
  client:
    image: nerv-minimal
    depends_on: [web]
    command: sh -c 'sleep 1 && curl -s http://web:8080/'
```

```
$ docker compose up --abort-on-container-exit --exit-code-from client
...
[client] | hello from web
```

`docker compose down` removes the containers and the network compose made for them.

### The Docker API

A program that talks to the Docker API instead, such as an editor's container tooling, a test framework or a Docker SDK, finds podman's API through `DOCKER_HOST`, which is set for you:

```
$ echo $DOCKER_HOST
unix:///run/user/1000/podman/podman.sock
$ curl -s --unix-socket /run/user/1000/podman/podman.sock http://d/_ping
OK
```

The socket is yours and the containers behind it are your rootless ones, with the same defaults as above. Nothing runs until a client connects: podman starts on the first request and stops again after five seconds without one. Docker's own client runs containers through it unchanged.

## Registries

A machine pulls from Fedora's registries, `registry.fedoraproject.org` and `quay.io/fedora`, trusted as Fedora's packages are, and from no other registry until its operator allows one. A short name is never looked up anywhere:

```
$ podman pull alpine
Error: short-name "alpine" did not resolve to an alias and no unqualified-search registries are defined in ...
$ podman pull docker.io/library/alpine
Trying to pull docker.io/library/alpine:latest...
Error: unable to copy from source docker://alpine:latest: copying system image from manifest list: Source image rejected: Running image docker://alpine:latest is rejected by policy.
```

`FROM python` in a Containerfile fails the same way, and `nerv-static` and `nerv-minimal` always mean the local images. Everything local works: images you built, `podman load`, and `podman pull oci:` from a directory.

### Fedora's images

Fedora's images pull by their full name and run as they do on Fedora:

```
$ podman pull -q registry.fedoraproject.org/fedora-minimal
b4640397816bc2b25c27f488c2d54f3c3c4fc711f9baa54fa9a9bc9e0ff95963
$ podman run --rm registry.fedoraproject.org/fedora-minimal cat /etc/fedora-release
Fedora release 44 (Forty Four)
$ podman pull -q quay.io/fedora/fedora-minimal
b4640397816bc2b25c27f488c2d54f3c3c4fc711f9baa54fa9a9bc9e0ff95963
```

Fedora does not sign its images, so they are accepted as pulled over TLS.

### Allowing another registry

The policy is `/usr/share/containers/policy.json`. Copy it to `/etc/containers/policy.json`, which replaces it, and add the registry under `"docker"`, here Docker Hub:

```
$ doas cp /usr/share/containers/policy.json /etc/containers/policy.json
```

```
        "docker": {
            "": [
                {
                    "type": "reject"
                }
            ],
            "registry.fedoraproject.org": [
                {
                    "type": "insecureAcceptAnything"
                }
            ],
            "quay.io/fedora": [
                {
                    "type": "insecureAcceptAnything"
                }
            ],
            "docker.io": [
                {
                    "type": "insecureAcceptAnything"
                }
            ]
        }
```

Pull by the full name:

```
$ podman pull -q docker.io/library/alpine
33bee74c45f307e3268adc2010c0f55c48e7a6041e12cd12432bb1a46e498e43
$ podman run --rm docker.io/library/alpine cat /etc/alpine-release
3.24.2
```

Docker Hub publishes no signatures podman can verify, so its images are accepted as the registry serves them. A registry that signs its images with a sigstore key is allowed with verification instead, using the key as the requirement:

```
            "registry.example.com": [
                {
                    "type": "sigstoreSigned",
                    "keyPath": "/etc/pki/containers/registry.example.com.pub",
                    "signedIdentity": {"type": "matchRepository"}
                }
            ]
```

with `/etc/containers/registries.d/registry.example.com.yaml` telling podman where the signatures are:

```
docker:
  registry.example.com:
    use-sigstore-attachments: true
```

## Your files in a container

A container sees its own files and nothing of yours. To give it a directory of yours, add `:Z` to the volume, and podman labels that directory as this one container's:

```
$ podman run --rm -v ~/data:/data:Z docker.io/library/alpine ls /data
```

`:z`, lower case, labels it for every container to share instead. Without either, the container is refused the directory. The directory stays yours either way: you read and write it as before. Inside, the container's IDs are its own ([above](#rootless-podman)), so it reads what the directory lets others read.

Each container is kept apart from every other, not only from the machine: two containers started from the same image cannot see each other's files or processes.

## The GPU in a container

`--device nerv.com/gpu=all` gives a container the machine's GPU through the compute fabric, and `--group-add keep-groups` carries your permission to use it inside. A program calls the CUDA driver API as it would on the machine, here in Docker Hub's Python image with Docker Hub allowed:

```
$ podman run --rm --device nerv.com/gpu=all --group-add keep-groups docker.io/library/python:3-slim python3 -c '
import ctypes
cuda = ctypes.CDLL("libcuda.so.1")
name = ctypes.create_string_buffer(64)
print(cuda.cuInit(0), cuda.cuDeviceGetName(name, 64, 0), name.value.decode())'
axon: attached to NVIDIA GB10 (124525 MiB) at unix:/run/axon/sock
0 0 NVIDIA GB10
```

The CUDA runtime and the frameworks built on it work the same way. PyTorch's own CUDA 13 build, installed into the same image, trains on the GPU with cuBLAS and cuDNN:

```
$ podman run --rm --device nerv.com/gpu=all --group-add keep-groups docker.io/library/python:3-slim sh -c '
pip install -q --root-user-action=ignore torch numpy --index-url https://download.pytorch.org/whl/cu130
python3 -c "
import torch
x = torch.randn(4096, 4096, device=\"cuda\")
print(torch.__version__, torch.cuda.get_device_name(0), (x @ x).shape)"'
axon: attached to NVIDIA GB10 (124525 MiB) at unix:/run/axon/sock
2.14.1+cu130 NVIDIA GB10 torch.Size([4096, 4096])
```
