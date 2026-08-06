# Bronze hands — two things to point at

Both are taste calls, so I rendered the options instead of guessing. I have guessed the palm direction
wrong twice already.

---

## 1. Which way should the palms face? → `PALMS_compare.png`

The camera-facing walk pastes **one** hand sprite twice and mirrors one of them. Which one gets mirrored
decides whether the palms turn IN toward the body or OUT away from it. All four possibilities:

| | left hand | right hand | what you see |
|---|---|---|---|
| **A_neither** | as drawn | as drawn | both face the same way — asymmetric |
| **B_left** | mirrored | as drawn | a symmetric pair |
| **C_right** | as drawn | mirrored | a symmetric pair, facing the other way — **what ships today** |
| **D_both** | mirrored | mirrored | both face the same way — the mirror of A |

The still is cropped to the hands and blown up 4×, because a looping gif is the wrong medium for judging
which way a palm points — *"i cant even tell which direction that animation is going with it repeating"*.
The four `PALMS_*.gif` files are there too if you want them moving.

**My read: B_left** — its curls turn inward toward the body, and C (today's) turns them outward, which is
the defect you reported. But you decide; say the letter.

---

## 2. Hand size → `HAND_SIZES.png`

Your words: *"the gauntlet on the side facing the screen way too big, if it is scaled it should be
slightly not like having one huge and one small hand."*

I measured three different mismatches and can't tell from the words which you mean, so here are the
numbers on a 320px-tall body:

| used for | source sprite | drawn |
|---|---|---|
| side view, NEAR hand | 16 × 20 | **43 × 54** |
| side view, FAR hand | 18 × 22 | **44 × 54** |
| camera-facing view, both | 12 × 21 | **31 × 54** |

- **Near vs far in the side view: 43 vs 44px — 1.02×, essentially identical.** So "one huge and one
  small" isn't a size difference there. What *does* differ: the far hand is dimmed to 62% and drawn
  behind the body, which reads as smaller and further away even though it is the same size.
- **Side view vs camera-facing: 43 vs 31px — 1.39×.** This one is a real difference. It happens because
  hands are scaled by HEIGHT, so a narrower source sprite (the profile fist, 12px wide vs 16px) draws
  narrower.
- **Overall size: a fist is 17% of body height.** A real fist is about 10–11%.

The sheet shows both views at **0.17 (current) / 0.14 / 0.11** so you can judge the overall size. Frame
picked is full reach, not the passing pose where the fists hide behind the torso.

**Tell me which is wrong** — the overall size (and which ratio), the side-vs-front difference, or the
near/far read in the side view — and I'll fix that one rather than guessing at all three.

---

Both live in `official.py` once you choose: the palm mirroring in the front-walk render, the ratio in
`GAITS`. Change it there, run `build.py`, and every animation and the gallery follow.
