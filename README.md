# Compliance Pattern Extraction from Natural Language

This repository contains experiments and analysis code for extracting compliance requirements from natural language, encoding them as AST-like rules, and evaluating these encodings.

## Directory Overview

Top-level folders:

- `Application/`
  - BPMN/PNML examples and specification artifacts used for testing the extracted ASTs.
- `CaseStudy/`
  - Case-study pipeline: process description prompting, file-search-store setup/upload helpers, AST-to-text transformation, and similarity-based case-study evaluation.
- `Eval/`
  - Extraction scripts and benchmark evaluation pipeline (Gemini, GPT, Sonnet), plus merged outputs and ground truth.
- `UserStudy/`
  - User-study materials, generated encodings, and result analysis scripts.

## Dependencies

Use Python 3.10+.

Optional:
```bash
python -m venv .venv
source .venv/bin/activate
```
Required:
```bash
pip install -U pip
pip install openai google-genai anthropic pydantic sentence-transformers torch textdistance fuzzywuzzy pandas numpy matplotlib prompt-toolkit
```

API keys (as needed by the scripts):

- `OPENAI_API_KEY` for `Eval/GPT/*.py`
- `GEMINI_API_KEY` for `Eval/Gemini/*.py` and `CaseStudy/*.py`
- `ANTHROPIC_API_KEY` for `Eval/Sonnet/*.py`

Define these as enviroment variables (i.e., add to .bashrc), or modify the extraction scripts to directly use your own keys.

## User Study

The links to the actual 3 Studies will be posted after double blind.

Main folder: `UserStudy/`

- `GeneratedEncodings/`: generated JSON encodings used in study preparation.
- `Results/`: CSV survey exports, GT mapping files, and analysis scripts.

Typical workflow:

1. Place or update CSV result files in `UserStudy/Results/` (for example `GroupA.csv`, `GroupB.csv`, `GroupC.csv`).
2. Run the analysis script:

```bash
cd UserStudy/Results
python eval.py
```

3. The script computes per-question averages and writes files such as:
   - `GroupA.csv_averages.csv`
   - `GroupB.csv_averages.csv`
   - `GroupC.csv_averages.csv`

Notes:
- `UserStudy/Results/eval.py` expects semicolon-separated CSV files.
- Ground-truth type mapping (which answer is humanmade, which answers are generated) is read from `UserStudy/Results/GroupBGT.csv`.

## Replicat: Empirical Evaluation

Main folder: `Eval/`

- `gt/`: benchmark ground truth JSONs (`bpmq`, `crl`, `pcl`, `ppsl`, `status`, `sun`, `zasada`, etc.).
- `Gemini/`, `GPT/`, `Sonnet/`: model-specific extraction, dataset generation, and merge scripts.
- `eval.py`, `eval_ml.py`, `eval_ml_all.py`: evaluation scripts over merged outputs. 
- `eval_ml_all.py` is the script used for the final results in the Paper

### 1) Run a single extraction

Example (Gemini):

```bash
cd Eval/Gemini
python extract.py bpmq --temperature 0.3 --range 1
```

Equivalent scripts exist for:

- `Eval/GPT/extract.py`
- `Eval/Sonnet/extract.py`

Each writes timestamped JSON outputs in the current model folder.

### 2) Run full dataset generation (all temperatures / datasets)

From a model folder:

```bash
python generate_dataset.py
```

This creates multiple timestamped files (typically moved/stored under `raws/`).

### 3) Merge raw outputs per model

```bash
python merge.py
```

This creates `merged_results.json` in the model folder, by reading all the files generated in raws.

### 4) Evaluate merged outputs

From `Eval/`:

```bash
python eval.py --file Gemini/merged_results.json
python eval_ml.py --file Gemini/merged_results.json --threshold 0.70
python eval_ml_all.py --threshold 0.70
```

## Replicate: Case Study

Main folder: `CaseStudy/`

- `ProcessDescription.py`: generate NL + AST requirements from a process description using Gemini and optional file-search-store grounding.
- `upload.py` / `create.py`: helper scripts for creating and populating a Gemini file search store.
- `case_study_eval.py`: evaluate AST↔NL semantic consistency for all JSON files in `Outputs/`.
- `ast_transform.py`: inspect AST-to-text transformation + similarity for a single JSON file.
- `TransASTParser.py`, `translation.py`, `translationsimple.py`: AST translation internals.

### 1) Create and populate a file search store

```bash
cd CaseStudy
python create.py
python upload.py /path/to/source.pdf exam_regulation.pdf
```

### 2) Generate case-study requirements from process text

```bash
python ProcessDescription.py "Your process description text" 0.3
```
Process description can also just be questions regarding a process or similar as can be seen from the Ouput files in CaseStudy/Outputs.

Output is written to `CaseStudy/Outputs/<temperature>_<timestamp>.json` and includes:

- `input_text`
- `NL_requirements`
- `AST_requirements`
- `citations`

### 3) Evaluate generated outputs in bulk

```bash
python case_study_eval.py --input-dir Outputs --threshold 0.6898
```

### 4) Inspect a single output file

```bash
python ast_transform.py Outputs/<your_file>.json
```


