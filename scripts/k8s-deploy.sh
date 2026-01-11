#!/bin/bash

# Clinical Mental Health Assistant - Kubernetes Deploy
# Deploys application to Kubernetes cluster

set -e

echo "☸️  Kubernetes Deployment Script"
echo "================================="
echo ""

cd "$(dirname "$0")/.."

# Configuration
NAMESPACE="${NAMESPACE:-production}"
KUBECTL="${KUBECTL:-kubectl}"

echo "📋 Deployment Configuration:"
echo "   Namespace: $NAMESPACE"
echo "   Kubectl: $KUBECTL"
echo ""

# Check if kubectl is available
if ! command -v $KUBECTL &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Create namespace if it doesn't exist
echo "1️⃣ Creating namespace (if needed)..."
$KUBECTL create namespace $NAMESPACE --dry-run=client -o yaml | $KUBECTL apply -f -
echo "✅ Namespace ready"
echo ""

# Apply secrets (if secrets file exists)
if [ -f "deployment/k8s/secrets.yaml" ]; then
    echo "2️⃣ Applying secrets..."
    $KUBECTL apply -f deployment/k8s/secrets.yaml -n $NAMESPACE
    echo "✅ Secrets applied"
else
    echo "⚠️  No secrets.yaml found (copy from secrets.yaml.example)"
fi
echo ""

# Apply configurations
echo "3️⃣ Applying configurations..."
$KUBECTL apply -f deployment/k8s/configmap.yaml -n $NAMESPACE
echo "✅ ConfigMap applied"
echo ""

# Deploy Redis
echo "4️⃣ Deploying Redis..."
$KUBECTL apply -f deployment/k8s/redis-deployment.yaml -n $NAMESPACE
echo "✅ Redis deployed"
echo ""

# Deploy application
echo "5️⃣ Deploying application..."
$KUBECTL apply -f deployment/k8s/deployment.yaml -n $NAMESPACE
echo "✅ Application deployed"
echo ""

# Setup ingress
echo "6️⃣ Setting up ingress..."
$KUBECTL apply -f deployment/k8s/ingress.yaml -n $NAMESPACE
echo "✅ Ingress configured"
echo ""

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
$KUBECTL rollout status deployment/clinical-assistant -n $NAMESPACE --timeout=5m
echo "✅ Deployment ready!"
echo ""

# Show status
echo "=============================="
echo "✅ Deployment complete!"
echo ""
echo "Check status:"
echo "  kubectl get pods -n $NAMESPACE"
echo "  kubectl get svc -n $NAMESPACE"
echo "  kubectl get ingress -n $NAMESPACE"
echo ""
echo "View logs:"
echo "  kubectl logs -f deployment/clinical-assistant -n $NAMESPACE"
