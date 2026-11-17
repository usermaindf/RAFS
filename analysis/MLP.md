# MLP evaluation in S2 (comparison with ShortcutCatcher Table 4)

Last updated: 2026-11-17 11:37 (Regenerate manually with: `python mlp_report.py`)

Configuration: AutoGluon NeuralNetTorch defaults, permutation importance, window 5, following upstream Table 4.
- VPN S2: 100 rounds, MLP seeds 0, 1 and 2, on CPU.
- App-Time / App-Version S2: recorded training took about 200 seconds per fit; a full baseline search would take about 28 hours. The report uses a **matched-compute comparison**: the baseline is capped at 34 rounds (about 200 retrainings), while RAFS runs to completion (about 200 retrainings). This report lists App seed 0 on GPU.

| Run | Status | F1⁰(C) | F1*(C) | Best / completed rounds | Retrainings to best round | Total retrainings |
|---|---|---:|---:|---:|---:|---:|
| VPN S2 · Baseline · seed 0 | Completed | 11.8 | 41.4 | 57 / 91 | 337 | 535 |
| VPN S2 · Baseline · seed 1 | Completed | 16.2 | 13.1 | 46 / 91 | 271 | 535 |
| VPN S2 · Baseline · seed 2 | Completed | 21.2 | 51.9 | 54 / 91 | 319 | 535 |
| VPN S2 · RAFS · seed 0 | Completed | 11.8 | 47.9 | 14 / 17 | 157 | 187 |
| VPN S2 · RAFS · seed 1 | Completed | 16.2 | 40.9 | 12 / 19 | 133 | 211 |
| VPN S2 · RAFS · seed 2 | Completed | 21.2 | 49.2 | 12 / 18 | 133 | 204 |
| App-Time S2 · Baseline · seed 0 | Completed | 9.0 | 14.2 | 10 / 34 | 55 | 199 |
| App-Version S2 · Baseline · seed 0 | Completed | 12.2 | 22.8 | 17 / 34 | 97 | 199 |
| App-Time S2 · RAFS · seed 0 | Completed | 9.0 | 27.1 | 15 / 16 | 169 | 176 |
| App-Version S2 · RAFS · seed 0 | Completed | 12.2 | 29.3 | 15 / 15 | 164 | 164 |

## Summary of completed runs

| Setting | Upstream Table 4 (F1⁰(C) → F1*(C)) | Reproduced Baseline F1*(C) | RAFS F1*(C) | Difference |
|---|---|---:|---:|---:|
| VPN S2 | 21.2 → 21.1 | 35.5 ± 20.1 (n=3) | 46.0 ± 4.5 (n=3) | 10.5 ± 15.6 (n=3) |
| App-Time S2 | 8.3 → 22.1 | 14.2 | 27.1 | 12.9 |
| App-Version S2 | 12.5 → 25.0 | 22.8 | 29.3 | 6.5 |

The two App rows use matched compute with the baseline capped at 34 rounds, so they are not directly comparable with the 100-round baseline in upstream Table 4. The VPN row follows the upstream configuration.

Run MLP experiments with `reproduce.py --model NeuralNetTorch`; see README.md for round limits.
