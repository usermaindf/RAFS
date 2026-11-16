# RAFS: Redundancy-Aware Field Search

论文《冗余感知的协议字段级捷径搜索：面向可靠的加密流量分类》的项目自有实现与实验结果。

不分发第三方 ShortcutCatcher 基线源码、原始特征表、含原始特征列的扩展表、抓包或权重。训练需另行取得兼容基线和数据；历史结果分析和绘图无需这些外部材料。

| 路径 | 内容 |
|---|---|
| `src/` | 项目新增的字段分组、联合搜索、对照变体和集成入口 |
| `preprocessing/` | 项目编写的头部提取、行匹配、相对特征构造程序 |
| `results/` | 本项目实测逐轮统计 CSV 和图表数值快照 |
| `analysis/` | 统计与绘图脚本、去除本机路径后的训练计数日志 |
| `reproduce.py` | 外部代码与数据运行入口，以及发布文件校验 |
| `SHA256SUMS` | 全包校验清单 |

## 环境与历史结果复算

建议 Python 3.10 独立环境。历史实验使用 Python 3.9、AutoGluon 1.4.0，关键依赖版本见 requirements。未复制依赖源码。RF 使用 CPU，MLP 使用 PyTorch；系统与依赖不同可能产生数值差异。

```sh
python -m pip install -r requirements.txt
python reproduce.py --verify
python analysis/seeds_report.py
python analysis/stats_tests.py
python analysis/sens_report.py
python analysis/mlp_report.py
python analysis/plot_figures.py
```

统计脚本读取已记录的真实实验数据。图 3–11 使用 `results/figure_data.json` 冻结快照，输出 SVG/PDF/PNG；图 3 机制测量没有独立批量生成程序。中文绘图需安装宋体或 Noto Serif CJK SC。`--refresh-data` 不适用于此包。重新生成 Markdown 会更新时间戳，此后校验清单也需更新。

## 从头训练：自行提供基线和数据

`--baseline-dir` 指向自行取得的 ShortcutCatcher 兼容实现，需有 `loop.py`、`model.py`、`explain.py`、`noise.py`。Loop 需支持 `set_data`、`iterate_window`、`save_importances` 和 `save_iteration_time` 接口。本包在运行时引用这些外部模块，不复制实现。

`--data-root` 指向外部目录，其中有 `per-flow/<setting>/{train,val,test,visible,invisible}_normalized.csv`。普通实验需 116 特征列和 `class` 标签；相对特征实验需另增 25 列相对值。9 设置为 `vpn-service`、`app53-time`、`app53-version` 各自的 `s0/s1/s2`。

```sh
# 替换外部文件路径
python reproduce.py --baseline-dir /path/to/ShortcutCatcher --data-root /path/to/dataset --datasets vpn-service-s2 --variants grouppair --seeds 0 --dry-run
python reproduce.py --baseline-dir /path/to/ShortcutCatcher --data-root /path/to/dataset
```

默认 9 设置 × 3 种子 × none/group/grouppair，w=5、k=4、最多 100 轮。可选 `--seeds 0 1 2 3 4 5 6 7 8 9`、`--pair-top 3/5`、`--window 3/7`、`--variants grouprel grouppairrel`（仅 App，需相对特征目录）。`--model NeuralNetTorch` 自动使用 permutation importance；论文仅在三个 S2 上评估 MLP。历史 App S2 基线 34 轮、RAFS 100 轮；VPN 两者均 100 轮，需分别指定 `--rounds`。

新输出写入 `runs/`，不覆盖历史结果；若已有日志，请换用新的 `--run-dir`。汇总新结果时，将环境变量 `RAFS_RESULTS_ROOT` 和 `RAFS_LOG_ROOT` 都设为运行目录绝对路径，再执行统计脚本。

## 特征重建与验证边界

项目自有的相对特征程序依次为 `extract_netd.py`、`match_rows.py`、`build_rel.py`，参数见脚本头部。NETD 原始数据与基线特征须自行取得；中间 pickle、第三方标签和特征表不分发。

论文方法基于 ShortcutCatcher 并使用 AutoGluon，请引用原工作。项目自有代码尚未指定开源许可证，不替第三方材料授予许可。已验证历史统计和绘图；集成入口仅对本地外部基线验证，不保证所有上游版本兼容。
