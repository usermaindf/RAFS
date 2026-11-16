"""Run project-authored extensions against an externally provided baseline and data."""
from pathlib import Path
import argparse, hashlib, subprocess, sys
ROOT=Path(__file__).resolve().parent
SETTINGS=[f'{f}-{s}' for f in ('vpn-service','app53-time','app53-version') for s in ('s0','s1','s2')]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--verify',action='store_true');p.add_argument('--baseline-dir',type=Path);p.add_argument('--data-root',type=Path)
    p.add_argument('--datasets',nargs='+',choices=SETTINGS,default=SETTINGS)
    p.add_argument('--variants',nargs='+',choices=['none','group','grouppair','grouprob','groupshift','grouprel','grouppairrel'],default=['none','group','grouppair'])
    p.add_argument('--seeds',nargs='+',type=int,default=[0,1,2]);p.add_argument('--model',choices=['RandomForestGini','NeuralNetTorch'],default='RandomForestGini')
    p.add_argument('--rounds',type=int,default=100);p.add_argument('--window',type=int,default=5);p.add_argument('--pair-top',type=int,default=4)
    p.add_argument('--run-dir',type=Path,default=ROOT/'runs');p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    if a.verify:
        for line in (ROOT/'SHA256SUMS').read_text(encoding='utf8').splitlines():
            expected,name=line.split('  ',1)
            if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:raise ValueError(name)
        print('All release files verified; no third-party code or feature tables bundled.');return
    if not a.baseline_dir or not a.data_root:p.error('--baseline-dir and --data-root are required.')
    baseline=a.baseline_dir.resolve();data=a.data_root.resolve();work=a.run_dir.resolve()
    for name in ('loop.py','model.py','explain.py','noise.py'):
        if not (baseline/name).is_file():p.error(f'Missing external baseline file: {baseline/name}')
    if work==ROOT or work==ROOT/'results' or ROOT/'results' in work.parents:p.error('Choose a separate run directory.')
    for variant in a.variants:
        run_variant=variant
        if a.model=='NeuralNetTorch':run_variant+='_mlp'
        elif variant=='grouppair' and a.pair_top!=4:run_variant+=f'_k{a.pair_top}'
        elif variant=='grouppair' and a.window!=5:run_variant+=f'_w{a.window}'
        for seed in a.seeds:
            tag=run_variant if seed==0 else f'{run_variant}_seed{seed}'
            for setting in a.datasets:
                if 'rel' in variant and setting.startswith('vpn'):continue
                for split in ('train','val','test','visible','invisible'):
                    if not (data/'per-flow'/setting/(split+'_normalized.csv')).is_file():p.error(f'Missing data: {setting}/{split}')
                cmd=[sys.executable,str(ROOT/'src/rafs.py'),'--baseline-dir',str(baseline),'--data-root',str(data),
                    '--dataset',setting,'--variant',run_variant,'--seed',str(seed),'--model',a.model,'--rounds',str(a.rounds),
                    '--window',str(a.window),'--pair-top',str(a.pair_top)]
                if a.dry_run:print(subprocess.list2cmdline(cmd));continue
                logs=work/('logs' if tag=='none' else 'logs_'+tag);logs.mkdir(parents=True,exist_ok=True)
                log=logs/(setting+'.log');status=logs/(setting+'.exit')
                if log.exists() or status.exists():raise FileExistsError(log)
                with log.open('w',encoding='utf8') as out:r=subprocess.run(cmd,cwd=work,stdout=out,stderr=subprocess.STDOUT)
                status.write_text(str(r.returncode),encoding='utf8')
                if r.returncode:raise RuntimeError(f'Experiment failed: {log}')
                print('Completed',tag,setting,flush=True)
if __name__=='__main__':main()
