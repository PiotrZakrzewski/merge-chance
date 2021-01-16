from mergechance.analysis import (
    get_merged,
    get_outsiders,
    get_stale,
    get_open,
    merge_chance,
    median_time_to_merge,
    get_implied_insiders
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
        "author": {
            "login": "author1"
        }
    }


@pytest.fixture()
def pr_closed_outsider():
    now = datetime.datetime.now().isoformat()
    return {
        "createdAt": now,
        "closedAt": now,
        "authorAssociation": None,
        "state": "CLOSED",
        "author": {
            "login": "author1"
        }
    }


@pytest.fixture()
def pr_merged_outsider():
    now = datetime.datetime.now().isoformat()
    return {
        "createdAt": now,
        "closedAt": now,
        "authorAssociation": None,
        "state": "MERGED",
        "author": {
            "login": "author1"
        }
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
        "author": {
            "login": "author1"
        }
    }


@pytest.fixture()
def pr_open_insider():
    now = datetime.datetime.now().isoformat()
    return {
        "createdAt": now,
        "closedAt": None,
        "authorAssociation": "MEMBER",
        "state": "OPEN",
        "author": {
            "login": "author1"
        }
    }


@pytest.fixture()
def pr_closed_insider():
    now = datetime.datetime.now().isoformat()
    return {
        "createdAt": now,
        "closedAt": now,
        "authorAssociation": "MEMBER",
        "state": "CLOSED",
        "author": {
            "login": "author1"
        }
    }


@pytest.fixture()
def pr_merged_insider():
    now = datetime.datetime.now().isoformat()
    return {
        "createdAt": now,
        "closedAt": now,
        "authorAssociation": "MEMBER",
        "state": "MERGED",
        "author": {
            "login": "author1"
        }
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
        "author": {
            "login": "author1"
        }
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

@pytest.fixture()
def pr_merged_1day():
    delta = datetime.timedelta(days=1)
    now =datetime.datetime.now()
    time_ago = now - delta
    return {
        "createdAt": time_ago.isoformat(),
        "closedAt": now.isoformat(),
        "authorAssociation": None,
        "state": "MERGED",
    }

@pytest.fixture()
def pr_merged_2day():
    delta = datetime.timedelta(days=2)
    now =datetime.datetime.now()
    time_ago = now - delta
    return {
        "createdAt": time_ago.isoformat(),
        "closedAt": now.isoformat(),
        "authorAssociation": None,
        "state": "MERGED",
    }

@pytest.fixture()
def pr_merged_3day():
    delta = datetime.timedelta(days=3)
    now =datetime.datetime.now()
    time_ago = now - delta
    return {
        "createdAt": time_ago.isoformat(),
        "closedAt": now.isoformat(),
        "authorAssociation": None,
        "state": "MERGED",
    }


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
    assert pytest.approx(chance, 0.1) == 33.3


def test_merge_chance_empty():
    res = merge_chance([])
    assert res is None


def test_median_time(pr_merged_1day, pr_merged_2day, pr_merged_3day):
    prs = [pr_merged_1day, pr_merged_1day, pr_merged_1day]
    med_t = median_time_to_merge(prs)
    assert pytest.approx(med_t, 0.1) == 1.0

    prs = [pr_merged_1day, pr_merged_2day, pr_merged_3day]
    med_t = median_time_to_merge(prs)
    assert pytest.approx(med_t, 0.1) == 2.0


def test_implied_insider(pr_merged_outsider):
    prs = [pr_merged_outsider] * 6
    implied = get_implied_insiders(prs)
    assert {'author1'} == implied
