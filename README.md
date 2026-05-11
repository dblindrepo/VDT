# VDT: A New Vietnamese Dependency Treebank via Semi-Automatic Annotation

A rule-based system for converting Vietnamese constituency trees into dependency representations in the CoNLL-U format. The conversion pipeline implements head-percolation rules and dependency labeling heuristics tailored to the annotation scheme of the NIIVTB-1 Vietnamese treebank.

## Overview

The system takes as input phrase-structure trees annotated with functional tags (e.g., `-SBJ`, `-CMP`, `-LOC`) and produces labeled dependency trees through the following stages:

1. **Head percolation**: Head-finding rules are applied recursively to identify the headword of each constituent. Coordination structures are detected and handled via conjunction-specific heuristics.
2. **Dependency labeling**: The dependency relation between a dependent and its head is determined by a cascade of rules conditioned on the constituent labels of the child node (C) and its parent (P).
3. **Post-processing**: NULL elements are resolved by relinking their dependents to the appropriate antecedent, second-order dependencies (enhanced dependencies) are propagated, and passive constructions involving *bi/duoc* are re-labeled.

## Project Structure

```
vdt_converter/
├── main.py                  # Command-line entry point
├── converter.py             # End-to-end conversion pipeline
├── preprocessing.py         # Tree traversal utilities and POS extraction
├── head_percolation.py      # Head-finding rules and headword assignment
├── dependency_rules.py      # Dependency relation labeling rules
├── postprocessing.py        # NULL resolution, head relinking, and label correction
└── NIIVTB-1/                # Input treebank directory (Train/Dev/Test splits)
```

## Requirements

```bash
pip install nltk
```

## Usage

```bash
python main.py --input-dir <path_to_NIIVTB-1> [--base-dir <output_directory>]
```

### Arguments

| Argument | Required | Description |
|---|---|---|
| `--input-dir` | Yes | Path to the NIIVTB-1 treebank directory containing `Train/`, `Dev/`, and `Test/` subdirectories with `.prd` files. |
| `--base-dir` | No | Root directory for output files. Defaults to the parent directory of `--input-dir`. |

### Example

```bash
# Input data in the current project directory
python main.py --input-dir ./NIIVTB-1

# Specify a separate output directory
python main.py --input-dir ./NIIVTB-1 --base-dir ./output
```

### Output Structure

The following directories are created automatically under `<base-dir>`:

```
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

## Output Format

Each output file follows the CoNLL-U 10-column format:

| Column | Field | Description |
|---|---|---|
| 1 | ID | Token index (1-based) |
| 2 | FORM | Word form |
| 3 | LEMMA | Underscore (not used) |
| 4 | UPOS | Part-of-speech tag |
| 5 | XPOS | Underscore (not used) |
| 6 | FEATS | Functional tag (e.g., PRD, CMP, TMP) |
| 7 | HEAD | Index of the syntactic head (0 for root) |
| 8 | DEPREL | Dependency relation label |
| 9 | DEPS | Enhanced dependencies (second relations) |
| 10 | MISC | Underscore (not used) |

