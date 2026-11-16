"""Compare the original ShortcutCatcher with our variants -> COMPARE.md

Per setting: F1*(C) chosen exactly like evaluate/table2.py (round with best verification F1),
number of model retrainings until that round, total retrainings, wall time.
Usage: python compare.py
"""
import csv
import datetime as dt
import os
import re

HERE = os.environ.get('RAFS_LOG_ROOT', os.path.dirname(os.path.abspath(__file__)))
REPO = os.environ.get('RAFS_RESULTS_ROOT', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'results')))
SUB = 'soft_window-0.0-5/dataset/RandomForestGini-removal-0.15-default'
SETTINGS = [('vpn-service', 'VPN'), ('app53-time', 'App-Time'), ('app53-version', 'App-Version')]
VARIANTS = [('none', '原版 ShortcutCatcher', 'logs'), ('group', '+ 协议字段分组', 'logs_group')]


def rows(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def fits_per_round(log):
    """Number of model.run() calls per completed round, from the log."""
    if not os.path.exists(log):
        return []
    txt = open(log, encoding='utf-8', errors='replace').read()
    out, n = [], 0
    for line in txt.splitlines():
        if line.startswith('[Training] Start training'):
            n += 1
        elif line.startswith('[Timing Summary]'):
            out.append(n); n = 0
    return out


def one(variant, logdir, name, rule=None):
    """rule: 'f1' = argmax verification macro-F1 (official table2.py); 'lcb' = argmax bootstrap LCB of
    macro-F1 (robust variants). Default: 'lcb' if the run logged it, else 'f1'."""
    res = 'results' if variant == 'none' else f'results_{variant}'
    sub = SUB.replace('/dataset/', '/dataset_rel/') if 'rel' in variant else SUB   # variants run on dataset_rel/
    d = os.path.join(REPO, res, 'per-flow', name, sub)
    if not os.path.isdir(d):        # non-default window: folder is soft_window-0.0-<w>
        import glob
        hits = glob.glob(os.path.join(REPO, res, 'per-flow', name, 'soft_window-0.0-*', *sub.split('/')[1:]))
        if hits:
            d = hits[0]
    try:
        f_d = rows(os.path.join(d, 'leaderboard-False-0.15.csv'))
        f_c = rows(os.path.join(d, 'leaderboard-True-invisible-0.15.csv'))
        f_v = rows(os.path.join(d, 'leaderboard-True-visible-0.15.csv'))
        times = rows(os.path.join(d, 'iteration_times.csv'))
    except FileNotFoundError:
        return None
    n = min(len(f_v), len(f_c))
    if n == 0:
        return None
    if rule is None:
        rule = 'lcb' if 'f1_lcb' in f_v[0] else 'f1'
    col = 'f1_lcb' if rule == 'lcb' else 'f1_macro'
    best = max(range(n), key=lambda i: float(f_v[i][col]))
    fits = fits_per_round(os.path.join(HERE, logdir, f'{name}.log'))[:n]
    secs = [sum(float(t[k]) for k in ('base_time', 'selection_time', 'explain_time', 'verification_time')) for t in times[:n]]
    done = os.path.exists(os.path.join(HERE, logdir, f'{name}.exit'))
    return {
        'd0': float(f_d[0]['f1_macro']) * 100, 'c0': float(f_c[0]['f1_macro']) * 100,
        'cs': float(f_c[best]['f1_macro']) * 100, 'best_round': best + 1, 'rounds': n,
        'fits_to_best': sum(fits[:best + 1]), 'fits_total': sum(fits), 'min_to_best': sum(secs[:best + 1]) / 60,
        'removed': f_v[best]['feature'].split('+')[1:], 'done': done,
    }


def main():
    L = ['# 模块替换对比：原版 vs 协议字段分组', '',
         f'最后更新：{dt.datetime.now():%Y-%m-%d %H:%M}。运行 `python compare.py` 刷新。', '',
         '指标说明：', '',
         '- F1*(C)：部署场景 check 集的 macro-F1，取验证集最好的那一轮，与官方 `evaluate/table2.py` 相同',
         '- 到最佳轮的重训次数：从开始到选出最佳轮，一共重新训练了多少次模型（越少越省算力）',
         '- 到最佳轮耗时：同一台机器上的时间（分钟），只适合同机比较', '',
         '| 设置 | 方法 | 状态 | F1⁰(C) | F1*(C) | 最佳轮 / 总轮数 | 到最佳轮的重训次数 | 总重训次数 | 到最佳轮耗时（分钟） |',
         '|---|---|---|---:|---:|---:|---:|---:|---:|']
    removed = []
    for prefix, disp in SETTINGS:
        for s in ('s0', 's1', 's2'):
            name = f'{prefix}-{s}'
            for var, vdisp, logdir in VARIANTS:
                r = one(var, logdir, name)
                if r is None:
                    L.append(f'| {disp} {s.upper()} | {vdisp} | 未开始 | | | | | | |')
                    continue
                st = '完成' if r['done'] else '运行中'
                L.append(f"| {disp} {s.upper()} | {vdisp} | {st} | {r['c0']:.1f} | {r['cs']:.1f} | "
                         f"{r['best_round']} / {r['rounds']} | {r['fits_to_best']} | {r['fits_total']} | {r['min_to_best']:.1f} |")
                removed.append((f'{disp} {s.upper()}', vdisp, r['removed']))
    L += ['', '## 最佳轮时被删除的特征', '']
    for n, v, rm in removed:
        L.append(f"- {n}，{v}（{len(rm)} 项）：{', '.join(rm) if rm else '无'}")
    with open(os.path.join(HERE, 'COMPARE.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
