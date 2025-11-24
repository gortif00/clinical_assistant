# Backend - Clinical Mental Health Assistant

FastAPI-based backend service providing REST API for mental health analysis.

## 🏗️ Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── analyze.py      # Analysis endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # Configuration and constants
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── models_loader.py   # Model loading logic
│   │   └── pipeline.py        # ML pipeline functions
│   └── utils/
│       ├── __init__.py
│       └── text_cleaning.py   # Text preprocessing
├── models/                     # Model files (not in git)
│   ├── classifier/
│   ├── t5_summarizer/
│   └── llama_peft/
├── requirements.txt            # Python dependencies
└── README.md
```

## 🚀 Installation

### 1. Create Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Models

See [../MODEL_SETUP.md](../MODEL_SETUP.md) for detailed instructions on copying your trained models.

### 4. Configure Environment

```bash
# Set Hugging Face token
export HF_TOKEN="your_token_here"

# Optional: Custom model paths
export CLASSIFICATION_MODEL_PATH="/path/to/classifier"
```

## 🎮 Running the Server

### Development Mode (with auto-reload)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using the Startup Script

```bash
cd ..  # Go to project root
./start_backend.sh
```

## 📡 API Endpoints

### Health Check
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true
}
```

### Analyze Case
```http
POST /api/v1/analyze
```

**Request:**
```json
{
  "text": "Patient clinical observations...",
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
    "all_probabilities": {...}
  },
  "summary": "Clinical summary text...",
  "recommendation": "Treatment recommendation...",
  "metadata": {
    "original_text_length": 450,
    "summary_length": 180,
    "recommendation_length": 320
  }
}
```

### Interactive API Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ⚙️ Configuration

Edit `app/core/config.py` to customize:

```python
# Model paths
CLASSIFICATION_MODEL_PATH = MODELS_DIR / "classifier"
T5_SUMMARIZATION_PATH = MODELS_DIR / "t5_summarizer"
LLAMA_LORA_CHECKPOINT_PATH = MODELS_DIR / "llama_peft"

# Classification parameters
CLASSIFICATION_MAX_LENGTH = 192
CLASSIFICATION_CONFIDENCE_THRESHOLD = 0.6

# Summarization parameters
SUMMARIZATION_MIN_LENGTH = 128
SUMMARIZATION_MAX_LENGTH = 256

# Generation parameters
GENERATION_MAX_NEW_TOKENS = 512
GENERATION_TEMPERATURE = 0.7
GENERATION_TOP_P = 0.9
```

## 🧪 Testing

### Test with curl

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Patient experiencing persistent sadness...",
    "auto_classify": true
  }'
```

### Test with Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={
        "text": "Your patient case description here...",
        "auto_classify": True
    }
)

print(response.json())
```

## 📦 Dependencies

Key dependencies:
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **transformers**: Hugging Face transformers
- **torch**: PyTorch deep learning
- **peft**: Parameter-Efficient Fine-Tuning (LoRA)
- **bitsandbytes**: 4-bit quantization
- **accelerate**: Distributed training utilities

See `requirements.txt` for complete list.

## 🔧 Troubleshooting

### Models Not Loading

**Problem**: `Models not loaded correctly`

**Solution**:
1. Check model files exist: `ls -la models/*/`
2. Verify paths in `app/core/config.py`
3. Check permissions: `chmod -R 755 models/`

### CUDA Out of Memory

**Problem**: `RuntimeError: CUDA out of memory`

**Solutions**:
1. Use CPU mode: Edit `config.py` → `DEVICE = "cpu"`
2. Close other GPU applications
3. Reduce generation tokens: `GENERATION_MAX_NEW_TOKENS = 256`

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'transformers'`

**Solution**:
```bash
pip install -r requirements.txt
```

### Port Already in Use

**Problem**: `Address already in use`

**Solution**:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --port 8001
```

## 🐛 Logging

Logs are printed to stdout. To save logs:

```bash
uvicorn app.main:app --log-level info 2>&1 | tee app.log
```

Log levels: `critical`, `error`, `warning`, `info`, `debug`, `trace`

## 🚀 Performance Tips

### GPU Optimization
- Use CUDA 11.8+ for best compatibility
- Enable TF32 for faster training: `torch.backends.cuda.matmul.allow_tf32 = True`
- Use mixed precision: Already enabled via `bfloat16`

### CPU Mode
If running on CPU:
```python
# In config.py
DEVICE = "cpu"
QUANTIZATION_CONFIG["bnb_4bit_compute_dtype"] = "float32"
```

### Memory Management
```python
import torch
import gc

# Clear CUDA cache periodically
torch.cuda.empty_cache()
gc.collect()
```

## 📊 Model Information

### Classification Model
- **Type**: Fine-tuned transformer
- **Classes**: 5 (BPD, Bipolar, Depression, Anxiety, Schizophrenia)
- **Input Length**: 192 tokens

### T5 Summarizer
- **Base**: T5-base
- **Output Length**: 128-256 tokens

### Llama Generator
- **Base**: Llama-3.2-1B-Instruct
- **Quantization**: 4-bit (QLoRA)
- **Adapter**: LoRA fine-tuned
- **Output**: 512 tokens max

## 🔐 Security Notes

### For Production

1. **Disable Debug Mode**: Remove `--reload` flag
2. **CORS**: Restrict `allow_origins` in `main.py`
3. **Authentication**: Add API key or OAuth
4. **Rate Limiting**: Use middleware for rate limiting
5. **HTTPS**: Use reverse proxy (nginx) with SSL

Example nginx config:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📈 Monitoring

### Health Check Endpoint

```bash
# Simple check
curl http://localhost:8000/api/v1/health

# With timeout
curl --max-time 5 http://localhost:8000/api/v1/health
```

### Metrics (Optional)

Add Prometheus metrics:
```bash
pip install prometheus-fastapi-instrumentator
```

```python
# In main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

## 🤝 Contributing

When adding new endpoints:
1. Create route in `app/api/v1/`
2. Add business logic in `app/ml/pipeline.py`
3. Update configuration in `app/core/config.py`
4. Document in OpenAPI (automatic via FastAPI)

## 📄 License

[Your License Here]
