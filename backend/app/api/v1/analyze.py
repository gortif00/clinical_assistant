# backend/app/api/v1/analyze.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.ml.models_loader import manager, get_device
from app.core.config import MIN_TEXT_LENGTH

router = APIRouter(tags=["analysis"])


class CaseRequest(BaseModel):
    text: str = Field(..., min_length=MIN_TEXT_LENGTH, description="Patient clinical observations")
    auto_classify: bool = Field(default=True, description="Enable automatic classification")
    pathology: Optional[str] = Field(default=None, description="Manually selected pathology (if auto_classify is False)")


class CaseResponse(BaseModel):
    classification: dict
    summary: str
    recommendation: str
    metadata: dict


@router.get("/health")
def health_check():
    """Check if API and models are ready"""
    models_ready = manager.check_models_loaded()
    return {
        "status": "healthy" if models_ready else "degraded",
        "models_loaded": models_ready
    }


@router.get("/get_status")
def get_status():
    """Get execution device status (for frontend display)"""
    device = get_device()
    return {
        "status": "ok",
        "device": device
    }


@router.post("/analyze", response_model=CaseResponse)
def analyze_case(data: CaseRequest):
    """
    Analyze a clinical case and generate treatment recommendations.
    
    Supports two modes:
    - Auto-classify: Automatically detects mental health condition
    - Manual: Uses user-specified pathology
    """
    
    # Validate text length
    if len(data.text.strip()) < MIN_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Text too short. Minimum {MIN_TEXT_LENGTH} characters required."
        )
    
    # Check if models are loaded
    if not manager.check_models_loaded():
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Please ensure all models are available."
        )
    
    try:
        # ⚡ Use optimized consolidated pipeline
        result = manager.process_request(
            text=data.text,
            auto_classify=data.auto_classify,
            pathology=data.pathology
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during analysis: {str(e)}"
        )