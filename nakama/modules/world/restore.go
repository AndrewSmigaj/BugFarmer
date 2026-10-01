package world

// Restoring a backup (D73; docs/product/architecture/architecture_persistence.md → "Restoring a backup").
//
// To restore, put ONE backup file in <BF_BACKUP_DIR>/restore/ and restart the server (tools/saves/restore_backup.py
// does both). At the next start — in InitModule, before the save queue or anything else runs, and Nakama serves no
// request until InitModule returns:
//  1. the file is checked: a backup this build can read, intact (its hash), and every zone save and character in a
//     format this build can load (an older one is upgraded as usual when its zone loads);
//  2. the current state is backed up to <dir>/pre-restore/ and read back — if that fails, nothing is restored;
//  3. ONE transaction (MultiUpdate) puts back every zone record and character in the file, removes every zone record
//     and character that isn't in it — so anything made after the backup is gone — and records the restore.
//     Characters of deleted accounts are left out. The pre-upgrade copies, character_backup, the accounts and the
//     world list are never touched;
//  4. the file moves to restore/done/ — or, refused or failed, to restore/failed/ with the reason in the log, and
//     storage is exactly as it was.
//
// The record (collection "restores", keyed by the file's hash and when it was put in place) makes a file that
// couldn't be moved away harmless: the next start sees it was applied and doesn't apply it again. Putting the same
// backup in place again later is a new request, and is applied.

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/heroiclabs/nakama-common/runtime"
)

// restoreCollection records each restore applied (system-owned; never part of a backup).
const restoreCollection = "restores"

// RestoreIfRequested applies the backup waiting in <BF_BACKUP_DIR>/restore/, if there is one. InitModule calls it
// before StartSaveSystem. It never stops the server from starting: a refused or failed restore leaves storage as it
// was, moves the file to restore/failed/ and logs why.
func RestoreIfRequested(ctx context.Context, logger runtime.Logger, nk runtime.NakamaModule, env map[string]string) {
	dir := env["BF_BACKUP_DIR"]
	if dir == "" {
		return
	}
	r := &restorer{nk: nk, logger: logger, dir: dir, now: time.Now}
	_, _ = r.run(ctx)
}

type restorer struct {
	nk     runtime.NakamaModule
	logger runtime.Logger
	dir    string
	now    func() time.Time
}

// restoreResult says what a restore did (for the log, the tool and the tests).
type restoreResult struct {
	file                        string
	zones, chars                int // put back
	removedZones, removedChars  int // made after the backup, removed
	leftOut                     int // characters of deleted accounts
	preRestore                  string
	alreadyApplied, nothingToDo bool
}

func (r *restorer) inbox() string { return filepath.Join(r.dir, "restore") }

// run applies the waiting restore, if any. The error is why a restore was refused or failed (already logged).
func (r *restorer) run(ctx context.Context) (*restoreResult, error) {
	if err := os.MkdirAll(r.inbox(), 0o755); err != nil { // so the folder is there for someone to use
		r.logger.Warn("Restore: can't use %s: %v", r.inbox(), err)
	}
	files, err := r.waiting()
	if err != nil {
		r.logger.Error("Restore: can't read %s: %v", r.inbox(), err)
		return nil, err
	}
	switch len(files) {
	case 0:
		return &restoreResult{nothingToDo: true}, nil
	case 1:
	default:
		err := fmt.Errorf("%d files are waiting in restore/ — put exactly one there", len(files))
		for _, f := range files {
			r.moveTo(f, "failed")
		}
		r.logger.Error("RESTORE REFUSED — nothing was changed: %v (all moved to restore/failed/)", err)
		return nil, err
	}
	path := files[0]
	res, err := r.apply(ctx, path)
	if err != nil {
		r.moveTo(path, "failed")
		r.logger.Error("RESTORE OF %s REFUSED — nothing was changed: %v (the file is in restore/failed/)", filepath.Base(path), err)
		return nil, err
	}
	r.moveTo(path, "done")
	if res.alreadyApplied {
		r.logger.Warn("Restore: %s was already applied (it couldn't be moved away last time) — not applied again", res.file)
		return res, nil
	}
	r.logger.Info("RESTORED %s: %d zone record(s) and %d character(s) put back; %d zone record(s) and %d character(s) "+
		"made after it removed; %d character(s) of deleted accounts left out. The state before is in pre-restore/%s",
		res.file, res.zones, res.chars, res.removedZones, res.removedChars, res.leftOut, res.preRestore)
	return res, nil
}

// waiting lists the files in restore/ (not its folders, not hidden files).
func (r *restorer) waiting() ([]string, error) {
	des, err := os.ReadDir(r.inbox())
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return nil, nil
		}
		return nil, err
	}
	var out []string
	for _, de := range des {
		if de.Type().IsRegular() && !strings.HasPrefix(de.Name(), ".") {
			out = append(out, filepath.Join(r.inbox(), de.Name()))
		}
	}
	return out, nil
}

// moveTo moves a restore file into restore/<sub>/, never over another file.
func (r *restorer) moveTo(path, sub string) {
	dest := filepath.Join(r.inbox(), sub)
	if err := os.MkdirAll(dest, 0o755); err != nil {
		r.logger.Warn("Restore: couldn't make %s: %v", dest, err)
		return
	}
	name := filepath.Base(path)
	target := filepath.Join(dest, name)
	for n := 2; ; n++ {
		if _, err := os.Stat(target); errors.Is(err, os.ErrNotExist) {
			break
		}
		target = filepath.Join(dest, fmt.Sprintf("%s-%d%s", strings.TrimSuffix(name, filepath.Ext(name)), n, filepath.Ext(name)))
	}
	if err := os.Rename(path, target); err != nil {
		r.logger.Warn("Restore: couldn't move %s to restore/%s/: %v", name, sub, err)
	}
}

// apply checks the backup and puts it back in one transaction, after backing up the current state.
func (r *restorer) apply(ctx context.Context, path string) (*restoreResult, error) {
	res := &restoreResult{file: filepath.Base(path)}
	info, err := os.Stat(path)
	if err != nil {
		return nil, err
	}
	f, err := readBackupFile(path)
	if err != nil {
		return nil, err
	}
	// This placement of this backup: applied already? (It is, if the file couldn't be moved away after applying.)
	recordKey := fmt.Sprintf("%s-%d", f.ContentHash, info.ModTime().UnixNano())
	recs, err := r.nk.StorageRead(ctx, []*runtime.StorageRead{{Collection: restoreCollection, Key: recordKey, UserID: ""}})
	if err != nil {
		return nil, fmt.Errorf("checking whether it was already applied: %w", err)
	}
	if len(recs) > 0 {
		res.alreadyApplied = true
		return res, nil
	}
	if err := checkRestorable(f); err != nil {
		return nil, err
	}

	// The current state, kept before anything changes — and the list of what is there now.
	zonesNow, charsNow, err := listBackupContent(ctx, r.nk)
	if err != nil {
		return nil, fmt.Errorf("listing the current state: %w", err)
	}
	pre, err := newBackupFile("pre-restore", r.now(), zonesNow, charsNow)
	if err != nil {
		return nil, err
	}
	preName := "pre-restore-" + pre.CreatedAt.Format(backupTimeLayout) + ".json"
	preDir := filepath.Join(r.dir, "pre-restore")
	if _, err := os.Stat(filepath.Join(preDir, preName)); err == nil {
		preName = fmt.Sprintf("pre-restore-%s-%d.json", pre.CreatedAt.Format(backupTimeLayout), pre.CreatedAt.UnixNano())
	}
	if _, err := writeBackupFile(preDir, preName, pre, readBackupFile); err != nil {
		return nil, fmt.Errorf("the backup of the current state (taken first) failed, so nothing was restored: %w", err)
	}
	res.preRestore = preName

	chars, leftOut, err := r.withoutDeletedAccounts(ctx, f.Characters)
	if err != nil {
		return nil, err
	}
	res.leftOut = leftOut

	writes := make([]*runtime.StorageWrite, 0, len(f.ZoneState)+len(chars)+1)
	inBackup := map[string]bool{}
	for _, o := range f.ZoneState {
		writes = append(writes, &runtime.StorageWrite{Collection: ZoneStateCollection, Key: o.Key, UserID: "",
			Value: string(o.Value), PermissionRead: int(o.Read), PermissionWrite: int(o.Write)})
		inBackup[memberKey(ZoneStateCollection, "", o.Key)] = true
	}
	for _, o := range chars {
		writes = append(writes, &runtime.StorageWrite{Collection: CharacterCollection, Key: o.Key, UserID: o.UserID,
			Value: string(o.Value), PermissionRead: int(o.Read), PermissionWrite: int(o.Write)})
		inBackup[memberKey(CharacterCollection, o.UserID, o.Key)] = true
	}
	res.zones, res.chars = len(f.ZoneState), len(chars)

	var deletes []*runtime.StorageDelete
	for _, o := range zonesNow {
		if !inBackup[memberKey(ZoneStateCollection, "", o.Key)] {
			deletes = append(deletes, &runtime.StorageDelete{Collection: ZoneStateCollection, Key: o.Key, UserID: ""})
			res.removedZones++
		}
	}
	for _, o := range charsNow {
		if !inBackup[memberKey(CharacterCollection, o.UserID, o.Key)] {
			deletes = append(deletes, &runtime.StorageDelete{Collection: CharacterCollection, Key: o.Key, UserID: o.UserID})
			res.removedChars++
		}
	}

	record, _ := json.Marshal(map[string]interface{}{
		"file": res.file, "backup_created_at": f.CreatedAt, "applied_at": r.now().UTC(), "pre_restore": preName,
		"zone_records": res.zones, "characters": res.chars, "removed_zone_records": res.removedZones,
		"removed_characters": res.removedChars, "left_out_characters": leftOut,
	})
	writes = append(writes, &runtime.StorageWrite{Collection: restoreCollection, Key: recordKey, UserID: "",
		Value: string(record), PermissionRead: 0, PermissionWrite: 0})

	if _, _, err := r.nk.MultiUpdate(ctx, nil, writes, deletes, nil, false); err != nil {
		return nil, fmt.Errorf("writing it (one transaction, so nothing was applied): %w", err)
	}
	return res, nil
}

func memberKey(collection, userID, key string) string { return collection + "|" + userID + "|" + key }

// checkRestorable: every zone save and character in the backup must be a format this build can load. Older formats
// are fine — they are upgraded when loaded, keeping a pre-upgrade copy as usual.
func checkRestorable(f *backupFile) error {
	for _, o := range f.ZoneState {
		if strings.HasSuffix(o.Key, ":world") {
			if _, _, err := upgradeSaveJSON(o.Value, worldSaveVersion, worldSaveSteps); err != nil {
				return fmt.Errorf("zone save %s can't be loaded by this build: %w", o.Key, err)
			}
		}
	}
	for _, o := range f.Characters {
		if _, _, err := upgradeSaveJSON(o.Value, characterSaveVersion, characterSaveSteps); err != nil {
			return fmt.Errorf("character %s/%s can't be loaded by this build: %w", o.UserID, o.Key, err)
		}
	}
	return nil
}

// withoutDeletedAccounts leaves out the characters whose account no longer exists (storage refuses them).
func (r *restorer) withoutDeletedAccounts(ctx context.Context, chars []backupObject) ([]backupObject, int, error) {
	if len(chars) == 0 {
		return chars, 0, nil
	}
	var ids []string
	seen := map[string]bool{}
	for _, c := range chars {
		if !seen[c.UserID] {
			seen[c.UserID] = true
			ids = append(ids, c.UserID)
		}
	}
	exists := map[string]bool{}
	for start := 0; start < len(ids); start += backupPage {
		end := start + backupPage
		if end > len(ids) {
			end = len(ids)
		}
		users, err := r.nk.UsersGetId(ctx, ids[start:end], nil)
		if err != nil {
			return nil, 0, fmt.Errorf("checking the characters' accounts: %w", err)
		}
		for _, u := range users {
			exists[u.Id] = true
		}
	}
	kept := make([]backupObject, 0, len(chars))
	for _, c := range chars {
		if exists[c.UserID] {
			kept = append(kept, c)
		}
	}
	return kept, len(chars) - len(kept), nil
}
