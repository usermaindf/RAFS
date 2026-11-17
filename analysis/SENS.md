# Sensitivity analysis and additional VPN seeds

Last updated: 2026-11-17 11:37 (Regenerate manually with: `python sens_report.py`)

Progress: 171 runs; Completed 171, Running 0, Pending 0, Failed 0. 

## A. VPN: 10 RF seeds (seeds 0–2 from the initial runs)

| Setting | Baseline | Field grouping | RAFS | Joint search − Baseline (paired) | Wilcoxon p | Wins/Losses |
|---|---:|---:|---:|---:|---:|---:|
| VPN S0 | 44.9 ± 6.5 (n=10) | 45.6 ± 8.4 (n=10) | 47.4 ± 5.8 (n=10) | +2.5 | 0.322 | 7/3 |
| VPN S1 | 48.4 ± 8.2 (n=10) | 45.9 ± 6.1 (n=10) | 50.1 ± 4.8 (n=10) | +1.7 | 0.557 | 6/4 |
| VPN S2 | 39.8 ± 5.9 (n=10) | 27.3 ± 20.6 (n=10) | 48.0 ± 3.3 (n=10) | +8.2 | 0.00977 | 8/2 |
| **VPN All** | | | | +4.1 | 0.0208 | 21/9 |

## B/C. Hyperparameter sensitivity (RAFS, seeds 0–2, deployment test-set macro F1)

k is the number of top-ranked fields used to form field pairs; w is the number of single-field candidates tested per round (the upstream window parameter).

| Setting | k=3, w=5 | k=4, w=5 (default) | k=5, w=5 | k=4, w=3 | k=4, w=7 |
|---|---:|---:|---:|---:|---:|
| VPN S0 | 47.7 ± 7.6 (n=3) | 47.1 ± 8.1 (n=3) | 48.6 ± 6.7 (n=3) | 51.6 ± 6.1 (n=3) | 37.3 ± 4.6 (n=3) |
| VPN S1 | 45.4 ± 2.4 (n=3) | 49.2 ± 7.2 (n=3) | 46.3 ± 9.4 (n=3) | 49.6 ± 3.4 (n=3) | 49.7 ± 3.4 (n=3) |
| VPN S2 | 46.3 ± 1.5 (n=3) | 49.6 ± 3.7 (n=3) | 49.2 ± 3.8 (n=3) | 50.8 ± 6.3 (n=3) | 49.8 ± 3.5 (n=3) |
| App-Time S0 | 64.2 ± 0.8 (n=3) | 64.1 ± 0.7 (n=3) | 64.2 ± 0.8 (n=3) | 64.6 ± 0.4 (n=3) | 64.5 ± 0.6 (n=3) |
| App-Time S1 | 62.4 ± 1.5 (n=3) | 62.4 ± 1.5 (n=3) | 62.4 ± 1.5 (n=3) | 62.6 ± 1.3 (n=3) | 62.4 ± 1.5 (n=3) |
| App-Time S2 | 31.9 ± 0.3 (n=3) | 31.9 ± 0.3 (n=3) | 31.9 ± 0.3 (n=3) | 32.9 ± 1.3 (n=3) | 31.2 ± 2.2 (n=3) |
| App-Version S0 | 65.3 ± 0.1 (n=3) | 65.4 ± 0.2 (n=3) | 65.4 ± 0.2 (n=3) | 64.9 ± 0.3 (n=3) | 65.3 ± 0.2 (n=3) |
| App-Version S1 | 63.4 ± 0.4 (n=3) | 63.4 ± 0.4 (n=3) | 63.4 ± 0.4 (n=3) | 63.8 ± 0.5 (n=3) | 63.2 ± 0.8 (n=3) |
| App-Version S2 | 36.7 ± 5.0 (n=3) | 36.7 ± 5.0 (n=3) | 36.7 ± 5.0 (n=3) | 39.5 ± 0.4 (n=3) | 39.6 ± 0.2 (n=3) |
| **Mean over settings with all 3 seeds completed** | 51.5 (9/9) | 52.2 (9/9) | 52.0 (9/9) | 53.4 (9/9) | 51.4 (9/9) |
| **Mean retrainings to the selected round** | 107 | 129 | 144 | 86 | 156 |

Reference means: baseline 48.6; field grouping 50.0 (see SEEDS.md).

## Files

- Run sensitivity experiments with `reproduce.py --pair-top` or `--window`; report: `analysis/sens_report.py`; tests: `analysis/stats_tests.py`.
- This report reads archived results and exit-status files.
