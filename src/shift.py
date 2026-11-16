"""[our module] Shift-aware field importance (replaces module 1, the explainer).

ShortcutCatcher's idea is to find features that the model relies on in the training scenario but
that are not valid in the deployment scenario. Its explainer, however, ranks candidates with the
random forest's Gini importance, which is computed from the training data alone and never looks at the
verification set V. The K candidates tried in each round are therefore "the fields most useful in
training", not "the fields most likely to be shortcuts".

Here each protocol field (grouping.py) gets a shift score
    shift(f) = PI_in(f) - PI_V(f)
where PI_in is the permutation importance on the in-distribution validation split of D and PI_V the
permutation importance on V. A field the model depends on in-distribution but that does not help (or
hurts) on V gets a high score. All columns of a field are permuted jointly with the same row
permutation. The search loop is unchanged: it simply tries the top-K fields by shift score.

References: permutation importance (Breiman, 2001); model reliance (Fisher, Rudin & Dominici, JMLR 2019);
comparing feature attributions across distributions to explain shift.
"""
import numpy as np

from grouping import field_of

LABEL = 'class'


class ShiftExplain:
    def __init__(self, groups, verify_df, n_repeats=3, seed=0, metric='accuracy'):
        self.groups = groups
        self.verify_df = verify_df
        self.n_repeats = n_repeats
        self.seed = seed
        self.metric = metric
        self.last = {}   # field -> (PI_in, PI_V), for logging

    def _score(self, predictor, df):
        return float((predictor.predict(df).values == df[LABEL].values).mean())

    def _pi(self, predictor, df, cols, base, rng):
        drops = []
        for _ in range(self.n_repeats):
            tmp = df.copy()
            perm = rng.permutation(len(tmp))
            tmp[cols] = tmp[cols].values[perm]
            drops.append(base - self._score(predictor, tmp))
        return float(np.mean(drops))

    def get_importance(self, predictor, val_df, label_column=LABEL, n_repeats=None):
        used = set(predictor.feature_metadata.get_features())        # columns the current model uses
        fields = {}
        for f, cols in self.groups.items():
            active = [c for c in cols if c in used]
            if active:
                fields[f] = active
        base_in = self._score(predictor, val_df)
        base_v = self._score(predictor, self.verify_df)
        rng = np.random.RandomState(self.seed)                       # same permutations every round
        out = {}
        for f, cols in fields.items():
            pi_in = self._pi(predictor, val_df, cols, base_in, rng)
            pi_v = self._pi(predictor, self.verify_df, cols, base_v, rng)
            self.last[f] = (pi_in, pi_v)
            out[f] = pi_in - pi_v
        top = sorted(out.items(), key=lambda x: x[1], reverse=True)[:5]
        print('[Shift] top fields (PI_in - PI_V): ' +
              ', '.join(f'{f}={s:+.4f} (in {self.last[f][0]:+.4f}, V {self.last[f][1]:+.4f})' for f, s in top))
        return out
