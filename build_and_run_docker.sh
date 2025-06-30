#!/bin/bash

set -e

echo "Building Docker image..."
docker build \
  -f rag_endpoint/Dockerfile \
  -t rav_endpoint \
  . \
  --platform linux/amd64

echo "Running Docker container..."
docker run \
  --rm \
  --env-file .env \
  -v "$(pwd)"/gcloud-key.json:/key.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/key.json \
  -p 8080:5000 \
  rav_endpoint

