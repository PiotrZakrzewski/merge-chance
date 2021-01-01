# How Likely Is Your OSS Contribution to Succeed

__Check Merge Chance for a public GitHub Repo [here](https://merge-chance.info)__

Or use `get_pr_gql.py` script from this repo for more control and data.

Requires python 3.6+
Prepare a venv
```shell
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```
You will need a GitHub token, [instructions](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token).

run the script
```shell
GH_TOKEN=YOUR_GH_TOKEN python get_pr_gql.py ORG/REPO
```
Make a score plot
```shell
python score.py org_repo.csv
```
or if you want to plot only outsider contributions (author affiliation other than MEMBER or OWNER) do:
```shell
python score.py org_repo.csv --outsiders
```
## What is in the other directories?
- `web` merge-chance.info code
- `exploration` contains a simple analysis of one repository
- `gh-rest-api` contains my old script for fetching the same data with REST-api (slooow)
