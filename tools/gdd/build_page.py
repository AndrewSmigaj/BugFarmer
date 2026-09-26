#!/usr/bin/env python3
"""Build the GDD review page from docs/gdd/*.md.

The owner answers the design document one section at a time on a private claude.ai page. This script is the
only way that page is made: it reads the section files (docs/gdd/README.md gives the review order), turns each
into structured data — proposals (Keep / Cut / Change) and questions (options + my recommendation) — and writes
one self-contained HTML file from review_page.template.html. The page is then published with the Artifact tool.

    python3 tools/gdd/build_page.py                  # -> tools/gdd/_build/review_page.html
    python3 tools/gdd/build_page.py --out some.html

It fails loudly (exit 1) when a section marked "review" is malformed: a question without options, a
recommendation that names a missing option, a proposal without a title — so a broken page is never published.
The markdown shape it reads is documented at the bottom of docs/gdd/README.md.
"""
import argparse
import base64
import html
import io
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
GDD = ROOT / "docs" / "gdd"
TEMPLATE = pathlib.Path(__file__).with_name("review_page.template.html")
DEFAULT_OUT = pathlib.Path(__file__).with_name("_build") / "review_page.html"
BEETLE = ROOT / "tools/_generated/player/reviews/2026-09-26-art-demo/sprites"

# ------------------------------------------------------------------ markdown (the small subset the GDD uses)

def inline(raw):
    """One run of text -> HTML: `code`, [links](https://…), **bold**, *italic*. Everything else is escaped."""
    held = []

    def hold(fragment):
        held.append(fragment)
        return f"\x00{len(held) - 1}\x00"

    raw = re.sub(r"`([^`]+)`", lambda m: hold("<code>" + html.escape(m.group(1)) + "</code>"), raw)

    def link(m):
        text, url = m.group(1), m.group(2)
        if re.match(r"https?://", url):
            return hold(f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">') + text + hold("</a>")
        return text  # repo-relative links mean nothing on claude.ai: keep the words, drop the link

    raw = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, raw)
    s = html.escape(raw, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?=\S)(.+?)(?<=\S)\*(?![\w*])", r"<em>\1</em>", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: held[int(m.group(1))], s)


def table(rows):
    def cells(row):
        return [c.strip() for c in row.strip().strip("|").split("|")]

    head = cells(rows[0])
    body = rows[2:] if len(rows) > 1 and re.match(r"^\|?\s*:?-", rows[1].strip()) else rows[1:]
    out = ['<div class="tbl"><table><thead><tr>']
    out += [f"<th>{inline(c)}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells(row)) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


LIST_ITEM = re.compile(r"^([-*]|\d+\.)\s+(.*)$")


def blocks(lines):
    """Lines -> HTML blocks: paragraphs, lists (with indented continuation lines), tables, quotes, code."""
    out, para, i = [], [], 0

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(x.strip() for x in para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            flush()
            i += 1
        elif line.startswith("```"):
            flush()
            j, code = i + 1, []
            while j < len(lines) and not lines[j].startswith("```"):
                code.append(lines[j])
                j += 1
            out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
            i = j + 1
        elif line.lstrip().startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(table(rows))
        elif LIST_ITEM.match(line):
            flush()
            ordered = LIST_ITEM.match(line).group(1)[0].isdigit()
            items = []
            while i < len(lines):
                m = LIST_ITEM.match(lines[i])
                if m:
                    items.append([m.group(2)])
                elif items and lines[i].startswith("  ") and lines[i].strip():
                    items[-1].append(lines[i].strip())
                else:
                    break
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join("<li>" + inline(" ".join(it)) + "</li>" for it in items) + f"</{tag}>")
        elif line.startswith(">"):
            flush()
            quote = []
            while i < len(lines) and lines[i].startswith(">"):
                quote.append(lines[i][1:].strip())
                i += 1
            out.append("<blockquote>" + inline(" ".join(quote)) + "</blockquote>")
        else:
            para.append(line)
            i += 1
    flush()
    return "\n".join(out)


def plain(md):
    """Markdown -> plain text (for titles stored alongside answers)."""
    return re.sub(r"[*`]", "", md).strip()

# ------------------------------------------------------------------ section files

class Malformed(Exception):
    pass


def split_h3(lines):
    items, cur = [], None
    for line in lines:
        if line.startswith("### "):
            cur = {"head": line[4:].strip(), "lines": []}
            items.append(cur)
        elif cur is not None:
            cur["lines"].append(line)
    return items


def parse_proposal(item, where):
    m = re.match(r"^(P\d+)\.\s+(.+)$", item["head"])
    if not m:
        raise Malformed(f"{where}: proposal heading must read '### P<n>. Title' — got {item['head']!r}")
    lines = item["lines"]
    k = next((i for i, l in enumerate(lines) if l.startswith("**Lenses:**")), None)
    body, lens = (lines[:k], lines[k:]) if k is not None else (lines, [])
    lens_text = re.sub(r"^\*\*Lenses:\*\*\s*", "", " ".join(x.strip() for x in lens if x.strip()))
    return {"id": m.group(1), "title": inline(m.group(2)), "plain": plain(m.group(2)),
            "html": blocks(body), "lenses": inline(lens_text)}


OPTION = re.compile(r"^- \*\*([A-Z])\.\*\*\s*(.*)$")
RECOMMEND = re.compile(r"^\*\*Recommendation:\s*([A-Z])\.\*\*\s*(.*)$")


def parse_question(item, where):
    m = re.match(r"^(Q\d+)\.\s+(.+)$", item["head"])
    if not m:
        raise Malformed(f"{where}: question heading must read '### Q<n>. Question?' — got {item['head']!r}")
    qid, lines = m.group(1), item["lines"]
    context, options, rec, i = [], [], None, 0
    while i < len(lines):
        line = lines[i]
        mo, mr = OPTION.match(line), RECOMMEND.match(line)
        if mo:
            text = [mo.group(2)]
            i += 1
            while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
                text.append(lines[i].strip())
                i += 1
            options.append({"key": mo.group(1), "html": inline(" ".join(text))})
            continue
        if mr:
            text = [mr.group(2)]
            i += 1
            while i < len(lines) and lines[i].strip():
                text.append(lines[i].strip())
                i += 1
            rec = {"key": mr.group(1), "html": inline(" ".join(text))}
            continue
        if not options:
            context.append(line)
        i += 1
    if len(options) < 2:
        raise Malformed(f"{where} {qid}: a question needs at least two '- **A.** …' options")
    if rec and rec["key"] not in {o["key"] for o in options}:
        raise Malformed(f"{where} {qid}: the recommendation names option {rec['key']}, which doesn't exist")
    return {"id": qid, "title": inline(m.group(2)), "plain": plain(m.group(2)),
            "context": blocks(context), "options": options, "rec": rec}


REFERENCE_PARTS = ["Current design", "As built", "How it will work"]


def parse_section(path):
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    meta_m = re.search(r"<!--\s*gdd:(.*?)-->", text)
    if not lines[0].startswith("# ") or not meta_m:
        raise Malformed(f"{path.name}: needs a '# §NN · Title' first line and a '<!-- gdd: … -->' line")
    meta = dict(re.findall(r"(\w+)=([\w\-]+)", meta_m.group(1)))
    title = re.sub(r"^§\s*\d+\s*·\s*", "", lines[0][2:].strip())
    parts, order, cur, lead = {}, [], None, []
    for line in lines[1:]:
        if line.startswith("<!--"):
            continue
        if line.startswith("## "):
            cur = line[3:].strip()
            order.append(cur)
            parts[cur] = []
        elif cur is None:
            lead.append(line)
        else:
            parts[cur].append(line)

    def part(name):
        return parts.get(name, [])

    section = {
        "id": meta.get("id"), "status": meta.get("status", "draft"), "updated": meta.get("updated", ""),
        "title": title, "file": f"docs/gdd/{path.name}",
        "lead": blocks(lead),
        "experience": blocks(part("The experience")),
        "decided": blocks(part("Decided")),
        "reference": [{"title": n, "html": blocks(part(n))} for n in REFERENCE_PARTS if part(n)],
        "proposals": [parse_proposal(it, path.name) for it in split_h3(part("Proposals"))],
        "questions": [parse_question(it, path.name) for it in split_h3(part("Questions"))],
        "sources": blocks(part("Sources")),
        "settle": blocks(next((parts[n] for n in order if n.startswith("To settle")), [])),
        "gather": blocks(part("Sources to gather")),
    }
    if section["status"] in ("review", "final") and not (section["proposals"] or section["questions"]):
        raise Malformed(f"{path.name}: status {section['status']} but no proposals or questions")
    return section


def review_order():
    """The order table in docs/gdd/README.md: | order | § | section | status | [file](file) |"""
    order = []
    for line in (GDD / "README.md").read_text(encoding="utf-8").split("\n"):
        m = re.match(r"^\|\s*(\d+)\s*\|\s*(\d{2})\s*\|.*\((\w+\.md)\)\s*\|\s*$", line)
        if m:
            order.append((int(m.group(1)), m.group(3)))
    return [name for _, name in sorted(order)]

# ------------------------------------------------------------------ page

def beetle_strip():
    """The code-drawn burying beetle's 6 walk frames as one sprite strip (data URI) for the page header."""
    frames = sorted(BEETLE.glob("beetle_walk_*.png"))
    if len(frames) != 6:
        return ""
    from PIL import Image
    strip = Image.new("RGBA", (32 * 6, 32), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        strip.paste(Image.open(f).convert("RGBA"), (32 * i, 0))
    buf = io.BytesIO()
    strip.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    try:
        names = review_order()
        if not names:
            raise Malformed("README.md: no section table found")
        sections = [parse_section(GDD / n) for n in names]
    except Malformed as e:
        print(f"GDD page NOT built — {e}", file=sys.stderr)
        return 1
    stamp = max((s["updated"] for s in sections if s["updated"]), default="")
    data = {"version": stamp, "sections": sections}
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = TEMPLATE.read_text(encoding="utf-8")
    page = page.replace("/*GDD_DATA*/", payload).replace("{{BEETLE}}", beetle_strip())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page, encoding="utf-8")
    ready = [s["id"] for s in sections if s["status"] == "review"]
    counts = {s["id"]: (len(s["proposals"]), len(s["questions"])) for s in sections if s["status"] == "review"}
    print(f"GDD page built: {args.out} ({len(page) // 1024} KB) · {len(sections)} sections · ready for review: "
          + ", ".join(f"§{i} ({counts[i][0]} proposals, {counts[i][1]} questions)" for i in ready))
    return 0


if __name__ == "__main__":
    sys.exit(main())
