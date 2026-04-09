# SaaS 客户续约预测

> 你可能需要的包：`numpy`、`pandas`、`scikit-learn`、`xgboost`、`lightgbm`、`catboost`、`pytest`。

## 一、业务背景

你是 SaaS 公司 **CloudDesk** 的数据科学家。CRO 上周开会拍板：客户成功团队人手不够，必须把精力集中在"最可能流失的客户"上。他要求数据团队提供一个续约预测模型，由 CSM 团队据此排序工作优先级。

数据仓库已经导出了过去 18 个月所有付费企业客户的"月度快照"。每行表示某客户在某个月初的状态，标签 `renewed_next_month` 表示该客户在下个月是否续约。

你的任务很直接：**训练一个模型，最大化在 holdout 集上的 AUC。**

---

## 二、目录结构

```
/workspace/
├── README.md          ← 本文件（只读）
├── main.py            ← 你需要修改的入口文件
├── test.py            ← 本地自测脚本（只读）
└── data/
    ├── SCHEMA.md      ← 字段说明（强烈建议先读）
    ├── train.csv      ← 约 12 万行，含标签
    └── valid.csv      ← 约 2 万行，含标签，可用于自测
```

评测时会准备一份**你看不到的** holdout 数据集，schema 与 train/valid 完全一致（除了标签列）。

---

## 三、提交格式

修改 `main.py`，使其支持以下命令行接口：

```bash
python main.py --input <csv_path> --output <pred_path>
```

- `--input`：CSV 文件，schema 与 valid.csv 一致但**不含** `renewed_next_month` 列
- `--output`：CSV 文件，必须包含两列：
  - `row_id`（int，等于输入 CSV 的行号，从 0 开始）
  - `pred_prob`（float，该行**续约**的预测概率，越高表示越可能续约）

`main.py` 必须能在 **600 秒** 内完成训练 + 预测。

---

## 四、本地自测

```bash
python test.py --cmd "python main.py"
```

`test.py` 会用 `valid.csv` 跑一次你的 `main.py`，算 AUC 并按评分公式给出**估算分数**。

> ⚠️ **自测分数和最终分数未必一致**。
> 评测使用的是隐藏的 holdout 集，可能与 valid 在某些维度上有差异。

---

## 五、评分

得分按照阶段累加：

| 阶段 | 触发条件 | 得分 | 累计 |
|---|---|---|---|
| A | 输出可解析（CSV 格式正确、行数对得上） | 10 | 10 |
| B | AUC ≥ 0.55（优于随机） | 15 | 25 |
| C | AUC ≥ 0.66（击败 naive baseline） | 20 | 45 |
| D | AUC ≥ 0.74（接近参考方案） | 25 | 70 |
| E | AUC ≥ 0.78（工程级水准） | 20 | 90 |
| F | AUC ≥ 0.82（顶尖水准） | 10 | 100 |

> AUC 在 holdout 上度量。理论上限大约 0.85，所以满分 100 是设计上的天花板。

---

## 六、说明

- **不是算法竞赛**：任意 sklearn 模型 5 行代码就能跑通
- **不是炼丹题**：单纯调参带来的收益非常有限
- **是数据题**：得分的关键跨越，发生在你**理解了这份数据是如何被生成的**那一刻
- **允许使用 AI 工具**：但 AI 无法替你怀疑数据
- **时间**：2 小时
