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
