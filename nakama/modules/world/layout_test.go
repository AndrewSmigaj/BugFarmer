package world

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// layoutState is a 64 x 64 zone (2 x 2 chunks) of grass, its authored chunks already in the cache baseChunk reads.
func layoutState() *WorldState {
	s := &WorldState{CurrentZone: &ZoneConfig{ZoneID: "layout_fp", Width: 64, Height: 64}, BaseChunks: map[string]*ChunkData{}}
	for cy := 0; cy < 2; cy++ {
		for cx := 0; cx < 2; cx++ {
			s.BaseChunks[ChunkKey(cx, cy)] = NewEmptyChunk(cx, cy, "grass")
		}
	}
	return s
}

func TestLayoutFingerprint(t *testing.T) {
	fp := func(edit func(*WorldState)) string {
		s := layoutState()
		if edit != nil {
			edit(s)
		}
		return s.layoutFingerprint("data/zones/layout_fp")
	}
	base := fp(nil)
	if base == "" || fp(nil) != base {
		t.Fatalf("the same layout must give the same fingerprint: %q / %q", base, fp(nil))
	}
	fence := func(raw string) func(*WorldState) {
		return func(s *WorldState) { s.BaseChunks[ChunkKey(1, 1)].Occupants[3][4] = json.RawMessage(raw) }
	}
	for name, edit := range map[string]func(*WorldState){
		"a ground tile":   func(s *WorldState) { s.BaseChunks[ChunkKey(1, 0)].Ground[5][6] = "dirt" },
		"an occupant":     fence(`{"id":"fence_wood"}`),
		"the zone's size": func(s *WorldState) { s.CurrentZone.Width = 96 },
	} {
		if fp(edit) == base {
			t.Errorf("changing %s must change the fingerprint", name)
		}
	}
	if fp(fence(`{"id":"fence_wood"}`)) != fp(fence("{ \"id\" :  \"fence_wood\" }")) {
		t.Errorf("the occupant's JSON spacing must not change the fingerprint")
	}
	if fp(fence("null")) != base {
		t.Errorf("an empty occupant written as null must be the same as an empty cell")
	}
	roof := func(s *WorldState) {
		c := s.BaseChunks[ChunkKey(0, 0)]
		c.Roof = make([][]bool, ChunkSize)
		for i := range c.Roof {
			c.Roof[i] = make([]bool, ChunkSize)
		}
		c.Roof[2][2] = true
	}
	if fp(roof) != base {
		t.Errorf("the roof map (lighting only) must not change the fingerprint")
	}
}

func TestDecideLayout(t *testing.T) {
	rules := func(r ...LayoutMigration) *ZoneConfig { return &ZoneConfig{LayoutMigrations: r} }
	for _, c := range []struct {
		name        string
		saved, now  string
		zone        *ZoneConfig
		want        layoutDecision
		whyMentions string
	}{
		{"no layout recorded (a format-1 save)", "", "new", rules(), layoutLoad, "made before layouts were recorded"},
		{"the same layout", "new", "new", rules(), layoutLoad, ""},
		{"another layout, no rule", "old", "new", rules(), layoutRefuse, `"from": "old"`},
		{"a rule for another fingerprint only", "old", "new", rules(LayoutMigration{From: "older", KeepEdits: true}), layoutRefuse, "old"},
		{"keep its edits", "old", "new", rules(LayoutMigration{From: "old", KeepEdits: true}), layoutLoad, "loaded with its edits"},
		{"start fresh", "old", "new", rules(LayoutMigration{From: "old"}), layoutSetAside, "set aside"},
		{"any other layout starts fresh", "old", "new", rules(LayoutMigration{From: "*"}), layoutSetAside, "set aside"},
		{"an exact rule beats * (after it)", "old", "new",
			rules(LayoutMigration{From: "*"}, LayoutMigration{From: "old", KeepEdits: true}), layoutLoad, "loaded with its edits"},
		{"an exact rule beats * (before it)", "old", "new",
			rules(LayoutMigration{From: "old", KeepEdits: true}, LayoutMigration{From: "*"}), layoutLoad, "loaded with its edits"},
		{"a bench zone starts fresh by itself", "old", "new", &ZoneConfig{BenchOf: "village_21_B"}, layoutSetAside, "bench"},
		{"a bench zone's rule still counts", "old", "new",
			&ZoneConfig{BenchOf: "village_21_B", LayoutMigrations: []LayoutMigration{{From: "old", KeepEdits: true}}}, layoutLoad, "loaded"},
	} {
		got, why := decideLayout(c.saved, c.now, c.zone)
		if got != c.want || !strings.Contains(why, c.whyMentions) {
			t.Errorf("%s: got %v %q, want %v mentioning %q", c.name, got, why, c.want, c.whyMentions)
		}
	}
}

// startLayoutZone starts zone "layouttest" (64 x 64 grass, the given extra zone.json fields) from a temporary data
// folder, with `save` (if any) as its stored world save.
func startLayoutZone(t *testing.T, nk *memStorage, extra string) *WorldState {
	t.Helper()
	dir := t.TempDir()
	zoneDir := filepath.Join(dir, "data", "zones", "layouttest")
	if err := os.MkdirAll(zoneDir, 0o755); err != nil {
		t.Fatal(err)
	}
	cfg := `{"zone_id":"layouttest","name":"layout test","width":64,"height":64,"spawn_point":[32,32]` + extra + `}`
	if err := os.WriteFile(filepath.Join(zoneDir, "zone.json"), []byte(cfg), 0o644); err != nil {
		t.Fatal(err)
	}
	t.Chdir(dir)
	state, _, _ := (&Match{}).MatchInit(t.Context(), nopRuntimeLogger(), nil, nk, map[string]interface{}{
		"world_id": "w", "owner_id": "o", "zone_id": "layouttest",
	})
	ws, _ := state.(*WorldState)
	return ws
}

func TestMatchInitFollowsTheLayoutRules(t *testing.T) {
	zoneKey := ZoneStateKey("layouttest", "")
	saveKey := memKey(ZoneStateCollection, "", worldSaveKey(zoneKey))
	saveOn := func(layout string) string {
		return fmt.Sprintf(`{"version":%d,"zone_id":"layouttest","layout":%q,"tick":500,"swarms":[]}`, worldSaveVersion, layout)
	}

	// The zone's own fingerprint, from a start with no save; that start also records it in what it would save.
	ws := startLayoutZone(t, newMemStorage(), "")
	if ws == nil || ws.LayoutFingerprint == "" {
		t.Fatal("the zone must start with no save and know its layout")
	}
	current := ws.LayoutFingerprint
	if got := (&Match{}).buildWorldSave(ws).Layout; got != current {
		t.Fatalf("a save must record the layout it was made on: %q, want %q", got, current)
	}

	t.Run("same layout loads", func(t *testing.T) {
		nk := newMemStorage()
		nk.objs[saveKey] = saveOn(current)
		if ws := startLayoutZone(t, nk, ""); ws == nil || ws.TickCount != 500 {
			t.Fatalf("a save made on this layout must load")
		}
	})
	t.Run("another layout without a rule is refused", func(t *testing.T) {
		nk := newMemStorage()
		nk.objs[saveKey] = saveOn("elsewhere")
		if ws := startLayoutZone(t, nk, ""); ws != nil {
			t.Fatal("the zone started over a save made on another layout")
		}
		if nk.objs[saveKey] != saveOn("elsewhere") || len(nk.objs) != 1 {
			t.Errorf("storage was changed: %v", nk.objs)
		}
	})
	t.Run("keep_edits loads it", func(t *testing.T) {
		nk := newMemStorage()
		nk.objs[saveKey] = saveOn("elsewhere")
		ws := startLayoutZone(t, nk, `,"layout_migrations":[{"from":"elsewhere","keep_edits":true}]`)
		if ws == nil || ws.TickCount != 500 {
			t.Fatal("a keep_edits rule must load the save")
		}
	})
	for name, extra := range map[string]string{
		"a fresh rule sets it aside":           `,"layout_migrations":[{"from":"*","keep_edits":false}]`,
		"a bench zone sets it aside by itself": `,"bench_of":"village_21_B"`,
	} {
		t.Run(name, func(t *testing.T) {
			nk := newMemStorage()
			nk.objs[saveKey] = saveOn("elsewhere")
			ws := startLayoutZone(t, nk, extra)
			if ws == nil || ws.TickCount != 0 {
				t.Fatal("the zone must start fresh, without the old save")
			}
			if kept := nk.objs[memKey(ZoneStateCollection, "", layoutBackupKey(zoneKey, "elsewhere"))]; kept != saveOn("elsewhere") {
				t.Errorf("the set-aside save must be kept untouched: %q", kept)
			}
			if nk.objs[saveKey] != saveOn("elsewhere") {
				t.Errorf("starting must not rewrite the save itself (the next save replaces it)")
			}
		})
	}
}
