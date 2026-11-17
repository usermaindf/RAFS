"""Paired statistical tests for the main comparisons -> STATS.md

Unit of pairing: (setting, RF seed). All methods use identical data splits, the same RF seed and the same
final-round rule (argmax verification macro-F1, as evaluate/table2.py).
Tests
  * accuracy:   Wilcoxon signed-rank (two-sided) on paired check-set F1 differences; sign test;
                bootstrap 95% CI of the mean difference (10,000 resamples of the pairs)
  * stability:  per setting, the cross-seed std and the worst seed; Wilcoxon over the 9 (or 6) settings
  * efficiency: retrainings until the selected round; Wilcoxon on paired differences
Multiple comparisons: Holm correction within each table.
Usage: python stats_tests.py
"""
import datetime as dt
import math
import os

import numpy as np
from scipy.stats import binomtest, wilcoxon

import compare
import seeds_report as R

HERE = os.environ.get('RAFS_LOG_ROOT', os.path.dirname(os.path.abspath(__file__)))
NAMES = {'none': 'Baseline', 'group': 'Field grouping', 'grouppair': 'RAFS', 'grouprel': 'Grouping + relative features',
         'grouppairrel': 'RAFS + relative features', 'groupshift': 'Grouping + shift-aware ranking', 'grouprob': 'Grouping + robust verification'}
COMPARISONS = [  # (method A, method B, scope)
    ('none', 'group', 'all'), ('none', 'grouppair', 'all'), ('group', 'grouppair', 'all'),
    ('none', 'groupshift', 'all'), ('none', 'grouprob', 'all'),
    ('grouppair', 'grouppairrel', 'app'), ('group', 'grouprel', 'app'), ('none', 'grouppairrel', 'app'),
]
SCOPES = {'all': '9  settings', 'app': 'App 6  settings', 'vpn': 'VPN 3  settings'}


def load():
    res = {}
    for name, _ in R.SETTINGS:
        for var in NAMES:
            seeds = range(10) if name.startswith('vpn') and var in ('none', 'group', 'grouppair') else R.SEEDS
            for s in seeds:
                if 'rel' in var and name.startswith('vpn'):
                    continue
                rt, ld = R.dirs(var, s)
                if not os.path.exists(os.path.join(HERE, ld, f'{name}.exit')):
                    continue
                r = compare.one(rt, ld, name, rule='lcb' if var == 'grouprob' else 'f1')
                if r:
                    res[(var, s, name)] = r
    return res


def in_scope(name, scope):
    return scope == 'all' or (scope == 'app' and name.startswith('app53')) or (scope == 'vpn' and name.startswith('vpn'))


def holm(ps):
    order = np.argsort(ps)
    adj = np.empty(len(ps))
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (len(ps) - rank) * ps[i])
        adj[i] = min(1.0, running)
    return adj


def wil(d):
    d = np.asarray(d, float)
    if np.all(d == 0) or len(d) < 2:
        return 1.0
    return float(wilcoxon(d, zero_method='wilcox', alternative='two-sided').pvalue)


def boot_ci(d, B=10000, seed=0):
    d = np.asarray(d, float)
    rng = np.random.RandomState(seed)
    m = d[rng.randint(0, len(d), size=(B, len(d)))].mean(1)
    return np.percentile(m, 2.5), np.percentile(m, 97.5)


def stars(p):
    return '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'n.s.'


def main():
    res = load()
    L = ['# Paired statistical tests for the main comparisons', '',
         f'Generated: {dt.datetime.now():%Y-%m-%d %H:%M}. Script: `stats_tests.py`(same archived measurements as SEEDS.md). ', '',
         'The pairing unit is setting × RF seed. Data splits and seeds are matched across methods, using the documented final-round selection rules. '
         'Tests use the two-sided Wilcoxon signed-rank test, with Holm correction within each table. '
         'Section 1 uses 10 VPN seeds (0–9) for the baseline, field grouping and RAFS; other comparisons use 3 seeds. Sections 2 and 3 use seeds 0–2. '
         'Significance: *** p<0.001, ** p<0.01, * p<0.05; n.s. denotes non-significance, based on adjusted p-values.', '']

    # ---------------- accuracy
    rows, ps = [], []
    for a, b, scope in COMPARISONS:
        for sc in ([scope] if scope == 'app' else ['all', 'app', 'vpn']):
            d = [res[(b, s, n)]['cs'] - res[(a, s, n)]['cs'] for n, _ in R.SETTINGS for s in range(10)
                 if in_scope(n, sc) and (a, s, n) in res and (b, s, n) in res]
            if not d:
                continue
            p = wil(d)
            lo, hi = boot_ci(d)
            wins = sum(x > 0 for x in d); ties = sum(x == 0 for x in d)
            p_sign = binomtest(wins, len(d) - ties, 0.5).pvalue if len(d) - ties > 0 else 1.0
            rows.append([f'{NAMES[b]} vs {NAMES[a]}', SCOPES[sc], len(d), np.mean(d), lo, hi,
                         f'{wins}/{ties}/{len(d) - wins - ties}', p_sign, p])
            ps.append(p)
    adj = holm(np.array(ps))
    L += ['## 1. Deployment test-set macro F1: paired differences (B − A)', '',
          '| Comparison (B vs A) | Scope | n | Mean difference | 95% bootstrap CI | Wins/Ties/Losses | Sign test p | Wilcoxon p | Holm adjusted p | Significance |',
          '|---|---|---:|---:|---|---|---:|---:|---:|---|']
    for r, pa in zip(rows, adj):
        L.append(f'| {r[0]} | {r[1]} | {r[2]} | {r[3]:+.2f} | [{r[4]:+.2f}, {r[5]:+.2f}] | {r[6]} | '
                 f'{r[7]:.3g} | {r[8]:.3g} | {pa:.3g} | {stars(pa)} |')

    # ---------------- stability
    L += ['', '## 2. Stability: cross-seed SD and worst-seed performance (Wilcoxon; pairing unit: setting)', '',
          '| Comparison (B vs A) | Scope | Settings | SD A → B (Mean) | p (SD) | Worst seed A → B (Mean) | p (Worst seed) |',
          '|---|---|---:|---|---:|---|---:|']
    srows, sps = [], []
    for a, b, scope in [('none', 'group', 'all'), ('none', 'grouppair', 'all'), ('group', 'grouppair', 'all'),
                        ('none', 'grouppair', 'vpn'), ('none', 'grouppair', 'app'), ('grouppair', 'grouppairrel', 'app')]:
        sa, sb, wa, wb = [], [], [], []
        for n, _ in R.SETTINGS:
            if not in_scope(n, scope):
                continue
            xa = [res[(a, s, n)]['cs'] for s in R.SEEDS if (a, s, n) in res]
            xb = [res[(b, s, n)]['cs'] for s in R.SEEDS if (b, s, n) in res]
            if len(xa) == 3 and len(xb) == 3:
                sa.append(np.std(xa, ddof=1)); sb.append(np.std(xb, ddof=1)); wa.append(min(xa)); wb.append(min(xb))
        if not sa:
            continue
        p1 = wil(np.array(sb) - np.array(sa)); p2 = wil(np.array(wb) - np.array(wa))
        srows.append((a, b, scope, len(sa), np.mean(sa), np.mean(sb), np.mean(wa), np.mean(wb), p1, p2))
        sps += [p1, p2]
    sadj = holm(np.array(sps)) if sps else []
    for k, r in enumerate(srows):
        L.append(f'| {NAMES[r[1]]} vs {NAMES[r[0]]} | {SCOPES[r[2]]} | {r[3]} | {r[4]:.1f} → {r[5]:.1f} | '
                 f'{sadj[2 * k]:.3g} {stars(sadj[2 * k])} | {r[6]:.1f} → {r[7]:.1f} | {sadj[2 * k + 1]:.3g} {stars(sadj[2 * k + 1])} |')
    L += ['', 'With only 3 seeds, within-setting SD estimates are imprecise. With only 3–9 settings, the attainable Wilcoxon p-values are also limited'
          ' (0.25 at n=3, 0.031 at n=6, and 0.0039 at n=9). Treat this section as exploratory.']

    # ---------------- efficiency
    L += ['', '## 3. Efficiency: retrainings through the selected round (pairing unit: setting × seed)', '',
          '| Comparison (B vs A) | n | A Mean | B Mean | B / A | Wilcoxon p |', '|---|---:|---:|---:|---:|---:|']
    for a, b in [('none', 'group'), ('none', 'grouppair'), ('group', 'grouppair')]:
        xa, xb = [], []
        for n, _ in R.SETTINGS:
            for s in R.SEEDS:
                if s < 3 and (a, s, n) in res and (b, s, n) in res:
                    xa.append(res[(a, s, n)]['fits_to_best']); xb.append(res[(b, s, n)]['fits_to_best'])
        p = wil(np.array(xb) - np.array(xa))
        L.append(f'| {NAMES[b]} vs {NAMES[a]} | {len(xa)} | {np.mean(xa):.0f} | {np.mean(xb):.0f} | '
                 f'{np.mean(xb) / np.mean(xa):.2f} | {p:.3g} {stars(p)} |')
    with open(os.path.join(HERE, 'STATS.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')
    print('written STATS.md')


if __name__ == '__main__':
    main()
