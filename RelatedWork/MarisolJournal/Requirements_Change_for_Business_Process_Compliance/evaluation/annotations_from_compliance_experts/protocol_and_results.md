# Comparison of Annotations from Experts

## 1. Evaluation Methodology Overview

The evaluation is structured around two annotation tasks performed independently by two domain experts (Expert 1 and Expert 2):

- **Task 1 – Requirement Formalization**  
  Experts formalize natural-language requirements using the proposed notation.

- **Task 2 – Compliance Impact Analysis**  
  Experts assess how changes in requirements affect the compliance of an existing process model.

A ground truth was established by the authors and used as a reference for both tasks. Importantly, the evaluation does not assume a single correct encoding, but explicitly accounts for annotation-style variability.

---

## 2. Task 1 – Methodology (Formalization vs. Ground Truth)

### 2.1 Unit of Analysis

The unit of analysis in Task 1 is a single expert formalization of:
- one requirement,
- one version (v1 or v2),
- by one expert.

This results in:
- **20 requirements**
- **2 versions**
- **2 experts**
- **80 Task 1 annotations**

---

### 2.2 Comparison Procedure

Each expert annotation was compared against the ground truth along the following dimensions:

1. **Semantic coverage**
   - Are all required elements present? (e.g., precondition, norm)
   - Are the correct actions, roles, modalities, etc, captured?

2. **Structural encoding**
   - Preconditions vs. embedded data constraints
   - Explicit vs. implicit permissions
   - Single vs. multiple norms
   - Control-flow vs. temporal encoding

3. **Deontic correctness**
   - Obligation vs. permission vs. prohibition
   - No unintended strengthening or weakening

---

### 2.3 Alignment Categories

Each annotation was assigned exactly one of the following labels:

- **Full alignment**  
  The expert formalization matches the ground truth both semantically and structurally.

- **Style-equivalent alignment**  
  The expert formalization differs only in modeling style, while preserving the same semantic meaning.

- **Partial misalignment**  
  A semantic element is missing or incorrectly represented (e.g., omitted obligation or wrong modality).

Style-equivalent annotations are treated as semantically correct.

---

## 3. Task 1 – Quantitative Results

### 3.1 Overall Alignment Distribution

| Alignment category | Count | Percentage |
|-------------------|-------|------------|
| Full alignment | 49 | 61.25% |
| Style-equivalent alignment | 30 | 37.5% |
| Partial misalignment | 1 | 1.25% |
| **Total** | **80** | **100%** |

**Semantic alignment rate:**

49 + 30 / 80 = 98.75\%


Only one annotation exhibits a true semantic deviation from the ground truth.

---

### 3.2 Results per Expert

**Expert 1**
- Full alignment: 24  
- Style-equivalent alignment: 16  
- Partial misalignment: 0  

➡ **Semantic alignment: 100%**

**Expert 2**
- Full alignment: 25  
- Style-equivalent alignment: 14  
- Partial misalignment: 1  

➡ **Semantic alignment: 97.5%**

The single partial misalignment occurs in **r17_v1**, where a secondary obligation (“record the reason in the system”) was omitted.

---

### 3.3 Observed Patterns in Task 1

**Pattern 1 – Style dominates over error**  
Most non-identical annotations are style-equivalent rather than incorrect.

**Pattern 2 – Errors occur only in complex requirements**  
The only true misalignment occurs in a requirement combining multiple preconditions, temporal constraints, and multiple consequences.

**Pattern 3 – No systematic expert bias**  
Neither expert shows systematic misunderstanding; differences are localized and non-recurrent.

---

## 4. Task 2 – Methodology (Compliance Impact Analysis)

### 4.1 Unit of Analysis

The unit of analysis in Task 2 is one changed requirement evaluated once per expert, resulting in **20 judgments per expert**.

---

### 4.2 Labeling Scheme

Experts classified the process impact using three labels:

- **NC (Non-Compliant)** – the process violates the requirement  
- **OC (Over-Compliant)** – the process enforces stricter behavior than required  
- **NE (No effect)** – the requirement has no effect

---

## 5. Task 2 – Quantitative Results

### 5.1 Per-Expert Label Distribution

| Expert | NC | OC | NE | Total |
|------|----|----|----|------|
| Expert 1 | 10 | 9 | 1 | 20 |
| Expert 2 | 9 | 6 | 5 | 20 |

Expert 2 assigns NE more frequently, reflecting a stricter interpretation of no effect, while Expert 1 more often classifies such cases as over-compliance.

---

### 5.2 Inter-Annotator Agreement

- **Observed agreement (Po):** 0.70  
- **Expected agreement (Pe):** 0.37  
- **Cohen’s κ:** **0.52** (moderate agreement)

This level of agreement is expected given the fine-grained, three-category labeling scheme.

---

## 6. Interpretation of Task 2 Agreement Patterns

**Pattern 4 – NC disagreements are meaningful**  
Disagreements involving NC reflect genuine analytical differences in identifying deviations.

**Pattern 5 – OC vs NE disagreements are style-driven**  
Most disagreements occur between OC and NE, reflecting different interpretations of permissions and having no effect.

**Pattern 6 – Binary compliance perspective is more stable**  
Collapsing OC and NE into a single “non-compliant” category substantially increases agreement, indicating high consensus on compliance risk.

---

## 7. Summary of Findings

- **Task 1:** Formalization is highly robust, with **98.75% semantic alignment**. Differences are predominantly stylistic.
- **Task 2:** Compliance impact analysis shows moderate agreement, with disagreements concentrated in borderline over- vs having no effect cases.
- **Overall:** The evaluation shows that different tasks require different evaluation strategies. For requirement formalization (Task 1), multiple semantically equivalent representations must be allowed, as differences largely reflect modeling style rather than errors. In contrast, compliance impact analysis (Task 2) requires convergence on outcomes, since allowing representational variability at this stage would undermine reliable compliance assessment.