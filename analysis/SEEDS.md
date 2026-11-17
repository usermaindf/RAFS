# Multi-seed comparison: ShortcutCatcher and RAFS variants

Last updated: 2026-11-17 11:37 (Regenerate manually with: `python seeds_report.py`)

Setting: RandomForest; vary only `random_state`. Seed 0 matches the AutoGluon default used in the baseline experiments. All other settings follow the original reproduction commands.

- Baseline, field grouping and the in-loop-only ablation select the round with the highest validation macro F1-score, following upstream `evaluate/table2.py`.
- Grouping + robust verification selects the round with the highest bootstrap lower confidence bound of validation macro F1-score (mean minus one standard deviation).
- The in-loop-only ablation reuses the robust-verification runs but restores the original final-round selection rule.

## 1. Run status

| Setting | Baseline seed 0 | Baseline seed 1 | Baseline seed 2 | Field grouping seed 0 | Field grouping seed 1 | Field grouping seed 2 | Grouping + robust verification seed 0 | Grouping + robust verification seed 1 | Grouping + robust verification seed 2 | Grouping + shift-aware ranking seed 0 | Grouping + shift-aware ranking seed 1 | Grouping + shift-aware ranking seed 2 | RAFS seed 0 | RAFS seed 1 | RAFS seed 2 | Grouping + relative features seed 0 | Grouping + relative features seed 1 | Grouping + relative features seed 2 | RAFS + relative features seed 0 | RAFS + relative features seed 1 | RAFS + relative features seed 2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VPN S0 | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Not run (relative features unavailable for VPN) | Not run (relative features unavailable for VPN) | Not run (relative features unavailable for VPN) | Not run (relative features unavailable for VPN) | Not run (relative features unavailable for VPN) | Not run (relative features unavailable for VPN) |
| VPN S1 | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Not run (relative features unavailable for VPN) | Not run (relative features unavailable for VPN) | Not run (relative features unavailable for VPN) | Not run (relative features unavailable for VPN) | Not run (relative features unavailable for VPN) | Not run (relative features unavailable for VPN) |
| VPN S2 | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Not run (relative features unavailable for VPN) | Not run (relative features unavailable for VPN) | Not run (relative features unavailable for VPN) | Not run (relative features unavailable for VPN) | Not run (relative features unavailable for VPN) | Not run (relative features unavailable for VPN) |
| App-Time S0 | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |
| App-Time S1 | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |
| App-Time S2 | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |
| App-Version S0 | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |
| App-Version S1 | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |
| App-Version S2 | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |

Completed 171 / 171 runs. 

## 2. test set macro-F1 F1*(C): mean ± SD over 3 seeds

| Setting | Baseline | Field grouping | Grouping + robust verification (in-loop only) | Grouping + robust verification | Grouping + shift-aware ranking | RAFS | Grouping + relative features | RAFS + relative features |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| VPN S0 | 49.2 ± 10.5 | 46.4 ± 9.0 | 38.9 ± 5.6 | 38.9 ± 5.6 | 50.7 ± 6.4 | 47.1 ± 8.1 | – | – |
| VPN S1 | 44.9 ± 10.2 | 43.7 ± 8.1 | 49.0 ± 6.6 | 49.0 ± 6.6 | 57.5 ± 7.0 | 49.2 ± 7.2 | – | – |
| VPN S2 | 43.2 ± 7.4 | 36.3 ± 20.2 | 22.0 ± 17.0 | 22.0 ± 17.0 | 19.9 ± 7.9 | 49.6 ± 3.7 | – | – |
| App-Time S0 | 59.0 ± 0.8 | 64.2 ± 0.8 | 64.2 ± 0.8 | 64.2 ± 0.8 | 64.8 ± 0.8 | 64.1 ± 0.7 | 65.1 ± 0.7 | 65.0 ± 0.6 |
| App-Time S1 | 59.1 ± 0.7 | 63.3 ± 1.8 | 62.4 ± 1.5 | 62.4 ± 1.5 | 58.6 ± 1.0 | 62.4 ± 1.5 | 62.6 ± 0.6 | 62.6 ± 0.6 |
| App-Time S2 | 29.9 ± 3.0 | 32.3 ± 0.5 | 32.0 ± 1.0 | 32.0 ± 1.0 | 33.0 ± 0.1 | 31.9 ± 0.3 | 31.2 ± 3.4 | 33.5 ± 1.5 |
| App-Version S0 | 60.5 ± 1.2 | 65.3 ± 0.1 | 65.3 ± 0.1 | 65.3 ± 0.1 | 62.5 ± 1.6 | 65.4 ± 0.2 | 66.0 ± 1.1 | 66.0 ± 1.1 |
| App-Version S1 | 58.9 ± 0.3 | 63.4 ± 0.4 | 63.4 ± 0.4 | 63.4 ± 0.4 | 63.8 ± 0.5 | 63.4 ± 0.4 | 64.2 ± 0.3 | 64.2 ± 0.3 |
| App-Version S2 | 32.3 ± 6.5 | 35.0 ± 4.3 | 35.0 ± 4.3 | 35.0 ± 4.3 | 35.0 ± 2.3 | 36.7 ± 5.0 | 35.1 ± 1.9 | 35.1 ± 1.9 |
| **Mean over 9 settings** | 48.6 | 50.0 | 48.0 | 48.0 | 49.5 | 52.2 | 54.0 | 54.4 |
| **Mean over 6 App settings** (parentheses show settings with all 3 seeds completed) | 50.0 (6/6) | 53.9 (6/6) | 53.7 (6/6) | 53.7 (6/6) | 52.9 (6/6) | 54.0 (6/6) | 54.0 (6/6) | 54.4 (6/6) |

Relative-feature variants run only on App data. Their overall mean covers only App settings; use the App-only row for a comparable evaluation.

## 3. Paired differences from the baseline (same setting and seed)

Format: mean difference ± SD / wins (seeds outperforming the baseline : total seeds)

| Setting | Field grouping | Grouping + robust verification (in-loop only) | Grouping + robust verification | Grouping + shift-aware ranking | RAFS | Grouping + relative features | RAFS + relative features |
|---|---:|---:|---:|---:|---:|---:|---:|
| VPN S0 | -2.7 ± 4.3 / 1:3 | -10.3 ± 15.6 / 1:3 | -10.3 ± 15.6 / 1:3 | 1.6 ± 15.4 / 2:3 | -2.0 ± 15.5 / 1:3 | – | – |
| VPN S1 | -1.2 ± 18.2 / 2:3 | 4.1 ± 4.8 / 2:3 | 4.1 ± 4.8 / 2:3 | 12.6 ± 13.2 / 3:3 | 4.3 ± 16.1 / 2:3 | – | – |
| VPN S2 | -6.9 ± 18.3 / 2:3 | -21.2 ± 23.6 / 1:3 | -21.2 ± 23.6 / 1:3 | -23.3 ± 6.7 / 0:3 | 6.4 ± 7.3 / 2:3 | – | – |
| App-Time S0 | 5.2 ± 0.5 / 3:3 | 5.2 ± 0.5 / 3:3 | 5.2 ± 0.5 / 3:3 | 5.8 ± 1.0 / 3:3 | 5.1 ± 0.4 / 3:3 | 6.1 ± 0.9 / 3:3 | 5.9 ± 1.0 / 3:3 |
| App-Time S1 | 4.2 ± 1.2 / 3:3 | 3.3 ± 1.7 / 3:3 | 3.3 ± 1.7 / 3:3 | -0.5 ± 1.3 / 1:3 | 3.3 ± 1.7 / 3:3 | 3.5 ± 0.8 / 3:3 | 3.5 ± 0.8 / 3:3 |
| App-Time S2 | 2.4 ± 2.6 / 3:3 | 2.1 ± 2.2 / 3:3 | 2.1 ± 2.2 / 3:3 | 3.1 ± 3.1 / 3:3 | 2.0 ± 2.9 / 3:3 | 1.3 ± 4.7 / 2:3 | 3.6 ± 1.6 / 3:3 |
| App-Version S0 | 4.8 ± 1.1 / 3:3 | 4.8 ± 1.1 / 3:3 | 4.8 ± 1.1 / 3:3 | 2.0 ± 2.5 / 2:3 | 4.9 ± 1.1 / 3:3 | 5.5 ± 0.6 / 3:3 | 5.5 ± 0.6 / 3:3 |
| App-Version S1 | 4.5 ± 0.6 / 3:3 | 4.5 ± 0.6 / 3:3 | 4.5 ± 0.6 / 3:3 | 4.9 ± 0.2 / 3:3 | 4.5 ± 0.6 / 3:3 | 5.3 ± 0.1 / 3:3 | 5.3 ± 0.1 / 3:3 |
| App-Version S2 | 2.7 ± 3.2 / 2:3 | 2.7 ± 3.1 / 2:3 | 2.7 ± 3.1 / 2:3 | 2.6 ± 7.5 / 2:3 | 4.4 ± 6.0 / 2:3 | 2.8 ± 7.3 / 2:3 | 2.8 ± 7.3 / 2:3 |
| **All** | 1.4 ± 8.4 / 22:27 | -0.5 ± 11.9 / 21:27 | -0.5 ± 11.9 / 21:27 | 1.0 ± 11.4 / 19:27 | 3.7 ± 7.2 / 22:27 | 4.1 ± 3.5 / 16:18 | 4.4 ± 2.9 / 17:18 |

## 4. Stability: cross-seed SD / worst-seed F1*(C); lower SD and higher worst-seed performance are better

| Setting | Baseline | Field grouping | Grouping + robust verification (in-loop only) | Grouping + robust verification | Grouping + shift-aware ranking | RAFS | Grouping + relative features | RAFS + relative features |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| VPN S0 | 10.5 / 42.5 | 9.0 / 38.4 | 5.6 / 33.5 | 5.6 / 33.5 | 6.4 / 46.3 | 8.1 / 41.1 | – | – |
| VPN S1 | 10.2 / 37.9 | 8.1 / 34.4 | 6.6 / 42.5 | 6.6 / 42.5 | 7.0 / 50.7 | 7.2 / 42.7 | – | – |
| VPN S2 | 7.4 / 36.5 | 20.2 / 14.0 | 17.0 / 10.4 | 17.0 / 10.4 | 7.9 / 11.1 | 3.7 / 46.2 | – | – |
| App-Time S0 | 0.8 / 58.2 | 0.8 / 63.3 | 0.8 / 63.3 | 0.8 / 63.3 | 0.8 / 64.0 | 0.7 / 63.3 | 0.7 / 64.3 | 0.6 / 64.3 |
| App-Time S1 | 0.7 / 58.4 | 1.8 / 61.3 | 1.5 / 61.3 | 1.5 / 61.3 | 1.0 / 57.5 | 1.5 / 61.3 | 0.6 / 61.9 | 0.6 / 61.9 |
| App-Time S2 | 3.0 / 26.5 | 0.5 / 31.8 | 1.0 / 30.9 | 1.0 / 30.9 | 0.1 / 32.9 | 0.3 / 31.8 | 3.4 / 27.6 | 1.5 / 31.8 |
| App-Version S0 | 1.2 / 59.1 | 0.1 / 65.1 | 0.1 / 65.1 | 0.1 / 65.1 | 1.6 / 60.7 | 0.2 / 65.1 | 1.1 / 64.9 | 1.1 / 64.9 |
| App-Version S1 | 0.3 / 58.6 | 0.4 / 63.2 | 0.4 / 63.2 | 0.4 / 63.2 | 0.5 / 63.2 | 0.4 / 63.2 | 0.3 / 63.9 | 0.3 / 63.9 |
| App-Version S2 | 6.5 / 28.5 | 4.3 / 31.0 | 4.3 / 31.0 | 4.3 / 31.0 | 2.3 / 33.2 | 5.0 / 31.0 | 1.9 / 33.6 | 1.9 / 33.6 |

## 5. Efficiency: retrainings to the selected round (mean over 3 seeds)

| Setting | Baseline | Field grouping | Grouping + robust verification (in-loop only) | Grouping + robust verification | Grouping + shift-aware ranking | RAFS | Grouping + relative features | RAFS + relative features |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| VPN S0 | 445 | 93 | 89 | 89 | 116 | 129 | – | – |
| VPN S1 | 309 | 77 | 87 | 87 | 81 | 117 | – | – |
| VPN S2 | 415 | 104 | 100 | 100 | 91 | 125 | – | – |
| App-Time S0 | 453 | 79 | 79 | 79 | 106 | 121 | 109 | 250 |
| App-Time S1 | 223 | 95 | 75 | 75 | 95 | 101 | 71 | 117 |
| App-Time S2 | 335 | 102 | 108 | 108 | 113 | 141 | 109 | 153 |
| App-Version S0 | 241 | 99 | 102 | 102 | 91 | 180 | 105 | 201 |
| App-Version S1 | 293 | 110 | 110 | 110 | 115 | 163 | 133 | 241 |
| App-Version S2 | 341 | 69 | 75 | 75 | 115 | 85 | 75 | 93 |

## 6. Per-seed F1*(C)

| Setting | Baseline seed 0 | Baseline seed 1 | Baseline seed 2 | Field grouping seed 0 | Field grouping seed 1 | Field grouping seed 2 | Grouping + robust verification (in-loop only) seed 0 | Grouping + robust verification (in-loop only) seed 1 | Grouping + robust verification (in-loop only) seed 2 | Grouping + robust verification seed 0 | Grouping + robust verification seed 1 | Grouping + robust verification seed 2 | Grouping + shift-aware ranking seed 0 | Grouping + shift-aware ranking seed 1 | Grouping + shift-aware ranking seed 2 | RAFS seed 0 | RAFS seed 1 | RAFS seed 2 | Grouping + relative features seed 0 | Grouping + relative features seed 1 | Grouping + relative features seed 2 | RAFS + relative features seed 0 | RAFS + relative features seed 1 | RAFS + relative features seed 2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| VPN S0 | 43.7 | 61.3 | 42.5 | 38.4 | 56.2 | 44.7 | 38.4 | 33.5 | 44.7 | 38.4 | 33.5 | 44.7 | 47.9 | 46.3 | 58.1 | 41.1 | 44.0 | 56.3 |  |  |  |  |  |  |
| VPN S1 | 40.1 | 56.6 | 37.9 | 48.8 | 34.4 | 47.9 | 48.8 | 55.7 | 42.5 | 48.8 | 55.7 | 42.5 | 50.7 | 57.1 | 64.6 | 57.0 | 42.7 | 47.9 |  |  |  |  |  |  |
| VPN S2 | 36.5 | 42.0 | 51.1 | 41.5 | 14.0 | 53.4 | 41.5 | 14.0 | 10.4 | 41.5 | 14.0 | 10.4 | 11.1 | 26.2 | 22.4 | 46.2 | 53.5 | 49.1 |  |  |  |  |  |  |
| App-Time S0 | 58.2 | 59.0 | 59.9 | 63.3 | 64.7 | 64.6 | 63.3 | 64.7 | 64.6 | 63.3 | 64.7 | 64.6 | 65.0 | 64.0 | 65.5 | 63.3 | 64.5 | 64.6 | 65.2 | 64.3 | 65.7 | 65.2 | 64.3 | 65.4 |
| App-Time S1 | 59.0 | 58.4 | 59.8 | 64.1 | 61.3 | 64.5 | 64.1 | 61.3 | 61.8 | 64.1 | 61.3 | 61.8 | 57.5 | 59.4 | 58.7 | 64.1 | 61.3 | 61.8 | 61.9 | 62.8 | 63.1 | 61.9 | 62.8 | 63.1 |
| App-Time S2 | 26.5 | 31.4 | 31.9 | 31.8 | 32.9 | 32.2 | 30.9 | 32.9 | 32.2 | 30.9 | 32.9 | 32.2 | 33.1 | 32.9 | 33.1 | 31.8 | 31.8 | 32.2 | 31.8 | 27.6 | 34.3 | 31.8 | 34.4 | 34.3 |
| App-Version S0 | 61.1 | 59.1 | 61.2 | 65.3 | 65.1 | 65.4 | 65.3 | 65.1 | 65.4 | 65.3 | 65.1 | 65.4 | 60.7 | 63.6 | 63.3 | 65.5 | 65.1 | 65.4 | 67.0 | 64.9 | 66.1 | 67.0 | 64.9 | 66.1 |
| App-Version S1 | 58.9 | 58.6 | 59.3 | 63.9 | 63.2 | 63.2 | 63.9 | 63.2 | 63.2 | 63.9 | 63.2 | 63.2 | 63.9 | 63.2 | 64.2 | 63.9 | 63.2 | 63.2 | 64.3 | 63.9 | 64.4 | 64.3 | 63.9 | 64.4 |
| App-Version S2 | 28.5 | 28.7 | 39.9 | 31.0 | 34.6 | 39.5 | 31.0 | 34.6 | 39.5 | 31.0 | 34.6 | 39.5 | 33.2 | 37.5 | 34.1 | 31.0 | 39.8 | 39.5 | 33.6 | 37.3 | 34.5 | 33.6 | 37.3 | 34.5 |

## Files

- Run experiments with `python reproduce.py`; see README.md for variants and seed selections.
- Report generator: `analysis/seeds_report.py`; metrics are computed by `analysis/compare.py`.
- Archived count logs: `analysis/logs_<variant>[_seed<k>]/`; result CSVs: `results/results_<variant>[_seed<k>]/`.
- Relative-feature experiments are available only for App-Time and App-Version.
