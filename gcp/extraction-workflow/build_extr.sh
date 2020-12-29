gcloud builds submit --tag gcr.io/$GCP_PROJECT/extract
gcloud run deploy extract --image gcr.io/$GCP_PROJECT/extract --update-env-vars GH_TOKEN=$GH_TOKEN
