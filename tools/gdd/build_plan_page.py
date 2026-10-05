#!/usr/bin/env python3
"""Render the active plan, docs/plans/village-slice.md, as one readable page for publishing privately to claude.ai.

The owner can't read a long plan in the terminal (2026-10-04), so the plan is published as a page and republished at
the end of each stage (the plan's "How we stay on track"). Reuses the GDD builder's inline and table rendering
(build_page.py) and adds what the plan needs on top: nested lists, # / ## / ### headings with anchors, a contents list.

    python3 tools/gdd/build_plan_page.py        # -> tools/gdd/_build/village-slice.html (git-ignored)

Then publish that file with the Artifact tool, passing the page's address (in the plan's Stage 0, step 3) as url.
"""
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/gdd"))
import build_page as bp  # noqa: E402

SRC = ROOT / "docs/plans/village-slice.md"
OUT = ROOT / "tools/gdd/_build/village-slice.html"
ITEM = re.compile(r"^( *)([-*]|\d+\.)\s+(.*)$")


def slug(text, used):
    s = re.sub(r"[^a-z0-9]+", "-", bp.plain(text).lower()).strip("-")[:48] or "s"
    base, n = s, 2
    while s in used:
        s, n = f"{base}-{n}", n + 1
    used.add(s)
    return s


def render_list(lines, i):
    """Parse a (possibly nested) list starting at lines[i]; return (html, next index)."""
    first = ITEM.match(lines[i])
    indent = len(first.group(1))
    ordered = first.group(2)[0].isdigit()
    items = []  # each: [text parts], [child html]
    while i < len(lines):
        line = lines[i]
        m = ITEM.match(line)
        if not line.strip():
            # a blank line ends the list unless the next line continues it at this or a deeper level
            j = i + 1
            if j < len(lines) and (ITEM.match(lines[j]) and len(ITEM.match(lines[j]).group(1)) >= indent):
                i = j
                continue
            break
        if m and len(m.group(1)) == indent:
            items.append([[m.group(3)], []])
            i += 1
        elif m and len(m.group(1)) > indent and items:
            sub, i = render_list(lines, i)
            items[-1][1].append(sub)
        elif not m and items and line.startswith(" " * (indent + 1)):
            if line.lstrip().startswith("|"):  # a table inside a list item
                rows = []
                while i < len(lines) and lines[i].lstrip().startswith("|"):
                    rows.append(lines[i].strip())
                    i += 1
                items[-1][1].append(bp.table(rows))
            else:
                if items[-1][1]:  # text after a sub-list: its own paragraph inside the item
                    items[-1][1].append("<p>" + bp.inline(line.strip()) + "</p>")
                else:
                    items[-1][0].append(line.strip())
                i += 1
        else:
            break
    tag = "ol" if ordered else "ul"
    body = "".join("<li>" + bp.inline(" ".join(t)) + "".join(kids) + "</li>" for t, kids in items)
    return f"<{tag}>{body}</{tag}>", i


def render(md):
    lines = md.split("\n")
    out, toc, para, used, i = [], [], [], set(), 0
    title = ""

    def flush():
        if para:
            out.append("<p>" + bp.inline(" ".join(x.strip() for x in para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            flush(); i += 1
        elif line.startswith("# "):
            flush(); title = line[2:].strip(); i += 1
        elif line.startswith("## "):
            flush()
            text = line[3:].strip()
            sid = slug(text, used)
            toc.append((2, text, sid))
            cls = ' class="summary"' if text.startswith("In one screen") else ''
            out.append(f'</section><section id="{sid}"{cls}><h2>{bp.inline(text)}</h2>')
            i += 1
        elif line.startswith("### "):
            flush()
            text = line[4:].strip()
            sid = slug(text, used)
            toc.append((3, text, sid))
            out.append(f'<h3 id="{sid}">{bp.inline(text)}</h3>')
            i += 1
        elif line.startswith("```"):
            flush()
            j, code = i + 1, []
            while j < len(lines) and not lines[j].startswith("```"):
                code.append(lines[j]); j += 1
            out.append('<div class="code"><pre><code>' + html.escape("\n".join(code)) + "</code></pre></div>")
            i = j + 1
        elif line.lstrip().startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(lines[i]); i += 1
            out.append(bp.table(rows))
        elif ITEM.match(line):
            flush()
            h, i = render_list(lines, i)
            out.append(h)
        elif line.startswith(">"):
            flush()
            q = []
            while i < len(lines) and lines[i].startswith(">"):
                q.append(lines[i][1:].strip()); i += 1
            out.append("<blockquote>" + bp.inline(" ".join(q)) + "</blockquote>")
        else:
            para.append(line); i += 1
    flush()
    body = "\n".join(out)
    return title, toc, body + "</section>"


def main():
    title, toc, body = render(SRC.read_text(encoding="utf-8"))
    toc_html = "".join(
        f'<li class="l{lvl}"><a href="#{sid}">{bp.inline(t)}</a></li>' for lvl, t, sid in toc)
    page = TEMPLATE.replace("%%TITLE%%", bp.inline(title)).replace("%%TOC%%", toc_html).replace("%%BODY%%", body)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT} ({len(page)//1024} KB, {len(toc)} headings)")


TEMPLATE = r"""<title>Village Slice Plan</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: a contents rail beside one readable column; the one-screen summary is lifted as the only boxed block. */
:root {
  --bg: #f4f6f3; --panel: #ffffff; --ink: #1d2621; --muted: #5c6a62; --line: #d5ddd7;
  --accent: #2d6a5c; --accent-soft: #e2efe9; --code-bg: #eaefeb;
  --body: "Atkinson Hyperlegible", "Segoe UI", system-ui, sans-serif;
  --mono: "JetBrains Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #121815; --panel: #19211d; --ink: #e2e9e4; --muted: #98a79e; --line: #2c3832;
  --accent: #79bfae; --accent-soft: #1f3330; --code-bg: #202a25; color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #121815; --panel: #19211d; --ink: #e2e9e4; --muted: #98a79e; --line: #2c3832;
  --accent: #79bfae; --accent-soft: #1f3330; --code-bg: #202a25; color-scheme: dark; }
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font: 16px/1.6 var(--body); margin: 0; padding-inline: 16px; }
.wrap { max-width: 1180px; margin: 0 auto; padding-block: 28px 64px; display: grid; grid-template-columns: 250px minmax(0, 1fr); gap: 40px; }
nav { position: sticky; top: calc(env(safe-area-inset-top, 0px) + 16px); align-self: start; max-height: calc(100vh - 32px); overflow: auto; font-size: 13.5px; }
nav summary { margin: 0 0 8px; color: var(--muted); text-transform: uppercase; letter-spacing: .08em; font-size: 12px; cursor: pointer; }
nav ul { list-style: none; margin: 0; padding: 0; }
nav li { margin: 0; }
nav li.l3 { padding-left: 14px; font-size: 12.5px; }
nav a { display: block; padding: 3px 8px; border-radius: 4px; color: var(--muted); text-decoration: none; line-height: 1.35; }
nav a:hover, nav a:focus-visible { background: var(--accent-soft); color: var(--ink); outline: none; }
main { min-width: 0; max-width: 78ch; }
h1 { font-size: 30px; line-height: 1.2; margin: 0 0 14px; text-wrap: balance; }
h2 { font-size: 22px; line-height: 1.3; margin: 40px 0 10px; padding-top: 14px; border-top: 1px solid var(--line); text-wrap: balance; }
h3 { font-size: 18px; margin: 28px 0 8px; color: var(--accent); text-wrap: balance; }
p { margin: 0 0 12px; }
ul, ol { margin: 0 0 12px; padding-left: 22px; }
li { margin: 3px 0; }
li > ul, li > ol { margin: 4px 0 6px; }
strong { font-weight: 700; }
a { color: var(--accent); }
code { font-family: var(--mono); font-size: .86em; background: var(--code-bg); padding: 1px 4px; border-radius: 3px; overflow-wrap: anywhere; }
blockquote { margin: 0 0 16px; padding: 10px 14px; border-left: 3px solid var(--accent); background: var(--panel); color: var(--muted); }
.tbl { overflow-x: auto; margin: 0 0 16px; border: 1px solid var(--line); border-radius: 6px; background: var(--panel); }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th, td { text-align: left; vertical-align: top; padding: 7px 10px; border-bottom: 1px solid var(--line); }
th { background: var(--accent-soft); font-weight: 700; }
tr:last-child td { border-bottom: 0; }
td:nth-child(2) { font-variant-numeric: tabular-nums; }
.code pre { overflow-x: auto; background: var(--code-bg); padding: 12px; border-radius: 6px; }
section.summary { background: var(--panel); border: 1px solid var(--line); border-left: 4px solid var(--accent); border-radius: 8px; padding: 4px 22px 10px; margin-top: 22px; }
section.summary h2 { border-top: 0; margin-top: 12px; }
.note { color: var(--muted); font-size: 13px; margin-bottom: 18px; }
@media (max-width: 860px) {
  .wrap { grid-template-columns: minmax(0, 1fr); gap: 12px; }
  nav { position: static; max-height: none; border: 1px solid var(--line); border-radius: 8px; padding: 10px; background: var(--panel); }
}
@media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth; } }
</style>
<div class="wrap">
<nav aria-label="Contents"><details id="toc" open><summary>Contents</summary><ul>%%TOC%%</ul></details></nav>
<main>
<h1>%%TITLE%%</h1>
<p class="note">The repo copy is <code>docs/plans/village-slice.md</code>; this page is rebuilt from it. Start with the one-screen summary; everything after it is the working detail.</p>
<section>
%%BODY%%
</main>
</div>
<script>
try { if (matchMedia("(max-width: 860px)").matches) document.getElementById("toc").open = false; } catch (e) {}
</script>
"""

if __name__ == "__main__":
    main()
