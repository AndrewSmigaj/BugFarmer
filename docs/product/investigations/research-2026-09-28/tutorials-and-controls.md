# Research: tutorial chains, controls and settings (2026-09-28)

Status: research complete, not yet reviewed by a second agent (see section 4). Feeds GDD §20 (UI, onboarding and
tutorials) and §16 (NPCs). The owner has left tutorials, controls and settings to the assistant's design (D59,
2026-09-28); this document is the evidence and the recommendation behind that design, for the owner to see.

**In short.** Tutorials: one lesson system with three ways in (on joining, from townspeople, on first meeting a thing
or place), every lesson written down in a Journal the player can reread, progress kept per character. The first
village chain is twelve short steps, starting at the Mayor, fanning out to the Bug Dealer, Marjoram and Wynn in any
order, then on to the Ecologist and his monitoring station and to the blacksmith and the first mine (section 3.1).
Controls: the genre's standard (W A S D, left to use, right to interact, 1 to 0 and the wheel, M for the map) plus E
to interact without aiming, Tab for the bag, Q to heal, G to drop, R for tool modes, Space to dodge; the wheel always
walks the hotbar, and the shovel's modes move to R (section 3.2). Everything rebindable, with a grouped settings list.

What was asked, restated: tutorials matter and should be done well. Most games teach the same basics. Some lessons
come from townspeople as the first quests, some open when a player joins, some open when a player reaches a new
place, and many should end with a task that leads to the next lesson (for example, returning to a townsperson who
then points to another townsperson). We choose the design on taste and good game design. Separately: what the
controls and the settings menu of a PC 2D top-down multiplayer sandbox should be.

## What the game does today (read from the code, 2026-09-28)
The client (Unity 6000.2.9f1) reads the keyboard and mouse through Unity's old input API (`Input.GetKey`,
`Input.GetAxis`) with every key written into the code, so nothing can be rebound today. The newer Input System
package (1.14.2) is installed and the project runs both systems at once (`activeInputHandler: 2` in
`ProjectSettings/ProjectSettings.asset`), but no script uses it; `Assets/InputSystem_Actions.inputactions` is
Unity's unused template file. There is no settings menu at all. There are no tutorials or quests.

The keys in use now:
- Walk: W A S D or the arrow keys (the old "Horizontal"/"Vertical" axes in `ProjectSettings/InputManager.asset`;
  a gamepad's left stick also feeds these axes, and nothing else on a gamepad does anything).
- Dodge: Space (`Player/PlayerController.cs:52`, `dodgeKey = KeyCode.Space`).
- Left mouse: use whatever is held; what happens depends on the held tool; holding it keeps breaking
  (`Player/PlayerInputRouter.cs`, `RouteLeftClick`). With the shovel, Shift + left mouse digs (P12 removes this).
- Right mouse: "interact", tried in order: put down one bug from the cursor, open a station or storage, open a shop,
  read a sign, open a mannequin, use a bed, place the held placeable, else the weapon's second move
  (`PlayerInputRouter.cs`, `RouteRightClick`).
- E: pick up the nearest item (`Player/PickupController.cs:61`); walking over items also pulls them in.
- R: turn the thing being placed (`Player/PlacementController.cs:64`).
- I: inventory (`UI/InventoryPanel.cs:215`). B: the shovel's ground panel (`UI/ShovelBuilderPanel.cs:110`; P12 removes it).
- 1 to 0: hotbar slots. Mouse wheel: steps through the hotbar, except that while the shovel is held the shovel
  takes the wheel (`UI/HotbarUI.cs:110-130`, "The shaped-ground builder owns the wheel while a shovel is
  equipped"). So today, with the shovel in hand, the wheel cannot move you off the shovel; only the number keys can.
  This is the wheel conflict the brief asks about, and it already exists in the code.
- Escape: closes whichever panel is open. F1 to F10: developer tools (debug overlay, day/night preview, outfits).

## 1. Source table
"Deep" means the whole page was read with a fetch, not a search snippet. "Fits" judges the technique against our
constraints: no storyline and the player sets their own goals; multiplayer with each player's own progress and
players who join late; lessons that can be read again; the cost to build.

| # | Source | Read | Concrete technique | Fits us? |
|---|---|---|---|---|
| 1 | Stardew Valley wiki, Quests — https://stardewvalleywiki.com/Quests | deep | The opening is a set of small story quests, each teaching one system and ending in a small reward: Introductions (greet townspeople) leads to How To Win Friends (give a gift); Getting Started (plant, water and harvest a parsnip, from the seed package in the house) opens Raising Animals, Advancement (reach Farming 1 and craft a scarecrow) and Archaeology (donate to the museum). Letters bring the rest on set days or after an event: Willy's letter on day 2 gives the fishing rod at the beach; the morning after the first copper ore, a letter asks for a furnace (Forging Ahead) then a bar (Smelting); the morning after mine level 5, a letter opens the Adventurer's Guild (Initiation: slay 10 slimes). Story quests never expire and can be dropped with no penalty. A Help Wanted board posts one small two-day job each day (deliver an item, gather, slay, fish). The quest log is on a key (F) and shows progress. | Strong fit. Each step is one short verb-task with a reward, and several steps are triggered by what the player did (first copper ore, reaching mine level 5), not by a script. That is the "unlock as you go" shape the owner wants. The daily board is a good later layer. |
| 2 | Stardew Valley wiki, Multiplayer — https://stardewvalleywiki.com/Multiplayer | deep | "Quest progress is largely kept on an individual level, though players can help each other with quests." Mine progress and the museum are shared, but each player gets their own museum rewards; tools and skills are per player. | Fits: the model for us is per-player lesson progress in a shared world. The page does not say what a late-joining farmhand receives; see the "not sure" list. |
| 3 | Stardew Valley wiki, Television — https://stardewvalleywiki.com/Television | deep | "Livin' Off The Land" airs twice a week with tips on farming, fishing, foraging and town life, and re-runs on a two-year cycle; the Queen of Sauce teaches a recipe each Sunday. An in-world, optional, repeatable place to get tips. | Partly: an in-world tips source fits the setting (a 2126 radio or bulletin board), but tips that air on set days are not re-readable on demand. |
| 4 | Pixelated Playgrounds, "Game Design Perspective: Stardew Valley" — https://www.pixelatedplaygrounds.com/sidequests/game-design-perspective-stardew-valley | deep (short) | The Community Center bundles "provide the player with a sense of direction in a game that otherwise has few explicit long-term goals"; systems overlap so every activity helps another. | Fits: long optional goal lists give direction without a story. Our equivalent could be the Ecologist's tab and the townspeople's quest boards. |
| 5 | Terraria wiki, Guide — https://terraria.wiki.gg/wiki/Guide | deep | The Guide stands next to the player at world start. "Help" cycles through advice chosen by the player's progress (early: "use your pickaxe to dig through dirt"; later: which boss or area is next, what brings each townsperson). "Crafting": show him any item and he lists every recipe that uses it and the station needed. Version 1.4.0.1 "massively overhauled the Guide's help dialogue, adding hints and tips for content all the way up to the Lunar Events." | Fits well as a re-readable, progress-aware hint source that works for any player at any time, in any multiplayer world. The recipe lookup is the part to copy. Weakness: it is passive; you have to think to ask him. |
| 6 | Wikipedia, Terraria — https://en.wikipedia.org/wiki/Terraria | deep (targeted) | Reviewers criticised the lack of a tutorial on PC, while the console versions' tutorial world was praised; a 2018 study by Ji Soo Lim found that "the participants had to rely on a wiki to learn more about the game." | A warning: a hint NPC alone did not stop players leaving the game for a wiki. Recipes and "what is this for" must be answerable in the game. Our decided examine view (item and recipe details with real biology) is exactly this. |
| 7 | Gamers.Wiki, "Every Hugin Hint in Valheim" — https://gamers.wiki/en/games/valheim/guides/every-hugin-hint-in-valheim-and-the-ten-worth-stopping-for | deep | Valheim's raven Hugin is triggered by changes in the player's state ("you picked up ore, you crafted a hammer, you crossed into the Black Forest, you died"); "he materialises beside you and keeps coming back until you stop and read him." A settings switch turns the raven off; only the hints stop, while runestones and item descriptions keep working. | Strong fit for "unlocks when you first meet a thing or reach a new area". The in-world messenger suits co-op because each player sees their own. The "keeps coming back" nag is the part to soften. |
| 8 | Inven Global, Valheim beginner's guide — https://www.invenglobal.com/articles/13389/valheim-guide-beginners-tips-tricks-basics | deep | Hugin's past tips can be re-read: press Tab and click the raven icon (the "Valheim Compendium"). | Fits: the re-readable log is what keeps contextual tips from being lost when a player clicks through them in a fight. |
| 9 | Palia wiki, Learning the Ropes — https://palia.wiki.gg/wiki/Learning_the_Ropes | deep | After "Welcome to Palia", Ashura's quest sends the player to five townspeople "in any order": Auni (bug catching) hands over a starter belt, smoke bombs, a recipe and the quest "Bug Catching 101"; Einar gives a rod and "Fishing 101"; Hassian a bow, arrows, the arrow recipe and "Hunting 101"; Badruu a hoe, watering can, seeds and "Gardening 101"; Reth the campfire recipe and "Cooking 101". Then it walks through placing a garden plot, tilling, planting and watering, placing a campfire, foraging and cooking. | The closest match to the owner's picture: one hub quest fans out to each townsperson, who teaches their own trade and hands over the tool for it. Letting the player visit them in any order respects "set your own goals". Palia is an online game with per-player quests, so the shape is proven in multiplayer. |
| 10 | Palia wiki, Bug Catching 101 — https://palia.wiki.gg/wiki/Bug_Catching_101 | deep | A skill's first quest is one tiny task and a return: catch one of two named bugs (a day butterfly or a night moth, so either time of day works) then "Return to Auni", who praises the catch and gives a small reward, friendship and renown. | Fits: "catch one bug and bring it back" is exactly our first catching lesson, and offering a day bug or a night bug means a player who joins at night is not stuck. |
| 11 | DigitalTQ, Dinkum walkthrough part 1 — https://www.digitaltq.com/dinkum-new-game-walkthrough-part-1 | deep | Day 1 is a short list of placement jobs from Fletch, the town manager: place the base tent, then your own tent, then the visitors' site; talking to Fletch in the base tent gives the Adventure Journal ("keep track of your Island's Progress"), and Fletch's last talk of the day hands over a bug net, a sleeping bag and the campfire recipe. The clock does not start until the journal is given. | Fits: the first tools come from a person as part of a conversation, and the first night waits until the basics are done. We cannot stop the clock (the world is shared), so we take the hand-over, not the frozen time. |
| 12 | DigitalTQ, Dinkum walkthrough part 2 — https://www.digitaltq.com/dinkum-john-permanent-residence-walkthrough-part-2 | deep | The next goal is to make the travelling trader John stay: buy from his stall, do his two small daily requests, then buy his shop deed from Fletch and bring the building materials (planks from the table saw, tin sheets, nails). Each step quietly teaches a system: buying, daily requests, deeds, the saw, delivering materials. When he moves in he sells new things, which points to the next resident. | Fits the owner's "end with a task that leads to the next person" shape exactly: one townsperson's chain ends by introducing another. The deed and building parts do not fit our village, whose shops already exist. |
| 13 | Necesse beginner's guide (deilru) — https://deilru.com/necesse-tutorial-guide/ | deep | Six on-screen steps in the top-left, one at a time: "Chop a tree and craft a torch", "Talk to the Elder", "Craft a Wood Pickaxe at the Workstation", "Go underground and mine ore", "Place the settlement flag and open the settlement menu", "Talk to the Elder to accept the boss quest". Accepting the boss quest ends the tutorial and hands over to the Elder's quests. | Fits as the lightweight "on joining" layer: a short fixed checklist that ends at a person. Six steps is the right size. |
| 14 | Necesse wiki, Getting Started — https://necessewiki.com/Guide:Getting_Started | deep | The player starts with a wood axe, a wood sword and a "Crafting Guide" item; "The Elder is your game guide and quests giver"; quests from him need a settlement flag first. | Fits: a guide item you always carry is a cheap re-readable reference. Our equivalent is a journal page, not an item that takes a slot. |
| 15 | Minecraft wiki, Tutorial hints — https://minecraft.wiki/w/Tutorial_hints | deep | Java Edition shows a chain of corner pop-ups in a new survival world: move, look around, find a tree, hold Mine until a log breaks, open the inventory, craft planks ("The recipe book can help"), and in multiplayer a social-menu hint. Each shows a progress bar; the hint text names the player's own bound key. Progress is kept per device, not per world ("tutorialStep" in options.txt). Bedrock shows each tip up to three times, picks tips for mouse, touch or controller, and lets the player reset or turn them off in settings. | Fits for the "on joining" controls layer. Two details to copy: show the player's own key (it changes if they rebind), and pick the tip by input device. Keep progress per player, stored with the character, so it follows them to any server. |
| 16 | Minecraft wiki, Recipe book — https://minecraft.wiki/w/Recipe_book | deep | Recipes unlock by meeting a condition, usually holding an ingredient ("iron ingots unlock iron tool recipes"; boats unlock by touching water); a corner pop-up announces them; a toggle shows only what you can make now; a search box; clicking a recipe fills the grid. | Fits: "you picked up X, here is what X makes" is a gentle way to reveal crafting, and it pairs with our decided examine view. |
| 17 | Minecraft wiki, Advancement — https://minecraft.wiki/w/Advancement | deep | Advancements are "a way to gradually guide new players into Minecraft and give them challenges to complete". A tree per theme; the screen reveals "up to two advancements being displayed ahead of an unlocked one"; each can be done out of order. | Fits "set your own goals": a visible map of optional next steps, with a little of the road ahead shown and the rest left to discover. |
| 18 | Celia Hodent, "The Gamer's Brain, Part 2: UX of Onboarding and Player Engagement" (GDC 2016, her write-up) — https://celiahodent.com/gamers-brain-ux-onboarding/ (video: https://www.gdcvault.com/play/1023231/The-Gamer-s-Brain-Part) | deep | Learning by doing beats being told. "When you teach the player something when they can actually do it, it gives context", and giving it a purpose makes it stick. At most three new things at once: "Don't explain more than 3 things and focus on the why (main goals) rather than the how or the what." Reminders work better spaced out and in a new context. Three kinds of forgetting need three fixes; for "recall" failures, give reminders and hints (Fortnite pins a chosen recipe on screen). Do not punish players while they learn. "Show the locks before giving the keys." | The core rules for our chain: one verb per step, taught at the moment the player can do it, with a reason. Pinning a recipe or a lesson on screen is a cheap way to make lessons re-readable. |
| 19 | Ernest Adams, "The Designer's Notebook: Eight Ways To Make a Bad Tutorial" — https://www.gamedeveloper.com/design/the-designer-s-notebook-eight-ways-to-make-a-bad-tutorial | deep | The eight failures: forcing returning players to repeat it; screen after screen of text; naming buttons vaguely; stopping the guidance halfway; punishing mistakes; a condescending tone; not letting players skip; and having no tutorial at all ("truly intuitive interfaces don't exist"). Fixes: learning by doing, highlight the real button, allow instant retry, let players leave or turn teaching off. | Fits and sets the "must not" list. For us: a second character or a veteran on a new server must be able to skip; every key named must be the player's real binding; a lesson can never be failed. |
| 20 | Game Accessibility Guidelines, full list — https://gameaccessibilityguidelines.com/full-list/ | deep | Basic: "Allow controls to be remapped / reconfigured"; "Ensure controls are as simple as possible"; "Include an option to adjust the sensitivity of controls"; "Ensure that all areas of the user interface can be accessed using the same input method as the gameplay"; "Allow players to progress through text prompts at their own pace"; "Include interactive tutorials"; "Use an easily readable default font size"; "Ensure no essential information is conveyed by a fixed colour alone"; "Ensure no essential information is conveyed by sounds alone"; "Provide separate volume controls or mutes for effects, speech and background / music"; "Ensure that all settings are saved/remembered"; "Avoid flickering images and repetitive patterns". Intermediate: "Avoid / provide alternatives to requiring buttons to be held down"; "Avoid repeated inputs (button-mashing/quick time events)"; "Indicate / allow reminder of controls during gameplay"; "Indicate / allow reminder of current objectives during gameplay"; "Include contextual in-game help / guidance / tips"; "Allow interfaces to be resized"; "Provide captions or visuals for significant background sounds"; "Include a means of practicing without failure"; "Provide an option to turn off / hide background movement"; "Support more than one input device"; for PC, "support windowed mode". Advanced: "Allow all narrative and instructions to be replayed"; "Allow the font size to be adjusted". | This is the checklist the settings list is built from. The tutorial rules are there too: interactive, own pace, reminders of controls and objectives, replayable instructions. |
| 21 | Xbox Accessibility Guideline 107, Input — https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/107 | deep | "Players should be given the option to remap all of the controls within the game itself ... and the Esc key on PC games", ideally assigning an action to any input rather than just swapping two buttons. "When a player remaps a control within the game, the labelling of the new mapping is represented correctly across any hints, tips, tutorials, or controller map schemes." Avoid long holds, rapid repeated presses and pressing two buttons at once; where they cannot be avoided, give a less demanding alternative (The Long Dark's "accessible interactions" turns every press-and-hold into a press). With a keyboard, a player must be able to start, change settings, play and quit using the keyboard alone. Sensitivity must be adjustable by at least 50% up or down. Menus should work with single digital presses and act on release, not on press. | Fits and has direct consequences: our hold-to-break needs a toggle alternative; Shift + click to dig needs two keys at once (P12 already removes it); every tutorial text must print the player's current binding. |
| 22 | Steamworks, Steam Deck compatibility review — https://partner.steamgames.com/doc/steamdeck/compat | deep | Verified needs: "The default controller configuration must provide users with the ability to access all content", without changing in-game settings; glyphs that match the controller in use and never show keyboard glyphs; text entry through the Steam on-screen keyboard API or the game's own controller-driven text entry; a resolution the Deck supports (1280x800 or 1280x720); "the smallest on-screen font character should never fall below 9 pixels in height at 1280x800"; a default setting that runs at 30 fps at 800p; no "unsupported device" warnings; launchers must also work with a controller. "Playable" means it works but needs the user to do some setup. | Sets the bar if we want Verified: full gamepad play, pad glyphs, controller text entry for character names and chat, and a UI that stays readable at 1280x800. A mouse-only design would at best be "Playable". |
| 23 | Terraria wiki, Controls — https://terraria.wiki.gg/wiki/Controls | deep | Defaults: W A S D (or arrows) to move, Space to jump, left mouse to use, right mouse to interact, E grapple, Esc inventory, 1 to 0 and the mouse wheel for the hotbar, M map, H quick heal, J quick mana, B quick buff, R quick mount, hold Left Shift for auto-select (picks the right tool for what is under the cursor), Left Ctrl toggles Smart Cursor, Enter chat, X lock-on, + and - zoom. Item actions on the inventory are fixed: Alt-click favourites, Ctrl-click trashes, Shift-click quick-stacks. "Throw" (drop the held item on the ground) is listed as unbound by default. On a gamepad: left stick moves, right stick aims, right trigger uses, left trigger jumps, B interacts, Y inventory, the bumpers step through the hotbar, pressing the right stick toggles Smart Cursor, and a lock-on button targets enemies. Keys are changed in the settings. | Fits: this is the base of the genre's layout (left use, right interact, W A S D, number keys and wheel, M map, H heal, Enter chat). Our game has no jump, which frees Space for the dodge we already use. |
| 24 | Terraria wiki, Settings — https://terraria.wiki.gg/wiki/Settings | deep | General: autosave, autopause, pause when unfocused, smart doors, and "Autofire" (keep swinging while held, for every weapon). Interface: pickup text, placement preview, highlight new items, tile grid, gamepad instructions, hover text boxes. Video: fullscreen, resolution, borderless window, parallax, frame skip, lighting mode, quality, "Blood and Gore", "Miner's Wobble", storm, sunlight, heat distortion, waves, "Screen Shake" and "Thunder Effects" (the lightning flash) as separate switches. Volume: music, sound, ambient. Cursor: colour and border colour, Smart Cursor as toggle or hold, which tool Smart Cursor prefers, lock-on priority. Keybindings menu. 12 languages. | Fits: a good model for small, specific comfort switches (shake, flashes, distortion each on their own). The cursor colour option matters for us because our cursor sits over busy grass. |
| 25 | Stardew Valley wiki, Controls — https://stardewvalleywiki.com/Controls | deep | Defaults: W A S D, left click or C to use a tool, right click or X to "check / do action", Esc or E for the menu, F journal, M map, T chat, Left Shift run, Y emotes, Tab swaps the toolbar row, the wheel steps through items, 1 to 0, minus and equals pick slots. "All hotkeys can be reassigned" in the Options tab, but "Controller buttons can not be reassigned". Gamepad: A checks, X uses the tool, B menu, Y crafting, the triggers switch items and the bumpers switch toolbar rows. | Fits, with a gap to avoid: Stardew lets keys be rebound but not the pad, which XAG 107 counts as a failure. Its "use key also on a letter" (C and X as keyboard-only alternatives to the mouse) is a good accessibility touch. |
| 26 | Stardew Valley wiki, Options — https://stardewvalleywiki.com/Options | deep | General: auto-run, portraits, "Always Show Tool Hit Location", "Hide Tool Hit Location When Moving", gamepad mode (auto, on, off), controller placement tile indicator, controller-style menus (the cursor snaps between buttons), pause when the window is inactive, "Show Advanced Crafting Information". Sound: music, sound, ambient and footstep volumes, a choice of fishing-bite sound, dialogue typing sound, mute animal sounds. Graphics: windowed, fullscreen or borderless; resolution; VSync; UI scale 75 to 150%; zoom 75 to 200%; zoom buttons; "Show Flash Effects"; hardware cursor. Controls: rumble, invert toolbar scroll, reset to defaults, and one row per action. | Fits closely: separate UI scale and world zoom, a hit-location outline, and a switch for flashes are exactly right for a top-down grid game. Its settings are the best small model for ours. |
| 27 | Necesse wiki, Controls — https://necessewiki.com/Controls | deep | Defaults: W A S D; left mouse attacks, places or uses; right mouse interacts; E inventory; Q health potion; Z mana potion; B buff potions; R places a torch; 1 to 0 and the wheel for the hotbar; M map; C settlement; F mount; T emote wheel; Left Ctrl toggles "smart mining"; V armour-set ability; Space trinket ability. Eat food, loot all and sort are unbound by default. | Fits, and it is the closest top-down relative: same left use, right interact. It puts quick heal on Q (next to W A S D) rather than Terraria's H. |
| 28 | BisectHosting, Core Keeper controls — https://www.bisecthosting.com/blog/core-keeper-controls-pc-playstation-xbox-keyboard-mouse-gamepad | deep | Defaults: W A S D or arrows; left mouse attacks; right mouse "use"; E interacts; Tab inventory; R sorts; Q quick-stacks into a chest; Delete trashes; 1 to 0 and the wheel; M map (wheel zooms, middle mouse pings); hold Left Shift to swap to a torch for a moment; Enter chat. Gamepad: left stick moves, right stick aims, right trigger attacks, left trigger uses, bumpers step through items. | Partly: Core Keeper puts "interact" on E and a second "use" on right mouse. We borrow E for interacting with the nearest thing, because our right mouse is overloaded today (stations, shops, signs, beds, placing, a weapon's second move); right mouse stays "interact with what is under the cursor" and gives placing to the left button. |
| 29 | Xbox Accessibility Guideline 117, visual distractions and motion — https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/117 | deep | "Avoid the use of camera shake, camera bobbing effects, motion blur ... or provide an option to turn off these behaviors"; Halo Infinite sets blur, screen shake, full-screen effects and speed lines each on a 0 to 100% slider. Moving, blinking or flashing content behind text should be possible to pause, hide or turn off; an opaque plate behind in-game text helps. | Fits: screen shake (hits, stings, thunder), the lightning flash and moving background effects each get a 0 to 100% slider, not one switch. |
| 30 | Xbox Accessibility Guideline 104, subtitles and captions — https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/104 | deep | Captions cover all important sounds, not only speech, with arrows for direction when the source is off screen (Minecraft Java's sound subtitles such as "Minecart rolls" with a left or right arrow). Captions on by default or offered before any sound plays; each kind (speech, background talk, ambient sounds) switchable on its own; at most two lines of about 40 characters; a background plate with adjustable opacity; mixed case; a sans-serif choice; scalable to 200%. | Fits a bug game well: the buzz of an approaching wasp, a sting wind-up, thunder and a bug escaping a pen are exactly the "important sounds" a deaf or muted player would miss. Our townspeople do not speak aloud yet, so speech subtitles are cheap. |
| 31 | Xbox Accessibility Guideline 101, text display — https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/101 | deep | Minimum default text height on PC: "18 px at 1080p" and "36 px at 4K" (26 px at 1080p for console, measured from the lowest descender to the highest ascender). "Players should be able to resize text up to 200 percent of the minimum font sizes ... without the loss of content". Icons and button pictures scale with the text. At least one sans-serif option; lines no wider than about 80 characters; sentence case. Text over a busy scene gets an outline or plate. | Fits and sets numbers: our pixel font needs a body height of 18 px or more at 1080p by default (about 13 px at the Deck's 800p, above Valve's 9 px floor), and the UI scale must reach 200%. |
| 32 | Wikipedia, Great Plateau (The Legend of Zelda: Breath of the Wild) — https://en.wikipedia.org/wiki/Great_Plateau | deep | The opening area is a closed-off plateau (you cannot leave until you get the paraglider). The Old Man's few lines "can be ignored without much detriment"; four shrines, each teaching one ability, can be done in any order ("How the player goes about completing the objectives of the tutorial is up to choice"), and on the way the player also meets cooking, temperature, stamina and physics. Finishing all four earns the paraglider, which opens the world. Critics called it one of the best tutorials made. | Fits "set your own goals": a small set of lessons in free order, all visible, with one clear reward at the end that opens the next stage. We cannot wall off the village (the world is shared and open), so the reward, not a wall, has to carry it. |
| 33 | Satisfactory wiki, Tutorial — https://satisfactory.wiki.gg/wiki/Tutorial | deep | Tier 0 "Onboarding" is 11 steps: dismantle the drop pod, open the Codex, equip the weapon, scan and mine iron, build the HUB, then six HUB upgrades, each a delivery that unlocks the next buildings. The ship's voice announces each step and a to-do list tracks it. It "can be skipped entirely when starting a game", and in multiplayer "tutorial messages are shared. Only the host is required to complete the tutorial." | Partly: "each step is a delivery that unlocks the next thing" is the hand-off shape we want. The multiplayer rule is the one to avoid: a shared tutorial teaches nobody who joins later. |
| 34 | Stardew Valley Sprinkler, controller mechanics — https://stardewvalleysprinkler.com/post/a-deep-dive-into-controller-mechanics-in-stardew-valley-from-quick-deletes-to-quick-buys | deep (thin) | On a pad, Stardew has "Check/Do Action" and "Use Tool"; the right stick moves a cursor "to target a different tile or UI element", which "can auto-reset in some contexts" and is kept for awkward placement, furniture and bombs. The shoulder buttons step through the toolbar. | Partly: confirms the "act near the character, with an optional stick cursor" model for a grid game. The claim that tools default to the facing tile comes from a search snippet of a forum thread, not this page (see the "not sure" list). |
| 35 | ScrollToArms (Valheim mod), README and source — https://github.com/isimp/ScrollToArms | deep (code) | Valheim has our exact conflict: in build mode the wheel rotates the piece, so a player holding the hammer "gets stuck" on it. The mod keeps the plain wheel for the tool and adds "Hold Left Alt and scroll" to move along the hotbar, then shows what the wheel does right now next to the hotbar, for example "Wheel: rotate \| [Alt] + wheel: hotbar". Which tools keep the wheel is a setting. (The README says most of it was written with Claude Code; it is used here as a working example of the pattern, not as an authority.) | The pattern behind the runner-up W3 in section 3.2: the shovel keeps the plain wheel, a held modifier plus the wheel always walks the hotbar, and a small label says which is which. The recommendation (W1) goes further and gives the wheel back to the hotbar entirely; this mod is the evidence that the trap is real and felt by players. |
| 36 | Steamworks, Steam Deck recommendations — https://partner.steamgames.com/doc/steamdeck/recommendations | deep | The default controller configuration must reach all functionality; games that accept both mouse-style and stick-style pointing at once ("Mixed Input") work cleanly with the Deck's trackpads; games should open the on-screen keyboard themselves when text is needed (`ShowFloatingGamepadTextInput`, `ShowGamepadTextInput`); saves should move between Deck and PC through the cloud; put all needed functions in the game rather than a launcher. | Fits: our cursor-aimed actions should accept the stick-driven cursor and the trackpad at the same time, and chat and character naming must call up the Deck keyboard. |
| 37 | George Fan (PopCap), "How I Got My Mom to Play Through Plants vs. Zombies", GDC 2012, talk notes — https://notes.hamatti.org/sources/talks/how-i-got-my-mom-to-play-through-plants-vs.-zombies (video: https://www.gdcvault.com/play/1015541/How-I-Got-My-Mom) | deep (notes) | Ten rules: blend the tutorial into the game (the "Tutorial Chameleon"); doing over reading; spread new mechanics out; "just get the player to do it once"; about "eight words on the screen at any given time"; messages that do not interrupt and can be read when convenient; adaptive messages that appear only when a problem shows up ("One of your peashooters died! Try planting them further to the left!"); little UI noise; teach through visuals; lean on what players already know. | Fits and gives hard numbers for our text: one sentence, about eight words, per prompt. Adaptive help (only when the player is stuck or something went wrong) suits a no-story sandbox. |
| 38 | Game Developer, "The art of the tutorial: when to hold a player's hand, when to let it go" — https://www.gamedeveloper.com/design/the-art-of-the-tutorial-when-to-hold-a-player-s-hand-when-to-let-it-go | deep | Designers disagree on how much to hold hands. Brenda Romero: "the wider the audience, the younger the audience, the more gentle the ramp". Teddy Diefenbach: "Unlock inputs a button at a time, so that you're introduced to each play mechanic as you find need for it." Soren Johnson prefers "thorough in-game mouseover help—which means that everything must have pop-up help rather than a handholding tutorial." | Fits: our decided examine view (every item explains itself) is Johnson's approach and carries most of the teaching; the quest chain only has to carry the first steps. |
| 39 | Roblox Creator Hub, Onboarding techniques — https://create.roblox.com/docs/production/game-design/onboarding-techniques | deep | Three techniques: visual cues ("Visuals like arrows and particle effects communicate without words"); contextual, just-in-time tutorials "triggered by natural gameplay moments, such as entering new zones or acquiring new items"; timed hints that appear only if a player has not worked something out after a set time ("find a balance between displaying them so quickly that players feel they haven't gotten the chance to figure it out on their own, and waiting so long that they get frustrated"). | Fits: area-triggered and item-triggered lessons are the owner's "unlock on reaching a new area"; the timed hint is how a quest marker should appear (only after the player has had a chance to find the person). |
| 40 | Minecraft wiki, Controls — https://minecraft.wiki/w/Controls | deep | Java Edition defaults: left mouse attacks or breaks (hold to break); right mouse uses, places and toggles doors and levers; middle mouse picks the block; E inventory; Q drops the held item ("If items are stacked, only one gets thrown"); 1 to 9 hotbar; F swaps to the off hand; T chat; / opens chat with a command; hold Tab for the player list; L advancements; F1 hides the interface; F2 screenshot; Left Ctrl sprint, Left Shift sneak, Space jump. | Fits as the other big reference players bring: Q-to-drop and T-to-chat are Minecraft habits. We keep T as a second chat key; we put drop on G instead of Q because in our world a dropped meal feeds bugs (D54), and Q is better spent on healing. |
| 41 | Steam discussion, Core Keeper, "Appalling that there are no settings for selecting display resolution and scaling" (Aug to Sep 2024) — https://steamcommunity.com/app/1621690/discussions/0/4764332864593558710/ | deep | At the 1.0 release a player on a 4K screen reports "huge pixels and massive UI", with windowed mode as the only workaround, and black bars on ultrawide screens; another player says he did not buy the game for this reason. (Search results say later updates added integer scaling; not confirmed here.) | Fits as the player's side of the settings question: in a pixel-art game, interface size and world zoom must be separate settings, and 4K and ultrawide screens must be handled from day one. |
| 42 | Steam discussion, Necesse "Welcome and FAQ" — https://steamcommunity.com/app/1169040/discussions/0/3344417177391667933/ | deep | "You can zoom in using the zoom controls (default Numpad +/-) or use the slider in general settings"; "UI scale can be adjusted in Interface settings." | Fits: the closest relative keeps world zoom (a key pair and a slider) apart from interface size, as Stardew does [26]. |

## 2. Codebase study
Four real open-source codebases were read (files downloaded from GitHub on 2026-09-28 and read in full or in the
quoted ranges). Mindustry is a multiplayer factory game with a first-sector tutorial; Luanti (formerly Minetest) is a
multiplayer block sandbox; the Unity Input System samples are the official rebinding and hint code for the engine and
package our client already has installed (checked against the copy in our project, not only GitHub); ScrollToArms is
a small Valheim mod that solves the same mouse-wheel conflict our shovel has.

### 2.1 Mindustry's contextual hints (`HintsFragment.java`)
File: `core/src/mindustry/ui/fragments/HintsFragment.java`,
https://github.com/Anuken/Mindustry/blob/master/core/src/mindustry/ui/fragments/HintsFragment.java

Every hint is two tests: when it may appear, and what action completes it. Completing means the player actually did
the thing, not that they pressed "OK":
```java
desktopMove(visibleDesktop, () -> Core.input.axis(Binding.moveX) != 0 || Core.input.axis(Binding.moveY) != 0),

depositItems(
    () -> !player.dead() && player.unit().hasItem(),
    () -> !player.dead() && !player.unit().hasItem()
),

conveyorPathfind(
    () -> control.input.block == Blocks.titaniumConveyor,
    () -> Core.input.keyRelease(Binding.diagonalPlacement) || (mobile && Core.settings.getBool("swapdiagonal"))
),
```
Only one hint shows at a time, it never interrupts a cutscene, it waits until the player has played for a few
seconds, the whole system obeys one "Hints" switch, and each hint has a Skip button:
```java
group.visibility = () -> Core.settings.getBool("hints", true) && ui.hudfrag.shown();
...
}else if(hint != null && !renderer.isCutscene() && state.isGame() && control.saves.getTotalPlaytime() > 8000){
    display(hint);
...
t.button("@hint.skip", Styles.nonet, () -> {
    if(current != null){
        complete();
    }
}).size(112f, 40f).left();
```
A finished hint is remembered in the player's own settings, so it never comes back on any server:
```java
@Override
public void finish(){
    Core.settings.put(name() + "-hint-done", finished = true);
}
```
Hints can depend on other hints (`dependencies`), and the text is chosen per device (`hint.<name>.mobile`).

What to copy: the pair of tests (show-when / done-when), done-by-doing, one at a time, a skip button, a global switch,
remembered per player. What not to copy: the text names keys literally, so a player who rebinds sees the wrong key.
From `core/assets/bundles/bundle.properties`
(https://github.com/Anuken/Mindustry/blob/master/core/assets/bundles/bundle.properties):
```
hint.desktopMove = Use [accent][[WASD][] to move.
hint.respawn = To respawn as a ship, press [accent][[V][].
```
XAG 107 (row 21) asks for the opposite: every hint must show the player's current binding.

### 2.2 Mindustry's objectives (`MapObjectives.java`)
File: `core/src/mindustry/game/MapObjectives.java`,
https://github.com/Anuken/Mindustry/blob/master/core/src/mindustry/game/MapObjectives.java

The map-scripted tutorial is a graph of objectives. Each objective runs only when all its parents are done, checks
a condition against the world every update, and when done can raise flags that other objectives wait for:
```java
/** The parents of this objective. All parents must be done in order for this to be updated. */
public transient Seq<MapObjective> parents = new Seq<>(2);
...
public void done(){
    state.rules.objectiveFlags.removeAll(flagsRemoved);
    state.rules.objectiveFlags.addAll(flagsAdded);
    completed = true;
    ...
}
...
public boolean qualified(){
    return !completed && dependencyFinished();
}
```
A typical objective is a plain condition, for example "have N of an item":
```java
public boolean update(){
    return state.rules.defaultTeam.items().has(item, amount);
}
```
Only the server may complete an objective; clients just display it:
```java
//objectives cannot get completed on the client, but they do try to update for timers and such
if(obj.update() && !net.client()){
    Call.completeObjective(all.indexOf(obj));
}
```
Each objective can carry `details` text shown on click and world `markers` (points, text, shapes) that point the
player to the place.

What to copy: lessons as data (a small graph of steps, each a checkable condition, with a marker), checked and
completed by the server so a player cannot fake them, and parents instead of a single fixed line so steps can open
in parallel. What differs for us: Mindustry's objectives belong to the whole team on a map. Ours must belong to
each player, stored with the character, because a late joiner has not done what the first player did.

### 2.3 Luanti's settings and keys (`builtin/settingtypes.txt`)
File: `builtin/settingtypes.txt`, https://github.com/luanti-org/luanti/blob/master/builtin/settingtypes.txt

All settings are declared in one data file that the settings menu is built from. Each line gives a name, a label,
a type and a default:
```
#    If enabled, the "Sneak" key will toggle when pressed.
#    This functionality is ignored when fly is enabled.
toggle_sneak_key (Toggle Sneak key) bool false
...
#    Prevent digging and placing from repeating when holding the respective buttons.
#    Enable this when you dig or place too often by accident.
#    On touchscreens, this only affects digging.
safe_dig_and_place (Safe digging and placing) bool false
```
Each action has one keyboard default and one gamepad default on the same line, and keyboard keys are stored as
physical positions (scancodes), so W A S D stays in the same place on a French or German keyboard:
```
keymap_forward (Move forward) key SYSTEM_SCANCODE_26|GAMEPAD_AXIS_MINUS_1
keymap_dig (Dig/punch/use) key KEY_LBUTTON|GAMEPAD_AXIS_PLUS_5
keymap_place (Place/use) key KEY_RBUTTON|GAMEPAD_AXIS_PLUS_4
keymap_drop (Drop item) key SYSTEM_SCANCODE_20|GAMEPAD_BUTTON_12
keymap_chat (Open chat) key SYSTEM_SCANCODE_23
```
(Scancode 20 is the key where Q sits on a US keyboard; 23 is T.) The top-level groups are Controls (General,
Actions and Keybindings, Keyboard and Mouse, Touchscreen, Gamepads), Graphics and Audio (Screen, FPS, Camera, Effects,
Audio, User Interfaces with GUI, HUD and Chat), Client and Server, and Advanced.

What to copy: one data table of settings (name, label, type, default, which group), hold-versus-toggle switches, a
"safe digging" switch that stops a held button from repeating, and one row per action with both a keyboard and a
pad default, stored by physical key position.

### 2.4 Unity Input System, the rebinding sample (the engine we use)
Files: `Assets/Samples/RebindingUI/RebindActionUI.cs`, `RebindSaveLoad.cs`, `GamepadIconsExample.cs` in
https://github.com/Unity-Technologies/InputSystem/tree/develop/Assets/Samples/RebindingUI (read from the develop
branch; our client has package version 1.14.2, whose Package Manager sample should be checked before copying).

Rebinding one action: turn the action off, wait for the next key or button, then show the new name everywhere:
```csharp
if (actionWasEnabledPriorToRebind)
    action.actionMap.Disable();

// Configure the rebind.
m_RebindOperation = action.PerformInteractiveRebinding(bindingIndex)
    .OnCancel(...)
    .WithActionEventNotificationsBeingSuppressed()
    .WithTimeout(m_RebindTimeout)
    .OnComplete(
        operation =>
        {
            ...
            UpdateBindingDisplay();
            CleanUp();
```
The label for any action comes from the binding itself, so the same call can feed tutorial text:
```csharp
displayString = action.GetBindingDisplayString(bindingIndex, out deviceLayoutName, out controlPath, displayStringOptions);
```
Saving is one JSON string of only the changes the player made:
```csharp
var rebinds = actions.SaveBindingOverridesAsJson();
PlayerPrefs.SetString(playerPreferenceKey, rebinds);
...
actions.LoadBindingOverridesFromJson(rebinds);
```
Swapping two actions' keys (the usual answer to "that key is already used") is built in (`SwapBinding`, which
applies each binding's path to the other), and `GamepadIconsExample.cs` swaps a text label for an Xbox or
PlayStation button picture based on the device layout, which is what Steam Deck Verified's glyph rule needs.

The copy of the package our project already has (`BugFarmerClient/Library/PackageCache/com.unity.inputsystem@be6c4fd0abf5`,
`package.json` version 1.14.2) contains the same rebinding API (`InputActionRebindingExtensions.cs`:
`GetBindingDisplayString` at line 368, `SaveBindingOverridesAsJson` at 1101, `LoadBindingOverridesFromJson` at
1201) and two more samples that answer our questions directly.

`Samples~/InGameHints/InGameHintsExample.cs` is the fix for Mindustry's hard-coded key names: the hint text holds a
placeholder, and the real binding is put in, and rebuilt whenever the player switches device or keyboard layout:
```csharp
// This is invoked by PlayerInput when the controls on the player change. If the player switches control
// schemes or keyboard layouts, we end up here and re-generate our hints.
public void OnControlsChanged()
{
    UpdateUIHints(regenerate: true); // Force re-generation of our cached text strings to pick up new bindings.
}
...
m_ThrowObjectHelpText = kThrowObjectHelpTextFormat
    .Replace("{throw}", m_PlayerInput.actions["throw"].GetBindingDisplayString())
    .Replace("{drop}", m_PlayerInput.actions["drop"].GetBindingDisplayString());
```
`Samples~/GamepadMouseCursor/README.md` shows the other half of controller support for a mouse-aimed game: keep the
menus pointer-driven and let the stick drive a virtual mouse ("an oft-used alternative is to instead keep having
UIs operated by pointer input but to drive the pointer from gamepad input"), via the `VirtualMouseInput` component,
which warps the real cursor when a mouse exists and draws a software cursor when it does not.

What this means for us: full rebinding, hints that name the player's real key, and a stick-driven cursor are all
supported in the exact package we have. The real cost is moving the input code off the old `Input.GetKey` calls
onto Input System actions (every file listed at the top), not the settings screen itself.

### 2.5 ScrollToArms, a Valheim mod that shares the mouse wheel (`src/WheelMode.cs`, `src/WheelReads.cs`)
Repository: https://github.com/isimp/ScrollToArms (C#, Unity, BepInEx/Harmony). Its README notes it was written
mostly with Claude Code; it is studied here because it is a small, working, published answer to the exact conflict
we have (a tool that owns the wheel traps the player on that hotbar slot), not as an authority.

The rule it implements: the tool keeps the plain wheel, and a held modifier plus the wheel always walks the hotbar.
The other wheel users read the wheel through one gate that returns zero while the hotbar owns it:
```csharp
/// <summary>The wheel as the camera and the piece rotation see it: nothing while the hotbar owns it.</summary>
public static float Read()
{
    var value = ZInput.GetMouseScrollWheel();
    return Picker.HotbarOwnsWheel() ? 0f : value;
}
```
And it always tells the player what the wheel will do right now, only when that is worth saying:
```csharp
case State.BuildRotates:
    return $"Wheel: rotate  |  {modifier} + wheel: hotbar";
...
case State.ToolKeeps:
    return $"{ItemNameList.ShownName(tool.m_shared.m_name)} keeps the wheel{putAway}{back}";
```
What it teaches us: the trap is real and players feel it (Valheim's players asked for exactly this), and any fix
needs one owner of the wheel decided in one place (our `HotbarUI.HandleScrollWheel` already has that shape) plus a
label that names what the wheel does right now. Section 3.2 recommends going one step further (W1): the plain wheel
stays with the hotbar and the shovel's mode gets its own key. This mod's pattern (a modifier that returns the wheel
to the hotbar) is the runner-up, W3. Either way the modifier must be rebindable, and the number keys plus a single
"next / previous slot" key stay as a route that needs no second key (XAG 107, row 21).

## 3. Findings and recommendations

### 3.0 How the search was done
Each topic was approached from at least four directions, so that no conclusion rests on one search:
- **Stardew Valley's onboarding:** (1) the game's wiki pages on quests, multiplayer and television; (2) design
  write-ups (Pixelated Playgrounds; a Medium analysis refused the fetch); (3) the player's side, searches on new
  players feeling lost in the first week; (4) the technique, letters that arrive after something the player did.
- **Terraria's Guide:** (1) the Guide's wiki page and its version history; (2) the player's side, "can you learn
  Terraria without the wiki"; (3) reviews and research (Wikipedia's reception section and the 2018 study it cites);
  (4) how the controls and settings pages describe hints and help.
- **Other games' first hours:** (1) by game: Palia, Dinkum, Necesse, Minecraft, Valheim, Breath of the Wild,
  Satisfactory, and Core Keeper (search results only); (2) by engine feature: how Minecraft stores tutorial progress
  per device; (3) by code: Mindustry's hints and objectives; (4) by problem: quest progress for players who join a
  shared world late.
- **Writing on teaching players:** (1) conference talks (Celia Hodent, GDC 2016; George Fan, GDC 2012); (2) columns
  (Ernest Adams; Game Developer's round-up of designers); (3) platform guidance (Roblox's onboarding page); (4) the
  accessibility guidelines' rules on tutorials.
- **Default keys:** (1) each game's wiki (Terraria, Stardew, Necesse) and a guide for Core Keeper, whose wikis refused
  the fetch; (2) code (Mindustry's `Binding.java`, Luanti's key list); (3) guidelines (XAG 107); (4) the problem of one
  wheel with two jobs (Valheim threads and a mod's source).
- **Controllers and the Steam Deck:** (1) Valve's compatibility and recommendation pages; (2) each game's gamepad
  section; (3) the Unity samples for a stick-driven cursor and for hints that name the real button; (4) Stardew's
  controller settings.
- **Settings menus:** (1) Terraria's and Stardew's settings pages; (2) Luanti's settings file; (3) XAG 117, 104 and 101;
  (4) players' complaints (a Core Keeper thread on missing scaling settings, Necesse's FAQ); PCGamingWiki refused the
  fetch.
- **Accessibility:** (1) the Game Accessibility Guidelines full list; (2) XAG 101, 104, 107 and 117; (3) the worked
  examples inside them (The Long Dark, Halo Infinite, Minecraft's sound subtitles); (4) the Unity samples that make
  rebinding and correct key names cheap.

Pages that refused the fetch are not counted as read: the Valheim fandom wiki (402), the Medium Stardew analysis
(403), PCGamingWiki (403), a ScienceDirect study of tutorials (403), an Enshrouded thread on per-player quest progress
(403), and the Core Keeper wikis (404 and blocked). In total 42 sources are in the table (40 read in full, 2 thin),
plus five code studies from four open-source projects.

### 3.1 Question A: tutorial chains

#### What the good examples share
1. **The first lessons come from people.** Each townsperson gives one small job, the job is the lesson, and a small
   reward follows (Stardew [1], Palia [9, 10], Dinkum [11, 12], Necesse [13]).
2. **A welcoming figure hands out the first errands, often in any order.** Palia's Learning the Ropes sends the player
   to five teachers in any order, each handing over the tool for their trade [9]; Breath of the Wild's four shrines can
   be done in any order and one reward opens the world [32]; Dinkum's town manager gives the first tools during
   conversation [11].
3. **Later lessons are set off by what the player did or where they went, not by a calendar.** Stardew's letter the
   morning after the first copper ore, or after reaching mine level 5 [1]; Valheim's raven when you pick up ore or
   enter a new land [7]; Minecraft's recipes appearing when you first hold an ingredient [16]; Roblox's guidance names
   "entering new zones or acquiring new items" as the triggers [39].
4. **Each lesson is finished by doing the thing once, and the words are few.** At most three new things at once, and
   say why rather than how (Hodent [18]); about eight words on screen, "just get the player to do it once" (Fan [37]);
   Mindustry completes a hint only when the player performs the action (section 2.1).
5. **Everything taught can be found again.** Valheim's compendium [8], Terraria's Guide and his recipe lookup [5],
   Minecraft's recipe book and advancement tree [16, 17], Stardew's quest log [1]. The accessibility guidelines ask for
   reminders of the controls and of the current goal during play, and for all instructions to be replayable [20].
6. **It can be skipped, switched off, and is never forced on a returning player** (Adams [19]; Valheim's switch [7];
   Minecraft Bedrock's reset and off switch [15]; Satisfactory's skip [33]; Mindustry's switch and skip button, 2.1).
7. **A hint-giver alone is not enough.** Terraria has one, and players still left for the wiki [5, 6]. What closes the
   gap is an explanation on every item ("everything must have pop-up help", Soren Johnson [38]) — which our game has
   already decided to have in the examine view.

What goes wrong in the examples:
- **Shared tutorials in multiplayer teach only the first player.** Satisfactory: "Only the host is required to
  complete the tutorial" [33]. Mindustry's objectives belong to the team on a map (2.2).
- **Hints keyed to the world's progress mislead a new character in an old world.** Terraria's Guide chooses advice
  partly from the world's state [5]. Our lessons must key on the player's own actions.
- **Hard-coded key names break when players rebind** (Mindustry's hint text, 2.1). XAG 107 asks that every hint show
  the current binding [21]; Unity's own sample shows how (2.4).
- **Stopping the clock during the first day** (Dinkum [11]) is not possible for us: one world clock, no skipping the
  night, and the world only stops when nobody is online (D57, 2026-09-28).

#### The candidates, scored
Scores are 1 (poor) to 5 (good); for cost, 5 means cheapest. The brief's five axes are used, plus a sixth,
"gives direction", because a sandbox with no story needs something to answer "what could I do next?".

| Candidate | Few words, learn by doing | Fits "no story, own goals" | Multiplayer: own progress, late joiners | Can be read again | Cost | Gives direction | Total | Verdict |
|---|---|---|---|---|---|---|---|---|
| A. Townsperson quest chain only (Stardew, Palia, Dinkum) | 3 | 3 | 4 | 2 | 2 | 5 | 19 | Reject alone: dialogue once, then gone; a fixed chain drifts toward a storyline. |
| B. First-encounter tips only (Valheim's raven, Mindustry's hints, Minecraft's pop-ups) | 5 | 5 | 5 | 2 | 4 | 2 | 23 | Reject alone: teaches controls well but never introduces the townspeople or the money loop. |
| C. A guide or journal to read (Terraria's Guide, Necesse's Crafting Guide, a codex) | 2 | 5 | 5 | 5 | 4 | 2 | 23 | Reject alone: reading a manual is the "wall of text" the brief rules out. |
| D. Lessons that open on reaching a new area (Roblox, Breath of the Wild, Stardew's mine letters) | 4 | 4 | 5 | 2 | 4 | 3 | 22 | Keep as a part: right for the mine, the Bee Meadow, the lake. |
| E. Hybrid: one lesson system with three ways in (on joining, from townspeople, on first meeting a thing or place), every lesson logged in one Journal | 4 | 4 | 5 | 5 | 3 | 5 | 26 | **Pick.** |
| F. A separate tutorial world or a fixed scripted opening (Terraria's console tutorial world; Satisfactory's fixed Tier 0 steps) | 3 | 2 | 1 | 3 | 1 | 4 | 14 | Reject: splits friends on joining and is a scripted story in all but name. |
| G. No tutorial, only discovery (Core Keeper, going by search results) | 5 | 5 | 5 | 1 | 5 | 1 | 22 | Reject: Terraria's reviews show the cost [6]; Adams calls it the eighth failure [19]. |

Why E scores 3 on cost rather than 1: the three ways in are not three systems. They are one small lesson system whose
lessons are written as data in a file (the shape of Mindustry's objectives and hints, sections 2.1 and 2.2), where a lesson is a trigger, a
"done when" check, one or two short lines, an optional townsperson, marker and reward, and the lessons it opens next.

#### Recommendation: E
One lesson system, three ways in, one Journal:
- **On joining** (per character): three corner prompts for the controls, then the Mayor.
- **From townspeople:** a first chain in the village where one person sends you to several others, in any order, as
  Palia does, and each step ends back at a person who sends the player on to the next, as the owner asked (D59,
  2026-09-28).
- **On first meeting a thing or reaching a place:** one-line tips (the raven model without the nag), and new
  townspeople's lessons when the player first reaches their area (the tunnel foreman in the mine, Maren in the Bee
  Meadow, the Fisherman at the lake).
- **Everything lands in the Journal** (lessons done and open, people met and what they deal in, a key list), and every
  item keeps its examine page, which carries the long tail that no chain can.

Why this and not a plain chain: the chain gives direction and meets the townspeople, the tips teach the controls at
the moment they are needed, the area lessons make exploring pay, and the Journal makes all of it re-readable. No part
has a story: every step is an optional job with a small reward.

Rules the system follows (each from the sources):
1. **Per character, never shared.** Lesson progress is saved with the character, next to the existing `IntroSeen`
   and `KnownRecipes` fields of `CharacterSave` (`nakama/modules/world/character_persist.go`). A late joiner starts
   their own chain whatever other players have done. Other players can help (give a bug, show the way), but lessons
   that teach a control (catch, plant, place) count only the player's own action.
2. **Done by doing, checked by the server when there is a reward.** Coin rewards come only after the server has seen
   the action (a sale, a catch, a craft, a placement, entering a zone), as Mindustry lets only the server complete an
   objective (2.2). Tips with no reward complete on the player's own machine and are saved to the character.
3. **One sentence, the player's real keys.** Each prompt is one line of about eight words [37], never more than three
   new things at once [18], with the key filled in from the player's current binding (2.4), switching to controller
   buttons when a pad is in use.
4. **Nothing expires, nothing is forced, nothing can be failed.** Lessons wait (Stardew's story quests never expire
   [1]); any lesson can be hidden; one setting turns prompts off; another resets them. An account that has finished the
   village lessons with another character is asked once whether to skip them, and still gets their rewards.
5. **Markers appear late, not at once.** A "!" over a townsperson who has a job for you is always shown (only to you);
   a guide arrow appears only if you have not found them after a while (Roblox's timed hints [39]). Our emote bubble
   (`World/Emote.cs`, already "Cosmetic, client-local") is the base for the per-player "!".
6. **Works at any hour.** The world has one clock and no skipping the night (D57), so every step must work at night:
   shopkeepers trade at home at night (P18, accepted 2026-09-27) and the marker follows them home; the first catch
   accepts any small bug, as Palia's first catch accepts a day butterfly or a night moth [10].
7. **Keyed to the player, not the world.** No lesson assumes the world is new (see the Terraria problem above).
8. **Show a little of the road ahead.** The Journal lists the next one or two lessons as greyed entries with a
   one-line hint of where they start, as Minecraft's advancement screen shows up to two steps ahead [17] and as the
   greyed Ecology button already does (D40); the rest stays hidden to keep surprises.
9. **Answer "what is this for?" on the item itself.** Every item's examine page lists what it is made at and what it
   is used in, which is Terraria's Guide recipe lookup [5] and Minecraft's recipe book [16] built into the page the
   game has already decided to have. This, more than any chain, is what keeps players from needing a wiki.
10. **Help when something goes wrong, not before.** A one-line tip when a catch fails because the net is too small,
    when the pickaxe cannot break an ore, or the first time the player faints (George Fan's adaptive messages [37]).

#### The draft first chain (the starting village)
Names are the prototype's shopkeepers (`nakama/data/entities/occupants.json`): Marjoram (General Store), the Bug Dealer,
Brann (Blacksmith), Wynn (Carpenter), Dr. Vesper (Ecologist), and the Mayor; these are prototype names, not decided.
Places follow the rebuilt village (`docs/product/zones/village_21_B.md`): the player arrives on the plaza by the notice
board and signpost; the Town Hall is west of the plaza; the Carpenter and Blacksmith are south-east; the Ecologist's
cabin is east on the east lane; the road south leads past the quarry to the first mine. The starting kit is the
prototype's (overview "As built"): wooden tools, a small net, a watering can, three kinds of seeds, torches, a
flashlight and fencing for a pen, and no coins.

| # | Who | Opens when | What the player does | Teaches | Done when | Reward | Hands on to |
|---|---|---|---|---|---|---|---|
| 1 | (on joining) | A new character arrives | Three corner prompts, one at a time: walk; pick a hotbar slot; talk to the Mayor (marked) | Moving, the hotbar, "interact" | The player has talked to the Mayor | — | The Mayor |
| 2 | The Mayor | Step 1 done | Listen to a two-line welcome, take the Journal, open it once | The Journal key; that lessons are optional | The Journal has been opened | The Journal | Three people at once, shown in the Journal in any order: the Bug Dealer, Marjoram, Wynn (he suggests the Bug Dealer first, "you'll want coins") |
| 3 | The Bug Dealer | Talked to him | Choose the net, swing it at any small bug, catch one | Choosing a tool, using it (left click), the bug slots | A bug the player caught is in their bag | — | Back to the Bug Dealer |
| 4 | The Bug Dealer | Step 3 done | Trade with him and sell the bug | The trade screen and the sell box, coins | The server has recorded a sale | First coins (the game's first income, as D25 already intends) | Marjoram ("She sells seeds; spend it there") |
| 5 | Marjoram | Talked to her | Till open ground, plant three seeds, water them; refill the can at water | Hoe, seeds, watering can, refilling | Three seeds planted and watered by the player | A few more seeds | Wynn ("Bugs keep better alive; Wynn builds pens"). A later "Harvest" note from her opens by itself when the first crop is ripe |
| 6 | Wynn | Talked to him | Place the starting fencing in a closed ring and let a caught bug go inside | Placing things and the placement preview; pens hold bugs; letting bugs go from the cursor | A closed pen holds a bug the player released | — | Back to Wynn |
| 7 | Wynn | Step 6 done | Cut four wood with the axe, make a gate at his workbench, set it in the pen | Gathering; crafting at a village station; recipes | The server has recorded the craft and the placement | The gate recipe (it is sold by the carpenter in today's data, `recipes.json`: `gate_wood`, 4 wood, `shop:carpenter`) | The Mayor ("He'll want to hear you've settled") |
| 8 | The Mayor | Steps 4, 5 and 7 done, in any order | Talk to him | The map and the signposts at every fork; the notice board (jobs later) | Talked | A few coins | Dr. Vesper, east along the lane (marker on the east-lane signpost) |
| 9 | Dr. Vesper | Talked to him | Meet him; the Ecology tab's greyed button lights up (as decided in D40) | That the Ecology tab exists and what it is for | Talked | A monitoring station | His first quest, step 10 |
| 10 | Dr. Vesper | Step 9 done | Set the station up in the village meadow, open the Ecology tab and look at the fly numbers; optionally look at three flies with the magnifying glass | The Ecology tab; research filling a bug's page | Station placed by the player and tab opened | Coins | Brann ("He's short of copper; the old mine is south") |
| 11 | Brann | Talked to him | Take torches, go down the first mine, mine copper ore and coal, bring them back. On first entering the mine, the tunnel foreman gives a one-line tip on placing torches | Going below; light; which pickaxe breaks which ore | Ore and coal handed to Brann | — | Back to Brann |
| 12 | Brann | Step 11 done | Smelt a copper bar at his furnace | Processing at a station | A bar made by the player | Coins | The open world: the notice board, Dr. Vesper's next quests in the Ecology tab, and two optional spokes, Maren in the Bee Meadow to the west and the Fisherman at the lake |

The steps 3 to 7 are the three spokes; a player may do them in any order, and whoever they finish with points to
the next person they have not met yet. Every step can be walked away from and picked up later from the Journal.

Sample lines, one sentence each (the key in brackets is filled from the player's own binding):
- Prompt: "Walk with [W A S D]." Prompt: "Pick a tool with [1]-[0] or the wheel." Prompt: "Talk to the Mayor: [right click]."
- The Mayor: "Welcome. Folk here live off bugs." / "Meet the Bug Dealer, Marjoram and Wynn."
- The Bug Dealer: "Catch me any small bug. Net's in your bag." / "Good. Trade with me and sell it."
- Marjoram: "Till, plant, water. Three seeds will do." / "Bugs keep better alive. Ask Wynn."
- Wynn: "Close a ring of fence, then let one in." / "Four wood makes a gate. Use my bench."
- Dr. Vesper: "Set this station in the meadow. I'll show you the numbers."
- Brann: "Copper's short. Mine's south; take torches."

After the first chain, the other ways in (examples, not a full list):
- **On reaching a place:** the first mine (the tunnel foreman, planned for Underground Passages in
  `docs/product/economy/zones/underground_passages.md`); the Bee Meadow (Maren); the lake (the Fisherman, once he is
  back, since fishing starts in the village, D51); the Ant Tunnels (the myrmecologist's board, D52).
- **On first meeting a thing:** the first wasp nearby (the dodge key); the first time hurt (the quick-heal key); the
  first dead bug picked up (where to process it); the first ore the pickaxe cannot break (what can); a full bag; the
  first fibre (the Weaver); the first stone (the Stonemason); the first night (torches, and that shopkeepers can be
  visited at home).
- **Pinned goals:** like Fortnite's pinned recipe [18], the player can pin one open lesson or recipe to the screen.

### 3.2 Question B: controls and settings

#### The genre's defaults side by side
"Not found" means the source read did not list it; it is not a claim that the game has no key.

| Action | Terraria [23] | Stardew Valley [25] | Necesse [27] | Core Keeper [28] | Minecraft / Luanti [40, 2.3] | What most agree on |
|---|---|---|---|---|---|---|
| Walk | W A S D (arrows too) | W A S D | W A S D | W A S D (arrows too) | W A S D | W A S D |
| Use, attack, place | Left mouse | Left mouse or C | Left mouse | Left mouse | Left mouse | Left mouse |
| Interact | Right mouse | Right mouse or X | Right mouse | E (right mouse is a second "use") | Right mouse (use, place, open) | Right mouse; E is common too |
| Inventory | Esc | E or Esc | E | Tab | E (Minecraft), I (Luanti) | No single standard |
| Hotbar | 1 to 0, wheel | 1 to 0, minus, equals, wheel | 1 to 0, wheel | 1 to 0, wheel | 1 to 9, wheel | 1 to 0 and the wheel |
| Map | M | M | M | M | V minimap (Luanti) | M |
| Drop the held item | "Throw", unbound by default | not found (items are dragged out) | not found | not found | Q (one item at a time) | No key in the 2D games; Q in the block games |
| Quick heal | H | none | Q | not found | none | H or Q |
| Dodge or dash | none (accessories) | none | Space (trinket ability) | not found | none | Space where it exists |
| Chat | Enter | T | not found | Enter | T | Enter or T |
| Quest log or journal | none | F | none | none | L (advancements) | F where it exists |
| Zoom | + and - | a setting | not found | wheel on the map | none | + and - |
| Emotes | not found | Y | T | not found | none | varies |

The de-facto standard is W A S D, left mouse to use, right mouse to interact, 1 to 0 plus the wheel for the hotbar, and
M for the map. Everything else varies, so our choices there should follow our own verbs and hand comfort, with every
key rebindable.

#### Controllers and the Steam Deck
- **What Verified needs** [22, 36]: the whole game playable with the default controller setup and no setting changes;
  button pictures that match the pad and never show keyboard keys; a way to type with the pad (Steam's on-screen
  keyboard for character names and chat); text no smaller than 9 pixels high at 1280x800; 30 fps at 800p by default;
  mouse-style (trackpad) and stick-style pointing accepted together.
- **How the genre aims with a stick:** Terraria moves a free cursor with the right stick and adds Smart Cursor,
  toggled by pressing the stick, which picks the tile for the held tool, plus a lock-on for enemies [23]. Stardew acts
  near the character, with an optional right-stick cursor that resets and a setting to show which tile will be hit;
  its menus can snap between buttons [26, 34]. Core Keeper aims with the right stick [28].
- **For us:** "smart target, with an optional free cursor". The target cell is chosen near the player from the held
  tool (the net picks the nearest catchable bug in reach; the hoe and can pick the cell in front; the pickaxe and axe the
  nearest thing to break in the facing direction; a placeable the cell in front), shown with an outline and an icon.
  Moving the right stick takes over with a free cursor limited to reach, which returns to smart targeting after a moment
  of stillness; pressing the right stick switches between the two. Menus move focus between slots and buttons; Unity's
  virtual mouse (2.4) is only a fallback for any screen that needs a pointer.

#### The accessibility items that matter most here
1. **Every action rebindable** on keyboard, mouse and pad, including Esc, with two keys per action and a swap when a
   key is already taken [20, 21, 2.4].
2. **Prompts show the player's own keys**, and pad buttons when a pad is in use [21, 2.4].
3. **No required two-key presses or long holds.** Holding the button to keep breaking or digging can be switched to
   click-to-start/click-to-stop, or to one action per click (The Long Dark's "accessible interactions" [21]; Luanti's
   "safe digging" [2.3]; Terraria's autofire [24]).
4. **Nothing told by colour alone.** Today's green or red placement preview gets a tick or cross shape; danger is shown
   by an icon and an outline, not only red [20].
5. **Readable text:** at least 18 px body height at 1080p by default, scalable to 200% [31]; at least 9 px at 1280x800
   on the Deck [22]; a clean sans-serif font as an option beside the pixel font [31].
6. **Captions for important sounds, with a direction arrow:** a wasp coming, a sting winding up, thunder, a bug
   escaping a pen [30].
7. **Less motion on request:** screen shake from 0 to 100%, flashes (lightning, hits) from 0 to 100%, and swaying
   plants reduced [29, 24].
8. **Separate volumes** for music, effects, ambient sound and interface sounds [20, 26].
9. **Settings from the title screen**, and a short first-launch screen for text size, captions, shake and controls,
   before the opening plays [30, 20].
10. **All settings remembered** [20].

One guideline we cannot meet directly: changing the game's speed [20]. In a shared world nothing may run faster or
slower for one player (D58, 2026-09-28). Smart targeting, the hold and toggle options and captions are the substitutes.

#### Candidate keyboard layouts, scored
Scores 1 (poor) to 5 (good).

| Candidate | Familiar to genre players | Frequent keys near the left hand | Few clashes | Same actions on the pad | No required holds or two-key presses | Fits our actions (catch, release, dodge, trade, examine, tool modes) | Total | Verdict |
|---|---|---|---|---|---|---|---|---|
| C1. Terraria as it is (Esc bag, H heal, right mouse only for interact) | 4 | 3 | 3 | 3 | 3 | 2 | 18 | Reject: Esc as the bag and H are a stretch; no dodge, drop or tool-mode keys. |
| C2. Stardew as it is (E or Esc menu, F journal, T chat, C and X as keyboard-only use and interact) | 4 | 4 | 4 | 4 | 4 | 2 | 22 | Borrow the "second key" idea; lacks heal, dodge, drop. |
| C3. Core Keeper as it is (E interact, Tab bag, Q quick-stack, R sort) | 3 | 5 | 4 | 4 | 4 | 3 | 23 | Borrow E-to-interact and Tab; Q is better spent on healing for us. |
| C4. Recommended mix (table below) | 4 | 5 | 5 | 5 | 5 | 5 | 29 | **Pick.** |
| C5. Today's prototype (I bag, E pick up, R rotate, B shovel panel, Shift + click to dig, right mouse places, the shovel keeps the wheel) | 3 | 4 | 2 | 1 | 1 | 3 | 14 | Replace: no rebinding, a two-key dig, placement split between buttons, the wheel trap. |

#### The mouse-wheel choice, scored
Today the shovel takes the wheel, so with the shovel in hand the wheel cannot reach another slot
(`UI/HotbarUI.cs:117-120`). The owner left how the shovel switches between digging and laying to us (D45,
2026-09-27); P12 proposed the wheel.

| Candidate | Always know what the wheel does | Never trapped on the shovel | Fast for builders | Same as other games | No required two-key presses | Cost | Total | Verdict |
|---|---|---|---|---|---|---|---|---|
| W1. The wheel always walks the hotbar; the shovel's mode steps with R (Shift + R back), Ctrl + wheel as a shortcut, a d-pad direction on a pad | 5 | 5 | 4 | 5 | 5 | 5 | 29 | **Pick.** |
| W2. P12 as written, no escape: the shovel keeps the wheel, number keys only | 3 | 1 | 5 | 2 | 5 | 5 | 21 | Reject: the trap already in the code. |
| W3. P12 plus an escape: the shovel keeps the wheel, Alt + wheel walks the hotbar, a label says which (the ScrollToArms pattern, 2.5) | 4 | 4 | 5 | 3 | 4 | 4 | 24 | Runner-up, if building speed matters most. |
| W4. A ring menu of ground types opened by holding a key (like Terraria's multi-mode tools) | 4 | 5 | 3 | 4 | 3 | 3 | 22 | Reject for now; worth it only if the ground list grows long. |

The deciding case for W1: a wasp arrives while you are laying a path. With W1 the wheel reaches your weapon as it
always does; with P12 the same flick changes the ground type. W1 keeps everything else P12 asked for: the mode stays
visible in the hotbar slot, on the cursor and in a short label, and the hidden Shift-to-dig and the separate
materials panel still go. R is free for this because furniture does not rotate (D45) and doors turn by themselves; if
something must turn later, turning is simply that item's mode on the same key.

#### The recommended bindings
Every row can be rebound, and each action can hold a second key.

| Action | Keyboard and mouse | Second key | Gamepad | Why |
|---|---|---|---|---|
| Walk | W A S D | Arrow keys | Left stick | The standard |
| Use the held item: swing, catch, water, place, heal a friend with a bandage or potion | Left mouse (holding repeats; see settings) | — | Right trigger | "Left uses what is in your hand", as in Terraria, Stardew and Necesse (Core Keeper places with the right button); placing moves here from the right button, which also ends today's split where torches are placed with the left button and everything else with the right |
| Interact with the thing under the cursor: talk, open, trade, sleep, offer something to a player | Right mouse | — | A | The standard; offering by right-clicking a player is already accepted (P17, D54) |
| Interact with the nearest thing in reach, no aiming: the same verbs, plus picking up | E | — | A | Core Keeper's E; gives the keyboard and pad the same verb; E already picks things up today |
| A weapon's second move | Right mouse, when nothing interactable is under the cursor | — | Left trigger | Kept from today's order of checks |
| Dodge | Space | — | B | Kept; Necesse also uses Space |
| Hotbar slots | 1 to 0 | — | — | The standard |
| Next and previous slot | Mouse wheel, always | A spare key, unbound until the player sets one | RB and LB | The wheel never changes meaning |
| Tool mode (the shovel: Dig, then each ground the player has materials for) | R (Shift + R goes back) | Ctrl + wheel | D-pad left and right | P12's switch, moved off the plain wheel |
| Quick heal (uses the best healing item carried) | Q | H | X | Necesse's Q, the easiest reach for the most urgent key; Terraria's H as the second key |
| Drop the held item (one; hold for the whole stack) | G | Drag it out of the bag onto the world | D-pad down, held | Dropping is new and decided (D54); dropped food feeds bugs, so it is kept off the key next to W |
| Inventory | Tab | I | Y | Core Keeper's Tab; today's I kept as the second key |
| Journal (lessons, people met, key list) | J | — | Menu, then the Journal page | Named for what it opens; Stardew players know F, which stays free for the player to choose |
| Bugs (each bug's page and the Ecology tab) | B | — | Menu, then the Bugs page | Frees B from the shovel panel P12 removes |
| Map | M | — | View | The standard |
| Examine the thing under the cursor (the full page) | V | Middle mouse | D-pad up | Opens the decided examine page without taking a mouse button |
| Chat | Enter | T | Menu, then Chat (opens the Deck keyboard) | Enter (Terraria, Core Keeper) or T (Stardew, Minecraft) |
| Emotes | Y | — | Left stick press | Stardew's Y |
| Zoom in and out | + and - | — | a setting | Terraria's keys; the wheel stays the hotbar's |
| Close a panel, or open the menu | Esc | — | B in menus, Menu to open | Esc is rebindable too (XAG 107) |
| Help: the key list | F1 | — | inside the Menu | The usual help key on Windows (Minecraft and Luanti use F1 to hide the interface instead) |
| Fullscreen on or off | F11 | Alt + Enter | — | Common on PC |
| Switch smart targeting and free cursor | — | — | Right stick press | Terraria puts Smart Cursor on the same button |

Clashes this avoids:
1. The wheel means one thing (today's shovel trap goes).
2. Right mouse means "the thing under the cursor", and nothing else fights for it except the weapon's second move,
   which only fires on empty ground.
3. No action needs two keys at once: Shift + R and Ctrl + wheel are shortcuts with single-key routes beside them.
4. Drop is not beside W, because an accidental drop in the wild feeds the bugs.
5. While the chat box is open, game keys are off, so typing an "e" never opens anything.
6. F12 is left to Steam's screenshot key, and today's developer keys (F1 to F10, `Debug/DebugOverlay.cs`,
   `Player/PlayerController.cs`, `World/DayNightController.cs`) are hidden in release builds.
7. With Tab as the bag, the player list lives in the menu rather than on Tab (Minecraft players hold Tab for it,
   so the menu entry should say so).
8. On the pad, B dodges in play and goes back in menus; play and menus use separate sets of actions, as Unity's input
   system is built to do (2.4).

#### The settings list
Grouped as a player looks for them. Defaults in brackets.

**Before you start** (first launch only; also inside Accessibility): text size [100%], captions [on], screen shake
[100%], a preview of the prompts with the detected device.

**Gameplay:** language; lesson prompts [on]; reset lessons; guide arrow [only when stuck] (on, only when stuck, off); holding
the use button [hold repeats] (hold repeats, click to start and stop, one action per click); pick up by walking over
things [on]; target outline [always] (always, while using a tool, off); smart targeting with keyboard and mouse [off] (the pad's
automatic target, which also makes keyboard-only and one-handed play possible, as XAG 107 asks [21]); damage numbers
[on]; confirm before quitting [on].

**Controls, keyboard and mouse:** every action with two keys and a reset per row and for all; swap on conflict; mouse
wheel direction [normal]; which key the Ctrl + wheel shortcut uses [Ctrl].

**Controls, gamepad:** every action rebindable; cursor speed [100%, from 50% to 200%]; stick dead zone; vibration
[100%, 0 to 100%]; start in smart targeting or free cursor [smart]; button pictures [automatic] (automatic, Xbox,
PlayStation, Steam Deck).

**Display:** window [borderless] (windowed, borderless, fullscreen); resolution; v-sync [on]; frame cap [monitor]
(30, 60, 120, 144, unlimited); pixel-perfect scaling [on] (whole-number scaling with borders, or fill the screen);
world zoom [the standard view] in whole steps, kept apart from interface size [41, 42]; wide and
ultrawide screens show more of the world at the sides rather than black bars; brightness [50%] for dark tunnels; bloom and colour grade [on].

**Interface:** interface size [100%, 75% to 200%]; font [pixel] (pixel, clear sans-serif); dark plate behind text
[on] with opacity; cursor size [100%] and colour; hotbar at the bottom or the top (the open question in §20 becomes a
setting, with one default chosen by us).

**Audio:** master, music, effects, ambient, interface [each 0 to 100%]; mute when the window is in the background
[off]; mono sound [off].

**Captions:** sound captions [on]; direction arrows [on]; caption size [100%, to 200%]; caption background opacity
[70%].

**Accessibility:** a "reduce motion" switch that sets shake to 0, flashes to 0 and plant sway to low; a "no holds"
switch that turns every hold into a press (The Long Dark's approach [21]); high-contrast outlines on bugs that can
hurt you [off]; placement preview colours [green and red with tick and cross] (or blue and orange with tick and
cross); the Ecology tab's charts drawn in colours that colour-blind players can tell apart, with each line labelled;
a link back to the first-launch screen.

**Chat and players:** chat text size; chat background opacity; show player names [on]; offers from other players
[everyone] (everyone, friends, nobody), since offering is by right-click (P17).

**Where settings are kept:** display settings stay on each machine, as Valve advises [36]; controls, interface,
captions and accessibility follow the account.

#### What it would cost
1. **Move the input code onto the Input System's actions.** Every key read listed at the top of this document changes.
   This is the largest item and it has to come first: rebinding, the correct key names in prompts, and pad support all
   depend on it (2.4).
2. **A settings screen** with the groups above, saved; the rebinding rows are mostly Unity's sample (2.4).
3. **The lesson system:** a data file of lessons, a per-character record next to `IntroSeen` and `KnownRecipes`, the
   server checks for rewarded steps, the corner prompt, the Journal, a lasting per-player "!" built from
   `World/Emote.cs`, and the guide arrow. (A reminder from past work: an old server build silently drops new saved
   fields, so the server image must be rebuilt when the save gains the lesson record.)
4. **Pad play:** smart targeting, focus movement through every panel (the bag's drag and drop needs a pad route),
   button pictures, and Steam's on-screen keyboard. Worth designing for now and building after the keyboard version,
   if Steam Deck Verified is a goal.

## 4. Claims I am not sure about
About other games:
1. **Terraria's drop key.** The official wiki's Controls and Game controls pages list "Throw" as unbound by default
   (https://terraria.wiki.gg/wiki/Game_controls), while older guides in search results say T, and a Terraria forum
   thread is titled "Leave the throw hotkey unbound by default". I did not read that thread; it suggests the default
   changed after accidental throws, which would support keeping our drop key away from W, but I have not confirmed
   when or why it changed.
2. **Stardew's controller targeting.** That tools act on the tile the farmer faces comes from a search snippet of a
   forum thread, not a page I read in full; the page I read (row 34) is thin. The Options page (row 26) confirms the
   tile-indicator and snapping-menu settings, not the facing rule itself.
3. **Stardew for a late-joining farmhand.** The Multiplayer page says quest progress is mostly individual but does not
   say which opening quests and letters a farmhand who joins later receives.
4. **Valheim's raven.** The switch's label ("Enable Raven Hints", under Misc) and re-reading tips from the compendium
   come from two secondary sites; the Valheim wiki refused the fetch. Whether hints are tracked per character was not
   confirmed.
5. **Core Keeper's keys** come from a hosting company's guide (row 28), because both Core Keeper wikis refused the
   fetch; its quick heal and dodge keys were not found. Core Keeper's tutorial ("throws them out into the world with no
   objectives") is from search results only.
6. **Necesse's keys** are from the community wiki, whose game version is not stated; chat and zoom keys were not listed.
7. **Palia's quests being per player** is assumed from it being an online game with personal quest logs; the pages
   read do not say it.
8. **George Fan's "eight words"** is from a third party's notes of the talk, not the slides.
9. **Mindustry's hint delay:** `control.saves.getTotalPlaytime() > 8000` is read as 8 seconds of play, assuming
   milliseconds; I did not check the unit.
10. **The ScrollToArms mod** says it was written mostly with Claude Code. It is a working example of the pattern, not
    evidence that the pattern is good; the evidence for the problem is Valheim's own players asking for it (search
    results on the Valheim forum and two other mods doing the same).
11. **Steam Deck and trackpads:** Valve's pages accept mouse-style pointing alongside the stick ("Mixed Input"), but I
    found no rule saying whether a game that needs the trackpad as a mouse by default can be Verified. The plan above
    avoids depending on it (smart targeting plus the stick cursor).
12. **The Unity rebinding sample** was read on GitHub's develop branch; the same files exist in our installed 1.14.2
    package and the API calls were checked there, but the two versions may differ in detail.

About our own game (to check before building):
13. **Where a new player may farm before owning a plot.** Step 5 says "open ground"; the village's fields belong to
    townspeople (D41), and private plots come later from City Hall. Whether there is a common garden or any open
    ground a newcomer may till is a question for §06 and §15.
14. **The monitoring station in a shared village.** If another player has already set one up there, should the new
    player's step 10 ask for their own, or be done by reading the existing one? P9 says quests are per player while
    the zone's balance is shared; the station's ownership is not settled.
15. **The starting kit and the names** used in the chain are the prototype's (overview "As built";
    `occupants.json`), not decided design. The magnifying glass is not in today's kit although D12 says it should be.
16. **Whether flies and other small bugs are about at night.** Step 3 accepts any small bug so that it works at night,
    but I did not check which species are active after dark.
17. **Text size in practice.** The 18-pixel figure is Microsoft's measure (lowest descender to highest ascender at
    1080p); our pixel font has not been measured.
18. **The scores in the candidate tables are my judgement**, not measurements; they rank the options and show the
    trade-offs, and a playtest could reorder the close ones (W1 against W3, C3 against C4).

About this research:
19. **No second reviewer.** The project's research routine asks for a separate critic agent to hunt for gaps; this task
    was run without sub-agents by instruction, so that review has not happened. The most useful things for a critic to
    test are the wheel ruling (W1 over P12's wheel), the choice of Q for healing and G for dropping, and whether a
    twelve-step first chain is too long before a player feels free.
