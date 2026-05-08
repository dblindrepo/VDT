import os
import glob
import argparse

from converter import to_oneline, get_dependency_tree_list, finish_dependency_tree


FOLDERS = ['Train', 'Dev', 'Test']


def setup_directories(base_dir):
    oneline_dir = os.path.join(base_dir, 'OneLine')
    output_dir = os.path.join(base_dir, 'VnDep')
    counter_dir = os.path.join(base_dir, 'Counter')

    for directory in [oneline_dir, output_dir, counter_dir]:
        for folder in FOLDERS:
            os.makedirs(os.path.join(directory, folder), exist_ok=True)

    return oneline_dir, output_dir, counter_dir


def main():
    parser = argparse.ArgumentParser(description='VDT Converter - Convert constituency trees to dependency trees')
    parser.add_argument('--input-dir', required=True, help='Path to NIIVTB-1 directory (e.g., /content/NIIVTB-1)')
    parser.add_argument('--base-dir', default=None, help='Base directory for output (default: parent of input-dir)')
    args = parser.parse_args()

    input_dir = args.input_dir
    base_dir = args.base_dir or os.path.dirname(input_dir)

    oneline_dir, output_dir, counter_dir = setup_directories(base_dir)

    path_list = sorted(glob.glob(os.path.join(input_dir, '*', '*.prd')))
    total_files = len(path_list)
    print(f"Found {total_files} .prd files to process")

    for index, path in enumerate(path_list):
        folder = os.path.basename(os.path.dirname(path))
        filename = os.path.basename(path)
        print(f"\n[{index + 1}/{total_files}] File: {folder}/{filename}")

        print("  Step 1: Converting to one-line format...")
        to_oneline(input_dir, oneline_dir, folder, filename)

        print("  Step 2: Building dependency trees...")
        dependency_treebank = get_dependency_tree_list(oneline_dir, folder, filename)

        print("  Step 3: Post-processing & writing CoNLL-U...")
        finish_dependency_tree(oneline_dir, output_dir, folder, filename, dependency_treebank)

        print("  Done.")


if __name__ == '__main__':
    main()
