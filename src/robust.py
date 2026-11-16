"""[our module] Uncertainty-aware verification for the ShortcutCatcher loop.

ShortcutCatcher decides (a) which feature to remove in each round and (b) which round to deploy by
the point estimate of accuracy / macro-F1 on one small verification set V (60 flows for VPN).
With so few samples, one flow changes accuracy by 1.7 points, so both decisions follow noise and the
final argmax over ~25-90 rounds is optimistically biased (winner's curse).

Here every evaluation on V is repeated on B bootstrap resamples of V. The same
resample indices are reused for every candidate model (common random numbers), so candidates are
compared on identical resamples. Decisions use the lower confidence bound
    LCB = mean - lam * std
of the bootstrap distribution, i.e. a pessimistic (worst-case-leaning) score in the spirit of
distributionally robust selection (GroupDRO) and the one-standard-error rule (Breiman et al., 1984).
  * in-loop feature choice: 'score_test' of the verification leaderboard is replaced by LCB(accuracy)
    (raw accuracy kept in 'acc_raw');
  * final round selection: 'f1_lcb' column (LCB of macro-F1) is written and used by compare.py.
"""
import numpy as np
from sklearn.metrics import f1_score

from model import Model

VERIFY_NAME = 'Visible OOD'


class RobustModel(Model):
    def __init__(self, model_name='RandomForestGini', n_boot=200, lam=1.0, boot_seed=0):
        super().__init__(model_name)
        self.n_boot, self.lam, self.boot_seed = n_boot, lam, boot_seed
        self._idx = {}   # id(verification df) -> bootstrap index matrix (shared by all candidates)

    def _boot_indices(self, y):
        """Plain (non-stratified) bootstrap. A stratified bootstrap keeps every class size fixed, and on
        VPN the classifier is right or wrong on whole classes, so stratified resamples have zero variance;
        the plain bootstrap lets class weights vary and exposes this class-level uncertainty."""
        key = (len(y), hash(tuple(y)))
        if key not in self._idx:
            rng = np.random.RandomState(self.boot_seed)
            self._idx[key] = rng.randint(0, len(y), size=(self.n_boot, len(y)))
        return self._idx[key]

    def evaluate(self, data, name="", n_bins=15):
        df = super().evaluate(data, name, n_bins)
        if name != VERIFY_NAME:
            return df
        label_col = getattr(self.predictor, 'label', 'class')
        y = data[label_col].values
        proba = self.predictor.predict_proba(data)
        pred = proba.columns.values[proba.values.argmax(1)]
        idx = self._boot_indices(y)
        accs = np.array([(pred[i] == y[i]).mean() for i in idx])
        labels = np.unique(y)
        f1s = np.array([f1_score(y[i], pred[i], labels=labels, average='macro', zero_division=0) for i in idx])
        df['acc_raw'] = df['score_test']
        df['acc_boot_mean'], df['acc_boot_std'] = accs.mean(), accs.std()
        df['f1_boot_mean'], df['f1_boot_std'] = f1s.mean(), f1s.std()
        df['f1_lcb'] = f1s.mean() - self.lam * f1s.std()
        df['score_test'] = accs.mean() - self.lam * accs.std()   # drives the in-loop choice
        print(f"[Robust] verification acc {df['acc_raw'].values[0]:.4f} -> LCB {df['score_test'].values[0]:.4f} "
              f"(boot std {accs.std():.4f}); F1 LCB {df['f1_lcb'].values[0]:.4f}")
        return df
