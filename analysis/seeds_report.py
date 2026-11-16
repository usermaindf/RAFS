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
RUNS = [('none', '原版'), ('group', '字段分组'), ('grouprob', '字段分组+稳健验证'), ('groupshift', '字段分组+偏移感知'), ('grouppair', '字段分组+联合搜索'), ('grouprel', '字段分组+相对值'), ('grouppairrel', '字段分组+联合搜索+相对值')]
# (key, display, run variant, final-selection rule)
METHODS = [('none', '原版', 'none', 'f1'), ('group', '字段分组', 'group', 'f1'),
           ('grouprob_f1', '分组+稳健验证（仅环内）', 'grouprob', 'f1'),
           ('grouprob', '分组+稳健验证', 'grouprob', 'lcb'),
           ('groupshift', '分组+偏移感知', 'groupshift', 'f1'),
           ('grouppair', '分组+联合搜索', 'grouppair', 'f1'),
           ('grouprel', '分组+相对值', 'grouprel', 'f1'),
           ('grouppairrel', '分组+联合搜索+相对值', 'grouppairrel', 'f1')]
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
        return ('完成' if c == '0' else f'失败(exit {c})'), None
    if os.path.exists(log):
        txt = open(log, encoding='utf-8', errors='replace').read()
        return ('运行中' + ('（日志有 Traceback）' if 'Traceback' in txt else '')), len(re.findall(r'\[Timing Summary\]', txt))
    return '等待', None


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
    L = ['# 多种子对比：原版 ShortcutCatcher 与两个改进', '',
         f'最后更新：{dt.datetime.now():%Y-%m-%d %H:%M}（运行期间每 10 分钟自动刷新；手动刷新：`python seeds_report.py`）', '']
    if os.path.exists(os.path.join(HERE, 'REL_ALL_DONE')):
        L += ['**全部实验已结束。**', '']
    L += ['设置：RandomForest，只改随机森林的 `random_state`（种子 0 = 论文设置，即 AutoGluon 的默认值）。'
          '其余参数与官方复现命令完全相同。', '',
          '- 原版、字段分组、"仅环内"：最终轮取验证集 macro-F1 最高的一轮，与官方 `evaluate/table2.py` 一致',
          '- 分组+稳健验证：最终轮取验证集 bootstrap macro-F1 下置信界（均值 − 1 个标准差）最高的一轮',
          '- "仅环内"是消融：和"分组+稳健验证"用同一批运行，只是最终轮换回原规则来选', '',
          '## 1. 运行状态', '',
          '| 设置 | ' + ' | '.join(f'{vd} 种子{s}' for v, vd in RUNS for s in SEEDS) + ' |',
          '|---|' + '---|' * (len(RUNS) * len(SEEDS))]
    n_done = n_all = 0
    for name, disp in SETTINGS:
        cells = []
        for var, _ in RUNS:
            for seed in SEEDS:
                rtag, logdir = dirs(var, seed)
                if 'rel' in var and name.startswith('vpn'):
                    cells.append('未运行（VPN 暂无相对值数据）'); continue      # relative features built for App-Time / App-Version only
                st, rounds = status(logdir, name)
                n_all += 1
                if st == '完成':
                    n_done += 1
                    for key, _, rv, rule in METHODS:
                        if rv == var:
                            r = compare.one(rtag, logdir, name, rule=rule)
                            if r:
                                res[(key, seed, name)] = r
                cells.append(st + (f'（第 {rounds} 轮）' if rounds is not None else ''))
        L.append(f'| {disp} | ' + ' | '.join(cells) + ' |')
    L += ['', f'已完成 {n_done} / {n_all} 组。', '']

    def vals(key, name, k='cs'):
        return [res[(key, s, name)][k] for s in SEEDS if (key, s, name) in res]

    L += ['## 2. check 集 macro-F1 F1*(C)：3 个种子的均值 ± 标准差', '',
          '| 设置 | ' + ' | '.join(d for _, d, _, _ in METHODS) + ' |', '|---|' + '---:|' * len(METHODS)]
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
    L += ['| **9 个设置平均** | ' + ' | '.join(avgs) + ' |',
          '| **仅 App 6 个设置平均**（括号内为 3 个种子都完成的设置数） | ' + ' | '.join(app) + ' |', '',
          '注意：相对值方法只在 App 上运行，它们的"9 个设置平均"实际只是 App 设置的平均，不能和其他方法直接比较；请看"仅 App"一行。', '']

    L += ['## 3. 与原版的配对差值（同设置、同种子）', '',
          '格式：差值均值 ± 标准差 / 胜场（比原版高的种子数 : 总数）', '',
          '| 设置 | ' + ' | '.join(d for k, d, _, _ in METHODS if k != 'none') + ' |',
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
    L.append('| **全部** | ' + ' | '.join('–' if not tot[k] else f'{fmt(tot[k])} / {sum(x > 0 for x in tot[k])}:{len(tot[k])}'
                                         for k, *_ in METHODS if k != 'none') + ' |')
    L += ['', '## 4. 稳定性：跨种子标准差 / 最差种子的 F1*(C)（标准差越小越稳，最差值越高越好）', '',
          '| 设置 | ' + ' | '.join(d for _, d, _, _ in METHODS) + ' |', '|---|' + '---:|' * len(METHODS)]
    for name, disp in SETTINGS:
        cells = []
        for k, *_ in METHODS:
            s = stats(vals(k, name))
            cells.append('–' if s is None else f'{s[1]:.1f} / {s[2]:.1f}')
        L.append(f'| {disp} | ' + ' | '.join(cells) + ' |')

    L += ['', '## 5. 效率：到最佳轮的重训次数（3 个种子均值）', '',
          '| 设置 | ' + ' | '.join(d for _, d, _, _ in METHODS) + ' |', '|---|' + '---:|' * len(METHODS)]
    for name, disp in SETTINGS:
        cells = []
        for k, *_ in METHODS:
            v = vals(k, name, 'fits_to_best')
            cells.append(f'{sum(v) / len(v):.0f}' if v else '–')
        L.append(f'| {disp} | ' + ' | '.join(cells) + ' |')

    L += ['', '## 6. 每个种子的明细（F1*(C)）', '',
          '| 设置 | ' + ' | '.join(f'{d} 种子{s}' for _, d, _, _ in METHODS for s in SEEDS) + ' |',
          '|---|' + '---:|' * (len(METHODS) * len(SEEDS))]
    for name, disp in SETTINGS:
        L.append(f'| {disp} | ' + ' | '.join(
            (f"{res[(k, s, name)]['cs']:.1f}" if (k, s, name) in res else '') for k, *_ in METHODS for s in SEEDS) + ' |')
    L += ['', '## 文件', '',
          '- 运行脚本：`run_seeds.sh`（原版、字段分组的种子 1、2）；`run_rob.sh`（分组+稳健验证，种子 0–2）；`run_shift.sh`（分组+偏移感知，种子 0–2）；`run_pair.sh`（分组+联合搜索，种子 0–2）；`run_rel.sh`（相对值缓解，仅 App-Time / App-Version，种子 0–2）',
          '- 报告脚本：`seeds_report.py`（复用 `compare.py` 的指标计算）',
          '- 日志：`logs_<方法>[_seed<k>]/`；结果 CSV：`ShortcutCatcher-main/results_<方法>[_seed<k>]/`',
          '- 相对值实验全部结束后会出现 `REL_ALL_DONE` 文件', '']
    with open(os.path.join(HERE, 'SEEDS.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))


if __name__ == '__main__':
    main()
