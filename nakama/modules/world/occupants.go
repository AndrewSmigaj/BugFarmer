package world

// PlacedOccupant is stored in chunk data for all footprint cells.
// Anchor cell has Anchor=true, footprint cells have Anchor=false (omitted in JSON).
type PlacedOccupant struct {
	ID     string `json:"id"`
	Dir    int    `json:"dir,omitempty"`    // 0=down, 1=left, 2=right, 3=up
	Anchor bool   `json:"anchor,omitempty"` // true for anchor cell, false/omitted for footprint
	Text   string `json:"text,omitempty"`   // per-placement authored text (signs); read-only at runtime
}
