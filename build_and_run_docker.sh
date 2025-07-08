#!/bin/bash

set -e
DOCKERFILE_PATH="rag/Dockerfile"
IMAGE_NAME="rav_rag"
HOST_PORT=8080
CONTAINER_PORT=8000

echo "Building Docker image..."
docker build \
  --platform linux/amd64 \
  -f "$DOCKERFILE_PATH" \
  -t "$IMAGE_NAME" \
  .

echo "Running Docker container..."
docker run \
  --rm \
  --env-file .env \
  -v "$(pwd)/gcloud-key.json:/key.json:ro" \
  -e GOOGLE_APPLICATION_CREDENTIALS=/key.json \
  -p ${HOST_PORT}:${CONTAINER_PORT} \
  "$IMAGE_NAME"

echo "Container started on http://localhost:${HOST_PORT}"
