# How a bug decides what to do, and when it fights

*My proposal (2026-10-04), built on the decisions recorded in D83 (2026-10-03/04). Nothing here is built yet; the
village's bugs are the first place it would be built and played (see the next page).*

### What stays exactly as it is
How bug numbers rise and fall doesn't change. Today a colony grows from the food its bugs bring home: each trip home
lays an egg, eggs hatch, nests refill and new nests are founded. Bugs die to predators, hunger and old age. Caps and
the director's top-ups are safety nets underneath. That is what makes the village's numbers swing, spike and
sometimes crash until a species is topped up again, and you decided on 2026-10-03 that swings like that are what you
want. So none of it is replaced.

### What changes: why a bug fights, and what it does afterwards
Today there are three separate ways a bug can start a fight, and once it chases you it stops doing everything else.
The proposal gives every bug **one list of what matters to it**, checked from the top a few times a second. The first
thing that applies is what it does.

```svg One list per bug, checked from the top. A fight is just one of the duties, so a bug can return to its work.
<svg width="720" height="330" viewBox="0 0 720 330" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A bug's priority list: stay alive, duty, routine for the hour, wander near home">
  <g style="font-size:18px">
    <rect x="70" y="14" width="630" height="64" rx="8" style="fill:var(--cut-soft);stroke:var(--cut)"/>
    <text x="90" y="42" style="fill:var(--ink);font-weight:700">1. Stay alive</text>
    <text x="90" y="66" style="fill:var(--ink-2)">flee, hide, drop what it carries</text>
    <rect x="70" y="90" width="630" height="64" rx="8" style="fill:var(--change-soft);stroke:var(--change)"/>
    <text x="90" y="118" style="fill:var(--ink);font-weight:700">2. Duty</text>
    <text x="90" y="142" style="fill:var(--ink-2)">defend the nest, raise the alarm, hunt if hungry, carry food home, lay</text>
    <rect x="70" y="166" width="630" height="64" rx="8" style="fill:var(--add-soft);stroke:var(--add)"/>
    <text x="90" y="194" style="fill:var(--ink);font-weight:700">3. Routine for the hour</text>
    <text x="90" y="218" style="fill:var(--ink-2)">forage by day, hunt at night, rest</text>
    <rect x="70" y="242" width="630" height="64" rx="8" style="fill:var(--keep-soft);stroke:var(--keep)"/>
    <text x="90" y="270" style="fill:var(--ink);font-weight:700">4. Wander near home</text>
    <text x="90" y="294" style="fill:var(--ink-2)">when nothing above applies</text>
    <line x1="34" y1="22" x2="34" y2="296" style="stroke:var(--ink-3);stroke-width:3"/>
    <polygon points="24,290 44,290 34,310" style="fill:var(--ink-3)"/>
  </g>
</svg>
```

### What gives a bug a reason to fight
Each species gets its reasons from its own life:
- its nest is disturbed;
- its brood is threatened;
- it is hungry, and you are food (a blood-feeder);
- you are in its patch at the hour it hunts;
- a nestmate was hurt nearby (only bugs from the same nest join in).

Simply being close to you is also a reason, but only for the bugs whose nature that is (hunters and hostile bugs).
Danger stays real (D83): the village is fairly easy but dangerous enough that you want armour and a sword, and it gets
harder outward.

### Four temperaments
| Temperament | What it means | In the village |
|---|---|---|
| Calm | Ignores you unless you hurt it | flies, butterflies, millipedes, carrion beetles |
| Defensive | Defends its nest or itself, then goes back | paper wasps |
| Hunter | Hunts in its patch at its hour; you can be the prey | the centipede at night |
| Hostile | Attacks what comes near | hornets at lights, later; further out, more of these |

Further out, more hunters and hostile bugs. Black-ant workers are calm; their soldiers patrol the colony and the
trails and attack intruders; fire ants (my recommendation for the dangerous deep ant) are hostile near their mounds.

### How many attack at once
Never all at once, and never a fixed one or two (your correction of 2026-10-03). The number of attackers at any one
moment grows with how angry the group is, and attackers take turns swooping in and pulling back. The others circle and
menace. The numbers below only illustrate; each bug's are tuned in the arena.

```svg How many attack at once grows with the group's anger; attackers take turns.
<svg width="720" height="300" viewBox="0 0 720 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Attackers at once by anger: brushed past the nest 1, hit it once 2 to 3, keep hitting 4 to 5">
  <g style="font-size:18px">
    <line x1="80" y1="230" x2="700" y2="230" style="stroke:var(--line-strong);stroke-width:2"/>
    <text x="20" y="40" style="fill:var(--ink-2)">attackers at once</text>
    <rect x="120" y="190" width="120" height="40" rx="4" style="fill:var(--change-soft);stroke:var(--change)"/>
    <text x="180" y="180" text-anchor="middle" style="fill:var(--ink);font-weight:700">1</text>
    <rect x="320" y="140" width="120" height="90" rx="4" style="fill:var(--change-soft);stroke:var(--change)"/>
    <text x="380" y="130" text-anchor="middle" style="fill:var(--ink);font-weight:700">2–3</text>
    <rect x="520" y="70" width="120" height="160" rx="4" style="fill:var(--cut-soft);stroke:var(--cut)"/>
    <text x="580" y="60" text-anchor="middle" style="fill:var(--ink);font-weight:700">4–5</text>
    <text x="180" y="256" text-anchor="middle" style="fill:var(--ink)">walked past the nest</text>
    <text x="380" y="256" text-anchor="middle" style="fill:var(--ink)">hit the nest once</text>
    <text x="580" y="256" text-anchor="middle" style="fill:var(--ink)">keep hitting it</text>
    <text x="390" y="290" text-anchor="middle" style="fill:var(--ink-2)">example numbers only: tuned per bug in the arena</text>
  </g>
</svg>
```

### Nest defence uses the colony's real numbers
When you disturb a nest, the defenders that come out are the bugs that actually live there (and its soldiers, where
the species has them). A booming colony boils over; one that just crashed barely defends. Killing defenders really
shrinks the colony, which must rebuild from food. The fight reads the ecology, and the fight changes it.

### After a fight
The bug goes back to what it was doing: home, carrying food, back to its trail. A leash makes sure you can always get
away: it gives up after some time without landing a strike, when it is too far from home, or when it can't reach you.

### Examples: what you would see
| Bug | What you see |
|---|---|
| Paper wasp | A wasp on your cabbages ignores you unless you swing at it. Swat it and it fights back, and nestmates close by join. Walk past the nest and a couple of guards come out to look. Hit the nest and every wasp at home comes out; afterwards they all go home. |
| Centipede | By day it hides under its log and only strikes if you lift or break the log. At night it hunts its patch and lunges at a player crossing it. Hungry ones roam farther. |
| Black ants | Workers ignore you unless you really attack them; a tap of the bug stick steers them without angering them. Soldiers patrol and attack intruders who come close. Break into the mound and as many soldiers as the colony really has pour out, chase you to the edge of their range, then go home. |
| Fire ants | Attack on sight near their colonies. |
| Mosquitoes | Hungry ones come for your blood; fed ones fly off to rest, so a swarm thins as it feeds. |

Killing a nest's bugs will also alert that nest; today only damaging the nest itself does.
