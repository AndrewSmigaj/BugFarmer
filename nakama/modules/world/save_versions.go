package world

import (
	"encoding/json"
	"errors"
	"fmt"
	"strconv"
)

// Save-format versioning, shared by world saves and character saves.
//
// Every stored document carries "version": the format of the build that wrote it. On load:
//   - the same version is read as-is;
//   - an OLDER version is upgraded one step at a time (v1 -> v2 -> …) on the raw JSON, so a step can rename or
//     reshape fields the current Go structs no longer know about; the caller keeps the untouched original as a
//     backup before the upgraded document is ever written back;
//   - a NEWER version (a save from a later build, e.g. after a downgrade) is never read and never overwritten —
//     guessing at an unknown format, or starting empty and autosaving over it, loses the player's world.
//
// This replaced "any other version = treat the save as missing", which silently wiped every zone on the first
// format change (the next autosave wrote an empty zone over the old document).
//
// Adding a format change: bump the version constant, and add the step for the OLD version to its map — a func
// that edits the document in place from version v to v+1. Never edit an existing step; add a new one.

// saveStep turns a version-v document into a version-(v+1) document, in place.
type saveStep func(doc map[string]json.RawMessage) error

var (
	errSaveFromNewerBuild = errors.New("saved by a newer version of the game")
	errSaveNoUpgradeStep  = errors.New("no upgrade step for this save version")
	errSaveUnreadable     = errors.New("save is unreadable")
)

// upgradeSaveJSON returns `raw` upgraded to version `target` through `steps`, plus the version it was stored at.
// Documents already at `target` come back byte-identical.
func upgradeSaveJSON(raw []byte, target int, steps map[int]saveStep) ([]byte, int, error) {
	var head struct {
		Version int `json:"version"`
	}
	if err := json.Unmarshal(raw, &head); err != nil {
		return nil, 0, fmt.Errorf("%w: %v", errSaveUnreadable, err)
	}
	stored := head.Version
	switch {
	case stored > target:
		return nil, stored, fmt.Errorf("%w (save format %d, this build writes %d)", errSaveFromNewerBuild, stored, target)
	case stored < 1:
		return nil, stored, fmt.Errorf("%w: missing or invalid version %d", errSaveUnreadable, stored)
	case stored == target:
		return raw, stored, nil
	}
	var doc map[string]json.RawMessage
	if err := json.Unmarshal(raw, &doc); err != nil {
		return nil, stored, fmt.Errorf("%w: %v", errSaveUnreadable, err)
	}
	for v := stored; v < target; v++ {
		step, ok := steps[v]
		if !ok {
			return nil, stored, fmt.Errorf("%w: format %d -> %d", errSaveNoUpgradeStep, v, v+1)
		}
		if err := step(doc); err != nil {
			return nil, stored, fmt.Errorf("upgrading save format %d -> %d failed: %w", v, v+1, err)
		}
		doc["version"] = json.RawMessage(strconv.Itoa(v + 1))
	}
	out, err := json.Marshal(doc)
	if err != nil {
		return nil, stored, fmt.Errorf("re-encoding the upgraded save failed: %w", err)
	}
	return out, stored, nil
}
