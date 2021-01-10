"""Module for calculating stats from data provided by gh_gql.py"""
from dateutil import parser
import time


STALE_THRESHOLD = 90 * 24 * 60 * 60  # 90 days in seconds

ANALYSIS_FIELDS = ["closedAt", "createdAt", "authorAssociation", "state"]


def median_time_to_merge(prs: list) -> float:
    pass


def merge_chance(prs: list) -> tuple:
    """Return a tuple of proportion of successful PRs and the amount of
    prs that were taken into consideration among those from the input.
    Open and not stale PRs are not valid and are ignored."""
    outsiders_prs = get_outsiders(prs)
    merged = get_merged(outsiders_prs)
    open = get_open(outsiders_prs)
    stale = get_stale(open)
    ignored = len(open) - len(stale)
    total = len(outsiders_prs) - ignored
    if not total:
        return None
    chance = len(merged) / total
    return chance, total


def get_merged(prs: list) -> list:
    return [pr for pr in prs if pr["state"] == "MERGED"]


def get_open(prs: list) -> list:
    return [pr for pr in prs if pr["state"] == "OPEN"]


def get_outsiders(prs: list) -> list:
    return [pr for pr in prs if _is_outsider(pr["authorAssociation"])]


def get_stale(prs: list) -> list:
    """Returns the PRs without stale PRs."""
    now = time.time()
    return [pr for pr in prs if _is_stale(pr, now)]


def _is_outsider(author: str):
    return author not in {"OWNER", "MEMBER"}


def _is_stale(pr, now):
    if pr["state"] != "OPEN":
        return False
    ts = pr["createdAt"]
    ts = parser.parse(ts).timestamp()
    return (now - ts) > STALE_THRESHOLD
