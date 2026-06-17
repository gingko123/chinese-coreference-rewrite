from dataclasses import dataclass

from .mention_extractor_types import Mention


@dataclass(frozen=True)
class BackendInfo:
    name: str
    available: bool
    message: str


@dataclass(frozen=True)
class BackendResult:
    info: BackendInfo
    entities: list[Mention]


def backend_status(backend: str) -> BackendInfo:
    """Return whether an optional NLP backend can be imported."""
    if backend == "rule":
        return BackendInfo("rule", True, "使用内置规则抽取。")
    if backend == "hanlp":
        try:
            import hanlp  # noqa: F401
        except Exception as exc:
            return BackendInfo("hanlp", False, f"HanLP 未启用：{exc}")
        return BackendInfo("hanlp", True, "HanLP 已安装；当前版本保留规则抽取作为主流程。")
    if backend == "ltp":
        try:
            import ltp  # noqa: F401
        except Exception as exc:
            return BackendInfo("ltp", False, f"LTP 未启用：{exc}")
        return BackendInfo("ltp", True, "LTP 已安装；当前版本保留规则抽取作为主流程。")
    return BackendInfo(backend, False, "未知 NLP 后端，已回退到规则抽取。")


def extract_backend_entities(text: str, backend: str) -> BackendResult:
    """Hook for optional HanLP/LTP extraction.

    The project keeps rule extraction as the stable baseline. This hook makes
    the architecture ready for HanLP/LTP without forcing heavy model downloads.
    """
    info = backend_status(backend)
    return BackendResult(info=info, entities=[])
