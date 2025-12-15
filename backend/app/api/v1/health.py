# backend/app/api/v1/health.py
# HEALTH CHECK ENDPOINTS FOR KUBERNETES AND MONITORING
# Provides comprehensive health checks for models, GPU, memory, and disk

from fastapi import APIRouter, status
from datetime import datetime
import psutil  # System monitoring (CPU, memory, disk)
import torch  # GPU availability detection
from typing import Dict, Any
import asyncio  # Parallel execution of health checks

router = APIRouter()

class HealthChecker:
    """
    Health check system for monitoring application status.
    
    Provides methods to check:
    - ML models loading status
    - GPU availability and memory
    - System memory usage
    - Disk space availability
    """
    
    @staticmethod
    async def check_model_loaded() -> Dict[str, Any]:
        """
        Verify that ML models are loaded and ready.
        
        Checks if the three critical models are in memory:
        - Classifier (BERT): Mental health condition detection
        - Summarizer (T5): Clinical summary generation
        - Generator (Llama): Treatment recommendations
        
        Returns:
            Dict with status and individual model loading state
        """
        try:
            from app.ml.models_loader import manager
            return {
                "status": "healthy" if manager.cls_model is not None else "unhealthy",
                "models_loaded": {
                    "classifier": manager.cls_model is not None,
                    "summarizer": manager.sum_pipeline is not None,
                    "generator": manager.gen_model is not None
                }
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    async def check_gpu() -> Dict[str, Any]:
        """
        Check GPU availability and memory usage.
        
        Detects three types of compute devices:
        - CUDA: NVIDIA GPUs (with memory info)
        - MPS: Apple Silicon GPUs (M1/M2/M3)
        - CPU: Fallback when no GPU is available
        
        Returns:
            Dict with device type, GPU name, and memory stats (if CUDA)
        """
        try:
            if torch.cuda.is_available():
                return {
                    "status": "healthy",
                    "device": "cuda",
                    "gpu_name": torch.cuda.get_device_name(0),
                    "gpu_memory": {
                        "allocated": f"{torch.cuda.memory_allocated(0) / 1e9:.2f} GB",
                        "cached": f"{torch.cuda.memory_reserved(0) / 1e9:.2f} GB"
                    }
                }
            elif torch.backends.mps.is_available():
                return {
                    "status": "healthy",
                    "device": "mps",
                    "gpu_name": "Apple Silicon"
                }
            else:
                return {
                    "status": "warning",
                    "device": "cpu",
                    "message": "Running on CPU - performance may be degraded"
                }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    async def check_memory() -> Dict[str, Any]:
        """
        Check system RAM usage.
        
        Monitors total, available, and used percentage of system memory.
        Issues a warning if memory usage exceeds 90%.
        
        Returns:
            Dict with memory stats in GB and usage percentage
        """
        try:
            memory = psutil.virtual_memory()
            return {
                "status": "healthy" if memory.percent < 90 else "warning",
                "total_gb": round(memory.total / 1e9, 2),
                "available_gb": round(memory.available / 1e9, 2),
                "used_percent": memory.percent
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    async def check_disk() -> Dict[str, Any]:
        """
        Check disk space availability.
        
        Monitors root filesystem usage.
        Issues a warning if disk usage exceeds 90%.
        
        Returns:
            Dict with disk stats in GB and usage percentage
        """
        try:
            disk = psutil.disk_usage('/')
            return {
                "status": "healthy" if disk.percent < 90 else "warning",
                "total_gb": round(disk.total / 1e9, 2),
                "free_gb": round(disk.free / 1e9, 2),
                "used_percent": disk.percent
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic health check - responds if the application is alive.
    
    This is the simplest health check, used by load balancers
    and monitoring systems to verify the service is running.
    
    Returns:
        Status, timestamp, and service name
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "clinical-assistant-api"
    }

@router.get("/health/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check():
    """
    Detailed health check with all system verifications.
    
    Runs comprehensive checks on:
    - ML models loading status
    - GPU availability and memory
    - System RAM usage
    - Disk space
    
    All checks run in parallel for faster response.
    
    Returns:
        Overall status (healthy/degraded/unhealthy) and individual check results
    """
    checker = HealthChecker()
    
    # Execute all checks in parallel for faster response
    models_check, gpu_check, memory_check, disk_check = await asyncio.gather(
        checker.check_model_loaded(),
        checker.check_gpu(),
        checker.check_memory(),
        checker.check_disk()
    )
    
    # Determine overall status based on individual checks
    all_statuses = [
        models_check.get("status"),
        gpu_check.get("status"),
        memory_check.get("status"),
        disk_check.get("status")
    ]
    
    # Priority: unhealthy > warning > healthy
    if "unhealthy" in all_statuses:
        overall_status = "unhealthy"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    elif "warning" in all_statuses:
        overall_status = "degraded"
        http_status = status.HTTP_200_OK
    else:
        overall_status = "healthy"
        http_status = status.HTTP_200_OK
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "models": models_check,
            "gpu": gpu_check,
            "memory": memory_check,
            "disk": disk_check
        },
        "uptime_seconds": psutil.Process().create_time()
    }

@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Kubernetes readiness probe - checks if the app can receive traffic.
    \n    Used by Kubernetes to determine if the pod should receive requests.
    If models are not loaded, the pod is marked as not ready and won't
    receive traffic until they are.
    \n    Returns:
        ready: True if models are loaded, False otherwise
    """
    checker = HealthChecker()
    models_status = await checker.check_model_loaded()
    
    if models_status.get("status") == "healthy":
        return {
            "ready": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    else:
        return {
            "ready": False,
            "reason": "Models not loaded",
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Kubernetes liveness probe - checks if the app should be restarted.
    \n    Used by Kubernetes to determine if the pod is stuck or deadlocked.
    If this endpoint stops responding, Kubernetes will restart the pod.
    \n    Returns:
        alive: Always True (if this endpoint responds, the app is alive)
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }
