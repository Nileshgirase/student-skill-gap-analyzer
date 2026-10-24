import hashlib
import html
import logging
import re
from datetime import datetime, timezone
from typing import Any
from bs4 import BeautifulSoup
import httpx

from app.connectors.base import BaseJobConnector, NormalizedJob

logger = logging.getLogger(__name__)


def clean_html_description(raw_html: str) -> str:
    """
    Decodes HTML entities, decomposes script/style elements, and strips HTML tags,
    returning clean readable text while preserving natural word boundaries.
    """
    if not raw_html:
        return ""
    unescaped = html.unescape(raw_html)
    soup = BeautifulSoup(unescaped, "html.parser")

    # Remove script and style elements if any exist
    for element in soup(["script", "style"]):
        element.decompose()

    # Insert spaces after block elements so inline elements are not severed by newlines
    for block in soup.find_all(["p", "div", "li", "br", "h1", "h2", "h3", "h4", "h5", "h6", "tr"]):
        block.append("\n")

    text = soup.get_text()
    # Clean up excessive blank lines while preserving paragraph spacing
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    non_empty_lines = [line for line in lines if line]
    return "\n".join(non_empty_lines)


def calculate_role_relevance(job_title: str, target_role: str) -> tuple[bool, str]:
    """
    Determines whether a job title is relevant to the target role using token and phrase matching.
    Returns (is_relevant, explanation).
    """
    norm_title = re.sub(r"[^a-z0-9\s]", " ", job_title.lower())
    norm_role = re.sub(r"[^a-z0-9\s]", " ", target_role.lower())

    # Exact normalized phrase match
    if norm_role in norm_title:
        return True, f"Exact phrase match: job title '{job_title}' contains '{target_role}'."

    # Token overlap check (ignoring common stop words)
    stop_words = {"and", "or", "the", "a", "an", "in", "for", "of", "to", "at", "with"}
    role_tokens = [w for w in norm_role.split() if w not in stop_words]
    title_tokens = set(norm_title.split())

    if not role_tokens:
        return False, "Target role does not contain valid keywords."

    matched_tokens = [w for w in role_tokens if w in title_tokens]
    match_ratio = len(matched_tokens) / len(role_tokens)

    # Require at least 70% of role tokens to appear in the title
    if match_ratio >= 0.7:
        return True, (
            f"Token match: {len(matched_tokens)}/{len(role_tokens)} keywords "
            f"matched ({', '.join(matched_tokens)}) in '{job_title}'."
        )

    return False, f"Job title '{job_title}' does not sufficiently match target role '{target_role}'."


class GreenhouseConnector(BaseJobConnector):
    """
    Connector for Greenhouse public ATS job boards.
    Queries official public board feeds (https://boards-api.greenhouse.io).
    """
    source_name = "Greenhouse"
    source_type = "public_ats_feed"
    base_api_url = "https://boards-api.greenhouse.io/v1/boards"

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

    def _derive_board_token(self, company_name: str) -> str:
        """
        Normalizes company name into Greenhouse board slug (lowercase alphanumeric with hyphens).
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
        Searches Greenhouse public jobs and returns (status, explanation_message, list[NormalizedJob]).
        Statuses align with system specification: verified_jobs_found, company_not_verified,
        no_matching_jobs, or source_unavailable.
        """
        board_token = self._derive_board_token(company_name)
        if not board_token:
            return "company_not_verified", "Company name is invalid or cannot be parsed.", []

        url = f"{self.base_api_url}/{board_token}/jobs?content=true"
        client = self._get_client()

        try:
            response = client.get(url)
            if response.status_code == 404:
                logger.info("Greenhouse board not found for token: %s", board_token)
                return (
                    "company_not_verified",
                    f"No public Greenhouse job board could be verified for '{company_name}'.",
                    [],
                )
            response.raise_for_status()
            data = response.json()
        except httpx.TimeoutException:
            logger.warning("Greenhouse request timed out for company: %s", company_name)
            return "source_unavailable", f"Connection to Greenhouse timed out while querying '{company_name}'.", []
        except httpx.HTTPStatusError as exc:
            logger.warning("Greenhouse HTTP error %s for company %s", exc.response.status_code, company_name)
            return "source_unavailable", f"Greenhouse returned an upstream HTTP {exc.response.status_code} error.", []
        except Exception as exc:
            logger.warning("Unexpected error querying Greenhouse for %s: %s", company_name, str(exc))
            return "source_unavailable", f"Source unavailable: {str(exc)}", []

        raw_jobs: list[dict[str, Any]] = data.get("jobs", [])
        if not raw_jobs:
            return "no_matching_jobs", f"No open positions are currently listed on {company_name}'s public board.", []

        matched_jobs: list[NormalizedJob] = []
        now = datetime.now(timezone.utc)

        for job in raw_jobs:
            title = job.get("title", "").strip()
            is_relevant, notes = calculate_role_relevance(title, target_role)
            if not is_relevant:
                continue

            raw_content = job.get("content", "")
            clean_text = clean_html_description(raw_content)

            # Skip posting if description is completely missing or empty
            if not clean_text:
                continue

            source_url = job.get("absolute_url") or f"https://boards.greenhouse.io/{board_token}/jobs/{job.get('id')}"
            location_info = job.get("location", {})
            location_name = location_info.get("name") if isinstance(location_info, dict) else str(location_info)

            # Parse posted_at / updated_at date if present
            posted_at = None
            if job.get("updated_at"):
                try:
                    posted_at = datetime.fromisoformat(job["updated_at"].replace("Z", "+00:00"))
                except Exception:
                    posted_at = None

            # Calculate content hash for deduplication
            content_hash = hashlib.sha256(f"{source_url}:{clean_text}".encode("utf-8")).hexdigest()

            normalized = NormalizedJob(
                employer_name=company_name,
                job_title=title,
                source_name=self.source_name,
                source_url=source_url,
                source_type=self.source_type,
                description_text=clean_text,
                location=location_name,
                employment_type=None,
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
                f"Reviewed {len(raw_jobs)} open postings at {company_name}, but none matched '{target_role}'.",
                [],
            )

        return (
            "verified_jobs_found",
            f"Found {len(matched_jobs)} verified job posting(s) for '{target_role}' at {company_name}.",
            matched_jobs,
        )
