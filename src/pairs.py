"""[our module] Redundancy-aware joint search (extends module 2, the search strategy).

Diagnosis on VPN S2 (see experiments/shortcutcatcher_repro/MODULE1_shift_explainer.md): IP addresses and
TCP timestamps both encode the capture environment. Removing either one alone does not help: the model
falls back on the other, and F1 can even get worse. Removing them together roughly triples check F1.
A greedy search that only ever tests one field per round sees no gain at any step and finds such
combinations only by chance. This is the limitation ShortcutCatcher states itself ("cannot capture
interactions between features"; future work: group-wise removal / Shapley interactions).

Here each round tests, besides the top-`window` single fields, every pair among the top-`pair_top`
fields (by the same importance ranking), and removes the best candidate (single or pair). When a single
and a pair score the same, the single wins (fewer removals). Everything else (training, evaluation,
importance, logging, final-round selection) is as in Loop.iterate_window. Used together with
protocol-field grouping (grouping.py).

Reference ideas: pairwise / Shapley interaction screening (e.g. SHAP-IQ, NeurIPS 2023), group feature
selection.
"""
import itertools
import time


def iterate_window_pairs(self, model_path, results_path, iid_data, visible_ood, invisible_ood, num_gpus,
                         rounds=10, window=5, mode="soft", pair_top=4):
    saving_path = model_path
    for i in range(rounds):
        print(f"\n===== Iteration {i+1}/{rounds} =====")
        select_feature_elapsed = 0.0
        base_window_elapsed = 0.0
        if i == 0:
            t0 = time.perf_counter()
            noised_train, noised_val = self.noise.apply(self.origin_train, self.origin_val, self.feature_noise)
            best_predictor = self.model.run(noised_train, noised_val, saving_path, num_gpus)
            best_visible_results_df = self.model.evaluate(visible_ood, "Visible OOD")
            base_round_elapsed = time.perf_counter() - t0
        else:
            ranked = [f for f, _ in sorted(self.feature_importance_dict.items(), key=lambda x: x[1], reverse=True)]
            singles = [(f,) for f in ranked[:window]]
            pairs = list(itertools.combinations(ranked[:min(pair_top, len(ranked))], 2))
            # never test a candidate that would remove every remaining field (no features -> no model)
            candidates = [c for c in singles + pairs if len(c) < len(ranked)]
            t_sel = time.perf_counter()
            best_cand, best_acc = None, -1.0
            for j, cand in enumerate(candidates):
                print(f"             ===== Iteration {i+1}-{j+1}/{'+'.join(cand)} =====")
                for f in cand:
                    self.increase_feature_noise(f)
                noised_train, noised_val = self.noise.apply(self.origin_train, self.origin_val, self.feature_noise)
                self.model.run(noised_train, noised_val, saving_path, num_gpus)
                acc = self.model.evaluate(visible_ood, "Visible OOD")['score_test'].values[0]
                print(f"[Pair] candidate {'+'.join(cand)}: verification accuracy {acc:.4f}")
                if acc > best_acc:              # strict: singles come first and win ties
                    best_cand, best_acc = cand, acc
                for f in cand:
                    self.decrease_feature_noise(f)
            print(f"[Pair] selected {'+'.join(best_cand)} ({'pair' if len(best_cand) == 2 else 'single'}), "
                  f"verification accuracy {best_acc:.4f}")
            for f in best_cand:
                self.increase_feature_noise(f)
            select_feature_elapsed = time.perf_counter() - t_sel
            t_b = time.perf_counter()
            noised_train, noised_val = self.noise.apply(self.origin_train, self.origin_val, self.feature_noise)
            best_predictor = self.model.run(noised_train, noised_val, saving_path, num_gpus)
            best_visible_results_df = self.model.evaluate(visible_ood, "Visible OOD")
            base_window_elapsed = time.perf_counter() - t_b

        t_imp = time.perf_counter()
        self.best_score = best_visible_results_df['score_test'].values[0]
        self.feature_importance_dict = self.explainer.get_importance(best_predictor, self.origin_val)
        get_importance_elapsed = time.perf_counter() - t_imp

        t_v = time.perf_counter()
        iid_df = self.model.evaluate(iid_data, name="IID")
        self.save_results(iid_df, f'{results_path}/leaderboard-False-{self.noise.standard}.csv')
        self.save_results(best_visible_results_df, f'{results_path}/leaderboard-True-visible-{self.noise.standard}.csv')
        self.save_importances(results_path)
        evaluate_verification_elapsed = time.perf_counter() - t_v
        invisible_df = self.model.evaluate(invisible_ood, name="Invisible OOD")
        self.save_results(invisible_df, f'{results_path}/leaderboard-True-invisible-{self.noise.standard}.csv')

        self.save_iteration_time(results_path, {
            "iteration": i + 1,
            "base_time": base_round_elapsed if i == 0 else base_window_elapsed,
            "selection_time": select_feature_elapsed,
            "explain_time": get_importance_elapsed,
            "verification_time": evaluate_verification_elapsed,
        })
        remaining = len(self.feature_importance_dict)
        # Stop when 2 or fewer fields are left: a pair candidate would then remove every remaining field and
        # AutoGluon cannot fit a model without features (this crashed the first batch of runs, 2026-11-08).
        # The original loop also stops once its window has shrunk to 2.
        if remaining <= 2:
            print("[Forbidden] All features forbidden or evaluated. Stopping.")
            break
        window = min(window, remaining)
    print("[Finished] Experiment complete.")
