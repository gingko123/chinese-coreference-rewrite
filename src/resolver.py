from dataclasses import dataclass

from .mention_extractor import Mention, extract_mentions


@dataclass(frozen=True)
class ResolverConfig:
    use_distance: bool = True
    use_position: bool = True
    use_type: bool = True
    use_gender: bool = True


DEFAULT_CONFIG = ResolverConfig()


@dataclass(frozen=True)
class CandidateScore:
    pronoun: Mention
    candidate: Mention
    score: float
    reasons: list[str]


@dataclass(frozen=True)
class CoreferenceResult:
    pronoun: Mention
    antecedent: Mention
    score: float
    candidates: list[CandidateScore]


def _type_score(pronoun: Mention, candidate: Mention) -> tuple[float, str]:
    if pronoun.label == "PERSON_PRONOUN" and candidate.label == "PERSON":
        return 0.45, "type match"
    if pronoun.label == "OBJECT_PRONOUN" and candidate.label == "OBJECT":
        return 0.45, "type match"
    if pronoun.label == "ORG_PRONOUN" and candidate.label == "ORG":
        return 0.5, "type match"
    if pronoun.label == "OBJECT_PRONOUN" and candidate.label in {"ORG", "PERSON"}:
        return -0.2, "type mismatch"
    if pronoun.label == "PERSON_PRONOUN" and candidate.label != "PERSON":
        return -0.2, "type mismatch"
    return 0.0, "weak type signal"


def _gender_score(pronoun: Mention, candidate: Mention) -> tuple[float, str]:
    if pronoun.gender in {"unknown", "neutral"} or candidate.gender == "unknown":
        return 0.05, "gender unknown"
    if pronoun.gender == candidate.gender:
        return 0.25, "gender match"
    return -0.35, "gender mismatch"


def score_candidate(
    pronoun: Mention,
    candidate: Mention,
    config: ResolverConfig = DEFAULT_CONFIG,
) -> CandidateScore:
    """Score one candidate antecedent for one pronoun."""
    distance = max(pronoun.start - candidate.end, 0)
    distance_score = max(0.0, 0.3 - distance / 80) if config.use_distance else 0.0
    position_score = (0.15 if candidate.end <= pronoun.start else -0.4) if config.use_position else 0.0

    if config.use_type:
        type_value, type_reason = _type_score(pronoun, candidate)
    else:
        type_value, type_reason = 0.0, "type disabled"

    if config.use_gender:
        gender_value, gender_reason = _gender_score(pronoun, candidate)
    else:
        gender_value, gender_reason = 0.0, "gender disabled"

    score = distance_score + position_score + type_value + gender_value
    reasons = [
        f"distance={distance}",
        type_reason,
        gender_reason,
        "before pronoun" if candidate.end <= pronoun.start else "after pronoun",
    ]
    return CandidateScore(pronoun, candidate, round(score, 4), reasons)


def resolve_text(
    text: str,
    backend: str = "rule",
    config: ResolverConfig = DEFAULT_CONFIG,
) -> tuple[list[Mention], list[Mention], list[CoreferenceResult]]:
    """Resolve coreference links with a lightweight rule-based strategy."""
    entities, pronouns = extract_mentions(text, backend=backend)
    results: list[CoreferenceResult] = []

    for pronoun in pronouns:
        candidates = [
            entity
            for entity in entities
            if entity.end <= pronoun.start
            or (pronoun.start <= entity.start and entity.end <= pronoun.end)
        ]
        scored = sorted(
            [score_candidate(pronoun, candidate, config=config) for candidate in candidates],
            key=lambda item: item.score,
            reverse=True,
        )
        if scored and scored[0].score > 0:
            results.append(
                CoreferenceResult(
                    pronoun=pronoun,
                    antecedent=scored[0].candidate,
                    score=scored[0].score,
                    candidates=scored,
                )
            )

    return entities, pronouns, results
