from abc import ABC, abstractmethod
from datetime import datetime
from pydantic import BaseModel, Field


class NormalizedJob(BaseModel):
    """
    Standardized job model returned by all source connectors.
    Guarantees consistent data representation regardless of the source.
    """
    employer_name: str = Field(..., description="Verified company or employer name")
    job_title: str = Field(..., description="Official job title from the source")
    source_name: str = Field(..., description="Name of the source system (e.g. Greenhouse)")
    source_url: str = Field(..., description="Direct URL to the job posting")
    source_type: str = Field(
        default="public_ats_feed",
        description="Source classification (official_careers, public_ats_feed, etc.)",
    )
    description_text: str = Field(..., description="Normalized clean text of the job description")
    location: str | None = Field(default=None, description="Job location or remote status")
    employment_type: str | None = Field(default=None, description="Full-time, contract, internship, etc.")
    posted_at: datetime | None = Field(default=None, description="Date posted if provided by source")
    fetched_at: datetime = Field(..., description="Timestamp when job snapshot was fetched")
    content_hash: str | None = Field(default=None, description="SHA-256 hash of posting content")
    is_stale: bool = Field(default=False, description="Freshness status indicator")
    verification_status: str = Field(default="verified", description="verified, unverified, or failed")
    verification_notes: str | None = Field(default=None, description="Explanation of verification result")


class BaseJobConnector(ABC):
    """
    Abstract base interface for all job posting source connectors.
    """
    source_name: str
    source_type: str

    @abstractmethod
    def search_jobs(self, company_name: str, target_role: str) -> list[NormalizedJob]:
        """
        Queries the source for postings matching the company name and target role.
        Must handle errors, rate limits, timeouts, and parsing variations gracefully.
        """
        pass
