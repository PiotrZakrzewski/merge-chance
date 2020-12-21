# How Likely Is Your OSS Contribution to Succeed
Use this script to calculate the proportion of PRs that get a response, get merged or rejected.

Requires python 3.6+
Prepare a venv
```shell
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

run the script
```shell
GH_TOKEN=YOUR_GH_TOKEN python get_pr_gql.py ORG/REPO
```
Make a score plot
```shell
python score.py org_repo.csv
```

## What is in the other directories?
- exploration contains a simple analysis of one repository
- gh-rest-api contains my old script for fetching the same data with REST-api (slooow)
