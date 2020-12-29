from flask import Flask, request
import requests as rq
import os
import sys
from datetime import datetime
from google.cloud import bigquery
import base64

bq_client = bigquery.Client(location="EU")

app = Flask(__name__)

TOKEN = os.getenv("GH_TOKEN")
STEP_SIZE = 100
GH_GQL_URL = "https://api.github.com/graphql"


@app.route("/", methods=["POST"])
def index():
    if not TOKEN:
        print("You need to set GH_TOKEN env var")
        sys.exit(1)
    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400
    target_repo = base64.b64decode(envelope["message"]["data"]).decode("utf-8").strip()
    if "/" not in target_repo:
        return f"Bad Request: msg must be org/repo", 400
    owner, repo = target_repo.split("/")
    first_resp = first_query(owner, repo)
    total = first_resp["data"]["repository"]["pullRequests"]["totalCount"]
    has_next = first_resp["data"]["repository"]["pullRequests"]["pageInfo"][
        "hasNextPage"
    ]
    cursor = first_resp["data"]["repository"]["pullRequests"]["edges"][-1]["cursor"]
    print(f"Repo: {target_repo}. Total PRs to process {total}.")
    to_bigquery(first_resp, owner, repo)
    while has_next:
        result = paginated_query(owner, repo, cursor)
        has_next = result["data"]["repository"]["pullRequests"]["pageInfo"][
            "hasNextPage"
        ]
        to_bigquery(result, owner, repo)
        cursor = result["data"]["repository"]["pullRequests"]["edges"][-1]["cursor"]
    print(f"Done fetching {target_repo}")
    return ("", 204)


def first_query(owner, repo):
    data = {
        "query": """
  query {
    repository(owner:"%s", name:"%s") {
      pullRequests(first: %s) {
        totalCount
        pageInfo {
          hasNextPage
        }
        edges {
          cursor
          node {
            state
            createdAt
            authorAssociation
            closedAt
            number
          }
        }
      }
    }
  }
  """
        % (owner, repo, STEP_SIZE)
    }
    return gql_request(data)


def paginated_query(owner, repo, cursor):
    data = {
        "query": """
  query {
    repository(owner:"%s", name:"%s") {
      pullRequests(first: %s, after: "%s") {
        totalCount
        pageInfo {
          hasNextPage
        }
        edges {
          cursor
          node {
            state
            createdAt
            authorAssociation
            closedAt
            number
          }
        }
      }
    }
  }
  """
        % (owner, repo, STEP_SIZE, cursor)
    }
    return gql_request(data)


def gql_request(data):
    headers = {"Authorization": f"bearer {TOKEN}"}
    res = rq.post(GH_GQL_URL, headers=headers, json=data)
    return res.json()


def to_bigquery(gql_result, owner: str, repo: str):
    rows = []
    extracted_at = datetime.now().isoformat()
    for edge in gql_result["data"]["repository"]["pullRequests"]["edges"]:
        node = edge["node"]
        author = node["authorAssociation"]
        record = {
            "state": node["state"],
            "created_at": node["createdAt"],
            "extracted_at": extracted_at,
            "author": author,
            "org": owner,
            "repo": repo,
            "closed_at": node["closedAt"],
            "number": node["number"],
        }
        rows.append(record)
    bq_client.insert_rows_json("GitHub.PRs", rows)
