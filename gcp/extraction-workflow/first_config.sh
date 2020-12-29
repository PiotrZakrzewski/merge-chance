gcloud config set project $GCP_PROJECT
gcloud config set run/region $GCP_REGION
gcloud config set run/platform managed
gcloud pubsub topics create target-repos
gcloud projects add-iam-policy-binding $GCP_PROJECT \
     --member=serviceAccount:service-$GCP_NUMBER@gcp-sa-pubsub.iam.gserviceaccount.com \
     --role=roles/iam.serviceAccountTokenCreator
gcloud iam service-accounts create cloud-run-extract \
     --display-name "Cloud Run Extract"
gcloud run services add-iam-policy-binding extract \
   --member=serviceAccount:cloud-run-extract@$GCP_PROJECT.iam.gserviceaccount.com \
   --role=roles/run.invoker
gcloud pubsub subscriptions create extract-subscription --topic target-repos \
   --push-endpoint=$SERVICE_URL/ \
   --push-auth-service-account=cloud-run-extract@$GCP_PROJECT.iam.gserviceaccount.com
