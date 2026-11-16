"""Match every row of the released ShortcutCatcher CSVs to its source NETD flow pcap.

The released features are min-max normalised (fitted on the train split) and rounded to 1e-6, so they cannot
be inverted directly. Fields that forge() does not touch (TCP seq/ack, IP ID, IP length) identify a flow
uniquely. For each key column we fit the affine map raw -> normalised (start: pool min/max; then least
squares on matched pairs) and match rows by nearest neighbour in that space.
Pools: train/val/test rows <- NETD train pcaps; visible/invisible rows <- NETD test pcaps.

Usage: python -I match_rows.py <netd.pkl> <csv dir prefix, e.g. .../per-flow/app53-time> <out.pkl>
Output: {(scenario, split): array of flow indices (into netd.pkl), aligned with CSV rows}
"""
import pickle
import sys

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

KEYS = [f'{f}_pkt{i}' for f in ('tcp_seq', 'tcp_ack', 'ip_id', 'ip_len') for i in range(5)]
RAWNAME = {'tcp_seq': 'seq', 'tcp_ack': 'ack', 'ip_id': 'ip_id', 'ip_len': 'ip_len'}
TOL = 5e-6


def raw_matrix(flows):
    R = np.zeros((len(flows), len(KEYS)))
    for n, f in enumerate(flows):
        for j, k in enumerate(KEYS):
            fld, i = k.rsplit('_pkt', 1)
            i = int(i)
            if i < len(f['pkts']):
                R[n, j] = f['pkts'][i][RAWNAME[fld]]
    return R


def fit_affine(raw, norm):
    A = np.vstack([raw, np.ones_like(raw)]).T
    return np.linalg.lstsq(A, norm, rcond=None)[0]


def match(R, C, ab):
    P = R * ab[:, 0] + ab[:, 1]
    tree = cKDTree(P)
    d, idx = tree.query(C, k=1, p=np.inf)
    return d, idx


def main():
    pkl, prefix, out = sys.argv[1:4]
    flows = pickle.load(open(pkl, 'rb'))
    split_of = np.array([f['split'] for f in flows])
    R_all = raw_matrix(flows)
    result, report = {}, []
    prev_ab = None
    for sc in ('s1', 's2', 's0'):   # s1 first; its fitted map is a good start for the others
        d = f'{prefix}-{sc}'
        train = pd.read_csv(f'{d}/train_normalized.csv', usecols=KEYS)
        # initial affine map from the train split: norm = (raw - min) / (max - min) over the pool
        pool_tr = np.where(split_of == 'train')[0]
        mn, mx = R_all[pool_tr].min(0), R_all[pool_tr].max(0)
        ab = np.stack([1 / np.maximum(mx - mn, 1), -mn / np.maximum(mx - mn, 1)], 1)
        if prev_ab is not None:
            dist0, _ = match(R_all[pool_tr], train[KEYS].values, ab)
            dist1, _ = match(R_all[pool_tr], train[KEYS].values, prev_ab)
            if (dist1 < 1e-4).mean() > (dist0 < 1e-4).mean():
                ab = prev_ab.copy()
        # stage 1: match on high-entropy seq/ack/IP ID columns only (their train min/max barely change
        # between scenarios); IP length columns can have a very different train max (e.g. ip_len_pkt4).
        sub = [j for j, k in enumerate(KEYS) if not k.startswith('ip_len')]
        for it in range(3):     # refine the affine map on the train split
            P = R_all[pool_tr][:, sub] * ab[sub, 0] + ab[sub, 1]
            dist, idx = cKDTree(P).query(train[KEYS].values[:, sub], k=1, p=np.inf)
            ok = dist < 1e-4
            ab = np.stack([fit_affine(R_all[pool_tr][idx[ok], j], train[KEYS].values[ok, j]) for j in range(len(KEYS))])
        prev_ab = ab
        for split, pool_name in [('train', 'train'), ('val', 'train'), ('test', 'train'),
                                 ('visible', 'test'), ('invisible', 'test')]:
            C = pd.read_csv(f'{d}/{split}_normalized.csv', usecols=KEYS)[KEYS].values
            pool = np.where(split_of == pool_name)[0]
            P = R_all[pool][:, sub] * ab[sub, 0] + ab[sub, 1]
            dist, idx = cKDTree(P).query(C[:, sub], k=1, p=np.inf)
            gidx = pool[idx]
            ok = dist <= TOL
            # duplicates: several CSV rows mapped to one pcap; count those whose CSV rows differ (real errors)
            Cdf = pd.DataFrame(C)
            first = {}
            real_dup = 0
            for r, g in enumerate(gidx):
                if g in first and not np.allclose(C[first[g]], C[r]):
                    real_dup += 1
                first.setdefault(g, r)
            report.append(f'{sc} {split:9s} rows {len(C):6d} matched {ok.mean():.4f} max dist {dist.max():.2e} '
                          f'rows sharing a pcap {len(gidx) - len(np.unique(gidx))} (with different CSV values: {real_dup})')
            result[(sc, split)] = np.where(ok, gidx, -1)
    pickle.dump(result, open(out, 'wb'))
    print('\n'.join(report))


if __name__ == '__main__':
    main()
