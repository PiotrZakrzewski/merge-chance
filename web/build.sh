gcloud builds submit --tag gcr.io/$GCP_PROJECT/mergechance
gcloud run deploy mergechance --image gcr.io/$GCP_PROJECT/mergechance --update-env-vars GH_TOKEN=$GH_TOKEN
