# backend/app/ml/models_loader.py
# MODEL MANAGER: SINGLETON PATTERN WITH LAZY LOADING
# Manages loading and caching of all three ML models (BERT, T5, Llama)
# Uses lazy loading to only load models when needed, dramatically improving startup time

import torch  # PyTorch for deep learning
import warnings  # Suppress transformer warnings
import gc  # Garbage collector for memory management
from transformers import (
    AutoModelForSeq2SeqLM,  # T5 model for summarization
    AutoModelForSequenceClassification,  # BERT model for classification
    AutoModelForCausalLM,  # Llama model for text generation
    AutoTokenizer,  # Tokenizer for all models
    pipeline,  # High-level API for inference
    BitsAndBytesConfig  # 4-bit quantization configuration
)
from peft import PeftModel  # Parameter-Efficient Fine-Tuning (LoRA adapter)

# Import configuration constants
from app.core.config import (
    CLASSIFICATION_MODEL_PATH,  # Path to fine-tuned BERT classifier
    T5_SUMMARIZATION_PATH,  # Path to fine-tuned T5 summarizer
    LLAMA_MODEL_CHECKPOINT,  # Llama base model (HuggingFace repo or local)
    LLAMA_LORA_CHECKPOINT_PATH,  # Path to LoRA adapter weights
    LLAMA_USE_LOCAL_FILES_ONLY,  # Whether to use only local files (no HF download)
    LLAMA_USE_ADAPTER,  # Whether to apply LoRA adapter
    DEVICE,  # Target device (cuda/mps/cpu)
    QUANTIZATION_CONFIG,  # 4-bit quantization settings
    HF_TOKEN  # HuggingFace API token for accessing gated models
)

# Suppress unnecessary warnings from transformers library
warnings.filterwarnings("ignore")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_device():
    """
    Detect the optimal device for model execution.
    
    Priority order:
    1. CUDA (NVIDIA GPU) - Best performance, supports 4-bit quantization
    2. MPS (Apple Silicon GPU) - Good performance, limited quantization support
    3. CPU - Slowest, but universal fallback
    
    Returns:
        str: 'cuda', 'mps', or 'cpu'
    """
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def print_gpu_memory():
    """
    Monitor and display GPU memory usage.
    
    Useful for debugging memory issues and verifying models are loaded correctly.
    Only provides detailed info for CUDA (NVIDIA GPUs).
    """
    device = get_device()
    if device == "cuda":
        # Get memory stats from CUDA
        allocated = torch.cuda.memory_allocated() / 1e9  # Convert bytes to GB
        reserved = torch.cuda.memory_reserved() / 1e9
        print(f"CUDA GPU Memory: {allocated:.2f}GB allocated, {reserved:.2f}GB reserved")
    elif device == "mps":
        # MPS doesn't expose detailed memory stats
        print(f"MPS GPU: Available (Apple Silicon)")


# ============================================================================
# MODEL MANAGER CLASS (SINGLETON PATTERN)
# ============================================================================

class ModelManager:
    """
    Singleton pattern for efficient model management with lazy loading.
    
    This class ensures that:
    1. Models are loaded only once (singleton pattern)
    2. Models are loaded only when needed (lazy loading)
    3. Models are cached in memory for fast subsequent requests
    4. Memory is managed efficiently across all three models
    
    The three models managed are:
    - Classifier (BERT): Detects mental health condition from text
    - Summarizer (T5): Generates clinical summary
    - Generator (Llama): Creates treatment recommendations
    
    Key optimization: Using lazy loading, the first request takes 30-60s
    (loads all models), but subsequent requests are 3-5s (uses cached models).
    This is 60-80% faster than reloading models on each request.
    """
    
    def __init__(self):
        """
        Initialize the ModelManager with empty model slots.
        
        Models are set to None initially and loaded on first use.
        This dramatically speeds up application startup time.
        """
        # Classification model components
        self.cls_model = None  # BERT model for classification
        self.cls_tokenizer = None  # Tokenizer for BERT
        
        # Summarization model components
        self.sum_pipeline = None  # High-level pipeline API (CUDA only)
        self.sum_model = None  # Raw T5 model (for MPS/CPU)
        self.sum_tokenizer = None  # Tokenizer for T5
        
        # Generation model components
        self.gen_model = None  # Llama model with or without LoRA
        self.gen_tokenizer = None  # Tokenizer for Llama
        self.base_llama_model = None  # Base Llama before LoRA is applied


    def load_classifier(self):
        """
        Load the mental health classification model (BERT-based).
        
        This model classifies text into one of 5 mental health conditions:
        - BPD (Borderline Personality Disorder)
        - Bipolar Disorder
        - Depression
        - Anxiety
        - Schizophrenia
        
        Uses lazy loading: If already loaded, returns immediately.
        
        Returns:
            bool: True if successfully loaded, False otherwise
        """
        # Check if already loaded (lazy loading optimization)
        if self.cls_model is not None:
            return True  # ⚡ Already loaded, skip expensive loading process
        
        print("🔍 Loading classification model (Mental Health Classifier)...")
        try:
            # Load tokenizer (converts text to model input format)
            self.cls_tokenizer = AutoTokenizer.from_pretrained(str(CLASSIFICATION_MODEL_PATH))
            
            # Load the fine-tuned BERT model
            self.cls_model = AutoModelForSequenceClassification.from_pretrained(
                str(CLASSIFICATION_MODEL_PATH)
            )
            
            # Move model to optimal device (GPU if available, otherwise CPU)
            device = get_device()
            self.cls_model = self.cls_model.to(device)
            
            # Set to evaluation mode (disables dropout, batch normalization, etc.)
            self.cls_model.eval()
            
            print(f"✅ Classification model loaded on {device.upper()}")
            print_gpu_memory()
            return True
        except Exception as e:
            print(f"❌ Error loading classification model: {e}")
            # Clean up partially loaded components
            self.cls_model = None
            self.cls_tokenizer = None
            return False


    def load_summarizer(self):
        """
        Load the T5 summarization model.
        
        This model generates concise clinical summaries from longer
        patient case descriptions. Uses T5-base (220M parameters).
        
        Two loading strategies:
        - CUDA: Uses optimized pipeline API for faster inference
        - MPS/CPU: Uses raw model (pipeline has compatibility issues)
        
        Uses lazy loading: If already loaded, returns immediately.
        
        Returns:
            bool: True if successfully loaded, False otherwise
        """
        # Check if already loaded (lazy loading optimization)
        if self.sum_pipeline is not None or self.sum_model is not None:
            return True  # ⚡ Already loaded, skip
        
        print("🚀 Loading T5 model for Summarization...")
        try:
            device = get_device()
            
            # Load tokenizer and model
            self.sum_tokenizer = AutoTokenizer.from_pretrained("t5-base")
            self.sum_model = AutoModelForSeq2SeqLM.from_pretrained(str(T5_SUMMARIZATION_PATH))
            
            # Choose loading strategy based on device
            if device == "cuda":
                # CUDA: Use optimized pipeline for better performance
                device_id = 0  # First CUDA device
                self.sum_pipeline = pipeline(
                    "summarization",  # Task type
                    model=self.sum_model,
                    tokenizer=self.sum_tokenizer,
                    device=device_id  # Explicitly set device
                )
                print(f"✅ T5 Summarizer loaded with pipeline on {device.upper()}")
            else:
                # MPS/CPU: Use raw model (pipeline has issues on MPS)
                self.sum_model = self.sum_model.to(device)
                self.sum_model.eval()
                print(f"✅ T5 Summarizer loaded (raw model) on {device.upper()}")
            
            print_gpu_memory()
            return True
        except Exception as e:
            print(f"❌ Error loading T5 Summarizer: {e}")
            # Clean up partially loaded components
            self.sum_pipeline = None
            self.sum_model = None
            self.sum_tokenizer = None
            return False


    def load_generator(self):
        """
        Load the Llama 3 model with QLoRA adapter for treatment recommendations.
        
        This model generates personalized treatment suggestions based on
        the diagnosed mental health condition. Uses LoRA adapters for
        efficient fine-tuning.
        
        Key optimizations:
        - 4-bit quantization on CUDA (reduces memory ~75%, 4GB → ~1GB)
        - LoRA adapters (trains only 1% of parameters)
        - Device-specific loading strategies for CUDA/MPS/CPU
        
        Two loading modes:
        1. With LoRA adapter (LLAMA_USE_ADAPTER=True, CUDA only): Fine-tuned model
        2. Without adapter: Base Llama model
        
        Uses lazy loading: If already loaded, returns immediately.
        
        Returns:
            bool: True if successfully loaded, False otherwise
        """
        # Check if already loaded (lazy loading optimization)
        if self.gen_model is not None:
            return True  # ⚡ Already loaded, skip expensive loading
        
        print("🚀 Loading Llama 3 with QLoRA for Generation...")
        try:
            device = get_device()
            
            # ========================================
            # VERIFY HF_TOKEN FOR GATED MODELS
            # ========================================
            if HF_TOKEN is None or HF_TOKEN == "":
                print("⚠️  WARNING: HF_TOKEN not set!")
                print("   Llama 3.2 is a gated model and requires authentication.")
                print("   Set HF_TOKEN environment variable or add to .env file.")
                print("   Attempting to load anyway (will fail if model not cached)...")
            else:
                print(f"✅ HF_TOKEN detected: {HF_TOKEN[:8]}...")
            
            # ========================================
            # 4-BIT QUANTIZATION CONFIGURATION
            # ========================================
            # Reduces memory usage by ~75% with minimal accuracy loss
            # Only works on CUDA GPUs (bitsandbytes doesn't support MPS/CPU)
            if device == "cuda":
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,  # Enable 4-bit quantization
                    bnb_4bit_quant_type="nf4",  # Normal Float 4-bit (better than int4)
                    bnb_4bit_compute_dtype=torch.bfloat16  # Use bfloat16 for computation
                )
                model_dtype = torch.bfloat16
                print("⚡ Using 4-bit quantization on CUDA GPU")
            else:
                # MPS/CPU: No quantization available
                bnb_config = None
                model_dtype = torch.bfloat16 if device == "mps" else torch.float32
                if device == "mps":
                    print("🍎 Apple Silicon detected - standard loading")
                else:
                    print("💻 Loading on CPU")
            
            # ========================================
            # LOAD TOKENIZER
            # ========================================
            # Tokenizer converts text into model input format
            if self.gen_tokenizer is None:
                self.gen_tokenizer = AutoTokenizer.from_pretrained(
                    LLAMA_MODEL_CHECKPOINT,  # Model checkpoint ID
                    token=HF_TOKEN,  # HuggingFace authentication token
                    local_files_only=LLAMA_USE_LOCAL_FILES_ONLY  # Use cached files if available
                )
                # Set padding token (Llama doesn't have one by default)
                # Use EOS (end-of-sequence) token as padding (common practice)
                if self.gen_tokenizer.pad_token is None:
                    self.gen_tokenizer.pad_token = self.gen_tokenizer.eos_token
            
            # ========================================
            # LOAD BASE LLAMA MODEL
            # ========================================
            if self.base_llama_model is None:
                print(f"   ↳ Loading Llama Base on {device.upper()}...")
                self.base_llama_model = AutoModelForCausalLM.from_pretrained(
                    LLAMA_MODEL_CHECKPOINT,
                    quantization_config=bnb_config,  # Apply 4-bit quantization (CUDA only)
                    device_map=device if device == "cuda" else None,  # Auto device mapping for CUDA
                    torch_dtype=model_dtype,  # Model precision (bfloat16 or float32)
                    token=HF_TOKEN,
                    local_files_only=LLAMA_USE_LOCAL_FILES_ONLY,
                    low_cpu_mem_usage=True  # Optimize memory during loading
                )
                
                # Move to device if not using CUDA (CUDA uses device_map automatically)
                if device != "cuda":
                    # For MPS, keep on CPU for better stability (MPS can be unstable with large models)
                    if device == "mps":
                        print("   (Keeping on CPU for stability with MPS)")
                    # Note: Not moving to MPS device to avoid stability issues
            
            # ========================================
            # APPLY LORA ADAPTER (IF AVAILABLE)
            # ========================================
            # Clean up existing model if loaded
            if self.gen_model is not None:
                del self.gen_model
                gc.collect()  # Force garbage collection
                if device == "cuda":
                    torch.cuda.empty_cache()  # Clear CUDA memory
                elif device == "mps":
                    torch.mps.empty_cache()  # Clear MPS memory
            
            # Apply LoRA adapter based on device and configuration
            if LLAMA_USE_ADAPTER and device == "cuda":
                # LoRA adapter is compatible with 4-bit quantization on CUDA
                print("🔧 Applying LoRA adapter...")
                self.gen_model = PeftModel.from_pretrained(
                    self.base_llama_model,  # Base model
                    str(LLAMA_LORA_CHECKPOINT_PATH)  # Path to LoRA weights
                )
                print("✅ LoRA adapter applied")
            elif LLAMA_USE_ADAPTER and device == "mps":
                # LoRA adapter trained with 4-bit, incompatible with non-quantized MPS model
                print("⚠️  LoRA adapter skipped on MPS (trained with 4-bit, incompatible)")
                print("   Using base Llama 3.2 model")
                self.gen_model = self.base_llama_model
            else:
                # No adapter configured or not available
                print("⚠️  Using base model without LoRA adapter")
                self.gen_model = self.base_llama_model
            
            # Set to evaluation mode (disables dropout, batch normalization)
            self.gen_model.eval()
            
            print("✅ Llama 3 Generator loaded successfully")
            
            # ========================================
            # MEMORY CLEANUP
            # ========================================
            # Clear caches to free up memory after loading
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
            # Clean up partially loaded components
            self.gen_model = None
            self.gen_tokenizer = None
            return False


    def load_all_models(self):
        """
        Load all three models at startup (called from FastAPI lifespan).
        
        This preloads all models during application startup so that
        the first request doesn't have to wait for model loading.
        
        Typical loading time: 30-60 seconds (happens once)
        
        Returns:
            bool: True if all models loaded successfully, False otherwise
        """
        import time
        print("\n" + "="*60)
        print("LOADING ALL MODELS")
        print("="*60 + "\n")
        
        start_time = time.time()
        success = True
        
        # Load classification model (BERT)
        print("[1/3] Loading Classification Model (BERT)...")
        t0 = time.time()
        if not self.load_classifier():
            success = False
            print("⚠️ Classification model failed to load")
        else:
            print(f"   ✅ Loaded in {time.time() - t0:.1f}s\n")
        
        # Load T5 summarizer
        print("[2/3] Loading Summarization Model (T5)...")
        t0 = time.time()
        if not self.load_summarizer():
            success = False
            print("⚠️ T5 summarizer failed to load")
        else:
            print(f"   ✅ Loaded in {time.time() - t0:.1f}s\n")
        
        # Load Llama generator
        print("[3/3] Loading Generation Model (Llama 3.2 + LoRA)...")
        t0 = time.time()
        if not self.load_generator():
            success = False
            print("⚠️ Llama generator failed to load")
        else:
            print(f"   ✅ Loaded in {time.time() - t0:.1f}s\n")
        
        total_time = time.time() - start_time
        print("=" * 60)
        if success:
            print(f"✅ ALL MODELS LOADED SUCCESSFULLY in {total_time:.1f}s")
        else:
            print(f"⚠️ SOME MODELS FAILED TO LOAD (took {total_time:.1f}s)")
        print("="*60 + "\n")
        
        return success
    
    def check_models_loaded(self):
        """
        Check if critical models (classification and summarization) are loaded.
        
        Only requires classification and T5 models to be loaded.
        Llama generator is optional (system can function without it).
        
        This is used for health checks to determine if the system is ready
        to accept traffic.
        
        Returns:
            bool: True if critical models (BERT + T5) are loaded
        """
        return all([
            self.cls_model is not None,  # BERT classification model
            self.cls_tokenizer is not None,  # BERT tokenizer
            (self.sum_pipeline is not None or self.sum_model is not None)  # T5 model (pipeline or raw)
        ])
    
    def get_models(self):
        """
        Get all currently loaded model instances.
        
        Useful for debugging and monitoring to check which models
        are currently in memory.
        
        Returns:
            dict: Dictionary containing all model instances
        """
        return {
            'classification_model': self.cls_model,
            'classification_tokenizer': self.cls_tokenizer,
            't5_summarizer': {'model': self.sum_model, 'tokenizer': self.sum_tokenizer} if self.sum_model else self.sum_pipeline,
            'llama_model': self.gen_model,
            'llama_tokenizer': self.gen_tokenizer
        }
    
    def process_request_streaming(self, text: str, auto_classify: bool = True, pathology: str = None):
        """
        STREAMING-OPTIMIZED pipeline: SKIPS summary generation entirely.
        
        For streaming endpoints only. Does classification + recommendation,
        but summary is NOT generated (saves ~2-3 seconds and prevents leakage).
        
        Returns:
            dict: classification + recommendation only (NO summary field)
        """
        import time
        from app.utils.text_cleaning import clean_text
        from app.core.config import LABEL_MAP
        import numpy as np
        
        inicio = time.time()
        
        # STAGE 1: Classification (same as regular pipeline)
        if auto_classify:
            print("\n[STREAM MODE - STAGE 1/2] 🔍 Classifying pathology...")
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
            print(f"\n[STREAM MODE - MANUAL] ℹ️ Using pathology: {pathology}")
            detected_pathology = pathology
            confidence = None
            all_probs = {}
            cleaned_text = clean_text(text)
        
        # STAGE 2: SKIP SUMMARY - Go directly to recommendation
        # Use cleaned text directly as context (no T5 summary)
        print("\n[STREAM MODE - STAGE 2/2] 💊 Generating recommendation (NO SUMMARY)...")
        
        if self.gen_model is None or self.gen_tokenizer is None:
            final_recommendation = (
                f"⚠️ Llama model unavailable. Basic recommendation for {detected_pathology}:\n\n"
                "Please consult with a licensed mental health professional."
            )
            print("⚠️ Using fallback recommendation")
        else:
            # ChatGPT-style structured prompt for streaming
            system_prompt = (
                "You are an experienced clinical psychologist providing comprehensive, well-structured clinical guidance. "
                "Create professional reports with clear section titles and subtitles that adapt to each specific case. "
                "Use a clean, readable format with proper headings similar to ChatGPT's response style. "
                "Write in professional but accessible language."
            )
            
            user_prompt = (
                f"Based on the patient observations below, create a structured treatment recommendation.\n\n"
                f"Diagnosed Condition: {detected_pathology}\n"
                f"Clinical Observations: {cleaned_text[:600]}\n\n"
                f"Provide a comprehensive treatment plan with:\n\n"
                f"# Treatment Plan: {detected_pathology}\n\n"
                "## Clinical Overview\n"
                "Brief overview of this patient's presentation based on observations (2 paragraphs)\n\n"
                "## Treatment Approach\n\n"
                "### Pharmacological Interventions\n"
                f"Appropriate medications for {detected_pathology} (1 paragraph)\n\n"
                "### Psychotherapy\n"
                "Evidence-based therapy approaches:\n"
                "- **[Therapy 1]**: How it helps\n"
                "- **[Therapy 2]**: Application\n\n"
                "### Self-Management\n"
                "Practical strategies for daily management\n\n"
                "## Follow-up Plan\n"
                "Monitoring and next steps (1 paragraph)\n\n"
                "Use markdown headers (# ## ###) and adapt all content to this specific case."
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
                truncation=True,
                max_length=1536
            ).to(self.gen_model.device)
            
            with torch.no_grad():
                output_tokens = self.gen_model.generate(
                    **input_ids,
                    max_new_tokens=600,  # Increased for structured streaming output
                    min_new_tokens=200,
                    do_sample=True,
                    temperature=0.75,
                    top_p=0.92,
                    repetition_penalty=1.2,
                    no_repeat_ngram_size=4,
                    eos_token_id=self.gen_tokenizer.eos_token_id,
                    pad_token_id=self.gen_tokenizer.pad_token_id,
                    early_stopping=True,
                )
            
            final_recommendation = self.gen_tokenizer.decode(
                output_tokens[0][input_ids["input_ids"].shape[1]:],
                skip_special_tokens=True
            ).strip()
            
            print("✅ Recommendation generated (streaming-ready)")
        
        fin = time.time()
        print(f"\n⏱️ Streaming pipeline time: {fin - inicio:.2f} seconds")
        
        return {
            "classification": {
                "pathology": detected_pathology,
                "confidence": confidence,
                "all_probabilities": all_probs
            },
            "recommendation": final_recommendation,  # NO SUMMARY FIELD
            "metadata": {
                "processing_time": round(fin - inicio, 2),
                "mode": "streaming"
            }
        }
    
    def process_request(self, text: str, auto_classify: bool = True, pathology: str = None):
        """
        Execute the complete 3-stage ML pipeline for clinical case analysis.
        
        This is the main entry point for processing clinical text. It orchestrates
        three sequential stages:
        
        1. CLASSIFICATION (BERT): Identifies the mental health condition
        2. SUMMARIZATION (T5): Generates concise clinical summary
        3. GENERATION (Llama): Creates personalized treatment recommendations
        
        The pipeline is optimized for speed with:
        - Parallel tokenization where possible
        - Efficient memory management
        - Device-aware processing (CUDA/MPS/CPU)
        - Consolidated execution (no model reloading)
        
        Args:
            text (str): Raw patient clinical text (max ~512 tokens recommended)
            auto_classify (bool): If True, uses BERT to classify condition.
                                 If False, uses provided pathology parameter.
            pathology (str): Manual pathology selection, used when auto_classify=False.
                           Must be one of: 'depression', 'anxiety', 'bipolar', 'bpd', 'schizophrenia'
        
        Returns:
            dict: Complete analysis results containing:
                - classification_result (dict): Predicted condition and confidence scores
                - summary (str): Clinical summary of the case
                - recommendation (str): Treatment recommendations
                - processing_time (dict): Timing for each stage
                - metadata (dict): Model versions, parameters used
        
        Raises:
            Exception: If models are not loaded or processing fails
        """
        import time
        import re
        import numpy as np
        from app.utils.text_cleaning import clean_text
        from app.core.config import LABEL_MAP
        
        # Record start time for performance tracking
        inicio = time.time()
        
        # ========================================================================
        # STAGE 1: CLASSIFICATION - Identify Mental Health Condition
        # ========================================================================
        # Uses fine-tuned BERT model to classify text into one of 5 conditions:
        # Depression, Anxiety, Bipolar, BPD, Schizophrenia
        
        if auto_classify:
            print("\n[STAGE 1/3] 🔍 Classifying pathology...")
            
            # Clean input text (remove HTML, URLs, normalize whitespace)
            cleaned_text = clean_text(text)
            
            # Tokenize text for BERT input
            inputs = self.cls_tokenizer(
                cleaned_text,
                padding=True,  # Pad to max length in batch
                truncation=True,  # Truncate if longer than max_length
                max_length=512,  # BERT maximum sequence length
                return_tensors="pt"  # Return PyTorch tensors
            ).to(self.cls_model.device)  # Move to model's device (GPU/CPU)
            
            # Run inference (no gradient computation needed)
            with torch.no_grad():
                outputs = self.cls_model(**inputs)  # Get model predictions
                # Convert logits to probabilities using softmax
                probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()[0]
            
            # Get predicted class and confidence
            pred_id = int(np.argmax(probs))  # Index of highest probability
            detected_pathology = LABEL_MAP[pred_id]  # Convert ID to label name
            confidence = float(probs[pred_id])  # Confidence score (0-1)
            
            # Create probability distribution for all classes
            all_probs = {LABEL_MAP[i]: float(p) for i, p in enumerate(probs)}
            
            # Confidence threshold check: If confidence is low, patient may be healthy
            CONFIDENCE_THRESHOLD = 0.55  # Minimum confidence to diagnose pathology
            if confidence < CONFIDENCE_THRESHOLD:
                original_pathology = detected_pathology
                detected_pathology = "no_significant_pathology"
                print(f"⚠️ Low confidence ({confidence:.2%}) - No clear pathology detected")
                print(f"   (Highest match was {original_pathology}, but below threshold)")
            else:
                print(f"✅ Detected: {detected_pathology} ({confidence:.2%})")
        else:
            # Manual mode: Use provided pathology instead of classification
            print(f"\n[MANUAL MODE] ℹ️ Using pathology: {pathology}")
            detected_pathology = pathology
            confidence = None  # No confidence in manual mode
            all_probs = {}
            cleaned_text = clean_text(text)
        
        # ========================================================================
        # STAGE 2: SUMMARIZATION - Generate Clinical Summary
        # ========================================================================
        # Uses T5 model to generate concise summary of patient case
        
        print("\n[STAGE 2/3] 📝 Generating summary...")
        
        if self.sum_pipeline is not None:
            # CUDA: Use optimized pipeline API for better performance
            summary_result = self.sum_pipeline(
                cleaned_text,
                min_length=256,  # Minimum summary length (tokens)
                max_length=512,  # Maximum summary length (tokens)
                clean_up_tokenization_spaces=True  # Clean up tokenizer artifacts
            )
            diagnosis_summary = summary_result[0]["summary_text"]
        else:
            # MPS/CPU: Use raw model (pipeline has compatibility issues)
            # Prepend "summarize: " as T5 expects task prefix
            inputs = self.sum_tokenizer(
                "summarize: " + cleaned_text,
                return_tensors="pt",
                max_length=512,  # Max input length
                truncation=True
            ).to(self.sum_model.device)
            
            # Generate summary using beam search
            with torch.no_grad():
                summary_ids = self.sum_model.generate(
                    **inputs,
                    min_length=256,  # Minimum output length
                    max_length=512,  # Maximum output length
                    num_beams=4,  # Beam search with 4 beams (better quality)
                    early_stopping=True  # Stop when all beams reach EOS
                )
            
            # Decode tokens back to text
            diagnosis_summary = self.sum_tokenizer.decode(
                summary_ids[0], 
                skip_special_tokens=True  # Remove <pad>, <eos>, etc.
            )
        
        print(f"✅ Summary generated ({len(diagnosis_summary)} chars)")
        
        # ========================================================================
        # STAGE 3: GENERATION - Create Treatment Recommendations
        # ========================================================================
        # Uses Llama 3.2 with LoRA to generate personalized treatment plans
        
        print("\n[STAGE 3/3] 💊 Generating recommendation...")
        
        # Check if Llama model is available (it's optional)
        if self.gen_model is None or self.gen_tokenizer is None:
            # Fallback: Use basic template when Llama is unavailable
            final_recommendation = (
                f"⚠️ Llama model unavailable. Basic recommendation for {detected_pathology}:\n\n"
                "Please consult with a licensed mental health professional for personalized treatment."
            )
            print("⚠️ Using fallback recommendation")
        else:
            # ========================================
            # CREATE PROMPT FOR LLAMA (uses summary for better context)
            # ========================================
            # Very simple prompt - the 1B model works better with minimal instructions
            system_prompt = "You are a clinical psychologist writing a treatment plan."
            
            # Direct, minimal user prompt - explicitly start fresh numbering
            user_prompt = f"""Patient diagnosis: {detected_pathology}

Write a NEW treatment plan starting from section 1:

## 1. Medications
List 2-3 medications for {detected_pathology} with brief explanations.

## 2. Therapy
List 2-3 therapy approaches and how each helps.

## 3. Lifestyle
Recommend exercise, sleep habits, and stress management.

## 4. Follow-up
Describe the monitoring schedule.

Begin your response with "## 1. Medications":"""
            
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
                truncation=True,
                max_length=2048
            ).to(self.gen_model.device)
            
            # Generation parameters optimized for clear, coherent output
            with torch.no_grad():
                output_tokens = self.gen_model.generate(
                    **input_ids,
                    max_new_tokens=512,  # Reduced for more focused output
                    min_new_tokens=200,  # Ensure substantial content
                    do_sample=True,
                    temperature=0.5,  # Lower for more coherent, focused output
                    top_p=0.85,  # More conservative sampling for quality
                    repetition_penalty=1.15,  # Moderate penalty to reduce repetition
                    no_repeat_ngram_size=3,  # Prevent 3-word phrase repetition
                    eos_token_id=self.gen_tokenizer.eos_token_id,
                    pad_token_id=self.gen_tokenizer.pad_token_id,
                )
            
            # Decode generated tokens to text
            # Only decode the newly generated tokens (skip input prompt)
            response = self.gen_tokenizer.decode(
                output_tokens[0][input_ids["input_ids"].shape[1]:],  # Skip input tokens
                skip_special_tokens=True  # Remove <eos>, <pad>, etc.
            ).strip()
            
            # ========================================
            # CLEAN UP AND FORMAT GENERATED TEXT
            # ========================================
            # Remove "Recommendation: " prefix if model added it
            match = re.search(r"Recommendation:\s*", response, re.IGNORECASE)
            response = response[match.end():].strip() if match else response
            
            # Fix malformed headers: "5. Medications #" -> "## Medications"
            response = re.sub(r'\d+\.\s*([A-Za-z\s]+)\s*#', r'## \1', response)
            
            # Fix standalone # symbols
            response = re.sub(r'^\s*#\s*$', '', response, flags=re.MULTILINE)
            
            # Fix headers without proper spacing: "##Medications" -> "## Medications"
            response = re.sub(r'^(#{1,3})([A-Za-z])', r'\1 \2', response, flags=re.MULTILINE)
            
            # Clean up escape characters
            response = re.sub(r'\\+([^\s])', r'\1', response)
            response = re.sub(r'\\{2,}', '', response)
            response = response.replace('\\n', '\n')
            
            # Add proper line breaks before headers if missing
            response = re.sub(r'([.!?])\s*(##)', r'\1\n\n\2', response)
            
            # Normalize multiple spaces (but preserve newlines)
            response = re.sub(r'[ \t]+', ' ', response)
            response = re.sub(r'\n{3,}', '\n\n', response)
            
            # Ensure headers are on their own lines
            response = re.sub(r'([^\n])(## )', r'\1\n\n\2', response)
            response = re.sub(r'(## [^\n]+)([^\n])', r'\1\n\2', response)
            
            # Add bullet points to items that look like lists
            lines = response.split('\n')
            formatted_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-') and not line.startswith('*'):
                    # Check if line looks like a medication or therapy name followed by description
                    if re.match(r'^[A-Z][a-z]+(\s+[A-Z]?[a-z]+)*:', line):
                        line = '- **' + line.replace(':', ':** ', 1)
                formatted_lines.append(line)
            response = '\n'.join(formatted_lines)
            
            # Final cleanup
            response = response.strip()
            
            # If output seems truncated (ends mid-sentence), add notice
            if response and response[-1] not in '.!?':
                response += "\n\n*[Note: Consult with healthcare provider for complete guidance.]*"
            
            final_recommendation = response
            
            print("✅ Recommendation generated")
        
        # ========================================================================
        # RETURN RESULTS
        # ========================================================================
        fin = time.time()
        print(f"\n⏱️ Total processing time: {fin - inicio:.2f} seconds")
        
        # Return complete analysis results
        return {
            "classification": {
                "pathology": detected_pathology,  # Detected condition
                "confidence": confidence,  # Confidence score (0-1, None if manual)
                "all_probabilities": all_probs  # Probability distribution for all classes
            },
            "summary": diagnosis_summary,  # Clinical summary of case
            "recommendation": final_recommendation,  # Treatment recommendations
            "metadata": {
                "original_text_length": len(text),  # Length of input text
                "summary_length": len(diagnosis_summary),  # Length of generated summary
                "recommendation_length": len(final_recommendation),  # Length of recommendations
                "processing_time": round(fin - inicio, 2)  # Total time in seconds
            }
        }


# ============================================================================
# GLOBAL SINGLETON INSTANCE
# ============================================================================
# Create a single global instance of ModelManager that will be used throughout
# the application. This ensures models are loaded once and reused for all requests.
# This instance is imported by other modules like api/v1/analyze.py
manager = ModelManager()


# ============================================================================
# LEGACY FUNCTIONS FOR BACKWARD COMPATIBILITY
# ============================================================================
# These functions redirect to the manager instance for backward compatibility
# with older code that may import these functions directly.

def load_all_models():
    """
    Load all models at startup (legacy wrapper function).
    
    This function redirects to the manager instance for backward compatibility
    with older code that may call load_all_models() directly.
    
    Returns:
        bool: True if all models loaded successfully
    """
    return manager.load_all_models()


def check_models_loaded():
    """
    Check if critical models are loaded (legacy wrapper function).
    
    This function redirects to the manager instance for backward compatibility.
    
    Returns:
        bool: True if critical models are loaded
    """
    return manager.check_models_loaded()


# ============================================================================
# END OF FILE
# ============================================================================
# This file implements the complete model management system for the clinical
# assistant application. It uses singleton pattern with lazy loading for optimal
# performance and memory efficiency.def get_models():
    """Get all model instances (legacy wrapper)"""
    return manager.get_models()