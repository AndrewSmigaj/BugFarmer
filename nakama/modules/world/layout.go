package world

// THE LAYOUT FINGERPRINT (Stage 1.5, docs/plans/village-slice.md).
//
// A world save is a diff against the zone's AUTHORED layout: cell edits, plus registries keyed by cell (trees, nests,
// crops, containers, swarm positions). Loaded over a different layout — the village rebuilt at 512 x 512, say — those
// land on the wrong cells. So every save records the fingerprint of the layout it was made on (WorldSave.Layout), and
// at MatchInit a save whose fingerprint doesn't match the zone's layout now is loaded only if the zone's zone.json says
// what to do with it (ZoneConfig.LayoutMigrations): keep its edits over the new layout, or set it aside and start
// fresh. Without a rule the zone doesn't start — the same as any other save the server can't use: the save is left
// untouched and the log says why. Bench zones (bench_of) are throwaway and start fresh on their own.
//
// The fingerprint covers what a save's positions depend on: the zone's size and every cell's authored ground tile and
// occupant. Not the roof map (lighting only), and not the rest of zone.json (spawn tuning changes often and moves
// nothing a save holds).

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"

	"github.com/heroiclabs/nakama-common/runtime"
)

// layoutFingerprint works out the fingerprint of the current zone's authored layout from its chunk files (read through
// baseChunk, so the save's diff reuses them; a missing chunk file is grass, as everywhere else).
func (s *WorldState) layoutFingerprint(zonePath string) string {
	chunksX, chunksY := s.zoneChunkGrid()
	h := sha256.New()
	fmt.Fprintf(h, "layout 1 %dx%d\n", chunksX*ChunkSize, chunksY*ChunkSize)
	var occ bytes.Buffer
	for cy := 0; cy < chunksY; cy++ {
		for cx := 0; cx < chunksX; cx++ {
			c := s.baseChunk(zonePath, cx, cy)
			for ly := 0; ly < ChunkSize; ly++ {
				for lx := 0; lx < ChunkSize; lx++ {
					ground := ""
					if ly < len(c.Ground) && lx < len(c.Ground[ly]) {
						ground = c.Ground[ly][lx]
					}
					occ.Reset()
					if ly < len(c.Occupants) && lx < len(c.Occupants[ly]) {
						if raw := c.Occupants[ly][lx]; len(raw) > 0 && string(raw) != "null" {
							if json.Compact(&occ, raw) != nil {
								occ.Reset()
								occ.Write(raw)
							}
						}
					}
					h.Write([]byte(ground))
					h.Write([]byte{0})
					h.Write(occ.Bytes())
					h.Write([]byte{0})
				}
			}
		}
	}
	return hex.EncodeToString(h.Sum(nil)[:16])
}

// layoutDecision is what MatchInit does with a save, given the layout it was made on.
type layoutDecision int

const (
	layoutLoad     layoutDecision = iota // load it
	layoutSetAside                       // keep it as a backup and start the zone fresh
	layoutRefuse                         // don't start the zone; the save is left untouched
)

// decideLayout says what to do with a save made on layout `saved` when the zone's layout is now `current`, and why
// (empty when there is nothing to say). A save from before fingerprints (saved == "") was made on the layout the zone
// had when this build first loaded it — layouts change only with a build that already records them — so it loads, and
// its next save records the current layout. An exact rule beats "*".
func decideLayout(saved, current string, z *ZoneConfig) (layoutDecision, string) {
	if saved == "" {
		return layoutLoad, "its save records no layout (made before layouts were recorded) — loaded as made on this one"
	}
	if saved == current {
		return layoutLoad, ""
	}
	var rule *LayoutMigration
	if z != nil {
		for i := range z.LayoutMigrations {
			if m := &z.LayoutMigrations[i]; m.From == saved || (m.From == "*" && rule == nil) {
				rule = m
				if m.From == saved {
					break
				}
			}
		}
	}
	switch {
	case rule != nil && rule.KeepEdits:
		return layoutLoad, fmt.Sprintf("its save was made on layout %s, the zone is now %s — loaded with its edits (layout_migrations)", saved, current)
	case rule != nil:
		return layoutSetAside, fmt.Sprintf("its save was made on layout %s, the zone is now %s — set aside, starting fresh (layout_migrations)", saved, current)
	case z != nil && z.BenchOf != "":
		return layoutSetAside, fmt.Sprintf("its save was made on layout %s, the bench zone is now %s — set aside, starting fresh", saved, current)
	}
	return layoutRefuse, fmt.Sprintf("its save was made on layout %s but the zone's layout is now %s. Add a rule to the zone's "+
		`zone.json — "layout_migrations": [{"from": "%s", "keep_edits": true}] keeps the save's edits over the new layout, `+
		`"keep_edits": false sets the save aside (kept as a backup) and starts the zone fresh`, saved, current, saved)
}

// layoutBackupKey names the copy of a save set aside because it was made on layout `layout`.
func layoutBackupKey(zoneKey, layout string) string {
	return fmt.Sprintf("%s:layout-%s", worldSaveKey(zoneKey), layout)
}

// keepWorldSaveCopy stores `raw` under `key`, unless something is already there: the first copy is the original.
func keepWorldSaveCopy(ctx context.Context, nk runtime.NakamaModule, key, raw string) error {
	objs, err := nk.StorageRead(ctx, []*runtime.StorageRead{{Collection: ZoneStateCollection, Key: key, UserID: ""}})
	if err != nil {
		return err
	}
	if len(objs) > 0 {
		return nil
	}
	_, err = nk.StorageWrite(ctx, []*runtime.StorageWrite{{
		Collection: ZoneStateCollection, Key: key, UserID: "", Value: raw,
		PermissionRead: 0, PermissionWrite: 0, // server-only
	}})
	return err
}
