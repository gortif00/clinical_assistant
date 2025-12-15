# backend/app/ml/pipeline.py
"""
ML Pipeline functions for clinical case analysis.

This module provides standalone pipeline functions for the 3-stage analysis:
1. Classification: Identify mental health condition
2. Summarization: Generate clinical summary
3. Generation: Create treatment recommendations

These functions are an alternative to the consolidated ModelManager.process_request()
method and may be used for custom workflows or legacy compatibility.
"""

import torch
import numpy as np
import re
from typing import Dict, Optional

from app.core.config import (
    LABEL_MAP,
    CLASSIFICATION_MAX_LENGTH,
    CLASSIFICATION_CONFIDENCE_THRESHOLD,
    SUMMARIZATION_MIN_LENGTH,
    SUMMARIZATION_MAX_LENGTH,
    GENERATION_MAX_NEW_TOKENS,
    GENERATION_TEMPERATURE,
    GENERATION_TOP_P,
    GENERATION_REPETITION_PENALTY,
    GENERATION_TOP_K
)
from app.utils.text_cleaning import clean_text


def classify_mental_health(
    text: str, 
    model, 
    tokenizer, 
    max_length: int = CLASSIFICATION_MAX_LENGTH
) -> Optional[Dict]:
    """
    Classify patient text into one of 5 mental health conditions.
    
    Uses a fine-tuned BERT model to classify clinical text into:
    - Depression
    - Anxiety
    - Bipolar Disorder
    - Borderline Personality Disorder (BPD)
    - Schizophrenia
    
    Args:
        text (str): Raw patient clinical text to classify
        model: BERT classification model (AutoModelForSequenceClassification)
        tokenizer: BERT tokenizer (AutoTokenizer)
        max_length (int): Maximum sequence length (default: 512)
        
    Returns:
        Optional[Dict]: Classification results containing:
            - label (str): Predicted condition name
            - label_id (int): Numeric class ID (0-4)
            - confidence (float): Probability of predicted class (0-1)
            - all_probs (dict): Probability distribution for all 5 classes
        Returns None if model/tokenizer not provided.
    """
    # Validate that model and tokenizer are loaded
    if model is None or tokenizer is None:
        return None
    
    # Clean input text (remove HTML, URLs, normalize whitespace)
    cleaned = clean_text(text)
    inputs = tokenizer(
        cleaned,
        padding=True,
        truncation=True,
        max_length=max_length,
        return_tensors="pt"
    )
    
    # Move inputs to device with proper tensor allocation for MPS
    device = model.device
    if str(device) == "mps":
        # For MPS, explicitly move each tensor
        inputs = {k: v.to(device) for k, v in inputs.items()}
    else:
        inputs = inputs.to(device)
    
    # Predict
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
    
    pred_id = int(np.argmax(probs))
    pred_label = LABEL_MAP[pred_id]
    confidence = float(probs[pred_id])
    
    return {
        'label': pred_label,
        'label_id': pred_id,
        'confidence': confidence,
        'all_probs': {LABEL_MAP[i]: float(p) for i, p in enumerate(probs)}
    }


def generate_treatment_recommendation_with_classification(
    patient_text: str,
    classification_model_obj,
    classification_tokenizer_obj,
    t5_summarizer_pipeline,
    llama_peft_model,
    llama_tokenizer_obj,
    confidence_threshold: float = CLASSIFICATION_CONFIDENCE_THRESHOLD
) -> Dict:
    """
    Generate a treatment recommendation using the complete pipeline.
    
    1. Classifies the pathology from the text
    2. Summarizes the complete diagnosis text with T5
    3. Uses the pathology and summary to generate recommendation with Llama 3
    
    Args:
        patient_text: Clinical observation text
        classification_model_obj: Classification model
        classification_tokenizer_obj: Classification tokenizer
        t5_summarizer_pipeline: T5 summarization pipeline
        llama_peft_model: Llama model with LoRA
        llama_tokenizer_obj: Llama tokenizer
        confidence_threshold: Minimum confidence threshold
        
    Returns:
        Dictionary with classification, summary, recommendation, and metadata
    """
    
    # Check if critical models are loaded (Llama is optional)
    if (
        t5_summarizer_pipeline is None
        or classification_model_obj is None
        or classification_tokenizer_obj is None
    ):
        return {"error": "Error: Critical models (classification/summarization) not loaded correctly."}
    
    llama_available = llama_peft_model is not None and llama_tokenizer_obj is not None
    
    # ==================== STAGE 1: CLASSIFICATION ====================
    print("\n[STAGE 1/3] 🔍 Classifying pathology...")
    
    classification = classify_mental_health(
        patient_text,
        classification_model_obj,
        classification_tokenizer_obj
    )
    
    if classification is None:
        return {"error": "Classification failed"}
    
    detected_pathology = classification["label"]
    confidence = classification["confidence"]
    
    print(f"✅ Detected pathology: {detected_pathology}")
    print(f"   Confidence: {confidence:.2%}")
    
    if confidence < confidence_threshold:
        print(f"⚠️  Low confidence (<{confidence_threshold:.0%}). Top 3 predictions:")
        sorted_probs = sorted(
            classification["all_probs"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for label, prob in sorted_probs[:3]:
            print(f"      {label}: {prob:.2%}")
    
    # ==================== STAGE 2: SUMMARIZATION ====================
    print("\n[STAGE 2/3] 📝 Generating diagnosis summary...")
    
    cleaned_text = clean_text(patient_text)
    
    # Get T5 model and tokenizer
    t5_model = t5_summarizer_pipeline["model"]
    t5_tokenizer = t5_summarizer_pipeline["tokenizer"]
    
    # Tokenize input
    inputs = t5_tokenizer(
        "summarize: " + cleaned_text,
        return_tensors="pt",
        max_length=512,
        truncation=True
    )
    
    # Move to device with MPS handling
    device = t5_model.device
    if str(device) == "mps":
        inputs = {k: v.to(device) for k, v in inputs.items()}
    else:
        inputs = inputs.to(device)
    
    # Calculate appropriate max_length based on input length
    input_length = len(cleaned_text.split())
    dynamic_max_length = min(SUMMARIZATION_MAX_LENGTH, max(50, int(input_length * 0.6)))
    dynamic_min_length = min(SUMMARIZATION_MIN_LENGTH, dynamic_max_length - 20)
    
    # Generate summary
    with torch.no_grad():
        summary_ids = t5_model.generate(
            **inputs,
            min_length=dynamic_min_length,
            max_length=dynamic_max_length,
            num_beams=4,
            early_stopping=True
        )
    
    diagnosis_summary = t5_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    print(f"✅ Summary generated ({len(diagnosis_summary)} chars)")
    print(f"   Preview: {diagnosis_summary[:100]}...")
    
    # ==================== STAGE 3: GENERATION ====================
    print("\n[STAGE 3/3] 💊 Generating treatment recommendation...")
    
    if not llama_available:
        final_recommendation = (
            f"⚠️ Llama model unavailable. Basic recommendation for {detected_pathology}:\n\n"
            "Please consult with a licensed mental health professional for personalized treatment. "
            "The classification and summary above can help guide the initial assessment."
        )
        print("⚠️ Using fallback recommendation (Llama model not loaded)")
    else:
        system_prompt = (
            "You are an expert clinical psychologist providing evidence-based treatment "
            "recommendations. Your recommendations should be specific, actionable, and "
            "tailored to the diagnosed condition."
        )
        
        user_prompt = (
            f"Diagnosed Pathology: {detected_pathology}\n"
            f"Clinical Summary: {diagnosis_summary}\n\n"
            "Generate a comprehensive, evidence-based treatment recommendation including:\n"
            "1. Recommended psychotherapy approaches\n"
            "2. Medication considerations (if applicable)\n"
            "3. Lifestyle interventions\n"
            "4. Follow-up and monitoring plan"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        prompt = llama_tokenizer_obj.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        input_ids = llama_tokenizer_obj(
            prompt,
            return_tensors="pt",
            truncation=True
        )
        
        # Move to device with proper MPS handling
        device = llama_peft_model.device
        if str(device) == "mps":
            input_ids = {k: v.to(device) for k, v in input_ids.items()}
        else:
            input_ids = input_ids.to(device)
        
        output_tokens = llama_peft_model.generate(
            **input_ids,
            max_new_tokens=256,
            do_sample=False,
            num_beams=1,
            repetition_penalty=1.2,
            eos_token_id=llama_tokenizer_obj.eos_token_id,
            pad_token_id=llama_tokenizer_obj.pad_token_id,
        )
        
        final_recommendation = llama_tokenizer_obj.decode(
            output_tokens[0][input_ids["input_ids"].shape[1]:],
            skip_special_tokens=True
        ).strip()
        
        print("✅ Recommendation generated")
    
    # ==================== FINAL RESULT ====================
    result = {
        "classification": {
            "pathology": detected_pathology,
            "confidence": confidence,
            "all_probabilities": classification["all_probs"],
        },
        "summary": diagnosis_summary,
        "recommendation": final_recommendation,
        "metadata": {
            "original_text_length": len(patient_text),
            "summary_length": len(diagnosis_summary),
            "recommendation_length": len(final_recommendation),
        },
    }
    
    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETED")
    print("=" * 60)
    
    return result


def generate_treatment_manual_mode(
    patient_text: str,
    pathology: str,
    t5_summarizer_pipeline,
    llama_peft_model,
    llama_tokenizer_obj
) -> Dict:
    """
    Generate treatment recommendation with manually selected pathology.
    
    Args:
        patient_text: Clinical observation text
        pathology: Manually selected pathology
        t5_summarizer_pipeline: T5 summarization pipeline
        llama_peft_model: Llama model with LoRA
        llama_tokenizer_obj: Llama tokenizer
        
    Returns:
        Dictionary with summary, recommendation, and metadata
    """
    
    if t5_summarizer_pipeline is None:
        return {"error": "Error: Summarization model not loaded correctly."}
    
    llama_available = llama_peft_model is not None and llama_tokenizer_obj is not None
    
    print(f"\n[MANUAL MODE] ℹ️ Analyzing case for {pathology}...")
    
    # ==================== SUMMARIZATION ====================
    print("📝 Extracting clinical summary...")
    
    cleaned_text = clean_text(patient_text)
    
    # Get T5 model and tokenizer
    t5_model = t5_summarizer_pipeline["model"]
    t5_tokenizer = t5_summarizer_pipeline["tokenizer"]
    
    # Tokenize input
    inputs = t5_tokenizer(
        "summarize: " + cleaned_text,
        return_tensors="pt",
        max_length=512,
        truncation=True
    )
    
    # Move to device with MPS handling
    device = t5_model.device
    if str(device) == "mps":
        inputs = {k: v.to(device) for k, v in inputs.items()}
    else:
        inputs = inputs.to(device)
    
    # Calculate appropriate max_length based on input length
    input_length = len(cleaned_text.split())
    dynamic_max_length = min(SUMMARIZATION_MAX_LENGTH, max(50, int(input_length * 0.6)))
    dynamic_min_length = min(SUMMARIZATION_MIN_LENGTH, dynamic_max_length - 20)
    
    # Generate summary
    with torch.no_grad():
        summary_ids = t5_model.generate(
            **inputs,
            min_length=dynamic_min_length,
            max_length=dynamic_max_length,
            num_beams=4,
            early_stopping=True
        )
    
    summary = t5_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    print(f"✅ Summary generated ({len(summary)} chars)")
    
    # ==================== GENERATION ====================
    print("💊 Formulating treatment recommendations...")
    
    if not llama_available:
        recommendation = (
            f"⚠️ Llama model unavailable. Basic recommendation for {pathology}:\n\n"
            "Please consult with a licensed mental health professional for personalized treatment. "
            "The summary above can help guide the initial assessment."
        )
        print("⚠️ Using fallback recommendation (Llama model not loaded)")
    else:
        system_prompt = (
            "You are an expert clinical psychologist. "
            "You write clear, structured treatment recommendations, "
            "always emphasizing safety and referral to a professional."
        )
        
        user_prompt = (
            f"Detected/Selected pathology: {pathology}\n"
            f"Diagnosis summary: {summary}\n\n"
            "Generate a structured treatment recommendation with:\n"
            "1. Psychoeducation\n"
            "2. Recommended therapeutic approaches\n"
            "3. Self-care guidelines\n"
            "4. Warning signs that require urgent professional help."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        prompt = llama_tokenizer_obj.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        input_ids = llama_tokenizer_obj(
            prompt,
            return_tensors="pt",
            truncation=True
        )
        
        # Move to device with proper MPS handling
        device = llama_peft_model.device
        if str(device) == "mps":
            input_ids = {k: v.to(device) for k, v in input_ids.items()}
        else:
            input_ids = input_ids.to(device)
        
        output = llama_peft_model.generate(
            **input_ids,
            max_new_tokens=256,
            do_sample=False,
            num_beams=1,
            repetition_penalty=1.2,
            eos_token_id=llama_tokenizer_obj.eos_token_id,
            pad_token_id=llama_tokenizer_obj.pad_token_id,
        )
        
        recommendation = llama_tokenizer_obj.decode(
            output[0][input_ids["input_ids"].shape[1]:],
            skip_special_tokens=True
        ).strip()
        
        print("✅ Recommendation generated")
    
    # ==================== RESULT ====================
    result = {
        "classification": {
            "pathology": pathology,
            "confidence": None,
            "all_probabilities": {},
        },
        "summary": summary,
        "recommendation": recommendation,
        "metadata": {
            "original_text_length": len(patient_text),
            "summary_length": len(summary),
            "recommendation_length": len(recommendation),
        },
    }
    
    print("\n" + "=" * 60)
    print("✅ MANUAL MODE PIPELINE COMPLETED")
    print("=" * 60)
    
    return result
