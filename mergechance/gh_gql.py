"""Module for handling GitHub's GraphQL API."""
from typing import List
import os
import logging
import requests as rq

log = logging.getLogger(__name__)

TOKEN = os.getenv("GH_TOKEN")
STEP_SIZE = 100  # 100 is Max
GH_GQL_URL = "https://api.github.com/graphql"


def get_pr_fields(org: str, repo: str, fields: List[str], page_cap=1, cursor=None) -> tuple:
    """Get specified GitHub PR fields.

    org - GitHub organization/users
    repo - GitHub repository
    fields - list of PR edge fields (See GitHub GraphQL docs)
    page_cap - how many pages (each 100 records) to fetch
    start_at - graphQl cursor to resume previous query
    """
    pages = 0
    has_next = True
    rows = []
    while has_next and pages < page_cap:
        result = _paginated_query(org, repo, cursor, fields)
        rows.extend(_to_rows(result))
        page_info = result["data"]["repository"]["pullRequests"]["pageInfo"]
        has_next = page_info["hasPreviousPage"]
        cursor = page_info["startCursor"]
        pages += 1
    return rows, cursor


def _to_rows(result: dict):
    rows = []
    for edge in result["data"]["repository"]["pullRequests"]["edges"]:
        rows.append(edge["node"])
    return rows


def _paginated_query(owner, repo, cursor, fields):
    fields = "\n".join(fields)
    cursor_part = f', before: "{cursor}"' if cursor else ""
    data = {
        "query": """
  query {
    repository(owner:"%s", name:"%s") {
      pullRequests(last: %s %s) {
        pageInfo {
          hasPreviousPage
          startCursor
        }
        edges {
          cursor
          node {
            timelineItems(last: 1 , itemTypes: CLOSED_EVENT) {
              edges {
                node {
                  ... on ClosedEvent {
                    actor{
                      login
                    }
                  }
                }
              }
            }
            author {
              login
            }
            %s
          }
        }
      }
    }
  }
  """
        % (owner, repo, STEP_SIZE, cursor_part, fields)
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
