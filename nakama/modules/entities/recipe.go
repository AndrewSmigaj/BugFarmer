package entities

// RecipeIO is one ingredient or output: an item id and a count.
type RecipeIO struct {
	Item  string `json:"item"`
	Count int    `json:"count"`
}

// RecipeDef is a crafting recipe (loaded from data/entities/recipes.json). The server is the
// sole authority for consuming inputs and producing outputs; the client reads the same data to
// render the panel (have/need, output preview).
//
// There is NO quick/slow mode — speed is the single ProcessTicks knob (10Hz: a workbench tool is
// ~8 ticks ≈ instant; a furnace smelt is 200 ≈ 20s). Crafting outputs are display/inventory state
// and NEVER enter the deterministic sim hash; only a station whose OUTPUT is an insect food/
// breeding source registers on the food ledger (that path stays on StationState, not here).
type RecipeDef struct {
	ID           string     `json:"-"`                  // set from the map key during load
	Station      string     `json:"station"`            // placeable entity id whose panel offers this recipe
	Inputs       []RecipeIO `json:"inputs"`             // consumed per craft
	Output       RecipeIO   `json:"output"`             // produced per craft
	ProcessTicks int        `json:"process_ticks"`      // ticks to convert one batch (the ONLY speed knob)
	Catalyst     *RecipeIO  `json:"catalyst,omitempty"` // optional required+consumed extra (e.g. fuel)
	Unlock       string     `json:"unlock,omitempty"`   // "" / "default" = always; "shop:<npc>" | "find" = gated (must learn)
	Collection   string     `json:"collection,omitempty"` // optional "recipe book" group; a shop book-entry grants every recipe sharing this collection
}
