# Requirements Change for Business Process Compliance (RC4PC)

**Impact Analysis of Regulatory Requirement Changes on Business Process Compliance**

**RC4PC** is a research prototype for analyzing the **impact of changes in regulatory requirements on business process compliance**.  
It implements a **three-step analysis pipeline** that combines AI-assisted analysis and algorithmic change detection to (i) formalize regulatory requirements, (ii) identify atomic requirement changes, and (iii) assess their impact on business process compliance.

This repository accompanies the experiments, analyses, and figures presented in the associated research paper.

---

## Overview of the RC4PC Pipeline

The RC4PC approach consists of three main steps:

1. **Requirement Formalization**  
   Natural-language regulatory requirements are transformed into a structured, machine-interpretable representation using an LLM.

2. **Atomic Change Detection**  
   Fine-grained (atomic) changes between two versions of a requirement are identified using a dedicated change analysis algorithm.

3. **Compliance Impact Analysis**  
   The detected requirement changes are analyzed to assess their impact on business process compliance.

The pipeline is executed iteratively across **multiple datasets and multiple runs** to study result stability.

---


## Repository Structure

```
├── config/        # Configuration files (e.g., API keys)
├── data/          # Input data and outputs for all pipeline steps
├── evaluation/    # Ground truth, baselines, stability analysis, and expert comparisons
├── figures/       # Figures used in the paper
├── notebooks/     # Jupyter notebooks to run the pipeline and analyses
├── scripts/       # Core algorithms and analysis scripts
├── environment.yml
```

---

## Folder Description

### config/

Contains configuration files required to run the pipeline:
- API keys for LLM-based analysis steps
- Other configuration parameters used by notebooks and scripts

---

### data/

Contains **both input and output data** used throughout the experiments.

- **Input data**
  - Multiple versions of regulatory requirements
  - Corresponding business process models
  - Organized per dataset

- **Output data**
  - Intermediate results produced by each pipeline step
  - Final compliance impact analysis results
  - Stored separately for each dataset and each of the five iterations

This structure supports reproducibility and stability analysis.

---

### evaluation/

Contains all artifacts related to evaluation and comparison, including:

1. **Quantitative result analysis**  
   Precision, Recall, and F1-score calculations.

2. **Stability analysis of RC4PC**  
   Analysis of result consistency across multiple iterations.

3. **Ground truth**  
   Gold-standard annotations used for evaluation.

4. **Baseline comparison**  
   Results obtained by applying *Winter et al. (2020)* to the same datasets.

5. **Additional evaluation artifacts**
   - The 9 requirements from *Zasada et al. (2023)* formalized using our requirement representation.
   - Comparison between:
     - Annotations produced by two compliance experts
     - Annotations produced by one of the authors and used as ground truth
   - Includes:
     - Instructions provided to the experts
     - The comparison protocol
     - The expert annotations
     - Analysis of results

---

### figures/

Contains all figures and diagrams included in the associated research paper.

---

### notebooks/

Contains Jupyter notebooks used to execute and analyze the RC4PC pipeline:

- **Main pipeline notebook**  
  Provides an easy-to-use interface for executing:
  - Step 1: Requirement formalization
  - Step 2: Atomic change detection
  - Step 3: Compliance impact analysis

- **Stability analysis notebook**  
  Used to calculate and analyze the stability of the results for step 1 and step 3 across multiple iterations.

---

### scripts/

Contains Python scripts implementing the core logic of RC4PC:

- Implementation of the **atomic change detection algorithm** (Step 2)
- Scripts to:
  - Analyze pipeline outputs
  - Compute result distributions
  - Support evaluation and auxiliary analyses

These scripts are invoked by the notebooks and can also be executed independently.

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <REPOSITORY_URL>
```

### 2. Set Up the Environment

Create and activate the Conda environment:

```bash
conda env create -n rc4pc -f environment.yml
conda activate rc4pc
```

---

## Configuration

Create a file `api_keys.json` inside the `config/` folder:

```json
{
  "api_openai": "your_openai_api_key"
}
```

> Required for pipeline steps that rely on LLM-based analysis.

---

## Running the Pipeline

1. Open the **main Jupyter notebook** in the `notebooks/` folder.
2. Follow the notebook cells to execute:
   - Step 1: Requirement formalization
   - Step 2: Atomic change detection
   - Step 3: Compliance impact analysis
3. Outputs are automatically stored in the corresponding subfolders of `data/`.

---

