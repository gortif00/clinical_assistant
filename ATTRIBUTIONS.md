# 📜 Attributions & Licenses

This document provides proper attribution for all models, datasets, and resources used in the Clinical Mental Health Assistant project.

---

## 🤖 Models

### 1. MentalBERT (Classifier Base Model)

**Paper**: MentalBERT: Publicly Available Pretrained Language Models for Mental Healthcare

**Authors**: Shaoxiong Ji, Tianlin Zhang, Luna Ansari, Jie Fu, Prayag Tiwari, Erik Cambria

**Citation**:
```bibtex
@inproceedings{ji2022mentalbert,
  title     = {{MentalBERT: Publicly Available Pretrained Language Models for Mental Healthcare}},
  author    = {Shaoxiong Ji and Tianlin Zhang and Luna Ansari and Jie Fu and Prayag Tiwari and Erik Cambria},
  year      = {2022},
  booktitle = {Proceedings of the 13th Language Resources and Evaluation Conference (LREC)}
}
```

**License**: Apache 2.0  
**URL**: https://huggingface.co/mental/mental-bert-base-uncased  
**Usage**: Base model for fine-tuning the mental health condition classifier

---

### 2. T5-base (Summarization Model)

**Paper**: Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer

**Authors**: Colin Raffel, Noam Shazeer, Adam Roberts, Katherine Lee, Sharan Narang, Michael Matena, Yanqi Zhou, Wei Li, Peter J. Liu

**Citation**:
```bibtex
@article{raffel2020t5,
  author  = {Colin Raffel and Noam Shazeer and Adam Roberts and Katherine Lee and Sharan Narang and Michael Matena and Yanqi Zhou and Wei Li and Peter J. Liu},
  title   = {Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer},
  journal = {Journal of Machine Learning Research},
  year    = {2020},
  volume  = {21},
  number  = {140},
  pages   = {1-67},
  url     = {http://jmlr.org/papers/v21/20-074.html}
}
```

**License**: Apache 2.0  
**URL**: https://huggingface.co/t5-base  
**Usage**: Fine-tuned for clinical text summarization

---

### 3. Llama 3.2-1B-Instruct (Treatment Generation)

**Model**: Llama 3.2-1B-Instruct

**Provider**: Meta AI

**Citation**:
```bibtex
@misc{llama32,
  title        = {Llama 3.2: Open Foundation and Fine-Tuned Chat Models},
  author       = {{Meta AI}},
  year         = {2024},
  url          = {https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct}
}
```

**License**: Llama 3.2 Community License Agreement  
**URL**: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct  
**Usage**: Fine-tuned with LoRA/QLoRA for treatment recommendation generation

**License Terms**: 
- ✅ Commercial use allowed
- ✅ Modification and distribution allowed
- ✅ Research use encouraged
- ⚠️ Subject to Meta's Acceptable Use Policy

---

## 📊 Datasets

### 1. Mental Disorders Classification Dataset

**Dataset**: Mental Disorders Classification

**Author**: Kanakmi

**Citation**:
```bibtex
@misc{kanakmi2024mental,
  title        = {Mental Disorders Classification Dataset},
  author       = {Kanakmi},
  year         = {2024},
  publisher    = {Hugging Face},
  url          = {https://huggingface.co/datasets/Kanakmi/mental-disorders}
}
```

**License**: Apache 2.0  
**URL**: https://huggingface.co/datasets/Kanakmi/mental-disorders  
**Usage**: Training data for the BERT-based mental health classifier (5 conditions)  
**Size**: ~204K training samples  
**Classes**: BPD, Bipolar Disorder, Depression, Anxiety, Schizophrenia

---

### 2. PubMed Article Summarization Dataset

**Dataset**: PubMed Article Summarization

**Provider**: The Devastator (Kaggle)

**Citation**:
```bibtex
@misc{pubmed2023summarization,
  title        = {PubMed Article Summarization Dataset},
  author       = {{The Devastator}},
  year         = {2023},
  publisher    = {Kaggle},
  url          = {https://www.kaggle.com/datasets/thedevastator/pubmed-article-summarization-dataset}
}
```

**License**: CC0: Public Domain  
**URL**: https://www.kaggle.com/datasets/thedevastator/pubmed-article-summarization-dataset  
**Usage**: Training data for T5 summarization model  
**Content**: Medical article abstracts and summaries from PubMed

---

## 🛠️ Frameworks & Libraries

### FastAPI
- **License**: MIT
- **URL**: https://fastapi.tiangolo.com/

### PyTorch
- **License**: BSD-3-Clause
- **URL**: https://pytorch.org/

### Transformers (HuggingFace)
- **License**: Apache 2.0
- **URL**: https://huggingface.co/docs/transformers/

### PEFT (Parameter-Efficient Fine-Tuning)
- **License**: Apache 2.0
- **URL**: https://github.com/huggingface/peft

### BitsAndBytes (Quantization)
- **License**: MIT
- **URL**: https://github.com/TimDettmers/bitsandbytes

---

## 📋 License Summary

| Resource | License | Commercial Use | Attribution Required |
|----------|---------|----------------|---------------------|
| MentalBERT | Apache 2.0 | ✅ Yes | ✅ Yes |
| T5-base | Apache 2.0 | ✅ Yes | ✅ Yes |
| Llama 3.2 | Llama 3.2 License | ✅ Yes | ✅ Yes |
| Mental Disorders Dataset | Apache 2.0 | ✅ Yes | ✅ Yes |
| PubMed Dataset | CC0 Public Domain | ✅ Yes | ❌ No |
| This Project | MIT | ✅ Yes | ✅ Yes |

---

## ⚖️ Compliance Notes

### For Academic Use
If you use this project or its components in academic research, please cite:
1. This repository
2. The relevant model papers (MentalBERT, T5, Llama 3.2)
3. The dataset sources

### For Commercial Use
All components are commercially usable, but ensure:
- ✅ Compliance with Llama 3.2 Acceptable Use Policy
- ✅ Proper attribution is maintained
- ✅ Medical disclaimers are provided (this is a diagnostic support tool, not a replacement for professional judgment)

### Data Privacy
- ✅ All processing occurs locally (no external API calls)
- ✅ No patient data is transmitted or stored
- ✅ HIPAA/GDPR considerations are the deployer's responsibility

---

## 🙏 Acknowledgments

We gratefully acknowledge:
- **Meta AI** for Llama 3.2 models
- **Google Research** for T5 architecture
- **The MentalBERT Team** for domain-specific pretraining
- **HuggingFace** for model hosting and transformers library
- **Dataset Contributors** for making mental health data available for research

---

## 📧 Questions?

For licensing questions or attribution issues:
- Open an issue on GitHub
- Review individual model/dataset licenses at their source URLs
- Consult your legal team for commercial deployment

---

**Last Updated**: December 2025
