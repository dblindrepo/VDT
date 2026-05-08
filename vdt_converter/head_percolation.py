import re

from preprocessing import get_subtree, get_all_index_in_tree, get_all_subtree_address


def is_head(rule, label):
    return re.search(rule, label)


def has_SPL_and_S(unique):
    has_S = False
    has_SPL = False
    for element in unique:
        if re.search('^S(-|$)', element):
            has_S = True
        elif re.search('^SPL(-|$)', element):
            has_SPL = True
    if has_S and has_SPL:
        return True
    else:
        return False


def has_same_phrase_type(C_label_list):
    phrase_type_set = set()
    for C_label in C_label_list:
        phrase_type = C_label.split('-')[0]
        phrase_type_set.add(phrase_type)
        if len(phrase_type_set) == 2:
            return False
    return True


def deepen_head_list(mother_tree, tree_address, head_index_list):
    deep_address_list = []
    deep_label_list = []
    first_index = head_index_list[0][0]
    last_index = head_index_list[-1][0]
    for index in range(first_index, last_index + 1):
        if tree_address != 'root':
            subtree_address = tree_address + [index]
        else:
            subtree_address = [index]
        deep_address_list.append(subtree_address)
        deep_label_list.append(get_subtree(subtree_address, mother_tree).label())
    return deep_address_list, deep_label_list


def get_conjunction(P_address, C_address_list, C_label_list):
    P_of_C_dic = {}
    previous_C_address = str(C_address_list[0])
    for C_address, C_label in zip(C_address_list[1:], C_label_list[1:]):
        if C_label == 'PU':
            P_of_C_dic[str(C_address)] = (previous_C_address, 'punct')
        elif re.search('^(Cp|CONJP)', C_label):
            P_of_C_dic[str(C_address)] = (previous_C_address, 'cc')
        else:
            P_of_C_dic[str(C_address)] = (previous_C_address, 'conj')
        if (C_label != 'PU') and (C_label != 'Cp') and ('CONJP' not in C_label):
            previous_C_address = str(C_address)
    return P_of_C_dic


def is_conjunction(C_label_list):
    unique = set(C_label_list)
    if len(unique) == 3:
        if ('PU' in unique) and ((('Cp' in unique) or ('CONJP' in unique)) and (('Cp' != C_label_list[0]) or ('CONJP' != C_label_list[0]))):
            return True
        elif (('PU' in unique) or ('Cp' in unique) or ('CONJP' in unique)) and has_SPL_and_S(unique):
            return True
    elif len(unique) == 2:
        if ('PU' in unique) or ((('Cp' in unique) or ('CONJP' in unique)) and (('Cp' != C_label_list[0]) or ('CONJP' != C_label_list[0]))):
            return True
        elif has_SPL_and_S(unique):
            return True
    elif len(unique) == 1:
        return True
    return False


# --- Head-percolation rules ---

HEAD_PERCOLATION_RULES = {
    "S": ['^VP', '-PRD', '^(S|SQ|SPL)', '^ADJP', '^NP', '^PP'],
    "SQ": ['^(VP|QVP)', '-PRD', '^(S|SQ)', '^ADJP', '^NP'],
    "SPL": ['^VP', '^SPL', '^ADJP', '^NP', '^PP'],
    "SBAR": ['^(S|SQ|SPL)', '^SBAR'],
    "NP": ['-H', '^Nn_', '^NP', '^QP', '^VP', '^ADJP', '^(S|SBAR)', '^PP'],
    "VP": ['-H', '^Vv_', '^VP', '^ADJP', '^NP', '^(S|SBAR)', '^PP', '^RP'],
    "ADJP": ['-H', '^Aa_', '^ADJP', '^NP', '^(S|SBAR)', '^PP', '^RP'],
    "RP": ['-H', '^RP'],
    "QP": ['-H', '^QP', '^RP'],
    "PP": ['-H', '^PP', '^VP', '^(S|SBAR)', '^NP', '^ADJP'],
    "QNP": ['-H', '^QNP', '^NP', '^VP', '^ADJP'],
    "QADJP": ['-H', '^QADJP', '^ADJP', '^NP'],
    "QRP": ['-H', '^QRP', '^RP', '^NP'],
    "QPP": ['-H', '^QPP', '^PP', '^NP'],
    "UCP": ['-H'],
    "CONJP": ['-H']
}


def finding_head_of_tree(tree):
    phrase_type = tree.label().split('-')[0]
    head_index_result = []
    head_label_result = []

    if phrase_type not in HEAD_PERCOLATION_RULES:
        for index, element in enumerate(tree):
            label_of_element = element.label()
            if is_head("-H$", label_of_element):
                head_index_result.append([index])
                head_label_result.append(label_of_element)
        if head_index_result:
            return head_index_result, head_label_result
        else:
            return [[0]], [tree[0].label()]

    if phrase_type == 'RP':
        for rule in HEAD_PERCOLATION_RULES['RP']:
            if not head_index_result:
                for index, element in zip(range(len(tree) - 1, -1, -1), reversed(tree)):
                    label_of_element = element.label()
                    if is_head(rule, label_of_element):
                        head_index_result.append([index])
                        head_label_result.append(label_of_element)
            else:
                break
        if head_index_result:
            return head_index_result[::-1], head_label_result[::-1]
        else:
            return [[0]], [tree[0].label()]

    else:
        for rule in HEAD_PERCOLATION_RULES[phrase_type]:
            if not head_index_result:
                for index, element in enumerate(tree):
                    label_of_element = element.label()
                    if is_head(rule, label_of_element):
                        head_index_result.append([index])
                        head_label_result.append(label_of_element)
            else:
                break
        if head_index_result:
            return head_index_result, head_label_result
        else:
            return [[0]], [tree[0].label()]


HEAD_EXCEPTION_RULES = {
    "NP": [r"^(Nn_swsp|Nn_w)(-|$)", r"^(Nn|Nu|Nun|Nt)(-|$)", r"^(Num|Nq|Nr)(-|$)", r"^(Pd|Pp)"],
    "ADJP": [r"^(Aa)"],
    "QP": [r"^Nq(-|$)", r"^Num(-|$)"],
    "Nn_swsp": [r"^(Ncs|Nc)(-|$)"],
    "VP": [r"^(Ve|Vc|D|Vcp|Vv)(-|$)"],
    "S": [r"^(S|SQ|SPL)($)", r"^(ADJP)"],
    "SBAR": [r"^(S|SQ|SPL)($)"],
    "PP": [r"^(Cs)"],
    "CONJP": [r"^(Aa)", r"^(Nn)"],
    "MDP": [r"-H$", r"^MDP(-|_|$)", r"^Cs(-|_|$)", r"^(An|Aa)(-|_|$)", r"^(Pd|Pp)(-|_|$)", r"^R(-|_|$)", r"^X(-|_|$)"]
}


def identify_head(tree, P_address, C_address_list, C_label_list, head_C_address_list, head_C_label_list):
    if is_conjunction(C_label_list):
        P_of_C_dic = get_conjunction(P_address, C_address_list, C_label_list)
        return [C_address_list[0], P_of_C_dic]

    if has_same_phrase_type(head_C_label_list):
        if (('Cp' in C_label_list) or ('CONJP' in C_label_list)) and (C_label_list[0] != 'Cp') and (C_label_list[0] != 'CONJP'):
            P_of_C_dic = get_conjunction(P_address, C_address_list, C_label_list)
            return [C_address_list[0], P_of_C_dic]
        else:
            first_element = head_C_address_list[0]
            if first_element[-1] >= 1:
                pre_address_of_head_C_address_list = first_element[:-1] + [first_element[-1] - 1]
                pre_subtree = get_subtree(pre_address_of_head_C_address_list, tree)
                pre_subtree_label = pre_subtree.label()
                if re.search('^(Cp|CONJP)', pre_subtree_label):
                    P_of_C_dic = get_conjunction(P_address, C_address_list, C_label_list)
                    return [C_address_list[0], P_of_C_dic]

        for head_C_address, head_C_label in zip(head_C_address_list, head_C_label_list):
            if '-' not in head_C_label:
                return [head_C_address]

        for head_C_address, head_C_label in zip(head_C_address_list, head_C_label_list):
            if '-SBJ' not in head_C_label:
                return [head_C_address]

    else:
        if ('Cp' in C_label_list) and (C_label_list[0] != 'Cp'):
            P_of_C_dic = get_conjunction(P_address, C_address_list, C_label_list)
            return [C_address_list[0], P_of_C_dic]
        else:
            P_phrase_type = get_subtree(P_address, tree).label().split('-')[0]
            for rule in HEAD_EXCEPTION_RULES[P_phrase_type]:
                for head_C_address, head_C_label in zip(head_C_address_list, head_C_label_list):
                    if is_head(rule, head_C_label):
                        return [head_C_address]
    return "Nope"


def from_phrase_to_headword(mother_tree, tree, tree_address):
    phrase_to_headword = [tree_address]
    if tree_address != 'root':
        tree = get_subtree(tree_address, mother_tree)
    P_of_C_dic = {}
    while type(tree[0]) != str:
        head_index_list, head_label_list = finding_head_of_tree(tree)
        if len(head_index_list) == 1:
            if tree_address != 'root':
                tree_address = tree_address + head_index_list[0]
            else:
                tree_address = head_index_list[0]
            tree = get_subtree(tree_address, mother_tree)
            phrase_to_headword.append(tree_address)

        else:
            address_list, label_list = deepen_head_list(mother_tree, tree_address, head_index_list)
            head_address_list = []
            for head_index in head_index_list:
                if tree_address != 'root':
                    head_address_list.append(tree_address + head_index)
                else:
                    head_address_list.append(head_index)
            result = identify_head(mother_tree, tree_address, address_list, label_list, head_address_list, head_label_list)
            tree_address = result[0]
            tree = get_subtree(tree_address, mother_tree)
            phrase_to_headword.append(tree_address)
            if len(result) == 2:
                P_of_C_dic.update(result[1])
    phrase_to_headword.append(tree[0])
    return [phrase_to_headword, P_of_C_dic]


def assign_headword_for_phrase(tree):
    P_of_C_dic = {}
    headword_of_phrase = {}
    phrase_address_list = ['root'] + get_all_subtree_address(tree)

    for phrase_address in phrase_address_list:
        if str(phrase_address) not in headword_of_phrase:
            if phrase_address != 'root':
                subtree = get_subtree(phrase_address, tree)
            else:
                subtree = tree
            if type(subtree[0]) != str:
                result = from_phrase_to_headword(tree, subtree, phrase_address)
                phrase_to_headword = result[0][:-1]
                headword = result[0][-1]
                P_of_C_dic.update(result[1])
                for head_phrase_address in phrase_to_headword:
                    headword_of_phrase[str(head_phrase_address)] = headword
            else:
                headword_of_phrase[str(phrase_address)] = subtree[0]

    for phrase_address in get_all_subtree_address(tree):
        subtree = get_subtree(phrase_address, tree)
        label = subtree.label().split('-')[0]
        if label == 'UCP':
            C_address_list = []
            C_label_list = []
            for index_subtree in range(len(subtree)):
                subtree_address = phrase_address + [index_subtree]
                subtree_label = get_subtree(subtree_address, tree).label()
                C_address_list.append(subtree_address)
                C_label_list.append(subtree_label)
            P_of_C_dic.update(get_conjunction(phrase_address, C_address_list, C_label_list))
    return [headword_of_phrase, P_of_C_dic]
