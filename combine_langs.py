import json
import os
from tqdm import tqdm


def unify_rels(rel1, rel2):
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
        return None
    #if rel1["Connective"] != rel2["Connective"]:
    #    #if the relations are implicit, 
    #    #the connectives will be emtpy lists
    #    return None

    rel1_arg1 = rel1["Arg1"]["TokenList"]
    rel1_arg2 = rel1["Arg2"]["TokenList"]
    rel2_arg1 = rel2["Arg1"]["TokenList"]
    rel2_arg2 = rel2["Arg2"]["TokenList"]

    arg1_common = [ind for ind in rel1_arg1 if ind in rel2_arg1]
    if len(arg1_common) < len(rel1_arg1) / 2 or len(arg1_common) < len(rel2_arg1) / 2:
        return None

    arg2_common = [ind for ind in rel1_arg2 if ind in rel2_arg2]
    if len(arg2_common) < len(rel1_arg2) / 2 or len(arg2_common) < len(rel2_arg2) / 2:
        return None

    arg1_comb = list(set(rel1_arg1 + rel2_arg1))
    arg2_comb = list(set(rel1_arg2 + rel2_arg2))

    if rel1["Type"] == "Explicit":
        new_rel = rel1
        connective = rel1["Connective"]["TokenList"]
    elif rel2["Type"] == "Explicit":
        new_rel = rel2
        connective = rel2["Connective"]["TokenList"]
    else:
        new_rel = rel1
        connective = []
    arg1_comb = [ind for ind in arg1_comb if not ind in connective]
    arg2_comb = [ind for ind in arg2_comb if not ind in connective]

    new_rel["Arg1"]["TokenList"] = arg1_comb
    new_rel["Arg2"]["TokenList"] = arg2_comb

    return new_rel


def unify_files(l1_path, l2_path, out_path, keep_single=False):
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
    out_path : str
        Path to save the result to.
    keep_single : Bool
        Whether or not to keep relations,
        that only occur in one of the files.
        Default: False
    """
    
    rels1 = []
    rels2 = []

    for line in open(l1_path):
        rel = json.loads(line)
        rels1.append(rel)
    for line in open(l2_path):
        rel = json.loads(line)
        rels2.append(rel)

    found_rels = []

    for i, rel1 in enumerate(rels1):
        for j, rel2 in enumerate(rels2):
            new_rel = unify_rels(rel1, rel2)
            if not new_rel is None:
                found_rels.append((i,j,new_rel))

    new_rels = []
    for i, j, new_rel in found_rels:
        rels1[i] = None
        rels2[j] = None
        new_rels.append(new_rel)

    if keep_single:
        for rel in rels1:
            if not rel is None:
                new_rels.append(rel)
        for rel in rels2:
            if not rel is None:
                new_rels.append(rel)

    for i, rel in enumerate(new_rels):
        rel["ID"] = i

    with open(out_path, "w") as out_file:
        for rel in new_rels:
            json.dump(rel,out_file)
            out_file.write("\n")


def unify_langs(dir1, dir2, out_dir, keep_files=False, keep_rels=False):
    """
    Combine relations for files in two directories.

    Parameters
    ----------
    dir1 : str
        Path to first directory.
    dir2 : str
        Path to second directory.
    out_dir : str
        Directory to save results to.
    keep_files : bool
        Copy files that only occur in one of the directories.
    keep_rels : bool
        When processing two files, keep relations
        that only occur in one of them.
    """
    fns1 = set(os.listdir(dir1))
    fns2 = set(os.listdir(dir2))

    fns_both = [fn for fn in fns1 if fn in fns2]
    num_files = len(fns_both)

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    for fn in tqdm(fns_both):
        path1 = os.path.join(dir1, fn)
        path2 = os.path.join(dir2, fn)
        out_path = os.path.join(out_dir, fn)
        unify_files(path1, path2, out_path, keep_single=keep_rels)

    if keep_files:
        fns1 = [fn for fn in fns1 if fn not in fns_both]
        fns2 = [fn for fn in fns2 if fn not in fns_both]
        for fn in fns1:
            prev_path = os.path.join(dir1, fn)
            new_path = os.path.join(out_dir, fn)
            shutil.copy(prev_path, new_path)
        for fn in fns2:
            prev_path = os.path.join(dir2, fn)
            new_path = os.path.join(out_dir, fn)
            shutil.copy(prev_path, new_path)


#def unify_langs(dir1, dir2, out_dir, keep_files=False, keep_rels=False):
#unify_langs("/data/europarl/common/transferred/from_en", "/data/europarl/common/transferred/from_fr", "/data/europarl/common/parsed/en_fr")
#unify_langs("/data/europarl/common/transferred/from_en", "/data/europarl/common/transferred/from_cs", "/data/europarl/common/parsed/en_cs")
#unify_langs("/data/europarl/common/transferred/from_cs", "/data/europarl/common/transferred/from_fr", "/data/europarl/common/parsed/cs_fr")
#unify_langs("/data/europarl/common/parsed/cs_fr", "/data/europarl/common/transferred/from_en", "/data/europarl/common/parsed/cs_fr_en")


