#!/usr/bin/env python3
"""A markdown renderer for exactly the markdown the handbook is written in.

Imported by build.py. Stdlib only, like everything else here.

WHY NOT A LIBRARY
  The handbook is authored in the OS tree and rendered here, so something has
  to turn it into HTML. A dependency would be the obvious answer, and it was
  rejected for two reasons that are about this site rather than about taste:

    1. The site's whole build is `python3 build.py` with no third-party
       imports, and that property is worth more than the hundred lines below.
    2. A general renderer emits general HTML. This one emits the site's own
       classes — `table.data`, `.term`, `.prose` — so a handbook chapter comes
       out looking like a page of this site rather than like a README that has
       been styled afterwards.

  The corpus was surveyed before this was written. It uses: code spans, bold,
  tables, fenced code, h1-h3, unordered lists, italic, horizontal rules,
  blockquotes and links. No images, no raw HTML, no ordered lists. Anything
  outside that set raises rather than being silently dropped, because a
  chapter that renders wrong is worse than a build that stops.

NOT A GENERAL MARKDOWN IMPLEMENTATION
  Do not reach for this to render arbitrary markdown. It knows one document
  family. If the handbook grows a construct, add it here deliberately and
  extend the survey in docs/handbook.md.
"""

import html
import re

__all__ = ["render", "MarkdownError"]


class MarkdownError(Exception):
    """A construct this renderer does not implement, with a line number."""


# Inline code is pulled out before anything else touches the text, so that
# emphasis and link syntax inside a code span stays literal. `--opt=*` in a
# terminal example must not become `--opt=<em>`.
_SENTINEL = "\x00"


def _inline(text, link):
    spans = []

    def stash(m):
        spans.append(m.group(1))
        return f"{_SENTINEL}{len(spans) - 1}{_SENTINEL}"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text, quote=False)

    def anchor(m):
        label, href = m.group(1), m.group(2)
        target = link(href)
        if target is None:
            return label
        return f'<a href="{html.escape(target, quote=True)}">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", anchor, text)
    # <https://example.com> — the handbook's autolink form.
    text = re.sub(r"&lt;(https?://[^&\s]+)&gt;", r'<a href="\1">\1</a>', text)

    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # Single asterisks, but not the inside of a word and not a stray bullet.
    text = re.sub(r"(?<![*\w])\*([^*\s][^*]*?)\*(?![*\w])", r"<em>\1</em>", text)

    def restore(m):
        return f"<code>{html.escape(spans[int(m.group(1))], quote=False)}</code>"

    return re.sub(rf"{_SENTINEL}(\d+){_SENTINEL}", restore, text)


def _slug(text):
    """A heading id, so chapters can be linked into by section."""
    s = re.sub(r"<[^>]+>", "", text).lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    return re.sub(r"\s+", "-", s.strip())[:60]


def _table(rows, link):
    """A markdown table as table.data, which is what the site styles.

    The handbook's contents pages use `| | |` — a table with deliberately
    empty headers, used as a two-column layout rather than as data. Emitting
    a <thead> of blanks there would put an empty ruled row at the top of the
    page, so a table whose headers are all empty is rendered without one.
    """
    head, body = rows[0], rows[2:]
    aligns = []
    for cell in rows[1]:
        cell = cell.strip()
        aligns.append("right" if cell.endswith(":") and not cell.startswith(":")
                      else "center" if cell.startswith(":") and cell.endswith(":")
                      else "left")

    def cells(row, tag):
        out = []
        for i, c in enumerate(row):
            a = aligns[i] if i < len(aligns) else "left"
            style = "" if a == "left" else f' style="text-align:{a}"'
            scope = ' scope="col"' if tag == "th" else ""
            out.append(f"<{tag}{scope}{style}>{_inline(c.strip(), link)}</{tag}>")
        return "".join(out)

    parts = ['<div class="table-scroll">', '<table class="data">']
    if any(c.strip() for c in head):
        parts += ["<thead><tr>", cells(head, "th"), "</tr></thead>"]
    parts.append("<tbody>")
    for row in body:
        parts += ["<tr>", cells(row, "td"), "</tr>"]
    parts += ["</tbody>", "</table>", "</div>"]
    return "\n".join(parts)


def _split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return line.split("|")


# handbook/README.md is both the repository's README and the manual's front
# page, so it carries sentences addressed to authors ("read DISCIPLINE.md
# before adding a chapter") that an operator should never be shown. Wrapping
# those upstream keeps one source file serving both jobs.
_SKIP = re.compile(r"<!--\s*site:skip\s*-->.*?<!--\s*site:endskip\s*-->",
                   re.S | re.I)


def render(text, link=lambda h: h):
    """Markdown -> HTML.

    `link` rewrites an href — .md paths into URLs, say. Returning None means
    "this is not a link here": the label is kept and the anchor dropped. That
    is what a cross-reference to an unpublished chapter has to become, since
    the alternative is a link to a page that does not exist.
    """
    text = _SKIP.sub("", text)
    # Any other comment is an authoring note and is not content either.
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    lines = text.replace("\r\n", "\n").split("\n")
    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # --- fenced code ------------------------------------------------
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            i += 1
            body = []
            while i < n and not lines[i].strip().startswith("```"):
                body.append(lines[i])
                i += 1
            if i >= n:
                raise MarkdownError("unterminated code fence")
            i += 1
            code = html.escape("\n".join(body), quote=False)
            cls = f' data-lang="{html.escape(lang, quote=True)}"' if lang else ""
            # The site already has a terminal component; a fenced block is the
            # same thing without the title bar.
            out.append(f'<pre class="term term__body"{cls}>{code}</pre>')
            continue

        # --- heading ----------------------------------------------------
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            inner = _inline(m.group(2).strip(), link)
            if level == 1:
                out.append(f'<h1 class="page-title">{inner}</h1>')
            else:
                tag = f"h{min(level, 6)}"
                cls = "section-title" if level == 2 else "sub-title"
                out.append(f'<{tag} id="{_slug(inner)}" class="{cls}">{inner}</{tag}>')
            i += 1
            continue

        # --- horizontal rule --------------------------------------------
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            out.append('<hr class="rule">')
            i += 1
            continue

        # --- table ------------------------------------------------------
        if stripped.startswith("|") and i + 1 < n and re.match(
                r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?$", lines[i + 1].strip()):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(_split_row(lines[i]))
                i += 1
            out.append(_table(rows, link))
            continue

        # --- blockquote -------------------------------------------------
        if stripped.startswith(">"):
            body = []
            while i < n and lines[i].strip().startswith(">"):
                body.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            inner = _inline(" ".join(l.strip() for l in body if l.strip()), link)
            # The handbook's sanctioned "Underneath." box is a blockquote whose
            # first run is bold. It is a callout, not a quotation.
            cls = "note" if inner.startswith("<strong>") else "pull"
            out.append(f'<blockquote class="{cls}"><p>{inner}</p></blockquote>')
            continue

        # --- unordered list ---------------------------------------------
        if re.match(r"^\s*[-*+]\s+", line):
            out.append(_list(lines, i, link))
            i = _list_end(lines, i)
            continue

        if re.match(r"^\s*\d+\.\s+", line):
            raise MarkdownError(
                f"line {i + 1}: ordered lists are not implemented — the handbook "
                f"corpus had none. Add support here rather than around it.")

        if re.match(r"^!\[", stripped):
            raise MarkdownError(
                f"line {i + 1}: images are not implemented. Handbook figures "
                f"should be authored as HTML so they carry the site's classes.")

        # --- paragraph ---------------------------------------------------
        body = []
        while i < n and lines[i].strip() and not _starts_block(lines[i], lines, i):
            body.append(lines[i].strip())
            i += 1
        out.append(f"<p>{_inline(' '.join(body), link)}</p>")

    return "\n".join(out)


def _starts_block(line, lines, i):
    s = line.strip()
    return bool(
        s.startswith("```") or s.startswith(">") or s.startswith("|")
        or re.match(r"^#{1,6}\s", s)
        or re.match(r"^(-{3,}|\*{3,}|_{3,})$", s)
        or re.match(r"^\s*[-*+]\s+", line)
        or re.match(r"^\s*\d+\.\s+", line)
    )


def _item_indent(line):
    return len(line) - len(line.lstrip())


def _list_end(lines, start):
    i = start
    while i < len(lines):
        if re.match(r"^\s*[-*+]\s+", lines[i]):
            i += 1
        elif lines[i].strip() and _item_indent(lines[i]) > 0 \
                and not _starts_block(lines[i], lines, i):
            i += 1            # a continuation line of the previous item
        else:
            break
    return i


def _list(lines, start, link):
    """Nested unordered lists, nesting taken from indentation."""
    end = _list_end(lines, start)
    items = []          # (indent, text)
    for line in lines[start:end]:
        m = re.match(r"^(\s*)[-*+]\s+(.*)$", line)
        if m:
            items.append([len(m.group(1)), m.group(2).strip()])
        elif items:
            items[-1][1] += " " + line.strip()

    def build(idx, indent):
        parts = ['<ul class="list">']
        while idx < len(items):
            ind, text = items[idx]
            if ind < indent:
                break
            if ind > indent:
                nested, idx = build(idx, ind)
                # The nested list belongs inside the item that introduced it.
                parts[-1] = parts[-1][:-len("</li>")] + nested + "</li>"
                continue
            parts.append(f"<li>{_inline(text, link)}</li>")
            idx += 1
        parts.append("</ul>")
        return "\n".join(parts), idx

    return build(0, items[0][0])[0]
