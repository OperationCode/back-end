#!/bin/sh -ex

# Usage: ./docker-build.sh [tag]
# Examples:
#   ./docker-build.sh           # Uses default tag 'latest' (creates multi-arch manifest)
#   ./docker-build.sh staging   # Creates :staging-amd64, :staging-arm64, and :staging manifest
#   ./docker-build.sh v1.2.3    # Creates :v1.2.3-amd64, :v1.2.3-arm64, and :v1.2.3 manifest

# Configuration
AWS_REGION=${AWS_REGION:-us-east-2}
ECR_REPO="633607774026.dkr.ecr.${AWS_REGION}.amazonaws.com/back-end"
TAG=${1:-latest}

echo "Building and pushing with tag: ${TAG}"
echo "ECR Repository: ${ECR_REPO}"

# Refresh AWS ECR login
echo "Refreshing AWS ECR login for region ${AWS_REGION}..."
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin 633607774026.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build and push AMD64 image using buildx with provenance disabled
docker buildx build \
  --platform linux/amd64 \
  --tag ${ECR_REPO}:${TAG}-amd64 \
  --provenance=false \
  --push .

# Build and push ARM64 image using buildx with provenance disabled
docker buildx build \
  --platform linux/arm64 \
  --tag ${ECR_REPO}:${TAG}-arm64 \
  --provenance=false \
  --push .

# Remove existing manifest list if it exists
docker manifest rm ${ECR_REPO}:${TAG} || true

# Create manifest list
docker manifest create \
  ${ECR_REPO}:${TAG} \
  ${ECR_REPO}:${TAG}-amd64 \
  ${ECR_REPO}:${TAG}-arm64

docker manifest inspect ${ECR_REPO}:${TAG}

# Push the manifest
docker manifest push ${ECR_REPO}:${TAG}

echo ""
echo "Successfully pushed: ${ECR_REPO}:${TAG}"
