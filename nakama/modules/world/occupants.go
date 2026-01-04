package world

// PlacedOccupant is stored in chunk data at anchor cell.
// Blocked cells store "@" marker string.
type PlacedOccupant struct {
	ID  string `json:"id"`
	Dir int    `json:"dir,omitempty"` // 0=down, 1=left, 2=right, 3=up
}
