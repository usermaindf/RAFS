"""Extract raw header values of the first 5 packets of every NETD flow pcap (App-Time / App-Version).

Output (pickle): list of dicts with
  file, split (train/test), label, t0 (first packet time)
  per packet i<5: src (bytes), proto, seq, ack, flags, ip_id, ip_len, win, ttl, tsval, tsecr (None if absent)
Only standard headers are read; payload is ignored.

Usage: python -I extract_netd.py <NETD/App-Time> <out.pkl>
"""
import os
import pickle
import sys
from multiprocessing import Pool

import dpkt

N = 5


def tcp_ts(opts):
    try:
        for k, d in dpkt.tcp.parse_opts(opts):
            if k == 8 and len(d) == 8:
                return int.from_bytes(d[:4], 'big'), int.from_bytes(d[4:], 'big')
    except Exception:
        pass
    return None, None


def one(args):
    path, split, label = args
    pk = []
    with open(path, 'rb') as fh:
        magic = fh.read(4); fh.seek(0)
        r = dpkt.pcapng.Reader(fh) if magic == b'\x0a\x0d\x0d\x0a' else dpkt.pcap.Reader(fh)
        dl = r.datalink()
        t0 = None
        for ts, buf in r:
            try:
                if dl == 1:
                    l3 = dpkt.ethernet.Ethernet(buf).data
                elif dl == 113:
                    l3 = dpkt.sll.SLL(buf).data
                else:
                    l3 = dpkt.ip.IP(buf) if buf[0] >> 4 == 4 else dpkt.ip6.IP6(buf)
            except Exception:
                continue
            if not isinstance(l3, dpkt.ip.IP):
                continue
            l4 = l3.data
            if t0 is None:
                t0 = float(ts)
            p = dict(src=bytes(l3.src), proto=l3.p, ip_id=l3.id, ip_len=l3.len, ttl=l3.ttl,
                     seq=0, ack=0, flags=0, win=0, tsval=None, tsecr=None)
            if isinstance(l4, dpkt.tcp.TCP):
                p.update(seq=l4.seq, ack=l4.ack, flags=l4.flags, win=l4.win)
                p['tsval'], p['tsecr'] = tcp_ts(l4.opts)
            pk.append(p)
            if len(pk) >= N:
                break
    return dict(file=os.path.basename(path), split=split, label=label, t0=t0, pkts=pk)


def main():
    root, out = sys.argv[1], sys.argv[2]
    jobs = []
    for split in ('train', 'test'):
        for label in sorted(os.listdir(os.path.join(root, split))):
            d = os.path.join(root, split, label)
            jobs += [(os.path.join(d, f), split, label) for f in sorted(os.listdir(d))]
    with Pool(16) as pool:
        flows = pool.map(one, jobs, chunksize=64)
    pickle.dump(flows, open(out, 'wb'))
    print('flows', len(flows), 'empty', sum(1 for f in flows if not f['pkts']))


if __name__ == '__main__':
    main()
