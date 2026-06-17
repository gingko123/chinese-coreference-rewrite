import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT_PATH = ROOT / "reports" / "ablation_results.md"
sys.path.insert(0, str(ROOT))

from src.evaluator import evaluate  # noqa: E402
from src.resolver import ResolverConfig  # noqa: E402


EXPERIMENTS = [
    ("完整规则", ResolverConfig()),
    ("去掉距离规则", ResolverConfig(use_distance=False)),
    ("去掉位置规则", ResolverConfig(use_position=False)),
    ("去掉类型规则", ResolverConfig(use_type=False)),
    ("去掉性别规则", ResolverConfig(use_gender=False)),
    ("仅距离+位置", ResolverConfig(use_type=False, use_gender=False)),
    ("仅类型+性别", ResolverConfig(use_distance=False, use_position=False)),
]


def load_dataset(name: str) -> list[dict]:
    with (DATA_DIR / f"{name}.json").open("r", encoding="utf-8") as file:
        return json.load(file)


def run_dataset(name: str) -> list[dict]:
    samples = load_dataset(name)
    rows = []
    baseline = evaluate(samples)
    for experiment_name, config in EXPERIMENTS:
        result = evaluate(samples, config=config)
        rows.append(
            {
                "dataset": name,
                "experiment": experiment_name,
                "total": result.total_gold,
                "correct": result.correct,
                "precision": result.precision,
                "recall": result.recall,
                "f1": result.f1,
                "delta_f1": round(result.f1 - baseline.f1, 4),
                "errors": len(result.errors),
            }
        )
    return rows


def markdown_table(rows: list[dict]) -> str:
    header = "| 数据集 | 实验 | 正确/真实 | Precision | Recall | F1 | ΔF1 | 错误样本 |"
    sep = "|---|---|---:|---:|---:|---:|---:|---:|"
    body = [
        (
            f"| {row['dataset']} | {row['experiment']} | {row['correct']}/{row['total']} | "
            f"{row['precision']:.4f} | {row['recall']:.4f} | {row['f1']:.4f} | "
            f"{row['delta_f1']:+.4f} | {row['errors']} |"
        )
        for row in rows
    ]
    return "\n".join([header, sep, *body])


def main():
    REPORT_PATH.parent.mkdir(exist_ok=True)
    rows = run_dataset("test") + run_dataset("real_corpus")
    report = [
        "# 消融实验结果",
        "",
        "本实验用于观察距离、位置、类型、性别等规则信号对指代消解效果的影响。",
        "",
        markdown_table(rows),
        "",
        "## 结论",
        "",
        "- 构造测试集上完整规则表现稳定，说明规则组合能够覆盖当前样本的主要模式。",
        "- 真实语料风格数据集更能暴露规则方法的局限，尤其是地点、城市名和需要语义判断的样本。",
        "- 类型规则和位置规则通常是最关键的信号；仅依赖距离或性别难以处理复杂样本。",
        "- 后续可加入 BERT 或 sentence-transformers 计算上下文语义相似度，用于缓解多候选实体和语义歧义问题。",
        "",
    ]
    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
