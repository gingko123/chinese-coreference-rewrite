from dataclasses import dataclass

from .resolver import DEFAULT_CONFIG, ResolverConfig, resolve_text


@dataclass(frozen=True)
class ErrorCase:
    text: str
    gold: list[tuple[str, str]]
    predicted: list[tuple[str, str]]
    missing: list[tuple[str, str]]
    extra: list[tuple[str, str]]
    error_types: list[str]


@dataclass(frozen=True)
class EvaluationResult:
    total_gold: int
    total_predicted: int
    correct: int
    accuracy: float
    precision: float
    recall: float
    f1: float
    errors: list[ErrorCase]


def _gold_pairs(sample: dict) -> list[tuple[str, str]]:
    return [
        (item["pronoun"], item["antecedent"])
        for item in sample.get("coreference", [])
    ]


def _predicted_pairs(
    text: str,
    backend: str = "rule",
    config: ResolverConfig = DEFAULT_CONFIG,
) -> list[tuple[str, str]]:
    _, _, results = resolve_text(text, backend=backend, config=config)
    return [(item.pronoun.text, item.antecedent.text) for item in results]


def _classify_errors(
    gold: list[tuple[str, str]],
    predicted: list[tuple[str, str]],
) -> list[str]:
    gold_by_pronoun = {pronoun: antecedent for pronoun, antecedent in gold}
    predicted_by_pronoun = {pronoun: antecedent for pronoun, antecedent in predicted}
    types: set[str] = set()

    for pronoun, antecedent in gold_by_pronoun.items():
        if pronoun not in predicted_by_pronoun:
            types.add("漏判代词")
        elif predicted_by_pronoun[pronoun] != antecedent:
            types.add("先行词错误")

    for pronoun in predicted_by_pronoun:
        if pronoun not in gold_by_pronoun:
            types.add("误判关系")

    return sorted(types)


def evaluate(
    samples: list[dict],
    backend: str = "rule",
    config: ResolverConfig = DEFAULT_CONFIG,
) -> EvaluationResult:
    """Evaluate predicted antecedents with relation-level metrics."""
    total_gold = 0
    total_predicted = 0
    correct = 0
    errors: list[ErrorCase] = []

    for sample in samples:
        gold = _gold_pairs(sample)
        predicted = _predicted_pairs(sample["text"], backend=backend, config=config)

        gold_set = set(gold)
        predicted_set = set(predicted)

        sample_correct = len(gold_set & predicted_set)
        missing = sorted(gold_set - predicted_set)
        extra = sorted(predicted_set - gold_set)

        total_gold += len(gold_set)
        total_predicted += len(predicted_set)
        correct += sample_correct

        if missing or extra:
            errors.append(
                ErrorCase(
                    text=sample["text"],
                    gold=gold,
                    predicted=predicted,
                    missing=missing,
                    extra=extra,
                    error_types=_classify_errors(gold, predicted),
                )
            )

    accuracy = correct / total_gold if total_gold else 0.0
    precision = correct / total_predicted if total_predicted else 0.0
    recall = correct / total_gold if total_gold else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return EvaluationResult(
        total_gold=total_gold,
        total_predicted=total_predicted,
        correct=correct,
        accuracy=round(accuracy, 4),
        precision=round(precision, 4),
        recall=round(recall, 4),
        f1=round(f1, 4),
        errors=errors,
    )
