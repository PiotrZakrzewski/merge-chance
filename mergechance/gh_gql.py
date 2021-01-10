"""Module for handling GitHub's GraphQL API."""
from typing import List
import os
import logging
import requests as rq

log = logging.getLogger(__name__)

TOKEN = os.getenv("GH_TOKEN")
STEP_SIZE = 100  # 100 is Max
GH_GQL_URL = "https://api.github.com/graphql"


def get_pr_fields(org: str, repo: str, fields: List[str], page_cap=3) -> List[dict]:
    result = _first_query(org, repo, fields)
    rows = _to_rows(result)
    page_info = result["data"]["repository"]["pullRequests"]["pageInfo"]
    has_next = page_info["hasPreviousPage"]
    cursor = page_info["startCursor"]
    pages = 1
    while has_next and pages < page_cap:
        result = _paginated_query(org, repo, cursor, fields)
        rows.extend(_to_rows(result))
        page_info = result["data"]["repository"]["pullRequests"]["pageInfo"]
        has_next = page_info["hasPreviousPage"]
        cursor = page_info["startCursor"]
        pages += 1
    return rows


def _to_rows(result: dict):
    rows = []
    for edge in result["data"]["repository"]["pullRequests"]["edges"]:
        rows.append(edge["node"])
    return rows


def _first_query(org: str, repo: str, fields: List[str]):
    fields = "\n".join(fields)
    data = {
        "query": """
  query {
    repository(owner:"%s", name:"%s") {
      pullRequests(last: %s) {
        pageInfo {
          hasPreviousPage
          startCursor
        }
        edges {
          node {
            %s
          }
        }
      }
    }
  }
  """
        % (org, repo, STEP_SIZE, fields)
    }
    return _gql_request(data)


def _paginated_query(owner, repo, cursor, fields):
    fields = "\n".join(fields)
    data = {
        "query": """
  query {
    repository(owner:"%s", name:"%s") {
      pullRequests(last: %s, before: "%s") {
        pageInfo {
          hasPreviousPage
          startCursor
        }
        edges {
          cursor
          node {
            %s
          }
        }
      }
    }
  }
  """
        % (owner, repo, STEP_SIZE, cursor, fields)
    }
    return _gql_request(data)


def _gql_request(data):
    headers = {"Authorization": f"bearer {TOKEN}"}
    res = rq.post(GH_GQL_URL, headers=headers, json=data)
    data = res.json()
    if "errors" in data:
        errs = data["errors"]
        log.critical(f"Failed GQL query with {errs}")
        raise GQLError()
    return data


class GQLError(Exception):
    pass
