# VDT converter

A rule-based converter that transforms Vietnamese **constituency trees** into **dependency trees** in [CoNLL-U](https://universaldependencies.org/format.html) format. The system is designed for the **NIIVTB-1** annotation scheme and assigns relations from the **VDT** label inventory.

## Module descriptions

| Module | Role |
|--------|------|
| main.py | CLI & Batch Processing: Handles arguments, sets up directory splits, and loops through data files. |
| converter.py | Pipeline coordinator and CoNLL-U format record builder |
| preprocessing.py | Tree addressing, POS extraction, leaf indexing |
| head_percolation.py | Phrasal head determining via head-percolation rules and coordination handling |
| dependency_rules.py | Dependency relation labeling |
| postprocessing.py | NULL/trace resolution and passive voice, negation correction |

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

