The PDFs saved locally. Let me extract their text directly, and find an archived copy of the tutsplus tutorial.

---

pdftotext isn't available. Let me try Python PDF libs and fetch the GitHub source and Kung-Fu Circle via alternate routes.

---

Both have extractable text. Let me read the Kung-Fu Circle chapter (the richest encirclement source).

---

I have rich material from two deep-read sources. Writing the technical synthesis now.

---

# Formation Movement & Encirclement — Technical Writeup

## 1. Slot-based formations (anchor + pattern)
A **fixed formation** is a set of positioned **slots**; one slot is the **leader** and every other slot is defined *relative* to it (relative position `p_r`, relative orientation `θ_r`). The leader steers as if it weren't in a formation; the pattern rides along. Each slot's **world position/orientation** is the leader transform applied to the relative offset (verbatim from the Millington-based lecture):

```
p_s = p_L + Ω_L · p_r
    = p_L + [ p_rx·cosθ − p_ry·sinθ ,  p_rx·sinθ + p_ry·cosθ ]
θ_s = (θ_L + θ_r) mod 2π
Ω_L = [[cosθ, −sinθ],[sinθ, cosθ]]     // leader's rotation matrix
```
Setting positions *directly* from geometry avoids the "naïve follow-the-leader" traffic jam (everyone shortest-pathing to the leader, colliding), but causes "warp speed" sweep of outlying slots on turns — so cap turn rate and size collision/obstacle avoidance to the whole formation.

**Anchor point / drift (the robust version).** Replace the real leader with an **invisible anchor point = center of mass of the slots (average position AND average orientation)**. It has its own steering, controls no individual, and ignores small obstacles/bumps. Crucially the anchor's kinematics are driven *by the members* so the formation "keeps up": base the anchor position/orientation/velocity on the **average of the characters currently in slots**, then push the anchor a small offset `k_offset` *ahead* of the COM along its velocity while moving (set it exactly to the average when stationary). **Anchor orientation must be the average slot orientation or the formation spins.** This is the drift that makes the formation center track its actual members instead of running off ahead.

**Scalable / emergent variants.** Scalable = a *function* computes slot count/offsets from N instead of a fixed list. Emergent = each character runs `arrive` toward a target chosen from neighbours' positions (e.g. "behind-and-to-the-side" for a V); if a target's taken, pick another — cheap but hard to shape (jostling in the V's center).

## 2. Encirclement — ring around a target (the emphasis)
The cleanest documented system is the **"Belgian AI" battle grid** from *Kingdoms of Amalur: Reckoning* (GameAIPro ch. 28). A **world-space grid of slots is carried, centered on the target** (player), forming a **ring of equidistant slots** ("tic-tac-toe board with the player at center", 8 slots). To distribute N agents evenly, slot `i` sits at angle `2πi/N` on radius `R`: `slot_i = target + R·(cos(2πi/N), sin(2πi/N))`.

**Centralized "stage manager" owns all assignment** — no spatial reasoning lives in individual agents. An attacker *requests* a slot; the manager assigns the **closest available slot** and the agent arrives to it. Because slots are keyed to fixed angular positions and each is claimed by exactly one agent, agents **cannot clump on one side** — an unclaimed angle is the only place a newcomer can go, producing natural flanking "without any creature explicitly knowing about any other."

**Reservation & capacity.** Each agent has a **grid weight** (cost of a slot); the target has a **grid capacity**. Assign only while `Σ weights < capacity` (a troll weight-8 fills more of a 12 budget than a soldier weight-4); overflow agents wait *outside* the ring. A parallel **attack capacity / attack weight** budget gates how many may actually strike. Difficulty scales purely by raising these capacities — individual weights stay fixed.

**Inner/outer circle.** Two radii: an **approach circle** (granted-but-not-attacking agents stand here) and an inner **attack circle** (only an agent with an attack token steps in). Unassigned agents wait outside. This reads clearly to the player and stops attackers fouling each other.

**Re-centering on a moving target (the hard part).** The grid is world-aligned and moves with the target, so an assigned slot may stop being the agent's nearest (e.g. player rolls toward a waiting enemy). Fix: **agents store NO slot memory — they re-query the manager every frame**, which can reassign / "steal" slots to minimize *total* travel time. Agents mid-attack **lock** their slot so they aren't displaced. The reassignment loop:
```
for creature in AttackingList:
    slot = closest slot to creature
    if slot.locked: continue
    assign slot to creature; remove creature from list
    if slot was already assigned: unassign the previous creature
```

## 3. Two-level steering
Anchor/stage-manager steers the *pattern* (long-range pathing, one entity); each **individual** independently does `arrive`-to-slot + separation + collision/obstacle avoidance. A slot may be briefly unreachable — the per-agent steering keeps behavior sane meanwhile. Formations nest: a sub-formation's anchor is itself a slot in a higher formation (same interface for individual or squad).

## 4. Computational cost
- Per-agent steering (arrive + separation): **O(1)** (separation is O(neighbors) with spatial partitioning).
- **Naïve greedy** "closest free slot per agent": O(n·slots).
- **Optimal** assignment (min total cost, cost=distance) is the **assignment problem — Hungarian algorithm O(n³)**; the exhaustive space is huge (20 slots×20 agents ≈ 2.5×10¹⁵), so games use greedy. Millington's heuristic: assign **most-constrained agents first** (low "ease of assignment"), each to its **lowest-cost** remaining slot; role slots use cost 0=ideal … ∞=impossible.

## 5. Determinism for a fixed-point integer server sim
- **Ring geometry:** `cos/sin` are non-deterministic across platforms/libms. **Precompute a fixed-point LUT** of `(cos,sin)` for the angular slots (e.g. N or 256 entries), store as scaled integers; `slot_i = target + (R·cos_fp[i] >> SHIFT, R·sin_fp[i] >> SHIFT)`. No runtime float trig.
- **Assignment must be deterministic:** iterate agents in a **fixed order (sorted by stable agent id)**, greedy-nearest with **tie-break by agent id then slot index** — never by hash/pointer/iteration order.
- **No double-claim:** a slot is claimed by the first agent in the deterministic order; the "steal"/reassign pass runs in that same fixed order so the outcome is reproducible. Lock-during-attack is a boolean in ledger state, not wall-clock timed.
- Keep the anchor COM/drift math in fixed-point (integer averages, integer `k_offset`), avoiding float accumulation drift across clients.

## Sources actually fetched and deep-read
- Georgia Tech CS AI lecture PDF — *Steering, Flocking, Formations* (Millington/Buckland formation-motion math, anchor point, slot assignment): `https://faculty.cc.gatech.edu/~surban6/2019fa-gameAI/lectures/2019_09_18_steering-formations.pdf`
- Game AI Pro, Chapter 28 — Michael Dawe, *Beyond the Kung-Fu Circle: A Flexible System for Managing NPC Attacks* (the encirclement/battle-grid system): `http://www.gameaipro.com/GameAIPro/GameAIPro_Chapter28_Beyond_the_Kung-Fu_Circle_A_Flexible_System_for_Managing_NPC_Attacks.pdf`

Note: the Envato Tuts+ "Battle Circle AI" article and its GitHub repo surfaced in search (corroborating the reserved-slot ring concept) but could not be deep-read — the article URL 301-redirected to a category page and the GitHub README did not render — so I have not cited them as read.