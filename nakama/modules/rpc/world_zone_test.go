package rpc

import (
	"os"
	"path/filepath"
	"testing"
)

// An unknown zone must be refused before any match exists for it (it used to fall back to village_21
// and write village_21's save from a second match).
func TestZoneExistsRefusesUnknownAndMalformedZones(t *testing.T) {
	root := t.TempDir()
	old := zonesRoot
	zonesRoot = root
	defer func() { zonesRoot = old }()

	if err := os.MkdirAll(filepath.Join(root, "village_21_B"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, "village_21_B", "zone.json"), []byte("{}"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(filepath.Join(root, "folder_only"), 0o755); err != nil {
		t.Fatal(err)
	}

	cases := []struct {
		id   string
		want bool
	}{
		{"village_21_B", true}, // the canonical village — its id has a capital letter
		{"ant_colony_40", false},
		{"folder_only", false},
		{"../secrets", false},
		{"", false},
	}
	for _, c := range cases {
		if got := zoneExists(c.id); got != c.want {
			t.Errorf("zoneExists(%q) = %v, want %v", c.id, got, c.want)
		}
	}

	if err := os.MkdirAll(filepath.Join(root, "bee_meadow_20"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, "bee_meadow_20", "zone.json"), []byte("{}"), 0o644); err != nil {
		t.Fatal(err)
	}
	if !zoneExists("bee_meadow_20") {
		t.Errorf("zoneExists(bee_meadow_20) = false, want true for an authored zone")
	}
}
