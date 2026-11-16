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
CFGS = [('grouppair_k3', 'k=3, w=5'), ('grouppair', 'k=4, w=5（默认）'), ('grouppair_k5', 'k=5, w=5'),
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
    L = ['# 第 3 步：敏感性分析 + VPN 补充种子', '',
         f'最后更新：{dt.datetime.now():%Y-%m-%d %H:%M}（运行期间每 10 分钟自动刷新；手动刷新：`python sens_report.py`）', '']
    if os.path.exists(os.path.join(HERE, 'SENS_ALL_DONE')):
        L += ['**全部实验已结束。**', '']
    # progress
    cnt = {'ok': 0, 'fail': 0, 'run': 0, 'wait': 0}
    jobs = [(v, s, n) for s in range(3, 10) for v in ('grouppair', 'group', 'none') for n in VPN] + \
           [(v, s, n) for s in range(3) for v, _ in CFGS if v != 'grouppair' for n, _ in R.SETTINGS]
    for j in jobs:
        cnt[state(*j)] += 1
    fails = [f'{v} 种子{s} {n}' for v, s, n in jobs if state(v, s, n) == 'fail']
    L += [f'进度：共 {len(jobs)} 组；完成 {cnt["ok"]}，运行中 {cnt["run"]}，等待 {cnt["wait"]}，失败 {cnt["fail"]}。', '']
    if fails:
        L += ['失败的运行：' + '；'.join(fails), '']

    # A) VPN 10 seeds
    L += ['## A. VPN：10 个 RF 种子（种子 0–2 来自之前的运行）', '',
          '| 设置 | 原版 | 字段分组 | 分组+联合搜索 | 联合搜索 − 原版（配对） | Wilcoxon p | 胜/负 |',
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
        L += [f'| **VPN 全部** | | | | {np.mean(allp):+.1f} | {wilcoxon(allp).pvalue:.3g} | '
              f'{sum(x > 0 for x in allp)}/{sum(x < 0 for x in allp)} |']

    # B/C) sensitivity
    L += ['', '## B/C. 超参数敏感性（分组+联合搜索，种子 0–2，check 集 macro-F1）', '',
          'k = 两两组合的候选字段数（前 k 个字段），w = 每轮测试的单字段数（ShortcutCatcher 原文的 window）。', '',
          '| 设置 | ' + ' | '.join(d for _, d in CFGS) + ' |', '|---|' + '---:|' * len(CFGS)]
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
    L.append('| **平均（3 个种子都完成的设置）** | ' + ' | '.join(
        f'{np.mean(means[v]):.1f} ({len(means[v])}/9)' if means[v] else '–' for v, _ in CFGS) + ' |')
    L.append('| **到最佳轮的重训次数（平均）** | ' + ' | '.join(
        f'{np.mean(fits[v]):.0f}' if fits[v] else '–' for v, _ in CFGS) + ' |')
    L += ['', '参照：原版平均 48.6，字段分组 50.0（见 `SEEDS.md`）。', '',
          '## 文件', '', '- 运行脚本：`run_sens.sh`；报告：`sens_report.py`；统计检验：`STATS.md`（`stats_tests.py`）',
          '- 全部结束后会出现 `SENS_ALL_DONE`', '']
    with open(os.path.join(HERE, 'SENS.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))
    subprocess.run([sys.executable, os.path.join(HERE, 'stats_tests.py')], capture_output=True)


if __name__ == '__main__':
    main()
