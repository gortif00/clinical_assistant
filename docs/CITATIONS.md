# 📚 Citations & References

## How to Cite This Project

If you use the Clinical Mental Health Assistant in your research or application, please cite:

```bibtex
@software{ortiz2025clinical,
  title        = {Clinical Mental Health Assistant: AI-Powered Diagnostic Support Tool},
  author       = {Gonzalo Ortiz},
  year         = {2025},
  url          = {https://github.com/gortif00/clinical_assistant},
  note         = {Production-ready NLP system for mental health condition classification and treatment recommendation}
}
```

---

## Required Citations for Components

### Models Used

#### 1. MentalBERT (Classification)

```bibtex
@inproceedings{ji2022mentalbert,
  title     = {{MentalBERT: Publicly Available Pretrained Language Models for Mental Healthcare}},
  author    = {Shaoxiong Ji and Tianlin Zhang and Luna Ansari and Jie Fu and Prayag Tiwari and Erik Cambria},
  year      = {2022},
  booktitle = {Proceedings of the 13th Language Resources and Evaluation Conference (LREC)},
  url       = {https://aclanthology.org/2022.lrec-1.26/}
}
```

**Paper URL**: https://aclanthology.org/2022.lrec-1.26/  
**Model URL**: https://huggingface.co/mental/mental-bert-base-uncased

#### 2. T5 (Summarization)

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

**Paper URL**: http://jmlr.org/papers/v21/20-074.html  
**Model URL**: https://huggingface.co/t5-base

#### 3. Llama 3.2 (Generation)

```bibtex
@misc{llama32,
  title        = {Llama 3.2: Open Foundation and Fine-Tuned Chat Models},
  author       = {{Meta AI}},
  year         = {2024},
  url          = {https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct},
  note         = {Llama 3.2-1B-Instruct with LoRA fine-tuning}
}
```

**Model URL**: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct

---

### Datasets Used

#### 1. Mental Disorders Classification Dataset

```bibtex
@misc{kanakmi2024mental,
  title        = {Mental Disorders Classification Dataset},
  author       = {Kanakmi},
  year         = {2024},
  publisher    = {Hugging Face},
  url          = {https://huggingface.co/datasets/Kanakmi/mental-disorders},
  note         = {Dataset containing 204K samples across 5 mental health conditions}
}
```

**Dataset URL**: https://huggingface.co/datasets/Kanakmi/mental-disorders  
**Size**: 204K training samples  
**Classes**: BPD, Bipolar Disorder, Depression, Anxiety, Schizophrenia

#### 2. PubMed Article Summarization Dataset

```bibtex
@misc{pubmed2023summarization,
  title        = {PubMed Article Summarization Dataset},
  author       = {{The Devastator}},
  year         = {2023},
  publisher    = {Kaggle},
  url          = {https://www.kaggle.com/datasets/thedevastator/pubmed-article-summarization-dataset},
  note         = {Medical text summarization corpus from PubMed abstracts}
}
```

**Dataset URL**: https://www.kaggle.com/datasets/thedevastator/pubmed-article-summarization-dataset

---

## Additional References

### Parameter-Efficient Fine-Tuning (LoRA)

```bibtex
@inproceedings{hu2022lora,
  title     = {{LoRA: Low-Rank Adaptation of Large Language Models}},
  author    = {Edward J. Hu and Yelong Shen and Phillip Wallis and Zeyuan Allen-Zhu and Yuanzhi Li and Shean Wang and Lu Wang and Weizhu Chen},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2022},
  url       = {https://arxiv.org/abs/2106.09685}
}
```

### Quantization (QLoRA)

```bibtex
@article{dettmers2024qlora,
  title   = {{QLoRA: Efficient Finetuning of Quantized LLMs}},
  author  = {Tim Dettmers and Artidoro Pagnoni and Ari Holtzman and Luke Zettlemoyer},
  journal = {Advances in Neural Information Processing Systems (NeurIPS)},
  year    = {2023},
  url     = {https://arxiv.org/abs/2305.14314}
}
```

---

## Framework Citations

### FastAPI

```bibtex
@software{fastapi,
  title  = {FastAPI},
  author = {Sebastián Ramírez},
  year   = {2018},
  url    = {https://fastapi.tiangolo.com/}
}
```

### PyTorch

```bibtex
@incollection{pytorch,
  title     = {PyTorch: An Imperative Style, High-Performance Deep Learning Library},
  author    = {Paszke, Adam and Gross, Sam and Massa, Francisco and Lerer, Adam and Bradbury, James and Chanan, Gregory and Killeen, Trevor and Lin, Zeming and Gimelshein, Natalia and Antiga, Luca and Desmaison, Alban and Kopf, Andreas and Yang, Edward and DeVito, Zachary and Raison, Martin and Tejani, Alykhan and Chilamkurthy, Sasank and Steiner, Benoit and Fang, Lu and Bai, Junjie and Chintala, Soumith},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS)},
  year      = {2019},
  url       = {https://arxiv.org/abs/1912.01703}
}
```

---

## Academic Usage Guidelines

### For Papers and Publications

When referencing this work in academic publications:

1. **Cite this project** using the BibTeX entry above
2. **Cite the base models** (MentalBERT, T5, Llama 3.2) you discuss
3. **Cite the datasets** if you reference the training methodology
4. **Mention the architecture** if relevant to your work

### For Presentations

Recommended acknowledgment text:
> "This system utilizes MentalBERT (Ji et al., 2022), T5 (Raffel et al., 2020), and Llama 3.2 (Meta AI, 2024), fine-tuned on mental health datasets for diagnostic support."

### For Theses and Dissertations

Include:
- Full citations for all models and datasets (see above)
- License information from [ATTRIBUTIONS.md](../ATTRIBUTIONS.md)
- Architecture diagrams crediting the original model designs
- Performance metrics with proper benchmarking methodology

---

## Commercial Usage

All components are licensed for commercial use:
- ✅ MentalBERT: Apache 2.0
- ✅ T5: Apache 2.0
- ✅ Llama 3.2: Llama 3.2 Community License (commercial-friendly)
- ✅ Datasets: Apache 2.0 / CC0

**Requirements**:
1. Maintain attribution notices
2. Comply with Llama 3.2 Acceptable Use Policy
3. Include medical disclaimers
4. Ensure HIPAA/GDPR compliance for patient data

---

## Contributing to Citations

If you've published work using this system:
1. Open a PR adding your citation to this file
2. We'll create a "Built With" section showcasing research
3. Help us build a community of mental health AI researchers

---

**Questions?** Open an issue or contact the maintainer.

**Last Updated**: December 2025
