# 2026-08-05 — RED fire-ant, three designs, FACE VISIBLE

> Owner direction (2026-08-05): there will be both a black and a red fire-ant version, and the player's
> face should be visible if possible.

Undirected again — the prompt gives only the material and the colour. What changed is the **head
treatment**: `EXPLORE` gained a `{head}` slot, and these two colourways use `HEAD_FACE` instead of
`HEAD_COVERED`, asking for an open-faced helm with the face drawn. Every other set keeps the full helm.

| | |
|---|---|
| **1** | mandible-horn crown with antennae, plated chest, layered tassets |
| **2** | rounded ant-head hood with antennae, segmented body, leg spurs at the hips |
| **3** | spiked crown/frill, spiked shoulders and thigh plates |

## Checks — best yet

| | red (this) | open (undirected) | directed 3-options |
|---|---|---|---|
| height spread | **1.3%** | 2.6% | 7.0% |
| width spread | 11.3% | 6.3% | — |
| baselines | **all 943** | all 940 | all 927 |
| stray magenta | **0** | 0 | 665 |

Faces read clearly at game size in the bottom row, which was the risk — a face is fine detail and fine
detail is what dies at 40px.

## ⚠ The black batch is MISSING

The paired `ant-carapace-black` call was made in the same command, which hit a **2-minute tool timeout**.
`gen.py` opens the output file *before* the API call returns, so `explore/ant-carapace-black/result.png`
exists at **0 bytes** and the image is gone. `RECORD.txt` was written before the call, so its presence
proves nothing about whether the request completed or was billed.

**Not re-run without asking** — it would be a second charge for something that may already have cost.
