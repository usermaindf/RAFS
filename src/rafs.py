"""Project-authored integration entry; the baseline implementation is external."""
from pathlib import Path
import argparse, sys, types
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline-dir',type=Path,required=True);p.add_argument('--data-root',type=Path,required=True)
    p.add_argument('--dataset',required=True);p.add_argument('--variant',default='grouppair');p.add_argument('--seed',type=int,default=0)
    p.add_argument('--model',default='RandomForestGini');p.add_argument('--rounds',type=int,default=100)
    p.add_argument('--window',type=int,default=5);p.add_argument('--pair-top',type=int,default=4);a=p.parse_args()
    sys.path.append(str(a.baseline_dir.resolve()))
    import pandas as pd
    from loop import Loop
    path=a.data_root.resolve()/'per-flow'/a.dataset
    importance='permutation' if a.model=='NeuralNetTorch' else 'default'
    loop=Loop(model_name=a.model,noise_type='removal',standard=.15,importance_type=importance,min_bound=0.)
    visible=pd.read_csv(path/'visible_normalized.csv')
    if 'rob' in a.variant:
        from robust import RobustModel
        loop.model=RobustModel(a.model,n_boot=200,lam=1.)
    if a.seed:
        for cfg in loop.model.hyperparameters.get('RF',[]):cfg['random_state']=a.seed
        if 'NN_TORCH' in loop.model.hyperparameters:loop.model.hyperparameters['NN_TORCH']['seed_value']=a.seed
    if a.variant.startswith('group'):
        from grouping import GroupExplain,GroupNoise,build_groups
        groups=build_groups(pd.read_csv(path/'train_normalized.csv',nrows=1).columns)
        loop.explainer=GroupExplain(importance,agg='sum');loop.noise=GroupNoise(groups,'removal',.15)
        if 'rel' in a.variant:
            from grouping import RelGroupNoise
            loop.noise=RelGroupNoise(groups,'removal',.15)
        if 'shift' in a.variant:
            from shift import ShiftExplain
            loop.explainer=ShiftExplain(groups,visible,n_repeats=3)
    loop.set_data(train_path=str(path/'train_normalized.csv'),val_path=str(path/'val_normalized.csv'),test_path=str(path/'test_normalized.csv'))
    if 'pair' in a.variant:
        from pairs import iterate_window_pairs
        loop.iterate_window=types.MethodType(lambda self,*args,**kwargs:iterate_window_pairs(self,*args,pair_top=a.pair_top,**kwargs),loop)
    tag=a.variant if a.seed==0 else f'{a.variant}_seed{a.seed}'
    base='results' if tag=='none' else 'results_'+tag
    kind='dataset_rel' if 'rel' in a.variant else 'dataset'
    output=Path(base)/'per-flow'/a.dataset/f'soft_window-0.0-{a.window}'/kind/f'{a.model}-removal-0.15-{importance}'
    output.mkdir(parents=True,exist_ok=True)
    loop.iterate_window(model_path=str(Path('models')/tag/a.dataset),results_path=str(output),iid_data=pd.read_csv(path/'test_normalized.csv'),
        visible_ood=visible,invisible_ood=pd.read_csv(path/'invisible_normalized.csv'),num_gpus=0,rounds=a.rounds,window=a.window,mode='soft')
if __name__=='__main__':main()
