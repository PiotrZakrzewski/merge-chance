from mergechance.analysis import (
    get_merged,
    get_outsiders,
    get_stale,
    get_open,
    merge_chance,
)

import datetime

import pytest


@pytest.fixture()
def pr_open_outsider():
    now = datetime.datetime.now().isoformat()
    return {
        "createdAt": now,
        "closedAt": None,
        "authorAssociation": None,
        "state": "OPEN",
    }


@pytest.fixture()
def pr_closed_outsider():
    now = datetime.datetime.now().isoformat()
    return {
        "createdAt": now,
        "closedAt": now,
        "authorAssociation": None,
        "state": "CLOSED",
    }


@pytest.fixture()
def pr_merged_outsider():
    now = datetime.datetime.now().isoformat()
    return {
        "createdAt": now,
        "closedAt": now,
        "authorAssociation": None,
        "state": "MERGED",
    }


@pytest.fixture()
def pr_open_outsider_stale():
    delta = datetime.timedelta(days=91)
    long_time_ago = datetime.datetime.now() - delta
    return {
        "createdAt": long_time_ago.isoformat(),
        "closedAt": None,
        "authorAssociation": None,
        "state": "OPEN",
    }


@pytest.fixture()
def pr_open_insider():
    now = datetime.datetime.now().isoformat()
    return {
        "createdAt": now,
        "closedAt": None,
        "authorAssociation": "MEMBER",
        "state": "OPEN",
    }


@pytest.fixture()
def pr_closed_insider():
    now = datetime.datetime.now().isoformat()
    return {
        "createdAt": now,
        "closedAt": now,
        "authorAssociation": "MEMBER",
        "state": "CLOSED",
    }


@pytest.fixture()
def pr_merged_insider():
    now = datetime.datetime.now().isoformat()
    return {
        "createdAt": now,
        "closedAt": now,
        "authorAssociation": "MEMBER",
        "state": "MERGED",
    }


@pytest.fixture()
def pr_open_insider_stale():
    delta = datetime.timedelta(days=91)
    long_time_ago = datetime.datetime.now() - delta
    return {
        "createdAt": long_time_ago.isoformat(),
        "closedAt": None,
        "authorAssociation": "MEMBER",
        "state": "OPEN",
    }


@pytest.fixture()
def prs(
    pr_open_outsider,
    pr_closed_outsider,
    pr_merged_outsider,
    pr_open_outsider_stale,
    pr_open_insider,
    pr_closed_insider,
    pr_merged_insider,
    pr_open_insider_stale,
):
    return [
        pr_open_outsider,
        pr_closed_outsider,
        pr_merged_outsider,
        pr_open_outsider_stale,
        pr_open_insider,
        pr_closed_insider,
        pr_merged_insider,
        pr_open_insider_stale,
    ]


def test_get_merged(prs):
    merged = get_merged(prs)
    assert len(prs) == 8
    assert len(merged) == 2


def test_get_stale(prs):
    stale = get_stale(prs)
    assert len(prs) == 8
    assert len(stale) == 2


def test_get_open(prs):
    open = get_open(prs)
    assert len(prs) == 8
    assert len(open) == 4


def test_get_outsiders(prs):
    out = get_outsiders(prs)
    assert len(prs) == 8
    assert len(out) == 4


def test_merge_chance(prs):
    chance, total = merge_chance(prs)
    assert total == 3
    assert pytest.approx(chance, 0.1) == 0.33


def test_merge_chance_empty():
    res = merge_chance([])
    assert res is None
