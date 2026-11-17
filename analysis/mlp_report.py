"""Progress + results for step 4 (MLP, scenario S2) -> MLP.md
Usage: python mlp_report.py
"""
import datetime as dt
import os
import re

import numpy as np
from scipy.stats import wilcoxon

import compare

compare.SUB = 'soft_window-0.0-5/dataset/NeuralNetTorch-removal-0.15-permutation'
HERE = os.environ.get('RAFS_LOG_ROOT', os.path.dirname(os.path.abspath(__file__)))
JOBS = ([(v, s, 'vpn-service-s2') for v in ('none_mlp', 'grouppair_mlp') for s in range(3)] +
        [(v, 0, d) for v in ('none_mlp', 'grouppair_mlp') for d in ('app53-time-s2', 'app53-version-s2')])
DISP = {'vpn-service-s2': 'VPN S2', 'app53-time-s2': 'App-Time S2', 'app53-version-s2': 'App-Version S2'}
PAPER = {'vpn-service-s2': (21.2, 21.1), 'app53-time-s2': (8.3, 22.1), 'app53-version-s2': (12.5, 25.0)}  # Table 4: F1^0(C), F1*(C)


def dirs(v, s):
    tag = v if s == 0 else f'{v}_seed{s}'
    return tag, f'logs_{tag}'


def status(v, s, d):
    tag, ld = dirs(v, s)
    ex, log = os.path.join(HERE, ld, f'{d}.exit'), os.path.join(HERE, ld, f'{d}.log')
    if os.path.exists(ex):
        c = open(ex).read().strip()
        return ('Completed' if c == '0' else f'Failed(exit {c})'), compare.one(tag, ld, d, rule='f1') if c == '0' else None
    if os.path.exists(log):
        txt = open(log, encoding='utf-8', errors='replace').read()
        n = len(re.findall(r'\[Timing Summary\]', txt))
        return f'Running (Round {n}  rounds)' + (', log contains  Traceback' if 'Traceback' in txt else ''), (compare.one(tag, ld, d, rule='f1') if n else None)
    return 'Pending', None


def main():
    L = ['# MLP evaluation in S2 (comparison with ShortcutCatcher Table 4)', '',
         f'Last updated: {dt.datetime.now():%Y-%m-%d %H:%M} (Regenerate manually with: `python mlp_report.py`)', '']
    if os.path.exists(os.path.join(HERE, 'MLP_ALL_DONE')):
        L += ['**All experiments completed. **', '']
    L += ['Configuration: AutoGluon NeuralNetTorch defaults, permutation importance, window 5, following upstream Table 4.',
          '- VPN S2: 100 rounds, MLP seeds 0, 1 and 2, on CPU.',
          '- App-Time / App-Version S2: recorded training took about 200 seconds per fit; a full baseline search would take about 28 hours. The report uses a **matched-compute comparison**: '
          'the baseline is capped at 34 rounds (about 200 retrainings), while RAFS runs to completion (about 200 retrainings). This report lists App seed 0 on GPU.', '',
          '| Run | Status | F1⁰(C) | F1*(C) | Best / completed rounds | Retrainings to best round | Total retrainings |', '|---|---|---:|---:|---:|---:|---:|']
    res = {}
    for v, s, d in JOBS:
        st, r = status(v, s, d)
        name = f"{DISP[d]} · {'Baseline' if v.startswith('none') else 'RAFS'} · seed {s}"
        if r:
            res[(v, s, d)] = (r, st == 'Completed')
            L.append(f"| {name} | {st} | {r['c0']:.1f} | {r['cs']:.1f} | {r['best_round']} / {r['rounds']} | "
                     f"{r['fits_to_best']} | {r['fits_total']} |")
        else:
            L.append(f'| {name} | {st} | | | | | |')
    L += ['', '## Summary of completed runs', '',
          '| Setting | Upstream Table 4 (F1⁰(C) → F1*(C)) | Reproduced Baseline F1*(C) | RAFS F1*(C) | Difference |', '|---|---|---:|---:|---:|']
    for d in DISP:
        o = [res[k][0]['cs'] for k in res if k[0] == 'none_mlp' and k[2] == d and res[k][1]]
        g = [res[k][0]['cs'] for k in res if k[0] == 'grouppair_mlp' and k[2] == d and res[k][1]]
        pair = [res[('grouppair_mlp', s, d)][0]['cs'] - res[('none_mlp', s, d)][0]['cs'] for s in range(3)
                if ('grouppair_mlp', s, d) in res and ('none_mlp', s, d) in res
                and res[('grouppair_mlp', s, d)][1] and res[('none_mlp', s, d)][1]]
        f = lambda v: '–' if not v else (f'{np.mean(v):.1f} ± {np.std(v, ddof=1):.1f} (n={len(v)})' if len(v) > 1 else f'{v[0]:.1f}')
        L.append(f'| {DISP[d]} | {PAPER[d][0]} → {PAPER[d][1]} | {f(o)} | {f(g)} | {f(pair)} |')
    L += ['', 'The two App rows use matched compute with the baseline capped at 34 rounds, so they are not directly comparable with the 100-round baseline in upstream Table 4. The VPN row follows the upstream configuration.',
          '', 'Run MLP experiments with `reproduce.py --model NeuralNetTorch`; see README.md for round limits.', '']
    with open(os.path.join(HERE, 'MLP.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L))


if __name__ == '__main__':
    main()
