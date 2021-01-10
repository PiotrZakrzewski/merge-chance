from flask import Flask, request, render_template, jsonify
import logging

from mergechance.db import autocomplete_list, get_from_cache, cache
from mergechance.gh_gql import get_pr_fields, GQLError
from mergechance.analysis import ANALYSIS_FIELDS, merge_chance, get_median_outsider_time

app = Flask(__name__)
log = logging.getLogger(__name__)


def sanitize_repo(target: str):
    """Sanitize user input (repo name)."""
    if not target:
        raise ValueError("Repo cannot be empty")
    target = target.lower()
    target = target.strip()
    target = _strip_url(target)
    # sometimes people copy paste from GitHub UI, which adds spaces in between
    # those can be safely removed, spaces are not allowed in GitHub repo names
    target = target.replace(" ", "")
    if target.count("/") != 1:
        raise ValueError("Invalid repo name. Must be in format: organization/name")
    return target


def _strip_url(target):
    """Target repo can be either a org/repo string or a full url."""
    exclude = "github.com/"
    if exclude in target:
        pos = target.find(exclude) + len(exclude)
        target = target[pos:]
    if target[-1] == "/":
        target = target[:-1]
    return target


def _get_chance(target):
    cached_chance = get_from_cache(target)
    if cached_chance:
        chance, median, total = cached_chance
        log.info(f"Retrieved {target} from cache")
    else:
        log.info(f"Retrieving {target} from GH API")
        # after sanitize_repo it is guaranteed to contain exactly one '/'
        owner, repo = target.split("/")
        try:
            prs = get_pr_fields(owner, repo, ANALYSIS_FIELDS)
        except GQLError:
            return None
        chance = merge_chance(prs)
        if not chance:
            return None
        chance, total = chance
        median = get_median_outsider_time(prs)
        cache(target, chance, median, total)
    return chance, median, total


@app.route("/autocomplete", methods=["GET"])
def auto_complete():
    """Endpoint for target repo autocomplete."""
    return jsonify(autocomplete_list())


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/target", methods=["GET"])
def target():
    target = request.args.get("repo")
    try:
        target = sanitize_repo(target)
    except ValueError:
        return ("Invalid repo name. Must be in format 'owner/name'.", 400)
    chance = _get_chance(target)
    if chance is None:
        return (
            f"Could not calculate merge chance for this repo. It might not exist on GitHub or have zero PRs.",
            404,
        )
    chance, median, total = chance
    return render_template("chance.html", chance=chance, repo=target, total=total, median=median)


@app.route("/badge", methods=["GET"])
def badge():
    target = request.args.get("repo")
    try:
        target = sanitize_repo(target)
    except ValueError:
        return ("Invalid repo name. Must be in format 'owner/name'.", 400)
    chance = _get_chance(target)
    if chance is None:
        return (
            f"Could not calculate merge chance for this repo. It might not exist on GitHub or have zero PRs.",
            404,
        )
    chance, median, _ = chance
    return jsonify(
        {"schemaVersion": 1, "label": "Merge Chance", "message": f"{chance}% after {median} days"}
    )
