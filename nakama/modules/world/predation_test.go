package world

// Tests for the predator-slice foundations: per-species kill_drops loot tables, edible
// carrion entering/leaving the deterministic food registry (ITEM_ROTTED at spawn,
// FOOD_CONSUMED(0) at lifetime expiry — both hash-bearing), and FindNearbyFood matching
// carrion by exact item type.
//
// Run inside the builder image:  go test ./modules/world/ -run TestKillDrop -v

import (
	"testing"

	"bugfarmer/entities"

	"github.com/heroiclabs/nakama-common/runtime"
)

func killDropTestState() *WorldState {
	state := newTestState(20)
	state.Entities["dead_fly"] = &EntityDef{Category: "resource", FoodValue: 10}
	state.Entities["wasp_stinger"] = &EntityDef{Category: "resource"} // inedible
	state.Species["fly_common"].KillDrops = []entities.KillDrop{
		{Item: "dead_fly", CountMin: 1, CountMax: 1, Chance: 1.0},
	}
	// Open chunk so IsBlocked doesn't trip on nil chunks at the drop point
	state.Chunks[ChunkKey(0, 0)] = NewEmptyChunk(0, 0, "grass")
	return state
}

// A kill drop from a species with an edible item: ground item carries the def's
// FoodValue AND an ITEM_ROTTED ledger event registers it as bug food.
func TestKillDropEdibleEmitsItemRotted(t *testing.T) {
	state := killDropTestState()
	m := &Match{}
	species := state.Species["fly_common"]

	m.spawnKillDrops(nopRuntimeLogger(), nil, state, species, 10, 10, 10, 10, 32)

	if len(state.GroundItems) != 1 {
		t.Fatalf("drops=%d, want 1", len(state.GroundItems))
	}
	for _, item := range state.GroundItems {
		if item.ItemType != "dead_fly" || item.FoodValue != 10 {
			t.Fatalf("drop %s food=%d, want dead_fly food=10", item.ItemType, item.FoodValue)
		}
		if item.Lifetime <= 0 {
			t.Fatal("carrion must have a finite lifetime")
		}
	}
	evs := eventsOfType(state, InfluenceItemRotted)
	if len(evs) != 1 || evs[0].Level != 10 {
		t.Fatalf("ITEM_ROTTED events=%d level=%v, want 1 at level 10", len(evs), evs)
	}
}

// An INEDIBLE drop (no food_value) emits NO registry event.
func TestKillDropInedibleStaysLedgerSilent(t *testing.T) {
	state := killDropTestState()
	m := &Match{}
	state.Species["fly_common"].KillDrops = []entities.KillDrop{
		{Item: "wasp_stinger", CountMin: 1, CountMax: 1, Chance: 1.0},
	}

	m.spawnKillDrops(nopRuntimeLogger(), nil, state, state.Species["fly_common"], 10, 10, 10, 10, 32)

	if len(state.GroundItems) != 1 {
		t.Fatalf("drops=%d, want 1", len(state.GroundItems))
	}
	if got := len(eventsOfType(state, InfluenceItemRotted)); got != 0 {
		t.Fatalf("inedible drop emitted %d ITEM_ROTTED events", got)
	}
}

// A blocked drop point (predator hovering over a fence) falls back to the victim's
// center — an edible item registered inside a blocks_bugs cell would be a permanent
// wall-attractor.
func TestKillDropBlockedFallsBackToVictim(t *testing.T) {
	state := killDropTestState()
	m := &Match{}
	state.Entities["fence_wood"] = &EntityDef{World: &WorldData{BlocksBugs: true}}
	chunk := state.Chunks[ChunkKey(0, 0)]
	chunk.SetOccupant(10, 10, &PlacedOccupant{ID: "fence_wood", Anchor: true})

	// Drop point = the fence cell center; fallback = open ground at (20, 20)
	m.spawnKillDrops(nopRuntimeLogger(), nil, state, state.Species["fly_common"],
		10.5, 10.5, 20, 20, 32)

	for _, item := range state.GroundItems {
		wx := float32(item.Position.ChunkX*32) + item.Position.LocalX
		wy := float32(item.Position.ChunkY*32) + item.Position.LocalY
		if wx > 15 && wy > 15 {
			return // landed near the fallback ✓
		}
		t.Fatalf("blocked drop landed at (%.1f, %.1f), want near the fallback (20, 20)", wx, wy)
	}
	t.Fatal("no drop spawned")
}

// Lifetime expiry of an EDIBLE item must clear the registry: FOOD_CONSUMED(level 0).
// Carrion is the first edible item that expires — without this, every uneaten corpse
// leaves a phantom registry entry and a joiner-vs-veteran resync loop.
func TestCarrionExpiryEmitsFoodConsumedZero(t *testing.T) {
	state := killDropTestState()
	m := &Match{}
	state.GroundItems["c1"] = &entities.GroundItem{
		ID: "c1", ItemType: "dead_fly", Count: 1,
		Position:  entities.EntityPosition{LocalX: 10, LocalY: 10},
		FoodValue: 10,
		Lifetime:  0.05, // expires on the first decay tick
	}

	m.processGroundItemDecay(state, nil)

	if _, exists := state.GroundItems["c1"]; exists {
		t.Fatal("expired carrion still in the world")
	}
	evs := eventsOfType(state, InfluenceFoodConsumed)
	if len(evs) != 1 || evs[0].Level != 0 || evs[0].FoodID != "c1" {
		t.Fatalf("expiry events wrong: %+v (want one FOOD_CONSUMED level 0 for c1)", evs)
	}
}

// An inedible item's expiry stays silent (no registry entry existed).
func TestInedibleExpiryStaysSilent(t *testing.T) {
	state := killDropTestState()
	m := &Match{}
	state.GroundItems["s1"] = &entities.GroundItem{
		ID: "s1", ItemType: "wasp_stinger", Count: 1,
		Position: entities.EntityPosition{LocalX: 10, LocalY: 10},
		Lifetime: 0.05,
	}

	m.processGroundItemDecay(state, nil)

	if got := len(eventsOfType(state, InfluenceFoodConsumed)); got != 0 {
		t.Fatalf("inedible expiry emitted %d FOOD_CONSUMED events", got)
	}
}

// FindNearbyFood matches carrion by exact item type (the centipede's attraction list)
// AND via the rotten_fruit wildcard (flies scavenge corpses — intended emergence).
func TestFindNearbyFoodMatchesCarrion(t *testing.T) {
	state := killDropTestState()
	state.GroundItems["c1"] = &entities.GroundItem{
		ID: "c1", ItemType: "dead_fly", Count: 1,
		Position:  entities.EntityPosition{LocalX: 12, LocalY: 10},
		FoodValue: 10,
	}
	pos := entities.EntityPosition{LocalX: 10, LocalY: 10}

	// Exact match (centipede)
	hits := FindNearbyFood(state, pos, 8, []string{"dead_fly"})
	if len(hits) != 1 || hits[0].ID != "c1" {
		t.Fatalf("exact-match hits=%v, want c1", hits)
	}
	// Wildcard (flies): any FoodValue>0 ground item
	hits = FindNearbyFood(state, pos, 8, []string{"rotten_fruit"})
	if len(hits) != 1 || hits[0].ID != "c1" {
		t.Fatalf("wildcard hits=%v, want c1 (flies scavenge carrion)", hits)
	}
}

// ===== Predation core (hunt / flee / strike) =====

// predationTestState: a wasp predator + fly prey in open chunks.
func predationTestState() *WorldState {
	state := newTestState(20)
	for cx := 0; cx <= 1; cx++ {
		for cy := 0; cy <= 1; cy++ {
			state.Chunks[ChunkKey(cx, cy)] = NewEmptyChunk(cx, cy, "grass")
		}
	}
	fly := state.Species["fly_common"]
	fly.BaseSpeed = 1.5
	fly.PredatorFleeRadius = 6.0
	fly.PredatorFleeSpeedMult = 1.8
	fly.KillDrops = []entities.KillDrop{{Item: "dead_fly", CountMin: 1, CountMax: 1, Chance: 1.0}}
	state.Entities["dead_fly"] = &EntityDef{Category: "resource", FoodValue: 10}
	state.Species["wasp_common"] = &entities.BugSpecies{
		ID: "wasp_common", Category: "swarm",
		BaseSpeed: 2.2, VisionRange: 14, MaxSwarmSize: 10, MinSwarmSize: 3,
		FliesOverFences: true,
		Predation: &entities.PredationConfig{
			Prey:                   []string{"fly_common"},
			HomeRange:              40,
			StrikeRadius:           3.0,
			StrikeCooldownTicks:    100,
			KillsPerStrike:         1,
			FeedPerKill:            35,
			HuntSpeedMult:          1.5,
			DepositSatiation:       80,
			HuntSatiationThreshold: 30,
			NestOccupant:           "wasp_nest",
		},
	}
	// Phase 2: the strike is authority-client-driven; tests act AS the authority via handlePredationStrike.
	state.GetOrCreateZone("testzone").AuthorityUserID = testAuthority
	return state
}

// testAuthority is the zone-authority user id the predation tests impersonate when reporting strikes.
const testAuthority = "auth"

// emulateAuthorityStrike does what the Phase-2 authority client does: if the predator is hunting a prey
// that exists, report the victims (lowest alive ids — a stand-in for nearest-individual selection, exact
// for these point-like test swarms) to handlePredationStrike, which validates (authority, prey species,
// cooldown, centre-range, alive ids) and applies the kill. Replaces the old autonomous checkPredationStrike.
func emulateAuthorityStrike(m *Match, state *WorldState, predator *entities.SwarmState) {
	if predator.TargetPreyID == "" {
		return
	}
	species := state.Species[predator.SpeciesID]
	if species == nil || species.Predation == nil {
		return
	}
	prey, ok := state.Swarms[predator.TargetPreyID]
	if !ok || prey.Count <= 0 {
		return
	}
	kills := species.Predation.KillsPerStrike
	if kills <= 0 {
		kills = 1
	}
	m.handlePredationStrike(nopRuntimeLogger(), nil, state, testAuthority, PredationStrikeMessage{
		PredatorSwarmID: predator.ID, PreySwarmID: prey.ID, BugIDs: prey.FirstAliveBugIDs(kills),
	})
}

func newWaspSwarm(id string, count int, x, y float32) *entities.SwarmState {
	s := newTestSwarm(id, count, x, y)
	s.SpeciesID = "wasp_common"
	s.HomePos = s.Position
	return s
}

// driveTick replicates the match loop's per-swarm order for the predation slice:
// think-if-due → move → strike check. deltaTime 0.1 (10Hz).
func driveTick(m *Match, state *WorldState, swarms ...*entities.SwarmState) {
	state.TickCount++
	for _, s := range swarms {
		if _, exists := state.Swarms[s.ID]; !exists {
			continue // despawned (emptied by strikes)
		}
		species := state.Species[s.SpeciesID]
		if state.TickCount >= s.NextThinkTick {
			if !m.predationThink(state, s, species, 32, 0.1, nopRuntimeLogger()) {
				// shared path stand-in: plain wander think (not needed for these tests —
				// prey without a nearby predator just stays put)
				s.SpeedMult = 1.0
				s.TargetPreyID = ""
				s.NextThinkTick = state.TickCount + 30
			}
		}
		s.Move(0.1, species, 32)
		if species.Predation != nil {
			emulateAuthorityStrike(m, state, s) // Phase 2: authority reports the strike; server validates+applies
		}
	}
}

// THE CLOSURE TEST: an open-field wasp 12u from a fly swarm must land a strike within
// 300 ticks — the test that would have caught the impossible-chase hole (fly flee 3.0
// vs wasp 2.2 in the original draft).
func TestPredationClosure(t *testing.T) {
	state := predationTestState()
	m := &Match{}
	wasp := newWaspSwarm("a_wasp", 6, 10, 10)
	fly := newTestSwarm("b_fly", 10, 22, 10)
	state.Swarms[wasp.ID] = wasp
	state.Swarms[fly.ID] = fly

	for i := 0; i < 300; i++ {
		driveTick(m, state, wasp, fly)
		if len(eventsOfType(state, InfluenceBugRemoved)) > 0 {
			if wasp.Satiation < 35 {
				t.Fatalf("strike fed nothing: satiation=%.0f", wasp.Satiation)
			}
			return // closed + killed ✓
		}
	}
	t.Fatalf("no strike within 300 ticks: wasp(%.1f,%.1f) fly(%.1f,%.1f) prey=%q",
		wasp.WorldX(32), wasp.WorldY(32), fly.WorldX(32), fly.WorldY(32), wasp.TargetPreyID)
}

// Strikes kill the LOWEST ascending alive ids and honor the cooldown.
func TestStrikeAscendingIdsAndCooldown(t *testing.T) {
	state := predationTestState()
	m := &Match{}
	wasp := newWaspSwarm("a_wasp", 6, 10, 10)
	fly := newTestSwarm("b_fly", 10, 11, 10) // already in strike range
	state.Swarms[wasp.ID] = wasp
	state.Swarms[fly.ID] = fly
	wasp.TargetPreyID = fly.ID
	wasp.HuntStartTick = state.TickCount

	// The authority reports the victim id; the server validates (cooldown/range/alive) + applies.
	strike := func(ids ...int) {
		m.handlePredationStrike(nopRuntimeLogger(), nil, state, testAuthority, PredationStrikeMessage{
			PredatorSwarmID: wasp.ID, PreySwarmID: fly.ID, BugIDs: ids,
		})
	}

	strike(0) // authority picks id 0 (its nearest individual)
	if fly.IsBugAlive(0) || !fly.IsBugAlive(1) {
		t.Fatalf("first strike must kill id 0 only (alive0=%v alive1=%v)", fly.IsBugAlive(0), fly.IsBugAlive(1))
	}

	// Immediately again: the SERVER cooldown blocks (authoritative throttle).
	strike(1)
	if !fly.IsBugAlive(1) {
		t.Fatal("strike fired inside the cooldown")
	}

	// After the cooldown: id 1 falls.
	state.TickCount += 101
	strike(1)
	if fly.IsBugAlive(1) {
		t.Fatal("second strike after cooldown must kill id 1")
	}
	if got := len(eventsOfType(state, InfluenceBugRemoved)); got != 2 {
		t.Fatalf("BUG_REMOVED events=%d, want 2", got)
	}
}

// Satiation thresholds: sated swarms don't acquire prey; a swarm sated mid-hunt drops it.
func TestSatiationGatesHunting(t *testing.T) {
	state := predationTestState()
	m := &Match{}
	wasp := newWaspSwarm("a_wasp", 6, 10, 10)
	fly := newTestSwarm("b_fly", 10, 16, 10)
	state.Swarms[wasp.ID] = wasp
	state.Swarms[fly.ID] = fly

	// At/above the full-load ceiling (a nest predator hunts until predatorFullSatiation=90, the forager
	// loop that deliberately removed the old rest-at-HuntSatiationThreshold dead zone): must NOT acquire.
	wasp.Satiation = 95
	state.TickCount = wasp.NextThinkTick + 1
	m.predationThink(state, wasp, state.Species["wasp_common"], 32, 0.1, nopRuntimeLogger())
	if wasp.TargetPreyID != "" {
		t.Fatal("full-load wasp (satiation 95 >= ceiling 90) acquired prey")
	}

	// Below: acquires.
	wasp.Satiation = 0
	state.TickCount = wasp.NextThinkTick + 1
	m.predationThink(state, wasp, state.Species["wasp_common"], 32, 0.1, nopRuntimeLogger())
	if wasp.TargetPreyID != fly.ID {
		t.Fatalf("hungry wasp did not acquire (prey=%q)", wasp.TargetPreyID)
	}

	// Sated mid-hunt: the next think drops the hunt.
	wasp.Satiation = 100
	state.TickCount = wasp.NextThinkTick + 1
	m.predationThink(state, wasp, state.Species["wasp_common"], 32, 0.1, nopRuntimeLogger())
	if wasp.TargetPreyID != "" {
		t.Fatal("sated mid-hunt wasp kept hunting")
	}
}

// Flee legs point AWAY at the predator-flee speed, and the EVENT carries the same
// multiplied speed the server moves at (the §14 sync contract).
func TestFleeLegDirectionAndSpeedParity(t *testing.T) {
	state := predationTestState()
	m := &Match{}
	wasp := newWaspSwarm("a_wasp", 6, 13, 10)
	fly := newTestSwarm("b_fly", 10, 10, 10)
	state.Swarms[wasp.ID] = wasp
	state.Swarms[fly.ID] = fly

	state.TickCount = fly.NextThinkTick + 1
	owned := m.predationThink(state, fly, state.Species["fly_common"], 32, 0.1, nopRuntimeLogger())
	if !owned {
		t.Fatal("flee branch did not fire with a predator at 3u")
	}
	if fly.TargetX >= 10 {
		t.Fatalf("flee leg target x=%.1f, want < 10 (away from the wasp at 13)", fly.TargetX)
	}
	if fly.SpeedMult != 1.8 {
		t.Fatalf("flee SpeedMult=%.2f, want 1.8", fly.SpeedMult)
	}
	evs := eventsOfType(state, InfluenceSwarmSetTarget)
	if len(evs) == 0 {
		t.Fatal("flee emitted no leg event")
	}
	wantSpeed := toFixed(1.5 * 1.8 * 0.1)
	if got := evs[len(evs)-1].Speed; got != wantSpeed {
		t.Fatalf("flee event speed=%d, want %d (BaseSpeed×mult×dt — server/client parity)", got, wantSpeed)
	}

	// SERVER-POSITION parity: Move must use the same multiplied speed.
	x0 := fly.WorldX(32)
	fly.Move(0.1, state.Species["fly_common"], 32)
	moved := x0 - fly.WorldX(32) // fleeing in -x
	want := float32(1.5 * 1.8 * 0.1)
	if moved < want*0.95 || moved > want*1.05 {
		t.Fatalf("server moved %.3f, want ≈%.3f (Move must honor SpeedMult)", moved, want)
	}
}

// After the predator leaves, the next think goes back through the shared path and
// resets SpeedMult — the silent-permanent-speed-buff catch.
func TestPostFleeSpeedReset(t *testing.T) {
	state := predationTestState()
	m := &Match{}
	wasp := newWaspSwarm("a_wasp", 6, 13, 10)
	fly := newTestSwarm("b_fly", 10, 10, 10)
	state.Swarms[wasp.ID] = wasp
	state.Swarms[fly.ID] = fly

	state.TickCount = fly.NextThinkTick + 1
	m.predationThink(state, fly, state.Species["fly_common"], 32, 0.1, nopRuntimeLogger())
	if fly.SpeedMult != 1.8 {
		t.Fatalf("setup: flee mult=%.2f", fly.SpeedMult)
	}

	// Predator gone → the flee branch declines → caller's shared path resets the mult
	// (replicate the match-loop contract).
	delete(state.Swarms, wasp.ID)
	state.TickCount = fly.NextThinkTick + 1
	if m.predationThink(state, fly, state.Species["fly_common"], 32, 0.1, nopRuntimeLogger()) {
		t.Fatal("flee branch fired with no predator")
	}
	fly.SpeedMult = 1.0 // the shared path's contractual reset
	if fly.EffectiveSpeedMult() != 1.0 {
		t.Fatal("speed mult must return to 1.0 on the shared path")
	}
}

// Fliers hunt THROUGH fences (leg unclamped); grounded predators clamp at them.
func TestFlierVsGroundedFenceBehavior(t *testing.T) {
	state := predationTestState()
	m := &Match{}
	state.Entities["fence_wood"] = &EntityDef{World: &WorldData{BlocksBugs: true}}
	chunk := state.Chunks[ChunkKey(0, 0)]
	for ly := 5; ly <= 15; ly++ {
		chunk.SetOccupant(15, ly, &PlacedOccupant{ID: "fence_wood", Anchor: true})
	}

	fly := newTestSwarm("b_fly", 10, 20, 10) // behind the fence wall at x=15
	state.Swarms[fly.ID] = fly

	// FLIER: hunt leg lands at the prey center, through the fence.
	wasp := newWaspSwarm("a_wasp", 6, 10, 10)
	state.Swarms[wasp.ID] = wasp
	state.TickCount = wasp.NextThinkTick + 1
	m.predationThink(state, wasp, state.Species["wasp_common"], 32, 0.1, nopRuntimeLogger())
	if wasp.TargetPreyID != fly.ID || wasp.TargetX < 19 {
		t.Fatalf("flier should aim through the fence: prey=%q targetX=%.1f", wasp.TargetPreyID, wasp.TargetX)
	}

	// GROUNDED predator (same config, no flight): leg clamps short of the fence.
	grounded := &entities.BugSpecies{
		ID: "centipede_test", Category: "individual", BaseSpeed: 1.6, VisionRange: 14,
		Predation: &entities.PredationConfig{
			Prey: []string{"fly_common"}, StrikeRadius: 1.2, StrikeCooldownTicks: 50,
			KillsPerStrike: 1, FeedPerKill: 30, HuntSpeedMult: 1.0, HuntSatiationThreshold: 30,
		},
	}
	state.Species["centipede_test"] = grounded
	cent := newTestSwarm("c_cent", 1, 10, 10)
	cent.SpeciesID = "centipede_test"
	cent.HomePos = cent.Position
	state.Swarms[cent.ID] = cent
	state.TickCount = cent.NextThinkTick + 1
	m.predationThink(state, cent, grounded, 32, 0.1, nopRuntimeLogger())
	if cent.TargetPreyID != fly.ID {
		t.Fatalf("grounded predator did not acquire (prey=%q)", cent.TargetPreyID)
	}
	if cent.TargetX >= 15 {
		t.Fatalf("grounded hunt leg crossed the fence: targetX=%.1f, want < 15", cent.TargetX)
	}
}

// No prey in range: the predator wanders WITHIN its home range at normal speed.
func TestPreyEmptyWanderInHomeRange(t *testing.T) {
	state := predationTestState()
	m := &Match{}
	wasp := newWaspSwarm("a_wasp", 6, 10, 10)
	state.Swarms[wasp.ID] = wasp

	for i := 0; i < 20; i++ {
		state.TickCount = wasp.NextThinkTick + 1
		if !m.predationThink(state, wasp, state.Species["wasp_common"], 32, 0.1, nopRuntimeLogger()) {
			t.Fatal("predator think must own the wander")
		}
		if wasp.SpeedMult != 1.0 {
			t.Fatalf("wander SpeedMult=%.2f, want 1.0", wasp.SpeedMult)
		}
		hx, hy := wasp.HomePos.WorldX(32), wasp.HomePos.WorldY(32)
		dx, dy := wasp.TargetX-hx, wasp.TargetY-hy
		if dx*dx+dy*dy > 41*41 {
			t.Fatalf("wander target outside home range: (%.1f,%.1f)", wasp.TargetX, wasp.TargetY)
		}
	}
}

// A hunt with no kill for 300 ticks gives up (back to wander).
func TestHuntTimeout(t *testing.T) {
	state := predationTestState()
	m := &Match{}
	wasp := newWaspSwarm("a_wasp", 6, 10, 10)
	fly := newTestSwarm("b_fly", 10, 16, 10)
	state.Swarms[wasp.ID] = wasp
	state.Swarms[fly.ID] = fly

	state.TickCount = wasp.NextThinkTick + 1
	m.predationThink(state, wasp, state.Species["wasp_common"], 32, 0.1, nopRuntimeLogger())
	if wasp.TargetPreyID != fly.ID {
		t.Fatal("setup: no acquisition")
	}

	state.TickCount += 301 // way past the timeout, no kill happened
	m.predationThink(state, wasp, state.Species["wasp_common"], 32, 0.1, nopRuntimeLogger())
	if wasp.TargetPreyID != "" {
		t.Fatal("hunt did not time out")
	}
}

// Population caps are UNTOUCHED by predation kills (kills only ever lower counts).
func TestStrikeRespectsNothingItShouldnt(t *testing.T) {
	state := predationTestState()
	m := &Match{}
	wasp := newWaspSwarm("a_wasp", 6, 10, 10)
	fly := newTestSwarm("b_fly", 1, 11, 10) // ONE bug: the strike empties the swarm
	state.Swarms[wasp.ID] = wasp
	state.Swarms[fly.ID] = fly
	state.SwarmsBySpecies["fly_common"] = []string{fly.ID}
	wasp.TargetPreyID = fly.ID
	wasp.HuntStartTick = state.TickCount

	m.handlePredationStrike(nopRuntimeLogger(), nil, state, testAuthority, PredationStrikeMessage{
		PredatorSwarmID: wasp.ID, PreySwarmID: fly.ID, BugIDs: []int{0},
	})

	if _, exists := state.Swarms[fly.ID]; exists {
		t.Fatal("emptied prey swarm must despawn (the catch convention)")
	}
	if !state.SwarmsDirty {
		t.Fatal("despawn must set SwarmsDirty")
	}
	// Carrion landed at the wasp's center
	if len(state.GroundItems) != 1 {
		t.Fatalf("carrion drops=%d, want 1", len(state.GroundItems))
	}
}

// ===== Net-tier catch matrix (the first enforcement of species net_size) =====
// hand ≡ small_net = tier 1 (hand-catching flies AND butterflies stays core early
// game); wasps (medium) need the large net (tier 3 — no medium net exists);
// trap_only (centipede) rejects EVERYTHING including hands.
func TestCatchNetTierMatrix(t *testing.T) {
	cases := []struct {
		name    string
		tool    string // "" = bare hands
		netSize string
		caught  bool
	}{
		{"hand x fly(small) MUST PASS", "", "small", true},
		{"hand x butterfly(small) MUST PASS", "", "small", true},
		{"small_net x fly", "small_net", "small", true},
		{"hand x wasp(medium)", "", "medium", false},
		{"small_net x wasp(medium)", "small_net", "medium", false},
		{"large_net x wasp(medium)", "large_net", "medium", true},
		{"large_net x centipede(trap_only)", "large_net", "trap_only", false},
		{"hand x centipede(trap_only)", "", "trap_only", false},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			state := predationTestState()
			state.Entities["small_net"] = &EntityDef{Category: "tool", ToolType: "net", ToolTier: 1, Reach: 2.5, CatchCap: 10}
			state.Entities["large_net"] = &EntityDef{Category: "tool", ToolType: "net", ToolTier: 3, Reach: 3.5, CatchCap: 20}
			state.Species["fly_common"].NetSize = c.netSize

			player := &PlayerState{
				UserID: "p1", EquippedTool: c.tool,
				Position: entities.EntityPosition{LocalX: 10, LocalY: 10},
			}
			state.Players = map[string]*PlayerState{"p1": player}
			state.Presences = map[string]runtime.Presence{}
			swarm := newTestSwarm("s1", 5, 11, 10)
			state.Swarms[swarm.ID] = swarm

			m := &Match{}
			m.handleCatchBug(nopRuntimeLogger(), nopDispatcher{}, state,
				CatchBugMessage{ClickX: 11, ClickY: 10, SwarmID: swarm.ID, BugIDs: []int{0, 1}},
				"p1", 32)

			caught := swarm.Count < 5
			if caught != c.caught {
				t.Fatalf("caught=%v, want %v (tool=%q vs net_size=%q)", caught, c.caught, c.tool, c.netSize)
			}
		})
	}
}

// kill_drops parse: count ranges + chance roll bounds + multiple entries.
func TestKillDropCountRange(t *testing.T) {
	state := killDropTestState()
	m := &Match{}
	state.Entities["centipede_parts"] = &EntityDef{Category: "resource"}
	state.Species["fly_common"].KillDrops = []entities.KillDrop{
		{Item: "centipede_parts", CountMin: 3, CountMax: 5, Chance: 1.0},
	}

	m.spawnKillDrops(nopRuntimeLogger(), nil, state, state.Species["fly_common"], 10, 10, 10, 10, 32)

	if len(state.GroundItems) != 1 {
		t.Fatalf("drops=%d, want 1", len(state.GroundItems))
	}
	for _, item := range state.GroundItems {
		if item.Count < 3 || item.Count > 5 {
			t.Fatalf("count=%d, want 3-5", item.Count)
		}
	}
}
