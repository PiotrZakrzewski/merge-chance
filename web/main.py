from flask import Flask, request
import requests as rq
import os
import sys
import logging

app = Flask(__name__)

log = logging.getLogger(__name__)

TOKEN = os.getenv("GH_TOKEN")
STEP_SIZE = 100 # 100 is Max
GH_GQL_URL = "https://api.github.com/graphql"


@app.route("/", methods=["GET"])
def index():
    if not TOKEN:
        print("You need to set GH_TOKEN env var")
        sys.exit(1)
    target = request.args.get("repo")
    if not target or '/' not in target:
        return ("No such repository on GitHub", 404)
    owner, repo = target.split("/")
    total, outsiders, insiders = get_stats(owner, repo)
    
    return (f"total: {total}, outsiders: {outsiders}, insiders: {insiders}", 200)

def calc_chance(stats):
    """Returns total_merged taken into account, outsiders_merged and insiders_merged."""
    total, outsiders, insiders = 0,0,0
    for edge in stats["data"]["repository"]["pullRequests"]["edges"]:
        node = edge["node"]
        author = node["authorAssociation"]
        state = node["state"]
        if state == "OPEN":
            continue
        total += 1
        if state == "MERGED" and author in {'OWNER', 'MEMBER'}:
            insiders += 1
        elif state == "MERGED":
            outsiders += 1
    return total, outsiders, insiders


def get_stats(owner, repo):
    result = first_query(owner, repo)
    total, outsiders, insiders = calc_chance(result)
    has_next = result["data"]["repository"]["pullRequests"]["pageInfo"][
            "hasPreviousPage"
        ]
    while total < 100 and has_next:
        cursor = result["data"]["repository"]["pullRequests"]["pageInfo"][
            "startCursor"
        ]
        result = paginated_query(owner, repo, cursor)
        has_next = result["data"]["repository"]["pullRequests"]["pageInfo"][
            "hasPreviousPage"
        ]
        add_total, add_outsiders, add_insiders = calc_chance(result)
        total += add_total
        outsiders += add_outsiders
        insiders += add_insiders
    return total, outsiders, insiders  


def first_query(owner, repo):
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
          cursor
          node {
            state
            authorAssociation
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
      pullRequests(last: %s, before: "%s") {
        pageInfo {
          hasPreviousPage
          startCursor
        }
        edges {
          cursor
          node {
            state
            authorAssociation
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
