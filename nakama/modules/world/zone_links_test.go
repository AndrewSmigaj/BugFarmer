package world

import (
	"os"
	"path/filepath"
	"sort"
	"testing"
)

// zoneLinkExceptions are one-way links kept on purpose, each with the reason. Keep this list short: every entry
// is a place where walking out of a zone and turning round does not bring you back.
var zoneLinkExceptions = map[string]string{
	// village_21_B is the candidate replacement for village_21 ("if it wins, it becomes THE village" —
	// docs/product/zones/village_21_B.md); every newer zone links to village_21_B, so the old village's south
	// exit comes back north into village_21_B. Which village is the real one is an open owner question
	// (docs/gdd/01_world.md); resolve this entry with it.
	"village_21/south": "legacy village pending the village_21 vs village_21_B decision",
}

// TestZoneNeighbourLinksAreConsistent walks the SAVED zones (nakama/data/zones — what the game loads) and checks
// the world map they form: a zone's id matches its folder; every neighbour it names exists; the neighbour names
// it back from the opposite edge; the two sit next to each other on the world grid (row 0 is the north-most row,
// so "north" is one row up); and the shared edge has the same length on both sides, so a crossing lands at the
// matching spot. A broken link is a real bug: a one-way link strands a player on the far side, and a link to a
// missing zone used to make the server borrow — and overwrite — the village's save.
//
// tools/run_go_tests.sh mounts nakama/data at /data, so ../../data resolves inside the test container exactly as
// it does in the repo.
func TestZoneNeighbourLinksAreConsistent(t *testing.T) {
	root := filepath.Join("..", "..", "data", "zones")
	entries, err := os.ReadDir(root)
	if err != nil {
		t.Fatalf("cannot read the zone data at %s — run the tests with tools/run_go_tests.sh, which mounts it: %v", root, err)
	}
	zones := map[string]*ZoneConfig{}
	for _, e := range entries {
		if !e.IsDir() {
			continue
		}
		if _, err := os.Stat(filepath.Join(root, e.Name(), "zone.json")); err != nil {
			continue
		}
		cfg, err := LoadZoneConfig(filepath.Join(root, e.Name()))
		if err != nil {
			t.Errorf("%s: %v", e.Name(), err)
			continue
		}
		if cfg.ZoneID != e.Name() {
			t.Errorf("%s/zone.json says zone_id %q — the folder name and the id must match", e.Name(), cfg.ZoneID)
		}
		zones[e.Name()] = cfg
	}
	if len(zones) == 0 {
		t.Fatalf("no zones found under %s", root)
	}

	opposite := map[string]string{"north": "south", "south": "north", "east": "west", "west": "east"}
	step := map[string][2]int{"north": {-1, 0}, "south": {1, 0}, "east": {0, 1}, "west": {0, -1}} // {row, col}
	ids := make([]string, 0, len(zones))
	for id := range zones {
		ids = append(ids, id)
	}
	sort.Strings(ids)
	links := 0
	for _, id := range ids {
		z := zones[id]
		for dir, to := range z.Neighbors {
			if to == "" {
				continue
			}
			links++
			back, ok := opposite[dir]
			if !ok {
				t.Errorf("%s: neighbour direction %q is not north/south/east/west", id, dir)
				continue
			}
			n, exists := zones[to]
			if !exists {
				t.Errorf("%s --%s--> %s: there is no zone %q in the zone data", id, dir, to, to)
				continue
			}
			if n.Neighbors[back] != id {
				if _, allowed := zoneLinkExceptions[id+"/"+dir]; !allowed {
					t.Errorf("%s --%s--> %s is one-way: %s's %s edge leads to %q, not back to %s",
						id, dir, to, to, back, n.Neighbors[back], id)
				}
			}
			if want := [2]int{z.Row + step[dir][0], z.Col + step[dir][1]}; [2]int{n.Row, n.Col} != want {
				t.Errorf("%s (row %d, col %d) --%s--> %s, but %s sits at row %d, col %d (expected row %d, col %d)",
					id, z.Row, z.Col, dir, to, to, n.Row, n.Col, want[0], want[1])
			}
			if (dir == "north" || dir == "south") && z.Width != n.Width {
				t.Errorf("%s --%s--> %s: the shared edge is %d cells wide on one side and %d on the other", id, dir, to, z.Width, n.Width)
			}
			if (dir == "east" || dir == "west") && z.Height != n.Height {
				t.Errorf("%s --%s--> %s: the shared edge is %d cells tall on one side and %d on the other", id, dir, to, z.Height, n.Height)
			}
		}
	}
	for key := range zoneLinkExceptions { // an exception that is no longer needed must go, so the list stays honest
		dir, id := filepath.Base(key), filepath.Dir(key)
		z, ok := zones[id]
		if !ok || z.Neighbors[dir] == "" {
			t.Errorf("stale exception %q: that link no longer exists — delete the entry", key)
		} else if n, ok := zones[z.Neighbors[dir]]; ok && n.Neighbors[opposite[dir]] == id {
			t.Errorf("stale exception %q: the link now points back correctly — delete the entry", key)
		}
	}
	if links == 0 {
		t.Fatalf("no zone links found — the zone data looks wrong")
	}
}
