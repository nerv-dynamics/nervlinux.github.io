#!/usr/bin/env python3
"""Pull the things this site does not own from the nerv-linux tree.

    python3 sync.py                      # ../nerv-linux
    python3 sync.py ~/src/nerv-linux     # somewhere else

Two kinds of thing come across, and the reason is the same for both: the site
must not be a second copy of something the OS already decides.

  myelin.css    Myelin, the OS colour scheme, as nerv-theme exports it. The
                site generates css/palette.css from this (see build.py) rather
                than keeping a hand-written copy of any value.

  handbook/     The published manual. Its chapters are written in the OS tree,
                next to the thing they describe, and rendered here.

  install.sh    The bootstrap behind `curl https://nervlinux.org/install.sh | sh`,
                from src/nerv-install/install.sh. One line differs: the host it
                fetches the installer from, which here is the public mirror. It
                lands at the site root, not in src/vendor/, because it is served
                as it is. Everything it fetches is verified against the key in
                the script, so the mirror is plain http on purpose: the installer
                speaks nothing else.

The copies land in src/vendor/ and are committed, so a clone of this repository
still builds with nothing beside it. Re-run this when the upstream changes; the
diff is the review.
"""

import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).parent
VENDOR = ROOT / "src" / "vendor"

# (source path in nerv-linux, destination in src/vendor/)
FILES = [
    ("packages/nerv-theme/files/myelin.css", "myelin.css"),
]
TREES = [
    ("handbook", "handbook"),
]

INSTALL_SH = "src/nerv-install/install.sh"
# The one line nerv-repo rewrites when it publishes the script to a host; here, to the mirror.
MIRROR = "http://repo.nervlinux.org"


def sync_install_sh(src):
    lines = (src / INSTALL_SH).read_text().splitlines(keepends=True)
    hits = [i for i, l in enumerate(lines) if l.startswith('BASE="${NERV_BASE:-')]
    if len(hits) != 1:
        sys.exit(f"{INSTALL_SH}: expected one BASE= line, found {len(hits)}; "
                 "the script changed shape, so look before publishing it")
    lines[hits[0]] = f'BASE="${{NERV_BASE:-{MIRROR}}}"\n'
    (ROOT / "install.sh").write_text("".join(lines))
    print(f"  {INSTALL_SH:48} -> install.sh (BASE={MIRROR})")


def main():
    src = pathlib.Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else ROOT.parent / "nerv-linux"
    src = src.resolve()
    if not (src / "packages").is_dir():
        sys.exit(f"{src} does not look like a nerv-linux tree")

    VENDOR.mkdir(parents=True, exist_ok=True)
    print(f"from {src}")

    for rel, dest in FILES:
        origin = src / rel
        if not origin.is_file():
            sys.exit(f"missing: {rel}")
        shutil.copy2(origin, VENDOR / dest)
        print(f"  {rel:48} -> src/vendor/{dest}")

    for rel, dest in TREES:
        origin = src / rel
        if not origin.is_dir():
            sys.exit(f"missing: {rel}/")
        target = VENDOR / dest
        if target.exists():
            shutil.rmtree(target)
        # Only the prose. Anything else in that tree is not ours to publish.
        shutil.copytree(origin, target, ignore=shutil.ignore_patterns(
            "*.py", "*.sh", ".*", "__pycache__"))
        n = len(list(target.rglob("*.md")))
        print(f"  {rel + '/':48} -> src/vendor/{dest}/ ({n} markdown files)")

    sync_install_sh(src)

    print("\nsynced. `git diff src/vendor/` is the review; then python3 build.py")


if __name__ == "__main__":
    main()
