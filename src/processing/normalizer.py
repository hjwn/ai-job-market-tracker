"""Normalization boundary for source-specific job postings."""

from __future__ import annotations

from typing import Any, Mapping

from src.models.job_posting import JobPosting


def normalize_saramin_job(raw_job: Mapping[str, Any]) -> JobPosting:
    """Convert one Saramin job object to the shared model.

    TODO: Implement after validating representative real API responses. Keeping
    this explicit prevents assumptions about optional and conditionally shaped
    fields from leaking into the common model.
    """
    raise NotImplementedError(
        "사람인 실제 응답을 검증한 뒤 정규화 필드 매핑을 구현해야 합니다."
    )
