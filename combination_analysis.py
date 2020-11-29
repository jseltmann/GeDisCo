import json
import os
from tqdm import tqdm


def unify_rels_orig(rel1, rel2):
    """
    Determine, if two relations are the same.
    If they are, return a new, combined relations.
    Otherwise, return None.

    Parameters
    ----------
    rel1 : dict()
        First relation.
    rel2 : dict()
        Second relation.

    Returns
    -------
    new_rel : dict()
        Combined relation.
    """

    if rel1["Sense"] != rel2["Sense"]:
        return False

    rel1_arg1 = rel1["Arg1"]["TokenList"]
    rel1_arg2 = rel1["Arg2"]["TokenList"]
    rel2_arg1 = rel2["Arg1"]["TokenList"]
    rel2_arg2 = rel2["Arg2"]["TokenList"]

    arg1_common = [ind for ind in rel1_arg1 if ind in rel2_arg1]
    if len(arg1_common) < len(rel1_arg1) / 2 or len(arg1_common) < len(rel2_arg1) / 2:
        return False

    arg2_common = [ind for ind in rel1_arg2 if ind in rel2_arg2]
    if len(arg2_common) < len(rel1_arg2) / 2 or len(arg2_common) < len(rel2_arg2) / 2:
        return False

    return True


def unify_rels_30(rel1, rel2):
    """
    Determine, if two relations are the same.
    If they are, return a new, combined relations.
    Otherwise, return None.

    Parameters
    ----------
    rel1 : dict()
        First relation.
    rel2 : dict()
        Second relation.

    Returns
    -------
    new_rel : dict()
        Combined relation.
    """

    if rel1["Sense"] != rel2["Sense"]:
        return False

    rel1_arg1 = rel1["Arg1"]["TokenList"]
    rel1_arg2 = rel1["Arg2"]["TokenList"]
    rel2_arg1 = rel2["Arg1"]["TokenList"]
    rel2_arg2 = rel2["Arg2"]["TokenList"]

    arg1_common = [ind for ind in rel1_arg1 if ind in rel2_arg1]
    if len(arg1_common) < len(rel1_arg1) * 0.3 or len(arg1_common) < len(rel2_arg1) * 0.3:
        return False

    arg2_common = [ind for ind in rel1_arg2 if ind in rel2_arg2]
    if len(arg2_common) < len(rel1_arg2) * 0.3 or len(arg2_common) < len(rel2_arg2) * 0.3:
        return False

    return True


def unify_rels_20(rel1, rel2):
    """
    Determine, if two relations are the same.
    If they are, return a new, combined relations.
    Otherwise, return None.

    Parameters
    ----------
    rel1 : dict()
        First relation.
    rel2 : dict()
        Second relation.

    Returns
    -------
    new_rel : dict()
        Combined relation.
    """

    if rel1["Sense"] != rel2["Sense"]:
        return False

    rel1_arg1 = rel1["Arg1"]["TokenList"]
    rel1_arg2 = rel1["Arg2"]["TokenList"]
    rel2_arg1 = rel2["Arg1"]["TokenList"]
    rel2_arg2 = rel2["Arg2"]["TokenList"]

    arg1_common = [ind for ind in rel1_arg1 if ind in rel2_arg1]
    if len(arg1_common) < len(rel1_arg1) * 0.2 or len(arg1_common) < len(rel2_arg1) * 0.2:
        return False

    arg2_common = [ind for ind in rel1_arg2 if ind in rel2_arg2]
    if len(arg2_common) < len(rel1_arg2) * 0.2 or len(arg2_common) < len(rel2_arg2) * 0.2:
        return False

    return True


def unify_rels_10(rel1, rel2):
    """
    Determine, if two relations are the same.
    If they are, return a new, combined relations.
    Otherwise, return None.

    Parameters
    ----------
    rel1 : dict()
        First relation.
    rel2 : dict()
        Second relation.

    Returns
    -------
    new_rel : dict()
        Combined relation.
    """

    if rel1["Sense"] != rel2["Sense"]:
        return False

    rel1_arg1 = rel1["Arg1"]["TokenList"]
    rel1_arg2 = rel1["Arg2"]["TokenList"]
    rel2_arg1 = rel2["Arg1"]["TokenList"]
    rel2_arg2 = rel2["Arg2"]["TokenList"]

    arg1_common = [ind for ind in rel1_arg1 if ind in rel2_arg1]
    if len(arg1_common) < len(rel1_arg1) * 0.1 or len(arg1_common) < len(rel2_arg1) * 0.1:
        return False

    arg2_common = [ind for ind in rel1_arg2 if ind in rel2_arg2]
    if len(arg2_common) < len(rel1_arg2) * 0.1 or len(arg2_common) < len(rel2_arg2) * 0.1:
        return False

    return True


def one_in_common_per_arg(rel1, rel2):
    rel1_arg1 = rel1["Arg1"]["TokenList"]
    rel1_arg2 = rel1["Arg2"]["TokenList"]
    rel2_arg1 = rel2["Arg1"]["TokenList"]
    rel2_arg2 = rel2["Arg2"]["TokenList"]

    comb1 = [t for t in rel1_arg1 if t in rel2_arg1]
    comb2 = [t for t in rel1_arg2 if t in rel2_arg2]

    if len(comb1) > 0 and len(comb2) > 0:
        return True
    return False


def one_in_common_sense(rel1, rel2):
    if rel1["Sense"] != rel2["Sense"]:
        return False
    rel1_arg1 = rel1["Arg1"]["TokenList"]
    rel1_arg2 = rel1["Arg2"]["TokenList"]
    rel2_arg1 = rel2["Arg1"]["TokenList"]
    rel2_arg2 = rel2["Arg2"]["TokenList"]

    comb1 = [t for t in rel1_arg1 if t in rel2_arg1]
    comb2 = [t for t in rel1_arg2 if t in rel2_arg2]

    if len(comb1) > 0 and len(comb2) > 0:
        return True
    return False


def one_in_common_sense_l2(rel1, rel2):
    s1 = rel1["Sense"][0].split(".")
    s2 = rel2["Sense"][0].split(".")
    if s1[:1] != s2[:1]:
        return False
    rel1_arg1 = rel1["Arg1"]["TokenList"]
    rel1_arg2 = rel1["Arg2"]["TokenList"]
    rel2_arg1 = rel2["Arg1"]["TokenList"]
    rel2_arg2 = rel2["Arg2"]["TokenList"]

    comb1 = [t for t in rel1_arg1 if t in rel2_arg1]
    comb2 = [t for t in rel1_arg2 if t in rel2_arg2]

    if len(comb1) > 0 and len(comb2) > 0:
        return True
    return False


def one_in_common_sense_l1(rel1, rel2):
    s1 = rel1["Sense"][0].split(".")
    s2 = rel2["Sense"][0].split(".")
    if s1[0] != s2[0]:
        return False
    rel1_arg1 = rel1["Arg1"]["TokenList"]
    rel1_arg2 = rel1["Arg2"]["TokenList"]
    rel2_arg1 = rel2["Arg1"]["TokenList"]
    rel2_arg2 = rel2["Arg2"]["TokenList"]

    comb1 = [t for t in rel1_arg1 if t in rel2_arg1]
    comb2 = [t for t in rel1_arg2 if t in rel2_arg2]

    if len(comb1) > 0 and len(comb2) > 0:
        return True
    return False


def unify_files(l1_path, l2_path, same_fn):
    """
    For one speech, unify the relations found from two languages.
    Two relations are considered the same, if they have the same sense
    and their arguments have a 50% overlap.

    Parameters
    ----------
    l1_path : str
        Path to relations file for first language.
        These are the files, where the word indices have been replaced
        with word indices in German texts.
    l2_path : str
        Path to relations for second language.
    same_fn : <function>
        Function to determine if two relations are the same.
    """
    
    rels1 = []
    rels2 = []

    for line in open(l1_path):
        rel = json.loads(line)
        rels1.append(rel)
    tot1 = len(rels1)
    for line in open(l2_path):
        rel = json.loads(line)
        rels2.append(rel)
    tot2 = len(rels2)

    aligned = 0
    found1, found2 = [], []
    dupls = 0

    for i, rel1 in enumerate(rels1):
        for j, rel2 in enumerate(rels2):
            same = same_fn(rel1, rel2)
            if same:
                if rel1 in found1 or rel2 in found2:
                    dupls += 1
                    continue
                found1.append(rel1)
                found2.append(rel2)
                aligned += 1

    return tot1, tot2, aligned, dupls


def unify_langs(dir1, dir2, res_path, same_fn):
    """
    Combine relations for files in two directories.
    Instead of writing the relations to file,
    return statistics.

    Parameters
    ----------
    dir1 : str
        Path to first directory.
    dir2 : str
        Path to second directory.
    res_path : str
        Path to write the statistics to.
    same_fn : <function>
        Function determining if two relations are the same.
    """
    fns1 = set(os.listdir(dir1))
    fns2 = set(os.listdir(dir2))

    fns_both = [fn for fn in fns1 if fn in fns2]
    num_files = len(fns_both)

    tot1, tot2, tot_aligned, tot_dupl = 0, 0, 0, 0

    for fn in tqdm(fns_both):
        path1 = os.path.join(dir1, fn)
        path2 = os.path.join(dir2, fn)
        rels1, rels2, aligned, dupl = unify_files(path1, path2, same_fn)
        tot1 += rels1
        tot2 += rels2
        tot_aligned += aligned
        tot_dupl += dupl

    outs = ""
    outs += dir1 + "\n"
    outs += dir2 + "\n"
    outs += str(same_fn) + "\n\n"

    frac_al1 = tot_aligned / tot1
    frac_dup1 = tot_dupl / tot1
    outs += "total 1: " + str(tot1) + "\t" + "frac al 1: " + str(frac_al1) + "frac dup 1: " + str(frac_dup1) + "\n"
    frac_al2 = tot_aligned / tot2
    frac_dup2 = tot_dupl / tot2
    outs += "total 2: " + str(tot2) + "\t" + "frac al 2: " + str(frac_al2) + "frac dup 2: " + str(frac_dup2) + "\n"
    outs += "total aligned: " + str(tot_aligned) + "\n"
    outs += "total dupl: " + str(tot_dupl) + "\n"

    with open(res_path, "w") as res_file:
        res_file.write(outs)


