package main

import (
	"context"
	"database/sql"

	"bugfarmer/rpc"
	"bugfarmer/world"

	"github.com/heroiclabs/nakama-common/runtime"
)

func InitModule(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, initializer runtime.Initializer) error {
	logger.Info("Bug Farmer module loading...")

	// Register world management RPCs
	if err := initializer.RegisterRpc("world_create", rpc.WorldCreate); err != nil {
		return err
	}
	if err := initializer.RegisterRpc("world_join", rpc.WorldJoin); err != nil {
		return err
	}
	if err := initializer.RegisterRpc("world_enter", rpc.WorldEnter); err != nil {
		return err
	}
	if err := initializer.RegisterRpc("world_list", rpc.WorldList); err != nil {
		return err
	}
	// world_leave removed - socket disconnect handles leaving

	// Register character RPCs (per-account roster; inventory writes happen only in the match)
	if err := initializer.RegisterRpc("character_list", rpc.CharacterList); err != nil {
		return err
	}
	if err := initializer.RegisterRpc("character_create", rpc.CharacterCreate); err != nil {
		return err
	}
	if err := initializer.RegisterRpc("character_delete", rpc.CharacterDelete); err != nil {
		return err
	}

	// Register authoritative match handler for world simulation
	if err := initializer.RegisterMatch("world", world.NewMatch); err != nil {
		return err
	}

	logger.Info("Bug Farmer module loaded successfully")
	return nil
}
