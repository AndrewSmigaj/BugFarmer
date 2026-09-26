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

IT SHOWS WHAT IS OFFICIAL — NOT WHAT IS ON DISK
-----------------------------------------------
Every name, path and animation comes from `official.py`. This page used to SCAN DIRECTORIES instead, so
it inherited the renderer's fallback chains and showed whatever happened to be lying around — which is
exactly why asking for "a gallery of the official ones" returned things nobody had chosen. Owner,
2026-08-06: *"I will for example ask for a gallery showing all the official whatevers and it will just
be random crap."*

Concretely, before this: `thrust_spear_two_handed.gif` appeared in the gallery for 22 outfits, long after
the code that produced it had been deleted; and 21 outfits displayed hands loaded from a gitignored
archive folder. Both were on disk, so both were shown.

Outfits in `official.PENDING` are listed as NOT official and are not rendered. An outfit is complete and
official, or it is pending — there is no third state where it borrows someone else's parts.

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
import official as O                                     # noqa: E402  the only source of truth

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
OUT = os.path.join(PLAYER, "gallery.html")


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


def _named(outfit, kind, names, ext):
    """The files official.py says should be there. A name that is ABSENT is reported as absent —
    never replaced by whatever else happens to be in the folder."""
    d = os.path.join(PLAYER, O.path(outfit, kind))
    out = {}
    for n in names:
        p = os.path.join(d, f"{n}{ext}")
        out[n] = rel(p) if os.path.exists(p) else None
    return out


def scan_tries(outfit):
    """Every attempt, so alternatives stay visible next to the one that was chosen.

    This is the ONLY place the gallery looks at the disk rather than at official.py, and deliberately:
    tries/ is exploration, its contents are not declared anywhere, and nothing is loaded FROM it.
    """
    d = os.path.join(PLAYER, O.path(outfit, O.TRIES_DIR))
    found = []
    if os.path.isdir(d):
        for batch in sorted(os.listdir(d)):
            bd = os.path.join(d, batch)
            if os.path.isdir(bd):
                for f in _pngs(bd):
                    found.append(dict(src=rel(os.path.join(bd, f)), batch=batch, **read_record(bd)))
    return found


def scan(outfit, official=True):
    o = (O.OUTFITS if official else O.PENDING)[outfit]
    frames = {} if not official else {
        bank: [v for v in _named(outfit, O.FRAMES_DIR, [f"{bank}_{i}" for i in (1, 2, 3)], ".png").values()]
        for bank in ("front", "side", "back")}
    return dict(
        name=outfit,
        official=official,
        approved=o.get("approved") or o.get("chosen", ""),
        words=o.get("words", ""),
        needs=o.get("needs", ""),
        frames={k: [p for p in v if p] for k, v in frames.items()},
        gauntlet=_named(outfit, O.HANDS_DIR, O.HAND_ROLES, ".png"),
        anims=_named(outfit, O.ANIM_DIR, list(O.ANIMATIONS), ".gif"),
        tries=scan_tries(outfit),
    )


def build():
    outfits = ([scan(n, True) for n in O.OUTFITS]
               + [scan(n, False) for n in O.PENDING])
    data = dict(outfits=outfits,
                anims=list(O.ANIMATIONS),          # declared order, not alphabetical disk order
                roles=O.HAND_ROLES,
                role_meaning=O.HAND_ROLE_MEANING,
                not_agreed=O.NOT_AGREED)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(PAGE.replace("__DATA__", json.dumps(data)))

    have = sum(1 for o in outfits if o["official"])
    print(f"  {have} official, {len(O.PENDING)} pending, {len(O.ANIMATIONS)} animations declared")
    print("  " + OUT.replace("/mnt/c/", "C:/"))
    for o in outfits:
        if not o["official"]:
            print(f"    PENDING  {o['name']} - {o['needs']}")
            continue
        missing = [k for k, v in o["anims"].items() if not v] + \
                  [f"hand:{k}" for k, v in o["gauntlet"].items() if not v]
        if missing:
            print(f"    INCOMPLETE  {o['name']} - missing {', '.join(missing)}")
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

const OFFICIAL = D.outfits.filter(o=>o.official);
const PENDING  = D.outfits.filter(o=>!o.official);

document.getElementById('sub').textContent =
  OFFICIAL.length + ' official · ' + PENDING.length + ' pending · ' +
  D.anims.length + ' animations declared in official.py';

const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const img = (src, cap) => `<img loading="lazy" src="${src}" alt="${esc(cap)}" data-cap="${esc(cap)}">`;

// Only OFFICIAL outfits appear in the grid. A pending outfit renders nothing at all — it is never
// shown wearing somebody else's parts, which is what the old directory-scanning page did.
function current() {
  if (!OFFICIAL.length) return '<p class="note">Nothing is official yet.</p>';
  const rows = flip ? D.anims : OFFICIAL.map(o=>o.name);
  const cols = flip ? OFFICIAL.map(o=>o.name) : D.anims;
  const by = Object.fromEntries(OFFICIAL.map(o=>[o.name,o]));
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
  let h = '<p class="note">Straight from official.py. An outfit is OFFICIAL and complete, or PENDING and ' +
          'not rendered — there is no third state where it borrows another outfit’s parts.</p>' +
          '<div class="grid"><table class="board"><tr><th class="rowhead">outfit</th><th>status</th>' +
          '<th>hands</th><th>animations</th><th>agreed</th><th>notes</th></tr>';
  for (const o of D.outfits) {
    const nh = Object.values(o.gauntlet).filter(Boolean).length;
    const na = Object.values(o.anims).filter(Boolean).length;
    h += `<tr><td class="rowhead">${esc(o.name)}</td>`;
    h += o.official ? `<td class="yes">official</td>` : `<td class="none">pending</td>`;
    h += `<td class="${nh===D.roles.length?'yes':'none'}">${nh}/${D.roles.length}</td>`;
    h += `<td class="${na===D.anims.length?'yes':'none'}">${na}/${D.anims.length}</td>`;
    h += `<td class="note">${esc(o.approved||'—')}</td>`;
    h += `<td class="note">${esc(o.needs || o.words || '')}</td></tr>`;
  }
  h += '</table></div>';
  if (D.not_agreed && Object.keys(D.not_agreed).length) {
    h += '<div class="card"><h2>Not agreed — deliberately absent so it cannot render by accident</h2>' +
         Object.entries(D.not_agreed).map(([k,v])=>`<p class="note"><b>${esc(k)}</b> — ${esc(v)}</p>`).join('') +
         '</div>';
  }
  return h;
}

function detail() {
  const o = D.outfits.find(x=>x.name===who);
  if (!o) return '<p class="note">No outfit.</p>';
  let h = '';
  const sec = (title, body, note) => body
    ? `<div class="card"><h2>${esc(title)}</h2>${note?`<p class="note">${esc(note)}</p>`:''}<div class="row">${body}</div></div>`
    : `<div class="card"><h2>${esc(title)}</h2><p class="note">none yet</p></div>`;

  if (!o.official)
    h += `<div class="card"><h2>NOT OFFICIAL</h2><p class="note">Nothing below is built. Needs: ${esc(o.needs)}</p></div>`;
  else if (o.words)
    h += `<div class="card"><h2>Approved ${esc(o.approved)}</h2><p class="note">“${esc(o.words)}”</p></div>`;

  // A declared animation with no file shows as a MISSING tile rather than being quietly left out.
  h += sec('Animations',
    D.anims.map(k=>{
      const v = o.anims[k];
      return `<figure>${v?img(v,o.name+' · '+k):'<div class="gap" style="padding:28px">missing</div>'}` +
             `<figcaption>${esc(k)}</figcaption></figure>`;
    }).join(''));

  h += sec('Frames',
    Object.entries(o.frames).map(([k,v])=>
      v.map((s,i)=>`<figure>${img(s,k+'_'+(i+1))}<figcaption>${esc(k)}_${i+1}</figcaption></figure>`).join('')).join(''));

  h += `<div class="card"><h2>Hands</h2><p class="note">One per official.HAND_ROLES. Every outfit has its own version of all ${D.roles.length}.</p>
        <div class="row zoom">` +
    D.roles.map(k=>{
      const v = o.gauntlet[k];
      return `<figure>${v?img(v,'hand '+k):'<div class="gap" style="padding:28px">missing</div>'}` +
             `<figcaption>${esc(k)}<br><span class="note">${esc(D.role_meaning[k]||'')}</span></figcaption></figure>`;
    }).join('') + '</div></div>';

  h += sec('Tries — every attempt, kept',
    o.tries.map(c=>`<figure>${img(c.src, o.name+' try')}<figcaption><b>${esc(c.batch)}</b>${
      c.when?'<br>'+esc(c.when):''}${c.prompt?'<br>'+esc(c.prompt.slice(0,150))+'…':''}</figcaption></figure>`).join(''),
    'Nothing is loaded from here. Choosing copies one into place; the rest stay for comparison.');
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
