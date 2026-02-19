# Compliance Pattern Extraction from Natural Language

This project extracts compliance patterns and requirements from natural language text using various AI models (GPT, Gemini, Llama, and Claude Sonnet). The extracted patterns are then evaluated against ground truth data to assess extraction accuracy and consistency.

## Folder Structure

### `/Eval`
Main evaluation directory containing:
- **`gt/`** - Ground truth data in JSON format for each process model:
  - `bpmq.json`, `crl.json`, `dcr.json`, `haar.json`, `lyn.json`, `pcl.json`, `ppsl.json`, `status.json`, `sun.json`, `winter.json`, `zasada.json`
  
- **`Gemini/`** - Extraction results using Google's Gemini model
  - `extract.py` - Script to run Gemini-based extraction
  - `*_output.json` - Output files from Gemini extraction
  
- **`GPT/`** - Extraction results using OpenAI's GPT model
  - `extract.py` - Script to run GPT-based extraction
  
- **`Llama/`** - Extraction results using Meta's Llama model
  - `extract.py` - Script to run Llama-based extraction
  
- **`Sonnet/`** - Extraction results using Anthropic's Claude Sonnet model
  - `extract.py` - Script to run Sonnet-based extraction
  
- **`UserStudyPrep/`** - Prepared data for user study evaluation with ground truth annotations
  
- **`outputs/`** - Directory for storing extraction results

- **`eval.py`** - Main evaluation script to compare extractions against ground truth
- **`methods_doc.md`** - Detailed documentation of extraction methods
- **`methods_doc_concise.md`** - Concise summary of extraction methods
- **`annotated_verification_methods.md`** - Documentation of verification methods with annotations

## How to Use

### Running Extraction Scripts

Each AI model has its own `extract.py` script in its respective folder. To run extraction:

```bash
cd Eval/<MODEL>/
python extract.py
```

Replace `<MODEL>` with one of: `Gemini`, `GPT`, `Llama`, or `Sonnet`

**Prerequisites:**
- Required API keys or model access configured for the respective service
- Python 3.x with necessary dependencies installed
- Input data (natural language text to extract patterns from)

**Output:**
- JSON files with extracted compliance patterns and requirements
- Results stored in `Eval/<MODEL>/<model>_output.json` or similar

### Run Evaluation

To evaluate the extraction results against ground truth:

```bash
cd Eval/
python eval.py
```

This will compare all model outputs against the ground truth data in `Eval/gt/` and generate evaluation metrics.

### Generate Comparison Reports

To analyze differences between model extractions:

```bash
python differences_summary.py
python substantial_differences_analysis.py
```

These scripts generate comparative analysis of how different models extracted the same compliance patterns.

## Data Format

- **Ground truth** (`Eval/gt/*.json`): Contains verified compliance patterns and requirements
- **Model outputs** (`Eval/<MODEL>/*_output.json`): Contains patterns extracted by each AI model
- **Format**: JSON files with structured compliance pattern information

## Workflow

1. Process natural language text through each model's extraction script
2. Each model generates JSON output with extracted patterns
3. Run `eval.py` to evaluate accuracy against ground truth
4. Use analysis scripts to identify differences and discrepancies
5. Prepare data for user study in `UserStudyPrep/` for human validation

