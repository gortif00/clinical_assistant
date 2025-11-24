# backend/app/ml/models_loader.py

import torch
import warnings
import gc
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoModelForSequenceClassification,
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline,
    BitsAndBytesConfig
)
from peft import PeftModel

from app.core.config import (
    CLASSIFICATION_MODEL_PATH,
    T5_SUMMARIZATION_PATH,
    LLAMA_MODEL_CHECKPOINT,
    LLAMA_LORA_CHECKPOINT_PATH,
    DEVICE,
    QUANTIZATION_CONFIG
)

warnings.filterwarnings("ignore")

# Global model instances
classification_model = None
classification_tokenizer = None
t5_summarizer = None
llama_model = None
llama_tokenizer = None


def print_gpu_memory():
    """Monitor GPU memory usage"""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1e9
        reserved = torch.cuda.memory_reserved() / 1e9
        print(f"GPU Memory: {allocated:.2f}GB allocated, {reserved:.2f}GB reserved")


def load_classification_model():
    """Load the mental health classification model"""
    global classification_model, classification_tokenizer
    
    print("🔍 Loading classification model (Mental Health Classifier)...")
    try:
        classification_tokenizer = AutoTokenizer.from_pretrained(str(CLASSIFICATION_MODEL_PATH))
        classification_model = AutoModelForSequenceClassification.from_pretrained(
            str(CLASSIFICATION_MODEL_PATH)
        )
        
        # Move to GPU if available
        if torch.cuda.is_available():
            classification_model = classification_model.to("cuda")
        classification_model.eval()
        
        print("✅ Classification model loaded successfully")
        print_gpu_memory()
        return True
    except Exception as e:
        print(f"❌ Error loading classification model: {e}")
        classification_model = None
        classification_tokenizer = None
        return False


def load_t5_summarizer():
    """Load the T5 summarization model"""
    global t5_summarizer
    
    print("🚀 Loading T5 model for Summarization...")
    try:
        # Load T5 base tokenizer
        t5_tokenizer = AutoTokenizer.from_pretrained("t5-base")
        
        # Load the fine-tuned model from checkpoint
        t5_model = AutoModelForSeq2SeqLM.from_pretrained(str(T5_SUMMARIZATION_PATH))
        
        # Create pipeline
        device = 0 if torch.cuda.is_available() else -1
        t5_summarizer = pipeline(
            "summarization",
            model=t5_model,
            tokenizer=t5_tokenizer,
            device=device
        )
        
        print("✅ T5 Summarizer loaded successfully")
        print_gpu_memory()
        return True
    except Exception as e:
        print(f"❌ Error loading T5 Summarizer: {e}")
        t5_summarizer = None
        return False


def load_llama_generator():
    """Load the Llama model with QLoRA adapter"""
    global llama_model, llama_tokenizer
    
    print("🚀 Loading Llama 3 with QLoRA for Generation...")
    try:
        # Configure quantization (4-bit)
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=QUANTIZATION_CONFIG["load_in_4bit"],
            bnb_4bit_quant_type=QUANTIZATION_CONFIG["bnb_4bit_quant_type"],
            bnb_4bit_compute_dtype=getattr(torch, QUANTIZATION_CONFIG["bnb_4bit_compute_dtype"])
        )
        
        # Load tokenizer
        llama_tokenizer = AutoTokenizer.from_pretrained(LLAMA_MODEL_CHECKPOINT)
        
        # Set pad token if not defined
        if llama_tokenizer.pad_token is None:
            llama_tokenizer.pad_token = llama_tokenizer.eos_token
        
        # Load base model with quantization
        llama_base_model = AutoModelForCausalLM.from_pretrained(
            LLAMA_MODEL_CHECKPOINT,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.bfloat16
        )
        
        # Apply LoRA weights
        llama_model = PeftModel.from_pretrained(
            llama_base_model, 
            str(LLAMA_LORA_CHECKPOINT_PATH)
        )
        llama_model.eval()
        
        print("✅ Llama 3 (QLoRA) Generator loaded successfully")
        
        # Clean up GPU cache
        torch.cuda.empty_cache()
        gc.collect()
        print_gpu_memory()
        
        return True
    except Exception as e:
        print(f"❌ Error loading Llama 3 Generator: {e}")
        llama_model = None
        llama_tokenizer = None
        return False


def load_all_models():
    """Load all models at startup"""
    print("\n" + "="*60)
    print("LOADING ALL MODELS")
    print("="*60 + "\n")
    
    success = True
    
    # Load classification model
    if not load_classification_model():
        success = False
        print("⚠️ Classification model failed to load")
    
    # Load T5 summarizer
    if not load_t5_summarizer():
        success = False
        print("⚠️ T5 summarizer failed to load")
    
    # Load Llama generator
    if not load_llama_generator():
        success = False
        print("⚠️ Llama generator failed to load")
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL MODELS LOADED SUCCESSFULLY")
    else:
        print("⚠️ SOME MODELS FAILED TO LOAD")
    print("="*60 + "\n")
    
    return success


def check_models_loaded():
    """Check if all models are loaded"""
    return all([
        classification_model is not None,
        classification_tokenizer is not None,
        t5_summarizer is not None,
        llama_model is not None,
        llama_tokenizer is not None
    ])