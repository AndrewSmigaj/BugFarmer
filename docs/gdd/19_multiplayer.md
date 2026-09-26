# §19 · Multiplayer & hosting
<!-- gdd: id=19 status=review updated=2026-09-26 -->

## The experience
It works like Terraria. From the main menu you play alone, **host** a world your friends join, or **join** someone
else's. Anyone can also run a world on a separate server program so it stays up all the time — that is how we will
run our own public world too, as one server among many. Everyone in a zone sees exactly the same bugs doing exactly
the same things. Your character belongs to the world you made it in, unless the host lets characters from other
worlds in.

## Decided
- **Like Terraria** — *"not sure what you mean, it should be like terraria."* · *"It should be like terraria."*
  (2026-09-26)
- **Our server is just another server** — *"We have no idea how many people can get on a server, our own server will
  not be part of the game itself just our own server people would be able to join just like any other players
  server. We would cap based on what is a feasible cap like the minecraft servers do."* (2026-09-26)
- **Joining** — typing an address plus Epic's free relay first, Steam later: you chose that option with *"I already
  answered this"* (2026-09-26).
- **Characters** — per world, plus a host setting that lets in characters from other worlds: *"Necesse's is fine"*
  (2026-09-26). Earlier: *"I think on each server, but we will have to think about this based on what players would
  like."*
- **Empty zones** — *"as already designed frozen with aggregation upon first access with random border crossing
  events."* (2026-09-26)
- **Shared-world rules** — *"the world is chaotic and anything goes (except stealing citizens stuff or destroying
  their houses, a message will pop up saying its basically not nice)"* (2026-09-26)

## Current design
- **Many separate worlds, each moderated by its own owner** — from the December 2025 requirements: a world has an
  owner and admins who can kick and ban; access can be public, private or invite-only; inside a world anyone can
  place or break blocks (no land claims — safe land comes from City Hall's private plots). (`requirements.md` §2–3)
- **Light anti-cheat** — *"No heavy anti-cheat or strict authority model (player-hosted servers)"* (GDD §5.3). The
  server still checks what matters: coins, inventory, catches, damage.
- **Zones run separately.** Each zone is its own running game on the server; walking off an edge moves you into the
  next one. A zone with nobody in it pauses and catches up when someone arrives (§01).
- **The world saves as it is** — each zone saves whole (bugs, farms, buildings, the clock) every 10 minutes, when it
  empties, and on shutdown, and time carries on after a restart. (`architecture_persistence.md`)

## As built
- The game talks to **Nakama**, a free open-source game-server program, set up on this PC the way developers run
  it. That's fine for building the game, but no player can be asked to set it up, and the game only looks for a
  server on this same PC (`NetworkManager.cs`, line 61).
- **Characters are already per server:** an account can have several; a character carries its coins, inventory,
  equipment and known recipes; only the server can change coins and inventory (`character_persist.go`).
- **Worlds save and restore** zone by zone (`world_save.go`). **New today:** an old save is upgraded when the game
  updates (the original copy is kept), and a save from a newer version is refused instead of being overwritten —
  for worlds and characters alike.
- **Everyone sees the same bugs:** today's two-player tests pass — standing together, all 76,447 bug checks
  matched; standing at opposite ends of the zone, all 77,737 matched.
- **Limits that exist:** a fixed 100 players per zone ("world is full" past that), and a "private" world only its
  owner can enter (`match.go`). Neither is a host setting yet.
- **Not built yet:** Host & Play, Join, a world-list screen, passwords, kick and ban, chat (a message type is
  reserved but nothing uses it), reconnecting, a version check.

## How it will work
This part is engineering, researched this week (sources at the bottom). It is here so you can see the plan; the
choices you can change are the proposals below.
- **A small server program of our own** that speaks exactly the same language as today's Nakama server, so the game
  and every test tool stay unchanged. The game starts it in the background for Host & Play, and it ships
  separately as the dedicated server. Nakama stays as a fallback. The proof: the tests that check every player sees
  the same bugs must give identical results on both.
- **Traffic is small.** Measured: the bug simulation sends about 2 KB per second per player in a busy zone (bursts
  around 7 KB/s). Player movement, map data and the one-off download when you enter a zone come on top and still
  need measuring; eight players should stay well within a home connection's upload.
- **Getting through home routers:** the game first asks the host's router to open the way automatically (UPnP);
  only some routers allow that (a 2011 study found about a third answered). When it fails, friends use a join code
  instead, and the connection goes through Epic's free relay — Epic's servers pass the game's traffic between you
  and your friends, and it works for any store. Steam's version comes later, if the game goes on Steam.

## Proposals
### P1. Three buttons, one kind of world
The main menu has **Single Player**, **Host & Play** and **Join**. Single Player is Host & Play with nobody else
allowed in — the same program underneath, so there is one set of bugs to fix, and any world can be opened to friends
later, as in Terraria. When the host quits, the world closes for everyone (as in Terraria); a dedicated server keeps
it running.

**Lenses:** Simpler alternative — one way of running a world, not two. Your "like terraria".

### P2. Join with an address or a short code
Friends type your address, which works when your router lets the game through, or a short **join code** you read
out to them, which always works because it goes through Epic's relay. A "recent servers" list remembers where
you've played.

**Lenses:** Picture the moment — a friend on a call: "the code is BUGS-4471". Already covered? — an address alone
only works when the host's router lets the game through.

### P3. The player limit is a host setting, measured before launch
Each world gets a **max players** setting (default 8 until measured). Before launch we measure the real ceiling —
the host's computer, their upload speed, and the slowest player's computer, since every player's computer simulates
the bugs in their zone — and print it next to the setting. For comparison: Terraria's server defaults to 16 (8
before 2020); Valheim, which also simulates on players' computers, caps at 10.

**Lenses:** Your *"cap based on what is a feasible cap"*. Scale — measured, not guessed.

### P4. A settings file and admin commands, like Minecraft and Terraria
The dedicated server reads one plain settings file: world name, password, max players, the network port (the
number the game listens on), allow characters from other worlds, players hurting each other (Q1), how often it
autosaves, how many backups to keep, and a welcome message. Admins get chat commands: kick, ban, unban, an
allow-list (only named players may join), save, and shut down.

**Lenses:** Built on what's already designed — the December requirements ask for kick, ban and access control.
Already covered? — standard in both reference games.

### P5. Automatic backups
Saves already upgrade safely when the game updates (built today). Still to build: the server keeps backups of every
world — for example the last 5, plus one a day for a week — and can restore one with a command.

**Lenses:** What can go wrong — a bad update, a crash mid-save, a griefer. Pillar 8, fair to your time.

### P6. A plain version check
If your game and the server are different versions, you are told plainly — *"This server runs 1.2; you have 1.1.
Update to join."* — instead of a confusing failure.

**Lenses:** What can go wrong. Picture the moment.

### P7. Drop back in after a disconnect
If your connection drops, rejoining puts you back where you were, with the bugs exactly in step — the same catch-up
that already lets a player walk into a busy zone mid-game and see every bug where it should be.

**Lenses:** What can go wrong. Built on something already proven.

### P8. Text chat
Press Enter to talk. Chat also shows players joining and leaving and admin notices. The "not nice" message pops up
on screen when someone tries to take a citizen's things (your words: *"a message will pop up"*), and is noted in
chat too.

**Lenses:** Already covered? — nothing today. Every reference game has chat.

## Questions
### Q1. Can players hurt each other?
Your rule makes the shared world chaotic — players can break and take each other's things there (never citizens').
Fighting each other is the open part. It costs real work: player-to-player damage, balancing weapons against
players (they're tuned against bugs), and deciding what you drop when another player kills you (§17). The July
combat research recommended no friendly fire by default, with an opt-in left open.
- **A.** Never — the chaos is about the world, not fights between players.
- **B.** Only when both players switch it on (Terraria's PvP toggle).
- **C.** The host decides in the server settings: off, both-players-opt-in, or always on. The default is opt-in, so
  nobody can hurt you unless you switch it on.

**Recommendation: C.** One setting lets a friendly co-op world and a rougher public world both exist, the way
Minecraft servers work; the default behaves like Terraria and keeps the research's "no friendly fire unless you
choose it".

### Q2. Which computers at launch?
Everyone who plays together must simulate the bugs identically, so every platform we support has to pass the
same-bugs tests against the others.
- **A.** Windows at launch; Mac, Linux and the Steam Deck after. The dedicated server runs on Windows and Linux from
  day one either way.
- **B.** Windows and Linux at launch (the Steam Deck also needs a Steam release and controller support — §20).
- **C.** Windows, Mac and Linux at launch.

**Recommendation: A.** One game build to test keeps launch focused. The Steam Deck depends on the Steam decision
and on controller support, and Mac needs its own round of same-bugs testing — both are safer after launch.

## Sources
- Your answers, 2026-09-26 (this session) — quoted above.
- `docs/product/design/requirements.md` §2–3 (worlds, moderation, placement rules — December 2025).
- `docs/product/design/game_design.md` §5.3, §10 (January 2026 GDD).
- `docs/product/architecture/architecture_persistence.md`; `nakama/modules/world/world_save.go`,
  `save_versions.go`, `character_persist.go`, `match.go` (the 100-player limit, private worlds), `messages.go` (the
  unused chat message type); `BugFarmerClient/Assets/Scripts/Networking/NetworkManager.cs` line 61.
- Bandwidth: measured from the server's performance logs of a `village_21_B` run (bug simulation only).
- `docs/product/investigations/deep_research_2026-07/combat/04_player_combat_and_bosses.md` (no friendly fire by
  default).
- How other games do it: Terraria — [Server](https://terraria.wiki.gg/wiki/Server),
  [Character](https://terraria.wiki.gg/wiki/Character); Necesse's character change —
  [article](https://www.savingcontent.com/2023/12/11/necesse-update-divorces-players-from-worlds-to-be-married-to-the-game-through-the-necesseverse/),
  [developer note](https://steamcommunity.com/app/1169040/discussions/0/4027970580228347979/); Minecraft —
  [player data](https://minecraft.wiki/w/Player.dat_format); Valheim — [FAQ](https://valheim.com/support/valheim-1-0-faq/).
- Connections: Epic relay — [EOS plugin for Unity](https://github.com/EOS-Contrib/eos_plugin_for_unity),
  [relay notes](https://docs.coherence.io/hosting/client-hosting/implementing-client-hosting/epic-online-services-eos-relay);
  home routers and automatic setup — [PAM 2012 study](https://www.icir.org/christian/publications/2012-pam-upnp.pdf);
  Steam — [networking](https://partner.steamgames.com/doc/features/multiplayer/networking).
