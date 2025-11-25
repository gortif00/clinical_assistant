# Docker Deployment Guide

## 🐳 Running with Docker

This guide covers containerized deployment using Docker and Docker Compose.

## Prerequisites

- Docker Desktop (Mac/Windows) or Docker Engine (Linux)
- Docker Compose
- 16GB+ RAM available for Docker
- Your trained models in `backend/models/`

## Quick Start

### 1. Build and Start Containers

```bash
# Build and start in detached mode
docker-compose up --build -d

# Or with logs visible
docker-compose up --build
```

### 2. Check Status

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 3. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Stop Containers

```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Configuration

### Environment Variables

Edit `.env` file:

```bash
# Hugging Face Authentication Token
HF_TOKEN=hf_your_token_here

# Optional: Use local Llama model
LLAMA_BASE_MODEL_PATH=/path/to/local/model
LLAMA_USE_LOCAL_FILES_ONLY=true

# Optional: Disable LoRA adapter
LLAMA_USE_ADAPTER=false
```

### Docker Compose Services

#### Backend Service
- **Port**: 8000
- **Models**: Mounted as volume from `./backend/models`
- **Health Check**: Checks API availability every 30s
- **Restart Policy**: Unless stopped manually

#### Frontend Service
- **Port**: 3000
- **Files**: Mounted as read-only volume
- **Depends On**: Backend service

## Important Notes

### GPU Limitations on macOS

⚠️ **Docker on macOS cannot access MPS (Apple Silicon GPU)**

Models will run on CPU inside containers, which is:
- ✅ **Stable** - No MPS compatibility issues
- ❌ **Slower** - 2-3x slower than MPS
- ✅ **Works** - All features functional

For GPU acceleration, run natively without Docker.

### Model Volume

Models are **mounted as volumes** (not copied into image) to:
- Keep image size small (~5GB vs ~8GB)
- Allow model updates without rebuilding
- Share models between containers

If you see "models not found" errors:
```bash
# Verify models exist
ls -la backend/models/*/

# Check volume mounts
docker-compose config
```

### First Run

First startup takes longer because:
1. Downloading base images (~2GB)
2. Installing Python packages (~3GB)
3. Loading models into memory (~5-10 minutes)

Subsequent runs are much faster (1-2 minutes).

## Build Options

### No Cache Build

Force complete rebuild:
```bash
docker-compose build --no-cache
docker-compose up
```

### Build Single Service

```bash
# Rebuild only backend
docker-compose build backend
docker-compose up -d backend

# Rebuild only frontend
docker-compose build frontend
docker-compose up -d frontend
```

## Troubleshooting

### "Port already in use"

```bash
# Find and kill process on port 8000
lsof -ti :8000 | xargs kill -9

# Or use different ports in docker-compose.yml
ports:
  - "8001:8000"  # Host:Container
```

### "Out of memory"

Increase Docker memory limit:
- Docker Desktop → Preferences → Resources
- Set memory to 16GB+ (32GB recommended)

### "Models not loading"

```bash
# Check if models directory is mounted correctly
docker-compose exec backend ls -la /app/backend/models/

# Check logs for detailed error
docker-compose logs backend | grep -i error
```

### "Cannot connect to backend"

```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Check if backend container is running
docker-compose ps backend

# Check backend logs
docker-compose logs backend --tail 50
```

## Advanced Configuration

### Custom Dockerfile

To modify the Docker image, edit `Dockerfile`:

```dockerfile
# Change base image
FROM python:3.11-slim

# Add system dependencies
RUN apt-get update && apt-get install -y \
    your-package \
    && rm -rf /var/lib/apt/lists/*

# Change Python version, etc.
```

### Docker Compose Overrides

Create `docker-compose.override.yml` for local changes:

```yaml
version: '3.8'

services:
  backend:
    environment:
      - DEBUG=true
    volumes:
      - ./custom-models:/app/backend/models
```

### Production Deployment

For production, consider:

1. **Use production WSGI server**:
```dockerfile
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

2. **Add reverse proxy** (nginx):
```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
```

3. **Enable HTTPS**:
```yaml
volumes:
  - ./ssl:/etc/nginx/ssl
```

4. **Add authentication**:
```python
# In FastAPI app
from fastapi.security import HTTPBearer
security = HTTPBearer()
```

5. **Configure CORS properly**:
```python
allow_origins=[
    "https://your-domain.com",
    "https://www.your-domain.com"
]
```

## Cloud Deployment

<!--
CLOUD DEPLOYMENT OVERVIEW:

Docker containers make it easy to deploy to any cloud provider.
This section covers the three major cloud platforms.

Important considerations:
- Models run on CPU in containers (no GPU acceleration)
- Need 16GB+ RAM for all models
- Consider using managed ML services for GPU support
- Set HF_TOKEN via secrets management (not environment variables)
- Use HTTPS with SSL certificates in production
- Add authentication/authorization
- Enable monitoring and logging

Cost estimates (approximate):
- GCP Cloud Run: $50-100/month (16GB RAM, CPU)
- AWS ECS Fargate: $60-120/month (4 vCPU, 16GB)
- Azure Container Instances: $50-100/month (4 CPU, 16GB)
- Add load balancer, storage, networking costs

For GPU support:
- GCP: Use Vertex AI or GKE with GPU nodes
- AWS: Use SageMaker or ECS with GPU instances
- Azure: Use Machine Learning or AKS with GPU nodes
-->

### Deploy to Google Cloud Run (GCP)

<!--
GOOGLE CLOUD RUN:

Pros:
- Fully managed, serverless
- Auto-scaling from 0 to N instances
- Pay per request (can scale to zero)
- Built-in load balancing
- Easy HTTPS setup

Cons:
- No GPU support
- Memory limit 32GB max
- Cold starts (2-5 minutes for model loading)
- Request timeout 60 minutes max

Best for: Low to medium traffic, cost-sensitive deployments
-->

```bash
# Prerequisites:
# 1. Install gcloud CLI: https://cloud.google.com/sdk/docs/install
# 2. Authenticate: gcloud auth login
# 3. Set project: gcloud config set project PROJECT-ID

# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/clinical-assistant

# Deploy to Cloud Run
gcloud run deploy clinical-assistant \
  --image gcr.io/PROJECT-ID/clinical-assistant \
  --platform managed \
  --region us-central1 \
  --memory 16Gi \
  --cpu 4 \
  --timeout 3600 \
  --concurrency 10 \
  --min-instances 0 \
  --max-instances 10 \
  --allow-unauthenticated \
  --set-env-vars HF_TOKEN=$HF_TOKEN

# Get the service URL
gcloud run services describe clinical-assistant --format='value(status.url)'

# Set up custom domain (optional)
gcloud run domain-mappings create \
  --service clinical-assistant \
  --domain your-domain.com
```

### Deploy to AWS ECS (Elastic Container Service)

<!--
AWS ECS:

Pros:
- Full AWS integration (RDS, S3, CloudWatch, etc.)
- Choice of EC2 (more control) or Fargate (serverless)
- Good for GPU if using EC2
- Flexible networking options

Cons:
- More complex setup than Cloud Run
- Requires understanding of AWS networking
- Higher minimum cost (always running)

Best for: Enterprise deployments, need AWS integration
-->

```bash
# Prerequisites:
# 1. Install AWS CLI: https://aws.amazon.com/cli/
# 2. Configure: aws configure
# 3. Create ECR repository

# Create ECR repository
aws ecr create-repository --repository-name clinical-assistant

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t clinical-assistant .
docker tag clinical-assistant:latest \
  AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/clinical-assistant:latest
docker push AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/clinical-assistant:latest

# Create ECS cluster (Fargate)
aws ecs create-cluster --cluster-name clinical-assistant-cluster

# Create task definition (save as task-definition.json)
cat > task-definition.json << EOF
{
  "family": "clinical-assistant",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "4096",
  "memory": "16384",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/clinical-assistant:latest",
      "portMappings": [{"containerPort": 8000}],
      "environment": [
        {"name": "HF_TOKEN", "value": "your-token"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/clinical-assistant",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service (requires VPC, subnets, security groups)
aws ecs create-service \
  --cluster clinical-assistant-cluster \
  --service-name clinical-assistant-service \
  --task-definition clinical-assistant \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"

# Set up Application Load Balancer (ALB) for HTTPS
# (Use AWS Console or CloudFormation for ALB setup)
```

### Deploy to Azure Container Instances

<!--
AZURE CONTAINER INSTANCES:

Pros:
- Simplest deployment (single command)
- Per-second billing
- Fast startup
- Good Azure integration

Cons:
- No auto-scaling
- No load balancing (single container)
- Manual restart if crashed
- Limited to single container group

Best for: Development, testing, low-traffic applications
-->

```bash
# Prerequisites:
# 1. Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
# 2. Login: az login

# Create resource group
az group create --name clinical-assistant-rg --location eastus

# Create container registry (ACR)
az acr create \
  --resource-group clinical-assistant-rg \
  --name clinicalassistantregistry \
  --sku Basic

# Login to ACR
az acr login --name clinicalassistantregistry

# Build and push
docker build -t clinical-assistant .
docker tag clinical-assistant clinicalassistantregistry.azurecr.io/clinical-assistant:latest
docker push clinicalassistantregistry.azurecr.io/clinical-assistant:latest

# Deploy to Azure Container Instances
az container create \
  --resource-group clinical-assistant-rg \
  --name clinical-assistant \
  --image clinicalassistantregistry.azurecr.io/clinical-assistant:latest \
  --cpu 4 \
  --memory 16 \
  --ports 8000 \
  --dns-name-label clinical-assistant-unique \
  --environment-variables HF_TOKEN=$HF_TOKEN \
  --registry-login-server clinicalassistantregistry.azurecr.io \
  --registry-username $(az acr credential show --name clinicalassistantregistry --query username -o tsv) \
  --registry-password $(az acr credential show --name clinicalassistantregistry --query passwords[0].value -o tsv)

# Get the public URL
az container show \
  --resource-group clinical-assistant-rg \
  --name clinical-assistant \
  --query ipAddress.fqdn \
  --output tsv

# View logs
az container logs \
  --resource-group clinical-assistant-rg \
  --name clinical-assistant
```

### Deploy to DigitalOcean App Platform

<!--
DIGITALOCEAN APP PLATFORM:

Pros:
- Simple, developer-friendly
- Affordable pricing
- Auto-deploy from GitHub
- Built-in monitoring

Cons:
- Limited to 8GB RAM (may need optimization)
- No GPU support
- Smaller ecosystem than AWS/GCP/Azure

Best for: Indie developers, startups, simple deployments
-->

```bash
# Prerequisites:
# 1. Create DigitalOcean account
# 2. Install doctl: https://docs.digitalocean.com/reference/doctl/

# Create app spec file
cat > .do/app.yaml << EOF
name: clinical-assistant
services:
  - name: backend
    github:
      repo: your-username/clinical-assistant
      branch: main
    build_command: docker build -t backend .
    run_command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    envs:
      - key: HF_TOKEN
        value: your-token
        type: SECRET
    instance_count: 1
    instance_size_slug: professional-m
    http_port: 8000
    routes:
      - path: /
EOF

# Deploy via CLI
doctl apps create --spec .do/app.yaml

# Or deploy via web UI:
# 1. Push code to GitHub
# 2. Connect repo in DigitalOcean dashboard
# 3. Set environment variables
# 4. Deploy
```

## Monitoring

### View Resource Usage

```bash
# Real-time stats
docker stats

# Container-specific stats
docker stats clinical-assistant-backend
```

### Health Checks

```bash
# Manual health check
curl http://localhost:8000/api/v1/health

# Automated monitoring
watch -n 5 'curl -s http://localhost:8000/api/v1/health | jq'
```

## Cleanup

### Remove Containers and Images

```bash
# Stop and remove containers
docker-compose down

# Remove images
docker rmi clinical_assistant-backend
docker rmi clinical_assistant-frontend

# Remove all unused images
docker image prune -a

# Remove all unused volumes
docker volume prune
```

### Complete Cleanup

```bash
# Nuclear option: remove everything
docker-compose down -v --rmi all
docker system prune -a --volumes
```

## Performance Tips

1. **Use volume mounts** for models (not COPY in Dockerfile)
2. **Increase Docker memory** to 16GB+
3. **Use multi-stage builds** to reduce image size
4. **Cache Python packages** with BuildKit
5. **Run on GPU-enabled cloud** for better performance

## Security Checklist

<!--
PRODUCTION SECURITY:

This checklist ensures your deployment meets security best practices.
Complete BEFORE deploying to production with real patient data.

HIPAA/GDPR Compliance:
If handling real patient data, you need:
- BAA (Business Associate Agreement) with cloud provider
- End-to-end encryption
- Audit logging
- Access controls
- Data retention policies
- Incident response plan

This application is currently designed for RESEARCH/DEMO use only.
Significant additional work needed for clinical production use.
-->

### Essential Security (Do before production)
- [ ] **Change default ports** - Use reverse proxy (nginx) on 80/443
- [ ] **Add authentication** - JWT tokens, OAuth2, or API keys
- [ ] **Enable HTTPS** - Use Let's Encrypt or cloud provider SSL
- [ ] **CORS whitelist** - Only allow your domain, not wildcard
- [ ] **Secrets management** - Use AWS Secrets Manager, GCP Secret Manager, or Azure Key Vault
- [ ] **Rate limiting** - Prevent abuse (use nginx, CloudFlare, or FastAPI middleware)
- [ ] **Input validation** - Already implemented, but review for edge cases
- [ ] **Error handling** - Don't expose stack traces in production

### Monitoring & Logging
- [ ] **Request logging** - Log all API calls with timestamps
- [ ] **Error tracking** - Use Sentry, Rollbar, or CloudWatch
- [ ] **Performance monitoring** - Track response times, memory usage
- [ ] **Health checks** - Set up monitoring ping to /api/v1/health
- [ ] **Alerts** - Email/Slack alerts for errors or downtime

### Data Protection
- [ ] **Data encryption** - Encrypt data at rest and in transit
- [ ] **No PII in logs** - Sanitize patient data from logs
- [ ] **Data retention** - Automatically delete old analysis results
- [ ] **Backup strategy** - Regular backups of any stored data
- [ ] **Access logs** - Track who accessed what and when

### Compliance & Legal
- [ ] **Privacy policy** - Clear terms for data usage
- [ ] **User consent** - Explicit consent for AI-generated advice
- [ ] **Disclaimers** - "Not a substitute for professional medical advice"
- [ ] **Terms of service** - Legal protection for service provider
- [ ] **GDPR compliance** - If serving EU users (right to deletion, data portability)
- [ ] **HIPAA compliance** - If handling PHI in US (requires BAA, encryption, audits)

### Maintenance
- [ ] **Regular updates** - Keep dependencies updated for security patches
- [ ] **Vulnerability scanning** - Use Snyk, Dependabot, or similar
- [ ] **Penetration testing** - Annual security audits
- [ ] **Incident response plan** - What to do if breached
- [ ] **Disaster recovery** - Backup and restore procedures

---

## 📚 Additional Resources

### Documentation
- **Local Development**: [QUICKSTART.md](QUICKSTART.md) - 5-minute setup without Docker
- **Model Setup**: [MODEL_SETUP.md](MODEL_SETUP.md) - Copying models from Google Drive
- **Main README**: [README.md](README.md) - Complete project documentation
- **Implementation**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical details

### Useful Links
- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Hugging Face**: https://huggingface.co/docs
- **Transformers**: https://huggingface.co/docs/transformers/

### Community & Support
- **FastAPI GitHub**: https://github.com/tiangolo/fastapi
- **Transformers GitHub**: https://github.com/huggingface/transformers
- **Docker Forums**: https://forums.docker.com/

---

## 🎓 Learning Notes

<!--
DOCKER DEPLOYMENT LESSONS:

Key takeaways from this deployment setup:

1. Model Separation:
   - Models as volumes (not in image) = faster builds
   - Trade-off: Must ensure models exist on host

2. Multi-stage Builds:
   - Could optimize further with multi-stage Dockerfile
   - Build dependencies in one stage, copy artifacts to slim runtime

3. Health Checks:
   - Essential for production (load balancer needs them)
   - Set appropriate timeout (models take time to load)

4. Environment Variables:
   - Use .env for local, secrets manager for production
   - Never commit secrets to git

5. Networking:
   - Docker Compose handles networking automatically
   - In production, use reverse proxy (nginx, Traefik)

6. Resource Limits:
   - Set memory/CPU limits to prevent resource exhaustion
   - Monitor actual usage and adjust

7. Logging:
   - Container logs to stdout/stderr (Docker best practice)
   - Use logging driver for centralized logs

8. Graceful Shutdown:
   - Handle SIGTERM for graceful model cleanup
   - Important for preventing corruption

9. GPU in Docker:
   - Requires nvidia-docker on Linux
   - Not available on macOS Docker Desktop
   - Cloud solutions: Use GPU-enabled VMs or managed services

10. Scaling:
    - Horizontal scaling difficult (models large, load time)
    - Consider model serving frameworks (TorchServe, TF Serving)
    - Or managed solutions (SageMaker, Vertex AI)
-->

### Docker Best Practices Applied Here

✅ **Slim base image** (python:3.11-slim) - smaller attack surface  
✅ **Non-root user** - security (not implemented, add if needed)  
✅ **Health checks** - container orchestration support  
✅ **Environment variables** - configuration flexibility  
✅ **Volumes for data** - models separate from image  
✅ **.dockerignore** - faster builds, smaller context  
✅ **Multi-service with Compose** - development parity with production  
✅ **Explicit versions** - reproducible builds (python:3.11-slim, not :latest)  
✅ **Logs to stdout** - Docker-native logging  
✅ **Single concern** - one service per container  

### What Could Be Improved

🔄 **Multi-stage builds** - Reduce final image size further  
🔄 **Non-root user** - Run as non-privileged user  
🔄 **Secrets management** - Use Docker secrets instead of env vars  
🔄 **Resource limits** - Set CPU/memory limits in compose  
🔄 **Restart policies** - Handle crashes gracefully  
🔄 **Network isolation** - Don't expose backend directly  
🔄 **Image scanning** - Scan for vulnerabilities (Trivy, Snyk)  
🔄 **Caching optimization** - Better layer caching for dependencies  

---

## 🚀 Next Steps

After successful Docker deployment:

1. **Test thoroughly** - Run through all use cases
2. **Monitor performance** - Track memory, CPU, response times
3. **Set up CI/CD** - Automated testing and deployment
4. **Add authentication** - Protect your API
5. **Enable HTTPS** - Essential for production
6. **Configure backups** - Don't lose data
7. **Document runbooks** - Deployment procedures for team
8. **Plan for scale** - What happens at 10x traffic?

---

**For local development without Docker, see [QUICKSTART.md](QUICKSTART.md)**  
**For comprehensive project info, see [README.md](README.md)**
