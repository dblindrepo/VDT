# VDT converter

A rule-based converter that transforms Vietnamese **constituency trees** (phrase-structure annotation with functional tags) into **dependency trees** in [CoNLL-U](https://universaldependencies.org/format.html) format. The system is designed for the **NIIVTB-1** annotation scheme and assigns relations from the **VDT** label inventory (83 dependency relations; see [`README.md`](README.md)).

## Source layout

```
vdt_converter/
├── main.py               # CLI: batch conversion over NIIVTB-1 splits
├── converter.py          # Pipeline orchestration and CoNLL-U record assembly
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

### 1. Preprocessing (`to_oneline`)

- Extracts sentences from `<s>…</s>` markup.
- Collapses internal whitespace so each sentence is a single Penn Treebank–style line.
- Writes intermediate files as `OneLine/<Split>/[Line]<name>.prd`.

### 2. Head percolation and labeling (`get_dependency_tree_list`)

**Head percolation** (`head_percolation.py`):

- Applies phrase-type-specific head tables for 16 categories (`S`, `SQ`, `SPL`, `SBAR`, `NP`, `VP`, `ADJP`, `RP`, `QP`, `PP`, `QNP`, `QADJP`, `QRP`, `QPP`, `UCP`, `CONJP`).
- Detects coordination (`PU`, `Cp`, `CONJP`, `S`/`SPL` mixes) and assigns `conj` / `cc` / `punct` links between conjuncts before generic head rules run.
- Maps each constituent to a lexical head index via `assign_headword_for_phrase()`.

**Dependency labeling** (`dependency_rules.py`):

- For each token, determines parent phrase `P` and child phrase `C` from head indices and tree addresses.
- Runs `get_dependency_relation()`—a **fixed-order cascade** of pattern checks (subjects, objects, complements, locative/temporal modifiers, relative clauses, determiners, coordination, etc.).
- Reads functional tags from constituent labels (e.g. `-SBJ`, `-CMP`, `-LOC`) via `get_function_tag()` into column 6 (`FEATS`).
- Falls back to `dep` when no rule matches.

**Tree utilities** (`preprocessing.py`):

- Address manipulation (`str_to_list`, `get_subtree`, `get_all_subtree_address`).
- POS tags from pre-terminal nodes (`get_all_POS`).
- Leaf re-indexing for rule lookup (`from_word_to_number`).

### 3. Post-processing (`finish_dependency_tree` → `postprocessing.py`)

Applied per sentence before write:

1. **Enhanced dependencies** — map co-indexed `NULL` traces to antecedent phrases (`add_second_relation`, `edit_second_relation_of_NULL`).
2. **Head relinking** — reattach dependents of NULL-headed subtrees to surface tokens (`relink_head_NULL`).
3. **NULL removal** — drop empty categories and re-index token IDs (`remove_NULL`, `map_index`).
4. **Label fixes** — passive subject/object relabeling (*bị/được*), negation, punctuation consistency (`fix_tree` → `edit_VCOMP_or_CCOMP`, `get_subjpass`, `edit_NEG`, `fix_PU`).

Output files: `VnDep/<Split>/[VnDep]<name>.conllu`, each sentence prefixed with `# ID = <n>`.

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
- [NLTK](https://www.nltk.org/) (constituency tree parsing)

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
