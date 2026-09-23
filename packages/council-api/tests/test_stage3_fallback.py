"""When the chairman fails, the council falls back to the peer-review winner."""

from __future__ import annotations

import asyncio

from council_api.council import CouncilService
from council_api.models import CouncilAssessment


class FailingChairman:
    async def chat_json(self, *args, **kwargs):
        raise RuntimeError("chairman unavailable")


def _assessment(label: str, model: str) -> CouncilAssessment:
    return CouncilAssessment(
        model=model, model_name=model, result_json={"from": model}, label=label
    )


ASSESSMENTS = [
    _assessment("Assessment A", "vendor/first"),
    _assessment("Assessment B", "vendor/second"),
    _assessment("Assessment C", "vendor/third"),
]


def _stage3(rankings: list[dict] | None) -> tuple[dict, bool]:
    service = CouncilService(llm=FailingChairman())  # type: ignore[arg-type]
    return asyncio.run(
        service._stage3_synthesise(
            "system", "user", ASSESSMENTS, [], "vendor/chair",
            aggregate_rankings=rankings,
        )
    )


def test_fallback_uses_the_top_ranked_assessment() -> None:
    rankings = [
        {"label": "Assessment C", "average_rank": 1.0},
        {"label": "Assessment A", "average_rank": 2.0},
    ]
    assert _stage3(rankings) == ({"from": "vendor/third"}, True)


def test_fallback_skips_ranked_labels_that_have_no_assessment() -> None:
    rankings = [
        {"label": "Assessment Z", "average_rank": 1.0},
        {"label": "Assessment B", "average_rank": 2.0},
    ]
    assert _stage3(rankings) == ({"from": "vendor/second"}, True)


def test_fallback_without_rankings_uses_the_first_assessment() -> None:
    assert _stage3([]) == ({"from": "vendor/first"}, True)
    assert _stage3(None) == ({"from": "vendor/first"}, True)


def test_fallback_with_no_assessments_is_empty() -> None:
    service = CouncilService(llm=FailingChairman())  # type: ignore[arg-type]
    result = asyncio.run(service._stage3_synthesise("s", "u", [], [], "vendor/chair"))
    assert result == ({}, True)
