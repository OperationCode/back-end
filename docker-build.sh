#!/bin/sh -ex

# Build and push AMD64 image using buildx with provenance disabled
docker buildx build \
  --platform linux/amd64 \
  --tag 633607774026.dkr.ecr.us-east-2.amazonaws.com/back-end:amd64 \
  --provenance=false \
  --push .

# Build and push ARM64 image using buildx with provenance disabled
docker buildx build \
  --platform linux/arm64 \
  --tag 633607774026.dkr.ecr.us-east-2.amazonaws.com/back-end:arm64 \
  --provenance=false \
  --push .

# Create manifest list
docker manifest create \
  633607774026.dkr.ecr.us-east-2.amazonaws.com/back-end \
  633607774026.dkr.ecr.us-east-2.amazonaws.com/back-end:amd64 \
  633607774026.dkr.ecr.us-east-2.amazonaws.com/back-end:arm64

docker manifest inspect 633607774026.dkr.ecr.us-east-2.amazonaws.com/back-end

# Push the manifest
docker manifest push 633607774026.dkr.ecr.us-east-2.amazonaws.com/back-end
