package world

// Rolling backups (D73; docs/product/architecture/architecture_persistence.md → "Backups").
//
// A backup is every zone's save and every character at ONE moment, in one JSON file:
//   - the listing runs as a task on the save queue, so it sees exactly what the jobs before it wrote — each zone and
//     the characters in it from the same moment, as a crash at that point would leave them (save_writer.go);
//   - the file is written under a temporary name in the same folder, synced, renamed, then READ BACK and checked
//     against its own content hash. Only a backup that reads back counts, and only then are older ones pruned (the
//     folder is on Windows, where a sync isn't guaranteed to reach the disk);
//   - a backup identical to the newest one isn't written;
//   - kept: the newest 10, the newest of each of the 7 most recent days that have one, and the newest of each of the
//     4 most recent weeks that have one — about 21 files at most. Only files named like ours are ever pruned.
//     Pre-restore copies (restore.go) sit in their own folder and are never pruned.
//
// When: once at start-up — queued before any zone can save, so it keeps the state from before an update — then every
// 30 minutes if anything was saved since. A failure is a warning: the game carries on, and the next backup tries again.
// What: every zone_state document except the pre-upgrade copies (`<zone>:world:v<N>`), so the old-format records of
// zones not yet moved to the WorldSave document are included; every character of every account. Not the accounts,
// the world list or the pre-upgrade copies.

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/heroiclabs/nakama-common/api"
	"github.com/heroiclabs/nakama-common/runtime"
)

// backupFormat is the version of the backup file's layout (not of the saves inside it).
const backupFormat = 1

const (
	defaultBackupInterval = 30 * time.Minute
	backupPage            = 100             // objects per storage listing page
	backupListTimeout     = 2 * time.Minute // how long a backup waits for its turn on the save queue and its listing
)

// backupRetention is how many backups are kept: the newest `recent`, plus the newest of each of the `daily` most
// recent days that have one, plus the newest of each of the `weekly` most recent weeks that have one (UTC, ISO weeks).
type backupRetention struct{ recent, daily, weekly int }

var defaultBackupRetention = backupRetention{recent: 10, daily: 7, weekly: 4}

// backupObject is one stored object, as it was stored.
type backupObject struct {
	UserID string          `json:"user_id,omitempty"` // a character's account; zone saves belong to the server ("")
	Key    string          `json:"key"`
	Read   int32           `json:"read"`
	Write  int32           `json:"write"`
	Value  json.RawMessage `json:"value"`
}

// backupFile is one backup: the zone saves and the characters, and a hash of them.
type backupFile struct {
	Format      int            `json:"format"`
	Kind        string         `json:"kind"` // "rolling" or "pre-restore"
	CreatedAt   time.Time      `json:"created_at"`
	ContentHash string         `json:"content_hash"` // sha256 of ZoneState + Characters (backupContentHash)
	ZoneState   []backupObject `json:"zone_state"`
	Characters  []backupObject `json:"characters"`
}

// nilUserID is how Nakama lists a system-owned object's owner.
const nilUserID = "00000000-0000-0000-0000-000000000000"

// worldSaveBackupKeyRe matches the pre-upgrade copies of zone saves (worldSaveBackupKey) — not part of a backup.
var worldSaveBackupKeyRe = regexp.MustCompile(`:world:v\d+$`)

// listBackupContent lists every zone save (not the pre-upgrade copies) and every character, each sorted by key and
// then owner — Nakama lists by read permission first, so sorting makes equal storage give an equal file.
func listBackupContent(ctx context.Context, nk runtime.NakamaModule) (zones, chars []backupObject, err error) {
	zones, err = listForBackup(ctx, nk, ZoneStateCollection, func(o *api.StorageObject) bool {
		return !worldSaveBackupKeyRe.MatchString(o.Key)
	})
	if err != nil {
		return nil, nil, fmt.Errorf("listing zone saves: %w", err)
	}
	chars, err = listForBackup(ctx, nk, CharacterCollection, nil)
	if err != nil {
		return nil, nil, fmt.Errorf("listing characters: %w", err)
	}
	return zones, chars, nil
}

// listForBackup pages through one collection, every account's objects (and the server's), keeping those keep allows.
func listForBackup(ctx context.Context, nk runtime.NakamaModule, collection string,
	keep func(*api.StorageObject) bool) ([]backupObject, error) {
	out := []backupObject{}
	cursor := ""
	for {
		objs, next, err := nk.StorageList(ctx, "", "", collection, backupPage, cursor)
		if err != nil {
			return nil, err
		}
		for _, o := range objs {
			if keep != nil && !keep(o) {
				continue
			}
			owner := o.UserId
			if owner == nilUserID {
				owner = ""
			}
			out = append(out, backupObject{UserID: owner, Key: o.Key, Read: o.PermissionRead, Write: o.PermissionWrite,
				Value: json.RawMessage(o.Value)})
		}
		if next == "" || next == cursor {
			break
		}
		cursor = next
	}
	sort.Slice(out, func(i, j int) bool {
		if out[i].Key != out[j].Key {
			return out[i].Key < out[j].Key
		}
		return out[i].UserID < out[j].UserID
	})
	return out, nil
}

// encodeJSON is json.Marshal without HTML escaping (a stored value is kept as it was) and without the newline.
func encodeJSON(v interface{}) ([]byte, error) {
	var buf bytes.Buffer
	enc := json.NewEncoder(&buf)
	enc.SetEscapeHTML(false)
	if err := enc.Encode(v); err != nil {
		return nil, err
	}
	return bytes.TrimSuffix(buf.Bytes(), []byte("\n")), nil
}

// backupContentHash is the hash a backup file carries of its contents (and is checked against when read back).
func backupContentHash(zones, chars []backupObject) (string, error) {
	b, err := encodeJSON(struct {
		ZoneState  []backupObject `json:"zone_state"`
		Characters []backupObject `json:"characters"`
	}{zones, chars})
	if err != nil {
		return "", err
	}
	sum := sha256.Sum256(b)
	return hex.EncodeToString(sum[:]), nil
}

func newBackupFile(kind string, at time.Time, zones, chars []backupObject) (*backupFile, error) {
	hash, err := backupContentHash(zones, chars)
	if err != nil {
		return nil, err
	}
	return &backupFile{Format: backupFormat, Kind: kind, CreatedAt: at.UTC(), ContentHash: hash, ZoneState: zones,
		Characters: chars}, nil
}

// readBackupFile reads a backup and checks it: a layout this build knows, and contents that match their hash.
func readBackupFile(path string) (*backupFile, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var f backupFile
	if err := json.Unmarshal(data, &f); err != nil {
		return nil, fmt.Errorf("%s is not a readable backup: %w", filepath.Base(path), err)
	}
	if f.Format < 1 || f.Format > backupFormat {
		return nil, fmt.Errorf("%s has backup format %d; this build reads up to %d", filepath.Base(path), f.Format, backupFormat)
	}
	hash, err := backupContentHash(f.ZoneState, f.Characters)
	if err != nil {
		return nil, err
	}
	if hash != f.ContentHash {
		return nil, fmt.Errorf("%s is damaged: its contents don't match its hash", filepath.Base(path))
	}
	return &f, nil
}

// writeBackupFile writes f as dir/name (never over an existing file): to a temporary file first, synced, then
// renamed; then reads it back. The file counts only if it reads back intact — a damaged one is removed.
func writeBackupFile(dir, name string, f *backupFile, readBack func(string) (*backupFile, error)) (string, error) {
	data, err := encodeJSON(f)
	if err != nil {
		return "", err
	}
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return "", err
	}
	final := filepath.Join(dir, name)
	if _, err := os.Stat(final); err == nil {
		return "", fmt.Errorf("%s already exists", name)
	}
	tmp := filepath.Join(dir, "."+name+".tmp")
	fh, err := os.OpenFile(tmp, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0o644)
	if err != nil {
		return "", err
	}
	_, werr := fh.Write(data)
	serr := fh.Sync()
	cerr := fh.Close()
	if err := errors.Join(werr, serr, cerr); err != nil {
		_ = os.Remove(tmp)
		return "", err
	}
	if err := os.Rename(tmp, final); err != nil {
		_ = os.Remove(tmp)
		return "", err
	}
	if d, err := os.Open(dir); err == nil { // best effort: the rename itself reaches the disk
		_ = d.Sync()
		_ = d.Close()
	}
	got, err := readBack(final)
	if err == nil && got.ContentHash != f.ContentHash {
		err = fmt.Errorf("%s read back with different contents", name)
	}
	if err != nil {
		_ = os.Remove(final)
		return "", fmt.Errorf("the backup did not read back intact (removed): %w", err)
	}
	return final, nil
}

// ---- the rolling backups' folder: names, retention, pruning ----

const backupTimeLayout = "20060102T150405Z"

// rollingBackupRe matches the rolling backups' names: world-<UTC time>.json, or world-<UTC time>-<n>.json.
var rollingBackupRe = regexp.MustCompile(`^world-(\d{8}T\d{6}Z)(?:-(\d+))?\.json$`)

type backupEntry struct {
	name string
	at   time.Time
	seq  int // the -<n> of a second backup in the same second
}

// rollingBackups lists the rolling backups in dir, newest first. Other files are not ours and are left alone.
func rollingBackups(dir string) ([]backupEntry, error) {
	des, err := os.ReadDir(dir)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return nil, nil
		}
		return nil, err
	}
	var out []backupEntry
	for _, de := range des {
		m := rollingBackupRe.FindStringSubmatch(de.Name())
		if de.IsDir() || m == nil {
			continue
		}
		at, err := time.Parse(backupTimeLayout, m[1])
		if err != nil {
			continue
		}
		seq, _ := strconv.Atoi(m[2])
		out = append(out, backupEntry{name: de.Name(), at: at, seq: seq})
	}
	sort.Slice(out, func(i, j int) bool {
		if !out[i].at.Equal(out[j].at) {
			return out[i].at.After(out[j].at)
		}
		return out[i].seq > out[j].seq
	})
	return out, nil
}

// backupsToDrop: of these backups (newest first), the ones the retention doesn't keep.
func backupsToDrop(entries []backupEntry, r backupRetention) []backupEntry {
	keep := make([]bool, len(entries))
	days, weeks := map[string]bool{}, map[string]bool{}
	for i, e := range entries { // newest first: the first seen of a day (or week) is that day's newest
		if i < r.recent {
			keep[i] = true
		}
		day := e.at.UTC().Format("2006-01-02")
		if !days[day] && len(days) < r.daily {
			days[day] = true
			keep[i] = true
		}
		y, w := e.at.UTC().ISOWeek()
		week := fmt.Sprintf("%d-W%02d", y, w)
		if !weeks[week] && len(weeks) < r.weekly {
			weeks[week] = true
			keep[i] = true
		}
	}
	var drop []backupEntry
	for i, e := range entries {
		if !keep[i] {
			drop = append(drop, e)
		}
	}
	return drop
}

// nextBackupName is the name for a rolling backup made at `at` that no existing file has.
func nextBackupName(dir string, at time.Time) string {
	base := "world-" + at.UTC().Format(backupTimeLayout)
	name := base + ".json"
	for n := 2; ; n++ {
		if _, err := os.Stat(filepath.Join(dir, name)); errors.Is(err, os.ErrNotExist) {
			return name
		}
		name = fmt.Sprintf("%s-%d.json", base, n)
	}
}

// removeStaleTemps removes the temporary files of backups that were cut off (the server stopped mid-write).
func removeStaleTemps(dir string) {
	des, err := os.ReadDir(dir)
	if err != nil {
		return
	}
	for _, de := range des {
		if n := de.Name(); !de.IsDir() && strings.HasPrefix(n, ".world-") && strings.HasSuffix(n, ".json.tmp") {
			_ = os.Remove(filepath.Join(dir, n))
		}
	}
}

// ---- the rolling backups ----

// backups takes the rolling backups (StartSaveSystem starts it when runtime.env BF_BACKUP_DIR is set).
type backups struct {
	sys      *saveSystem
	dir      string
	every    time.Duration
	keep     backupRetention
	now      func() time.Time
	readBack func(string) (*backupFile, error)

	lastHash string        // the newest backup's content hash ("" = none known)
	lastSeen int64         // the save queue's change count when the last backup was taken (-1 = no backup yet this run)
	stopped  chan struct{} // closed when the backups stop (ctx ended, or the server is stopping)
}

func newBackups(sys *saveSystem, dir string, every time.Duration) *backups {
	return &backups{sys: sys, dir: dir, every: every, keep: defaultBackupRetention, now: time.Now,
		readBack: readBackupFile, lastSeen: -1, stopped: make(chan struct{})}
}

// backupListing is a backup's listing, queued on the save queue; its result is ready once job.done closes.
type backupListing struct {
	job          *saveJob
	zones, chars []backupObject
	seen         int64 // the queue's change count at the listing
}

// queueListing queues the listing as a task on the save queue: it runs after every save queued before it, and no
// save is written while it runs.
func (b *backups) queueListing() *backupListing {
	l := &backupListing{}
	l.job = b.sys.writer.runTask(func(ctx context.Context) error {
		lctx, cancel := context.WithTimeout(ctx, backupListTimeout)
		defer cancel()
		l.seen = b.sys.writer.changes.Load()
		var err error
		l.zones, l.chars, err = listBackupContent(lctx, b.sys.nk)
		return err
	})
	return l
}

// finish waits for a queued listing and writes it as a backup (unless nothing changed since the newest one), then
// prunes. Returns the file written ("" = none).
func (b *backups) finish(ctx context.Context, l *backupListing, why string) (string, error) {
	wait := time.NewTimer(backupListTimeout)
	defer wait.Stop()
	select {
	case <-l.job.done:
	case <-wait.C:
		return "", fmt.Errorf("the save queue didn't reach the backup's listing within %v (halted: %q)", backupListTimeout, b.sys.writer.Halted())
	case <-ctx.Done():
		return "", ctx.Err()
	}
	if l.job.err != nil {
		return "", l.job.err
	}
	f, err := newBackupFile("rolling", b.now(), l.zones, l.chars)
	if err != nil {
		return "", err
	}
	if f.ContentHash == b.lastHash {
		b.lastSeen = l.seen
		b.sys.logger.Info("Backup (%s): nothing changed since the newest backup — none written", why)
		return "", nil
	}
	path, err := writeBackupFile(b.dir, nextBackupName(b.dir, f.CreatedAt), f, b.readBack)
	if err != nil {
		return "", err
	}
	b.lastHash, b.lastSeen = f.ContentHash, l.seen
	pruned := b.prune()
	b.sys.logger.Info("Backup (%s) written: %s — %d zone record(s), %d character(s); %d older backup(s) pruned",
		why, filepath.Base(path), len(f.ZoneState), len(f.Characters), pruned)
	return path, nil
}

// prune removes the rolling backups the retention doesn't keep. Called only after a backup has read back intact.
func (b *backups) prune() int {
	entries, err := rollingBackups(b.dir)
	if err != nil {
		b.sys.logger.Warn("Backups: couldn't list %s to prune: %v", b.dir, err)
		return 0
	}
	n := 0
	for _, e := range backupsToDrop(entries, b.keep) {
		if err := os.Remove(filepath.Join(b.dir, e.name)); err != nil {
			b.sys.logger.Warn("Backups: couldn't remove %s: %v", e.name, err)
			continue
		}
		n++
	}
	return n
}

// loadNewest remembers the newest backup's content hash, so an unchanged start-up writes no copy of it.
func (b *backups) loadNewest() {
	entries, err := rollingBackups(b.dir)
	if err != nil || len(entries) == 0 {
		return
	}
	f, err := readBackupFile(filepath.Join(b.dir, entries[0].name))
	if err != nil {
		b.sys.logger.Warn("Backups: the newest backup can't be read (%v) — the next one is written in full", err)
		return
	}
	b.lastHash = f.ContentHash
}

// start queues the start-up backup's listing (before any zone can save) and runs the backups from then on.
func (b *backups) start(ctx context.Context) {
	if err := os.MkdirAll(b.dir, 0o755); err != nil {
		b.sys.logger.Warn("Backups: can't use %s: %v", b.dir, err)
	}
	removeStaleTemps(b.dir)
	b.loadNewest()
	first := b.queueListing()
	go b.run(ctx, first)
}

func (b *backups) run(ctx context.Context, first *backupListing) {
	defer close(b.stopped)
	if _, err := b.finish(ctx, first, "start-up"); err != nil {
		b.sys.logger.Warn("Backup (start-up) failed — the game carries on; the next backup tries again: %v", err)
	}
	tick := time.NewTicker(b.every)
	defer tick.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-tick.C:
		}
		if b.sys.stopping.Load() {
			return
		}
		if b.sys.writer.changes.Load() == b.lastSeen {
			continue // nothing saved since the last backup
		}
		if _, err := b.finish(ctx, b.queueListing(), "every "+b.every.String()); err != nil {
			b.sys.logger.Warn("Backup failed — the game carries on; the next backup tries again: %v", err)
		}
	}
}
