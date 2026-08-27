"""Source-independent job-posting domain model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class JobPosting:
    """A normalized job posting shared by all data sources.

    Source identifiers, company, title, and URL are required for traceability.
    Remaining fields are optional because source APIs may omit them.
    """

    source: str
    source_job_id: str
    company: str
    title: str
    url: str
    location: str | None = None
    experience: str | None = None
    education: str | None = None
    employment_type: str | None = None
    published_at: datetime | None = None
    deadline: datetime | None = None
    description: str | None = None
    requirements: str | None = None
    preferred_qualifications: str | None = None
