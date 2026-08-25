"""
Oracle Taleo Jobs API: A Quick Start Example
See more at: https://apify.com/johnvc/oracle-taleo-jobs-api?fpr=9n7kx3
Input schema: https://apify.com/johnvc/oracle-taleo-jobs-api/input-schema?fpr=9n7kx3

This script shows how to call the Oracle Fusion Recruiting and Taleo Jobs API on
Apify from Python and read its structured JSON output: Oracle job postings with
titles, every location, ISO posted dates, requisition IDs, employer-published
skills, coordinates, pay ranges, and direct apply URLs. The default run exercises
several input parameters while staying cheap. The other recipes mirror the use
cases in the README.

Get your free Apify API key at: https://apify.com?fpr=9n7kx3

Examples:
  uv run python oracle-taleo-jobs-api-example.py
  uv run python oracle-taleo-jobs-api-example.py --example discover_sites
  uv run python oracle-taleo-jobs-api-example.py --example taleo_jobs
  uv run python oracle-taleo-jobs-api-example.py --example new_postings
  uv run python oracle-taleo-jobs-api-example.py --example markdown_for_agents
"""

from __future__ import annotations

import argparse
import os
from datetime import date, timedelta
from typing import Any

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

ACTOR_ID = "johnvc/oracle-taleo-jobs-api"


def _print_jobs(items: list[dict[str, Any]]) -> None:
    """Print a short summary of job rows.

    Args:
        items: Rows returned from the Actor's default dataset.
    """
    jobs = [i for i in items if i.get("resultType") == "job"]
    print(f"Returned {len(jobs)} job(s) out of {len(items)} row(s).\n")
    for item in jobs:
        salary = item.get("salaryText") or "no published range"
        print(
            f"- {item.get('title')} | {item.get('primaryLocation')} | "
            f"posted {item.get('postedDate')} | req {item.get('requisitionId')} | {salary}"
        )
        print(f"  {item.get('applyUrl') or item.get('url')}")
    _print_errors(items)


def _print_sites(items: list[dict[str, Any]]) -> None:
    """Print a short summary of career-site rows from discovery mode."""
    sites = [i for i in items if i.get("resultType") == "site"]
    print(f"Returned {len(sites)} career site(s) out of {len(items)} row(s).\n")
    for item in sites:
        print(
            f"- {item.get('company')} | tenant {item.get('tenant')} | "
            f"site {item.get('siteNumber')} ({item.get('siteName')}) | "
            f"{item.get('totalJobs')} open role(s) | {item.get('status')}"
        )
        print(f"  {item.get('careersUrl')}")
    _print_errors(items)


def _print_errors(items: list[dict[str, Any]]) -> None:
    """Surface labelled error rows. They are informational and are never charged."""
    errors = [i for i in items if i.get("errorMessage")]
    for item in errors:
        print(f"  note ({item.get('errorType')}): {item.get('errorMessage')}")


def _run(client: ApifyClient, run_input: dict[str, Any]) -> list[dict[str, Any]]:
    """Start the Actor, wait for it, and return every row from its dataset."""
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    if run is None:
        raise SystemExit("The Actor run did not return a result.")
    return list(client.dataset(run.default_dataset_id).iterate_items())


def run_default(client: ApifyClient) -> None:
    """Cheap general quick start against Oracle's own Fusion Recruiting board."""
    # Inputs are kept small (one board, 5 jobs) to keep this first run
    # inexpensive. Set maxJobsPerSite to 0 to pull every job on the site.
    run_input: dict[str, Any] = {
        "startUrls": [
            {"url": "https://eeho.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_45001"}
        ],
        "maxJobsPerSite": 5,
        "includeDetails": True,
        "descriptionFormat": "text",
    }
    _print_jobs(_run(client, run_input))


def run_discover_sites(client: ApifyClient) -> None:
    """Find every Oracle careers board a company runs, without a tenant code.

    Discovery mode returns one row per career site instead of jobs: company,
    tenant, host, siteNumber, siteName, careersUrl, apiUrl, and a live
    totalJobs count. This is the answer to "which companies run Oracle
    Recruiting Cloud, and which still run Taleo".
    """
    # Site rows are the cheapest thing this API returns, and verifyLive keeps
    # the backup and reference-only boards out of the result.
    run_input: dict[str, Any] = {
        "companies": ["Oracle"],
        "discoverOnly": True,
        "verifyLive": True,
        "includeInactive": False,
        "maxSites": 10,
    }
    _print_sites(_run(client, run_input))


def run_taleo_jobs(client: ApifyClient) -> None:
    """Read a public Oracle Taleo board with no login and no credentials.

    Taleo boards are older than Fusion Recruiting and plenty have been switched
    off by their owners. A retired board produces a clearly labelled error row
    rather than a failed run, and error rows are never charged.
    """
    run_input: dict[str, Any] = {
        "startUrls": [{"url": "https://uab.taleo.net/careersection/ext/jobsearch.ftl"}],
        "product": "taleo",
        "maxJobsPerSite": 10,
        "includeDetails": True,
    }
    _print_jobs(_run(client, run_input))


def run_new_postings(client: ApifyClient) -> None:
    """Return only Oracle job postings published in the last 14 days.

    Put this input on an Apify Schedule and diff on requisitionId to catch new
    roles the day they go live. postedAfter is most accurate with includeDetails
    on, because the exact posting timestamp lives on the detail record.
    """
    since = (date.today() - timedelta(days=14)).isoformat()
    run_input: dict[str, Any] = {
        "startUrls": [
            {"url": "https://eeho.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_45001"}
        ],
        "postedAfter": since,
        "includeDetails": True,
        "maxJobsPerSite": 25,
    }
    print(f"Looking for roles posted on or after {since}.\n")
    _print_jobs(_run(client, run_input))


def run_markdown_for_agents(client: ApifyClient) -> None:
    """Return job descriptions as Markdown, the format an AI agent wants.

    descriptionFormat "markdown" keeps headings, lists, and links intact instead
    of handing a model raw HTML or a flattened wall of text. The skills list and
    the coordinates come from the employer's own record, so there is nothing for
    a model to guess at.
    """
    run_input: dict[str, Any] = {
        "startUrls": [
            {"url": "https://eeho.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_45001"}
        ],
        "descriptionFormat": "markdown",
        "searchText": "engineer",
        "maxJobsPerSite": 3,
        "includeDetails": True,
        "detailConcurrency": 3,
    }
    items = _run(client, run_input)
    for item in items:
        if item.get("resultType") != "job":
            continue
        print(f"### {item.get('title')} ({item.get('primaryLocation')})")
        print(f"skills: {', '.join(item.get('skills') or []) or 'none published'}")
        print(f"coordinates: {item.get('latitude')}, {item.get('longitude')}")
        markdown = item.get("descriptionMarkdown") or ""
        print(markdown[:600] + ("..." if len(markdown) > 600 else ""))
        print()
    _print_errors(items)


EXAMPLES = {
    "default": run_default,
    "discover_sites": run_discover_sites,
    "taleo_jobs": run_taleo_jobs,
    "new_postings": run_new_postings,
    "markdown_for_agents": run_markdown_for_agents,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Oracle Taleo Jobs API examples")
    parser.add_argument("--example", choices=sorted(EXAMPLES), default="default")
    args = parser.parse_args()

    token = os.getenv("APIFY_API_TOKEN")
    if not token or token == "your_apify_api_token_here":
        raise SystemExit(
            "Set APIFY_API_TOKEN in .env first. "
            "Get a free key at https://apify.com?fpr=9n7kx3"
        )
    client = ApifyClient(token)
    EXAMPLES[args.example](client)


if __name__ == "__main__":
    main()
