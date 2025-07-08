#!/bin/bash

set -e

IMAGE_NAME=rag
REMOTE_IMAGE=ravprojectdev/rag:latest

echo "Building Docker image..."
docker build \
  -f rag/Dockerfile \
  -t ${IMAGE_NAME} \
  . \
  --platform linux/amd64

echo "Tagging image for Docker Hub..."
docker tag ${IMAGE_NAME} ${REMOTE_IMAGE}

echo "Pushing image to Docker Hub..."
docker push ${REMOTE_IMAGE}

echo "Done! Image pushed as ${REMOTE_IMAGE}"
