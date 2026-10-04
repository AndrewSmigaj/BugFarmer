# How many bugs a zone can hold, and how to get more

*My design proposal, 2026-10-04. The numbers are measured on this PC (i7-14700F) with the real game client running
headless; where a number is an estimate, it says so.*

### Where the numbers come from
I made a test copy of the village and multiplied every species' **starting** numbers by 1, 2 and 4. The real village
starts at about 900 bugs and settles to 200–400 after its first day, because most of the starting flies starve. So:

| Test | Bugs alive on average | What it stands for |
|---|---|---|
| 1× | ~290 | the village as you play it, after day 1 |
| 2× | ~550 | twice the village |
| 4× | ~2,600 | four times the starting numbers (the client fell behind here, so it stayed nearer its starting count) |

At the village's real numbers the bugs cost well under a millisecond per tick, which matches your playtests. The
problems only show at the bigger sizes, and they come from two specific pieces of code, not from simulating bugs as such.

### What a tick costs, part by part
Measured with timers on every part, at ~3,300 bugs in ~490 groups, at normal game speed:

| Part | Each tick (10 a second) |
|---|---|
| Moving the bugs | 17.7 ms, of which **15.0 ms is the food lookup** |
| Looping over the groups (they're re-sorted every tick) | 1.9 ms |
| Hunting-strike checks (copies and sorts each group's bugs) | 4.3 ms |
| State check (copies every bug into a 31-field record) | 3.3 ms |
| Everything else | 0.3 ms |
| **Whole tick** | **27.4 ms** |

Every frame (60 a second) adds 3.2 ms to smooth every bug's movement on screen and 3.3 ms of centipede trails, whether
the bugs are on screen or not.

About 23 of the 27 ms per tick, and most of the per-frame cost, is work that doesn't need doing.

### The fixes (the game stays exactly the same)
Every fix below gives **bit-identical results** on every computer, so every player still sees the same bugs and nothing about how the
game plays changes. They only remove wasted work.

0. **Bring the whole zone to life.** Separately from cost: the server only sets up food, nests and stations in the
   chunks a player has loaded (25 of the village's 64 around one player), and treats unloaded ground as a wall for
   moving bugs. The whole zone should live, as the bugs on the players' computers already do.
1. **Look food up once per group, and only nearby.** Today every bug that isn't hunting or eating looks for the
   nearest food every tick by checking every piece of food in the zone, and it does so from its group's centre, so
   all the bugs in a group get the same answer. Instead: one lookup per group per tick, and food kept in a grid of
   cells so a lookup only checks the cells within reach.
2. **Check the state without copying it.** Every tick, each computer fingerprints every bug's state so drift between
   players is caught. To read each bug, it currently builds that bug's full snapshot record (31 fields, text included)
   and sorts the bugs again. Instead: read the few numbers it needs straight from the bug, in a bug order kept sorted
   as bugs are added and removed. No throwaway objects, no re-sorting every tick.
3. **No re-sorting every tick anywhere.** The groups and the bugs in each group are sorted every tick so every computer
   processes them in the same order. Keep them in sorted lists, updated when a bug or group is born or dies.
4. **Only smooth and draw what's on screen.** The per-frame smoothing and centipede trails run only for bugs a player
   can see.
5. **Spread a tick over the frames between ticks.** A tick comes ten times a second and today all its work lands in
   one frame, so a heavy tick is a stutter even when the average is low. The work can be split across the six frames
   between ticks (the same steps in the same order, so identical results), so no single frame carries a whole tick.

### The snapshot: send it only when someone joins
**What it is.** A full picture of every bug's state, so a player who joins (or whose computer drifts out of step)
can pick up exactly where everyone else is. For each bug: position, speed, its random-number state, what it's doing,
its movement plan, its feeding and hunting timers and its lunge state. Plus the zone's food list, who is hunting
whom, which groups are calmed, and where the players stand.

**Why it goes up every 10 seconds today.** The server keeps only the last 20 seconds of events. A joiner gets "the
latest snapshot + every event since", which only works if the snapshot is less than 20 seconds old. Hence one every
10 seconds, all the time, whether anyone joins or not.

**Your idea is the better design: ask for it when someone joins.** When a player joins, or a computer asks to resync,
the server asks the computer in charge for a fresh snapshot, waits for it (a fraction of a second), and hands it over
with the few events since. Nothing goes up while nobody joins. If the computer in charge doesn't answer in time
(say it's leaving), the server falls back to what it does today for the very first moments of a zone: the joiner
builds the bugs from the shared seed, and the drift check pulls it into step.

**And make it small.** Each bug is written today as about 31 named text fields, about 670 bytes, including its group's
id repeated for every bug, two diagnostic fields, and eight lunge fields that are zero for almost every bug. The
server passes each group's bugs through untouched, so the client can pack them as plain numbers and compress them
without changing the server. Estimate: 50–100 bytes per bug instead of ~670, so a join at today's numbers downloads
under 100 KB instead of ~670 KB.

### Going much bigger later: only simulate bugs in full near players
*(an option, not part of the fixes above)*

Distant groups would move as a group (their centres already follow a shared path), and their individual bugs would
only be worked out when a player comes near; all computers agree when that happens because they share the players'
positions. This is how games with very large worlds keep cost tied to what players can see. It is a big change: it
touches hunting, the snapshot and the zone's ecology, and must keep every rule we have about bug behaviour living on
the players' computers. I'd only start it if the target is well past what the fixes above deliver.

### Your decision
After the fixes are in and measured again: **how many bugs a zone may hold.** I'll bring the measured cost per bug
on this PC with an allowance for a slower one, and a recommendation for each zone and how it splits across species.
My estimate today is a few thousand per zone; the measurement decides.
