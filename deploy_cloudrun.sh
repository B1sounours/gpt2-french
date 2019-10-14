#!/bin/bash

echo -e "Warning!\nThis can take some time because of the size of images.\n"
for d in gpt2-models/*; do
    # Push images to GCR
    [ -f "$d" ] && continue 
    tag=$(echo "$d" | cut -d "/" -f2-)
    gcloud builds submit "$d" --tag "gcr.io/deep-learning-254808/$tag"
    
    # Create CloudRun services
    gcloud beta run deploy "$tag" \
        --image "gcr.io/deep-learning-254808/$tag" \
        --platform=managed \
        --allow-unauthenticated \
        --region=us-east1 \
        --concurrency=1 \
        --memory=2Gi
done
echo -e "\nDone!\nURLs of Cloud Run services:\n\n$(gcloud beta run services list --platform=managed | grep -Po 'https.?://\S+')"