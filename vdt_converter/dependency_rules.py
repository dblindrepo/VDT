import re

from preprocessing import str_to_list, get_subtree, get_POS_of_word
from head_percolation import assign_headword_for_phrase


# --- Utility: C and P extraction ---

def get_C_of_headword(headword_of_phrase):
    duplicate_headword_of_phrase = {}
    duplicate_headword_of_phrase.update(headword_of_phrase)
    del duplicate_headword_of_phrase['root']
    merge = {}
    for key, value in sorted(duplicate_headword_of_phrase.items()):
        merge.setdefault(value, []).append(key)
    C = {}
    for headword in merge:
        C[headword] = min(merge[headword], key=len)
    return C


def get_P_of_C(phrase_address, root_address):
    path = str_to_list(phrase_address)[:-1]
    return root_address if not path else str(path)


# --- Processing tags ---

def has_subject(tree):
    if 'SBAR' in tree.label():
        for subtree in tree:
            if re.search('^(S|SQ)(-|$)', subtree.label()):
                for sub_subtree in subtree:
                    if re.search('^(S|SQ)(-|$)', sub_subtree.label()):
                        if '-SBJ' in sub_subtree.label():
                            return True
                        return has_subject(sub_subtree)
                    elif re.search('^(NP|VP|ADJP)(-SBJ|-SBJ-)', sub_subtree.label()) and ('NONE' not in sub_subtree[0].label()):
                        return True
                return False
        return False
    elif re.search('^(S|SQ)(-|$)', tree.label()):
        for subtree in tree:
            if re.search('^(S)(-SBJ)', subtree.label()):
                return True
            if re.search('^(NP|VP|ADJP)(-SBJ|-SBJ-)', subtree.label()) and ('NONE' not in subtree[0].label()):
                return True
        return False
    return False


def has_POS(tree, POS):
    if 'SBAR' in tree.label():
        for subtree in tree:
            if re.search('^(S|SPL|SQ)(-|$)', subtree.label()):
                for sub_subtree in subtree:
                    label_sub_subtree = sub_subtree.label()
                    if re.search('^(S|SPL|SQ)(-|$)', label_sub_subtree):
                        return has_POS(sub_subtree, POS)
                    if re.search('^{}(-|$)'.format(POS), label_sub_subtree):
                        return True
                return False
        return False
    elif re.search('^(S|SPL|SQ)(-|$)', tree.label()):
        for subtree in tree:
            label_subtree = subtree.label()
            if re.search('^{}(-|$)'.format(POS), label_subtree):
                return True
        return False
    return False


def get_function_tag(tree):
    headword_of_phrase = assign_headword_for_phrase(tree)[0]
    C_of_headword = get_C_of_headword(headword_of_phrase)
    function_tags_of_word = {}
    for word in tree.leaves():
        C_label = get_subtree(C_of_headword[word], tree).label()
        function_tags = C_label.split('-')
        temp = []
        for function_tag in function_tags:
            if function_tag in ['PRD', 'CMP', 'LGS', 'CMP', 'MDP', 'TMP', 'LOC', 'MNR', 'PRP', 'ADV', 'CND', 'CNC', 'CMD']:
                temp.append(function_tag)
        if temp:
            temp = '-'.join(temp)
            function_tags_of_word[word] = temp
        else:
            function_tags_of_word[word] = '_'
    return function_tags_of_word


# --- SBJ labels ---

def has_SBJ(C):
    if ('NP-SBJ' in C) or ('QNP-SBJ' in C):
        return 'nsubj'
    elif 'ADJP-SBJ' in C:
        return 'asubj'
    elif 'VP-SBJ' in C:
        return 'vsubj'
    elif ('S-SBJ' in C) or ('SPL-SBJ' in C) or ('SBAR-SBJ' in C) or ('SQ-SBJ' in C):
        return 'csubj'
    elif 'PP-SBJ' in C:
        return 'psubj'
    else:
        return False


# --- OBJ labels ---

def is_DOBJ(P, C):
    if re.search('^(VP|Vv)', P):
        if re.search('^(NP|QNP|QP)(-DOB)', C):
            return 'np_dobj'
    elif '-DOB' in C:
        return 'np_dobj'
    else:
        return False


def is_IOBJ(P, C):
    if re.search('^(VP|Vv)', P):
        if re.search('^(NP|QNP)(-IOB)', C):
            return 'np_iobj'
    else:
        return False


def is_PIOBJ(C):
    if re.search('^(PP)(-IOB)', C):
        return 'pp_iobj'


# --- CMP labels ---

def complement_of_Vc(p, C):
    if re.search('^(Vc)(-|$)', p):
        if re.search('^(NP|QNP)(-CMP|$)', C):
            return 'np_sc'
        elif re.search('^(ADJP)(-CMP|$)', C):
            return 'adjp_sc'
        elif re.search('^(PP)(-CMP|$)', C):
            return 'pp_sc'
        elif re.search('^(VP)(-CMP|$)', C):
            return 'vp_sc'
        elif re.search('^(S|SPL|SQ)(-CMP)', C):
            return 'c_sc'
    else:
        return False


def complement_of_verb(P, p, C):
    if re.search('^(VP)', P):
        if re.search('^(Vc)(-|$)', p):
            complement_of_Vc(p, C)
        else:
            if re.search('^(ADJP)(-CMP)', C):
                return 'acomp'
            elif re.search('^(PP|QPP)(-CMP)', C):
                return 'pcomp'
            elif re.search('^(VP)(-CMP)', C):
                return 'vcomp'
            elif re.search('^(NP|QNP)(-CMP)', C):
                return 'ncomp'
    else:
        return False


def is_CCOMP_or_XCOMP(P, p, C, C_tree):
    if re.search('^(VP|QVP|ADJP)', P):
        if re.search('^(Vc)(-|$)', p):
            complement_of_Vc(p, C)
        else:
            if re.search('^SQ', C):
                if has_subject(C_tree):
                    return 'ccomp'
                else:
                    if has_POS(C_tree, 'VP'):
                        return 'xcomp:vp'
                    elif has_POS(C_tree, 'ADJP'):
                        return 'xcomp:adjp'
                    elif has_POS(C_tree, 'NP') or has_POS(C_tree, 'QNP'):
                        return 'xcomp:np'
                    elif has_POS(C_tree, 'PP'):
                        return 'xcomp:pp'
            elif re.search('^(S)(-[0-9]|-CMP|$)', C):
                print("C_label", C)
                if has_subject(C_tree):
                    return 'ccomp'
                else:
                    if has_POS(C_tree, 'VP'):
                        return 'xcomp:vp'
                    elif has_POS(C_tree, 'ADJP'):
                        return 'xcomp:adjp'
                    elif has_POS(C_tree, 'NP') or has_POS(C_tree, 'QNP'):
                        return 'xcomp:np'
                    elif has_POS(C_tree, 'PP'):
                        return 'xcomp:pp'
            elif re.search('^(SBAR)(-[0-9]|-CMP|$)', C):
                if has_subject(C_tree):
                    return 'ccomp'
                else:
                    if has_POS(C_tree, 'VP'):
                        return 'xcomp:vp'
                    elif has_POS(C_tree, 'ADJP'):
                        return 'xcomp:adjp'
                    elif has_POS(C_tree, 'NP') or has_POS(C_tree, 'QNP'):
                        return 'xcomp:np'
                    elif has_POS(C_tree, 'PP'):
                        return 'xcomp:pp'
            else:
                is_ADVCL(C, C_tree)
    else:
        return False


def complement_of_PREP(P, C):
    if re.search('^(PP|QPP)', P):
        if re.search('^(NP|QNP|VP|ADJP|S|SPL)', C):
            return 'pp_comp'
    else:
        return False


# --- MOD labels ---

def is_AMOD(P, p, C):
    if re.search('^(ADJP|NP|QNP|SPL)', P):
        if re.search('^(ADJP|Aa|An|VA|NA)', C):
            return 'amod'
    elif re.search('^(VP)', P):
        if re.search('^(Vc)(-|$)', p):
            complement_of_Vc(p, C)
        else:
            if re.search('^(ADJP|Aa|VA|NA)(-ADV|-MNR|-TPC|-[0-9]|$)', C):
                return 'amod'
    elif re.search('^(ADJP)(-MNR|-PRP|-ADV)', C):
        return 'amod'
    else:
        return False


def is_NMOD(P, p, C):
    if re.search('^(NP|QNP|Nn)', P):
        if re.search('^(NP|Nr|Nt|Nu|Nun|Nn|ID)', C):
            return 'nmod'
    elif re.search('^(ADJP)', P):
        if re.search('^(NP)(-CMP)', C):
            return 'ncomp'
        elif re.search('^(NP|QNP|Nn|Pp|QP)', C):
            return 'nmod'
    elif re.search('^(VP)', P):
        if re.search('^(Vc)(-|$)', p):
            complement_of_Vc(p, C)
        else:
            if re.search('^(NP|Nn|QNP|QP|Pd|Nq)(-[0-9]|$)', C):
                return 'nmod'
    else:
        return False


def is_VMOD_or_DIR(P, p, C, C_tree, c):
    if re.search('^(ADJP|S)', P):
        if re.search('^(VP|Ve|Vc|Vcp|Vv|VN)', C):
            return 'vmod'
    elif re.search('^(NP|QNP)', P):
        if re.search('^(VP|Ve|Vc|Vcp|Vv|VN)', C):
            return 'vmod'
    elif re.search('^(VP|Vv)', P):
        if re.search('^(Vc)(-|$)', p):
            complement_of_Vc(p, C)
        elif re.search('^(Ve|Vc|Vcp|Vv|VN)', C):
            return 'vmod'
        elif re.search('^VP($|[0-9])', C):
            if re.search('^D', c):
                return 'dir'
            else:
                return 'vmod'
        elif re.search('^D', C):
            return 'dir'
    else:
        return False


def is_PMOD(C):
    if re.search('^(PP|QPP)', C):
        return 'pmod'
    else:
        return False


def is_RCMOD(P, C, C_tree):
    if re.search('^(NP|QNP)', P):
        if re.search('^(S|SBAR|SQ)($|[0-9])', C):
            return 'rcmod'
    else:
        is_ADVCL(C, C_tree)


def is_NP_LMOD(C):
    if re.search('^(NP)(-LOC)', C):
        return 'np_lmod'
    else:
        return False


def is_NP_TMOD(C):
    if re.search('^(NP)(-TMP)', C):
        return 'np_tmod'
    else:
        return False


def is_ADJP_LMOD(C):
    if re.search('^(ADJP)(-LOC)', C):
        return 'adjp_lmod'
    else:
        return False


def is_ADJP_TMOD(C):
    if re.search('^(ADJP)(-TMP)', C):
        return 'adjp_tmod'
    else:
        return False


def is_PP_LMOD(C):
    if re.search('^(PP|QPP)(-LOC)', C):
        return 'pp_lmod'
    else:
        return False


def is_PP_TMOD(C):
    if re.search('^(PP|QPP)(-TMP)', C):
        return 'pp_tmod'
    else:
        return False


def is_VP_TMOD(C):
    if re.search('^(VP)(-TMP)', C):
        return 'vp_tmod'
    else:
        return False


def is_VP_LMOD(C):
    if re.search('^(VP)(-LOC)', C):
        return 'vp_lmod'
    else:
        return False


def is_C_TMOD(C):
    if re.search('^(S)(-TMP)', C):
        return 'c_tmod'
    else:
        return False


def is_NP_ADVMOD(C):
    if re.search('^(NP|QP|QNP)(-MNR|-ADV|-PRP|-CND|-CNC|-TPC)', C):
        return 'np_advmod'
    else:
        return False


def is_PP_ADVMOD(C):
    if re.search('^(PP)(-MNR|-ADV|-PRP|-CND|-TPC)', C):
        return 'pp_advmod'
    else:
        return False


def is_VP_ADVMOD(C):
    if re.search('^(VP)(-MNR|-ADV|-PRP|-CND|-TPC)', C):
        return 'vp_advmod'
    else:
        return False


def is_ADVCL(C, C_tree):
    if re.search('^(S)($)', C):
        if has_POS(C_tree, 'VP-MNR') or has_POS(C_tree, 'VP-ADV') or has_POS(C_tree, 'ADJP-PRD-MNR'):
            return 'advcl'
    elif re.search('^(S|SBAR)(-CND|-PRP|-ADV|-MNR|-CNC|-TPC)', C):
        return 'advcl'
    elif re.search('^(SPL)(-PRP|-CNC|-MNR|-ADV|-CND|-TPC)', C):
        return 'advcl'
    else:
        return False


def is_QUANTIFIER_or_NUM(P, C):
    if re.search('^(NP|QNP|Nn|Nu)', P):
        if re.search('^(Num|QP)', C):
            return 'num'
        elif re.search('^(Nw|Nq)', C):
            return 'quantifier'
    else:
        return False


def is_NUMBER_or_QUANTMOD(P, C):
    if re.search('^(QP)', P):
        if re.search('^(Num)', C):
            return 'number'
        elif re.search('^(Nq)', C):
            return 'quantifier'
        else:
            return 'quantmod'
    else:
        return False


def is_CLF_or_NMOD(P, p):
    if re.search('^(Nn_swsp)', P):
        if re.search('^(Ncs)', p):
            return 'ncs'
        elif re.search('^(Nc)', p):
            return 'nc'
        else:
            return 'nmod'
    else:
        return False


def is_TIMOD(P, C):
    if ('NP' in P) and ('HLN' in C or 'TTL' in C):
        return 'timod'
    else:
        return False


def is_DET(P, C):
    if re.search('^(NP|QNP)', P) and re.search('^(Pd|Pp|QNP)', C):
        return 'det'
    else:
        return False


# --- Other labels ---

def is_PARATAXIS(C):
    if '-PRN' in C:
        return 'parataxis'
    else:
        return False


def is_PUNCT(C):
    if re.search('^(PU|LBRK|RBRK)', C):
        return 'punct'
    else:
        return False


def is_SINO(P):
    if '_w' in P:
        return 'sino'
    else:
        return False


def is_INTJ(C):
    if (re.search('^(E|M)', C)) or ('-MDP' in C) or ('-CMD' in C):
        return 'intj'
    else:
        return False


def is_ADJUNCT(C):
    if re.search('^(R|RP|QRP)(-|$)', C):
        return 'adjunct'
    else:
        return False


def is_VOCATIVE(C):
    if '-VOC' in C:
        return 'vocative'
    else:
        return False


def is_SOUND(c):
    if re.search('^ON', c):
        return 'sound'
    else:
        return False


def is_CC(C):
    if re.search('^(Cp|CONJP)', C):
        return 'cc'
    else:
        return False


def is_MARK(C):
    if 'Cs' in C:
        return 'mark'
    else:
        return False


# --- Main dependency relation function ---

def get_dependency_relation(P_address, C_address, P_index, C_index, tree):
    C_tree = get_subtree(C_address, tree)
    C = C_tree.label()
    P = get_subtree(P_address, tree).label()
    POS_of_word = get_POS_of_word(tree)
    p = POS_of_word[P_index]
    c = POS_of_word[C_index]

    # If C is UCP, relation is decided by the leftmost POS in the UCP tree
    if 'UCP' in C:
        C = C_tree[0].label()

    if has_SBJ(C):
        return has_SBJ(C)
    if is_ADJUNCT(C):
        return is_ADJUNCT(C)
    if is_ADVCL(C, C_tree):
        return is_ADVCL(C, C_tree)
    if is_VP_ADVMOD(C):
        return is_VP_ADVMOD(C)
    if is_NP_ADVMOD(C):
        return is_NP_ADVMOD(C)
    if is_PP_ADVMOD(C):
        return is_PP_ADVMOD(C)
    if is_PARATAXIS(C):
        return is_PARATAXIS(C)
    if is_VOCATIVE(C):
        return is_VOCATIVE(C)
    if is_TIMOD(P, C):
        return is_TIMOD(P, C)
    if is_INTJ(C):
        return is_INTJ(C)
    if is_SINO(P):
        return is_SINO(P)
    if is_SOUND(c):
        return is_SOUND(c)
    if is_VP_LMOD(C):
        return is_VP_LMOD(C)
    if is_VP_TMOD(C):
        return is_VP_TMOD(C)
    if is_ADJP_LMOD(C):
        return is_ADJP_LMOD(C)
    if is_ADJP_TMOD(C):
        return is_ADJP_TMOD(C)
    if is_NP_LMOD(C):
        return is_NP_LMOD(C)
    if is_NP_TMOD(C):
        return is_NP_TMOD(C)
    if is_PP_LMOD(C):
        return is_PP_LMOD(C)
    if is_PP_TMOD(C):
        return is_PP_TMOD(C)
    if is_C_TMOD(C):
        return is_C_TMOD(C)
    if is_PIOBJ(C):
        return is_PIOBJ(C)
    if is_IOBJ(P, C):
        return is_IOBJ(P, C)
    if is_DOBJ(P, C):
        return is_DOBJ(P, C)
    if complement_of_Vc(p, C):
        return complement_of_Vc(p, C)
    if is_CCOMP_or_XCOMP(P, p, C, C_tree):
        return is_CCOMP_or_XCOMP(P, p, C, C_tree)
    if complement_of_verb(P, p, C):
        return complement_of_verb(P, p, C)
    if complement_of_PREP(P, C):
        return complement_of_PREP(P, C)
    if is_VMOD_or_DIR(P, p, C, C_tree, c):
        return is_VMOD_or_DIR(P, p, C, C_tree, c)
    if is_RCMOD(P, C, C_tree):
        return is_RCMOD(P, C, C_tree)
    if is_QUANTIFIER_or_NUM(P, C):
        return is_QUANTIFIER_or_NUM(P, C)
    if is_CLF_or_NMOD(P, p):
        return is_CLF_or_NMOD(P, p)
    if is_NMOD(P, p, C):
        return is_NMOD(P, p, C)
    if is_NUMBER_or_QUANTMOD(P, C):
        return is_NUMBER_or_QUANTMOD(P, C)
    if is_DET(P, C):
        return is_DET(P, C)
    if is_AMOD(P, p, C):
        return is_AMOD(P, p, C)
    if is_PMOD(C):
        return is_PMOD(C)
    if is_CC(C):
        return is_CC(C)
    if is_MARK(C):
        return is_MARK(C)
    if is_PUNCT(C):
        return is_PUNCT(C)

    return 'dep'
