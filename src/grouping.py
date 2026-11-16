"""[our module] Protocol-field grouping for the ShortcutCatcher search loop.

ShortcutCatcher scores and removes one column at a time. Its columns are (protocol field x packet
index), e.g. ip_id_pkt0..ip_id_pkt4, and the four octets of an IP address. A shortcut carried by a
field therefore has to be found and removed once per copy, and the copies that are still present
keep acting as the same shortcut. Here the unit of search is the protocol field:
  * importance of a field  = aggregate of the importances of its columns (sum by default),
  * removing a field       = zeroing all of its columns at once.
The search loop itself (Loop.iterate_window) is unchanged; only the explainer output and the noise
operator are lifted from columns to fields.
"""
import re
from collections import OrderedDict

from explain import Explain
from noise import Noise


def field_of(column):
    k = re.sub(r'_pkt\d+$', '', column)              # per-packet copies -> field
    k = re.sub(r'_rel$', '', k)                       # relative version (dataset_rel) belongs to the same field
    k = re.sub(r'^(ip_(src|dst))_\d$', r'\1', k)     # IP address octets -> address
    return k


def build_groups(columns):
    groups = OrderedDict()
    for c in columns:
        if c == 'class':
            continue
        groups.setdefault(field_of(c), []).append(c)
    return groups


class GroupExplain(Explain):
    def __init__(self, importance_type='default', agg='sum'):
        super().__init__(importance_type)
        self.agg = agg

    def get_importance(self, predictor, val_df, label_column='class', n_repeats=1):
        col_imp = super().get_importance(predictor, val_df, label_column, n_repeats)
        field_imp = OrderedDict()
        for c, v in col_imp.items():
            field_imp.setdefault(field_of(c), []).append(float(v))
        if self.agg == 'max':
            return {k: max(v) for k, v in field_imp.items()}
        if self.agg == 'mean':
            return {k: sum(v) / len(v) for k, v in field_imp.items()}
        return {k: sum(v) for k, v in field_imp.items()}


class GroupNoise(Noise):
    """Noise operator whose keys are protocol fields; expands each field to its columns."""

    def __init__(self, groups, noise_type='removal', standard=0.15):
        super().__init__(noise_type, standard)
        self.groups = groups

    def apply(self, origin_train, origin_val, feature_noise):
        if feature_noise == {'base': 0}:
            return origin_train, origin_val
        expanded = {'base': 0}
        for k, v in feature_noise.items():
            if k == 'base':
                continue
            for c in self.groups.get(k, [k]):
                expanded[c] = v
        return super().apply(origin_train, origin_val, expanded)


REL_CAPABLE = {'tcp_seq', 'tcp_ack', 'tcp_timestamp', 'tcp_echo_timestamp', 'ip_id'}


class RelGroupNoise(GroupNoise):
    """[our module 3] Two-level, semantics-preserving mitigation (needs dataset_rel/).

    degree 0: absolute columns used, relative columns inactive (zeroed) -> same feature space as the original
    degree 1: for REL_CAPABLE fields, absolute columns zeroed and the within-flow relative columns activated
              (the environment-specific initial value is removed, the behaviour - bytes sent, clock ticks,
              packets sent - is kept); other fields are zeroed as before
    degree 2: relative columns zeroed as well (complete removal)
    The search loop needs no change: a field mitigated to degree 1 stays in the importance ranking and can be
    selected again, which moves it to degree 2.
    """

    def apply(self, origin_train, origin_val, feature_noise):
        zero = {'base': 0}
        for f, cols in self.groups.items():
            d = feature_noise.get(f, 0)
            rel = [c for c in cols if '_rel_pkt' in c]
            ab = [c for c in cols if '_rel_pkt' not in c]
            if d >= 1:
                for c in ab:
                    zero[c] = d
            if d != 1 or f not in REL_CAPABLE:
                for c in rel:
                    zero[c] = max(d, 1)
        return self._add_removal_noise(origin_train, origin_val, zero)


class NoRelGroupNoise(GroupNoise):
    """Sanity check on dataset_rel/: relative columns are always zeroed, so the model sees exactly the
    original feature space and results must equal plain field grouping on dataset/."""

    def apply(self, origin_train, origin_val, feature_noise):
        zero = {'base': 0}
        for f, cols in self.groups.items():
            d = feature_noise.get(f, 0)
            for c in cols:
                if '_rel_pkt' in c:
                    zero[c] = 1
                elif d >= 1:
                    zero[c] = d
        return self._add_removal_noise(origin_train, origin_val, zero)
