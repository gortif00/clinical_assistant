#!/usr/bin/env python3
"""
System Verification Demo for Report
=====================================
This script demonstrates the integrated pipeline processing a single clinical text
through all implemented components:
1. Text Classification (Mental Health Condition Detection)
2. Language Modeling - Summarization (T5)
3. Language Modeling - Generation (Llama 3 with LoRA)

Usage:
    python system_verification_demo.py
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.ml.models_loader import load_all_models, get_models
from app.ml.pipeline import generate_treatment_recommendation_with_classification
from app.utils.text_cleaning import clean_text
import json


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}")


def verify_models():
    """Verify all models are loaded correctly"""
    print_section("1. MODEL VERIFICATION")
    
    models = get_models()
    
    components = [
        ("Classification Model", models['classification_model']),
        ("Classification Tokenizer", models['classification_tokenizer']),
        ("T5 Summarizer", models['t5_summarizer']),
        ("Llama Generator", models['llama_model']),
        ("Llama Tokenizer", models['llama_tokenizer'])
    ]
    
    for name, component in components:
        status = "✅ LOADED" if component is not None else "❌ NOT LOADED"
        print(f"{name:.<50} {status}")
    
    # Check critical components
    critical_loaded = all([
        models['classification_model'] is not None,
        models['classification_tokenizer'] is not None,
        models['t5_summarizer'] is not None
    ])
    
    print(f"\n{'Critical Components Status':.<50} {'✅ READY' if critical_loaded else '❌ MISSING'}")
    
    return critical_loaded


def demonstrate_preprocessing(text: str):
    """Demonstrate text preprocessing"""
    print_section("2. TEXT PREPROCESSING")
    
    print("\nOriginal Text (first 200 chars):")
    print(f"  {text[:200]}...")
    print(f"\nLength: {len(text)} characters")
    
    cleaned = clean_text(text)
    print("\nCleaned Text (first 200 chars):")
    print(f"  {cleaned[:200]}...")
    print(f"\nLength: {len(cleaned)} characters")
    
    return cleaned


def demonstrate_classification(result: dict):
    """Display classification results"""
    print_section("3. CLASSIFICATION RESULTS")
    
    classification = result.get('classification', {})
    
    print(f"\n{'Predicted Pathology':.<40} {classification.get('pathology', 'N/A')}")
    print(f"{'Confidence':.<40} {classification.get('confidence', 0):.2%}")
    
    print("\nAll Class Probabilities:")
    all_probs = classification.get('all_probabilities', {})
    sorted_probs = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
    
    for label, prob in sorted_probs:
        bar_length = int(prob * 40)
        bar = "█" * bar_length
        print(f"  {label:.<35} {prob:>6.2%} {bar}")


def demonstrate_summarization(result: dict):
    """Display summarization results"""
    print_section("4. SUMMARIZATION RESULTS (T5 Language Model)")
    
    summary = result.get('summary', '')
    metadata = result.get('metadata', {})
    
    print(f"\n{'Original Length':.<40} {metadata.get('original_text_length', 0)} chars")
    print(f"{'Summary Length':.<40} {metadata.get('summary_length', 0)} chars")
    print(f"{'Compression Ratio':.<40} {metadata.get('summary_length', 1) / max(metadata.get('original_text_length', 1), 1):.2%}")
    
    print("\nClinical Summary:")
    print("─" * 80)
    print(summary)
    print("─" * 80)


def demonstrate_generation(result: dict):
    """Display generation results"""
    print_section("5. TREATMENT GENERATION (Llama 3 Language Model)")
    
    recommendation = result.get('recommendation', '')
    metadata = result.get('metadata', {})
    
    print(f"\n{'Recommendation Length':.<40} {metadata.get('recommendation_length', 0)} chars")
    
    print("\nTreatment Recommendation:")
    print("─" * 80)
    print(recommendation)
    print("─" * 80)


def run_integrated_pipeline():
    """Run the complete integrated pipeline demonstration"""
    print_section("INTEGRATED CLINICAL ASSISTANT PIPELINE DEMONSTRATION")
    print("This demonstration shows all three NLP components working together:\n")
    print("  • Component 1: Text Classification (Mental Health Diagnosis)")
    print("  • Component 2: Language Modeling - Summarization (T5)")
    print("  • Component 3: Language Modeling - Generation (Llama 3 + LoRA)")
    
    # Example clinical case
    clinical_text = """
    Patient is a 34-year-old female presenting with persistent feelings of sadness, 
    hopelessness, and loss of interest in previously enjoyed activities for the past 
    8 weeks. Reports difficulty sleeping (early morning awakening at 4 AM), decreased 
    appetite with 10-pound weight loss, and significant fatigue affecting work performance. 
    Patient describes feeling worthless and has difficulty concentrating on daily tasks. 
    Denies current suicidal ideation but reports occasional thoughts that "life isn't 
    worth living." No prior psychiatric history. Family history significant for depression 
    in mother. Patient reports increased social isolation and withdrawal from friends and 
    family. Describes crying episodes without clear trigger, occurring several times per week. 
    Physical examination unremarkable. PHQ-9 score: 18 (moderately severe depression). 
    Patient is motivated to engage in treatment and has good social support from spouse.
    """
    
    # Load models
    print("\nLoading ML models...")
    if not load_all_models():
        print("\n❌ ERROR: Failed to load all models. Please check model files.")
        return False
    
    # Verify models
    if not verify_models():
        print("\n❌ ERROR: Critical models not loaded. Cannot proceed.")
        return False
    
    # Demonstrate preprocessing
    cleaned_text = demonstrate_preprocessing(clinical_text)
    
    # Run integrated pipeline
    print_section("RUNNING INTEGRATED PIPELINE")
    print("\nProcessing clinical text through all three components...")
    print("(This may take 30-60 seconds depending on your hardware)\n")
    
    models = get_models()
    result = generate_treatment_recommendation_with_classification(
        patient_text=clinical_text,
        classification_model_obj=models['classification_model'],
        classification_tokenizer_obj=models['classification_tokenizer'],
        t5_summarizer_pipeline=models['t5_summarizer'],
        llama_peft_model=models['llama_model'],
        llama_tokenizer_obj=models['llama_tokenizer']
    )
    
    if "error" in result:
        print(f"\n❌ ERROR: {result['error']}")
        return False
    
    # Display results for each component
    demonstrate_classification(result)
    demonstrate_summarization(result)
    demonstrate_generation(result)
    
    # Final summary
    print_section("6. PIPELINE SUMMARY")
    print("\n✅ Successfully processed clinical text through all three components:")
    print(f"  1. Classification → Identified: {result['classification']['pathology']}")
    print(f"  2. Summarization → Generated: {result['metadata']['summary_length']} char summary")
    print(f"  3. Generation → Created: {result['metadata']['recommendation_length']} char recommendation")
    
    # Save results for report
    output_file = "pipeline_demo_results.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n📄 Full results saved to: {output_file}")
    
    return True


def print_system_info():
    """Print system information"""
    print_section("SYSTEM INFORMATION")
    
    try:
        import torch
        print(f"\n{'PyTorch Version':.<40} {torch.__version__}")
        print(f"{'CUDA Available':.<40} {torch.cuda.is_available()}")
        print(f"{'MPS Available (Apple Silicon)':.<40} {torch.backends.mps.is_available()}")
        
        if torch.cuda.is_available():
            print(f"{'CUDA Device':.<40} {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available():
            print(f"{'Device':.<40} Apple Silicon (MPS)")
        else:
            print(f"{'Device':.<40} CPU")
    except Exception as e:
        print(f"Could not retrieve system info: {e}")


def main():
    """Main execution function"""
    print("\n" + "═" * 80)
    print("  CLINICAL ASSISTANT - SYSTEM VERIFICATION FOR REPORT")
    print("═" * 80)
    
    print_system_info()
    
    # Run integrated demo
    success = run_integrated_pipeline()
    
    if success:
        print_section("✅ VERIFICATION COMPLETE")
        print("\nAll components verified and working correctly.")
        print("Results saved and ready for inclusion in report.")
    else:
        print_section("❌ VERIFICATION FAILED")
        print("\nPlease check error messages above and ensure:")
        print("  • All model files are in backend/models/")
        print("  • HF_TOKEN is set for Llama model")
        print("  • All dependencies are installed")
    
    print("\n" + "═" * 80 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
