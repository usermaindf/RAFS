"""Progress + results for step 3 -> SENS.md
  A) VPN with 10 RF seeds (0..9): original / field grouping / grouping + joint search
  B/C) sensitivity of grouping + joint search to pair_top (k) and window (w), seeds 0..2
Also re-runs stats_tests.py at the end of each refresh (STATS.md uses 10 VPN seeds once available).
Usage: python sens_report.py
"""
import datetime as dt
import os
import re
import subprocess
import sys

import numpy as np
from scipy.stats import wilcoxon

import compare
import seeds_report as R

HERE = os.environ.get('RAFS_LOG_ROOT', os.path.dirname(os.path.abspath(__file__)))
VPN = [n for n, _ in R.SETTINGS if n.startswith('vpn')]
CFGS = [('grouppair_k3', 'k=3, w=5'), ('grouppair', 'k=4, w=5 (default)'), ('grouppair_k5', 'k=5, w=5'),
        ('grouppair_w3', 'k=4, w=3'), ('grouppair_w7', 'k=4, w=7')]


def get(var, seed, name):
    rt, ld = R.dirs(var, seed)
    ex = os.path.join(HERE, ld, f'{name}.exit')
    if not os.path.exists(ex) or open(ex).read().strip() != '0':
        return None
    return compare.one(rt, ld, name, rule='f1')


def state(var, seed, name):
    rt, ld = R.dirs(var, seed)
    ex, log = os.path.join(HERE, ld, f'{name}.exit'), os.path.join(HERE, ld, f'{name}.log')
    if os.path.exists(ex):
        return 'ok' if open(ex).read().strip() == '0' else 'fail'
    return 'run' if os.path.exists(log) else 'wait'


def ms(v):
    if not v:
        return '–'
    return f'{np.mean(v):.1f} ± {np.std(v, ddof=1):.1f} (n={len(v)})' if len(v) > 1 else f'{v[0]:.1f}'


def main():
    L = ['# Sensitivity analysis and additional VPN seeds', '',
         f'Last updated: {dt.datetime.now():%Y-%m-%d %H:%M} (Regenerate manually with: `python sens_report.py`)', '']
    if os.path.exists(os.path.join(HERE, 'SENS_ALL_DONE')):
        L += ['**All experiments completed. **', '']
    # progress
    cnt = {'ok': 0, 'fail': 0, 'run': 0, 'wait': 0}
    jobs = [(v, s, n) for s in range(3, 10) for v in ('grouppair', 'group', 'none') for n in VPN] + \
           [(v, s, n) for s in range(3) for v, _ in CFGS if v != 'grouppair' for n, _ in R.SETTINGS]
    for j in jobs:
        cnt[state(*j)] += 1
    fails = [f'{v} seed {s} {n}' for v, s, n in jobs if state(v, s, n) == 'fail']
    L += [f'Progress: {len(jobs)} runs; Completed {cnt["ok"]}, Running {cnt["run"]}, Pending {cnt["wait"]}, Failed {cnt["fail"]}. ', '']
    if fails:
        L += ['Failed runs: ' + '; '.join(fails), '']

    # A) VPN 10 seeds
    L += ['## A. VPN: 10 RF seeds (seeds 0–2 from the initial runs)', '',
          '| Setting | Baseline | Field grouping | RAFS | Joint search − Baseline (paired) | Wilcoxon p | Wins/Losses |',
          '|---|---:|---:|---:|---:|---:|---:|']
    allp = []
    for n in VPN:
        v = {m: [r['cs'] for s in range(10) if (r := get(m, s, n))] for m in ('none', 'group', 'grouppair')}
        d = [get('grouppair', s, n)['cs'] - get('none', s, n)['cs'] for s in range(10)
             if get('grouppair', s, n) and get('none', s, n)]
        allp += d
        p = wilcoxon(d).pvalue if len(d) >= 2 and any(d) else float('nan')
        disp = dict(R.SETTINGS)[n]
        L.append(f'| {disp} | {ms(v["none"])} | {ms(v["group"])} | {ms(v["grouppair"])} | '
                 f'{np.mean(d):+.1f} | {p:.3g} | {sum(x > 0 for x in d)}/{sum(x < 0 for x in d)} |' if d else
                 f'| {disp} | {ms(v["none"])} | {ms(v["group"])} | {ms(v["grouppair"])} | – | – | – |')
    if len(allp) >= 2:
        L += [f'| **VPN All** | | | | {np.mean(allp):+.1f} | {wilcoxon(allp).pvalue:.3g} | '
              f'{sum(x > 0 for x in allp)}/{sum(x < 0 for x in allp)} |']

    # B/C) sensitivity
    L += ['', '## B/C. Hyperparameter sensitivity (RAFS, seeds 0–2, deployment test-set macro F1)', '',
          'k is the number of top-ranked fields used to form field pairs; w is the number of single-field candidates tested per round (the upstream window parameter).', '',
          '| Setting | ' + ' | '.join(d for _, d in CFGS) + ' |', '|---|' + '---:|' * len(CFGS)]
    means = {v: [] for v, _ in CFGS}
    fits = {v: [] for v, _ in CFGS}
    for n, disp in R.SETTINGS:
        cells = []
        for v, _ in CFGS:
            rs = [r for s in range(3) if (r := get(v, s, n))]
            cells.append(ms([r['cs'] for r in rs]))
            if len(rs) == 3:
                means[v].append(np.mean([r['cs'] for r in rs]))
                fits[v].append(np.mean([r['fits_to_best'] for r in rs]))
        L.append(f'| {disp} | ' + ' | '.join(cells) + ' |')
    L.append('| **Mean over settings with all 3 seeds completed** | ' + ' | '.join(
        f'{np.mean(means[v]):.1f} ({len(means[v])}/9)' if means[v] else '–' for v, _ in CFGS) + ' |')
    L.append('| **Mean retrainings to the selected round** | ' + ' | '.join(
        f'{np.mean(fits[v]):.0f}' if fits[v] else '–' for v, _ in CFGS) + ' |')
    L += ['', 'Reference means: baseline 48.6; field grouping 50.0 (see SEEDS.md).', '',
          '## Files', '', '- Run sensitivity experiments with `reproduce.py --pair-top` or `--window`; report: `analysis/sens_report.py`; tests: `analysis/stats_tests.py`.',
          '- This report reads archived results and exit-status files.', '']
    with open(os.path.join(HERE, 'SENS.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))
    subprocess.run([sys.executable, os.path.join(HERE, 'stats_tests.py')], capture_output=True)


if __name__ == '__main__':
    main()
