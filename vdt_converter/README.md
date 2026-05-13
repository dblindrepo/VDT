# VDT Converter

The automatic conversion from constituency trees to dependency structures relies heavily on predefined linguistic rules. Consequently, poorly designed head-selection rules may lead to incorrect head identification, which subsequently propagates errors to downstream dependency relations. In addition, structural ambiguities in constituency trees—where different syntactic structures express equivalent semantic meanings—can further introduce conversion inconsistencies.

To address these challenges, this directory provides the implementation of the constituent-to-dependency converter used in the semi-automatic construction pipeline of VDT. The converter transforms constituency trees into dependency structures through four major stages:

1. **Head Identification** — determines the syntactic head of each constituent based on predefined Vietnamese-specific head rules.
2. **Coordination Handling** — resolves coordination structures and assigns appropriate dependency relations.
3. **Dependency Label Assignment** — assigns labels for dependencies.
4. **NULL Element Processing** — handles traces and empty categories to preserve structural consistency.

The converter serves as the first core component of the semi-automatic annotation framework, producing the initial dependency treebank (**VDT Auto**) that is subsequently refined through manual revision and quality assurance procedures.

---

## Project Structure

```text
vdt_converter/
├── main.py                  # Command-line entry point
├── converter.py             # End-to-end conversion pipeline
├── preprocessing.py         # Tree traversal utilities and POS extraction
├── head_percolation.py      # Head-finding rules and headword assignment
├── dependency_rules.py      # Dependency relation labeling rules
├── postprocessing.py        # NULL resolution, head relinking, and label correction
└── NIIVTB-1/                # Input treebank directory (Train/Dev/Test splits)
```

---

## Module Descriptions

| Module | Description |
|---|---|
| `preprocessing.py` | Provides utility functions for tree address manipulation (string-to-list conversion), breadth-first enumeration of subtree addresses, POS-tag extraction, and word-to-index mapping. |
| `head_percolation.py` | Implements head-percolation tables for phrase categories such as `S`, `NP`, `VP`, `ADJP`, and `PP`, with specialized handling for right-headed structures and coordination ambiguities. |
| `dependency_rules.py` | Defines a prioritized cascade of pattern-matching rules for assigning dependency labels based on POS tags, function tags and constituency tags. |
| `postprocessing.py` | Handles NULL elements through co-indexed trace resolution and applies post-hoc corrections for passive constructions, negation consistency. |
| `converter.py` | Orchestrates the full conversion pipeline, including constituency parsing, head assignment, dependency generation, and CoNLL-U export. |
| `main.py` | Parses command-line arguments, initializes output directories, and processes all `.prd` files across dataset splits. |


## Requirements

```bash
pip install nltk
```


## Usage

```bash
python main.py --input-dir <path_to_NIIVTB-1> [--base-dir <output_directory>]
```

| Argument | Required | Description |
|---|---|---|
| `--input-dir` | Yes | Path to the NIIVTB-1 treebank directory containing `Train/`, `Dev/`, and `Test/` subdirectories with `.prd` files. |
| `--base-dir` | No | Root directory for output files. Defaults to the parent directory of `--input-dir`. |


## Example

```bash
# Input data in the current project directory
python main.py --input-dir ./NIIVTB-1

# Specify a separate output directory
python main.py --input-dir ./NIIVTB-1 --base-dir ./output
```


## Output Structure

The following directories are automatically generated under `<base-dir>`:

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

- `OneLine/` stores intermediate linearized constituency representations.
- `VnDep/` contains the final dependency trees in CoNLL-U format.


## Output Format

Each generated file follows the standard CoNLL-U 10-column format:

| Column | Field | Description |
|---|---|---|
| 1 | ID | Token index (1-based) |
| 2 | FORM | Word form |
| 3 | LEMMA | Underscore (`_`) placeholder |
| 4 | UPOS | Part-of-speech tag |
| 5 | XPOS | Underscore (`_`) placeholder |
| 6 | FEATS | Functional tag (e.g., `PRD`, `CMP`, `TMP`) |
| 7 | HEAD | Index of the syntactic head (`0` for root) |
| 8 | DEPREL | Dependency relation label |
| 9 | DEPS | Enhanced dependency relations |
| 10 | MISC | Underscore (`_`) placeholder |