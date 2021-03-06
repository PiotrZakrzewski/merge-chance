# merge-chance.info code
This is repo for the [merge-chance](https://merge-chance.info), page where you can checks success rate for your favorite open-source project on GitHub.

_if you just want to make some plots for given repo locally, use scripts from the `scripts` dir._

## Build & Setup

You will need a GitHub token, in order to extract data from GitHub [instructions](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token).

First setup a google cloud project and set following env vars:
```shell
export GCP_PROJECT=YOUR_PROJECT
export GCP_REGION=DESIRED_REGION
export GH_TOKEN=YOUR_GITHUB_TOKEN
```
Then create a service account with admin rights to your project's firestore. Save the json key to this service account as `key.json` in current dir.
Run the app locally with 
```shell
 gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 mergechance.main:app
```
Before first deploy to GCP run
```shell
./first_config.sh
```
in order to deploy it as a Cloud Run service on your GCP project run 
```shell
./build.sh
```
This will build the container with Cloud Build and deploy it.
