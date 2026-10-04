# §19 · Multiplayer & hosting
<!-- gdd: id=19 status=review updated=2026-09-30 -->

## The experience
It works like Terraria. From the main menu you play alone, **host** a world your friends join, or **join** someone
else's. Anyone can also run a world on a separate server program so it stays up all the time — that is how we will
run our own public world too, as one server among many. Everyone in a zone sees exactly the same bugs doing exactly
the same things, and the world runs the same for everyone. Your character belongs to the world you made it in,
unless the host lets characters from other worlds in. Out in the world anything goes except the townspeople's
things; your own plot is safe from other players, and fights between players happen only on servers that allow them.

## Decided
Each line is the owner's decision in my words, with its date.
- **Like Terraria** (2026-09-26) — hosting and joining work the way they do in Terraria.
- **Our server is just another server** (2026-09-26) — we will run a server of our own, but it is not part of the
  game: players join it like anyone else's. Each server holds as many players as is measured to work, the way
  Minecraft servers are capped.
- **Joining** (2026-09-26) — by typing an address, or through Epic's free connection service, which passes the game's
  traffic between players when a home router blocks a direct link; Steam's own version of that comes later.
- **Characters** (2026-09-26) — each world keeps its own characters, with a host setting that lets in characters
  from other worlds. **No limit on characters per account** — they're cheap to make (2026-09-28, D58).
- **Everything in the shared world runs the same for every player** (2026-09-28, D58).
- **Fights between players only where a server allows them** — the game is players against the world, but a server
  can switch player-versus-player on for those who want it (2026-09-28, D58).
- **Private plots are invite-only** — nobody else can add or change anything on a plot without its owner's
  permission; what the owner sets up there can still go wrong while they're away (2026-09-28, D58, D67).
- **The shared world is lawless except for what belongs to others** — the townspeople's things, owned stations such
  as a mining camp's, and the village's stations can't be damaged or taken, and a short message says so (2026-09-26;
  2026-09-27, D41, D44; 2026-09-28, D55).
- **Giving and healing** (2026-09-27, D50, D54): right-click a player to offer an item, bugs or coins; a new drop
  action puts things on the ground; left-click a bandage or potion on a friend to heal them at once; no trade screen
  between players at first.
- **One clock for the whole world**, no skipping the night, and the world stops only when nobody is online; empty
  zones stay frozen and catch up when someone arrives, with a few bugs wandering over from frozen neighbours
  (2026-09-26; 2026-09-28, D57, D61).
- **The roles of the server and the players' computers are rethought by what works best**, and each job still on the
  server has to justify its place, because this area breaks easily (2026-09-28, D58). Each bug's
  own behaviour stays on the players' computers, as it has since July 2026.
- **P5 is built in full** (2026-09-30, D73): characters saved with their zone every minute and when the server stops,
  the duplication faults fixed along with it, rolling backups, and a restore that brings zones and characters back
  together after a safety copy — all tested end to end. The backup folder, the restore behaviour and the numbers
  (10 recent, 7 daily and 4 weekly backups) were recommendations the owner accepted.

## Current design
- **Many separate worlds, each moderated by its own owner** — from the December 2025 requirements: a world has an
  owner and admins who can kick and ban; access can be public, private or invite-only; inside a world anyone can
  place or break blocks (no land claims — safe land comes from City Hall's private plots). (`requirements.md` §2–3)
- **Light anti-cheat** — no heavy anti-cheat and no strict checking of everything players do, since players host
  (January 2026, §5.3). The server still checks what matters: coins, inventory, catches, damage.
- **Zones run separately.** Each zone is its own running game on the server; walking off an edge moves you into the
  next one.
- **The world saves as it is** — each zone saves whole (bugs, farms, buildings) every 10 minutes, when it empties, and
  on shutdown. (`architecture_persistence.md`)

## As built
- The game talks to **Nakama**, a free open-source game-server program, set up on this PC the way developers run
  it. That's fine for building the game, but no player can be asked to set it up, and the game only looks for a
  server on this same PC (`NetworkManager.cs`, line 61).
- **Characters are already per server:** an account can have up to eight (the limit goes, D58); a character carries
  its coins, inventory, equipment and known recipes; only the server can change coins and inventory
  (`character_persist.go`, `rpc/character.go`).
- **Since 2026-09-30, a character is saved only together with the zone it is in** (D73), in one write,
  so the two always come back from the same moment: every minute while the zone is occupied, whenever someone leaves,
  after a sleep in a bed, and when the server stops cleanly — through one ordered save queue (`persistence.go`,
  `save_writer.go`). Before, characters and the world were saved at different moments and a shutdown saved nothing at
  all. A character is also in one zone at a time: walking into the next zone waits until the last one has
  saved it, and a second copy of the game in the same zone takes over from the first (`char_registry.go`) — so a
  crossing or a reconnect can no longer duplicate or lose items. Every zone and every character are also backed up
  together, at one moment — at each start and every 30 minutes while anything changes, keeping the newest 10, one a
  day for a week and one a week for a month — and one command restores a backup, keeping a safety copy of the
  current state first (`backup.go`, `restore.go`, `tools/saves/restore_backup.py`).
- **Worlds save and restore** zone by zone (`world_save.go`). Since 2026-09-26 an old save is upgraded when the game
  updates (the original copy is kept), and a save from a newer version is refused instead of being overwritten — for
  worlds and characters alike.
- **Everyone sees the same bugs:** the two-player tests of 2026-09-26 pass — standing together, all 76,447 bug checks
  matched; standing at opposite ends of the zone, all 77,737 matched.
- **Limits that exist:** a fixed 100 players per zone ("world is full" past that), and a "private" world only its
  owner can enter (`state.go`, `match.go`). Neither is a host setting yet.
- **What the server does today.** It keeps money, items and saves, crops and fruit trees, the weather and a clock for
  each zone; it referees catches, damage, shop trades, crafting, and placing and breaking things. It also still runs
  the bugs as groups: it decides where each group goes and when it hunts, flees or goes for a player; breeding, hunger,
  ageing and deaths; merging and splitting groups; ant trails, nests, broods and hives; and the ecology's balancing. It
  numbers every event so every computer applies it at the same moment, sends a late joiner everything they need to
  catch up, and checks that everyone stays in step. Each bug's own movement, lunges and feeding run on the players'
  computers, in step (`predation.go`, `match.go`, `architecture_swarm_sync.md` §0).
- **Known faults** (number 3 in the roadmap's list): the first player into a fresh zone may stall. (Fault 2 — two
  players arriving at once starting two copies of a zone — is fixed: one live copy per zone, 2026-09-30,
  `zone_lease.go`. Fault 6 — a failed zone crossing stranding the player — is fixed the same day: the game goes back
  to the zone it left, with a short message; only if that zone can't be entered either is the player left in no zone.)
- **Not built yet:** Host & Play, Join, a world-list screen, passwords, kick and ban, chat (the server has a slot set
  aside for it, unused), the game reconnecting by itself (the server already accepts a returning player), a version
  check, giving things to other players, a drop action, private plots and their invitations, one clock for the whole
  world, and the frozen zones' catch-up.

## How it will work
This part is engineering, researched on 2026-09-26 (sources at the bottom). It is here so you can see the plan; the
choices you can change are the proposals below.
- **A small server program of our own** that speaks exactly the same language as today's Nakama server, so the game
  and every test tool stay unchanged. The game starts it in the background for Host & Play, and it ships separately
  as the dedicated server. Nakama stays as a fallback. The proof: the tests that check every player sees the same bugs
  must give identical results on both.
- **Traffic is small.** Measured: the bug simulation sends about 2 KB per second per player in a busy zone (bursts
  around 7 KB/s). Player movement, map data and the one-off download when you enter a zone come on top and still
  need measuring; eight players should stay well within a home connection's upload.
- **Getting through home routers:** the game first asks the host's router to open the way automatically; only some
  routers allow that. When it fails, friends use a join code instead, and the connection goes through Epic's free
  connection service, which passes the game's traffic between you and your friends and works for any store. That
  means adding Epic's software to the game — real work, still to be estimated. Steam's version comes later, if the
  game goes on Steam.

## Proposals
### P1. Three buttons, one kind of world
<!-- key: 19.three-buttons-one-kind-world -->
The main menu has **Single Player**, **Host & Play** and **Join**. Single Player is Host & Play with nobody else
allowed in — the same program underneath, so there is one set of bugs to fix, and any world can be opened to friends
later, as in Terraria. When the host quits, the world closes for everyone still playing (as in Terraria), and every
character is saved first; a dedicated server keeps a world running.

**Lenses:** Simpler alternative — one way of running a world, not two. Like Terraria, as decided.

### P2. Join with an address or a short code
<!-- key: 19.join-address-short-code -->
Friends type your address, which works when your router lets the game through, or a short **join code** you read
out to them, which works for almost everyone because it goes through Epic's connection service. A "recent servers"
list remembers where you've played.

**Lenses:** Picture the moment — a friend on a call: "the code is BUGS-4471". Already covered? — an address alone
only works when the host's router lets the game through.

### P3. The player limit is a host setting, capped at what's measured
<!-- key: 19.player-limit-host-setting-capped -->
Each world gets a **max players** setting (default 8 until measured). Before launch we measure the real ceiling —
the host's computer, their upload speed, and the slowest player's computer, since every player's computer simulates
the bugs in their zone — both with everyone in one zone and with players spread across zones, since the host runs
every zone in use. The measured number is a hard cap: a host can set fewer players, never more, so no world can be
pushed past what keeps everyone in step. For comparison: Terraria's server defaults to 16 (8 before 2020); Valheim,
which also simulates on players' computers, caps at 10.

**Lenses:** Your decision to cap each server at what is feasible. Scale — measured, not guessed.

### P4. A settings file and admin commands, like Minecraft and Terraria
<!-- key: 19.settings-file-admin-commands-like -->
The dedicated server reads one plain settings file: world name, password, max players, the network port (the number
the game listens on), whether characters from other worlds may join, fights between players (P9), how often it
autosaves, how many backups to keep, and a welcome message. Admins get chat commands: kick, ban, unban, an allow-list
(only named players may join), save, and shut down.

**Characters from other worlds are off by default on a dedicated server** — ours included — and on for Host & Play.
A character from another world comes from the player's own computer, so the server can't vouch for its coins and
items; big public Terraria servers keep characters on the server for the same reason.

**Lenses:** Built on what's already designed — the December requirements ask for kick, ban and access control.
Fairness — no one brings made-up riches into a public world.

### P5. Automatic backups, and characters saved with the world
<!-- key: 19.automatic-backups-characters-saved-world -->
Saves already upgrade safely when the game updates. Still to build: the server keeps backups of every world — for
example the last 5, plus one a day for a week — and can restore one with a command. **Characters are backed up and
restored with their world**, so restoring one without the other can't duplicate or delete items; and characters are
saved every few minutes while playing and whenever a zone shuts down, not only on leaving or sleeping.

**Lenses:** What can go wrong — a bad update, a crash mid-save, a griefer, a host who quits without warning.

### P6. A plain version check
<!-- key: 19.plain-version-check -->
If your game and the server are different builds, you are told plainly — *"This server runs 1.2; you have 1.1.
Update to join."* — instead of a confusing failure. The check compares exact builds, since any change to the bugs'
behaviour would put players out of step.

**Lenses:** What can go wrong. Picture the moment.

### P7. Drop back in after a disconnect
<!-- key: 19.drop-back-after-disconnect -->
If your connection drops, your character leaves the world at once and is saved; rejoining puts you back where you
were, with the bugs exactly in step — the same catch-up that already lets a player walk into a busy zone mid-game and
see every bug where it should be.

**Lenses:** What can go wrong. Built on something already proven.

### P8. Text chat
<!-- key: 19.text-chat -->
Press Enter to talk (P24 of the overview). Chat also shows players joining and leaving and admin notices; on public
servers a player can mute or hide someone. The message about others' property pops up on screen when someone tries to
take what isn't theirs (as decided), and is noted in chat too.

**Lenses:** Already covered? — nothing today. Every reference game has chat.

### P9. Fights between players
<!-- key: 19.fights-between-players -->
As decided, fights between players happen only where a server allows them.
- **The server setting has three values**: off (the default), each player chooses, or everyone always — for rough
  public servers that want it.
- **When players choose**, each has a switch in the menu, as in Terraria, with a few seconds' wait before it changes
  (so nobody can switch mid-fight to dodge or ambush), and a small mark by the name of anyone who has fights on.
- **A beaten player drops nothing the winner can take** and wakes at their bed, as after any faint — as in Terraria,
  where players killed by other players drop no coins — so fights can't be used to rob people.
- **No fights on private plots.**
- **Bugs as weapons**: where fights are off, the game refuses to release biting bugs right next to another player, so
  netting wasps and letting them go beside someone can't get round the switch.

**Lenses:** The owner's ruling — players against the world, fights only where allowed. Fairness — nobody is hurt or
robbed without choosing to fight. **Cost and risk:** a new kind of damage the server has to judge from where each
player says they are (lag can make a hit feel unfair); the switch, the wait and the mark; the release check; deciding
whether nets, smoke and sprays affect other players. Weapons are tuned against bugs first; player fights get their own
balance pass only if servers use them.

### P10. How the server review is done
<!-- key: 19.server-review-done -->
The review is decided (D58); this is how to run it.
- **Start from a full list of the server's jobs, taken from the code** — every message it handles, every job it runs
  each tick, each bug group's decisions, every remote call — so nothing escapes. The biggest job on it is running the
  bugs as groups (As built).
- **Ask of each job**:
  - does it need one referee — money, items, trades and saves, where two players grabbing the same thing need one
    answer?
  - does it produce items? A crop has to be known ripe before the harvest is handed out, so moving it means the
    server keeps a checked copy;
  - does a frozen zone's catch-up need it? The catch-up runs on the server before anyone's computer is running the
    zone, so anything that moves off the server still needs a server copy that agrees exactly;
  - what would it cost the slowest player's computer, and how much would it add to what a late joiner downloads?
  - could it give players new ways to fall out of step, and what does the server trust from players' computers today?
- **The boundary stays**: each bug's own behaviour runs on the players' computers.
- **Each job gets a written verdict** with the evidence and the tests that prove players stay in step, before anything
  moves. The review has its own investigation document, and its findings come back here.
- **It comes first**: before the frozen zones' catch-up, the border events and bugs crossing between zones are built,
  since all of them depend on what the server runs.

**Lenses:** The owner's direction — every server-side job justified, in an area that breaks easily. What
can go wrong — a job moved without the in-step tests passing breaks the shared world, so the tests come first.

## Questions
### Q1. Which computers at launch?
<!-- key: 19.computers-launch -->
Everyone who plays together must simulate the bugs identically, so every platform we support has to pass the
same-bugs tests against the others. The Steam Deck runs the Windows version, so it needs a Steam release, full
controller play (P24 of the overview) and Valve's check — not a separate build.
- **A.** Windows at launch; the Steam Deck, Mac and Linux after. The dedicated server runs on Windows and Linux from
  day one either way.
- **B.** Windows and the Steam Deck at launch; Mac and Linux after.
- **C.** Windows, Mac and Linux at launch.

**Recommendation: A.** One game build to test keeps launch focused. The Steam Deck depends on the Steam decision and
on full controller play, and Mac and Linux each need their own round of same-bugs testing — all safer after launch.

### Q2. Does a world pause when you play alone?
<!-- key: 19.world-pause-play-alone -->
The shared world never pauses, and it stops only when nobody is online. With one player in Single Player, the world
could pause while they're in a menu, as Stardew Valley's and Terraria's single-player games do.
- **A.** Yes — in Single Player the world pauses whenever the only player opens the menu.
- **B.** No — the world keeps running, as it does for everyone else.

**Recommendation: A.** It costs nothing in a world with one player, and it's what players of both reference games
expect.

## Sources
- Your answers, 2026-09-26 to 2026-09-28 — restated above; `docs/product/ROADMAP.md` (the owner-decision table);
  `docs/product/economy/DECISIONS.md` D41, D44, D50, D54, D55, D57, D58, D61, D67; `docs/gdd/overview.md` part 18.
- `docs/product/design/requirements.md` §2–3 (worlds, moderation, placement rules — December 2025).
- `docs/product/design/game_design.md` §5.3, §10 (January 2026 design).
- `docs/product/architecture/architecture_persistence.md`; `docs/product/architecture/architecture_swarm_sync.md` §0
  and its correction to §1; `nakama/modules/world/world_save.go`, `save_versions.go`, `character_persist.go`,
  `handlers_home.go`, `handlers_bugs.go` (releasing bugs), `predation.go`, `state.go` and `match.go` (the 100-player
  limit, private worlds, the group-level bug decisions, the character saves), `messages.go` (the unused chat slot);
  `nakama/modules/rpc/character.go`; `BugFarmerClient/Assets/Scripts/Networking/NetworkManager.cs` line 61.
- Bandwidth: measured from the server's performance logs of a `village_21_B` run (bug simulation only).
- `docs/product/investigations/deep_research_2026-07/combat/04_player_combat_and_bosses.md` (no friendly fire by
  default).
- How other games do it: Terraria — [Server](https://terraria.wiki.gg/wiki/Server),
  [Multiplayer](https://terraria.wiki.gg/wiki/Multiplayer) (the fight switch's wait, no coins dropped to other
  players, teams), [Character](https://terraria.wiki.gg/wiki/Character); server-kept characters —
  [TShock](https://tshock.readme.io/docs/server-side-character-config); Necesse's characters —
  [article](https://www.savingcontent.com/2023/12/11/necesse-update-divorces-players-from-worlds-to-be-married-to-the-game-through-the-necesseverse/),
  [developer note](https://steamcommunity.com/app/1169040/discussions/0/4027970580228347979/); Minecraft —
  [player data](https://minecraft.wiki/w/Player.dat_format); Valheim — [FAQ](https://valheim.com/support/valheim-1-0-faq/).
- Connections: Epic's service — [EOS plugin for Unity](https://github.com/EOS-Contrib/eos_plugin_for_unity),
  [relay notes](https://docs.coherence.io/hosting/client-hosting/implementing-client-hosting/epic-online-services-eos-relay);
  home routers — [PAM 2012 study](https://www.icir.org/christian/publications/2012-pam-upnp.pdf); Steam —
  [networking](https://partner.steamgames.com/doc/features/multiplayer/networking).
