# Clinical Mental Health Assistant

AI-Powered Diagnostic Support Tool for Healthcare Professionals

## 🎯 Overview

This application provides an end-to-end clinical mental health analysis pipeline that combines:
- **Classification**: Identifies mental health conditions (Depression, Anxiety, Bipolar Disorder, BPD, Schizophrenia)
- **Summarization**: Generates concise clinical summaries using T5
- **Generation**: Creates evidence-based treatment recommendations using Llama 3

## 🏗️ Architecture

### Backend (FastAPI)
- **Classification Model**: Fine-tuned transformer for mental health diagnosis
- **T5 Summarizer**: Extracts clinical summaries from patient observations
- **Llama 3 + QLoRA**: Generates personalized treatment recommendations

### Frontend
- Modern chat-based interface inspired by Gradio
- Real-time analysis with progress indicators
- Example clinical cases for quick testing
- Manual and automatic classification modes

## 📋 Requirements

### System Requirements
- Python 3.8+
- CUDA-compatible GPU (recommended for optimal performance)
- 16GB+ RAM (32GB recommended)
- 10GB+ disk space for models

### Python Dependencies
See `backend/requirements.txt` for complete list:
- transformers
- torch
- peft (for LoRA adapters)
- accelerate
- bitsandbytes (for 4-bit quantization)
- fastapi
- uvicorn

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd clinical_assistant
```

### 2. Set Up Python Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Model Paths

You need to place your trained models in the `backend/models/` directory:

```
backend/models/
├── classifier/              # Your fine-tuned classification model
│   ├── config.json
│   ├── pytorch_model.bin
│   └── tokenizer files...
├── t5_summarizer/          # Your fine-tuned T5 checkpoint
│   ├── config.json
│   ├── pytorch_model.bin
│   └── tokenizer files...
└── llama_peft/             # Your Llama LoRA adapter
    ├── adapter_config.json
    └── adapter_model.bin
```

**Note**: You need to download/copy your trained models from Google Drive or Colab to these directories.

Update paths in `backend/app/core/config.py` if using different locations:
```python
CLASSIFICATION_MODEL_PATH = MODELS_DIR / "classifier"
T5_SUMMARIZATION_PATH = MODELS_DIR / "t5_summarizer"
LLAMA_LORA_CHECKPOINT_PATH = MODELS_DIR / "llama_peft"
```

### 4. Hugging Face Authentication (for Llama)

If using Llama models from Hugging Face, authenticate:
```bash
huggingface-cli login
```

Or set your token:
```bash
export HF_TOKEN="your_huggingface_token"
```

## 🎮 Usage

### Start the Backend API

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

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

### Model Parameters

Edit `backend/app/core/config.py` to adjust:

```python
# Classification
CLASSIFICATION_MAX_LENGTH = 192
CLASSIFICATION_CONFIDENCE_THRESHOLD = 0.6

# Summarization
SUMMARIZATION_MIN_LENGTH = 128
SUMMARIZATION_MAX_LENGTH = 256

# Generation
GENERATION_MAX_NEW_TOKENS = 512
GENERATION_TEMPERATURE = 0.7
GENERATION_TOP_P = 0.9
```

### Frontend API URL

Edit `frontend/js/app.js`:
```javascript
const API_URL = "http://localhost:8000/api/v1/analyze";
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

### Models Not Loading
```
Error: Models not loaded correctly
```
**Solution**: Verify model files exist in `backend/models/` directories and paths in `config.py` are correct.

### CUDA Out of Memory
```
RuntimeError: CUDA out of memory
```
**Solution**: 
- Reduce batch size
- Use CPU mode (slower): Set `DEVICE = "cpu"` in config.py
- Close other GPU applications

### Port Already in Use
```
Error: Address already in use
```
**Solution**: Change port or kill existing process:
```bash
lsof -ti:8000 | xargs kill -9
```

## 🔒 Important Notes

### Professional Use Only
This tool is designed for mental health professionals as a clinical decision support system. It should not replace professional judgment, comprehensive assessment, or established diagnostic protocols.

### Data Privacy
- Do not use real patient data without proper consent and compliance
- Ensure HIPAA/GDPR compliance in production environments
- Consider implementing authentication and encryption

### Model Limitations
- Models trained on specific datasets may have biases
- Performance varies based on text quality and length
- Always verify recommendations with clinical expertise

## 📄 License

[Your License Here]

## 👥 Contributors

[Your Name/Team]

## 📞 Support

For issues or questions:
- GitHub Issues: [your-repo/issues]
- Email: [your-email]

## 🙏 Acknowledgments

- Hugging Face Transformers
- Meta AI (Llama models)
- FastAPI framework
- Clinical datasets used for training

---

**⚠️ Disclaimer**: This software is for research and professional clinical support purposes only. It is not approved for direct patient care without proper validation and regulatory approval.
