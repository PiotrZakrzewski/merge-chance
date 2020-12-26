import requests as rq
import os
import sys
from datetime import datetime
from dateutil import parser


TOKEN = os.getenv("GH_TOKEN")
STEP_SIZE = 100
GH_GQL_URL = "https://api.github.com/graphql"


def main():
    if not TOKEN:
        print("You need to set GH_TOKEN env var")
        sys.exit(1)
    if len(sys.argv) < 2:
        print(
            "Pass github repo name as first position argument.\n 'facebook/react' for example"
        )
        sys.exit(1)
    owner, repo = sys.argv[1].split('/')
    first_resp = first_query(owner, repo)
    total = first_resp["data"]["repository"]["pullRequests"]["totalCount"]
    has_next = first_resp["data"]["repository"]["pullRequests"]["pageInfo"][
        "hasNextPage"
    ]
    cursor = first_resp["data"]["repository"]["pullRequests"]["edges"][-1]["cursor"]
    print(f"Total PRs to process {total}.")
    rows = [["state", "created_at", "extracted_at", "author"]]
    to_csv(first_resp, rows)
    while has_next:
        progress = round(len(rows) / total * 100, 2)
        print(f"Processed {progress}% of the total ...")
        result = paginated_query(owner, repo, cursor)
        has_next = result["data"]["repository"]["pullRequests"]["pageInfo"][
            "hasNextPage"
        ]
        to_csv(result, rows)
        cursor = result["data"]["repository"]["pullRequests"]["edges"][-1]["cursor"]
    print("Done fetching")
    csv_name = f"{owner}_{repo}.csv"
    print(f"Will save results to {csv_name}")
    with open(csv_name, "w") as outfile:
        lines = [",".join(row) for row in rows]
        text = "\n".join(lines)
        outfile.write(text + "\n")


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


def to_csv(gql_result, rows: list):
    extracted_at = datetime.now().timestamp()
    for edge in gql_result["data"]["repository"]["pullRequests"]["edges"]:
        node = edge["node"]
        created_at = node["createdAt"]
        # parse to ts
        created_at = parser.parse(created_at).timestamp()
        author = node["authorAssociation"]
        row = [node["state"], str(created_at), str(extracted_at), author]
        rows.append(row)


if __name__ == "__main__":
    main()
