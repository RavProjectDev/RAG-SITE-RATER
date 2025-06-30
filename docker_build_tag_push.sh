#!/bin/bash

set -e

IMAGE_NAME=rav_endpoint
REMOTE_IMAGE=ravprojectdev/rav_endpoint:latest

echo "Building Docker image..."
docker build \
  -f rag_endpoint/Dockerfile \
  -t ${IMAGE_NAME} \
  . \
  --platform linux/amd64

echo "Tagging image for Docker Hub..."
docker tag ${IMAGE_NAME} ${REMOTE_IMAGE}

echo "Pushing image to Docker Hub..."
docker push ${REMOTE_IMAGE}

echo "Done! Image pushed as ${REMOTE_IMAGE}"
