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
        return ('完成' if c == '0' else f'失败(exit {c})'), compare.one(tag, ld, d, rule='f1') if c == '0' else None
    if os.path.exists(log):
        txt = open(log, encoding='utf-8', errors='replace').read()
        n = len(re.findall(r'\[Timing Summary\]', txt))
        return f'运行中（第 {n} 轮）' + ('，日志有 Traceback' if 'Traceback' in txt else ''), (compare.one(tag, ld, d, rule='f1') if n else None)
    return '等待', None


def main():
    L = ['# 第 4 步：换成 MLP 分类器（场景 S2，对应 ShortcutCatcher 表 4）', '',
         f'最后更新：{dt.datetime.now():%Y-%m-%d %H:%M}（运行中每 10 分钟自动刷新；手动：`python mlp_report.py`）', '']
    if os.path.exists(os.path.join(HERE, 'MLP_ALL_DONE')):
        L += ['**全部实验已结束。**', '']
    L += ['设置：AutoGluon NeuralNetTorch 默认超参数，置换重要性，窗口 5（与原论文表 4 相同）。',
          '- VPN S2：与原论文完全相同（100 轮），MLP 种子 0、1、2，CPU。',
          '- App-Time / App-Version S2：MLP 单次训练约 200 秒，原版完整跑一次约需 28 小时，因此改为**等计算量对比**：'
          '原版限 34 轮（约 200 次重训），本文方法跑完为止（约 200 次重训）。只用种子 0，GPU。', '',
          '| 运行 | 状态 | F1⁰(C) | F1*(C) | 最佳轮 / 已跑轮数 | 到最佳轮的重训次数 | 总重训次数 |', '|---|---|---:|---:|---:|---:|---:|']
    res = {}
    for v, s, d in JOBS:
        st, r = status(v, s, d)
        name = f"{DISP[d]} · {'原版' if v.startswith('none') else '分组+联合搜索'} · 种子{s}"
        if r:
            res[(v, s, d)] = (r, st == '完成')
            L.append(f"| {name} | {st} | {r['c0']:.1f} | {r['cs']:.1f} | {r['best_round']} / {r['rounds']} | "
                     f"{r['fits_to_best']} | {r['fits_total']} |")
        else:
            L.append(f'| {name} | {st} | | | | | |')
    L += ['', '## 汇总（只统计已完成的运行）', '',
          '| 设置 | 原论文表 4（F1⁰(C) → F1*(C)） | 复现原版 F1*(C) | 分组+联合搜索 F1*(C) | 差值 |', '|---|---|---:|---:|---:|']
    for d in DISP:
        o = [res[k][0]['cs'] for k in res if k[0] == 'none_mlp' and k[2] == d and res[k][1]]
        g = [res[k][0]['cs'] for k in res if k[0] == 'grouppair_mlp' and k[2] == d and res[k][1]]
        pair = [res[('grouppair_mlp', s, d)][0]['cs'] - res[('none_mlp', s, d)][0]['cs'] for s in range(3)
                if ('grouppair_mlp', s, d) in res and ('none_mlp', s, d) in res
                and res[('grouppair_mlp', s, d)][1] and res[('none_mlp', s, d)][1]]
        f = lambda v: '–' if not v else (f'{np.mean(v):.1f} ± {np.std(v, ddof=1):.1f} (n={len(v)})' if len(v) > 1 else f'{v[0]:.1f}')
        L.append(f'| {DISP[d]} | {PAPER[d][0]} → {PAPER[d][1]} | {f(o)} | {f(g)} | {f(pair)} |')
    L += ['', 'App 两行是等计算量对比（原版限 34 轮），和原论文表 4（原版跑满 100 轮）不能直接比较；VPN 一行与原论文设置相同。',
          '', '运行脚本：`run_mlp.sh`；全部结束后出现 `MLP_ALL_DONE`。', '']
    with open(os.path.join(HERE, 'MLP.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L))


if __name__ == '__main__':
    main()
