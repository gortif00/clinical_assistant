#!/bin/bash

# Clinical Mental Health Assistant - Docker Build and Deploy
# Builds Docker image and optionally pushes to registry

set -e

echo "🐳 Docker Build & Deploy Script"
echo "================================"
echo ""

cd "$(dirname "$0")/.."

# Configuration
IMAGE_NAME="${IMAGE_NAME:-clinical-assistant}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-}"
PUSH="${PUSH:-false}"

# Build image
echo "📦 Building Docker image: $IMAGE_NAME:$IMAGE_TAG"
docker build \
    -f deployment/Dockerfile \
    -t $IMAGE_NAME:$IMAGE_TAG \
    .

echo "✅ Image built successfully"
echo ""

# Tag for registry if specified
if [ -n "$REGISTRY" ]; then
    FULL_IMAGE="$REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
    echo "🏷️  Tagging image: $FULL_IMAGE"
    docker tag $IMAGE_NAME:$IMAGE_TAG $FULL_IMAGE
    
    # Push if requested
    if [ "$PUSH" = "true" ]; then
        echo "📤 Pushing to registry..."
        docker push $FULL_IMAGE
        echo "✅ Image pushed to registry"
    fi
fi

echo ""
echo "=============================="
echo "✅ Build complete!"
echo ""
echo "Run locally:"
echo "  docker run -p 8000:8000 --env-file .env $IMAGE_NAME:$IMAGE_TAG"
echo ""
echo "Or use docker-compose:"
echo "  docker-compose -f deployment/docker-compose.yml up"
