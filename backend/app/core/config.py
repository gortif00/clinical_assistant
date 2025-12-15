# backend/app/core/config.py
# GLOBAL CONFIGURATION FILE
# Centralized configuration for model paths, parameters, and device detection

import os
from pathlib import Path

# ============================================================================
# BASE DIRECTORIES
# ============================================================================
# Calculate paths relative to this config file
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Go up to backend/
MODELS_DIR = BASE_DIR / "models"  # All trained models are stored here

# ============================================================================
# MODEL PATHS
# ============================================================================

# Classification model (Fine-tuned MentalBERT for 11 mental health conditions)
# Trained on 204K samples from the Mental Disorders dataset
CLASSIFICATION_MODEL_PATH = MODELS_DIR / "classifier"

# T5 Summarization model (Fine-tuned T5-base for clinical summaries)
# Generates concise medical summaries from patient case descriptions
T5_SUMMARIZATION_PATH = MODELS_DIR / "t5_summarizer"

# Llama model configuration (Base model + LoRA adapter)
# Uses Llama 3.2-1B-Instruct with QLoRA fine-tuning for treatment recommendations
LLAMA_BASE_MODEL_PATH = os.getenv("LLAMA_BASE_MODEL_PATH", None)  # Optional: local base model
LLAMA_MODEL_CHECKPOINT = LLAMA_BASE_MODEL_PATH if LLAMA_BASE_MODEL_PATH else "meta-llama/Llama-3.2-1B-Instruct"
LLAMA_LORA_CHECKPOINT_PATH = MODELS_DIR / "llama_peft"  # LoRA adapter weights
LLAMA_USE_LOCAL_FILES_ONLY = os.getenv("LLAMA_USE_LOCAL_FILES_ONLY", "false").lower() == "true"
LLAMA_USE_ADAPTER = os.getenv("LLAMA_USE_ADAPTER", "true").lower() == "true"

# ============================================================================
# DEVICE CONFIGURATION (GPU/CPU)
# ============================================================================
import torch

# Automatically detect the best available device:
# 1. MPS (Apple Silicon GPU - M1/M2/M3 chips)
# 2. CUDA (NVIDIA GPU)
# 3. CPU (fallback)
if torch.backends.mps.is_available():
    DEVICE = "mps"
    USE_GPU = True
    GPU_TYPE = "mps"
elif torch.cuda.is_available():
    DEVICE = "cuda:0"  # Use first CUDA device
    USE_GPU = True
    GPU_TYPE = "cuda"
else:
    DEVICE = "cpu"
    USE_GPU = False
    GPU_TYPE = None

# ============================================================================
# LABEL MAPPING (Mental Health Conditions)
# ============================================================================
# Maps model output IDs to human-readable condition names
# These 5 categories cover the most common mental health conditions
LABEL_MAP = {
    0: "BPD",  # Borderline Personality Disorder
    1: "Bipolar Disorder",
    2: "Depression",
    3: "Anxiety",
    4: "Schizophrenia"
}

# Reverse mapping: condition name -> ID (for manual selection): condition name -> ID (for manual selection)
LABEL_TO_ID = {v: k for k, v in LABEL_MAP.items()}

# ============================================================================
# MODEL PARAMETERS
# ============================================================================

# --- Classification (BERT) ---
# Maximum sequence length for input text (longer texts are truncated)
CLASSIFICATION_MAX_LENGTH = 192
# Minimum confidence threshold to trust the prediction (0-1)
CLASSIFICATION_CONFIDENCE_THRESHOLD = 0.6

# --- Summarization (T5) ---
# Minimum length of generated summary (in tokens)
SUMMARIZATION_MIN_LENGTH = 128
# Maximum length of generated summary (in tokens)
SUMMARIZATION_MAX_LENGTH = 256

# --- Generation (Llama) ---
# Maximum number of new tokens to generate in the recommendation
GENERATION_MAX_NEW_TOKENS = 512
# Temperature: Controls randomness (0.0 = deterministic, 1.0 = very random)
GENERATION_TEMPERATURE = 0.7
# Top-p (nucleus sampling): Only sample from top p% of probability mass
GENERATION_TOP_P = 0.9
# Repetition penalty: Discourage repeating the same phrases (1.0 = no penalty)
GENERATION_REPETITION_PENALTY = 1.15
# Top-k sampling: Only sample from top k tokens
GENERATION_TOP_K = 50

# Minimum text length required for analysis (characters)
# Requests with shorter text will be rejected
MIN_TEXT_LENGTH = 50

# ============================================================================
# QUANTIZATION CONFIGURATION (QLoRA for Llama)
# ============================================================================
# 4-bit quantization configuration to reduce memory usage
# This allows running Llama 3.2-1B on consumer GPUs (8GB VRAM)
QUANTIZATION_CONFIG = {
    "load_in_4bit": True,  # Enable 4-bit quantization
    "bnb_4bit_quant_type": "nf4",  # NormalFloat 4-bit (better than standard FP4)
    "bnb_4bit_compute_dtype": "bfloat16"  # Computation precision
}

# ==================== HUGGING FACE TOKEN ====================
HF_TOKEN = os.getenv("HF_TOKEN", None)

# ==================== SECURITY & AUTH ====================
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "dev-refresh-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# ==================== RATE LIMITING ====================
USE_REDIS_RATE_LIMITING = os.getenv("USE_REDIS_RATE_LIMITING", "false").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ==================== CORS ====================
CORS_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]

# ==================== LOGGING ====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
