# backend/app/core/config.py

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "models"

# ==================== MODEL PATHS ====================
# Classification model (fine-tuned)
CLASSIFICATION_MODEL_PATH = MODELS_DIR / "classifier"

# T5 Summarization model (fine-tuned checkpoint)
T5_SUMMARIZATION_PATH = MODELS_DIR / "t5_summarizer"

# Llama model (base + LoRA adapter)
# Set to local path if you have the base model downloaded, otherwise use HF repo
LLAMA_BASE_MODEL_PATH = os.getenv("LLAMA_BASE_MODEL_PATH", None)
LLAMA_MODEL_CHECKPOINT = LLAMA_BASE_MODEL_PATH if LLAMA_BASE_MODEL_PATH else "meta-llama/Llama-3.2-1B-Instruct"
LLAMA_LORA_CHECKPOINT_PATH = MODELS_DIR / "llama_peft"
LLAMA_USE_LOCAL_FILES_ONLY = os.getenv("LLAMA_USE_LOCAL_FILES_ONLY", "false").lower() == "true"
LLAMA_USE_ADAPTER = os.getenv("LLAMA_USE_ADAPTER", "true").lower() == "true"

# ==================== DEVICE CONFIGURATION ====================
import torch

# Detect available device: MPS (Apple Silicon), CUDA (NVIDIA), or CPU
if torch.backends.mps.is_available():
    DEVICE = "mps"
    USE_GPU = True
    GPU_TYPE = "mps"
elif torch.cuda.is_available():
    DEVICE = "cuda:0"
    USE_GPU = True
    GPU_TYPE = "cuda"
else:
    DEVICE = "cpu"
    USE_GPU = False
    GPU_TYPE = None

# ==================== LABEL MAPPING ====================
# Mental health condition labels (5 classes)
LABEL_MAP = {
    0: "BPD",
    1: "Bipolar Disorder",
    2: "Depression",
    3: "Anxiety",
    4: "Schizophrenia"
}

# Reverse mapping
LABEL_TO_ID = {v: k for k, v in LABEL_MAP.items()}

# ==================== MODEL PARAMETERS ====================
# Classification
CLASSIFICATION_MAX_LENGTH = 192
CLASSIFICATION_CONFIDENCE_THRESHOLD = 0.6

# Summarization
SUMMARIZATION_MIN_LENGTH = 128
SUMMARIZATION_MAX_LENGTH = 256

# Generation (matching notebook configuration)
GENERATION_MAX_NEW_TOKENS = 512
GENERATION_TEMPERATURE = 0.7
GENERATION_TOP_P = 0.9
GENERATION_REPETITION_PENALTY = 1.15
GENERATION_TOP_K = 50

# Minimum text length for analysis
MIN_TEXT_LENGTH = 50

# ==================== QUANTIZATION CONFIG ====================
# For Llama model (QLoRA)
QUANTIZATION_CONFIG = {
    "load_in_4bit": True,
    "bnb_4bit_quant_type": "nf4",
    "bnb_4bit_compute_dtype": "bfloat16"
}

# ==================== HUGGING FACE TOKEN ====================
HF_TOKEN = os.getenv("HF_TOKEN", None)
