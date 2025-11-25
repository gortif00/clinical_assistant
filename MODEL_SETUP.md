# Model Setup Guide

<!--
================================================================================
MODEL SETUP OVERVIEW
================================================================================
This guide explains how to copy your trained models from Google Drive/Colab
to your local project directory.

Why models are separate:
- Models are large files (~3GB total)
- Trained separately in notebooks
- Stored in Google Drive for persistence
- Not suitable for git repositories
- Need to be copied once for local development

Three models required:
1. CLASSIFIER (~500MB): Fine-tuned BERT for mental health diagnosis
2. T5 SUMMARIZER (~900MB): Fine-tuned T5 for clinical summarization  
3. LLAMA LORA (~50MB): LoRA adapter for treatment generation

Important: Missing ANY required file will cause loading errors!

Setup methods (choose one):
- Method 1: Direct Colab download (works anywhere)
- Method 2: Google Drive Desktop sync (easiest if installed)
- Method 3: rclone (for automated/scripted setup)

One-time process: Takes 10-20 minutes depending on internet speed
================================================================================
-->

## 📦 Copying Your Models from Google Drive/Colab

Your Jupyter notebook trains models that are stored in Google Drive.  
This guide shows you how to **copy those trained models** to your local machine.

## Required Models

### 1. Classification Model (~500MB)

<!--
CLASSIFICATION MODEL DETAILS:

Purpose: Detects which mental health condition from clinical text
Architecture: Fine-tuned BERT-based transformer
Classes: 5 (Bipolar, Depression, Anxiety, BPD, Schizophrenia)
Input: Clinical text (50+ characters)
Output: Pathology label + confidence scores

Required files explained:
- config.json: Model architecture (layers, attention heads, etc.)
- model.safetensors: Trained weights (~500MB, safer format)
- pytorch_model.bin: Alternative weight format (older)
- tokenizer.json: Vocabulary and tokenization rules
- vocab.txt: WordPiece vocabulary
- special_tokens_map.json: Special tokens ([CLS], [SEP], etc.)
- label_map.json: Maps class indices to pathology names
- training_metadata.json: Training history and metrics

Missing any file = loading error!
-->

- **Source**: `/content/drive/Shareddrives/NLP_PSYCOLOGY/CLASSIFICATION/final_model`
- **Destination**: `backend/models/classifier/`
- **Size**: ~500MB
- **Files needed**:
  - `config.json` (model architecture)
  - `model.safetensors` or `pytorch_model.bin` (trained weights)
  - `tokenizer_config.json` (tokenizer settings)
  - `tokenizer.json` (vocabulary and rules)
  - `vocab.txt` (WordPiece vocabulary)
  - `special_tokens_map.json` (special tokens)
  - `label_map.json` (class name mapping)
  - `training_metadata.json` (optional, training info)

### 2. T5 Summarization Model (~900MB)

<!--
T5 SUMMARIZATION MODEL DETAILS:

Purpose: Extracts key clinical information from verbose notes
Architecture: Fine-tuned T5-base (Text-to-Text Transfer Transformer)
Checkpoint: 799 (best validation performance)
Input: Clinical text + classification result
Output: Concise summary (~60% of original length)

Required files explained:
- config.json: T5 architecture configuration
- model.safetensors: Trained weights (~900MB)
- pytorch_model.bin: Alternative weight format
- spiece.model: SentencePiece tokenizer model
- tokenizer_config.json: Tokenizer configuration
- special_tokens_map.json: T5 special tokens
- trainer_state.json: Training checkpoint information

Note: T5 uses SentencePiece instead of WordPiece
-->

- **Source**: `/content/drive/Shareddrives/NLP_PSYCOLOGY/CHECKPOINTS/Summarization/version_2/checkpoint-799`
- **Destination**: `backend/models/t5_summarizer/`
- **Size**: ~900MB
- **Checkpoint**: 799 (best performing checkpoint)
- **Files needed**:
  - `config.json` (T5 architecture)
  - `model.safetensors` or `pytorch_model.bin` (trained weights)
  - `tokenizer_config.json` (tokenizer settings)
  - `spiece.model` (SentencePiece tokenizer)
  - `tokenizer.json` (vocabulary)
  - `special_tokens_map.json` (T5 special tokens)
  - `trainer_state.json` (optional, checkpoint info)

### 3. Llama LoRA Adapter (~50MB)

<!--
LLAMA LORA ADAPTER DETAILS:

Purpose: Generates evidence-based treatment recommendations
Architecture: LoRA adapter for Llama 3.2-1B-Instruct
Base model: Downloaded from HuggingFace (gated, requires token)
Adapter: Fine-tuned for clinical recommendations
Checkpoint: 51 (best performing)

LoRA explained:
- Parameter-Efficient Fine-Tuning technique
- Only stores small adapter weights (~50MB)
- Applied on top of base Llama model (2.5GB)
- Much smaller than full model fine-tuning

Required files explained:
- adapter_config.json: LoRA configuration (rank, alpha, target modules)
- adapter_model.safetensors: Adapter weights (~50MB)
- chat_template.jinja: Llama chat formatting template
- trainer_state.json: Training checkpoint info

Note: Base Llama model auto-downloaded from HuggingFace (needs HF_TOKEN)
-->

- **Source**: `/content/drive/Shareddrives/NLP_PSYCOLOGY/CHECKPOINTS/Generation/version_3/checkpoint-51`
- **Destination**: `backend/models/llama_peft/`
- **Size**: ~50MB (adapter only, base model auto-downloaded)
- **Checkpoint**: 51 (best performing)
- **Files needed**:
  - `adapter_config.json` (LoRA configuration)
  - `adapter_model.safetensors` or `adapter_model.bin` (adapter weights)
  - `chat_template.jinja` (optional, Llama formatting)
  - `trainer_state.json` (optional, checkpoint info)
  
**Note**: The base Llama 3.2-1B-Instruct model (~2.5GB) will be **automatically downloaded** from HuggingFace when you first run the backend (requires HF_TOKEN).

## Setup Methods

<!--
CHOOSE YOUR SETUP METHOD:

Method 1: Direct Download from Colab
- Best if: You have models in Colab, any OS
- Process: Zip in Colab → Download → Extract locally
- Time: 10-15 minutes (depends on connection)
- Pros: Works anywhere, no special software
- Cons: Manual download, multiple steps

Method 2: Google Drive Desktop Sync
- Best if: You have Google Drive Desktop installed
- Process: Sync shared drive → Copy files
- Time: 5-10 minutes (after initial sync)
- Pros: Fastest, automatic sync, easy
- Cons: Requires Google Drive Desktop

Method 3: rclone
- Best if: You want automated/scripted setup
- Process: Configure rclone → Copy with command
- Time: 5-10 minutes
- Pros: Scriptable, resumable, no browser
- Cons: Requires rclone installation and config

Recommendation:
- First time: Method 1 (works everywhere)
- Repeat setup: Method 2 or 3 (faster)
-->

### Method 1: Direct Download from Colab (Universal)

<!--
COLAB DOWNLOAD PROCESS:

1. Create zip files in Colab (compresses for faster download)
2. Download zips using Colab's file browser
3. Extract locally to correct directories
4. Verify all files present

Why zip:
- Faster download (single file vs hundreds)
- Preserves directory structure
- Less likely to fail mid-download

Expected download sizes:
- classifier.zip: ~500MB
- t5_summarizer.zip: ~900MB  
- llama_peft.zip: ~50MB
- Total: ~1.5GB (compressed)
-->

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
