import re
from itertools import groupby

from preprocessing import get_all_subtree_address, get_subtree, from_word_to_number
from head_percolation import assign_headword_for_phrase


# --- Second relation ---

def get_phrase_contain_index(tree):
    phrase_index_list = []
    phrase_address_list = get_all_subtree_address(tree)
    for phrase_address in phrase_address_list:
        subtree_label = get_subtree(phrase_address, tree).label()
        if re.search('[0-9]$', subtree_label):
            phrase_type = subtree_label.split('-')[0]
            index = subtree_label.split('-')[-1]
            phrase_index = phrase_type + '-' + index
            phrase_index_list.append((phrase_address, phrase_index))

    phrase_index_dic = dict()
    for phrase_index, phrase_address in groupby(sorted(phrase_index_list, key=lambda ele: ele[1]), key=lambda ele: ele[1]):
        phrase_index_dic[phrase_index] = [ele[0] for ele in phrase_address]
    return phrase_index_dic


def get_phrase_has_linked_NULL(tree):
    word_list = tree.leaves()
    tree = from_word_to_number(tree)
    result = []
    for word, leafPos in zip(word_list, tree.treepositions('leaves')):
        if re.search(r'^\*', word) and word[-1].isnumeric():
            i = -1
            index_word = tree[leafPos]
            address = leafPos[:i]
            POS = tree[address].label()
            while (POS == 'NONE') or (not POS.isupper()):
                i = i - 1
                address = leafPos[:i]
                POS = tree[address].label()
            phrase_type = POS.split('-')[0]
            NULL_index = word[-1]
            phrase_index = phrase_type + '-' + NULL_index
            result.append([index_word, phrase_index, list(address)])
    return result


def get_distance(phrase_address, map_address):
    count = 0
    for phrase_address_index, map_address_index in zip(phrase_address, map_address):
        if phrase_address_index - map_address_index == 0:
            count = count + 1
        else:
            return count
    return count


def find_map_phrase_address(phrase_of_NULL, map_phrase_list):
    phrase_index = phrase_of_NULL[1]
    phrase_address = phrase_of_NULL[2]

    # Priority 1
    for map_phrase, map_phrase_address in map_phrase_list.items():
        if map_phrase == phrase_index:
            if len(map_phrase_address) >= 2:
                distance = []
                for address in map_phrase_address:
                    distance.append(get_distance(phrase_address, address))
                selected_index = distance.index(max(distance))
                return map_phrase_address[selected_index]
            else:
                return map_phrase_address[0]

    # Priority 2
    map_phrase_exception = {
        'NP': r'^(Nc|Ncs|Nu|Nun|Nt|Nq|Num|Nw|Nr|Nn)',
        'VP': r'^(Ve|Vc|D|Vcp|Vv)',
        'ADJP': r'^(An|Aa)',
        'S': r'^SQ',
        'SQ': r'^S($)'
    }
    for map_phrase, map_phrase_address in map_phrase_list.items():
        phrase_type = phrase_index.split('-')[0]
        index_of_phrase = phrase_index.split('-')[1]
        if phrase_type in map_phrase_exception:
            if re.search(map_phrase_exception[phrase_type], map_phrase) and map_phrase[-1] == index_of_phrase:
                if len(map_phrase_address) >= 2:
                    distance = []
                    for address in map_phrase_address:
                        distance.append(get_distance(phrase_address, address))
                    selected_index = distance.index(max(distance))
                    return map_phrase_address[selected_index]
                else:
                    return map_phrase_address[0]
    return False


def add_second_relation(tree, dependency_tree, linked_NULL_list, map_phrase_list):
    headword_of_phrase = assign_headword_for_phrase(tree)[0]
    for linked_NULL in linked_NULL_list:
        element = dependency_tree[int(linked_NULL[0]) - 1]
        head_index = element[6]
        relation = element[7]
        map_phrase_address = find_map_phrase_address(linked_NULL, map_phrase_list)
        if map_phrase_address != False:
            map_index = headword_of_phrase[str(map_phrase_address)]
            map_element = dependency_tree[int(map_index) - 1]
            second_dep = map_element[8]
            if second_dep == '_':
                map_element[8] = head_index + ':' + relation
            else:
                map_element[8] = map_element[8] + '|' + head_index + ':' + relation
    return dependency_tree


def edit_second_relation_of_NULL(tree, dependency_tree, linked_NULL_list, map_phrase_list):
    headword_of_phrase = assign_headword_for_phrase(tree)[0]
    for linked_NULL in linked_NULL_list:
        element = dependency_tree[int(linked_NULL[0]) - 1]
        head_index = element[6]
        second_relation = element[8]
        if second_relation != '_':
            map_phrase_address = find_map_phrase_address(linked_NULL, map_phrase_list)
            if map_phrase_address != False:
                map_index = headword_of_phrase[str(map_phrase_address)]
                map_element = dependency_tree[int(map_index) - 1]
                second_dep = map_element[8]
                if second_dep == '_':
                    map_element[8] = second_relation
                else:
                    map_element[8] = map_element[8] + '|' + second_relation
    return dependency_tree


# --- Relink head NULL ---

def get_dep_dic_of_NULL(dependency_tree):
    dep_dic = {}
    for element in dependency_tree:
        word_index = element[0]
        word = element[1]
        NULL_pos = element[3]
        NULL_head_index = element[6]
        NULL_relation = element[7]
        if re.search(r'^\*', word):
            dep_index_list = []
            pos_list = []
            word_list = []
            for temp in dependency_tree:
                dep_word_index = temp[0]
                dep_word = temp[1]
                pos_of_dep_word = temp[3]
                head_index = temp[6]
                if head_index == word_index:
                    dep_index_list.append(dep_word_index)
                    pos_list.append(pos_of_dep_word)
                    word_list.append(dep_word)
            if dep_index_list:
                dep_dic[word_index] = [NULL_pos, NULL_head_index, NULL_relation, dep_index_list, pos_list, word_list]
    return dep_dic


def select_index(NULL_relation, NULL_pos, dep_index_list, pos_list, word_list):
    phrase_type_list = [r'^(NP|Nc|Ncs|Nu|Nun|Nt|Nq|Num|Nw|Nr|Nn)', r'^(VP|Ve|Vc|D|Vcp|Vv|VN)', r'^(VA|NA|ADJP|An|Aa)']
    print("dep_list", dep_index_list)

    if NULL_relation == "root":
        print(dep_index_list[0])
        return dep_index_list[0]
    elif NULL_relation == "conj":
        for i in range(1, len(dep_index_list)):
            print('pos', pos_list[i], 'word', word_list[i], '\n')
            if (pos_list[i] != 'PU') and ('*' not in word_list[i]):
                return dep_index_list[i]

    for phrase_type in phrase_type_list:
        if re.search(phrase_type, NULL_pos):
            for dep_index, pos, word in zip(dep_index_list, pos_list, word_list):
                if (re.search(phrase_type, pos)) and ('*' not in word):
                    return dep_index
    for dep_index, pos, word in zip(dep_index_list, pos_list, word_list):
        if (pos != 'PU') and (pos != 'Cp') and (pos != 'Cs') and ('*' not in word):
            return dep_index

    for dep_index, pos, word in zip(dep_index_list, pos_list, word_list):
        if (pos != 'PU') and ('*' not in word):
            return dep_index


def relink_head_NULL(dependency_tree):
    head_NULL_dic = get_dep_dic_of_NULL(dependency_tree)
    if head_NULL_dic:
        for NULL_index, dep_list in head_NULL_dic.items():
            NULL_pos = dep_list[0]
            NULL_head_index = dep_list[1]
            NULL_relation = dep_list[2]
            dep_index_list = dep_list[3]
            pos_list = dep_list[4]
            word_list = dep_list[5]
            if (len(word_list) == 1) and ('*' not in word_list[0]):
                selected_index = dep_index_list[0]
                selected_element = dependency_tree[int(selected_index) - 1]
                selected_element[6] = NULL_head_index
                selected_element[7] = NULL_relation

                for element in dependency_tree:
                    second_relation_field = element[8]
                    second_relation_list = second_relation_field.split('|')
                    second_relation_list = [
                        selected_index + ':' + second_relation.split(':')[1]
                        if second_relation.split(':')[0] == NULL_index
                        else second_relation
                        for second_relation in second_relation_list
                    ]
                    element[8] = '|'.join(second_relation_list)

            elif len(word_list) >= 2:
                selected_index = select_index(NULL_relation, NULL_pos, dep_index_list, pos_list, word_list)
                selected_element = dependency_tree[int(selected_index) - 1]
                selected_element[6] = NULL_head_index
                selected_element[7] = NULL_relation

                for element in dependency_tree:
                    head_index = element[6]
                    if head_index == NULL_index:
                        element[6] = selected_index

                    second_relation_field = element[8]
                    second_relation_list = second_relation_field.split('|')
                    second_relation_list = [
                        selected_index + ':' + second_relation.split(':')[1]
                        if second_relation.split(':')[0] == NULL_index
                        else second_relation
                        for second_relation in second_relation_list
                    ]
                    element[8] = '|'.join(second_relation_list)
    return dependency_tree


# --- Remove NULL ---

def minus_1(start_index, end_index):
    result = {}
    for index in range(start_index, end_index + 1):
        result[str(index)] = str(index - 1)
    return result


def map_index(tree_dependency, minus_1_map):
    for relation in tree_dependency:
        word_index = relation[0]
        if word_index in minus_1_map:
            relation[0] = minus_1_map[word_index]

        head_index = relation[6]
        if head_index in minus_1_map:
            relation[6] = minus_1_map[head_index]

        if relation[8] != '_':
            new_second_dependency = []
            second_dependency_element = relation[8]
            second_dependency_list = second_dependency_element.split('|')
            for second_dependency in second_dependency_list:
                split_second_dependency = second_dependency.split(':')
                number = split_second_dependency[0]
                dep = split_second_dependency[1]
                if number in minus_1_map:
                    second_dependency = minus_1_map[number] + ':' + dep
                new_second_dependency.append(second_dependency)
            relation[8] = '|'.join(new_second_dependency)

    return tree_dependency


def remove_NULL(tree_dependency):
    for index, element in enumerate(tree_dependency):
        index_word = index + 1
        head_index = element[6]
        second_relation_field = element[8]
        if second_relation_field != '_':
            new_second_relation_list = []
            second_relation_list = second_relation_field.split('|')
            for second_relation in second_relation_list:
                s_head_index = second_relation.split(':')[0]
                if (s_head_index != str(index_word)) and (s_head_index != head_index):
                    new_second_relation_list.append(second_relation)
            if new_second_relation_list:
                element[8] = '|'.join(new_second_relation_list)
            else:
                element[8] = '_'

    check_null_1 = True
    while check_null_1:
        for index, element in enumerate(tree_dependency):
            check_null_2 = True
            word = element[1]
            index_word = index + 1

            if re.search(r'(^\*)', word):
                minus_map = minus_1(index_word + 1, len(tree_dependency))
                tree_dependency = map_index(tree_dependency, minus_map)
                del tree_dependency[index]
                check_null_2 = False
                break
        if check_null_2:
            check_null_1 = False
    return tree_dependency


# --- Fix ambiguous cases ---

def edit_VCOMP_or_CCOMP(tree_dependency):
    for _, element in enumerate(tree_dependency):
        relation = element[7]
        word_index = element[6]
        functionTag = element[5]
        if relation == 'vcomp' or relation == 'ccomp':
            word = tree_dependency[int(word_index) - 1][1]
            if word.lower() == 'bị' or word.lower() == 'được':
                element[7] = element[7] + '_pass'
        elif functionTag == 'CMP':
            if relation == 'vmod':
                element[7] = 'vcomp_pass'
    return tree_dependency


def get_subjpass(tree_dependency):
    for _, element in enumerate(tree_dependency):
        main_relation = element[7]
        second_relation = element[8].split('|') if element[8] != '_' else []

        if main_relation.startswith('n') or 'pp_comp' in main_relation:
            rel_pairs = []
            for rel in second_relation:
                if rel and rel != '_':
                    parts = rel.split(':')
                    if len(parts) == 2:
                        rel_pairs.append((parts[0], parts[1]))
                    else:
                        rel_pairs.append((None, parts[0]))

            has_nsubj = any(r[1] == 'nsubj' for r in rel_pairs)
            has_np_dobj = any(r[1] == 'np_dobj' for r in rel_pairs)

            try:
                headofsub_index = int(element[6])
                main_head_word = tree_dependency[headofsub_index - 1][1].lower() if headofsub_index > 0 else None
            except (IndexError, ValueError):
                main_head_word = None

            def get_head_of_nsubj():
                for idx, (nsubj_index, relname) in enumerate(rel_pairs):
                    if relname == 'nsubj' and nsubj_index:
                        try:
                            head_word = tree_dependency[int(nsubj_index) - 1][1].lower()
                            if head_word in ('bị', 'được'):
                                rel_pairs[idx] = (nsubj_index, 'nsubj_pass')
                        except (IndexError, ValueError):
                            continue

            head_of_nsubj_word = get_head_of_nsubj()

            if has_nsubj and has_np_dobj:
                nsubj_indices = [i for i, r in rel_pairs if r == 'nsubj']
                np_dobj_indices = [i for i, r in rel_pairs if r == 'np_dobj']

                for idx, (nsubj_index, relname) in enumerate(rel_pairs):
                    if relname == 'nsubj':
                        same_index = nsubj_index in np_dobj_indices

                        if not same_index:
                            if head_of_nsubj_word in ('bị', 'được'):
                                rel_pairs[idx] = (nsubj_index, 'nsubj_pass')
                            if main_head_word in ('bị', 'được'):
                                element[7] = main_relation + '_pass'
                        else:
                            rel_pairs[idx] = (nsubj_index, 'nsubj_pass')
                            if head_of_nsubj_word in ('bị', 'được') or main_head_word in ('bị', 'được'):
                                element[7] = main_relation + '_pass'

                rel_pairs = [(i, r) for i, r in rel_pairs if r != 'np_dobj']

            elif has_nsubj and not has_np_dobj:
                for idx, (index, relname) in enumerate(rel_pairs):
                    if relname == 'nsubj' and head_of_nsubj_word in ('bị', 'được'):
                        rel_pairs[idx] = (index, 'nsubj_pass')

            elif not has_nsubj and has_np_dobj:
                if main_head_word in ('bị', 'được'):
                    element[7] = main_relation + '_pass'
                    rel_pairs = [(i, r) for i, r in rel_pairs if r != 'np_dobj']

            elif not rel_pairs and 'subj' in main_relation and main_head_word in ('bị', 'được'):
                element[7] = main_relation + '_pass'

            if not rel_pairs:
                element[8] = '_'
            else:
                element[8] = '|'.join(f"{i}:{r}" if i else r for i, r in rel_pairs)

    return tree_dependency


LIST_NEG = ['không', 'chưa', 'chẳng', 'đâu', 'chưa_thể', 'không_thể', 'chẳng_thể', 'chớ', 'đừng']


def edit_NEG(tree_dependency):
    for _, element in enumerate(tree_dependency):
        relation = element[7]
        index_word = element[0]
        index_head = element[6]
        word = element[1]
        if word.lower() in LIST_NEG:
            if relation == 'adjunct' and index_word < index_head:
                element[7] = 'neg'
    return tree_dependency


def fix_PU(tree_dependency):
    for _, element in enumerate(tree_dependency):
        relation = element[7]
        pos_Tag = element[3]
        if pos_Tag == 'PU' or pos_Tag == 'LBRK' or pos_Tag == 'RBRK':
            if relation != 'punct':
                element[7] = 'punct'
    return tree_dependency


def fix_tree(tree_dependency):
    edit_pass = edit_VCOMP_or_CCOMP(tree_dependency)
    edit_subj = get_subjpass(edit_pass)
    edit_neg = edit_NEG(edit_pass)
    new_tree = fix_PU(edit_neg)
    return new_tree
