# VDT: A Vietnamese Dependency Treebank via Semi-Automatic Annotation


This repository contains the implementation and resources for **VDT (Vietnamese Dependency Treebank)**. VDT is a high-precision linguistic resource developed using a semi-automatic annotation framework designed to bridge the gap between scalability and quality.

## Key Highlights

*   **Custom Label Set:** Introduces **83 dependency relations** designed to cover specific characteristics of Vietnamese (Sino-Vietnamese, classifier nouns, etc.).
*   **High Precision:** Combines the speed of algorithmic conversion with the rigor of manual post-editing.
*   **Scalability:** Provides a rule-based converter to transform constituency trees (NIIVTB-1) into dependency structures.

---

## Construction Pipeline

The construction of VDT follows a two-stage pipeline:

1.  **Phase 1: Automatic Conversion**  
    A specialized rule-based converter transforms the **NIIVTB-1** constituency treebank into an initial dependency version, referred to as VDT Auto.
2.  **Phase 2: Manual Post-editing**  
    Well-trained annotators perform rigorous manual edditing on *VDT Auto* to produce the final gold-standard treebank, VDT.

<p align="center">
  <img src="VDT-process.png" alt="VDT Construction Process" width="850"/>
</p>

---

## Dataset Statistics

The VDT corpus consists of **10,418 sentences** extracted from the NIIVTB-1 corpus, containing **224,249 tokens** with an overall Mean Dependency Distance (MDD) of **3.25**.

| Split | Sentences | Tokens |
|:------|----------:|-------:|
| Train | 8,418 | 177,243 |
| Dev   | 1,000 | 23,592 |
| Test  | 1,000 | 23,414 |

---

## Reproducing the Conversion (Quick Start)

To replicate the generation of **VDT Auto** from the source constituency trees, follow these steps:
### 1. Requirements
```bash
pip install nltk
```

### 2. Data Setup
Download the source **NIIVTB-1** treebank from its [official repository](https://github.com/mynlp/niivtb). Organize the files as follows:

```text
vdt_converter/
└── NIIVTB-1/
    ├── Train/
    ├── Dev/
    └── Test/
```
### 3. Run Conversion 
```bash
cd vdt_converter

python main.py --input-dir <path_to_NIIVTB-1> [--base-dir <output_directory>]
```

## Note: 
For a detailed breakdown of the conversion logic, head-percolation rules, and module descriptions, please refer to the [Converter Documentation](https://github.com/dblindrepo/VDT/tree/main/vdt_converter).

### 4. Output

The converter generates two sets of outputs under `<base-dir>/`:

```text
<base-dir>/
├── OneLine/              # Intermediate one-sentence-per-line files
│   ├── Train/
│   ├── Dev/
│   └── Test/
└── VnDep/                # Final CoNLL-U dependency trees
    ├── Train/
    ├── Dev/
    └── Test/
```

- `OneLine/` contains intermediate linearized representations.
- `VnDep/` contains the final converted dependency trees in CoNLL-U format.

## Release Notice

This repository is currently anonymized for double-blind review. The full guidelines and the final treebank will be publicly released upon paper acceptance.
