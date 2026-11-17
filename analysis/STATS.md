# Paired statistical tests for the main comparisons

Generated: 2026-11-17 11:37. Script: `stats_tests.py`(same archived measurements as SEEDS.md). 

The pairing unit is setting × RF seed. Data splits and seeds are matched across methods, using the documented final-round selection rules. Tests use the two-sided Wilcoxon signed-rank test, with Holm correction within each table. Section 1 uses 10 VPN seeds (0–9) for the baseline, field grouping and RAFS; other comparisons use 3 seeds. Sections 2 and 3 use seeds 0–2. Significance: *** p<0.001, ** p<0.01, * p<0.05; n.s. denotes non-significance, based on adjusted p-values.

## 1. Deployment test-set macro F1: paired differences (B − A)

| Comparison (B vs A) | Scope | n | Mean difference | 95% bootstrap CI | Wins/Ties/Losses | Sign test p | Wilcoxon p | Holm adjusted p | Significance |
|---|---|---:|---:|---|---|---:|---:|---:|---|
| Field grouping vs Baseline | 9  settings | 48 | -1.50 | [-4.87, +1.61] | 30/0/18 | 0.111 | 0.883 | 1 | n.s. |
| Field grouping vs Baseline | App 6  settings | 18 | +3.96 | [+3.07, +4.75] | 17/0/1 | 0.000145 | 2.29e-05 | 0.000412 | *** |
| Field grouping vs Baseline | VPN 3  settings | 30 | -4.77 | [-9.63, +0.05] | 13/0/17 | 0.585 | 0.146 | 1 | n.s. |
| RAFS vs Baseline | 9  settings | 48 | +4.10 | [+2.00, +6.10] | 38/0/10 | 6.17e-05 | 0.000177 | 0.00266 | ** |
| RAFS vs Baseline | App 6  settings | 18 | +4.03 | [+2.90, +5.24] | 17/0/1 | 0.000145 | 3.81e-05 | 0.00061 | *** |
| RAFS vs Baseline | VPN 3  settings | 30 | +4.15 | [+0.81, +7.21] | 21/0/9 | 0.0428 | 0.0208 | 0.208 | n.s. |
| RAFS vs Field grouping | 9  settings | 48 | +5.60 | [+2.17, +9.33] | 21/15/12 | 0.163 | 0.0121 | 0.133 | n.s. |
| RAFS vs Field grouping | App 6  settings | 18 | +0.07 | [-0.49, +0.80] | 2/12/4 | 0.688 | 0.6 | 1 | n.s. |
| RAFS vs Field grouping | VPN 3  settings | 30 | +8.91 | [+3.64, +14.57] | 19/3/8 | 0.0522 | 0.00947 | 0.114 | n.s. |
| Grouping + shift-aware ranking vs Baseline | 9  settings | 27 | +0.98 | [-3.43, +4.94] | 19/0/8 | 0.0522 | 0.135 | 1 | n.s. |
| Grouping + shift-aware ranking vs Baseline | App 6  settings | 18 | +2.98 | [+1.28, +4.54] | 14/0/4 | 0.0309 | 0.0056 | 0.0728 | n.s. |
| Grouping + shift-aware ranking vs Baseline | VPN 3  settings | 9 | -3.03 | [-14.28, +8.84] | 5/0/4 | 1 | 0.734 | 1 | n.s. |
| Grouping + robust verification vs Baseline | 9  settings | 27 | -0.54 | [-5.33, +3.28] | 21/0/6 | 0.00592 | 0.0385 | 0.347 | n.s. |
| Grouping + robust verification vs Baseline | App 6  settings | 18 | +3.75 | [+2.88, +4.57] | 17/0/1 | 0.000145 | 2.29e-05 | 0.000412 | *** |
| Grouping + robust verification vs Baseline | VPN 3  settings | 9 | -9.12 | [-20.70, +1.46] | 4/0/5 | 1 | 0.426 | 1 | n.s. |
| RAFS + relative features vs RAFS | App 6  settings | 18 | +0.42 | [-0.53, +1.23] | 13/0/5 | 0.0963 | 0.154 | 1 | n.s. |
| Grouping + relative features vs Field grouping | App 6  settings | 18 | +0.13 | [-0.96, +1.10] | 12/0/6 | 0.238 | 0.369 | 1 | n.s. |
| RAFS + relative features vs Baseline | App 6  settings | 18 | +4.45 | [+3.04, +5.55] | 17/0/1 | 0.000145 | 0.00042 | 0.00587 | ** |

## 2. Stability: cross-seed SD and worst-seed performance (Wilcoxon; pairing unit: setting)

| Comparison (B vs A) | Scope | Settings | SD A → B (Mean) | p (SD) | Worst seed A → B (Mean) | p (Worst seed) |
|---|---|---:|---|---:|---|---:|
| Field grouping vs Baseline | 9  settings | 9 | 4.5 → 5.0 | 1 n.s. | 45.1 → 44.7 | 1 n.s. |
| RAFS vs Baseline | 9  settings | 9 | 4.5 → 3.0 | 0.301 n.s. | 45.1 → 49.5 | 0.0938 n.s. |
| RAFS vs Field grouping | 9  settings | 9 | 5.0 → 3.0 | 0.902 n.s. | 44.7 → 49.5 | 0.87 n.s. |
| RAFS vs Baseline | VPN 3  settings | 3 | 9.4 → 6.3 | 1 n.s. | 39.0 → 43.3 | 1 n.s. |
| RAFS vs Baseline | App 6  settings | 6 | 2.1 → 1.4 | 1 n.s. | 48.2 → 52.6 | 0.312 n.s. |
| RAFS + relative features vs RAFS | App 6  settings | 6 | 1.4 → 1.0 | 1 n.s. | 52.6 → 53.4 | 0.844 n.s. |

With only 3 seeds, within-setting SD estimates are imprecise. With only 3–9 settings, the attainable Wilcoxon p-values are also limited (0.25 at n=3, 0.031 at n=6, and 0.0039 at n=9). Treat this section as exploratory.

## 3. Efficiency: retrainings through the selected round (pairing unit: setting × seed)

| Comparison (B vs A) | n | A Mean | B Mean | B / A | Wilcoxon p |
|---|---:|---:|---:|---:|---:|
| Field grouping vs Baseline | 27 | 339 | 92 | 0.27 | 1.49e-08 *** |
| RAFS vs Baseline | 27 | 339 | 129 | 0.38 | 1.49e-08 *** |
| RAFS vs Field grouping | 27 | 92 | 129 | 1.40 | 0.000137 *** |
