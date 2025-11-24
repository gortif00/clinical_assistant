# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.8+
- Your trained models from Google Drive/Colab
- 16GB+ RAM (32GB recommended)
- CUDA-compatible GPU (optional but recommended)

### Step 1: Set Up Models (First Time Only)

Copy your trained models from Google Drive to the project:

```bash
# Create model directories
mkdir -p backend/models/classifier
mkdir -p backend/models/t5_summarizer
mkdir -p backend/models/llama_peft
```

**Option A**: Download from Colab (see [MODEL_SETUP.md](MODEL_SETUP.md) for details)

**Option B**: Copy from Google Drive Desktop:
```bash
# Adjust paths based on your Google Drive location
cp -r "path/to/NLP_PSYCOLOGY/CLASSIFICATION/final_model/"* backend/models/classifier/
cp -r "path/to/NLP_PSYCOLOGY/CHECKPOINTS/Summarization/version_2/checkpoint-799/"* backend/models/t5_summarizer/
cp -r "path/to/NLP_PSYCOLOGY/CHECKPOINTS/Generation/version_3/checkpoint-51/"* backend/models/llama_peft/
```

### Step 2: Set Up Hugging Face Token

```bash
# Get your token from https://huggingface.co/settings/tokens
export HF_TOKEN="hf_your_token_here"

# Or use HF CLI
pip install huggingface_hub
huggingface-cli login
```

### Step 3: Start Backend

```bash
# Using the startup script (recommended)
./start_backend.sh

# Or manually
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Wait for models to load (this may take 2-5 minutes on first run).

### Step 4: Start Frontend

In a new terminal:

```bash
./start_frontend.sh

# Or manually
cd frontend
python3 -m http.server 3000
```

### Step 5: Open the Application

Open your browser and go to:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/api/v1/health

### Step 6: Try an Example

1. Click one of the example case buttons (Depression, Anxiety, or Bipolar)
2. Click "Analyze Case 🔬"
3. Wait for the analysis (30-60 seconds)
4. Review the classification, summary, and treatment recommendation

## 🎯 Testing the API Directly

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

### "Models not found"
```
Solution: Check MODEL_SETUP.md and verify models are in backend/models/
```

### "CUDA out of memory"
```
Solution: Edit backend/app/core/config.py and set DEVICE = "cpu"
```

### "Port already in use"
```
Solution: Kill the process:
  lsof -ti:8000 | xargs kill -9  # Backend
  lsof -ti:3000 | xargs kill -9  # Frontend
```

### "HuggingFace token error"
```
Solution: Set HF_TOKEN environment variable or run 'huggingface-cli login'
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
