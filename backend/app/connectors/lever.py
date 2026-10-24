import hashlib
import logging
import re
from datetime import datetime, timezone
from typing import Any
import httpx

from app.connectors.base import BaseJobConnector, NormalizedJob
from app.connectors.greenhouse import clean_html_description, calculate_role_relevance

logger = logging.getLogger(__name__)


class LeverConnector(BaseJobConnector):
    """
    Connector for Lever public ATS job boards.
    Queries official public postings feeds (https://api.lever.co/v0/postings/{company_site}?mode=json).
    """
    source_name = "Lever"
    source_type = "public_ats_feed"
    base_api_url = "https://api.lever.co/v0/postings"

    def __init__(self, timeout: float = 10.0, client: httpx.Client | None = None):
        self.timeout = timeout
        self._client = client

    def _get_client(self) -> httpx.Client:
        if self._client is not None:
            return self._client
        return httpx.Client(
            timeout=self.timeout,
            headers={"User-Agent": "StudentSkillGapAnalyzer/1.0 (Educational Project)"},
        )

    def _derive_company_site(self, company_name: str) -> str:
        """
        Normalizes company name into Lever site slug (lowercase alphanumeric with hyphens).
        """
        slug = re.sub(r"[^a-z0-9]+", "-", company_name.strip().lower()).strip("-")
        return slug

    def search_jobs(self, company_name: str, target_role: str) -> list[NormalizedJob]:
        """
        Implements BaseJobConnector.search_jobs.
        """
        _, _, jobs = self.search_jobs_detailed(company_name, target_role)
        return jobs

    def search_jobs_detailed(
        self,
        company_name: str,
        target_role: str,
    ) -> tuple[str, str, list[NormalizedJob]]:
        """
        Searches Lever public postings and returns (status, explanation_message, list[NormalizedJob]).
        Statuses align with system specification: verified_jobs_found, company_not_verified,
        no_matching_jobs, or source_unavailable.
        """
        company_site = self._derive_company_site(company_name)
        if not company_site:
            return "company_not_verified", "Company name is invalid or cannot be parsed.", []

        url = f"{self.base_api_url}/{company_site}?mode=json"
        client = self._get_client()

        try:
            response = client.get(url)
            if response.status_code == 404:
                logger.info("Lever board not found for site: %s", company_site)
                return (
                    "company_not_verified",
                    f"No public Lever job board could be verified for '{company_name}'.",
                    [],
                )
            response.raise_for_status()
            data = response.json()
        except httpx.TimeoutException:
            logger.warning("Lever request timed out for company: %s", company_name)
            return "source_unavailable", f"Connection to Lever timed out while querying '{company_name}'.", []
        except httpx.HTTPStatusError as exc:
            logger.warning("Lever HTTP error %s for company %s", exc.response.status_code, company_name)
            return "source_unavailable", f"Lever returned an upstream HTTP {exc.response.status_code} error.", []
        except Exception as exc:
            logger.warning("Unexpected error querying Lever for %s: %s", company_name, str(exc))
            return "source_unavailable", f"Lever source unavailable: {str(exc)}", []

        if not isinstance(data, list):
            return "no_matching_jobs", f"Unexpected response format from Lever for {company_name}.", []

        if not data:
            return "no_matching_jobs", f"No open positions are currently listed on {company_name}'s Lever board.", []

        matched_jobs: list[NormalizedJob] = []
        now = datetime.now(timezone.utc)

        for posting in data:
            title = posting.get("text", "").strip()
            is_relevant, notes = calculate_role_relevance(title, target_role)
            if not is_relevant:
                continue

            # Construct full description text from descriptionPlain/description and lists
            description_parts: list[str] = []
            plain_desc = posting.get("descriptionPlain")
            if plain_desc and plain_desc.strip():
                description_parts.append(plain_desc.strip())
            else:
                html_desc = posting.get("description", "")
                if html_desc:
                    cleaned = clean_html_description(html_desc)
                    if cleaned:
                        description_parts.append(cleaned)

            # Append sections from 'lists' (responsibilities, requirements, qualifications, etc.)
            for item in posting.get("lists", []):
                section_title = item.get("text", "").strip()
                section_content = clean_html_description(item.get("content", ""))
                if section_title and section_content:
                    description_parts.append(f"{section_title}:\n{section_content}")
                elif section_content:
                    description_parts.append(section_content)

            full_description = "\n\n".join(description_parts).strip()
            if not full_description:
                continue

            source_url = posting.get("hostedUrl") or posting.get("applyUrl") or f"https://jobs.lever.co/{company_site}/{posting.get('id')}"

            # Extract location and commitment (e.g. Full-time, Internship)
            categories = posting.get("categories", {})
            location_name = categories.get("location") if isinstance(categories, dict) else None
            employment_type = categories.get("commitment") if isinstance(categories, dict) else None

            # Parse posted_at date from epoch milliseconds
            posted_at = None
            created_at_ms = posting.get("createdAt")
            if created_at_ms and isinstance(created_at_ms, (int, float)):
                try:
                    posted_at = datetime.fromtimestamp(created_at_ms / 1000, tz=timezone.utc)
                except Exception:
                    posted_at = None

            # Calculate content hash for deduplication
            content_hash = hashlib.sha256(f"{source_url}:{full_description}".encode("utf-8")).hexdigest()

            normalized = NormalizedJob(
                employer_name=company_name,
                job_title=title,
                source_name=self.source_name,
                source_url=source_url,
                source_type=self.source_type,
                description_text=full_description,
                location=location_name,
                employment_type=employment_type,
                posted_at=posted_at,
                fetched_at=now,
                content_hash=content_hash,
                is_stale=False,
                verification_status="verified",
                verification_notes=notes,
            )
            matched_jobs.append(normalized)

        if not matched_jobs:
            return (
                "no_matching_jobs",
                f"Reviewed {len(data)} open postings at {company_name} on Lever, but none matched '{target_role}'.",
                [],
            )

        return (
            "verified_jobs_found",
            f"Found {len(matched_jobs)} verified job posting(s) for '{target_role}' at {company_name} on Lever.",
            matched_jobs,
        )
