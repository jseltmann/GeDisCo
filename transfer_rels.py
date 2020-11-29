import os
import json
import xml.etree.ElementTree as ET
from tqdm import tqdm
import random


def read_alignments(align_path):
    """
    Read alignments from file. Translate the
    alignment indices from numbering the words
    per sentence to numbering across the document.
    (I.e., if the first sentence in a language has 5
    words, then the first word of the second sentence
    will be labeled as 5 instead of 0.)

    Parameters
    ----------
    align_path : str
        Path to file containing the alignments.

    Return
    ------
    alignments : dict(int)
        Dictionary assigning a list of German word indices
        words to each English word index.
    """

    align_tuples = []

    alignments = dict()
    with open(align_path) as align_file:
        for line in align_file:
            if line.strip() == "":
                continue
            algmts = line[:-1].split(" ")
            algmts = [al.split("-") for al in algmts]
            for de, en in algmts:
                de = int(de) - 1
                en = int(en) - 1
                if en in alignments:
                    alignments[en].append(de)
                else:
                    alignments[en] = [de]

    return alignments


def read_relations(parsed_path):
    """
    Read parsed relations from file.

    Parameters
    ----------
    parsed_path : str
        Path to file containing the relations.

    Return
    ------
    relations : [dict]
        List of discourse relations.
    """

    relations = []
    with open(parsed_path) as parsed_file:
        for line in parsed_file:
            try:
                as_dict = json.loads(line)
                relations.append(as_dict)
            except Exception as e:
                print(line)
                raise e
    return relations


def replace_inds(relations, align_path):
    """
    Take output of English parser.
    Replace indices of words with corresponding word
    indices of the German text.

    Parameters
    ----------
    relations : [dict]
        List of relations found for the file.
    align_path : str
        File containing alignments.

    Return
    ------
    trans_rels : dict
        Relations with transferred indices.
    """

    trans_rels = []

    alignments = read_alignments(align_path)

    for relation in relations:
        arg1_list = relation['Arg1']['TokenList']
        arg1_new = [alignments[n] for n in arg1_list if n in alignments]
        arg1_new = [n for n_list in arg1_new for n in n_list]
        relation['Arg1']['TokenList'] = arg1_new

        arg2_list = relation['Arg2']['TokenList']
        arg2_new = [alignments[n] for n in arg2_list if n in alignments]
        arg2_new = [n for n_list in arg2_new for n in n_list]
        relation['Arg2']['TokenList'] = arg2_new

        connec_list = relation['Connective']['TokenList']
        connec_new = [alignments[n] for n in connec_list if n in alignments]
        connec_new = [n for n_list in connec_new for n in n_list]
        relation['Connective']['TokenList'] = connec_new

        trans_rels.append(relation)

    return trans_rels


def read_dimlex(dimlex_path):
    """
    Read discourse connectives from DiMLex file.

    Parameters
    ----------
    dimlex_path : str
        Path to xml file containing DiMLex.

    Return
    ------
    connectives : dict
        Dictionary of discourse connectives and possible senses.
    """

    tree = ET.parse(dimlex_path)
    entries = tree.iter("entry")
    connectives = dict()
    for entry in entries:
        word = entry.attrib["word"]
        rels = entry.iter("pdtb3_relation")
        
        senses = [rel.attrib["sense"] for rel in rels]
        #translate between pdtb and conll senses
        senses_conll = set()
        for sense in senses:
            sense = sense.split(".")
            if sense[-1].startswith("Arg"):
                sense = sense[:-1]
            sense = ".".join(sense)
            if sense.startswith("Comparison.Concession"):
                sense = "Comparison.Concession"
            elif sense == "Expansion.Level-of-detail":
                sense = "Expansion"
            elif sense == "Expansion.Substitution":
                sense = "Expansion"
            elif sense == "Contingency.Negative-condition":
                sense = "Contingency"
            elif sense == "Contingency.Purpose":
                sense = "Contingency"
            elif sense == "Expansion.Manner":
                sense = "Expansion"
            elif sense == "Expansion.Equivalence":
                sense = "Expansion"
            elif sense == "Expansion.Disjunction":
                sense = "Expansion"
            elif sense == "Temporal.Synchronous":
                sense = "Temporal.Synchrony"
            senses_conll.add(sense)

        orths = entry.iter("orth")
        for orth in orths:
            parts = orth.iter("part")
            parts = tuple([part.text for part in parts])
            connectives[parts] = senses_conll

    return connectives


def read_txt(txt_path):
    """
    Read txt file and return list of tokens.

    Parameters
    ----------
    txt_path : str
        Path to txt file.

    Return
    ------
    tokens : [str]
        Tokens in txt file.
    """

    tokens = []
    with open(txt_path) as txt_file:
        for line in txt_file:
            line = line.split()
            tokens += line
    return tokens


def is_contained(sense, senses):
    """
    Determine, if a sense found by the Wang/Lan parser
    is contained in a list of senses from the DimLex dataset.
    Includes some hard-coded rules to translate between
    CoNLL-2015 and pdtb3 relations.

    Parameters
    ----------
    sense : str
        Sense found by Wang/Lan.
    senses : [str]
        Senses for a connective in DimLex.

    Return
    ------
    contained : bool
       True if the sense is contained.
    """
    
    if sense in senses:
        return True

    if sense.startswith("Expansion.Alternative") and "Expansion" in senses:
        return True
    if sense == "Expansion.Restatement" and "Expansion" in senses:
        return True
    if sense == "Temporal.Synchrony" and "Temporal.Synchronous" in senses:
        return True

    return False


def trans_implicit(relation, dimlex_connectives, text):
    """
    Check if translated implicit relation has become explicit.

    Parameters
    ----------
    relation : dict
        Relation from output of replace_inds.
    dimlex_connectives : dict
        DimLex connectives with senses.
    text : [str]
        Text of for which the relation has been found.
    """
    text1 = [text[i] for i in relation["Arg1"]["TokenList"]]
    text2 = [text[i] for i in relation["Arg2"]["TokenList"]]
    sense = relation["Sense"][0]
    relation["orig_type"] = "Implicit"

    for connective in dimlex_connectives:
        senses = dimlex_connectives[connective]
        if not is_contained(sense,senses):
            continue

        if len(connective) == 1:
            words = connective[0].split()
            if text1[:len(words)] == words:
                #first argument begins with connective
                toks = relation["Arg1"]["TokenList"]
                new_conn = toks[:len(words)]
                tok_new = toks[len(words):]
                relation["Arg1"]["TokenList"] = tok_new
                relation["Connective"]["TokenList"] = new_conn
                relation["Type"] = "Explicit"
                return relation
            if text1[-len(words):] == words:
                #first argument ends with connective
                toks = relation["Arg1"]["TokenList"]
                new_conn = toks[-len(words):]
                tok_new = toks[:-len(words)]
                relation["Arg1"]["TokenList"] = tok_new
                relation["Connective"]["TokenList"] = new_conn
                relation["Type"] = "Explicit"
                return relation
            if text2[:len(words)] == words:
                #second argument begins with connective
                toks = relation["Arg2"]["TokenList"]
                new_conn = toks[:len(words)]
                tok_new = toks[len(words):]
                relation["Arg2"]["TokenList"] = tok_new
                relation["Connective"]["TokenList"] = new_conn
                relation["Type"] = "Explicit"
                return relation
            if text2[-len(words):] == words:
                #first argument ends with connective
                toks = relation["Arg2"]["TokenList"]
                new_conn = toks[-len(words):]
                tok_new = toks[:-len(words)]
                relation["Arg2"]["TokenList"] = tok_new
                relation["Connective"]["TokenList"] = new_conn
                relation["Type"] = "Explicit"
                return relation
        else: #spelling consists of two parts
            words1 = connective[0].split()
            words2 = connective[1].split()
            new_rel = relation
            found1, found2 = False, False
            if text1[:len(words1)] == words1:
                #first argument begins with connective
                toks = new_rel["Arg1"]["TokenList"]
                new_conn = toks[:len(words)]
                tok_new = toks[len(words):]
                new_rel["Arg1"]["TokenList"] = tok_new
                new_rel["Connective"]["TokenList"] += new_conn
                new_rel["Type"] = "Explicit"
                found1 = True
            if text1[-len(words):] == words:
                #first argument ends with connective
                toks = new_rel["Arg1"]["TokenList"]
                new_conn = toks[-len(words):]
                tok_new = toks[:-len(words)]
                new_rel["Arg1"]["TokenList"] = tok_new
                new_rel["Connective"]["TokenList"] += new_conn
                new_rel["Type"] = "Explicit"
                found1 = True
            if text2[:len(words)] == words2:
                #second argument begins with connective
                toks = new_rel["Arg2"]["TokenList"]
                new_conn = toks[:len(words)]
                tok_new = toks[len(words):]
                new_rel["Arg2"]["TokenList"] = tok_new
                new_rel["Connective"]["TokenList"] = new_conn
                new_rel["Type"] = "Explicit"
                found2 = True
            if text2[-len(words):] == words2:
                #first argument ends with connective
                toks = new_rel["Arg2"]["TokenList"]
                new_conn = toks[-len(words):]
                tok_new = toks[:-len(words)]
                new_rel["Arg2"]["TokenList"] = tok_new
                new_rel["Connective"]["TokenList"] = new_conn
                new_rel["Type"] = "Explicit"
                found2 = True
            if found1 and found2:
                return new_rel
    return relation


def trans_explicit(relation, dimlex_connectives, text):
    """
    Check if translated explicit relation has become implicit.

    Parameters
    ----------
    relation : dict
        Relation from output of replace_inds.
    dimlex_connectives : dict
        DimLex connectives with senses.
    text : [str]
        Text of for which the relation has been found.
    """
    curr_connective = relation["Connective"]["TokenList"]
    curr_connective = [text[i].lower() for i in curr_connective]
    found = False
    for connective in dimlex_connectives:
        connective = [part.split() for part in connective]
        connective = [word for part in connective for word in part]
        if connective == curr_connective:
            found = True
            break
    if not found:
        relation["Type"] = "Implicit"
        relation["Connective"]["TokenList"] = []
    relation["orig_type"] = "Explicit"
    return relation


def transfer_rels(relations_dir, align_dir, txt_dir, out_dir, dimlex_path):
    """
    Transfer relations for one language to German text.

    Parameters
    ----------
    relations_dir : str
        Path to directory containing parsed relations.
    align_dir : str
        Path to directory containing alignments.
    txt_dir : str
        Directory containing German text.
    out_dir : str
        Directory to save transferred relations to.
    dimlex_path : str
        File containing dimlex dataset.
    """

    dimlex_connectives = read_dimlex(dimlex_path)

    for fn in tqdm(os.listdir(relations_dir)):
        parsed_path = os.path.join(relations_dir, fn)
        relations = read_relations(parsed_path)

        align_path = os.path.join(align_dir, fn+".txt")
        if not os.path.exists(align_path):
            continue
        relations = replace_inds(relations, align_path)

        txt_path = os.path.join(txt_dir, fn+".txt")
        text = read_txt(txt_path)

        trans_relations = []
        for i, relation in enumerate(relations):
            #make relation arguments contiguous
            tok_list1 = relation["Arg1"]["TokenList"]
            if len(tok_list1) > 0:
                tok_min = min(tok_list1)
                tok_max = max(tok_list1)
                tok_list1 = list(range(tok_min,tok_max+1))
                relation["Arg1"]["TokenList"] = tok_list1

            tok_list2 = relation["Arg2"]["TokenList"]
            if len(tok_list2) > 0:
                tok_min = min(tok_list2)
                tok_max = max(tok_list2)
                tok_list2 = list(range(tok_min,tok_max+1))
                relation["Arg2"]["TokenList"] = tok_list2

            if relation["Type"] == "Explicit":
                relation = trans_explicit(relation, dimlex_connectives, text)
            else:
                relation = trans_implicit(relation, dimlex_connectives, text)

            tok_list1 = relation["Arg1"]["TokenList"]
            tok_list2 = relation["Arg2"]["TokenList"]
            if tok_list1 == [] or tok_list2 == []:
                continue
            trans_relations.append(relation)
        
        out_path = os.path.join(out_dir, fn)
        with open(out_path, "w") as out_file:
            for rel in trans_relations:
                json.dump(rel,out_file,ensure_ascii=False)
                out_file.write("\n")


simple_drop_probs = {"Comparison.Contrast": 0.5,
                     "Contingency.Cause.Reason": 0.5,
                     "Contingency.Cause.Result": 0.5,
                     "Expansion.Restatement": 2/3}


def sample_relations(orig_dir, new_dir, drop_probs, seed=28):
    """
    Take directory of relations and sample out
    some of the relations that occur more often
    in our corpus than in the PCC.

    Parameters
    ----------
    orig_dir : str
        Directory containing the original relations.
    new_dir : str
        Directory to save new relations to.
    drop_probs : dict()
        Dictionary containing probabilities, that a
        relation of a sense will be dropped.
        Senses not contained in the dictionary aren't dropped.
    seed : int
        Random seed to use.
    """

    random.seed(seed)
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    for fn in tqdm(os.listdir(orig_dir)):
        to_transfer = []
        with open(os.path.join(orig_dir, fn)) as relsf:
            for line in relsf:
                rel = json.loads(line)
                sense = rel["Sense"][0]
                if sense in drop_probs:
                    drop_num = random.random()
                    if drop_num < drop_probs[sense]:
                        drop = True
                    else:
                        drop = False
                else:
                    drop = False
                if not drop:
                    to_transfer.append(rel)

        with open(os.path.join(new_dir, fn), "w") as newf:
            for rel in to_transfer:
                json.dump(rel, newf)
                newf.write("\n")


def _single_sent(i_inds, e_inds, sent_inds):
    """
    Return true, if each argument of the relation
    is contained in one sentence each.
    Also count as true, if the last word of the argument is
    in the next sentence.
    """
    for j, curr_sent in enumerate(sent_inds):
        comb = [i for i in i_inds if i in curr_sent]
        overhang = [i for i in i_inds if i not in curr_sent]
        if len(comb) > 0 and len(overhang) < 2:
            if j < len(sent_inds) - 1:
                next_sent = sent_inds[j+1]
                comb2 = [i for i in e_inds if i in next_sent]
                overhang2 = [i for i in e_inds if i not in next_sent]
                if len(comb2) > 0 and len(overhang) < 2:
                    return True
            if j > 0:
                prev_sent = sent_inds[j-1]
                comb2 = [i for i in e_inds if i in prev_sent]
                overhang2 = [i for i in e_inds if i not in prev_sent]
                if len(comb2) > 0 and len(overhang) < 2:
                    return True
    return False


def sample_relations_impl_sents(orig_dir, txt_dir, new_dir):
    """
    Take directory of relations and sample out
    implicit relations that do not span between two sentences.

    Parameters
    ----------
    orig_dir : str
        Directory containing the original relations.
    txt_dir : str
        Directory containing German text.
    new_dir : str
        Directory to save new relations to.
    """

    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    for fn in tqdm(os.listdir(orig_dir)):
        txt_path = os.path.join(txt_dir, fn.split(".")[0] + ".txt")
        with open(txt_path) as txt_file:
            lines = txt_file.readlines()
            sents = [line.split() for line in lines]
            sent_inds = []
            word_count = 0
            for sent in sents:
                inds = set([i + word_count for i in range(len(sent))])
                sent_inds.append(inds)
                word_count += len(sent)

        to_transfer = []
        with open(os.path.join(orig_dir, fn)) as relsf:
            for line in relsf:
                relation = json.loads(line)
                i_inds = relation["Arg1"]["TokenList"]
                e_inds = relation["Arg2"]["TokenList"]
                if _single_sent(i_inds, e_inds, sent_inds):
                    to_transfer.append(relation)

        with open(os.path.join(new_dir, fn), "w") as newf:
            for rel in to_transfer:
                json.dump(rel, newf)
                newf.write("\n")
