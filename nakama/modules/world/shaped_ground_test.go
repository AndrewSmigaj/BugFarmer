package world

// Tests for the shaped-ground builder's server-side authority: PrimaryMaterial (the composite -> base
// resolver that keeps walkability/water/planting correct on shaped tiles) and ValidateShovelGround (the
// ONLY guard on the player-chosen ground id). These are the M2 gate — each case fails if the helper is
// reverted to a plain-string comparison.
//
// Run inside the builder image:  go test ./modules/world/ -run 'ShapedGround|ShovelGround|PrimaryMaterial' -v

import (
	"strings"
	"testing"
)

func TestPrimaryMaterial(t *testing.T) {
	cases := map[string]string{
		"grass":              "grass",             // plain id unchanged
		"grass~dirt~diagNE":  "grass",             // composite -> matA
		"water_deep":         "water_deep",        // plain water unchanged (collision must still fire)
		"":                   "",                  // empty stays empty
		"stone_floor~mud~quadNE": "stone_floor",   // multi-underscore matA preserved
	}
	for in, want := range cases {
		if got := PrimaryMaterial(in); got != want {
			t.Errorf("PrimaryMaterial(%q) = %q, want %q", in, got, want)
		}
	}
}

func TestValidateShovelGround_Valid(t *testing.T) {
	valid := []string{
		"grass",                // plain decorative material
		"dirt",
		"grass~dirt~diagNE",    // composite of two decorative materials + a known shape
		"sand~stone_floor~halfN",
		"mud~cave_floor~quadSW",
		"wood_floor~stone_path~full",
	}
	for _, id := range valid {
		if got, ok := ValidateShovelGround(id); !ok || got != id {
			t.Errorf("ValidateShovelGround(%q) = (%q,%v), want (%q,true)", id, got, ok, id)
		}
	}
}

func TestValidateShovelGround_Rejected(t *testing.T) {
	rejected := []string{
		"",                          // empty
		"water_shallow",             // water is not a placeable material (excluded)
		"water_deep~dirt~diagNE",    // composite water primary -> the desync-risk case, must be rejected
		"grass~water_deep~diagNE",   // composite water secondary -> rejected
		"garden_plot",               // tilled soil is the hoe's system
		"rug_small",                 // rugs are their own (future) system
		"grass~dirt~bogus",          // unknown shape
		"grass~dirt",                // wrong arity (missing shape)
		"grass~dirt~diagNE~extra",   // too many parts
		"unknownmat~dirt~diagNE",    // unknown material
		strings.Repeat("grass~dirt~diagNE", 5), // over the length cap
	}
	for _, id := range rejected {
		if got, ok := ValidateShovelGround(id); ok {
			t.Errorf("ValidateShovelGround(%q) = (%q,true), want rejected", id, got)
		}
	}
}

func TestGroundMaterialItem(t *testing.T) {
	cases := map[string]string{
		"grass":       "grass_turf",
		"dirt":        "dirt",
		"sand":        "sand",
		"mud":         "mud",
		"stone_floor": "stone", // stone family collapses to one block
		"stone_path":  "stone",
		"cave_floor":  "stone",
		"wood_floor":  "wood",
		"water_deep":  "", // not diggable/placeable via terraform
		"garden_plot": "",
	}
	for mat, want := range cases {
		if got := GroundMaterialItem(mat); got != want {
			t.Errorf("GroundMaterialItem(%q) = %q, want %q", mat, got, want)
		}
	}
}

// TestShovelInventoryRoundTrip exercises the grant/consume plumbing the terraform loop relies on: a dig
// grants a block (AddItem), a place finds+consumes it (FindItemSlot+RemoveItem), and consuming what you
// don't have fails cleanly.
func TestShovelInventoryRoundTrip(t *testing.T) {
	p := &PlayerState{} // [40]InventorySlot, all empty; itemCap falls back to 40

	if p.FindItemSlot("grass_turf") != -1 {
		t.Fatal("expected no grass_turf before digging")
	}
	// Dig grants a block.
	if slot := p.AddItem("grass_turf", 1); slot < 0 {
		t.Fatal("AddItem(grass_turf) failed")
	}
	slot := p.FindItemSlot("grass_turf")
	if slot < 0 {
		t.Fatal("FindItemSlot did not locate the granted grass_turf")
	}
	// Place consumes it.
	if !p.RemoveItem(slot, 1) {
		t.Fatal("RemoveItem(grass_turf) failed")
	}
	if p.FindItemSlot("grass_turf") != -1 {
		t.Error("grass_turf should be gone after placing")
	}
	// Placing a material you don't hold must fail (FindItemSlot returns -1).
	if p.FindItemSlot("stone") != -1 {
		t.Error("expected no stone block held")
	}
}
