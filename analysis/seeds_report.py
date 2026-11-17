"""Progress + results for the multi-seed comparison -> SEEDS.md

Methods (RF seeds 0/1/2):
  none      original ShortcutCatcher
  group     + protocol-field grouping (improvement 1)
  grouprob  + grouping + uncertainty-aware verification (improvement 2)
  grouprob_f1 is an ablation computed from the grouprob runs: robust in-loop choice, but the final
            round picked by the official rule (argmax verification macro-F1).
Seed 0: results/ + logs/ (none), results_<v>/ + logs_<v>/ (others). Seed k>0: results_<v>_seed<k>/ + logs_<v>_seed<k>/.
Usage: python seeds_report.py
"""
import datetime as dt
import math
import os
import re

import compare  # same metric code as COMPARE.md / evaluate/table2.py

HERE = os.environ.get('RAFS_LOG_ROOT', os.path.dirname(os.path.abspath(__file__)))
SEEDS = [0, 1, 2]
RUNS = [('none', 'Baseline'), ('group', 'Field grouping'), ('grouprob', 'Grouping + robust verification'), ('groupshift', 'Grouping + shift-aware ranking'), ('grouppair', 'RAFS'), ('grouprel', 'Grouping + relative features'), ('grouppairrel', 'RAFS + relative features')]
# (key, display, run variant, final-selection rule)
METHODS = [('none', 'Baseline', 'none', 'f1'), ('group', 'Field grouping', 'group', 'f1'),
           ('grouprob_f1', 'Grouping + robust verification (in-loop only)', 'grouprob', 'f1'),
           ('grouprob', 'Grouping + robust verification', 'grouprob', 'lcb'),
           ('groupshift', 'Grouping + shift-aware ranking', 'groupshift', 'f1'),
           ('grouppair', 'RAFS', 'grouppair', 'f1'),
           ('grouprel', 'Grouping + relative features', 'grouprel', 'f1'),
           ('grouppairrel', 'RAFS + relative features', 'grouppairrel', 'f1')]
SETTINGS = [(f'{p}-{s}', f'{d} {s.upper()}') for p, d in compare.SETTINGS for s in ('s0', 's1', 's2')]


def dirs(var, seed):
    if seed == 0:
        return var, ('logs' if var == 'none' else f'logs_{var}')
    return f'{var}_seed{seed}', f'logs_{var}_seed{seed}'


def status(logdir, name):
    log = os.path.join(HERE, logdir, f'{name}.log')
    ex = os.path.join(HERE, logdir, f'{name}.exit')
    if os.path.exists(ex):
        c = open(ex).read().strip()
        return ('Completed' if c == '0' else f'Failed(exit {c})'), None
    if os.path.exists(log):
        txt = open(log, encoding='utf-8', errors='replace').read()
        return ('Running' + (' (log contains  Traceback)' if 'Traceback' in txt else '')), len(re.findall(r'\[Timing Summary\]', txt))
    return 'Pending', None


def stats(v):
    if not v:
        return None
    m = sum(v) / len(v)
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1)) if len(v) > 1 else 0.0
    return m, sd, min(v), len(v)


def fmt(v):
    s = stats(v)
    return '–' if s is None else (f'{s[0]:.1f} ± {s[1]:.1f}' if s[3] > 1 else f'{s[0]:.1f}')


def main():
    res = {}   # (method key, seed, name) -> metrics
    L = ['# Multi-seed comparison: ShortcutCatcher and RAFS variants', '',
         f'Last updated: {dt.datetime.now():%Y-%m-%d %H:%M} (Regenerate manually with: `python seeds_report.py`)', '']
    if os.path.exists(os.path.join(HERE, 'REL_ALL_DONE')):
        L += ['**All experiments completed. **', '']
    L += ['Setting: RandomForest; vary only `random_state`. Seed 0 matches the AutoGluon default used in the baseline experiments. '
          'All other settings follow the original reproduction commands.', '',
          '- Baseline, field grouping and the in-loop-only ablation select the round with the highest validation macro F1-score, following upstream `evaluate/table2.py`.',
          '- Grouping + robust verification selects the round with the highest bootstrap lower confidence bound of validation macro F1-score (mean minus one standard deviation).',
          '- The in-loop-only ablation reuses the robust-verification runs but restores the original final-round selection rule.', '',
          '## 1. Run status', '',
          '| Setting | ' + ' | '.join(f'{vd} seed {s}' for v, vd in RUNS for s in SEEDS) + ' |',
          '|---|' + '---|' * (len(RUNS) * len(SEEDS))]
    n_done = n_all = 0
    for name, disp in SETTINGS:
        cells = []
        for var, _ in RUNS:
            for seed in SEEDS:
                rtag, logdir = dirs(var, seed)
                if 'rel' in var and name.startswith('vpn'):
                    cells.append('Not run (relative features unavailable for VPN)'); continue      # relative features built for App-Time / App-Version only
                st, rounds = status(logdir, name)
                n_all += 1
                if st == 'Completed':
                    n_done += 1
                    for key, _, rv, rule in METHODS:
                        if rv == var:
                            r = compare.one(rtag, logdir, name, rule=rule)
                            if r:
                                res[(key, seed, name)] = r
                cells.append(st + (f' (Round {rounds}  rounds)' if rounds is not None else ''))
        L.append(f'| {disp} | ' + ' | '.join(cells) + ' |')
    L += ['', f'Completed {n_done} / {n_all} runs. ', '']

    def vals(key, name, k='cs'):
        return [res[(key, s, name)][k] for s in SEEDS if (key, s, name) in res]

    L += ['## 2. test set macro-F1 F1*(C): mean ± SD over 3 seeds', '',
          '| Setting | ' + ' | '.join(d for _, d, _, _ in METHODS) + ' |', '|---|' + '---:|' * len(METHODS)]
    for name, disp in SETTINGS:
        L.append(f'| {disp} | ' + ' | '.join(fmt(vals(k, name)) for k, _, _, _ in METHODS) + ' |')
    avgs = []
    for k, *_ in METHODS:
        m = [stats(vals(k, n))[0] for n, _ in SETTINGS if vals(k, n)]
        avgs.append(f'{sum(m) / len(m):.1f}' if m else '–')
    app = []
    for k, *_ in METHODS:
        m = [stats(vals(k, n))[0] for n, _ in SETTINGS if n.startswith('app53') and len(vals(k, n)) == 3]
        app.append(f'{sum(m) / len(m):.1f} ({len(m)}/6)' if m else '–')
    L += ['| **Mean over 9 settings** | ' + ' | '.join(avgs) + ' |',
          '| **Mean over 6 App settings** (parentheses show settings with all 3 seeds completed) | ' + ' | '.join(app) + ' |', '',
          'Relative-feature variants run only on App data. Their overall mean covers only App settings; use the App-only row for a comparable evaluation.', '']

    L += ['## 3. Paired differences from the baseline (same setting and seed)', '',
          'Format: mean difference ± SD / wins (seeds outperforming the baseline : total seeds)', '',
          '| Setting | ' + ' | '.join(d for k, d, _, _ in METHODS if k != 'none') + ' |',
          '|---|' + '---:|' * (len(METHODS) - 1)]
    tot = {k: [] for k, *_ in METHODS}
    for name, disp in SETTINGS:
        cells = []
        for k, *_ in METHODS:
            if k == 'none':
                continue
            d = [res[(k, s, name)]['cs'] - res[('none', s, name)]['cs'] for s in SEEDS
                 if (k, s, name) in res and ('none', s, name) in res]
            tot[k] += d
            cells.append('–' if not d else f'{fmt(d)} / {sum(x > 0 for x in d)}:{len(d)}')
        L.append(f'| {disp} | ' + ' | '.join(cells) + ' |')
    L.append('| **All** | ' + ' | '.join('–' if not tot[k] else f'{fmt(tot[k])} / {sum(x > 0 for x in tot[k])}:{len(tot[k])}'
                                         for k, *_ in METHODS if k != 'none') + ' |')
    L += ['', '## 4. Stability: cross-seed SD / worst-seed F1*(C); lower SD and higher worst-seed performance are better', '',
          '| Setting | ' + ' | '.join(d for _, d, _, _ in METHODS) + ' |', '|---|' + '---:|' * len(METHODS)]
    for name, disp in SETTINGS:
        cells = []
        for k, *_ in METHODS:
            s = stats(vals(k, name))
            cells.append('–' if s is None else f'{s[1]:.1f} / {s[2]:.1f}')
        L.append(f'| {disp} | ' + ' | '.join(cells) + ' |')

    L += ['', '## 5. Efficiency: retrainings to the selected round (mean over 3 seeds)', '',
          '| Setting | ' + ' | '.join(d for _, d, _, _ in METHODS) + ' |', '|---|' + '---:|' * len(METHODS)]
    for name, disp in SETTINGS:
        cells = []
        for k, *_ in METHODS:
            v = vals(k, name, 'fits_to_best')
            cells.append(f'{sum(v) / len(v):.0f}' if v else '–')
        L.append(f'| {disp} | ' + ' | '.join(cells) + ' |')

    L += ['', '## 6. Per-seed F1*(C)', '',
          '| Setting | ' + ' | '.join(f'{d} seed {s}' for _, d, _, _ in METHODS for s in SEEDS) + ' |',
          '|---|' + '---:|' * (len(METHODS) * len(SEEDS))]
    for name, disp in SETTINGS:
        L.append(f'| {disp} | ' + ' | '.join(
            (f"{res[(k, s, name)]['cs']:.1f}" if (k, s, name) in res else '') for k, *_ in METHODS for s in SEEDS) + ' |')
    L += ['', '## Files', '',
          '- Run experiments with `python reproduce.py`; see README.md for variants and seed selections.',
          '- Report generator: `analysis/seeds_report.py`; metrics are computed by `analysis/compare.py`.',
          '- Archived count logs: `analysis/logs_<variant>[_seed<k>]/`; result CSVs: `results/results_<variant>[_seed<k>]/`.',
          '- Relative-feature experiments are available only for App-Time and App-Version.', '']
    with open(os.path.join(HERE, 'SEEDS.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))


if __name__ == '__main__':
    main()
