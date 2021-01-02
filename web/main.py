from flask import Flask, request, render_template, jsonify
import requests as rq
import os
import sys
import logging
import time
from firebase_admin import credentials, firestore, initialize_app


# Initialize Firestore DB
cred = credentials.Certificate("key.json")
default_app = initialize_app(cred)
db = firestore.client()
cache_ref = db.collection("cache")
app = Flask(__name__)

log = logging.getLogger(__name__)

TOKEN = os.getenv("GH_TOKEN")
STEP_SIZE = 100  # 100 is Max
GH_GQL_URL = "https://api.github.com/graphql"
TTL = 24 * 60 * 60  # A day in seconds


class GQLError(Exception):
    pass


def strip_url(target):
    exclude = 'github.com/'
    if exclude in target:
        pos = target.find(exclude) + len(exclude)
        target = target[pos:]
    return target


@app.route("/autocomplete", methods=["GET"])
def auto_complete():
    data = (
        cache_ref.order_by("ts", direction=firestore.Query.DESCENDING).limit(500).get()
    )
    repo_names = [repo.to_dict()["name"] for repo in data]
    return jsonify(repo_names)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


def _get_chance(target):
    if not target or "/" not in target:
        return None
    chance = get_from_cache(target)
    if chance:
        log.info(f"Retrieved {target} from cache")
    else:
        log.info(f"Retrieving {target} from GH API")
        owner, repo = target.split("/")
        try:
            _, succ, fail = get_stats(owner, repo)
        except GQLError:
            return None
        total = fail + succ
        if total == 0:
            return None
        chance = succ / total
        chance = chance * 100
        chance = round(chance, 2)
        cache(target, chance)
    return chance


@app.route("/target", methods=["GET"])
def target():
    if not TOKEN:
        print("You need to set GH_TOKEN env var")
        sys.exit(1)
    target = request.args.get("repo")
    if not target:
        return ("Invalid request", 400)
    target = target.lower()
    target = strip_url(target)
    chance = _get_chance(target)
    if chance is None:
        return (
            f"Could not calculate merge chance for this repo. It might not exist on GitHub or have zero PRs.",
            404,
        )
    return render_template("chance.html", chance=chance, repo=target)


@app.route("/badge", methods=["GET"])
def badge():
    if not TOKEN:
        print("You need to set GH_TOKEN env var")
        sys.exit(1)
    target = request.args.get("repo")
    if not target:
        return ("Invalid request", 400)
    target = target.lower()
    chance = _get_chance(target)
    if chance is None:
        return (
            f"Could not calculate merge chance for this repo. It might not exist on GitHub or have zero PRs.",
            404,
        )
    return jsonify(
        {"schemaVersion": 1, "label": "Merge Chance", "message": f"{chance}%"}
    )


def escape_fb_key(repo_target):
    return repo_target.replace("/", "_")


def get_from_cache(repo):
    repo = escape_fb_key(repo)
    try:
        cached = cache_ref.document(repo).get().to_dict()
        if not cached:
            return None
        age = time.time() - cached["ts"]
        if age < TTL:
            return cached["chance"]
        return None
    except Exception as e:
        log.critical(f"An error occured ruing retrieving cache: {e}")


def cache(repo, chance):
    escaped_repo = escape_fb_key(repo)
    try:
        ts = time.time()
        cache_ref.document(escaped_repo).set({"chance": chance, "ts": ts, "name": repo})
    except Exception as e:
        log.critical(f"An error occured during caching: {e}")


def calc_chance(stats):
    """Returns total_merged taken into account, outsiders_merged and insiders_merged."""
    total, out_s, out_f = 0, 0, 0
    for edge in stats["data"]["repository"]["pullRequests"]["edges"]:
        node = edge["node"]
        author = node["authorAssociation"]
        state = node["state"]
        if state == "OPEN":
            continue
        total += 1
        if author in {"OWNER", "MEMBER"}:
            continue
        if state == "MERGED":
            out_s += 1
        else:
            out_f += 1
    return total, out_s, out_f


def get_stats(owner, repo):
    result = first_query(owner, repo)
    total, succ, fail = calc_chance(result)
    has_next = result["data"]["repository"]["pullRequests"]["pageInfo"][
        "hasPreviousPage"
    ]
    while total < 100 and has_next:
        cursor = result["data"]["repository"]["pullRequests"]["pageInfo"]["startCursor"]
        result = paginated_query(owner, repo, cursor)
        has_next = result["data"]["repository"]["pullRequests"]["pageInfo"][
            "hasPreviousPage"
        ]
        add_total, add_succ, add_fail = calc_chance(result)
        total += add_total
        succ += add_succ
        fail += add_fail
    return total, succ, fail


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
    data = res.json()
    if "errors" in data:
        errs = data["errors"]
        log.critical(f"Failed GQL query with {errs}")
        raise GQLError()
    return data
