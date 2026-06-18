#!/usr/bin/env python3
"""Generate sweep-1: 20 bug-ecology tuning configs across 4 strategies × 5 variants, each a DELTA over
01_no_cull (cull off → read the natural dynamics). Run `python3 tools/bug_lab_configs/_gen_sweep1.py` to
(re)emit the A?_/B?_/C?_/D?_ json files, then `tools/run_sweep.sh` runs them all.

Baseline read (01_no_cull, 14 game-days): butterfly self-regulates ~100 (PASS); fly self-sustains in a
25↔148 boom-bust (center ~60); millipede PASS; wasp/centipede/beetle FLOOR-pinned + re-seed-propped
because flies are too thin/hard to encounter in the predator pens (centipede 7 kills/14d, wasp hunts
leaked butterflies). The 4 strategies attack that from 4 distinct mechanisms:

  A REACH        — find sparse prey: vision / speed / home-range / nest-spread (the owner's pick)
  B LETHALITY    — convert encounters → kills → offspring: feed_per_kill / strike / breed-bar / hunt-freq
  C PREY BASE    — make more prey to find: fruit throughput + fly breeding (also lifts the fly center→100)
  D SURVIVAL     — survive lean times + plant dynamics: satiation decay / lifespan / nectar amplitude

Current values these deltas are relative to (species.json / occupants.json / ecology_tuning defaults):
  centipede: vision 13, base 1.9, decay 0.10; pred home 0, hunt_mult 1.9, strike_r 2.3, strike_cd 40,
             feed 45, hunt_thresh 50
  wasp:      vision 16, base 2.2, decay 0.11; pred home 40, hunt_mult 1.5, strike_r 3.0, strike_cd 100,
             feed 48, hunt_thresh 45, deposit 80
  fly:       repro_cd 30, breed_amt 10        beetle: decay 0.10, lifespan 5040
  trees:     plum 5/600/3000  cherry 6/720/3600  apple 4/840/4200   (max_fruit/grow/drop ticks)
  tuning:    predator_breed_satiation 70, nectar_regen 0.012, max_nectar 100, nest_found_dist 2..6
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))


def emit(name, desc, *, species=None, fruit=None, tuning=None, lab=None):
    cfg = {"name": name, "description": desc, "extends": "01_no_cull"}
    if species:
        cfg["species"] = species
    if fruit:
        cfg["fruit"] = fruit
    if tuning:
        cfg["tuning"] = tuning
    if lab:
        cfg["lab"] = lab
    with open(os.path.join(HERE, f"{name}.json"), "w") as f:
        json.dump(cfg, f, indent=2)
    print("wrote", name)


# ── Strategy A — REACH ────────────────────────────────────────────────────────────────────────────
emit("A1_reach_vision_lo", "REACH: modest vision bump so predators spot prey further (cent 13→18, wasp 16→22).",
     species={"centipede_garden": {"vision_range": 18}, "wasp_common": {"vision_range": 22}})
emit("A2_reach_vision_hi", "REACH: large vision so predators see prey across the whole pen (cent 13→26, wasp 16→32).",
     species={"centipede_garden": {"vision_range": 26}, "wasp_common": {"vision_range": 32}})
emit("A3_reach_speed", "REACH: faster chase + roam (cent base 1.9→2.5 hunt_mult 1.9→2.6; wasp base 2.2→2.8 hunt_mult 1.5→2.2).",
     species={"centipede_garden": {"base_speed": 2.5, "predation": {"hunt_speed_mult": 2.6}},
              "wasp_common": {"base_speed": 2.8, "predation": {"hunt_speed_mult": 2.2}}})
emit("A4_reach_territory", "REACH: spread predators out — wasp home_range 40→70 + daughter nests founded 4..10 cells out (anti-clustering).",
     species={"wasp_common": {"predation": {"home_range": 70.0}}},
     tuning={"nest_found_dist_min": 4, "nest_found_dist_max": 10})
emit("A5_reach_all", "REACH: everything — big vision + fast chase + wide territory + spread nests.",
     species={"centipede_garden": {"vision_range": 26, "base_speed": 2.5, "predation": {"hunt_speed_mult": 2.6}},
              "wasp_common": {"vision_range": 32, "base_speed": 2.8, "predation": {"hunt_speed_mult": 2.2, "home_range": 70.0}}},
     tuning={"nest_found_dist_min": 4, "nest_found_dist_max": 10})

# ── Strategy B — LETHALITY / BREEDING ─────────────────────────────────────────────────────────────
emit("B1_feed_up", "LETHALITY: each kill sates more so fewer kills → breed (cent feed 45→65, wasp 48→65).",
     species={"centipede_garden": {"predation": {"feed_per_kill": 65.0}},
              "wasp_common": {"predation": {"feed_per_kill": 65.0}}})
emit("B2_strike_fast", "LETHALITY: strike more often + bigger reach (cent cd 40→20 r 2.3→3.2; wasp cd 100→55 r 3.0→3.8).",
     species={"centipede_garden": {"predation": {"strike_cooldown_ticks": 20, "strike_radius": 3.2}},
              "wasp_common": {"predation": {"strike_cooldown_ticks": 55, "strike_radius": 3.8}}})
emit("B3_breed_bar_down", "LETHALITY: breed on fewer meals — predator_breed_satiation 70→50; wasp deposits brood sooner (80→55).",
     tuning={"predator_breed_satiation": 50.0},
     species={"wasp_common": {"predation": {"deposit_satiation": 55.0}}})
emit("B4_hunt_always", "LETHALITY: hunt almost always instead of resting (cent hunt_thresh 50→90, wasp 45→85).",
     species={"centipede_garden": {"predation": {"hunt_satiation_threshold": 90.0}},
              "wasp_common": {"predation": {"hunt_satiation_threshold": 85.0}}})
emit("B5_lethality_all", "LETHALITY: feed-up + strike-fast + low breed bar + hunt-always combined.",
     tuning={"predator_breed_satiation": 50.0},
     species={"centipede_garden": {"predation": {"feed_per_kill": 65.0, "strike_cooldown_ticks": 20, "strike_radius": 3.2, "hunt_satiation_threshold": 90.0}},
              "wasp_common": {"predation": {"feed_per_kill": 65.0, "strike_cooldown_ticks": 55, "strike_radius": 3.8, "hunt_satiation_threshold": 85.0, "deposit_satiation": 55.0}}})

# ── Strategy C — PREY BASE (fruit throughput + fly breeding) ───────────────────────────────────────
FRUIT_FAST = {"tree_plum": {"fruit_grow_ticks": 360, "fruit_drop_ticks": 2100},
              "tree_cherry": {"fruit_grow_ticks": 430, "fruit_drop_ticks": 2520},
              "tree_apple": {"fruit_grow_ticks": 500, "fruit_drop_ticks": 2940}}
FRUIT_PLENTY = {"tree_plum": {"max_fruit": 8}, "tree_cherry": {"max_fruit": 9}, "tree_apple": {"max_fruit": 7}}
FRUIT_RICH = {t: {**FRUIT_FAST.get(t, {}), **FRUIT_PLENTY.get(t, {})} for t in FRUIT_FAST}
emit("C1_fruit_fast", "PREY BASE: fruit grows/drops faster (×0.6 grow, ×0.7 drop) → denser rotten-fruit fly food.",
     fruit=FRUIT_FAST)
emit("C2_fruit_plenty", "PREY BASE: more fruit per tree (max_fruit +3) → bigger fly-food batches.",
     fruit=FRUIT_PLENTY)
emit("C3_fly_breed_fast", "PREY BASE: flies breed faster (repro_cd 30→18, breed_amt 10→16) → more prey per unit food.",
     species={"fly_common": {"reproduce_cooldown": 18.0, "breed_amount": 16.0}})
emit("C4_prey_rich", "PREY BASE: fast + plenty fruit together (denser, bigger fly-food supply).",
     fruit=FRUIT_RICH)
emit("C5_prey_max", "PREY BASE: fast+plenty fruit + fast fly breeding — max prey base.",
     fruit=FRUIT_RICH, species={"fly_common": {"reproduce_cooldown": 18.0, "breed_amount": 16.0}})

# ── Strategy D — SURVIVAL + PLANT DYNAMICS ────────────────────────────────────────────────────────
emit("D1_decay_slow", "SURVIVAL: predators/decomposers lose satiation slower → survive longer between meals (cent/wasp/beetle decay →0.05).",
     species={"centipede_garden": {"satiation_decay_rate": 0.05}, "wasp_common": {"satiation_decay_rate": 0.05},
              "beetle_carrion": {"satiation_decay_rate": 0.05}})
emit("D2_lifespan_long", "SURVIVAL: predators live ~50% longer (cent/wasp lifespan 6300→9450; beetle 5040→7560) → more lifetime to feed+breed.",
     species={"centipede_garden": {"lifespan_secs": 9450.0, "lifespan_spread_secs": 2520.0},
              "wasp_common": {"lifespan_secs": 9450.0, "lifespan_spread_secs": 2520.0},
              "beetle_carrion": {"lifespan_secs": 7560.0, "lifespan_spread_secs": 1890.0}})
emit("D3_nectar_amplitude", "PLANT: slower nectar regen (0.012→0.006) → bigger, slower butterfly boom-bust swings.",
     tuning={"nectar_regen_per_tick": 0.006})
emit("D4_nectar_rich", "PLANT: richer nectar (regen 0.012→0.025, max 100→150) → butterflies overshoot/oscillate higher.",
     tuning={"nectar_regen_per_tick": 0.025, "max_nectar": 150.0})
emit("D5_survival_combo", "SURVIVAL+PLANT: slow decay + long lifespan + nectar amplitude together.",
     tuning={"nectar_regen_per_tick": 0.006},
     species={"centipede_garden": {"satiation_decay_rate": 0.05, "lifespan_secs": 9450.0, "lifespan_spread_secs": 2520.0},
              "wasp_common": {"satiation_decay_rate": 0.05, "lifespan_secs": 9450.0, "lifespan_spread_secs": 2520.0},
              "beetle_carrion": {"satiation_decay_rate": 0.05, "lifespan_secs": 7560.0, "lifespan_spread_secs": 1890.0}})

print("\n20 configs written (A1-5 reach, B1-5 lethality, C1-5 prey base, D1-5 survival).")
