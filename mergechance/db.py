import time
from firebase_admin import credentials, firestore, initialize_app
import logging


TTL = 24 * 60 * 60  # A day in seconds

# Initialize Firestore DB
cred = credentials.Certificate("key.json")
default_app = initialize_app(cred)
db = firestore.client()
cache_ref = db.collection("cache")

log = logging.getLogger(__name__)


def autocomplete_list() -> list:
    """return list of last used repos."""
    data = (
        cache_ref.order_by("ts", direction=firestore.Query.DESCENDING).limit(500).get()
    )
    repo_names = [repo.to_dict()["name"] for repo in data]
    return repo_names


def escape_fb_key(repo_target):
    """GitHub repos contain '/' which is a path delimiter in firestore."""
    return repo_target.replace("/", "_")


def get_from_cache(repo):
    repo = escape_fb_key(repo)
    try:
        cached = cache_ref.document(repo).get().to_dict()
        if not cached:
            return None
        median = cached.get("median")
        if not median:
            return None
        age = time.time() - cached["ts"]
        if age < TTL:
            return cached.get("chance"), median, cached.get("total"), cached.get("prs", [])
        return None
    except Exception as e:
        log.critical(f"An error occured ruing retrieving cache: {e}")


def cache(repo, chance, median, total, prs):
    escaped_repo = escape_fb_key(repo)
    try:
        ts = time.time()
        cache_ref.document(escaped_repo).set(
            {"chance": chance, "ts": ts, "name": repo, "total": total, "median": median, "prs": prs}
        )
    except Exception as e:
        log.critical(f"An error occured during caching: {e}")
