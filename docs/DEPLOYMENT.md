# 🚀 Production Deployment Guide

Guía completa para desplegar Clinical Assistant en producción con seguridad, monitoring y CI/CD.

## 📋 Tabla de Contenidos

- [Preparación](#preparación)
- [Docker](#docker)
- [Kubernetes](#kubernetes)
- [CI/CD](#cicd)
- [Monitoring](#monitoring)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

---

## Preparación

### 1. Requisitos

**Software requerido:**
- Docker 24.0+
- Kubernetes 1.28+ (kubectl, minikube/kind para local)
- Helm 3.0+ (opcional, para instalar Prometheus/Grafana)
- GitHub account (para CI/CD)

**Hardware mínimo (producción):**
- CPU: 4 cores
- RAM: 8 GB (16 GB recomendado)
- GPU: NVIDIA T4 o superior (8GB VRAM)
- Storage: 100 GB SSD

### 2. Secrets

Crear archivo `k8s/secrets.yaml` (⚠️ NUNCA commitear):

```bash
# Generar JWT secrets
JWT_SECRET=$(openssl rand -hex 32)
JWT_REFRESH_SECRET=$(openssl rand -hex 32)

# Crear secret en Kubernetes
kubectl create namespace production

kubectl create secret generic clinical-assistant-secrets \
  --namespace=production \
  --from-literal=hf-token='YOUR_HUGGINGFACE_TOKEN_HERE' \
  --from-literal=jwt-secret="$JWT_SECRET" \
  --from-literal=jwt-refresh-secret="$JWT_REFRESH_SECRET"
```

---

## Docker

### Build Local

```bash
# Build imagen
docker build -t clinical-assistant:latest .

# Run localmente
docker run -p 8000:8000 \
  -e HF_TOKEN='your_huggingface_token_here' \
  clinical-assistant:latest
```

### Docker Compose (con Redis)

```bash
# Levantar todo el stack
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Parar
docker-compose down
```

### Push a Registry

```bash
# Login a GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag y push
docker tag clinical-assistant:latest ghcr.io/gortif00/clinical-assistant:latest
docker push ghcr.io/gortif00/clinical-assistant:latest
```

---

## Kubernetes

### 1. Setup Cluster

**Opción A: Minikube (local testing)**
```bash
minikube start --cpus=4 --memory=8192 --driver=docker
minikube addons enable ingress
minikube addons enable metrics-server
```

**Opción B: Cloud (GKE, EKS, AKS)**
```bash
# Ejemplo GKE
gcloud container clusters create clinical-assistant \
  --zone=us-central1-a \
  --num-nodes=3 \
  --machine-type=n1-standard-4 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10 \
  --addons=HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver
```

### 2. Deploy Application

```bash
# Crear namespace
kubectl create namespace production

# Aplicar secrets (ver sección Preparación)
kubectl apply -f k8s/secrets.yaml

# Aplicar ConfigMap
kubectl apply -f k8s/configmap.yaml

# Deploy Redis (para rate limiting)
kubectl apply -f k8s/redis-deployment.yaml

# Deploy aplicación
kubectl apply -f k8s/deployment.yaml

# Aplicar Ingress
kubectl apply -f k8s/ingress.yaml
```

### 3. Verificar Deployment

```bash
# Check pods
kubectl get pods -n production

# Logs de un pod
kubectl logs -n production deployment/clinical-assistant -f

# Health check
kubectl exec -n production deployment/clinical-assistant -- curl localhost:8000/api/v1/health

# Port forward para testing local
kubectl port-forward -n production service/clinical-assistant-service 8000:80
```

### 4. Setup Autoscaling

El HPA ya está configurado en `k8s/deployment.yaml`:
- Min replicas: 3
- Max replicas: 10
- Target CPU: 70%
- Target Memory: 80%

```bash
# Ver status del HPA
kubectl get hpa -n production

# Detalles
kubectl describe hpa clinical-assistant-hpa -n production
```

---

## CI/CD

### 1. GitHub Actions Setup

El workflow `.github/workflows/ci-cd.yml` ya está configurado. Necesitas añadir estos **secrets** en GitHub:

**GitHub Repository → Settings → Secrets → Actions:**

| Secret Name | Description | Value |
|------------|-------------|-------|
| `HF_TOKEN` | HuggingFace token | `your_huggingface_token_here` |
| `GHCR_TOKEN` | GitHub token para GHCR | Tu Personal Access Token |
| `KUBECONFIG` | Kubernetes config | Base64 de tu `~/.kube/config` |
| `CODECOV_TOKEN` | Coverage reports | Token de Codecov |
| `SLACK_WEBHOOK` | Notificaciones | Webhook URL de Slack |

**Crear GHCR token:**
```bash
# GitHub → Settings → Developer settings → Personal access tokens
# Scopes: write:packages, read:packages, delete:packages
```

**Encode kubeconfig:**
```bash
cat ~/.kube/config | base64 | pbcopy
```

### 2. Pipeline Workflow

El pipeline se ejecuta automáticamente en:
- Push a `main` branch
- Pull requests
- Tags `v*` (releases)

**Stages:**
1. **Test** (5-10 min)
   - Linting (flake8, black)
   - Type checking (mypy)
   - Unit tests (pytest)
   - Coverage upload (Codecov)

2. **Security** (3-5 min)
   - Trivy vulnerability scan
   - Safety dependency check
   - Bandit code security

3. **Build** (10-15 min)
   - Docker build multi-platform
   - Push to GHCR
   - Tag: `latest`, `sha-XXXXXX`, `v1.0.0`

4. **Deploy** (5 min)
   - Update K8s deployment
   - Rolling update
   - Slack notification

### 3. Manual Trigger

```bash
# Desde GitHub UI: Actions → CI/CD Pipeline → Run workflow

# O usando gh CLI
gh workflow run ci-cd.yml
```

---

## Monitoring

### 1. Deploy Prometheus + Grafana

**Opción A: Helm (recomendado)**
```bash
# Añadir repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus + Grafana stack
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

# Acceder a Grafana
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
# User: admin, Password: prom-operator
```

**Opción B: Manual**
```bash
kubectl create namespace monitoring
kubectl apply -f k8s/prometheus-config.yaml
```

### 2. Importar Dashboard en Grafana

1. Abrir Grafana: http://localhost:3000
2. Login (admin/prom-operator)
3. Dashboards → Import
4. Copiar contenido de `k8s/grafana-dashboard.json`
5. Paste JSON → Load → Import

### 3. Alertas

Configurar alerts en Prometheus para:

```yaml
# Ejemplo: High error rate
- alert: HighErrorRate
  expr: rate(errors_total[5m]) > 0.05
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High error rate detected"
    description: "Error rate is {{ $value }} errors/sec"

# Ejemplo: Pod Down
- alert: PodDown
  expr: up{job="clinical-assistant"} == 0
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "Pod is down"
```

### 4. Métricas Importantes

**Application Metrics:**
- `http_requests_total` - Total requests
- `http_request_duration_seconds` - Request latency
- `model_inference_duration_seconds` - ML inference time
- `errors_total` - Error count

**System Metrics:**
- `container_memory_usage_bytes` - Memory usage
- `container_cpu_usage_seconds_total` - CPU usage
- `kube_pod_container_status_restarts_total` - Restart count

**Queries útiles:**
```promql
# Request rate (RPS)
rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(errors_total[5m]) / rate(http_requests_total[5m])

# Memory per pod
sum by (pod) (container_memory_usage_bytes{namespace="production"})
```

---

## Security

### 1. HTTPS con Cert-Manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Crear ClusterIssuer para Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

El Ingress ya está configurado para usar cert-manager (ver `k8s/ingress.yaml`).

### 2. Network Policies

Limitar tráfico entre pods:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: clinical-assistant
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 53  # DNS
    - protocol: UDP
      port: 53
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

### 3. Pod Security Standards

```bash
# Enforce restricted security
kubectl label namespace production \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted
```

### 4. Secrets Management

**Opción A: Sealed Secrets**
```bash
# Install
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Encrypt secret
kubeseal --format yaml < secret.yaml > sealed-secret.yaml
kubectl apply -f sealed-secret.yaml
```

**Opción B: External Secrets Operator**
Usar AWS Secrets Manager, Azure Key Vault, etc.

---

## Troubleshooting

### Pod no inicia

```bash
# Ver eventos
kubectl describe pod -n production <pod-name>

# Logs
kubectl logs -n production <pod-name> --previous

# Shell en pod
kubectl exec -it -n production <pod-name> -- /bin/bash
```

### Problemas de memoria

```bash
# Ver uso actual
kubectl top pods -n production

# Aumentar limits
kubectl patch deployment clinical-assistant -n production -p \
  '{"spec":{"template":{"spec":{"containers":[{"name":"api","resources":{"limits":{"memory":"16Gi"}}}]}}}}'
```

### Health checks fallando

```bash
# Test manual
kubectl exec -n production deployment/clinical-assistant -- \
  curl -f http://localhost:8000/api/v1/health/ready

# Ver logs del health check
kubectl logs -n production <pod-name> | grep health
```

### Rate limiting issues

```bash
# Check Redis
kubectl exec -n production deployment/redis -- redis-cli ping

# Ver rate limit logs
kubectl logs -n production <pod-name> | grep "rate limit"
```

### GPU no detectada

```bash
# Verificar GPU disponible
kubectl describe node | grep -A 5 "Allocated resources"

# Check NVIDIA device plugin
kubectl get pods -n kube-system | grep nvidia
```

### Debugging CI/CD

```bash
# Ver workflow runs
gh run list

# Logs de un run
gh run view <run-id> --log

# Re-run failed jobs
gh run rerun <run-id>
```

---

## 🎯 Checklist Pre-Production

- [ ] Secrets configurados en K8s y GitHub
- [ ] SSL/TLS con Let's Encrypt
- [ ] Health checks configurados correctamente
- [ ] HPA testado con carga
- [ ] Monitoring y alertas activas
- [ ] Logs centralizados (ELK, Loki, etc.)
- [ ] Backups configurados (modelos, configs)
- [ ] Rate limiting testado
- [ ] CI/CD pipeline pasando
- [ ] Network policies aplicadas
- [ ] Pod security standards enforced
- [ ] Disaster recovery plan documentado

---

## 📚 Referencias

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Prometheus Operator](https://prometheus-operator.dev/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Cert-Manager Docs](https://cert-manager.io/docs/)

---

## 🆘 Soporte

Para issues y bugs: https://github.com/gortif00/clinical_assistant/issues
