#!/bin/sh -ex

# Usage: ./docker-build.sh [tag]
# Examples:
#   ./docker-build.sh           # Uses default tag 'latest'
#   ./docker-build.sh staging   # Creates :staging
#   ./docker-build.sh v1.2.3    # Creates :v1.2.3

# Configuration
AWS_REGION=${AWS_REGION:-us-east-2}
ECR_REPO="633607774026.dkr.ecr.${AWS_REGION}.amazonaws.com/back-end"
TAG=${1:-latest}

echo "Building and pushing ARM64 image with tag: ${TAG}"
echo "ECR Repository: ${ECR_REPO}"

# Refresh AWS ECR login
echo "Refreshing AWS ECR login for region ${AWS_REGION}..."
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin 633607774026.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build and push ARM64 image using buildx with provenance disabled
docker buildx build \
  --platform linux/arm64 \
  --tag ${ECR_REPO}:${TAG} \
  --provenance=false \
  --push .

echo ""
echo "Successfully pushed: ${ECR_REPO}:${TAG}"
