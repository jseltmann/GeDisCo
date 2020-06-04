import os
import json
import xml.etree.ElementTree as ET


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
                de = int(de)
                en = int(en)
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
            as_dict = json.loads(line)
            relations.append(as_dict)
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

    #for fn in os.listdir(align_dir):
    #    if not fn[:-4] in parsed_fns:
    #        continue
    #    parsed_path = os.path.join(parsed_dir, fn[:-4])
    #    align_path = os.path.join(align_dir, fn)

    #    trans_rels[fn] = []

    alignments = read_alignments(align_path)

    #    with open(parsed_path) as parsed_f:
    #        for line in parsed_f:
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

#translate_parsed("/data/europarl/common/parsed/en",
#                 "/data/europarl/common/word_aligned/de_en_intersection")


def read_dimlex(dimlex_path):
    """
    Read discourse connectives from DiMLex file.

    Parameters
    ----------
    dimlex_path : str
        Path to xml file containing DiMLex.

    Return
    ------
    connectives : [str]
        List of discourse connectives.
    """

    tree = ET.parse(dimlex_path)
    entries = tree.iter("entry")
    connectives = []
    for entry in entries:
        word = entry.attrib["word"]
        connectives.append(word)
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

    for fn in os.listdir(relations_dir):
        parsed_path = os.path.join(relations_dir, fn)
        relations = read_relations(parsed_path)

        align_path = os.path.join(align_dir, fn+".txt")
        if not os.path.exists(align_path):
            continue
        relations = replace_inds(relations, align_path)
        print(relations[4])
        6 / 0

        txt_path = os.path.join(txt_dir, fn+".txt")
        text = read_txt(txt_path)

        
        for relation in relations:
            if relation["Type"] == "Explicit":
                connective = relation["Connective"]
                connective = [text[i] for i in connective]
                connective = " ".join(connective).lower()
                if not connective in dimlex_connectives:
                    relation["Type"] = "Implicit"
                    relation[




transfer_rels("/data/europarl/common/parsed/en",
              "/data/europarl/common/word_aligned/de_en_intersection",
              "/data/europarl/common/txt/de",
              "/data/europarl/common/transferred/from_en",
              "/data/dimlex/DimLex.xml")
