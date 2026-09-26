#!/bin/sh
# Apply Parts 1+2 data/build steps: lamp light blocks -> publish -> Go tests -> server rebuild.
set -e
cd "$(dirname "$0")/.."

echo "=== 1. lamp/torch light blocks (data-driven world.light) ==="
python3 - <<'PY'
import json
p='nakama/data/entities/placeables.json'
d=json.load(open(p))
lights={
 'torch':            {'radius':3.5,'color':'#FFB35C','intensity':1.0},
 'campfire':         {'radius':5.0,'color':'#FF9A3D','intensity':1.1},
 'lamp_post':        {'radius':6.0,'color':'#FFD27F','intensity':1.0},
 'lantern':          {'radius':4.0,'color':'#FFD27F','intensity':0.9},
 'lamp_floor':       {'radius':4.0,'color':'#FFE0A3','intensity':0.9},
 'lamp_table':       {'radius':3.0,'color':'#FFE0A3','intensity':0.8},
 'candelabra':       {'radius':3.0,'color':'#FFC97F','intensity':0.8},
 'lamp_floor_fancy': {'radius':4.5,'color':'#FFE0A3','intensity':1.0},
}
done=[]
for k,v in lights.items():
    if k in d:
        d[k].setdefault('world',{})['light']=v
        done.append(k)
json.dump(d,open(p,'w'),indent=2)
print('light blocks added:', ', '.join(done))
PY
python3 tools/data/publish_entities.py | tail -1

echo "=== 2. Go unit tests (incl. tree water gating) ==="
sh tools/run_go_tests.sh | tail -22

echo "=== 3. server rebuild (water-gated trees + day rollover) ==="
docker compose build builder | tail -1
docker compose up -d --force-recreate nakama | tail -1
sleep 8
docker compose logs nakama --since 15s 2>&1 | grep -cE "module loaded successfully|Startup done" || true
echo "=== done ==="
