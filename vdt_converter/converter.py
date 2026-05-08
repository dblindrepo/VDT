import re
import glob
import os

from nltk.tree import Tree

from preprocessing import from_word_to_number, get_all_POS
from head_percolation import assign_headword_for_phrase
from dependency_rules import (
    get_C_of_headword, get_P_of_C,
    get_dependency_relation, get_function_tag
)
from postprocessing import (
    get_phrase_has_linked_NULL, get_phrase_contain_index,
    add_second_relation, edit_second_relation_of_NULL,
    relink_head_NULL, remove_NULL, fix_tree
)


def get_all_relation(tree):
    tree = from_word_to_number(tree)

    result = assign_headword_for_phrase(tree)

    headword_of_phrase = result[0]
    C_of_headword = get_C_of_headword(headword_of_phrase)

    P_of_C_dic = result[1]
    relation_dic = {}
    root_address = C_of_headword[headword_of_phrase['root']]

    P_index = '0'
    relation = 'root'
    C_index = headword_of_phrase['root']
    relation_dic[C_index] = [P_index, relation]

    for C_index in tree.leaves():
        if C_index not in relation_dic:
            C_address = C_of_headword[C_index]
            if C_address in P_of_C_dic:
                P_address = P_of_C_dic[C_address][0]
                relation = P_of_C_dic[C_address][1]
                P_index = headword_of_phrase[P_address]
                relation_dic[C_index] = [P_index, relation]
            else:
                P_address = get_P_of_C(C_address, root_address)
                P_index = headword_of_phrase[P_address]
                relation = get_dependency_relation(P_address, C_address, P_index, C_index, tree)
                relation_dic[C_index] = [P_index, relation]
    return relation_dic


def get_dependency_tree_list(oneline_dir, folder, filename):
    filepath = os.path.join(oneline_dir, folder, f'[Line]{filename}')
    with open(filepath, 'r', encoding='utf8') as reader:
        lines = reader.readlines()

    print(f"  [get_dependency_tree_list] {folder}/{filename}: {len(lines)} sentences")

    dependency_tree_list = []
    for line_num, line in enumerate(lines, 1):
        print(f"    Processing sentence {line_num}/{len(lines)}...")
        dependency_tree = []
        tree = Tree.fromstring(line)
        original_tree = Tree.fromstring(line)
        relations = get_all_relation(tree)
        POS_tags = get_all_POS(tree)
        function_tag_list = get_function_tag(tree)

        for index, word in enumerate(original_tree.leaves()):
            word_index = str(index + 1)
            head_index = relations[word_index][0]
            relation = relations[word_index][1]
            POS = POS_tags[index]
            function_tag = function_tag_list[word_index]
            dependency_tree.append([word_index, word, '_', POS, '_', function_tag, head_index, relation, '_', '_'])
        dependency_tree_list.append(dependency_tree)
    return dependency_tree_list


def to_oneline(input_dir, oneline_dir, folder, filename):
    input_path = os.path.join(input_dir, folder, filename)
    output_path = os.path.join(oneline_dir, folder, f'[Line]{filename}')

    with open(input_path, 'r', encoding='utf8') as reader:
        regex = r'(?<=<s>).+?(?=</s>)'
        pattern = re.compile(regex, re.M | re.I | re.S)
        data = reader.readlines()
        data = ''.join(data)
        sentences = re.findall(pattern=pattern, string=data)

    with open(output_path, 'w', encoding='utf8') as writer:
        for sentence in sentences:
            writer.write(re.sub(re.compile(r'[\s\t\n]+', re.I | re.M), ' ', sentence).strip())
            writer.write('\n')


def finish_dependency_tree(oneline_dir, output_dir, folder, filename, dependency_treebank):
    oneline_path = os.path.join(oneline_dir, folder, f'[Line]{filename}')
    with open(oneline_path, 'r', encoding='utf8') as reader:
        lines = reader.readlines()

    new_filename = filename[:-4] + '.conllu'
    output_path = os.path.join(output_dir, folder, f'[VnDep]{new_filename}')

    with open(output_path, 'w', encoding='utf8') as writer:
        tree_index = 1
        for line, dependency_tree in zip(lines, dependency_treebank):
            print(filename, line)
            tree = Tree.fromstring(line)
            linked_NULL_list = get_phrase_has_linked_NULL(tree)
            map_phrase_list = get_phrase_contain_index(tree)

            new_dependency_tree = add_second_relation(tree, dependency_tree, linked_NULL_list, map_phrase_list)
            edit_dependency_tree = edit_second_relation_of_NULL(tree, new_dependency_tree, linked_NULL_list, map_phrase_list)
            relink_headNULL_dependency_tree = relink_head_NULL(edit_dependency_tree)
            remove_NULL_dependency_tree = remove_NULL(relink_headNULL_dependency_tree)
            new_tree_dep = fix_tree(remove_NULL_dependency_tree)

            writer.write('# ID = {}\n'.format(tree_index))
            tree_index = tree_index + 1
            for element in edit_dependency_tree:
                writer.write('\t'.join(element))
                writer.write('\n')
            writer.write('\n')


def count_folder(oneline_dir, counter_dir, folder, filename):
    oneline_path = os.path.join(oneline_dir, folder, f'[Line]{filename}')
    counter_path = os.path.join(counter_dir, folder, filename)

    count = 0
    with open(oneline_path, 'r', encoding='utf8') as reader:
        lines = reader.readlines()

    with open(counter_path, 'w', encoding='utf8') as writer:
        for line in lines:
            count += 1
        writer.write(format(count))
