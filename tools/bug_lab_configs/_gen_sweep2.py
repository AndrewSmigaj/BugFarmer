#!/usr/bin/env python3
"""Generate sweep-2: 10 configs designed from sweep-1's findings. Run this then `tools/run_sweep.sh 250
E1_flycap400 E2_seal ...` (or the bash glob picks up E*/F*).

SWEEP-1 VERDICT (20 configs, 4 strategies): fly hits target with C3 (faster fly breeding → 99.6, PASS);
butterfly robustly ~90 (PASS); millipede stable ~18. But the predators (wasp, centipede) + beetle stayed
FLOOR-pinned and re-seed-propped in ALL 17 clean runs — NO predator parameter (vision, speed, strike,
feed, breed-bar, lifespan, decay) nor any prey-base/food change moved them. Proof it's structural, not
behavioral: even in C3 (fly=99.6 GLOBAL) the predation log shows centipede→fly = 0 kills and wasp→fly = 8
(the wasp ate 130 leaked BUTTERFLIES in the open arena instead). The pen entrance-gaps let flies + wasps
leak into the foodless arena, so predator pens hold no sustained prey.

SWEEP-2 THESIS: fix the STRUCTURE. seal_pens (closed-ecosystem pens, no leak) + fly-cap headroom so each
predator pen sustains its own fly prey, on top of C3's fast fly breeding. E* isolate the structural lever;
F* combine it with the best predator-behavior directions to push wasp/centipede toward 30.

Locked-in winner reused below: C3 = fly_common repro_cd 30→18, breed_amt 10→16.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

# Reusable delta fragments ----------------------------------------------------------------------------
C3_FLY = {"fly_common": {"reproduce_cooldown": 18.0, "breed_amount": 16.0}}      # the fly→100 winner
CENTI_BUTTERFLY = {"centipede_garden": {"predation": {"prey": ["fly_common", "butterfly_meadow"]}}}
REACH = {"centipede_garden": {"vision_range": 26, "base_speed": 2.5, "predation": {"hunt_speed_mult": 2.6}},
         "wasp_common": {"vision_range": 32, "base_speed": 2.8, "predation": {"hunt_speed_mult": 2.2, "home_range": 70.0}}}
LETHAL = {"centipede_garden": {"predation": {"feed_per_kill": 65.0, "strike_cooldown_ticks": 20, "strike_radius": 3.2}},
          "wasp_common": {"predation": {"feed_per_kill": 65.0, "strike_cooldown_ticks": 55, "strike_radius": 3.8}}}
BEETLE_SURV = {"beetle_carrion": {"satiation_decay_rate": 0.05}}


def merge(*ds):
    """Shallow-by-species deep merge of the species fragments above (predation dicts merge too)."""
    out = {}
    for d in ds:
        for sid, fields in d.items():
            if sid not in out:
                out[sid] = {}
            for k, v in fields.items():
                if k == "predation" and isinstance(out[sid].get("predation"), dict):
                    out[sid]["predation"] = {**out[sid]["predation"], **v}
                else:
                    out[sid][k] = v
    return out


def emit(name, desc, *, species=None, tuning=None, lab=None, fruit=None):
    cfg = {"name": name, "description": desc, "extends": "01_no_cull"}
    if species:
        cfg["species"] = species
    if tuning:
        cfg["tuning"] = tuning
    if lab:
        cfg["lab"] = lab
    if fruit:
        cfg["fruit"] = fruit
    with open(os.path.join(HERE, f"{name}.json"), "w") as f:
        json.dump(cfg, f, indent=2)
    print("wrote", name)


CAP400 = {"max_pop": {"fly_common": 400}}
SEAL = {"seal_pens": True}

# ── E — isolate the STRUCTURAL lever ──────────────────────────────────────────────────────────────
emit("E1_flycap400", "STRUCT: fly cap 150→400 headroom + C3 fast fly breeding, pens still OPEN. Does global headroom alone reach the predator pens? (expect NO — leakage).",
     species=C3_FLY, lab=CAP400)
emit("E2_seal", "STRUCT: SEAL pens (closed ecosystems, no leak) + cap 400 + C3. THE key test — contained predator+prey should let wasp/centipede sustain on their own flies.",
     species=C3_FLY, lab={**SEAL, **CAP400})
emit("E3_seal_default_fly", "STRUCT: seal + cap 400 but DEFAULT fly breeding (no C3) — isolate sealing's effect from the fly-breeding boost.",
     lab={**SEAL, **CAP400})
emit("E4_centi_butterfly", "STRUCT: centipede also preys on butterflies (eat the abundant leaked butterflies) + C3, pens OPEN. Diet fix without sealing.",
     species=merge(C3_FLY, CENTI_BUTTERFLY), lab=CAP400)
emit("E5_seal_centi_butterfly", "STRUCT: seal + cap 400 + C3 + centipede eats butterflies too (a second prey inside its sealed pen has none, so this tests diet vs containment).",
     species=merge(C3_FLY, CENTI_BUTTERFLY), lab={**SEAL, **CAP400})

# ── F — combine the structural fix with the best predator-behavior directions ─────────────────────
emit("F1_seal_reach", "COMBINE: sealed pens + cap 400 + C3 + REACH (vision/speed up) — contained prey AND predators that find it fast.",
     species=merge(C3_FLY, REACH), lab={**SEAL, **CAP400})
emit("F2_seal_lethal", "COMBINE: sealed + cap 400 + C3 + LETHALITY (feed_per_kill + strike) — each encounter converts to a kill+meal.",
     species=merge(C3_FLY, LETHAL), lab={**SEAL, **CAP400})
emit("F3_seal_breedbar", "COMBINE: sealed + cap 400 + C3 + low breed bar (predator_breed_satiation 70→50, wasp deposit 80→55) — breed on fewer contained meals.",
     species=merge(C3_FLY, {"wasp_common": {"predation": {"deposit_satiation": 55.0}}}),
     tuning={"predator_breed_satiation": 50.0}, lab={**SEAL, **CAP400})
emit("F4_seal_full", "COMBINE: sealed + cap 400 + C3 + reach + lethality + low breed bar + beetle survival + beetle cap 20→40 — the full predator/decomposer push.",
     species=merge(C3_FLY, REACH, LETHAL, BEETLE_SURV, {"wasp_common": {"predation": {"deposit_satiation": 55.0}}}),
     tuning={"predator_breed_satiation": 50.0}, lab={**SEAL, "max_pop": {"fly_common": 400, "beetle_carrion": 40}})
emit("F5_seal_full_dense", "COMBINE: F4 + even more prey — fly cap 600 + fruit rich (faster+plenty) — max prey density inside sealed pens to push predators to 30.",
     species=merge(C3_FLY, REACH, LETHAL, BEETLE_SURV, {"wasp_common": {"predation": {"deposit_satiation": 55.0}}}),
     tuning={"predator_breed_satiation": 50.0}, lab={**SEAL, "max_pop": {"fly_common": 600, "beetle_carrion": 40}},
     fruit={"tree_plum": {"fruit_grow_ticks": 360, "fruit_drop_ticks": 2100, "max_fruit": 8},
            "tree_cherry": {"fruit_grow_ticks": 430, "fruit_drop_ticks": 2520, "max_fruit": 9},
            "tree_apple": {"fruit_grow_ticks": 500, "fruit_drop_ticks": 2940, "max_fruit": 7}})

print("\n10 configs written (E1-5 structural, F1-5 combined). Run: tools/run_sweep.sh 250 E1_flycap400 E2_seal E3_seal_default_fly E4_centi_butterfly E5_seal_centi_butterfly F1_seal_reach F2_seal_lethal F3_seal_breedbar F4_seal_full F5_seal_full_dense")
