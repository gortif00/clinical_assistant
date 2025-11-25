# backend/app/api/v1/analyze.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.ml.pipeline import (
    generate_treatment_recommendation_with_classification,
    generate_treatment_manual_mode
)
from app.ml.models_loader import (
    check_models_loaded,
    get_models
)
from app.core.config import MIN_TEXT_LENGTH, CLASSIFICATION_CONFIDENCE_THRESHOLD

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
    models_ready = check_models_loaded()
    return {
        "status": "healthy" if models_ready else "degraded",
        "models_loaded": models_ready
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
    if not check_models_loaded():
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Please ensure all models are available."
        )
    
    try:
        # Get current model instances
        models = get_models()
        
        if data.auto_classify:
            # Automatic classification mode
            result = generate_treatment_recommendation_with_classification(
                patient_text=data.text,
                classification_model_obj=models['classification_model'],
                classification_tokenizer_obj=models['classification_tokenizer'],
                t5_summarizer_pipeline=models['t5_summarizer'],
                llama_peft_model=models['llama_model'],
                llama_tokenizer_obj=models['llama_tokenizer'],
                confidence_threshold=CLASSIFICATION_CONFIDENCE_THRESHOLD,
            )
            
            if isinstance(result, str):
                raise HTTPException(status_code=500, detail=result)
            
            if not isinstance(result, dict):
                raise HTTPException(
                    status_code=500,
                    detail=f"Unexpected pipeline output type: {type(result).__name__}"
                )
            
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])
            
            return result
        
        else:
            # Manual pathology mode
            if not data.pathology:
                raise HTTPException(
                    status_code=400,
                    detail="Pathology must be provided when auto_classify is False."
                )
            
            result = generate_treatment_manual_mode(
                patient_text=data.text,
                pathology=data.pathology,
                t5_summarizer_pipeline=models['t5_summarizer'],
                llama_peft_model=models['llama_model'],
                llama_tokenizer_obj=models['llama_tokenizer']
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