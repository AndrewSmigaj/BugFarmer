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

	"bugfarmer/entities"
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

// TestCompositeMaterials: a solid id resolves to itself; a composite splits into its TWO materials
// (ignoring the shape). This is what makes place/dig cost/drop BOTH materials of a composite tile.
func TestCompositeMaterials(t *testing.T) {
	cases := map[string][]string{
		"dirt":              {"dirt"},
		"dug_soil":          {"dug_soil"},
		"grass~dirt~diagNE": {"grass", "dirt"},
		"sand~stone_floor~halfN": {"sand", "stone_floor"},
	}
	for in, want := range cases {
		got := CompositeMaterials(in)
		if len(got) != len(want) {
			t.Errorf("CompositeMaterials(%q) = %v, want %v", in, got, want)
			continue
		}
		for i := range want {
			if got[i] != want[i] {
				t.Errorf("CompositeMaterials(%q) = %v, want %v", in, got, want)
				break
			}
		}
	}
}

// TestGroundRecipeIngredients: a solid tile costs its one material's recipe; a COMPOSITE costs the UNION of
// both materials' recipes, with duplicate items SUMMED (a sandwich needs bread AND filling). First-seen order.
func TestGroundRecipeIngredients(t *testing.T) {
	w := &WorldState{GroundRecipes: map[string][]entities.RecipeIO{
		"stone_floor": {{Item: "stone", Count: 2}},
		"stone_path":  {{Item: "stone", Count: 1}},
		"grass":       {{Item: "grass_turf", Count: 1}},
		"wood_floor":  {{Item: "plank", Count: 2}},
	}}

	// Solid: just its own recipe.
	if got := w.groundRecipeIngredients("grass"); len(got) != 1 || got[0].Item != "grass_turf" || got[0].Count != 1 {
		t.Errorf("solid grass = %+v, want [grass_turf x1]", got)
	}
	// Composite with a SHARED item -> summed (stone 2 + stone 1 = 3), single entry.
	got := w.groundRecipeIngredients("stone_floor~stone_path~diagNE")
	if len(got) != 1 || got[0].Item != "stone" || got[0].Count != 3 {
		t.Errorf("stone_floor~stone_path = %+v, want [stone x3]", got)
	}
	// Composite with distinct items -> union, first-seen order (grass_turf then plank).
	got = w.groundRecipeIngredients("grass~wood_floor~halfN")
	if len(got) != 2 || got[0].Item != "grass_turf" || got[1].Item != "plank" || got[1].Count != 2 {
		t.Errorf("grass~wood_floor = %+v, want [grass_turf x1, plank x2]", got)
	}
	// Unknown / dug_soil (no recipe) -> empty (not diggable, not placeable).
	if got := w.groundRecipeIngredients("dug_soil"); len(got) != 0 {
		t.Errorf("dug_soil = %+v, want empty", got)
	}
}

// TestGroundShortfall: reports only the ingredients the player LACKS ("Need N item, ..."), "" when affordable.
func TestGroundShortfall(t *testing.T) {
	p := &PlayerState{}
	p.AddItem("stone", 1) // hold 1 stone, no plank

	ings := []entities.RecipeIO{{Item: "stone", Count: 2}, {Item: "plank", Count: 2}}
	short := groundShortfall(p, ings)
	if !strings.Contains(short, "1 stone") || !strings.Contains(short, "2 plank") {
		t.Errorf("shortfall = %q, want it to name '1 stone' (2 needed - 1 held) and '2 plank'", short)
	}
	// Affordable -> empty string.
	p.AddItem("stone", 1)
	p.AddItem("plank", 2)
	if s := groundShortfall(p, ings); s != "" {
		t.Errorf("shortfall with enough held = %q, want empty", s)
	}
}

// TestDigHitsFor: stone-family floors are tougher (3 hits); soft ground gives after 2.
func TestDigHitsFor(t *testing.T) {
	cases := map[string]int{
		"stone_floor": 3, "stone_path": 3, "cave_floor": 3,
		"grass": 2, "dirt": 2, "sand": 2, "mud": 2, "wood_floor": 2,
		"grass~dirt~diagNE":       2, // composite judged by primary material (grass)
		"stone_floor~grass~diagNE": 3, // primary = stone_floor
	}
	for id, want := range cases {
		if got := digHitsFor(id); got != want {
			t.Errorf("digHitsFor(%q) = %d, want %d", id, got, want)
		}
	}
}
