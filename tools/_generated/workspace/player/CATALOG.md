# Player art catalog — the running index

What player sprites + wearables exist or are in progress, so we don't have to remember. **Update this when you
start or finish a piece.** Status: `idea` · `in-progress` · `shipped` (published to `Resources/Player/layers/`).

## Base character
| id | direction(s) | status | notes |
|----|--------------|--------|-------|
| `base` | down (+ bald variant) | shipped | the locked base gear composites onto; lives in `refs/` |
| `hair` | down | shipped | hair-as-a-layer on the bald base |

## Wearables (by slot)
| id / set | slot(s) | status | notes |
|----------|---------|--------|-------|
| `copper_armor` | helmet · chest · legs · feet | in-progress | one-pass full-suit render being masked into pieces (owner) |
| `silver_armor` | helmet · chest · legs · feet | in-progress | fancy silver set being masked into pieces (owner) |

_(This is the starting index; extend the tables as we add caps, tools, more sets. Directions beyond `down`
get added when the walk animation needs them.)_
