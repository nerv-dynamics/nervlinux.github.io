#!/usr/bin/env python3
"""Assemble the site from src/layout.html + src/pages/*.html.

No dependencies, no toolchain, no lockfile. Run `python3 build.py` and commit
the result; GitHub Pages serves the output directly.

Each page in src/pages/ starts with a metadata comment:

    <!--
    title: Platforms
    desc:  One-line description used for <title> and meta description.
    slug:  platforms          (omit or use "." for the front page)
    nav:   platforms          (which nav item to mark current)
    -->
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"

# Copyright holder shown in the footer. This should be the natural person who
# owns the copyright, or a legal entity if one actually exists — an
# unincorporated trade name cannot hold a copyright.
OWNER = "Robert Luciani"

NAV = [
    ("design",    "/design/",    "Design"),
    ("system",    "/system/",    "System"),
    ("tools",     "/tools/",     "Tools"),
    ("userland",  "/userland/",  "Userland"),
    ("platforms", "/platforms/", "Platforms"),
    ("install",   "/install/",   "Install"),
]


def parse(text):
    """Split a page file into (metadata dict, body html)."""
    m = re.match(r"\s*<!--(.*?)-->\s*(.*)", text, re.S)
    if not m:
        sys.exit("page is missing its metadata comment")
    meta = {}
    for line in m.group(1).strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, m.group(2)


def render_nav(current):
    out = []
    for key, href, label in NAV:
        cur = ' aria-current="page"' if key == current else ""
        out.append(f'<a href="{href}"{cur}>{label}</a>')
    return "\n      ".join(out)


def main():
    layout = (SRC / "layout.html").read_text()
    pages = sorted((SRC / "pages").glob("*.html"))
    if not pages:
        sys.exit("no pages found in src/pages/")

    for page in pages:
        meta, body = parse(page.read_text())
        slug = meta.get("slug", "").strip(" /")

        html = layout
        for key, value in {
            "title": meta.get("title", "Nerv Linux"),
            "desc": meta.get("desc", ""),
            "canonical": "https://nervlinux.org/" + (f"{slug}/" if slug else ""),
            "nav": render_nav(meta.get("nav", "")),
            "owner": OWNER,
            "content": body.rstrip(),
        }.items():
            html = html.replace("{{" + key + "}}", value)

        left = re.findall(r"\{\{(\w+)\}\}", html)
        if left:
            sys.exit(f"{page.name}: unreplaced placeholders {sorted(set(left))}")

        dest = ROOT / "index.html" if not slug else ROOT / slug / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html)
        print(f"  {page.name:20} -> {dest.relative_to(ROOT)}")

    print(f"built {len(pages)} pages")


if __name__ == "__main__":
    main()
