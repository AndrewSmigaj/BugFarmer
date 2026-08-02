"""gallery.py — one HTML page showing every outfit as it actually stands. FREE, no API.

  python3 tools/player_sprites/gallery.py

Writes `tools/_generated/player/gallery.html`. Open it by double-clicking from Explorer.

WHY THIS IS HTML WHEN EVERY OTHER PREVIEW IS A PNG FOLDER
---------------------------------------------------------
CLAUDE.md says previews are plain PNG folders, "browse in a file explorer - no html", and
`tools/README.md` records that an earlier `previews/index.html` was deleted as dead code. That rule is
right for static zone renders and wrong here: a file explorer cannot show 22 outfits x 12 ANIMATIONS at
once, and the whole problem this solves is not being able to see what you have. Owner asked for this
explicitly on 2026-08-02. **Do not delete it as dead code.**

GENERATED, NEVER HAND-MAINTAINED
--------------------------------
Nothing below hardcodes an outfit name, an animation name or a count. Every sprite in this project is
going to be recreated; re-run this and the page reflects whatever is on disk at that moment. That is the
only reason it survives the rebuild.

TWO CONSTRAINTS THAT DECIDE THE SHAPE
-------------------------------------
Under `file://` a page cannot list a directory and cannot `fetch()` a local JSON file. So the manifest is
INLINED into the HTML as a <script> block, and the page must be written to `_generated/player/` for the
relative image paths to resolve. Moving it breaks every image.
"""
import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_animations as R                            # noqa: E402

PLAYER = R.PLAYER
OUTFITS = R.OUTFITS
OUT = os.path.join(PLAYER, "gallery.html")

# The four stages an outfit passes through, in order. Each knows how to detect itself so the progress
# board reports where an outfit ACTUALLY is rather than where a list says it should be.
STAGES = ["candidates", "frames", "gauntlets", "official"]


def rel(path):
    """Path relative to the gallery, forward slashes, URL-safe enough for file://."""
    return os.path.relpath(path, PLAYER).replace(os.sep, "/")


def _pngs(d):
    return sorted(f for f in os.listdir(d) if f.lower().endswith(".png")) if os.path.isdir(d) else []


def read_record(d):
    """The prompt/date out of a RECORD.txt, so candidates are captioned by what they ARE."""
    p = os.path.join(d, "RECORD.txt")
    if not os.path.exists(p):
        return {}
    out, prompt = {}, []
    with open(p, encoding="utf-8", errors="replace") as fh:
        body = fh.read()
    head, _, tail = body.partition("PROMPT:")
    for line in head.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            if k.strip() in ("when", "model", "size", "quality"):
                out[k.strip()] = v.strip()
    prompt = " ".join(tail.split())
    if prompt:
        out["prompt"] = prompt[:600]
    return out


def scan_candidates(outfit):
    """Candidate sheets, new structure first, then the places they live today."""
    d = R.outfit_dir(outfit)
    found = []
    new = os.path.join(d, "scratchpad", "1-candidates")
    if os.path.isdir(new):
        for b in sorted(os.listdir(new)):
            bd = os.path.join(new, b)
            for f in _pngs(bd):
                found.append(dict(src=rel(os.path.join(bd, f)), batch=b, **read_record(bd)))
        return found
    # pre-migration: explore/<outfit>/result.png and the outfit's own result.png
    for cand in (os.path.join(PLAYER, "explore", outfit), d):
        p = os.path.join(cand, "result.png")
        if os.path.exists(p):
            found.append(dict(src=rel(p), batch=os.path.basename(cand) + " (pre-migration)",
                              **read_record(cand)))
    return found


def scan_frames(outfit):
    d = R.frames_dir(outfit)
    out = {}
    for kind in ("front", "side", "back"):
        fs = [os.path.join(d, f"{kind}_{i}.png") for i in (1, 2, 3)]
        fs = [f for f in fs if os.path.exists(f)]
        if fs:
            out[kind] = [rel(f) for f in fs]
    return out


def scan_gauntlet(outfit):
    g, prov = R.gauntlet_dir(outfit)
    if g is None:
        return {}, prov
    return {os.path.splitext(f)[0]: rel(os.path.join(g, f))
            for f in _pngs(g) if os.path.splitext(f)[0] in ("front", "back", "side", "grip")}, prov


def scan_anims(outfit):
    d = R.anim_dir(outfit)
    if not os.path.isdir(d):
        return {}
    return {os.path.splitext(f)[0]: rel(os.path.join(d, f))
            for f in sorted(os.listdir(d)) if f.lower().endswith(".gif")}


def read_ledger(outfit):
    p = os.path.join(R.outfit_dir(outfit), "current", "CURRENT.md")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def scan(outfit):
    cands = scan_candidates(outfit)
    frames = scan_frames(outfit)
    gaunt, gprov = scan_gauntlet(outfit)
    anims = scan_anims(outfit)
    ledger = read_ledger(outfit)
    stages = {
        "candidates": len(cands),
        "frames": sum(len(v) for v in frames.values()),
        "gauntlets": len(gaunt),
        "official": 1 if ledger else 0,
    }
    return dict(name=outfit, candidates=cands, frames=frames, gauntlet=gaunt,
                gauntlet_source=gprov, anims=anims, ledger=ledger, stages=stages)


def build():
    outfits = [scan(o) for o in R.all_outfits()]
    anim_names = sorted({k for o in outfits for k in o["anims"]},
                        key=lambda n: (not n.startswith("walk"), not n.startswith("run"), n))
    data = dict(outfits=outfits, anims=anim_names, stages=STAGES)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(PAGE.replace("__DATA__", json.dumps(data)))
    tot = sum(len(o["anims"]) for o in outfits)
    print(f"  {len(outfits)} outfits, {tot} animations, {len(anim_names)} animation kinds")
    print("  " + OUT.replace("/mnt/c/", "C:/"))
    for o in outfits:
        if not o["anims"]:
            print(f"    EMPTY  {o['name']} - no animations rendered")
    return OUT


PAGE = r"""<!doctype html>
<meta charset="utf-8">
<title>Bug Farmer - player outfits</title>
<style>
  :root { --bg:#16161c; --panel:#1e1e26; --line:#33333f; --ink:#e8e8f0; --dim:#8a8a9c;
          --gold:#ffd98a; --ok:#7ddc8a; --no:#4a4a58; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--ink);
         font:14px/1.5 ui-sans-serif,system-ui,'Segoe UI',sans-serif; }
  header { position:sticky; top:0; z-index:20; background:var(--panel);
           border-bottom:1px solid var(--line); padding:10px 16px; }
  h1 { margin:0 0 8px; font-size:16px; font-weight:600; letter-spacing:.02em; }
  h1 small { color:var(--dim); font-weight:400; margin-left:8px; }
  nav button, .ctl { background:#2a2a34; color:var(--ink); border:1px solid var(--line);
      border-radius:6px; padding:5px 12px; margin-right:6px; cursor:pointer; font-size:13px; }
  nav button.on { background:var(--gold); color:#1a1a1a; border-color:var(--gold); font-weight:600; }
  main { padding:16px; }
  img { image-rendering:pixelated; display:block; }
  .grid { overflow-x:auto; }
  table { border-collapse:collapse; }
  th,td { border:1px solid var(--line); padding:0; text-align:center; vertical-align:middle; }
  th { background:var(--panel); color:var(--gold); font-size:12px; font-weight:600;
       padding:6px 10px; white-space:nowrap; position:sticky; top:0; }
  th.rowhead { position:sticky; left:0; z-index:5; text-align:left; }
  td.rowhead { background:var(--panel); color:var(--gold); font-size:12px; font-weight:600;
       padding:6px 10px; white-space:nowrap; text-align:left; position:sticky; left:0; }
  td img { max-width:150px; max-height:150px; margin:auto; cursor:zoom-in; }
  td.gap { color:var(--no); font-size:11px; padding:14px 8px; }
  .board td { padding:5px 9px; font-size:12px; }
  .board .yes { color:var(--ok); } .board .none { color:var(--no); }
  .card { background:var(--panel); border:1px solid var(--line); border-radius:8px;
          padding:12px; margin-bottom:14px; }
  .card h2 { margin:0 0 4px; font-size:14px; color:var(--gold); }
  .row { display:flex; flex-wrap:wrap; gap:10px; align-items:flex-end; }
  .row figure { margin:0; }
  .row figcaption { color:var(--dim); font-size:11px; max-width:170px; margin-top:3px; }
  .row img { max-width:170px; max-height:220px; border:1px solid var(--line);
             border-radius:4px; cursor:zoom-in; }
  .zoom img { max-width:110px; max-height:110px; background:#2a2a34; }
  .note { color:var(--dim); font-size:12px; }
  #lb { position:fixed; inset:0; background:#000d; display:none; z-index:99;
        align-items:center; justify-content:center; cursor:zoom-out; }
  #lb img { max-width:94vw; max-height:88vh; }
  #lb div { position:absolute; bottom:14px; color:var(--gold); font-size:13px; }
</style>
<header>
  <h1>Bug Farmer — player outfits <small id="sub"></small></h1>
  <nav>
    <button data-t="current" class="on">Current</button>
    <button data-t="progress">Progress</button>
    <button data-t="detail">Outfit detail</button>
    <span style="margin-left:14px" id="extra"></span>
  </nav>
</header>
<main id="main"></main>
<div id="lb"><img><div></div></div>
<script>
const D = __DATA__;
const main = document.getElementById('main'), extra = document.getElementById('extra');
let tab = 'current', flip = false, who = D.outfits.length ? D.outfits[0].name : null;

document.getElementById('sub').textContent =
  D.outfits.length + ' outfits · ' +
  D.outfits.reduce((n,o)=>n+Object.keys(o.anims).length,0) + ' animations';

const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const img = (src, cap) => `<img loading="lazy" src="${src}" alt="${esc(cap)}" data-cap="${esc(cap)}">`;

function current() {
  const rows = flip ? D.anims : D.outfits.map(o=>o.name);
  const cols = flip ? D.outfits.map(o=>o.name) : D.anims;
  const by = Object.fromEntries(D.outfits.map(o=>[o.name,o]));
  let h = '<div class="grid"><table><tr><th class="rowhead"></th>' +
          cols.map(c=>`<th>${esc(c)}</th>`).join('') + '</tr>';
  for (const r of rows) {
    h += `<tr><td class="rowhead">${esc(r)}</td>`;
    for (const c of cols) {
      const o = by[flip ? c : r], a = flip ? r : c;
      const src = o && o.anims[a];
      h += src ? `<td>${img(src, o.name+' · '+a)}</td>`
               : `<td class="gap">—</td>`;
    }
    h += '</tr>';
  }
  return h + '</table></div>';
}

function progress() {
  let h = '<p class="note">Where each outfit actually is. Counts are files found on disk, not a checklist.</p>' +
          '<div class="grid"><table class="board"><tr><th class="rowhead">outfit</th>' +
          D.stages.map(s=>`<th>${esc(s)}</th>`).join('') +
          '<th>animations</th><th>gauntlet source</th></tr>';
  for (const o of D.outfits) {
    h += `<tr><td class="rowhead">${esc(o.name)}</td>`;
    for (const s of D.stages) {
      const n = o.stages[s];
      h += n ? `<td class="yes">${s==='official'?'yes':n}</td>` : `<td class="none">—</td>`;
    }
    const na = Object.keys(o.anims).length;
    h += `<td class="${na?'yes':'none'}">${na||'—'}</td>`;
    h += `<td class="note">${esc(o.gauntlet_source)}</td></tr>`;
  }
  return h + '</table></div>';
}

function detail() {
  const o = D.outfits.find(x=>x.name===who);
  if (!o) return '<p class="note">No outfit.</p>';
  let h = '';
  const sec = (title, body, note) => body
    ? `<div class="card"><h2>${esc(title)}</h2>${note?`<p class="note">${esc(note)}</p>`:''}<div class="row">${body}</div></div>`
    : `<div class="card"><h2>${esc(title)}</h2><p class="note">none yet</p></div>`;

  h += sec('Current — animations',
    Object.entries(o.anims).map(([k,v])=>`<figure>${img(v,o.name+' · '+k)}<figcaption>${esc(k)}</figcaption></figure>`).join(''));

  h += sec('Current — frames',
    Object.entries(o.frames).map(([k,v])=>
      v.map((s,i)=>`<figure>${img(s,k+'_'+(i+1))}<figcaption>${esc(k)}_${i+1}</figcaption></figure>`).join('')).join(''));

  h += `<div class="card"><h2>Gauntlet</h2><p class="note">source: ${esc(o.gauntlet_source)}</p>
        <div class="row zoom">` +
    Object.entries(o.gauntlet).map(([k,v])=>`<figure>${img(v,'gauntlet '+k)}<figcaption>${esc(k)}</figcaption></figure>`).join('')
    + '</div></div>';

  h += sec('Candidates (scratchpad)',
    o.candidates.map(c=>`<figure>${img(c.src, o.name+' candidate')}<figcaption><b>${esc(c.batch)}</b>${
      c.when?'<br>'+esc(c.when):''}${c.prompt?'<br>'+esc(c.prompt.slice(0,150))+'…':''}</figcaption></figure>`).join(''),
    'Every candidate on disk is still named result.png — the batch folder is what tells them apart.');

  if (o.ledger) h += `<div class="card"><h2>CURRENT.md</h2><pre class="note" style="white-space:pre-wrap">${esc(o.ledger)}</pre></div>`;
  else h += `<div class="card"><h2>CURRENT.md</h2><p class="note">Not promoted yet — no ledger. Run promote.py.</p></div>`;
  return h;
}

function render() {
  extra.innerHTML =
    tab==='current' ? `<button class="ctl" id="fl">${flip?'rows = animations':'rows = outfits'}</button>`
  : tab==='detail'  ? `<select class="ctl" id="wh">${D.outfits.map(o=>`<option${o.name===who?' selected':''}>${esc(o.name)}</option>`).join('')}</select>`
  : '';
  main.innerHTML = tab==='current' ? current() : tab==='progress' ? progress() : detail();
  const fl = document.getElementById('fl'); if (fl) fl.onclick = ()=>{ flip=!flip; render(); };
  const wh = document.getElementById('wh'); if (wh) wh.onchange = e=>{ who=e.target.value; render(); };
}

document.querySelectorAll('nav button[data-t]').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('nav button[data-t]').forEach(x=>x.classList.remove('on'));
  b.classList.add('on'); tab=b.dataset.t; render();
});

const lb = document.getElementById('lb');
document.addEventListener('click', e=>{
  if (e.target.tagName==='IMG' && e.target.dataset.cap!==undefined) {
    lb.querySelector('img').src = e.target.src;
    lb.querySelector('div').textContent = e.target.dataset.cap;
    lb.style.display='flex';
  } else if (e.target.closest('#lb')) lb.style.display='none';
});
document.addEventListener('keydown', e=>{ if(e.key==='Escape') lb.style.display='none'; });
render();
</script>
"""


if __name__ == "__main__":
    build()
