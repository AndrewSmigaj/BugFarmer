package world

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/heroiclabs/nakama-common/runtime"
)

// CharacterCollection is the Nakama storage collection holding per-character saves.
// Records are USER-OWNED (key = charID, UserID = the account) with PermissionWrite:0 so a client
// can list/read its own characters but can NEVER write inventory/coins (server-only writes).
const CharacterCollection = "character"

// Appearance is the cosmetic identity chosen at character creation (drives the paper-doll composer).
type Appearance struct {
	Class string `json:"class"` // paper-doll class set (e.g. "merchant")
	Hair  string `json:"hair"`  // hair color
	Skin  string `json:"skin"`  // body skin tone (default|tan|deep)
}

// CharacterSave is the persisted, zone-independent state of ONE character (Terraria-style: an account
// may own several). It is the unit of persistence — loaded on join, written on leave. NONE of it is in
// the bug-sim state hash, so it never touches the frontier-gated deterministic system.
type CharacterSave struct {
	Version           int               `json:"version"`
	CharID            string            `json:"char_id"`
	Name              string            `json:"name"`
	Appearance        Appearance        `json:"appearance"`
	Coins             int64             `json:"coins"`
	BugSlots          [20]InventorySlot `json:"bug_slots"`
	ItemSlots         [40]InventorySlot `json:"item_slots"`
	ItemSlotsUnlocked int               `json:"item_slots_unlocked"`
	Equipment         [8]string         `json:"equipment"`
	EquippedTool      string            `json:"equipped_tool"`
	HP                int               `json:"hp"`
	MaxHP             int               `json:"max_hp"`
	// Home (set by sleeping in a bed) + last logout location.
	HomeZone     string  `json:"home_zone"`
	HomeX        float32 `json:"home_x"`
	HomeY        float32 `json:"home_y"`
	LastZone     string  `json:"last_zone"`
	LastX        float32 `json:"last_x"`
	LastY        float32 `json:"last_y"`
	IntroSeen    bool    `json:"intro_seen"`
	CreatedAt    int64   `json:"created_at"`
	LastPlayedAt int64   `json:"last_played_at"`
	// Gated recipes the character has learned (bought/found). Basic auto-unlock recipes are NOT stored.
	KnownRecipes []string `json:"known_recipes,omitempty"`
}

// CharacterSummary is the lightweight view for the select screen (no full inventory).
type CharacterSummary struct {
	CharID       string     `json:"char_id"`
	Name         string     `json:"name"`
	Appearance   Appearance `json:"appearance"`
	LastZone     string     `json:"last_zone"`
	LastPlayedAt int64      `json:"last_played_at"`
}

// DefaultCharacterSave builds a brand-new character's save: the starting kit (the single source of
// truth shared with AddPlayer, via applyStartingKit) + the chosen name/appearance. Home/Last are empty
// and IntroSeen=false → first login spawns at the zone's spawn_point with the intro.
func DefaultCharacterSave(charID, name string, app Appearance, now int64) *CharacterSave {
	var tmp PlayerState
	applyStartingKit(&tmp)
	return &CharacterSave{
		Version:           1,
		CharID:            charID,
		Name:              name,
		Appearance:        app,
		Coins:             tmp.Coins,
		BugSlots:          tmp.BugSlots,
		ItemSlots:         tmp.ItemSlots,
		ItemSlotsUnlocked: tmp.ItemSlotsUnlocked,
		Equipment:         tmp.Equipment,
		EquippedTool:      tmp.EquippedTool,
		HP:                tmp.HP,
		MaxHP:             tmp.MaxHP,
		IntroSeen:         false,
		CreatedAt:         now,
		LastPlayedAt:      now,
		KnownRecipes:      knownRecipesSlice(&tmp), // empty for a fresh character
	}
}

// knownRecipesSlice flattens a player's KnownRecipes map to a slice for persistence/sync.
func knownRecipesSlice(p *PlayerState) []string {
	out := make([]string, 0, len(p.KnownRecipes))
	for id := range p.KnownRecipes {
		out = append(out, id)
	}
	return out
}

// applyCharacterSave copies a save's persistent fields onto a live PlayerState (over AddPlayer's
// defaults). Position is NOT set here — the caller decides spawn (intro spawn / home / last).
func applyCharacterSave(p *PlayerState, save *CharacterSave) {
	p.Coins = save.Coins
	p.BugSlots = save.BugSlots
	p.ItemSlots = save.ItemSlots
	p.ItemSlotsUnlocked = save.ItemSlotsUnlocked
	if p.ItemSlotsUnlocked <= 0 {
		p.ItemSlotsUnlocked = baseUnlockedItemSlots
	}
	p.Equipment = save.Equipment
	p.EquippedTool = save.EquippedTool
	p.MaxHP = save.MaxHP
	if p.MaxHP <= 0 {
		p.MaxHP = 10
	}
	p.HP = save.HP
	if p.HP <= 0 || p.HP > p.MaxHP {
		p.HP = p.MaxHP // log back in alive
	}
	if save.Name != "" {
		p.Username = save.Name // the character's name is the in-world display name
	}
	p.CharacterID = save.CharID
	p.CharCreatedAt = save.CreatedAt
	p.Appearance = save.Appearance
	p.IntroSeen = save.IntroSeen
	p.KnownRecipes = make(map[string]bool, len(save.KnownRecipes))
	for _, id := range save.KnownRecipes {
		p.KnownRecipes[id] = true
	}
	p.HomeZone = save.HomeZone
	p.HomeX = save.HomeX
	p.HomeY = save.HomeY
}

// buildCharacterSave snapshots a live PlayerState into a CharacterSave for writing (on leave / sleep).
func buildCharacterSave(p *PlayerState, zoneID string, chunkSize int, now int64) *CharacterSave {
	return &CharacterSave{
		Version:           1,
		CharID:            p.CharacterID,
		Name:              p.Username,
		Appearance:        p.Appearance,
		Coins:             p.Coins,
		BugSlots:          p.BugSlots,
		ItemSlots:         p.ItemSlots,
		ItemSlotsUnlocked: p.ItemSlotsUnlocked,
		Equipment:         p.Equipment,
		EquippedTool:      p.EquippedTool,
		HP:                p.HP,
		MaxHP:             p.MaxHP,
		HomeZone:          p.HomeZone,
		HomeX:             p.HomeX,
		HomeY:             p.HomeY,
		LastZone:          zoneID,
		LastX:             p.WorldX(chunkSize),
		LastY:             p.WorldY(chunkSize),
		IntroSeen:         p.IntroSeen,
		CreatedAt:         p.CharCreatedAt,
		LastPlayedAt:      now,
		KnownRecipes:      knownRecipesSlice(p),
	}
}

// ---- storage helpers (exported for the rpc package + the match hooks) ----

// LoadCharacterSave reads one character (owned by userID). Returns (nil, nil) when absent.
func LoadCharacterSave(ctx context.Context, nk runtime.NakamaModule, userID, charID string) (*CharacterSave, error) {
	objs, err := nk.StorageRead(ctx, []*runtime.StorageRead{{
		Collection: CharacterCollection, Key: charID, UserID: userID,
	}})
	if err != nil {
		return nil, err
	}
	if len(objs) == 0 {
		return nil, nil
	}
	var save CharacterSave
	if err := json.Unmarshal([]byte(objs[0].Value), &save); err != nil {
		return nil, fmt.Errorf("corrupt character %s: %w", charID, err)
	}
	return &save, nil
}

// WriteCharacterSave persists one character (user-owned, server-only write permission).
func WriteCharacterSave(ctx context.Context, nk runtime.NakamaModule, userID string, save *CharacterSave) error {
	data, err := json.Marshal(save)
	if err != nil {
		return err
	}
	_, err = nk.StorageWrite(ctx, []*runtime.StorageWrite{{
		Collection:      CharacterCollection,
		Key:             save.CharID,
		UserID:          userID,
		Value:           string(data),
		PermissionRead:  1, // owner can read (the select screen)
		PermissionWrite: 0, // server-only writes — clients can't forge inventory
	}})
	return err
}

// DeleteCharacterSave removes one character (caller must own it).
func DeleteCharacterSave(ctx context.Context, nk runtime.NakamaModule, userID, charID string) error {
	return nk.StorageDelete(ctx, []*runtime.StorageDelete{{
		Collection: CharacterCollection, Key: charID, UserID: userID,
	}})
}

// ListCharacterSummaries returns the account's characters (lightweight view for the select screen).
func ListCharacterSummaries(ctx context.Context, nk runtime.NakamaModule, userID string) ([]CharacterSummary, error) {
	objs, _, err := nk.StorageList(ctx, "", userID, CharacterCollection, 100, "")
	if err != nil {
		return nil, err
	}
	out := make([]CharacterSummary, 0, len(objs))
	for _, o := range objs {
		var save CharacterSave
		if err := json.Unmarshal([]byte(o.Value), &save); err != nil {
			continue // skip a corrupt record rather than fail the whole list
		}
		out = append(out, CharacterSummary{
			CharID: save.CharID, Name: save.Name, Appearance: save.Appearance,
			LastZone: save.LastZone, LastPlayedAt: save.LastPlayedAt,
		})
	}
	return out, nil
}
