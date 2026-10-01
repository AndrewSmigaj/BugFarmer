package world

// memStorage — a faithful in-memory stand-in for Nakama's storage, and for the few other NakamaModule calls the
// save system makes, in unit tests. It copies the behaviour of Nakama 3.35 (server/core_storage.go,
// server/core_multi.go), read from that source on 2026-09-30:
//
//   - an object's version is the hex md5 of its value;
//   - a write with version "" always lands; "*" lands only if the object doesn't exist; a version hash lands only
//     if the stored object still has exactly that version — otherwise runtime.ErrStorageRejectedVersion;
//   - every StorageWrite / StorageDelete / MultiUpdate is ONE transaction: if any part is rejected or fails,
//     nothing in it is applied;
//   - a delete without a version never fails (even if the object is missing); with a version it must match;
//   - StorageList with an empty user id lists EVERY user's objects in the collection (StorageListObjectsAll),
//     including system-owned ones, in pages;
//   - an object can't be written for an account that doesn't exist (the storage table's foreign key);
//   - a value must be a JSON object (runtime_go_nakama.go StorageWrite / MultiUpdate).
//
// Anything not implemented hits the nil embedded interface and panics, so a test can't silently depend on it.
// storage_fake_test's own tests (TestMemStorage*) pin each rule above, so the stand-in can be trusted.

import (
	"bytes"
	"context"
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"sort"
	"strconv"
	"strings"
	"sync"
	"testing"

	"github.com/heroiclabs/nakama-common/api"
	"github.com/heroiclabs/nakama-common/runtime"
)

type memStorage struct {
	runtime.NakamaModule

	mu         sync.Mutex
	objs       map[string]string                     // "collection|user|key" -> value (its version is md5(value))
	writeCalls int                                   // StorageWrite calls — a test can check things were written TOGETHER
	multiCalls int                                   // MultiUpdate calls
	users      map[string]bool                       // accounts that exist; nil = every account exists
	matches    map[string]bool                       // live match ids, for MatchGet
	signal     func(id, data string) (string, error) // MatchSignal
	fail       map[string]error                      // the NEXT call of this kind fails once: read|write|delete|list|multi|users
}

func newMemStorage() *memStorage { return &memStorage{objs: map[string]string{}} }

func memKey(collection, userID, key string) string { return collection + "|" + userID + "|" + key }

// storageVersion is Nakama's object version: the hex md5 of the value (core_storage.go expectedVersion).
func storageVersion(value string) string {
	h := md5.Sum([]byte(value))
	return hex.EncodeToString(h[:])
}

// failOnce makes the next call of this kind fail with err — a database error, say.
func (m *memStorage) failOnce(kind string, err error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	if m.fail == nil {
		m.fail = map[string]error{}
	}
	m.fail[kind] = err
}

func (m *memStorage) takeFail(kind string) error {
	if err := m.fail[kind]; err != nil {
		delete(m.fail, kind)
		return err
	}
	return nil
}

func (m *memStorage) copyObjs() map[string]string {
	out := make(map[string]string, len(m.objs))
	for k, v := range m.objs {
		out[k] = v
	}
	return out
}

var errFakeForeignKey = errors.New(`insert or update on table "storage" violates foreign key constraint "storage_user_id_fkey"`)

func (m *memStorage) applyWrites(objs map[string]string, writes []*runtime.StorageWrite) error {
	for _, w := range writes {
		if v := []byte(w.Value); !json.Valid(v) || bytes.TrimSpace(v)[0] != '{' {
			return errors.New("value must be a JSON-encoded object")
		}
		if m.users != nil && w.UserID != "" && !m.users[w.UserID] {
			return fmt.Errorf("%w (user %s)", errFakeForeignKey, w.UserID)
		}
		k := memKey(w.Collection, w.UserID, w.Key)
		cur, exists := objs[k]
		switch w.Version {
		case "":
		case "*":
			if exists {
				return runtime.ErrStorageRejectedVersion
			}
		default:
			if !exists || storageVersion(cur) != w.Version {
				return runtime.ErrStorageRejectedVersion
			}
		}
		objs[k] = w.Value
	}
	return nil
}

func applyDeletes(objs map[string]string, deletes []*runtime.StorageDelete) error {
	for _, d := range deletes {
		k := memKey(d.Collection, d.UserID, d.Key)
		cur, exists := objs[k]
		if d.Version != "" && (!exists || storageVersion(cur) != d.Version) {
			return errors.New("Storage delete rejected - not found, version check failed, or permission denied.")
		}
		delete(objs, k)
	}
	return nil
}

func (m *memStorage) StorageRead(_ context.Context, reads []*runtime.StorageRead) ([]*api.StorageObject, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	if err := m.takeFail("read"); err != nil {
		return nil, err
	}
	var out []*api.StorageObject
	for _, r := range reads {
		if v, ok := m.objs[memKey(r.Collection, r.UserID, r.Key)]; ok {
			out = append(out, &api.StorageObject{Collection: r.Collection, Key: r.Key, UserId: r.UserID, Value: v, Version: storageVersion(v)})
		}
	}
	return out, nil
}

func (m *memStorage) StorageWrite(_ context.Context, writes []*runtime.StorageWrite) ([]*api.StorageObjectAck, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.writeCalls++
	if err := m.takeFail("write"); err != nil {
		return nil, err
	}
	next := m.copyObjs()
	if err := m.applyWrites(next, writes); err != nil {
		return nil, err // one transaction: nothing applied
	}
	m.objs = next
	acks := make([]*api.StorageObjectAck, 0, len(writes))
	for _, w := range writes {
		acks = append(acks, &api.StorageObjectAck{Collection: w.Collection, Key: w.Key, UserId: w.UserID, Version: storageVersion(w.Value)})
	}
	return acks, nil
}

func (m *memStorage) StorageDelete(_ context.Context, deletes []*runtime.StorageDelete) error {
	m.mu.Lock()
	defer m.mu.Unlock()
	if err := m.takeFail("delete"); err != nil {
		return err
	}
	next := m.copyObjs()
	if err := applyDeletes(next, deletes); err != nil {
		return err
	}
	m.objs = next
	return nil
}

// StorageList pages through one collection: one user's objects, or — with an empty userID — every user's
// (system-owned included), ordered by key then user. The cursor is the index of the next object.
func (m *memStorage) StorageList(_ context.Context, _, userID, collection string, limit int, cursor string) ([]*api.StorageObject, string, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	if err := m.takeFail("list"); err != nil {
		return nil, "", err
	}
	if limit <= 0 {
		limit = 100
	}
	var all []*api.StorageObject
	for k, v := range m.objs {
		parts := strings.SplitN(k, "|", 3)
		if parts[0] != collection || (userID != "" && parts[1] != userID) {
			continue
		}
		all = append(all, &api.StorageObject{Collection: collection, UserId: parts[1], Key: parts[2], Value: v, Version: storageVersion(v)})
	}
	sort.Slice(all, func(i, j int) bool {
		if all[i].Key != all[j].Key {
			return all[i].Key < all[j].Key
		}
		return all[i].UserId < all[j].UserId
	})
	start := 0
	if cursor != "" {
		n, err := strconv.Atoi(cursor)
		if err != nil || n < 0 || n > len(all) {
			return nil, "", fmt.Errorf("bad cursor %q", cursor)
		}
		start = n
	}
	end := start + limit
	next := strconv.Itoa(end)
	if end >= len(all) {
		end, next = len(all), ""
	}
	return all[start:end], next, nil
}

func (m *memStorage) MultiUpdate(_ context.Context, accountUpdates []*runtime.AccountUpdate, storageWrites []*runtime.StorageWrite, storageDeletes []*runtime.StorageDelete, walletUpdates []*runtime.WalletUpdate, _ bool) ([]*api.StorageObjectAck, []*runtime.WalletUpdateResult, error) {
	if len(accountUpdates) > 0 || len(walletUpdates) > 0 {
		panic("memStorage.MultiUpdate: account and wallet updates are not modelled")
	}
	m.mu.Lock()
	defer m.mu.Unlock()
	m.multiCalls++
	if err := m.takeFail("multi"); err != nil {
		return nil, nil, err
	}
	next := m.copyObjs()
	if err := m.applyWrites(next, storageWrites); err != nil { // core_multi.go: writes, then deletes, one transaction
		return nil, nil, err
	}
	if err := applyDeletes(next, storageDeletes); err != nil {
		return nil, nil, err
	}
	m.objs = next
	acks := make([]*api.StorageObjectAck, 0, len(storageWrites))
	for _, w := range storageWrites {
		acks = append(acks, &api.StorageObjectAck{Collection: w.Collection, Key: w.Key, UserId: w.UserID, Version: storageVersion(w.Value)})
	}
	return acks, nil, nil
}

func (m *memStorage) UsersGetId(_ context.Context, userIDs []string, _ []string) ([]*api.User, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	if err := m.takeFail("users"); err != nil {
		return nil, err
	}
	var out []*api.User
	for _, id := range userIDs {
		if m.users == nil || m.users[id] {
			out = append(out, &api.User{Id: id})
		}
	}
	return out, nil
}

func (m *memStorage) MatchGet(_ context.Context, id string) (*api.Match, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	if m.matches[id] {
		return &api.Match{MatchId: id}, nil
	}
	return nil, nil // Nakama: a match that isn't running is (nil, nil), not an error
}

func (m *memStorage) MatchSignal(_ context.Context, id string, data string) (string, error) {
	m.mu.Lock()
	hook := m.signal
	m.mu.Unlock()
	if hook == nil {
		panic("memStorage.MatchSignal: no signal hook set")
	}
	return hook(id, data)
}

// ---- the stand-in's own tests: each pins one Nakama behaviour listed at the top ----

func TestMemStorageVersionsLikeNakama(t *testing.T) {
	ctx := context.Background()
	nk := newMemStorage()
	w := func(version, value string) error {
		_, err := nk.StorageWrite(ctx, []*runtime.StorageWrite{{Collection: "c", Key: "k", Value: obj(value), Version: version}})
		return err
	}
	if err := w("*", "a"); err != nil {
		t.Fatalf(`"*" must create a missing object: %v`, err)
	}
	if err := w("*", "b"); !errors.Is(err, runtime.ErrStorageRejectedVersion) {
		t.Errorf(`"*" over an existing object must be rejected: %v`, err)
	}
	objs, _ := nk.StorageRead(ctx, []*runtime.StorageRead{{Collection: "c", Key: "k"}})
	if len(objs) != 1 || objs[0].Version != storageVersion(obj("a")) {
		t.Fatalf("a stored object's version must be md5 of its value: %+v", objs)
	}
	if err := w(storageVersion(obj("a")), "b"); err != nil {
		t.Errorf("a write with the current version must land: %v", err)
	}
	if err := w(storageVersion(obj("a")), "c"); !errors.Is(err, runtime.ErrStorageRejectedVersion) {
		t.Errorf("a write with a stale version must be rejected: %v", err)
	}
	if _, err := nk.StorageWrite(ctx, []*runtime.StorageWrite{{Collection: "c", Key: "missing", Value: obj("x"), Version: storageVersion(obj("x"))}}); !errors.Is(err, runtime.ErrStorageRejectedVersion) {
		t.Errorf("a versioned write to a missing object must be rejected: %v", err)
	}
	if err := w("", "d"); err != nil {
		t.Errorf(`version "" must always land: %v`, err)
	}
}

func TestMemStorageBatchesAreAllOrNothing(t *testing.T) {
	ctx := context.Background()
	nk := newMemStorage()
	nk.objs[memKey("c", "", "old")] = "v1"
	_, err := nk.StorageWrite(ctx, []*runtime.StorageWrite{
		{Collection: "c", Key: "new", Value: obj("x")},
		{Collection: "c", Key: "old", Value: obj("y"), Version: "stale"},
	})
	if !errors.Is(err, runtime.ErrStorageRejectedVersion) {
		t.Fatalf("expected the stale write to reject the batch: %v", err)
	}
	if _, wrote := nk.objs[memKey("c", "", "new")]; wrote || nk.objs[memKey("c", "", "old")] != "v1" {
		t.Errorf("a rejected batch must apply nothing: %v", nk.objs)
	}

	_, _, err = nk.MultiUpdate(ctx, nil,
		[]*runtime.StorageWrite{{Collection: "c", Key: "new", Value: obj("x")}},
		[]*runtime.StorageDelete{{Collection: "c", Key: "old", Version: "stale"}}, nil, false)
	if err == nil {
		t.Fatal("a MultiUpdate whose delete is rejected must fail")
	}
	if _, wrote := nk.objs[memKey("c", "", "new")]; wrote {
		t.Errorf("a failed MultiUpdate must apply none of its writes")
	}
	if err := nk.StorageDelete(ctx, []*runtime.StorageDelete{{Collection: "c", Key: "nothing-here"}}); err != nil {
		t.Errorf("a delete without a version never fails: %v", err)
	}
}

func TestMemStorageListsEveryUserInPages(t *testing.T) {
	ctx := context.Background()
	nk := newMemStorage()
	nk.objs[memKey("character", "u1", "c1")] = "1"
	nk.objs[memKey("character", "u2", "c2")] = "2"
	nk.objs[memKey("character", "u2", "c3")] = "3"
	nk.objs[memKey("zone_state", "", "z:world")] = "w"
	var got []string
	cursor := ""
	for pages := 0; ; pages++ {
		objs, next, err := nk.StorageList(ctx, "", "", "character", 2, cursor)
		if err != nil || pages > 3 {
			t.Fatalf("listing failed or never ended: %v", err)
		}
		for _, o := range objs {
			got = append(got, o.UserId+"/"+o.Key)
		}
		if next == "" {
			break
		}
		cursor = next
	}
	if strings.Join(got, ",") != "u1/c1,u2/c2,u2/c3" {
		t.Errorf("an empty user id must list every user's objects, all pages: %v", got)
	}
	if objs, _, _ := nk.StorageList(ctx, "", "", "zone_state", 10, ""); len(objs) != 1 || objs[0].UserId != "" {
		t.Errorf("system-owned objects are listed too: %+v", objs)
	}
	if objs, _, _ := nk.StorageList(ctx, "", "u2", "character", 10, ""); len(objs) != 2 {
		t.Errorf("a user id lists only that user's objects: %+v", objs)
	}
}

func TestMemStorageRefusesMissingAccountsAndInjectsFailures(t *testing.T) {
	ctx := context.Background()
	nk := newMemStorage()
	nk.users = map[string]bool{"u1": true}
	_, err := nk.StorageWrite(ctx, []*runtime.StorageWrite{
		{Collection: "c", Key: "ok", UserID: "u1", Value: obj("x")},
		{Collection: "c", Key: "gone", UserID: "deleted", Value: obj("y")},
	})
	if !errors.Is(err, errFakeForeignKey) || len(nk.objs) != 0 {
		t.Errorf("a write for a deleted account must fail the whole batch: %v, %v", err, nk.objs)
	}
	if users, _ := nk.UsersGetId(ctx, []string{"u1", "deleted"}, nil); len(users) != 1 || users[0].Id != "u1" {
		t.Errorf("UsersGetId must return only existing accounts: %+v", users)
	}

	boom := errors.New("database unavailable")
	nk.failOnce("write", boom)
	if _, err := nk.StorageWrite(ctx, []*runtime.StorageWrite{{Collection: "c", Key: "k", Value: obj("v")}}); !errors.Is(err, boom) {
		t.Errorf("an injected failure must be returned: %v", err)
	}
	if _, err := nk.StorageWrite(ctx, []*runtime.StorageWrite{{Collection: "c", Key: "k", Value: obj("v")}}); err != nil {
		t.Errorf("an injected failure happens once: %v", err)
	}

	if m, err := nk.MatchGet(ctx, "gone"); m != nil || err != nil {
		t.Errorf("a match that isn't running is (nil, nil): %v, %v", m, err)
	}
	nk.matches = map[string]bool{"live": true}
	if m, _ := nk.MatchGet(ctx, "live"); m == nil || m.MatchId != "live" {
		t.Errorf("a running match must be found: %v", m)
	}
}

// obj makes a small JSON object value — Nakama stores only JSON objects.
func obj(s string) string { return `{"v":"` + s + `"}` }

func TestMemStorageRefusesValuesThatAreNotObjects(t *testing.T) {
	nk := newMemStorage()
	for _, bad := range []string{"x", "[]", `"text"`, "{"} {
		if _, err := nk.StorageWrite(context.Background(), []*runtime.StorageWrite{{Collection: "c", Key: "k", Value: bad}}); err == nil {
			t.Errorf("Nakama refuses a value that isn't a JSON object: %q was written", bad)
		}
	}
	if _, err := nk.StorageWrite(context.Background(), []*runtime.StorageWrite{{Collection: "c", Key: "k", Value: ` {"a":[1]}`}}); err != nil {
		t.Errorf("a JSON object must be written: %v", err)
	}
}
