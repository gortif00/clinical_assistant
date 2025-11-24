# Model Setup Guide

## 📦 Copying Your Models from Google Drive/Colab

Your Jupyter notebook references models stored in Google Drive. Here's how to set them up locally:

## Required Models

### 1. Classification Model
- **Source**: `/content/drive/Shareddrives/NLP_PSYCOLOGY/CLASSIFICATION/final_model`
- **Destination**: `backend/models/classifier/`
- **Files needed**:
  - `config.json`
  - `pytorch_model.bin` (or `model.safetensors`)
  - `tokenizer_config.json`
  - `vocab.txt` (or tokenizer files)
  - `special_tokens_map.json`

### 2. T5 Summarization Model
- **Source**: `/content/drive/Shareddrives/NLP_PSYCOLOGY/CHECKPOINTS/Summarization/version_2/checkpoint-799`
- **Destination**: `backend/models/t5_summarizer/`
- **Files needed**:
  - `config.json`
  - `pytorch_model.bin`
  - `tokenizer_config.json`
  - `spiece.model` (SentencePiece tokenizer)
  - `special_tokens_map.json`

### 3. Llama LoRA Adapter
- **Source**: `/content/drive/Shareddrives/NLP_PSYCOLOGY/CHECKPOINTS/Generation/version_3/checkpoint-51`
- **Destination**: `backend/models/llama_peft/`
- **Files needed**:
  - `adapter_config.json`
  - `adapter_model.bin` (or `adapter_model.safetensors`)

## Setup Methods

### Method 1: Direct Download from Colab

In a Colab notebook, run:

```python
from google.colab import drive
import shutil
import os

# Mount drive
drive.mount('/content/drive')

# Create zip files
!cd /content/drive/Shareddrives/NLP_PSYCOLOGY/CLASSIFICATION && \
  zip -r /content/classifier.zip final_model/

!cd /content/drive/Shareddrives/NLP_PSYCOLOGY/CHECKPOINTS/Summarization/version_2 && \
  zip -r /content/t5_summarizer.zip checkpoint-799/

!cd /content/drive/Shareddrives/NLP_PSYCOLOGY/CHECKPOINTS/Generation/version_3 && \
  zip -r /content/llama_peft.zip checkpoint-51/

# Download the zip files from Colab's file browser
from google.colab import files
files.download('/content/classifier.zip')
files.download('/content/t5_summarizer.zip')
files.download('/content/llama_peft.zip')
```

Then extract to the appropriate directories:
```bash
cd backend/models
unzip ~/Downloads/classifier.zip -d classifier/
unzip ~/Downloads/t5_summarizer.zip -d t5_summarizer/
unzip ~/Downloads/llama_peft.zip -d llama_peft/
```

### Method 2: Google Drive Desktop Sync

1. Install Google Drive for Desktop
2. Sync the shared drive folder
3. Copy the model directories:

```bash
# macOS/Linux
cp -r "/Volumes/GoogleDrive/Shared drives/NLP_PSYCOLOGY/CLASSIFICATION/final_model" \
  backend/models/classifier/

cp -r "/Volumes/GoogleDrive/Shared drives/NLP_PSYCOLOGY/CHECKPOINTS/Summarization/version_2/checkpoint-799" \
  backend/models/t5_summarizer/

cp -r "/Volumes/GoogleDrive/Shared drives/NLP_PSYCOLOGY/CHECKPOINTS/Generation/version_3/checkpoint-51" \
  backend/models/llama_peft/
```

### Method 3: Using rclone

1. Install rclone: `brew install rclone` (macOS) or `sudo apt install rclone` (Linux)
2. Configure Google Drive: `rclone config`
3. Copy models:

```bash
rclone copy "gdrive:NLP_PSYCOLOGY/CLASSIFICATION/final_model" \
  backend/models/classifier/ -P

rclone copy "gdrive:NLP_PSYCOLOGY/CHECKPOINTS/Summarization/version_2/checkpoint-799" \
  backend/models/t5_summarizer/ -P

rclone copy "gdrive:NLP_PSYCOLOGY/CHECKPOINTS/Generation/version_3/checkpoint-51" \
  backend/models/llama_peft/ -P
```

## Verify Model Structure

After copying, your directory structure should look like:

```
backend/models/
├── classifier/
│   ├── config.json
│   ├── pytorch_model.bin
│   ├── tokenizer_config.json
│   ├── vocab.txt
│   └── special_tokens_map.json
├── t5_summarizer/
│   ├── config.json
│   ├── pytorch_model.bin
│   ├── tokenizer_config.json
│   ├── spiece.model
│   └── special_tokens_map.json
└── llama_peft/
    ├── adapter_config.json
    └── adapter_model.bin
```

## Verify Setup

Run this Python script to verify models:

```python
cd backend
python3 << EOF
from pathlib import Path

models_dir = Path("models")
required = {
    "classifier": ["config.json", "pytorch_model.bin"],
    "t5_summarizer": ["config.json", "pytorch_model.bin"],
    "llama_peft": ["adapter_config.json", "adapter_model.bin"]
}

all_good = True
for model, files in required.items():
    model_path = models_dir / model
    print(f"\n{model}:")
    for file in files:
        file_path = model_path / file
        exists = file_path.exists()
        symbol = "✅" if exists else "❌"
        print(f"  {symbol} {file}")
        if not exists:
            all_good = False

if all_good:
    print("\n✅ All models ready!")
else:
    print("\n⚠️  Some models are missing")
EOF
```

## Hugging Face Authentication

The Llama base model will be downloaded from Hugging Face. You need to:

1. Create a Hugging Face account: https://huggingface.co/join
2. Accept the Llama 3.2 license: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
3. Get your access token: https://huggingface.co/settings/tokens
4. Set the token:

```bash
export HF_TOKEN="hf_your_token_here"
```

Or use the Hugging Face CLI:
```bash
pip install huggingface_hub
huggingface-cli login
```

## Troubleshooting

### "Model files not found"
- Check the paths in `backend/app/core/config.py`
- Verify files exist with `ls -la backend/models/*/`

### "Permission denied"
- Ensure read permissions: `chmod -R 755 backend/models/`

### "Out of memory"
- Models require ~8GB RAM minimum
- Use CPU mode if GPU memory is insufficient
- Consider using smaller batch sizes

## Alternative: Host Models on Hugging Face

If models are too large for local storage, upload to Hugging Face:

```python
from huggingface_hub import HfApi

api = HfApi()
api.create_repo("your-username/clinical-classifier", private=True)
api.upload_folder(
    folder_path="backend/models/classifier",
    repo_id="your-username/clinical-classifier"
)
```

Then update `config.py`:
```python
CLASSIFICATION_MODEL_PATH = "your-username/clinical-classifier"
```
