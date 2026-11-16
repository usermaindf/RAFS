"""Build dataset_rel/: the released ShortcutCatcher CSVs (unchanged, byte-identical feature columns) plus
relative (within-flow) versions of the fields whose absolute value is an environment / flow identifier:

  tcp_seq_rel_pktI            seq   - first seq seen in the same direction (bytes sent so far)
  tcp_ack_rel_pktI            ack   - first seq of the opposite direction (bytes acknowledged), 0 if no ACK
  tcp_timestamp_rel_pktI      TSval - first TSval of the same direction (sender clock ticks elapsed)
  tcp_echo_timestamp_rel_pktI TSecr - first TSval of the opposite direction (echoed peer ticks), 0 if TSecr = 0
  ip_id_rel_pktI              IP ID - first IP ID of the same direction (packets sent by that host)
Values are computed exactly from the raw pcaps (32-bit / 16-bit wrap-around, signed), i.e. without the
1e-6 rounding of the release. Rows are mapped to pcaps by match_rows.py.

Usage: python -I build_rel.py <netd.pkl> <match.pkl> <src prefix .../dataset/per-flow/app53-time> <dst prefix .../dataset_rel/per-flow/app53-time>
"""
import os
import pickle
import shutil
import sys

import numpy as np
import pandas as pd

N = 5
REL_FIELDS = ['tcp_seq', 'tcp_ack', 'tcp_timestamp', 'tcp_echo_timestamp', 'ip_id']


def wrap(x, bits):
    m = 1 << bits
    x %= m
    return x - m if x >= m // 2 else x


def rel_features(flow):
    out = {f'{f}_rel_pkt{i}': 0 for f in REL_FIELDS for i in range(N)}
    pk = flow['pkts']
    if not pk:
        return out
    first_src = pk[0]['src']
    seq0, ts0, id0 = [None, None], [None, None], [None, None]
    for i, p in enumerate(pk[:N]):
        d = 0 if p['src'] == first_src else 1
        if id0[d] is None:
            id0[d] = p['ip_id']
        out[f'ip_id_rel_pkt{i}'] = wrap(p['ip_id'] - id0[d], 16)
        if p['proto'] != 6:
            continue
        if seq0[d] is None:
            seq0[d] = p['seq']
        out[f'tcp_seq_rel_pkt{i}'] = wrap(p['seq'] - seq0[d], 32)
        if p['flags'] & 0x10:                       # ACK flag
            if seq0[1 - d] is None:                 # peer not seen yet: use this ack as its base
                seq0[1 - d] = p['ack']
            out[f'tcp_ack_rel_pkt{i}'] = wrap(p['ack'] - seq0[1 - d], 32)
        if p['tsval'] is not None:
            if ts0[d] is None:
                ts0[d] = p['tsval']
            out[f'tcp_timestamp_rel_pkt{i}'] = wrap(p['tsval'] - ts0[d], 32)
            if p['tsecr']:
                if ts0[1 - d] is None:
                    ts0[1 - d] = p['tsecr']
                out[f'tcp_echo_timestamp_rel_pkt{i}'] = wrap(p['tsecr'] - ts0[1 - d], 32)
    return out


def main():
    netd, match, src, dst = sys.argv[1:5]
    flows = pickle.load(open(netd, 'rb'))
    M = pickle.load(open(match, 'rb'))
    cache = {}
    for (sc, split), idx in sorted(M.items()):
        if (idx < 0).any():
            raise SystemExit(f'unmatched rows in {sc}/{split}')
        df = pd.read_csv(f'{src}-{sc}/{split}_normalized.csv')
        rows = []
        for g in idx:
            if g not in cache:
                cache[g] = rel_features(flows[g])
            rows.append(cache[g])
        rel = pd.DataFrame(rows, index=df.index)
        cls = df.pop('class')
        out = pd.concat([df, rel], axis=1)
        out['class'] = cls
        os.makedirs(f'{dst}-{sc}', exist_ok=True)
        out.to_csv(f'{dst}-{sc}/{split}_normalized.csv', index=False)
        nz = (rel != 0).mean()
        print(f'{sc} {split:9s} rows {len(out):6d} | non-zero share: ' +
              ' '.join(f'{f}={nz[[f"{f}_rel_pkt{i}" for i in range(N)]].mean():.2f}' for f in REL_FIELDS))


if __name__ == '__main__':
    main()
