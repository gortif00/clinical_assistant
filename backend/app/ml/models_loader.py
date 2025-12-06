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


def get_device():
    """Get optimal device for model execution"""
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def print_gpu_memory():
    """Monitor GPU memory usage"""
    device = get_device()
    if device == "cuda":
        allocated = torch.cuda.memory_allocated() / 1e9
        reserved = torch.cuda.memory_reserved() / 1e9
        print(f"CUDA GPU Memory: {allocated:.2f}GB allocated, {reserved:.2f}GB reserved")
    elif device == "mps":
        print(f"MPS GPU: Available (Apple Silicon)")


class ModelManager:
    """
    Singleton pattern for efficient model management with lazy loading.
    Models are only loaded once and cached for subsequent requests.
    """
    
    def __init__(self):
        # Classification
        self.cls_model = None
        self.cls_tokenizer = None
        
        # Summarization
        self.sum_pipeline = None
        self.sum_model = None
        self.sum_tokenizer = None
        
        # Generation
        self.gen_model = None
        self.gen_tokenizer = None
        self.base_llama_model = None


    def load_classifier(self):
        """Load the mental health classification model (with lazy loading)"""
        if self.cls_model is not None:
            return True  # ⚡ Already loaded, skip
        
        print("🔍 Loading classification model (Mental Health Classifier)...")
        try:
            self.cls_tokenizer = AutoTokenizer.from_pretrained(str(CLASSIFICATION_MODEL_PATH))
            self.cls_model = AutoModelForSequenceClassification.from_pretrained(
                str(CLASSIFICATION_MODEL_PATH)
            )
            
            # Move to optimal device
            device = get_device()
            self.cls_model = self.cls_model.to(device)
            self.cls_model.eval()
            
            print(f"✅ Classification model loaded on {device.upper()}")
            print_gpu_memory()
            return True
        except Exception as e:
            print(f"❌ Error loading classification model: {e}")
            self.cls_model = None
            self.cls_tokenizer = None
            return False


    def load_summarizer(self):
        """Load the T5 summarization model (with lazy loading)"""
        if self.sum_pipeline is not None or self.sum_model is not None:
            return True  # ⚡ Already loaded, skip
        
        print("🚀 Loading T5 model for Summarization...")
        try:
            device = get_device()
            
            # Load tokenizer and model
            self.sum_tokenizer = AutoTokenizer.from_pretrained("t5-base")
            self.sum_model = AutoModelForSeq2SeqLM.from_pretrained(str(T5_SUMMARIZATION_PATH))
            
            # Try to use optimized pipeline for CUDA, fallback to raw model for MPS
            if device == "cuda":
                # Use optimized pipeline for CUDA
                device_id = 0
                self.sum_pipeline = pipeline(
                    "summarization",
                    model=self.sum_model,
                    tokenizer=self.sum_tokenizer,
                    device=device_id
                )
                print(f"✅ T5 Summarizer loaded with pipeline on {device.upper()}")
            else:
                # For MPS/CPU, use raw model (pipeline has issues on MPS)
                self.sum_model = self.sum_model.to(device)
                self.sum_model.eval()
                print(f"✅ T5 Summarizer loaded (raw model) on {device.upper()}")
            
            print_gpu_memory()
            return True
        except Exception as e:
            print(f"❌ Error loading T5 Summarizer: {e}")
            self.sum_pipeline = None
            self.sum_model = None
            self.sum_tokenizer = None
            return False


    def load_generator(self):
        """Load the Llama model with QLoRA adapter (with lazy loading)"""
        if self.gen_model is not None:
            return True  # ⚡ Already loaded, skip
        
        print("🚀 Loading Llama 3 with QLoRA for Generation...")
        try:
            device = get_device()
            
            # Configure quantization (4-bit) only if CUDA GPU is available
            if device == "cuda":
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.bfloat16
                )
                model_dtype = torch.bfloat16
                print("⚡ Using 4-bit quantization on CUDA GPU")
            else:
                bnb_config = None
                model_dtype = torch.bfloat16 if device == "mps" else torch.float32
                if device == "mps":
                    print("🍎 Apple Silicon detected - standard loading")
                else:
                    print("💻 Loading on CPU")
            
            # Load tokenizer
            if self.gen_tokenizer is None:
                self.gen_tokenizer = AutoTokenizer.from_pretrained(
                    LLAMA_MODEL_CHECKPOINT,
                    token=HF_TOKEN,
                    local_files_only=LLAMA_USE_LOCAL_FILES_ONLY
                )
                if self.gen_tokenizer.pad_token is None:
                    self.gen_tokenizer.pad_token = self.gen_tokenizer.eos_token
            
            # Load base model
            if self.base_llama_model is None:
                print(f"   ↳ Loading Llama Base on {device.upper()}...")
                self.base_llama_model = AutoModelForCausalLM.from_pretrained(
                    LLAMA_MODEL_CHECKPOINT,
                    quantization_config=bnb_config,
                    device_map=device if device == "cuda" else None,
                    torch_dtype=model_dtype,
                    token=HF_TOKEN,
                    local_files_only=LLAMA_USE_LOCAL_FILES_ONLY,
                    low_cpu_mem_usage=True
                )
                
                # Move to device if not CUDA (CUDA uses device_map)
                if device != "cuda":
                    # For MPS/CPU stability, keep on CPU
                    if device == "mps":
                        print("   (Keeping on CPU for stability with MPS)")
                    # Don't move to MPS, keep on CPU
            
            # Apply LoRA adapter if available and compatible
            if self.gen_model is not None:
                del self.gen_model
                gc.collect()
                if device == "cuda":
                    torch.cuda.empty_cache()
                elif device == "mps":
                    torch.mps.empty_cache()
            
            if LLAMA_USE_ADAPTER and device == "cuda":
                print("🔧 Applying LoRA adapter...")
                self.gen_model = PeftModel.from_pretrained(
                    self.base_llama_model,
                    str(LLAMA_LORA_CHECKPOINT_PATH)
                )
                print("✅ LoRA adapter applied")
            elif LLAMA_USE_ADAPTER and device == "mps":
                print("⚠️  LoRA adapter skipped on MPS (trained with 4-bit, incompatible)")
                print("   Using base Llama 3.2 model")
                self.gen_model = self.base_llama_model
            else:
                print("⚠️  Using base model without LoRA adapter")
                self.gen_model = self.base_llama_model
            
            self.gen_model.eval()
            
            print("✅ Llama 3 Generator loaded successfully")
            
            # Clean up cache
            if device == "cuda":
                torch.cuda.empty_cache()
            elif device == "mps":
                torch.mps.empty_cache()
            gc.collect()
            print_gpu_memory()
            
            return True
        except Exception as e:
            print(f"❌ Error loading Llama 3 Generator: {e}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            self.gen_model = None
            self.gen_tokenizer = None
            return False


    def load_all_models(self):
        """Load all models at startup (called from lifespan)"""
        print("\n" + "="*60)
        print("LOADING ALL MODELS")
        print("="*60 + "\n")
        
        success = True
        
        # Load classification model
        if not self.load_classifier():
            success = False
            print("⚠️ Classification model failed to load")
        
        # Load T5 summarizer
        if not self.load_summarizer():
            success = False
            print("⚠️ T5 summarizer failed to load")
        
        # Load Llama generator
        if not self.load_generator():
            success = False
            print("⚠️ Llama generator failed to load")
        
        print("\n" + "="*60)
        if success:
            print("✅ ALL MODELS LOADED SUCCESSFULLY")
        else:
            print("⚠️ SOME MODELS FAILED TO LOAD")
        print("="*60 + "\n")
        
        return success
    
    def check_models_loaded(self):
        """Check if critical models (classification and summarization) are loaded"""
        # Only require classification and T5 - Llama is optional
        return all([
            self.cls_model is not None,
            self.cls_tokenizer is not None,
            (self.sum_pipeline is not None or self.sum_model is not None)
        ])
    
    def get_models(self):
        """Get all model instances"""
        return {
            'classification_model': self.cls_model,
            'classification_tokenizer': self.cls_tokenizer,
            't5_summarizer': {'model': self.sum_model, 'tokenizer': self.sum_tokenizer} if self.sum_model else self.sum_pipeline,
            'llama_model': self.gen_model,
            'llama_tokenizer': self.gen_tokenizer
        }
    
    def process_request(self, text: str, auto_classify: bool = True, pathology: str = None):
        """
        Optimized end-to-end pipeline processing (consolidated for speed).
        
        Args:
            text: Patient clinical text
            auto_classify: Whether to auto-classify or use manual pathology
            pathology: Manual pathology selection (if auto_classify=False)
            
        Returns:
            Dictionary with classification, summary, recommendation, and metadata
        """
        import time
        import re
        import numpy as np
        from app.utils.text_cleaning import clean_text
        from app.core.config import LABEL_MAP
        
        inicio = time.time()
        
        # ==================== STAGE 1: CLASSIFICATION ====================
        if auto_classify:
            print("\n[STAGE 1/3] 🔍 Classifying pathology...")
            
            cleaned_text = clean_text(text)
            inputs = self.cls_tokenizer(
                cleaned_text,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            ).to(self.cls_model.device)
            
            with torch.no_grad():
                outputs = self.cls_model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()[0]
            
            pred_id = int(np.argmax(probs))
            detected_pathology = LABEL_MAP[pred_id]
            confidence = float(probs[pred_id])
            all_probs = {LABEL_MAP[i]: float(p) for i, p in enumerate(probs)}
            
            print(f"✅ Detected: {detected_pathology} ({confidence:.2%})")
        else:
            print(f"\n[MANUAL MODE] ℹ️ Using pathology: {pathology}")
            detected_pathology = pathology
            confidence = None
            all_probs = {}
            cleaned_text = clean_text(text)
        
        # ==================== STAGE 2: SUMMARIZATION ====================
        print("\n[STAGE 2/3] 📝 Generating summary...")
        
        if self.sum_pipeline is not None:
            # Use optimized pipeline (CUDA)
            summary_result = self.sum_pipeline(
                cleaned_text,
                min_length=256,
                max_length=512,
                clean_up_tokenization_spaces=True
            )
            diagnosis_summary = summary_result[0]["summary_text"]
        else:
            # Use raw model (MPS/CPU)
            inputs = self.sum_tokenizer(
                "summarize: " + cleaned_text,
                return_tensors="pt",
                max_length=512,
                truncation=True
            ).to(self.sum_model.device)
            
            with torch.no_grad():
                summary_ids = self.sum_model.generate(
                    **inputs,
                    min_length=256,
                    max_length=512,
                    num_beams=4,
                    early_stopping=True
                )
            
            diagnosis_summary = self.sum_tokenizer.decode(
                summary_ids[0], 
                skip_special_tokens=True
            )
        
        print(f"✅ Summary generated ({len(diagnosis_summary)} chars)")
        
        # ==================== STAGE 3: GENERATION ====================
        print("\n[STAGE 3/3] 💊 Generating recommendation...")
        
        if self.gen_model is None or self.gen_tokenizer is None:
            final_recommendation = (
                f"⚠️ Llama model unavailable. Basic recommendation for {detected_pathology}:\n\n"
                "Please consult with a licensed mental health professional for personalized treatment."
            )
            print("⚠️ Using fallback recommendation")
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
            
            prompt = self.gen_tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            input_ids = self.gen_tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True
            ).to(self.gen_model.device)
            
            with torch.no_grad():
                output_tokens = self.gen_model.generate(
                    **input_ids,
                    max_new_tokens=256,
                    min_new_tokens=128,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    eos_token_id=self.gen_tokenizer.eos_token_id,
                )
            
            response = self.gen_tokenizer.decode(
                output_tokens[0][input_ids["input_ids"].shape[1]:],
                skip_special_tokens=True
            ).strip()
            
            # Clean prefix if exists
            match = re.search(r"Recommendation:\s*", response, re.IGNORECASE)
            final_recommendation = response[match.end():].strip() if match else response
            
            print("✅ Recommendation generated")
        
        fin = time.time()
        print(f"\n⏱️ Total processing time: {fin - inicio:.2f} seconds")
        
        return {
            "classification": {
                "pathology": detected_pathology,
                "confidence": confidence,
                "all_probabilities": all_probs
            },
            "summary": diagnosis_summary,
            "recommendation": final_recommendation,
            "metadata": {
                "original_text_length": len(text),
                "summary_length": len(diagnosis_summary),
                "recommendation_length": len(final_recommendation),
                "processing_time": round(fin - inicio, 2)
            }
        }


# Global singleton instance
manager = ModelManager()


# Legacy functions for backward compatibility (redirect to manager)
def load_all_models():
    """Load all models at startup (legacy wrapper)"""
    return manager.load_all_models()


def check_models_loaded():
    """Check if critical models are loaded (legacy wrapper)"""
    return manager.check_models_loaded()


def get_models():
    """Get all model instances (legacy wrapper)"""
    return manager.get_models()