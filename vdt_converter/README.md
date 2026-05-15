# VDT converter

A rule-based converter that transforms Vietnamese **constituency trees** into **dependency trees** in [CoNLL-U](https://universaldependencies.org/format.html) format. The system is designed for the **NIIVTB-1** annotation scheme and assigns relations from the **VDT** label inventory (83 dependency relations; see [`README.md`](README.md)).

## Source layout

```
vdt_converter/
├── main.py               # CLI: batch conversion over NIIVTB-1 splits
├── converter.py          # Core conversion logic: head–dependent mapping, CoNLL-U record assembly, and file I/O
├── preprocessing.py      # Tree addresses, POS extraction, leaf indexing
├── head_percolation.py   # Head-percolation tables and coordination handling
├── dependency_rules.py   # Dependency relation labeling (83-label cascade)
├── postprocessing.py     # NULL/trace resolution and label correction
└── README.md   # This file
```

Input treebank data (not shipped in this repo) is expected in a sibling directory such as `NIIVTB-1/` with `Train/`, `Dev/`, and `Test/` subfolders containing `.prd` files.

## Conversion pipeline

`main.py` runs three steps for every `.prd` file:

```
.prd (constituency, <s>…</s>)
        │
        ▼  to_oneline()
OneLine/[Line]*.prd          one tree per line, whitespace-normalized
        │
        ▼  get_dependency_tree_list()
        │    • NLTK Tree.fromstring()
        │    • assign_headword_for_phrase()  — head percolation + coordination
        │    • get_dependency_relation()     — label each dependent
        │    • build 10-field CoNLL-U rows per token
        │
        ▼  finish_dependency_tree()
VnDep/[VnDep]*.conllu        post-process + write (# ID = n headers)
```

## Module reference

| Module | Role |
|--------|------|
| `main.py` | Argument parsing, output directory setup, glob over `*/*.prd`, sequential three-step batch run. |
| `converter.py` | `get_all_relation()` builds head/relation maps; `get_dependency_tree_list()` assembles CoNLL-U rows; `to_oneline()` and `finish_dependency_tree()` handle I/O. |
| `preprocessing.py` | Subtree navigation, breadth-first addresses, POS and leaf-index helpers. |
| `head_percolation.py` | `HEAD_PERCOLATION_RULES`, conjunction detection, recursive `assign_headword_for_phrase()`. |
| `dependency_rules.py` | Predicate helpers (`has_SBJ`, `is_DOBJ`, …) and `get_dependency_relation()` cascade. |
| `postprocessing.py` | NULL/antecedent resolution, second relations, relinking, indexing, and tree-wide label corrections. |

## Requirements

- Python 3
- [NLTK](https://www.nltk.org/)

```bash
pip install nltk
```

## Setup

Clone the repository and place the [NIIVTB-1 treebank](https://github.com/mynlp/niivtb) in the following layout:

```
NIIVTB-1/
├── Train/*.prd
├── Dev/*.prd
└── Test/*.prd
```

Each `.prd` file contains bracketed constituency trees enclosed in `<s>…</s>` sentence markup.

## Usage

```bash
python main.py --input-dir <path_to_NIIVTB-1> [--base-dir <output_root>]
```

| Argument | Required | Description |
|----------|:--------:|-------------|
| `--input-dir` | Yes | Path to the NIIVTB-1 directory (`Train/`, `Dev/`, `Test/`). |
| `--base-dir` | No | Output root directory. Defaults to the parent of `--input-dir`. |

Examples:

```bash
python main.py --input-dir ./NIIVTB-1
python main.py --input-dir ./NIIVTB-1 --base-dir ./output
```

## Output

```
<base-dir>/
├── OneLine/     # One constituency tree per line ([Line]*.prd)
└── VnDep/       # CoNLL-U dependency trees ([VnDep]*.conllu)
    ├── Train/
    ├── Dev/
    └── Test/
```

## Related documentation

- [`README.md`](README.md) — VDT treebank overview, label taxonomy, and citation
- `dependency_labeling_procedures.pdf` — formal specification of the labeling cascade
