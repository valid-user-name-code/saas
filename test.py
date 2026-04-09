"""
用法：
    python test.py --cmd "python main.py"

会在 valid.csv 上跑你的方案、算 AUC 并按评分公式给出**估算分数**。
"""
import argparse
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd
from sklearn.metrics import roc_auc_score


HERE = Path(__file__).parent
VALID_CSV = HERE / 'data' / 'valid.csv'
LABEL_COL = 'renewed_next_month'

# 与 internal/judge.py 中一致的得分阈值
PHASE_THRESHOLDS = [
    ('A 输出可解析',          0.0,  10),
    ('B 优于随机',            0.55, 15),
    ('C 击败 naive baseline', 0.66, 20),
    ('D 接近参考方案',        0.74, 25),
    ('E 工程级水准',          0.78, 20),
    ('F 顶尖水准',            0.82, 10),
]


def estimate_score(auc: float) -> tuple[int, list[tuple[str, bool, int]]]:
    """累加阶段得分。返回 (总分, 每阶段(name, passed, points))"""
    total = 0
    breakdown = []
    for name, threshold, points in PHASE_THRESHOLDS:
        passed = auc >= threshold
        if passed:
            total += points
        breakdown.append((name, passed, points))
    return total, breakdown


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cmd', required=True,
                        help='shell command that runs your solution, e.g. "python main.py"')
    args = parser.parse_args()

    if not VALID_CSV.exists():
        print(f"ERROR: {VALID_CSV} not found.", file=sys.stderr)
        sys.exit(1)

    valid = pd.read_csv(VALID_CSV)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        input_csv = tmp / 'input.csv'
        pred_csv = tmp / 'pred.csv'
        valid.drop(columns=[LABEL_COL]).to_csv(input_csv, index=False)

        cmd = shlex.split(args.cmd) + ['--input', str(input_csv), '--output', str(pred_csv)]
        print(f">>> Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            sys.exit(1)

        if not pred_csv.exists():
            print(f"ERROR: solution did not write {pred_csv}", file=sys.stderr)
            sys.exit(1)

        preds = pd.read_csv(pred_csv)
        if 'row_id' not in preds.columns or 'pred_prob' not in preds.columns:
            print("ERROR: prediction CSV must contain columns: row_id, pred_prob", file=sys.stderr)
            sys.exit(1)
        preds = preds.sort_values('row_id').reset_index(drop=True)

    auc = roc_auc_score(valid[LABEL_COL].values, preds['pred_prob'].values)
    total, breakdown = estimate_score(auc)

    print(f"\n=== Self-test result (on valid.csv) ===")
    print(f"  AUC: {auc:.4f}")
    print(f"  Estimated score: {total} / 100")
    print(f"\n  阶段细分：")
    for name, passed, points in breakdown:
        mark = '✓' if passed else '✗'
        print(f"    [{mark}] {name}  (+{points if passed else 0}/{points})")
    print(f"\n  ⚠️  This is an ESTIMATE on valid.csv.")
    print(f"     Final scoring uses a hidden holdout set.")


if __name__ == '__main__':
    main()
