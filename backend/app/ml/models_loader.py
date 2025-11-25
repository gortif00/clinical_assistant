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
    LLAMA_USE_LOCAL_FILES_ONLY,
    LLAMA_USE_ADAPTER,
    DEVICE,
    QUANTIZATION_CONFIG,
    HF_TOKEN
)

warnings.filterwarnings("ignore")

# Global model instances
classification_model = None
classification_tokenizer = None
t5_summarizer = None
t5_model = None
t5_tokenizer = None
llama_model = None
llama_tokenizer = None


def print_gpu_memory():
    """Monitor GPU memory usage"""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1e9
        reserved = torch.cuda.memory_reserved() / 1e9
        print(f"CUDA GPU Memory: {allocated:.2f}GB allocated, {reserved:.2f}GB reserved")
    elif torch.backends.mps.is_available():
        print(f"MPS GPU: Available (Apple Silicon)")


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
    global t5_summarizer, t5_model, t5_tokenizer
    
    print("🚀 Loading T5 model for Summarization...")
    try:
        # Load T5 base tokenizer
        t5_tokenizer = AutoTokenizer.from_pretrained("t5-base")
        
        # Load the fine-tuned model from checkpoint
        t5_model = AutoModelForSeq2SeqLM.from_pretrained(str(T5_SUMMARIZATION_PATH))
        
        # Move to GPU if available
        if torch.backends.mps.is_available():
            t5_model = t5_model.to("mps")
        elif torch.cuda.is_available():
            t5_model = t5_model.to("cuda")
        
        t5_model.eval()
        
        # Store model and tokenizer directly instead of using pipeline
        # (MPS has issues with pipeline wrapper)
        t5_summarizer = {"model": t5_model, "tokenizer": t5_tokenizer}
        
        print("✅ T5 Summarizer loaded successfully")
        print_gpu_memory()
        return True
    except Exception as e:
        print(f"❌ Error loading T5 Summarizer: {e}")
        t5_summarizer = None
        return False


def load_llama_generator():
    """Load the Llama model with QLoRA adapter (matching notebook configuration)"""
    global llama_model, llama_tokenizer
    
    print("🚀 Loading Llama 3 with QLoRA for Generation...")
    try:
        # Configure quantization (4-bit) only if CUDA GPU is available
        # Note: MPS (Apple Silicon) doesn't support bitsandbytes quantization
        if torch.cuda.is_available():
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16
            )
            print("⚡ Using 4-bit quantization on CUDA GPU")
        else:
            bnb_config = None
            if torch.backends.mps.is_available():
                print("🍎 Apple Silicon detected - using CPU for Llama (more stable)")
            else:
                print("💻 Loading on CPU")
        
        # Load tokenizer (matching notebook exactly)
        llama_tokenizer = AutoTokenizer.from_pretrained(
            LLAMA_MODEL_CHECKPOINT,
            token=HF_TOKEN,
            local_files_only=LLAMA_USE_LOCAL_FILES_ONLY
        )
        
        # Set pad token if not defined (matching notebook)
        if llama_tokenizer.pad_token is None:
            llama_tokenizer.pad_token = llama_tokenizer.eos_token
        
        # Load base model (transformers 4.57+ natively supports Llama 3.2)
        if torch.cuda.is_available():
            # CUDA GPU: Load with quantization (matching notebook)
            llama_base_model = AutoModelForCausalLM.from_pretrained(
                LLAMA_MODEL_CHECKPOINT,
                quantization_config=bnb_config,
                device_map="auto",
                torch_dtype=torch.bfloat16,
                token=HF_TOKEN,
                local_files_only=LLAMA_USE_LOCAL_FILES_ONLY
            )
        elif torch.backends.mps.is_available():
            # Apple Silicon: Load on CPU for stable generation
            # MPS has numerical instability issues with Llama models
            print("   (Using CPU for Llama - MPS has stability issues with this model)")
            llama_base_model = AutoModelForCausalLM.from_pretrained(
                LLAMA_MODEL_CHECKPOINT,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True,
                token=HF_TOKEN,
                local_files_only=LLAMA_USE_LOCAL_FILES_ONLY
            )  # Keep on CPU, don't move to MPS
        else:
            # CPU: Load without quantization
            llama_base_model = AutoModelForCausalLM.from_pretrained(
                LLAMA_MODEL_CHECKPOINT,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True,
                token=HF_TOKEN,
                local_files_only=LLAMA_USE_LOCAL_FILES_ONLY
            )
        
        # Apply LoRA weights (matching notebook)
        # NOTE: LoRA adapter was trained with 4-bit quantization (bitsandbytes)
        # which is NOT compatible with MPS (Apple Silicon). Using LoRA on MPS
        # produces gibberish because of dtype/quantization mismatch.
        if LLAMA_USE_ADAPTER and torch.cuda.is_available():
            # Only apply LoRA on CUDA where 4-bit quantization is supported
            print("🔧 Applying LoRA adapter...")
            llama_model = PeftModel.from_pretrained(
                llama_base_model, 
                str(LLAMA_LORA_CHECKPOINT_PATH)
            )
            print("✅ LoRA adapter applied")
        elif LLAMA_USE_ADAPTER and torch.backends.mps.is_available():
            print("⚠️  LoRA adapter skipped on MPS (trained with 4-bit quantization, incompatible)")
            print("   Using base Llama 3.2 model (will still generate coherent recommendations)")
            llama_model = llama_base_model
        else:
            print("⚠️  Using base model without LoRA adapter")
            llama_model = llama_base_model
        
        llama_model.eval()
        
        print("✅ Llama 3 (QLoRA) Generator loaded successfully")
        
        # Clean up GPU/memory cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        elif torch.backends.mps.is_available():
            torch.mps.empty_cache()
        gc.collect()
        print_gpu_memory()
        
        return True
    except Exception as e:
        print(f"❌ Error loading Llama 3 Generator: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
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
    """Check if critical models (classification and summarization) are loaded"""
    # Only require classification and T5 - Llama is optional
    return all([
        classification_model is not None,
        classification_tokenizer is not None,
        t5_summarizer is not None
    ])


def get_models():
    """
    Get all model instances. Use this function to access models instead of
    importing them directly to avoid stale references.
    """
    return {
        'classification_model': classification_model,
        'classification_tokenizer': classification_tokenizer,
        't5_summarizer': t5_summarizer,
        'llama_model': llama_model,
        'llama_tokenizer': llama_tokenizer
    }