# Quick Start Guide

<!--
================================================================================
QUICK START OVERVIEW
================================================================================
This guide gets you from zero to running application in 5 minutes (after models
are copied). It's designed for users who want to test the system quickly without
reading detailed documentation.

What this guide covers:
- Model setup (one-time, 5-10 minutes)
- Backend startup (2-5 minutes first time, <1 minute after)
- Frontend startup (instant)
- Testing with example cases
- API testing with curl/Python

What this guide skips:
- Detailed architecture explanations (see README.md)
- Docker deployment (see DOCKER_GUIDE.md)
- Model training (see notebooks)
- Production deployment considerations

Expected total time:
- First run: ~15 minutes (model setup + installation)
- Subsequent runs: ~2 minutes (just startup)
- Per analysis: ~50-60 seconds

Prerequisites explained:
- Python 3.8+: Required for modern transformers library features
- Models: Must be trained and copied (see MODEL_SETUP.md)
- 16GB RAM: Minimum for loading all 3 models (~4-6GB total)
- GPU: Optional but gives 4-5x speedup (MPS on Mac, CUDA on NVIDIA)
================================================================================
-->

## 🚀 Get Started in 5 Minutes

### Prerequisites
- **Python 3.8+** (tested with 3.11)
- **Your trained models** from Google Drive/Colab (see [MODEL_SETUP.md](MODEL_SETUP.md))
- **16GB+ RAM** (32GB recommended for comfortable performance)
- **GPU** (optional): Apple Silicon MPS or NVIDIA CUDA for 4-5x speedup

### Step 1: Set Up Models (First Time Only)

<!--
MODEL SETUP PROCESS:

This step copies your trained models from Google Drive to the local project.
You only need to do this once (or when models are updated).

Why separate models from code:
- Models are large (~3GB total)
- Models change less frequently than code
- Keeps git repository lightweight
- Allows model versioning separately

Three models required:
1. Classifier (~500MB): Detects which condition from clinical text
2. T5 Summarizer (~900MB): Extracts key information
3. Llama LoRA (~50MB): Generates treatment recommendations

Missing even one file will cause errors during startup.
-->

**Copy your trained models** from Google Drive to the project:

```bash
# Create model directories (one-time setup)
mkdir -p backend/models/classifier
mkdir -p backend/models/t5_summarizer
mkdir -p backend/models/llama_peft
```

**Option A**: Download from Colab  
See [MODEL_SETUP.md](MODEL_SETUP.md) for zip download and extraction instructions.

**Option B**: Copy from Google Drive Desktop  
If you have Google Drive Desktop installed:
```bash
# Adjust paths based on your Google Drive location
cp -r "path/to/NLP_PSYCOLOGY/CLASSIFICATION/final_model/"* backend/models/classifier/
cp -r "path/to/NLP_PSYCOLOGY/CHECKPOINTS/Summarization/version_2/checkpoint-799/"* backend/models/t5_summarizer/
cp -r "path/to/NLP_PSYCOLOGY/CHECKPOINTS/Generation/version_3/checkpoint-51/"* backend/models/llama_peft/
```

### Step 2: Set Up Hugging Face Token

<!--
HUGGINGFACE AUTHENTICATION:

Why needed:
- Llama 3.2 is a "gated" model by Meta
- Requires accepting license agreement
- Token proves you've accepted terms

What happens without token:
- Backend will fail to load Llama model
- You'll see "401 Unauthorized" errors
- Classification and summarization will still work (local models)

One-time setup:
1. Create HF account (free)
2. Accept Llama 3.2 license on HF website
3. Generate token with "Read" permissions
4. Set token via CLI or environment variable
-->

```bash
# Get your token from https://huggingface.co/settings/tokens
# Must first accept Llama 3.2 license at:
# https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct

# Method 1: Environment variable (current session only)
export HF_TOKEN="hf_your_token_here"

# Method 2: HF CLI (saves permanently)
pip install huggingface_hub
huggingface-cli login  # Paste token when prompted

# Verify authentication
huggingface-cli whoami
```

### Step 3: Start Backend

<!--
BACKEND STARTUP PROCESS:

What happens during startup:
1. Creates/activates Python virtual environment (5 seconds)
2. Installs dependencies if needed (5-10 minutes first time, skipped after)
3. Validates model files exist (2 seconds)
4. Checks HuggingFace authentication (1 second)
5. Loads classification model to GPU (30 seconds)
6. Loads T5 summarizer to GPU (1 minute)
7. Loads Llama base model to CPU (2 minutes)
8. Optionally loads LoRA adapter (30 seconds)
9. Starts FastAPI server on port 8000

Total time:
- First run: 15-20 minutes (with dependency installation)
- Subsequent runs: 2-5 minutes (just model loading)
- With Docker: 5-10 minutes (CPU-based, no MPS acceleration)

Progress indicators:
- You'll see "Loading classification model..." etc.
- Watch for "Application startup complete" message
- Backend ready when you see "Uvicorn running on http://0.0.0.0:8000"
-->

```bash
# Using the startup script (RECOMMENDED - handles everything)
./start_backend.sh

# Or manually (if you want more control)
cd backend
python3 -m venv venv                    # Create virtual environment
source venv/bin/activate                 # Activate it
pip install -r requirements.txt          # Install dependencies (first time only)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Wait for models to load** (2-5 minutes on first run):  
You'll see progress messages for each model loading. Don't interrupt!

### Step 4: Start Frontend

<!--
FRONTEND STARTUP:

The frontend is a static web application (HTML/CSS/JavaScript) that requires
a simple HTTP server to serve files.

What it does:
- Serves index.html and static assets
- Runs entirely in browser (no server-side processing)
- Communicates with backend API on port 8000

Startup time: Instant (just file serving)
No dependencies: Pure vanilla JavaScript, no npm/webpack/build step
-->

**In a new terminal** (keep backend running):

```bash
# Using the startup script (RECOMMENDED)
./start_frontend.sh

# Or manually with Python's built-in HTTP server
cd frontend
python3 -m http.server 3000
# If python3 not found, try: python -m http.server 3000
```

### Step 5: Open the Application

<!--
ACCESS POINTS:

1. Frontend UI (http://localhost:3000):
   - Main chat interface for end users
   - Interactive analysis with examples
   - Real-time progress indicators

2. API Docs (http://localhost:8000/docs):
   - Swagger UI for testing API directly
   - See all endpoints and schemas
   - Try requests without frontend

3. Health Check (http://localhost:8000/api/v1/health):
   - Quick test that backend is running
   - Shows loaded models and device info
   - Useful for monitoring/debugging
-->

**Open your browser** and navigate to:
- **Frontend UI**: http://localhost:3000 (main application)
- **API Docs**: http://localhost:8000/docs (interactive API documentation)
- **Health Check**: http://localhost:8000/api/v1/health (verify backend is ready)

### Step 6: Try an Example

<!--
TESTING WITH EXAMPLES:

The frontend includes 3 pre-loaded clinical cases:
1. Depression: Low mood, anhedonia, sleep disturbances
2. Anxiety: Panic attacks, excessive worry, physical symptoms
3. Bipolar: Mood swings, manic episodes, depressive episodes

What to expect:
1. Click example button (text appears in input)
2. Click "Analyze Case" (processing starts)
3. See progress: "Analyzing..." with spinner
4. Results appear in 50-60 seconds:
   - Classification: Pathology + confidence score
   - Probability bars: All 5 conditions with percentages
   - Summary: Key clinical information extracted
   - Recommendation: Evidence-based treatment plan
   - Disclaimer: Reminds this is AI-generated

Timing breakdown:
- Classification: ~5 seconds
- Summarization: ~10 seconds  
- Generation: ~35-45 seconds
- Total: ~50-60 seconds per analysis
-->

1. **Click** one of the example case buttons (Depression, Anxiety, or Bipolar)
2. **Click** "Analyze Case 🔬" button
3. **Wait** for the analysis (typically 50-60 seconds)
   - You'll see a spinner and "Analyzing..." message
   - Progress updates show which stage is running
4. **Review** the complete results:
   - 🎯 **Classification**: Which condition was detected + confidence
   - 📊 **Probabilities**: All 5 conditions with percentage bars
   - 📝 **Summary**: Concise clinical information
   - 💊 **Recommendation**: Personalized treatment plan

## 🎯 Testing the API Directly

<!--
DIRECT API TESTING:

You can bypass the frontend and test the backend API directly using:
- curl (command line)
- Python requests library
- Swagger UI at http://localhost:8000/docs
- Postman or similar tools

Useful for:
- Integration testing
- Automated testing
- Debugging backend issues
- Building custom clients
-->

### Using curl:

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I have been feeling extremely sad and hopeless for the past 3 months. I have lost interest in all my hobbies and can barely get out of bed. I am sleeping 12+ hours a day but still feel exhausted.",
    "auto_classify": true
  }'
```

### Using Python:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={
        "text": "Patient reports experiencing intense episodes of fear...",
        "auto_classify": True
    }
)

result = response.json()
print(f"Diagnosis: {result['classification']['pathology']}")
print(f"Confidence: {result['classification']['confidence']:.2%}")
```

## 📋 What to Expect

### First Run (5-10 minutes)
- Virtual environment creation
- Dependency installation
- Model loading into memory
- Hugging Face model downloads

### Subsequent Runs (1-2 minutes)
- Models already cached
- Faster startup

### Analysis Time
- Classification: ~5 seconds
- Summarization: ~10 seconds
- Generation: ~30-45 seconds
- **Total**: ~50-60 seconds per case

## ⚠️ Common Issues

<!--
TROUBLESHOOTING GUIDE:

These are the most common startup issues users encounter.
For each issue, we explain:
- What the error means
- Why it happens
- How to fix it
- How to prevent it

General debugging approach:
1. Check terminal output for specific error messages
2. Verify prerequisites (Python version, models, token)
3. Check file permissions
4. Test components individually (API health check)
5. Review logs for detailed error information
-->

### "Models not found" or "FileNotFoundError"
```
What it means: Backend can't find model files in expected directories

Why it happens:
- Models not copied from Google Drive
- Wrong directory structure
- Typo in config.py paths

Solution:
1. Verify models exist: ls -la backend/models/*/
2. Check each model has required files (config.json, model weights, etc.)
3. See MODEL_SETUP.md for detailed copying instructions
4. Ensure paths in config.py match your structure
```

### "CUDA out of memory" or "MPS allocation failed"
```
What it means: GPU doesn't have enough memory for models

Why it happens:
- GPU has <8GB VRAM
- Other programs using GPU
- All 3 models loaded simultaneously

Solution:
1. Close other GPU-using applications
2. Use CPU mode: Edit backend/app/core/config.py, set DEVICE = "cpu"
3. Or use Docker (automatically uses CPU)
4. Restart computer to clear GPU memory
```

### "Port already in use" or "Address already in use"
```
What it means: Another process is using port 8000 or 3000

Why it happens:
- Previous server didn't shut down cleanly
- Another application using same port
- Multiple instances running

Solution (macOS/Linux):
  lsof -ti:8000 | xargs kill -9  # Kill backend on port 8000
  lsof -ti:3000 | xargs kill -9  # Kill frontend on port 3000

Solution (Windows):
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F

Prevention:
- Always use Ctrl+C to stop servers gracefully
- Check no servers running before starting: lsof -ti:8000
```

### "HuggingFace token error" or "401 Unauthorized"
```
What it means: Can't authenticate with HuggingFace to download Llama

Why it happens:
- No HF_TOKEN set
- Token expired or invalid
- Haven't accepted Llama 3.2 license

Solution:
1. Accept license: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
2. Get token: https://huggingface.co/settings/tokens
3. Set token: export HF_TOKEN="hf_your_token_here"
4. Or use CLI: huggingface-cli login
5. Verify: huggingface-cli whoami
```

## 🎨 Frontend Features

- **Chat Interface**: Professional Gradio-inspired design
- **Auto Mode**: AI automatically detects mental health condition
- **Manual Mode**: Select diagnosis manually
- **Examples**: Pre-loaded clinical cases
- **Real-time**: Progress indicators during analysis
- **Responsive**: Works on desktop and tablet

## 📚 Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [MODEL_SETUP.md](MODEL_SETUP.md) for model configuration
- Explore the API docs at http://localhost:8000/docs
- Customize settings in `backend/app/core/config.py`

## 🆘 Need Help?

1. Check the [README.md](README.md) troubleshooting section
2. Review logs in the terminal
3. Test API health endpoint: http://localhost:8000/api/v1/health
4. Verify model files exist: `ls -la backend/models/*/`

## 📞 Support

For issues, please check:
- Terminal output for error messages
- Browser console (F12) for frontend errors
- API logs for backend issues

---

**Happy analyzing! 🧠✨**
