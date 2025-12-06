# backend/app/api/v1/health.py
from fastapi import APIRouter, status
from datetime import datetime
import psutil
import torch
from typing import Dict, Any
import asyncio

router = APIRouter()

class HealthChecker:
    """Sistema de health checks"""
    
    @staticmethod
    async def check_model_loaded() -> Dict[str, Any]:
        """Verifica que los modelos estén cargados"""
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
        """Verifica disponibilidad de GPU"""
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
        """Verifica uso de memoria"""
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
        """Verifica espacio en disco"""
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
    """Health check básico - solo responde si la app está viva"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "clinical-assistant-api"
    }

@router.get("/health/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check():
    """Health check detallado con todas las verificaciones"""
    checker = HealthChecker()
    
    # Ejecutar todos los checks en paralelo
    models_check, gpu_check, memory_check, disk_check = await asyncio.gather(
        checker.check_model_loaded(),
        checker.check_gpu(),
        checker.check_memory(),
        checker.check_disk()
    )
    
    # Determinar estado general
    all_statuses = [
        models_check.get("status"),
        gpu_check.get("status"),
        memory_check.get("status"),
        disk_check.get("status")
    ]
    
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
    """Readiness probe - verifica si la app puede recibir tráfico"""
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
    """Liveness probe - verifica si la app debe ser reiniciada"""
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }
