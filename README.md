# Clinical Mental Health Assistant

<!--
================================================================================
PROJECT OVERVIEW
================================================================================
An AI-Powered Diagnostic Support Tool designed to assist healthcare 
professionals in analyzing clinical mental health cases.

This project demonstrates a complete machine learning pipeline that processes 
clinical text through three stages:
1. CLASSIFICATION - Identifies which mental health condition(s) are present
2. SUMMARIZATION - Extracts key clinical information into concise summaries  
3. GENERATION - Produces evidence-based treatment recommendations

Technical Stack:
- Backend: FastAPI (Python web framework for REST API)
- ML Framework: PyTorch with Hugging Face Transformers
- Models: BERT-based classifier, T5 summarizer, Llama 3.2 generator
- Frontend: Vanilla HTML/CSS/JavaScript (chat interface)
- Deployment: Docker Compose OR local venv with GPU acceleration

Intended Audience:
- Healthcare professionals seeking AI-assisted case analysis
- Researchers studying NLP applications in mental health
- Students learning about transformer models and ML pipelines
- Developers building similar clinical decision support systems

⚠️ IMPORTANT: This tool is for research and educational purposes only.
It should NOT replace professional medical judgment or be used for actual 
clinical diagnosis without proper validation and regulatory approval.
================================================================================
-->

AI-Powered Diagnostic Support Tool for Healthcare Professionals

## 🎯 Overview

This application provides an **end-to-end clinical mental health analysis pipeline** that combines three transformer models:

- **Classification**: Identifies mental health conditions from clinical text
  - Detects 5 pathologies: Depression, Anxiety, Bipolar Disorder, BPD, Schizophrenia
  - Uses fine-tuned BERT-based model
  - Outputs confidence scores for each condition

- **Summarization**: Generates concise clinical summaries using T5
  - Extracts key symptoms, observations, and patient history
  - Reduces verbose clinical notes to essential information
  - Uses fine-tuned T5-base model (checkpoint-799)

- **Generation**: Creates evidence-based treatment recommendations using Llama 3.2
  - Generates personalized treatment plans based on diagnosis
  - Considers patient-specific factors and contraindications
  - Uses Llama 3.2-1B-Instruct with optional LoRA fine-tuning

## 🏗️ Architecture

<!--
The application follows a client-server architecture with clear separation 
of concerns:

FRONTEND (Static Web App)
- HTML/CSS/JavaScript chat interface running on port 3000
- Communicates with backend via REST API
- Displays real-time progress during analysis
- No server-side processing, just static file serving

BACKEND (FastAPI Application)
- REST API server on port 8000
- Handles model loading, inference, and response generation
- Three ML models loaded into memory at startup
- GPU-accelerated inference when available (MPS on Apple Silicon)

ML PIPELINE FLOW:
User Input → Classification → Summarization → Generation → Treatment Plan
     ↓              ↓               ↓              ↓              ↓
  Clinical    Detect       Extract Key    Generate        Final
   Text       Pathology    Information    Recommendations  Response

DEVICE CONFIGURATION:
- Classification Model: Runs on MPS (Apple Silicon GPU) or CUDA (NVIDIA)
- T5 Summarizer: Runs on MPS/CUDA for speed
- Llama Generator: Runs on CPU (MPS has numerical instability issues)
  
This hybrid approach balances speed and stability across different hardware.
-->

### Backend Architecture (FastAPI)

The backend is a **Python FastAPI application** that orchestrates three ML models:

- **Classification Model** (`backend/models/classifier/`)
  - Fine-tuned BERT-based transformer
  - Input: Clinical text (50+ characters)
  - Output: 5-class probabilities + confidence scores
  - Device: MPS (Apple Silicon) or CUDA (NVIDIA)

- **T5 Summarizer** (`backend/models/t5_summarizer/`)
  - Fine-tuned T5-base at checkpoint-799
  - Input: Clinical text + classification result
  - Output: Concise clinical summary (~60% of input length)
  - Device: MPS or CUDA

- **Llama 3.2 Generator** (`backend/models/llama_peft/`)
  - Llama 3.2-1B-Instruct base model
  - Optional: LoRA adapter for fine-tuning (disabled on MPS)
  - Input: Summary + diagnosis
  - Output: Treatment recommendations (max 256 tokens)
  - Device: CPU (for stability)

**API Endpoints:**
- `POST /api/v1/analyze` - Main analysis endpoint
- `GET /api/v1/health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)

### Frontend Architecture

- **Modern chat-based interface** inspired by Gradio
- **Real-time progress indicators** show which stage is running
- **Example clinical cases** for quick testing (Depression, Anxiety, Bipolar)
- **Two modes:**
  - **Auto mode**: System automatically classifies condition
  - **Manual mode**: User selects known pathology
- **Responsive design** works on desktop and mobile
- **No dependencies**: Pure HTML/CSS/JavaScript (no build step)

## 📋 Requirements

<!--
SYSTEM REQUIREMENTS EXPLANATION:

Python 3.8+:
- Minimum version for modern transformers library features
- Tested with Python 3.11 (recommended)
- Type hints and async/await support needed for FastAPI

GPU (Optional but Recommended):
- Apple Silicon (M1/M2/M3): Uses MPS (Metal Performance Shaders)
- NVIDIA: Uses CUDA (requires CUDA 11.8+ and appropriate drivers)
- Without GPU: Falls back to CPU (4-5x slower)

RAM Requirements:
- 16GB minimum: Can run all models but may be tight
- 32GB recommended: Comfortable for development and testing
- Model memory footprint: ~4-6GB total (classifier + T5 + Llama)

Disk Space:
- ~3GB for models (classifier 500MB, T5 900MB, Llama 2.5GB)
- ~2GB for Python dependencies
- ~5GB recommended total with workspace

PYTHON DEPENDENCIES:

Core ML Libraries:
- transformers 4.57.2: Hugging Face model library (Llama 3.2 support)
- torch 2.9.1: PyTorch ML framework with MPS support
- peft 0.7.0: Parameter-Efficient Fine-Tuning (LoRA adapters)
- accelerate 0.25.0: Distributed training and mixed precision

API Framework:
- fastapi 0.104.1: Modern Python web framework
- uvicorn 0.24.0: ASGI server for FastAPI
- pydantic: Data validation (included with FastAPI)

Optional (for training):
- bitsandbytes: 4-bit quantization (Linux/Windows only, not needed for inference)

See backend/requirements.txt for complete list with exact versions.
All versions pinned via pip freeze for reproducibility.
-->

### System Requirements

- **Python**: 3.8+ (tested with 3.11, recommended)
- **Operating System**: 
  - macOS (M1/M2/M3 with MPS acceleration)
  - Linux (CUDA support for NVIDIA GPUs)
  - Windows (CUDA support, WSL2 recommended)
- **Memory**: 16GB+ RAM (32GB recommended for comfortable development)
- **Storage**: 10GB+ free disk space
  - Models: ~3GB (classifier + T5 + Llama)
  - Dependencies: ~2GB
  - Working space: ~5GB
- **GPU** (Optional):
  - Apple Silicon: MPS (Metal Performance Shaders) - automatic
  - NVIDIA: CUDA 11.8+ with appropriate drivers
  - Without GPU: Falls back to CPU (4-5x slower but functional)

### Python Dependencies

**Core ML Stack:**
- `transformers==4.57.2` - Hugging Face Transformers (Llama 3.2 support)
- `torch==2.9.1` - PyTorch with Apple Silicon MPS support
- `peft==0.7.0` - Parameter-Efficient Fine-Tuning (LoRA)
- `accelerate==0.25.0` - Hardware acceleration and distributed training

**Web Framework:**
- `fastapi==0.104.1` - Modern Python web framework
- `uvicorn==0.24.0` - ASGI server for FastAPI
- `pydantic` - Data validation (included with FastAPI)

**Utilities:**
- `python-multipart` - Form data parsing
- `python-dotenv` - Environment variable management

See **`backend/requirements.txt`** for complete list with exact versions.  
All versions are pinned via `pip freeze` for reproducibility.

## 🚀 Installation

<!--
INSTALLATION OVERVIEW:

There are two installation methods:
1. LOCAL (Recommended for development): Uses venv with GPU acceleration
2. DOCKER (Recommended for deployment): Containerized, CPU-based

Choose LOCAL if:
- You have Apple Silicon Mac or NVIDIA GPU
- You want faster inference with GPU acceleration
- You're developing or testing models

Choose DOCKER if:
- You want easy deployment without dependency management
- You're deploying to cloud services
- You don't need GPU acceleration (CPU is acceptable)

The steps below cover LOCAL installation. For Docker, see DOCKER_GUIDE.md
-->

### Method 1: Local Installation (Recommended for Development)

This method provides **GPU acceleration** and faster inference.

#### 1. Clone the Repository

```bash
# Clone the repository (replace with your actual repo URL)
git clone <your-repo-url>
cd clinical_assistant
```

#### 2. Set Up Python Environment
```bash
# Navigate to backend directory
cd backend

# Create isolated Python environment (prevents dependency conflicts)
python -m venv venv

# Activate the environment
source venv/bin/activate  # macOS/Linux
# OR on Windows:
# venv\Scripts\activate

# Install all dependencies (takes 5-10 minutes first time)
# This installs ~70 packages including PyTorch, transformers, FastAPI, etc.
pip install -r requirements.txt

# Verify installation
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
```

**Expected output:**
```
PyTorch: 2.9.1
Transformers: 4.57.2
```

#### 3. Set Up Models

<!--
MODEL SETUP EXPLANATION:

The application requires three trained models. You have two options:

OPTION A: Download from Google Drive (if provided)
- Models are already trained and ready to use
- Just copy to backend/models/ directory
- See MODEL_SETUP.md for detailed instructions

OPTION B: Train your own models
- Requires clinical mental health datasets
- Training takes several hours on GPU
- Not covered in this README (see training notebooks)

Each model has specific required files:
- config.json: Model architecture configuration
- model weights: .safetensors or .bin files
- tokenizer files: vocab, special tokens, etc.
- metadata: training info, label maps, etc.

Missing even one file will cause loading errors.
-->

You need to place your trained models in the `backend/models/` directory:

```
backend/models/
├── classifier/              # Classification model (~500MB)
│   ├── config.json         # Model architecture config
│   ├── model.safetensors   # Model weights
│   ├── label_map.json      # Class labels mapping
│   ├── tokenizer.json      # Tokenizer vocabulary
│   ├── vocab.txt           # WordPiece vocabulary
│   └── training_metadata.json  # Training history
│
├── t5_summarizer/          # T5 summarization model (~900MB)
│   ├── config.json         # T5 architecture config
│   ├── model.safetensors   # Model weights (checkpoint-799)
│   ├── spiece.model        # SentencePiece tokenizer
│   ├── tokenizer.json      # Tokenizer config
│   └── trainer_state.json  # Training checkpoint info
│
└── llama_peft/             # Llama LoRA adapter (~50MB)
    ├── adapter_config.json # LoRA configuration
    ├── adapter_model.safetensors  # LoRA weights
    ├── chat_template.jinja # Chat formatting template
    └── trainer_state.json  # Training checkpoint info
```

**📥 Download Models:**

See **[MODEL_SETUP.md](MODEL_SETUP.md)** for detailed instructions on:
- Downloading models from Google Drive
- Copying models from Google Colab
- Verifying model files are complete
- Troubleshooting missing files

**⚙️ Custom Model Paths:**

If you want to use different model locations, update `backend/app/core/config.py`:
```python
# In backend/app/core/config.py
CLASSIFICATION_MODEL_PATH = MODELS_DIR / "classifier"  # Or your custom path
T5_SUMMARIZATION_PATH = MODELS_DIR / "t5_summarizer"
LLAMA_LORA_CHECKPOINT_PATH = MODELS_DIR / "llama_peft"
```

#### 4. Hugging Face Authentication (for Llama 3.2)

<!--
HUGGING FACE AUTHENTICATION:

Llama models are "gated" by Meta, requiring:
1. Hugging Face account (free)
2. Accept Llama 3.2 license agreement on HF website
3. Provide HF_TOKEN for authentication

Why needed:
- Meta restricts Llama access for legal/ethical reasons
- Ensures users agree to acceptable use policies
- Tracks model usage for research purposes

Without authentication:
- Backend will fail to load Llama model
- You'll see "401 Unauthorized" errors
- Other models (classifier, T5) will still work

Get your token at: https://huggingface.co/settings/tokens
-->

**Llama 3.2 is a gated model** requiring Hugging Face authentication:

**Step 1:** Create a Hugging Face account at https://huggingface.co/join

**Step 2:** Accept Llama 3.2 license:
- Visit https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
- Click "Agree and access repository"
- Wait for approval (usually instant)

**Step 3:** Get your access token:
- Go to https://huggingface.co/settings/tokens
- Create a new token with "Read" permissions
- Copy the token (starts with `hf_...`)

**Step 4:** Set your token (choose one method):

```bash
# Method A: Using huggingface-cli (recommended)
huggingface-cli login
# Paste your token when prompted

# Method B: Using environment variable
export HF_TOKEN="hf_your_token_here"  # macOS/Linux
# OR on Windows:
# set HF_TOKEN=hf_your_token_here

# Method C: Create .env file in project root
echo 'HF_TOKEN=hf_your_token_here' > .env
```

**Verify authentication:**
```bash
huggingface-cli whoami
# Should show your username
```

## 🎮 Usage

<!--
USAGE OVERVIEW:

The application consists of two servers that must both be running:

BACKEND SERVER (Port 8000):
- Loads ML models into memory (takes 2-5 minutes)
- Processes analysis requests via REST API
- Must start first before frontend

FRONTEND SERVER (Port 3000):
- Serves static HTML/CSS/JavaScript files
- Sends requests to backend API
- Can start in any order, but needs backend to function

STARTUP OPTIONS:

Option A: Use convenience scripts (recommended)
- ./start_backend.sh - Automatic setup and validation
- ./start_frontend.sh - Simple server startup
- Best for beginners

Option B: Manual startup (for development)
- Direct uvicorn/python commands
- More control over ports and options
- Best for development and debugging

Expected startup time:
- Backend: 2-5 minutes (model loading)
- Frontend: Instant (static files only)
- Total: ~5 minutes from cold start
-->

### Quick Start (Recommended)

Use the provided startup scripts:

```bash
# Terminal 1: Start backend (loads models, may take 2-5 minutes)
./start_backend.sh

# Terminal 2: Start frontend (instant)
./start_frontend.sh
```

Then open http://localhost:3000 in your browser.

### Manual Startup

If you prefer manual control:

#### Start the Backend API

```bash
# Make sure virtual environment is activated
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# Start FastAPI server with auto-reload (development mode)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# You'll see model loading messages:
# Loading classification model...
# Loading T5 summarizer...  
# Loading Llama generator...
# Application startup complete (takes 2-5 minutes)
```

**What happens during startup:**
1. FastAPI initializes application
2. Loads classification model to GPU (~30 seconds)
3. Loads T5 summarizer to GPU (~1 minute)
4. Loads Llama base model to CPU (~2 minutes)
5. Optionally loads LoRA adapter (if enabled)
6. Starts accepting requests

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health

### Start the Frontend

Option 1: Simple HTTP Server (Python)
```bash
cd frontend
python -m http.server 3000
```

Option 2: Node.js HTTP Server
```bash
cd frontend
npx http-server -p 3000
```

Then open: http://localhost:3000

## 📝 API Endpoints

### POST `/api/v1/analyze`

Analyze a clinical case and generate treatment recommendations.

**Request Body:**
```json
{
  "text": "Patient clinical observations (minimum 50 characters)",
  "auto_classify": true,
  "pathology": null
}
```

**Response:**
```json
{
  "classification": {
    "pathology": "Depression",
    "confidence": 0.89,
    "all_probabilities": {
      "Depression": 0.89,
      "Anxiety": 0.05,
      "...": "..."
    }
  },
  "summary": "Clinical summary text...",
  "recommendation": "Treatment recommendation text...",
  "metadata": {
    "original_text_length": 450,
    "summary_length": 180,
    "recommendation_length": 320
  }
}
```

### GET `/api/v1/health`

Check API and model status.

## 🎨 Frontend Features

### Chat Interface
- Clean, professional design inspired by Gradio
- Message history with user/bot avatars
- Loading indicators during analysis
- Animated transitions

### Analysis Modes
1. **Automatic Classification**: AI detects the mental health condition
2. **Manual Selection**: Clinician selects the diagnosis

### Example Cases
Pre-loaded clinical scenarios for:
- Depression
- Anxiety
- Bipolar Disorder

## 🔧 Configuration

<!--
CONFIGURATION MANAGEMENT:

All configuration is centralized in backend/app/core/config.py for easy
customization. This includes:
- Model paths
- Device selection (GPU/CPU)
- Hyperparameters for each model
- API settings

Why centralized config:
- Single source of truth
- Easy to adjust without searching through code
- Environment-specific settings possible
- Type hints for validation

Parameters explained below with guidance on when/why to change them.
-->

### Model Parameters

Edit **`backend/app/core/config.py`** to adjust behavior:

```python
# ===== CLASSIFICATION PARAMETERS =====
# How much text to consider (longer = more context but slower)
CLASSIFICATION_MAX_LENGTH = 192  # tokens (roughly 150 words)

# Minimum confidence to accept auto-classification
CLASSIFICATION_CONFIDENCE_THRESHOLD = 0.6  # 60%
# Lower = more sensitive (may misclassify)
# Higher = more conservative (may reject valid cases)

# ===== SUMMARIZATION PARAMETERS =====
# Summary length constraints
SUMMARIZATION_MIN_LENGTH = 128  # tokens (roughly 100 words)
SUMMARIZATION_MAX_LENGTH = 256  # tokens (roughly 200 words)
# Dynamic sizing: actual length = 60% of input length
# These are min/max bounds to prevent too short/long summaries

# ===== GENERATION PARAMETERS =====
# Maximum length of treatment recommendation
GENERATION_MAX_NEW_TOKENS = 512  # tokens (roughly 400 words)
# Longer = more detailed but slower

# Generation sampling parameters
GENERATION_TEMPERATURE = 0.7  # Creativity (0.0-1.0)
# Lower = more conservative/repetitive
# Higher = more creative/random
# 0.7 = balanced for clinical recommendations

GENERATION_TOP_P = 0.9  # Nucleus sampling (0.0-1.0)
# Controls diversity of word choices
# 0.9 = consider top 90% probable tokens

# ===== DEVICE CONFIGURATION =====
# Auto-detects: "mps" (Apple Silicon), "cuda" (NVIDIA), or "cpu"
# Override if needed:
# DEVICE = "cpu"  # Force CPU mode (slower but works everywhere)
```

### Device Override

To force CPU mode (if GPU causing issues):

```python
# In backend/app/core/config.py, add at top:
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Hide GPU from PyTorch
DEVICE = "cpu"
```

### Frontend API URL

Edit **`frontend/js/app.js`** if backend on different host/port:

```javascript
// Change this if deploying backend elsewhere
const API_URL = "http://localhost:8000/api/v1/analyze";

// For production (example):
// const API_URL = "https://api.yourdomain.com/api/v1/analyze";
```

### Environment Variables

Create **`.env`** file in project root for sensitive config:

```bash
# Hugging Face authentication
HF_TOKEN=hf_your_token_here

# Optional: Use local Llama model instead of downloading
# LLAMA_BASE_MODEL_PATH=/path/to/local/llama/model
# LLAMA_USE_LOCAL_FILES_ONLY=true

# Optional: Disable LoRA adapter (use base Llama only)
# LLAMA_USE_ADAPTER=false
```

## 📊 Model Information

### Classification Model
- **Base**: Fine-tuned transformer (e.g., BERT, RoBERTa)
- **Classes**: 5 mental health conditions
- **Input**: Clinical observations text
- **Output**: Pathology + confidence scores

### T5 Summarizer
- **Base**: T5-base
- **Task**: Extractive/abstractive summarization
- **Input**: Full clinical text
- **Output**: Concise clinical summary

### Llama 3 Generator
- **Base**: Llama-3.2-1B-Instruct
- **Method**: QLoRA (4-bit quantization)
- **Task**: Treatment recommendation generation
- **Input**: Pathology + clinical summary
- **Output**: Structured treatment plan

## 🐛 Troubleshooting

<!--
TROUBLESHOOTING PHILOSOPHY:

This section covers the most common issues users encounter.
For each problem, we provide:
- What the error means
- Why it happens
- Step-by-step solution
- How to prevent it

General debugging approach:
1. Read error message carefully
2. Check terminal logs (backend and frontend)
3. Test components individually (API health check)
4. Verify prerequisites (models, token, dependencies)
5. Try minimal reproduction (curl test)
6. Check system resources (RAM, disk space)

Most issues fall into categories:
- Setup (models not found, wrong paths)
- Resources (out of memory, disk full)
- Network (ports, firewalls, CORS)
- Authentication (HF token issues)
- Dependencies (version mismatches)
-->

### Models Not Loading

**Error messages:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'backend/models/classifier/config.json'
Error: Models not loaded correctly
OSError: Can't load config for 'backend/models/t5_summarizer'
```

**What it means:**  
Backend can't find model files in expected directories.

**Why it happens:**
- Models not copied from Google Drive
- Wrong directory structure  
- Typo in config.py paths
- Files corrupted during copy

**Solution:**
1. **Verify models exist:**
   ```bash
   ls -la backend/models/classifier/
   ls -la backend/models/t5_summarizer/
   ls -la backend/models/llama_peft/
   ```

2. **Check required files:**
   ```bash
   # Each model needs specific files:
   # classifier: config.json, model.safetensors, tokenizer files
   # t5_summarizer: config.json, model.safetensors, spiece.model
   # llama_peft: adapter_config.json, adapter_model.safetensors
   ```

3. **Verify paths in config.py:**
   ```python
   # In backend/app/core/config.py
   print(CLASSIFICATION_MODEL_PATH)  # Should exist
   print(T5_SUMMARIZATION_PATH)      # Should exist
   print(LLAMA_LORA_CHECKPOINT_PATH) # Should exist
   ```

4. **Re-copy models:**
   See [MODEL_SETUP.md](MODEL_SETUP.md) for detailed instructions

### CUDA/MPS Out of Memory

**Error messages:**
```
RuntimeError: CUDA out of memory. Tried to allocate 2.50 GiB
torch.cuda.OutOfMemoryError
RuntimeError: MPS backend out of memory
```

**What it means:**  
GPU doesn't have enough memory to load models.

**Why it happens:**
- GPU has <8GB VRAM
- Other programs using GPU (browsers, other ML processes)
- Multiple models loaded simultaneously
- Memory leak from previous run

**Solution:**

1. **Check GPU memory:**
   ```bash
   # NVIDIA GPU:
   nvidia-smi
   
   # Apple Silicon (no direct equivalent, use Activity Monitor)
   ```

2. **Close other GPU applications:**
   - Chrome/browsers with GPU acceleration
   - Other Python/ML processes
   - Games or graphics software

3. **Restart to clear memory:**
   ```bash
   # Sometimes only fix for fragmented memory
   sudo reboot
   ```

4. **Use CPU mode (slower but reliable):**
   ```python
   # In backend/app/core/config.py
   DEVICE = "cpu"
   ```

5. **Or use Docker (CPU-based):**
   ```bash
   # Docker doesn't access MPS on macOS
   docker-compose up
   ```

### Port Already in Use

**Error messages:**
```
ERROR: [Errno 48] Address already in use
OSError: [Errno 98] Address already in use
uvicorn.error: Cannot bind to port 8000
```

**What it means:**  
Another process is already using port 8000 or 3000.

**Why it happens:**
- Previous server didn't shut down cleanly
- Another application using same port
- Multiple terminals trying to start same service

**Solution:**

```bash
# macOS/Linux: Find and kill process
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend

# Or see what's using the port:
lsof -i:8000  # Shows process details

# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Prevention:**
- Always use Ctrl+C to stop servers gracefully
- Check no processes running before starting:
  ```bash
  lsof -ti:8000  # Should return nothing
  ```

### HuggingFace Token Errors

**Error messages:**
```
401 Client Error: Unauthorized for url
OSError: You are trying to access a gated repo
huggingface_hub.errors.HfHubHTTPError: 401 Unauthorized
```

**What it means:**  
Can't authenticate with HuggingFace to download Llama model.

**Why it happens:**
- No HF_TOKEN set
- Token expired or invalid
- Haven't accepted Llama 3.2 license agreement
- Token has wrong permissions

**Solution:**

1. **Accept Llama 3.2 license:**
   - Visit: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
   - Click "Agree and access repository"
   - Wait for approval (usually instant)

2. **Get/update your token:**
   - Go to: https://huggingface.co/settings/tokens
   - Create new token with "Read" permissions
   - Copy token (starts with `hf_...`)

3. **Set token:**
   ```bash
   # Method 1: Environment variable
   export HF_TOKEN="hf_your_token_here"
   
   # Method 2: HF CLI (persists)
   huggingface-cli login
   
   # Method 3: .env file
   echo 'HF_TOKEN=hf_your_token_here' > .env
   ```

4. **Verify authentication:**
   ```bash
   huggingface-cli whoami
   # Should show your username
   ```

### Slow Performance

**Symptoms:**
- Analysis takes >2 minutes per case
- High CPU usage
- Fans running loud

**Why it happens:**
- Running on CPU instead of GPU
- Models not optimized
- System thermal throttling

**Solution:**

1. **Verify GPU is being used:**
   ```python
   # Check in backend logs at startup
   # Should see: "Device: mps" or "Device: cuda"
   # If "Device: cpu", GPU not detected
   ```

2. **Check GPU availability:**
   ```python
   python3 -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
   python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
   ```

3. **Performance expectations:**
   - With GPU (MPS/CUDA): ~50-60 seconds per analysis
   - With CPU: ~3-5 minutes per analysis
   - Docker (CPU): ~3-5 minutes per analysis

### Frontend Not Connecting to Backend

**Symptoms:**
- "Failed to connect" errors in browser
- Network errors in console (F12)
- Infinite loading spinner

**Why it happens:**
- Backend not running
- Wrong API URL in frontend
- CORS issues
- Firewall blocking connection

**Solution:**

1. **Verify backend is running:**
   ```bash
   curl http://localhost:8000/api/v1/health
   # Should return JSON with status
   ```

2. **Check browser console (F12):**
   - Look for network errors
   - Check if request reaches backend

3. **Verify API URL:**
   ```javascript
   // In frontend/js/app.js
   const API_URL = "http://localhost:8000/api/v1/analyze";
   // Must match backend address
   ```

4. **Check CORS settings:**
   ```python
   # In backend/app/main.py
   # Should allow localhost:3000
   ```

5. **Test with curl directly:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{"text": "Test case description here...", "auto_classify": true}'
   ```

### Dependency Version Conflicts

**Error messages:**
```
ImportError: cannot import name 'XXX' from 'transformers'
ModuleNotFoundError: No module named 'peft'
```

**Solution:**

```bash
# Recreate virtual environment with exact versions
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verify critical versions
pip list | grep -E 'torch|transformers|peft'
# Should match requirements.txt versions
```

### Method 2: Docker Deployment (Recommended for Production)

<!--
DOCKER DEPLOYMENT:

Docker provides:
- Consistent environment across machines
- Easy deployment to cloud platforms
- No Python version conflicts
- Isolated from host system

Trade-offs:
- No GPU acceleration on macOS Docker
- Slightly slower (CPU-only)
- Larger disk usage (~8GB)

Best for:
- Production deployment
- Cloud hosting
- Team development (consistent env)
- When GPU not available

See DOCKER_GUIDE.md for comprehensive deployment guide including:
- Local Docker setup
- Cloud deployment (GCP, AWS, Azure)
- Production configuration
- Security best practices
-->

For containerized deployment, see **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)** which covers:

- **Local Docker Setup**: Run with `docker-compose up`
- **Cloud Deployment**: Step-by-step for GCP, AWS, Azure, DigitalOcean
- **Production Config**: HTTPS, authentication, monitoring
- **Security Checklist**: HIPAA/GDPR compliance considerations

**Quick Docker Start:**
```bash
# Ensure models are in backend/models/ and .env has HF_TOKEN
docker-compose up --build

# Access:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

**Note**: Docker on macOS cannot access MPS (Apple Silicon GPU), so models run on CPU (slower but stable).

---

## 🔒 Important Notes

<!--
LEGAL AND ETHICAL CONSIDERATIONS:

This section is CRITICAL for anyone deploying this system.
It covers legal, ethical, and safety considerations.

Key points:
1. Research/educational tool, not clinical device
2. No substitute for professional judgment
3. Data privacy and compliance requirements
4. Model limitations and biases
5. Liability and risk management

DO NOT deploy for real clinical use without:
- Legal review
- Medical oversight
- Regulatory approval
- Risk assessment
- Insurance coverage
-->

### ⚠️ Professional Use Only

This tool is designed as a **clinical decision support system** for mental health  
professionals. It is intended to assist, not replace, professional clinical judgment.

**Important Limitations:**
- This is a **research/educational tool**, not a medical device
- Not FDA-cleared or CE-marked for clinical diagnosis
- Should not be the sole basis for treatment decisions
- Requires professional interpretation and validation
- Not suitable for emergency or crisis situations

**Appropriate Use Cases:**
- ✅ Research and academic studies
- ✅ Clinical education and training
- ✅ Preliminary screening (with professional review)
- ✅ Documentation assistance for clinicians
- ❌ NOT for patient self-diagnosis
- ❌ NOT for emergency triage
- ❌ NOT as replacement for clinical assessment

### 🔐 Data Privacy & Compliance

**CRITICAL**: This application handles sensitive mental health data.

**Before using with real patient data:**

1. **Legal Compliance:**
   - **HIPAA** (US): Requires BAA, encryption, audit logs, access controls
   - **GDPR** (EU): Need consent, right to deletion, data portability
   - **HITECH Act**: Breach notification requirements
   - Consult legal counsel for your jurisdiction

2. **Security Requirements:**
   - ✅ End-to-end encryption (HTTPS)
   - ✅ User authentication and authorization
   - ✅ Audit logging of all access
   - ✅ Secure data storage and backup
   - ✅ Incident response plan
   - ✅ Regular security audits

3. **Patient Consent:**
   - Explicit consent for AI-assisted analysis
   - Explanation of how AI is used
   - Right to opt-out or request human-only review
   - Clear data retention and deletion policies

4. **Current Status:**
   - ⚠️ **NOT HIPAA/GDPR compliant** out of the box
   - No authentication implemented
   - No encryption at rest
   - No audit logging
   - **Requires significant additional work for production**

**Recommendations:**
- Use anonymized/de-identified data for testing
- Do not store real patient data without proper safeguards
- Deploy on compliant infrastructure (AWS HIPAA, GCP Healthcare API, etc.)
- Implement proper access controls and audit trails

### 🤖 Model Limitations & Biases

**Understand the limitations before deployment:**

1. **Training Data Biases:**
   - Models trained on specific datasets may not generalize
   - Potential biases related to demographics, culture, language
   - May underperform on underrepresented populations
   - Clinical terminology and diagnostic criteria may vary

2. **Performance Variability:**
   - Accuracy depends on text quality and completeness
   - May struggle with ambiguous or complex cases
   - Performance degrades with very short or very long text
   - Not validated against clinical gold standard

3. **False Positives/Negatives:**
   - Model predictions are probabilistic, not definitive
   - Can misclassify or miss conditions
   - Confidence scores are not calibrated probabilities
   - Always requires professional verification

4. **Ethical Considerations:**
   - AI should augment, not replace, human expertise
   - Risk of over-reliance on automated recommendations
   - Potential for harm if used incorrectly
   - Need for explainability and transparency

**Best Practices:**
- Always verify AI recommendations with clinical expertise
- Use as one data point among many
- Document when AI is used in clinical decisions
- Monitor for systematic errors or biases
- Regularly evaluate performance on diverse cases

### ⚖️ Liability & Risk Management

**Using this system involves risks:**

- **No Warranty**: Provided "as-is" without guarantees
- **User Responsibility**: You are responsible for how you use this tool
- **Medical Liability**: Clinician retains full responsibility for patient care
- **No Support**: This is open-source software, no official support
- **Regulatory**: May require FDA/CE approval for clinical use in your jurisdiction

**Risk Mitigation:**
- Treat as experimental/research tool only
- Never use as sole diagnostic criterion
- Maintain proper clinical documentation
- Have professional liability insurance
- Follow institutional review board (IRB) protocols for research
- Consult legal and regulatory experts

## 📚 Documentation

This project includes comprehensive documentation:

- **[README.md](README.md)** (this file) - Complete project overview and setup
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[MODEL_SETUP.md](MODEL_SETUP.md)** - Detailed model installation guide
- **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)** - Docker deployment and cloud hosting
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical architecture details

## 🎓 Learning Resources

**ML & NLP:**
- [Hugging Face Course](https://huggingface.co/course) - Transformers fundamentals
- [FastAPI Documentation](https://fastapi.tiangolo.com) - API development
- [PyTorch Tutorials](https://pytorch.org/tutorials/) - Deep learning basics

**Clinical NLP:**
- Papers on mental health classification
- Clinical text summarization research
- Ethics of AI in healthcare

**Deployment:**
- Docker documentation
- Cloud platform guides (GCP, AWS, Azure)
- Production ML best practices

## 📄 License

**MIT License** (or specify your license)

```
Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

[Full MIT License text...]
```

**Note**: Models may have separate licenses (check model cards on HuggingFace).

## 👥 Contributors

- **[Your Name]** - Initial development and implementation
- **[Team Members]** - Model training, data preparation, etc.

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📞 Support & Contact

**For Issues:**
- 🐛 **Bug Reports**: Open an issue on GitHub
- 💡 **Feature Requests**: Discuss in GitHub Discussions
- 📖 **Documentation**: Check documentation files first

**For Questions:**
- 💬 **General Questions**: GitHub Discussions
- 📧 **Private Inquiries**: [your-email@example.com]

**Response Time:**
- Best effort support (open-source project)
- Check existing issues before creating new ones
- Provide complete information (OS, Python version, error messages, logs)

## 🙏 Acknowledgments

This project builds on incredible work by the open-source community:

**Frameworks & Libraries:**
- [Hugging Face Transformers](https://github.com/huggingface/transformers) - ML model library
- [PyTorch](https://pytorch.org/) - Deep learning framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Uvicorn](https://www.uvicorn.org/) - ASGI server

**Models:**
- [Meta AI](https://ai.meta.com/) - Llama 3.2 foundation models
- [Google Research](https://research.google/) - T5 architecture
- [Hugging Face](https://huggingface.co/) - Model hosting and distribution

**Inspiration:**
- Gradio for chat interface design
- Clinical NLP research community
- Open-source mental health informatics projects

**Special Thanks:**
- Dataset providers and annotators
- Clinical professionals who provided domain expertise
- Beta testers and early users
- Open-source contributors

## 🌟 Star History

If you find this project useful, please consider:
- ⭐ Starring the repository
- 🔀 Forking for your own experiments
- 📢 Sharing with others
- 🤝 Contributing improvements

## 📈 Project Stats

- **Lines of Code**: ~2,500 (Python + JavaScript)
- **Models**: 3 (Classification, Summarization, Generation)
- **Total Model Size**: ~3GB
- **API Endpoints**: 2 (analyze, health)
- **Documentation Files**: 5
- **Dependencies**: ~70 Python packages

## 🚀 Future Roadmap

Potential improvements and extensions:

**Features:**
- [ ] Multi-language support
- [ ] Batch processing API
- [ ] Model confidence calibration
- [ ] Explainable AI (attention visualization)
- [ ] Treatment outcome tracking
- [ ] Integration with EHR systems

**Technical:**
- [ ] Model quantization for faster inference
- [ ] Distributed inference for scale
- [ ] Model monitoring and drift detection
- [ ] A/B testing framework
- [ ] GraphQL API option
- [ ] WebSocket for real-time streaming

**Deployment:**
- [ ] Kubernetes deployment manifests
- [ ] Terraform infrastructure as code
- [ ] CI/CD pipelines (GitHub Actions)
- [ ] Monitoring with Prometheus/Grafana
- [ ] Load testing and performance benchmarks

**Security:**
- [ ] OAuth2 authentication
- [ ] Rate limiting
- [ ] Input sanitization
- [ ] Audit logging
- [ ] SIEM integration

Contributions welcome for any of these!

---

## 📖 Citation

If you use this project in your research, please cite:

```bibtex
@software{clinical_mental_health_assistant,
  title={Clinical Mental Health Assistant: AI-Powered Diagnostic Support},
  author={[Your Name]},
  year={2025},
  url={https://github.com/yourusername/clinical_assistant}
}
```

---

**Built with ❤️ for advancing mental healthcare through AI**

**Questions? Issues? Feedback?** → [Open an issue](https://github.com/yourusername/clinical_assistant/issues)

---

**⚠️ Disclaimer**: This software is for research and professional clinical support purposes only. It is not approved for direct patient care without proper validation and regulatory approval.
