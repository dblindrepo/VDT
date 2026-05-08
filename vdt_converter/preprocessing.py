import re
from nltk.tree import Tree


def str_to_list(s):
    result = []
    num = ''
    for i in s:
        if i != '[' and i != ']':
            if i != ',':
                if i.isnumeric():
                    num += i
            else:
                result.append(int(num))
                num = ''
    result.append(int(num))
    return result


def get_all_index_in_tree(tree):
    result = []
    for index, subtree in enumerate(tree):
        if type(subtree) != str:
            result.append([index])
    return result


def get_subtree(subtree_address, tree):
    if type(subtree_address) == str:
        if subtree_address == 'root':
            return tree
        else:
            subtree_address = str_to_list(subtree_address)
    for index in subtree_address:
        tree = tree[index]
    return tree


def get_all_subtree_address(tree):
    queue = get_all_index_in_tree(tree)
    explored = []
    while queue:
        node = queue.pop(0)
        if node not in explored:
            explored.append(node)
            subtree = get_subtree(node, tree)
            index_subtree_list = get_all_index_in_tree(subtree)
            for index_subtree in index_subtree_list:
                queue.append(node + index_subtree)
    return explored


def get_POS_of_word(tree):
    result = {}
    for leafPos in tree.treepositions('leaves'):
        word = tree[leafPos]
        POS = tree[leafPos[:-1]].label()
        result[word] = POS
    return result


def get_all_POS(tree):
    result = []
    for leafPos in tree.treepositions('leaves'):
        i = -1
        POS = tree[leafPos[:i]].label().split('-')[0]
        while POS == 'NONE':
            i = i - 1
            POS = tree[leafPos[:i]].label().split('-')[0]
        result.append(POS)
    return result


def from_word_to_number(tree):
    for index, leafPos in enumerate(tree.treepositions('leaves')):
        tree[leafPos] = str(index + 1)
    return tree
