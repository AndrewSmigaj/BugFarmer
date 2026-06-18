#!/usr/bin/env python3
"""Generate sweep-3: 10 configs targeting the predator FLOOR with PREY IMMIGRATION — the fix sweeps 1-2
pointed to. Run this, then `tools/run_sweep.sh 250 G1_immig_open G2_immig_seal ... G10_immig_full_culled`.

SWEEP 1-2 VERDICT (30 runs): fly→100 (C3) and butterfly~90 SOLVED. But wasp/centipede/beetle stayed
FLOOR through EVERY predator/prey/food parameter AND sealing. Root cause (proven from the predation log):
the predator pens have no SUSTAINED prey. A predator alone with a small fly seed eats it to extinction in
~3 days, then — with no prey immigration (sealed) or all fly breeding monopolised by the fly_pen (open) —
its pen stays permanently empty and it lives on re-seed. Classic small-system predator-prey collapse; no
parameter fixes it.

THE FIX — prey immigration. spawnSwarmForSpecies picks a RANDOM spawn area, and fly_common has spawn areas
in all three pens (fly/wasp/centipede). So turning ON continuous fly spawning (spawn_interval 999999→20s,
swarm-count max 12→40) trickles fresh flies into every predator pen continuously — sustained prey to hunt.
This is NOT life-support/hack: in the real game predators roam a big world full of self-sustaining flies;
the lab's tiny isolated pens break that spatial reality, and immigration restores it. Flies themselves are
already self-maintained (C3). G* test immigration alone then combine it with the best predator behaviour.

Reused: C3 = fly repro_cd 18/breed 16; REACH/LETHAL/BREEDBAR/BEETLE as in sweep-2.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
C3_FLY = {"fly_common": {"reproduce_cooldown": 18.0, "breed_amount": 16.0}}
CENTI_BUTTERFLY = {"centipede_garden": {"predation": {"prey": ["fly_common", "butterfly_meadow"]}}}
REACH = {"centipede_garden": {"vision_range": 26, "base_speed": 2.5, "predation": {"hunt_speed_mult": 2.6}},
         "wasp_common": {"vision_range": 32, "base_speed": 2.8, "predation": {"hunt_speed_mult": 2.2, "home_range": 70.0}}}
LETHAL = {"centipede_garden": {"predation": {"feed_per_kill": 65.0, "strike_cooldown_ticks": 20, "strike_radius": 3.2}},
          "wasp_common": {"predation": {"feed_per_kill": 65.0, "strike_cooldown_ticks": 55, "strike_radius": 3.8}}}
BEETLE_SURV = {"beetle_carrion": {"satiation_decay_rate": 0.05}}
WASP_DEPOSIT = {"wasp_common": {"predation": {"deposit_satiation": 55.0}}}


def merge(*ds):
    out = {}
    for d in ds:
        for sid, fields in d.items():
            out.setdefault(sid, {})
            for k, v in fields.items():
                if k == "predation" and isinstance(out[sid].get("predation"), dict):
                    out[sid]["predation"] = {**out[sid]["predation"], **v}
                else:
                    out[sid][k] = v
    return out


def immig(interval=20):
    # continuous fly immigration: spawn a fresh fly swarm every `interval` game-sec, distributed at random
    # across all fly spawn areas (≈1/3 land in each predator pen); raise the swarm-count cap so it keeps firing.
    return {"caps": {"fly_common": {"spawn_interval": float(interval), "max": 40}}}


def lab(*dicts):
    out = {}
    for d in dicts:
        for k, v in d.items():
            if isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k] = {**out[k], **v}
            else:
                out[k] = v
    return out


SEAL = {"seal_pens": True}
CAP = lambda n: {"max_pop": {"fly_common": n}}


def emit(name, desc, *, extends="01_no_cull", species=None, tuning=None, lab=None, fruit=None):
    cfg = {"name": name, "description": desc, "extends": extends}
    for k, v in (("species", species), ("tuning", tuning), ("lab", lab), ("fruit", fruit)):
        if v:
            cfg[k] = v
    with open(os.path.join(HERE, f"{name}.json"), "w") as f:
        json.dump(cfg, f, indent=2)
    print("wrote", name)


FULL_PRED = merge(C3_FLY, REACH, LETHAL, BEETLE_SURV, WASP_DEPOSIT)

emit("G1_immig_open", "IMMIG: continuous fly immigration (20s) + cap400 + C3, pens OPEN. Baseline immigration test.",
     species=C3_FLY, lab=lab(immig(20), CAP(400)))
emit("G2_immig_seal", "IMMIG: immigration(20s) + SEALED + cap400 + C3. Contained pens kept stocked with fresh prey — the key test.",
     species=C3_FLY, lab=lab(immig(20), SEAL, CAP(400)))
emit("G3_immig_fast", "IMMIG: faster immigration (10s) + sealed + cap400 + C3. More prey turnover.",
     species=C3_FLY, lab=lab(immig(10), SEAL, CAP(400)))
emit("G4_immig_reach", "IMMIG: immigration(20s) + sealed + cap400 + C3 + REACH — predators find the immigrants fast.",
     species=merge(C3_FLY, REACH), lab=lab(immig(20), SEAL, CAP(400)))
emit("G5_immig_lethal", "IMMIG: immigration(20s) + sealed + cap400 + C3 + LETHALITY — convert each encounter to a kill+meal.",
     species=merge(C3_FLY, LETHAL), lab=lab(immig(20), SEAL, CAP(400)))
emit("G6_immig_breedbar", "IMMIG: immigration(20s) + sealed + cap400 + C3 + low breed bar (predator_breed_satiation 50, wasp deposit 55).",
     species=merge(C3_FLY, WASP_DEPOSIT), tuning={"predator_breed_satiation": 50.0}, lab=lab(immig(20), SEAL, CAP(400)))
emit("G7_immig_full", "IMMIG: immigration(20s) + sealed + cap400 + C3 + reach + lethality + low breed bar + beetle survival — full predator push.",
     species=FULL_PRED, tuning={"predator_breed_satiation": 50.0},
     lab=lab(immig(20), SEAL, {"max_pop": {"fly_common": 400, "beetle_carrion": 40}}))
emit("G8_immig_full_fast", "IMMIG: G7 but faster immigration (10s) + cap500 — more prey for a bigger predator population.",
     species=FULL_PRED, tuning={"predator_breed_satiation": 50.0},
     lab=lab(immig(10), SEAL, {"max_pop": {"fly_common": 500, "beetle_carrion": 40}}))
emit("G9_immig_centi_butterfly", "IMMIG: immigration(20s) + sealed + cap400 + C3 + centipede also eats butterflies (a 2nd prey) + reach.",
     species=merge(C3_FLY, REACH, CENTI_BUTTERFLY), lab=lab(immig(20), SEAL, CAP(400)))
emit("G10_immig_full_culled", "IMMIG: G7's full predator push but with the Director CULLS back ON (extends baseline) — the game-ready guardrailed config.",
     extends="00_baseline", species=FULL_PRED, tuning={"predator_breed_satiation": 50.0},
     lab=lab(immig(20), SEAL, {"max_pop": {"fly_common": 400, "beetle_carrion": 40}}))

print("\n10 configs written (G1-10, prey-immigration). Smoke-test G2 first, then run the batch.")
