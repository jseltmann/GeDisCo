import os
import json
from lxml import etree
import benepar


def trans_arg(arg, tok_tups):
    """
    Transfer relation argument from conll output format to input format.

    Parameters
    ----------
    arg : dict()
        Argument.
    toks_tups : [[]]
        List of tokens in text.
    """

    new_arg = dict()

    #generate token list
    tok_list = arg["TokenList"]
    new_tok_list = []
    for i, tok_ind in enumerate(tok_list):
        char_start, char_end, sent_num, _ = tok_tups[tok_ind]
        # format for each token:
        # [ind of first character, ind of first character after token,
        #  token index in text, index of sentence, index of token in arg["TokenList"]]
        new_tok = [char_start, char_end, tok_ind, sent_num, i]
        new_tok_list.append(new_tok)

    new_arg["TokenList"] = new_tok_list
    
    #generate CharacterSpanList
    split_lists = []
    curr_list = []
    for tok_tup in new_tok_list:
        if curr_list == []:
            curr_list.append(tok_tup)
        elif curr_list[-1][2] == tok_tup[2] - 1:
            curr_list.append(tok_tup)
        else:
            split_lists.append(curr_list)
            curr_list = [tok_tup]
    if curr_list != []:
        split_lists.append(curr_list)

    char_spans = []
    for tok_list in split_lists:
        char_span = [tok_list[0][0], tok_list[-1][1]]
        char_spans.append(char_span)

    new_arg["CharacterSpanList"] = char_spans

    #generate raw text
    word_inds = [tok_tup[2] for tok_tup in new_tok_list]
    words = [tok_tups[i][3] for i in word_inds]
    raw_text = ""
    for word in words:
        if word in [",",")",".",";",":","?","!"] or \
                raw_text == "" or \
                raw_text[-1] == "(":
            raw_text += word
        else:
            raw_text += " " + word

    new_arg["RawText"] = raw_text

    return new_arg


def transfer_to_conll(parsed_path, txt_path, out_path):
    """
    Take a file containing translated relations and
    transfer it to the data format of the CoNLL 2015 shared task.

    Parameters
    ----------
    parsed_path : str
        Path to file containing the transferred relations.
    txt_path : str
        Path to word-tokenized txt file with one sentence per line.
    out_path : str
        Path to save resulting file to.
    """

    char_count, tok_count, sent_count = -2,0,0
    toks = []

    with open(txt_path) as txt_file:
        for i, line in enumerate(txt_file):
            curr_toks = line.split()
            for j,tok in enumerate(curr_toks):
                if not tok in [",",")",".",";",":","?","!"] or j==0:
                    #count whitespaces and linebreaks
                    char_count += 1
                char_start = char_count + 1
                char_end = char_start + len(tok)
                sent_num = i
                toks.append([char_start, char_end, sent_num, tok])
                char_count += len(tok)
                if tok == "(":
                    #since the tokenization left whitespaces behind (
                    char_count += 1

    rels = []
    with open(parsed_path) as parsed_file:
        fn = parsed_path.split("/")[-1]
        for i, line in enumerate(parsed_file):
            rel = json.loads(line)
            new_rel = dict()
            new_rel["DocID"] = fn
            new_rel["ID"] = i
            new_rel["Sense"] = rel["Sense"]
            new_rel["Type"] = rel["Type"]
            new_rel["Arg1"] = trans_arg(rel["Arg1"], toks)
            new_rel["Arg2"] = trans_arg(rel["Arg2"], toks)
            new_rel["Connective"] = trans_arg(rel["Connective"], toks)

            rels.append(new_rel)

    with open(out_path, "w") as out_file:
        for rel in rels:
            json.dump(rel,out_file)
            out_file.write("\n")


def transfer_to_conll_dir(parsed_dir, txt_dir, out_dir):
    """
    Wrapper for transfer_to_conll to wok over directories.
    """

    fns = os.listdir(parsed_dir)

    for fn in fns:
        parsed_path = os.path.join(parsed_dir, fn)
        txt_path = os.path.join(txt_dir, fn+".txt")
        out_path = os.path.join(out_dir, fn+".json")

        transfer_to_conll(parsed_path, txt_path, out_path)


#transfer_to_conll_dir("/data/europarl/common/transferred/from_cs",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/conll_labels/from_cs")
#transfer_to_conll_dir("/data/europarl/common/transferred/from_fr",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/conll_labels/from_fr")
#transfer_to_conll_dir("/data/europarl/common/test",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/test2")



def transfer_to_pcc(parsed_path, txt_path, out_path):
    """
    Take a file containing translated relations and
    transfer it to the data format of the Potsdam Commentary Corpus.

    Parameters
    ----------
    parsed_path : str
        Path to file containing the transferred relations.
    txt_path : str
        Path to word-tokenized txt file with one sentence per line.
    out_path : str
        Path to save resulting file to.
    """
    
    toks = []

    for line in open(txt_path):
        toks += line.split()

    discourse = etree.Element("discourse")
    tokens = etree.SubElement(discourse, "tokens")
    for i, tok in enumerate(toks):
        etree.SubElement(tokens, "token", id=str(i)).text = tok

    relations = etree.SubElement(discourse, "relations")
    with open(parsed_path) as parsed_f:
        for line in parsed_f:
            rel = json.loads(line)
            rel_id = rel["ID"]
            rel_type = rel["Type"].lower()
            rel_sense = rel["Sense"][0]
            new_rel = etree.SubElement(relations, "relation", 
                relation_id=str(rel_id), type=rel_type, pdtb3_sense=rel_sense)

            conn = rel["Connective"]["TokenList"]
            conn_toks = [(i, toks[i]) for i in conn]
            connective_tokens = etree.SubElement(new_rel, "connective_tokens")
            for ind, tok in conn_toks:
                etree.SubElement(connective_tokens, "connective_token", 
                        id=str(ind), token=tok)
            
            arg1 = rel["Arg1"]["TokenList"]
            arg2 = rel["Arg2"]["TokenList"]
            # the PCC differentiates between internal and external arguments
            if len(conn) == 0:
                one_internal = True
            elif len(arg2) == 0:
                one_internal = True
            elif len(arg1) == 0:
                one_internal = False
            elif max(conn) >= min(arg2) and min(conn) > max(arg1):
                # if parts of the connective are in argument 2
                # and none in argument 1
                # we consider it to be the internal argument
                one_internal = False
            else:
                one_internal = True

            if one_internal:
                int_arg_tokens = etree.SubElement(new_rel, "int_arg_tokens")
                for tok_ind in arg1:
                    tok = toks[tok_ind]
                    etree.SubElement(int_arg_tokens, "int_arg_token",
                            id=str(tok_ind), token=tok)
                ext_arg_tokens = etree.SubElement(new_rel, "ext_arg_tokens")
                for tok_ind in arg2:
                    tok = toks[tok_ind]
                    etree.SubElement(ext_arg_tokens, "ext_arg_token",
                            id=str(tok_ind), token=tok)
            else:
                ext_arg_tokens = etree.SubElement(new_rel, "ext_arg_tokens")
                for tok_ind in arg1:
                    tok = toks[tok_ind]
                    etree.SubElement(ext_arg_tokens, "ext_arg_token",
                            id=str(tok_ind), token=tok)
                int_arg_tokens = etree.SubElement(new_rel, "int_arg_tokens")
                for tok_ind in arg2:
                    tok = toks[tok_ind]
                    etree.SubElement(int_arg_tokens, "int_arg_token",
                            id=str(tok_ind), token=tok)

    tree = etree.ElementTree(discourse)
    tree.write(out_path, encoding="UTF-8", 
            xml_declaration=True, pretty_print=True)


def transfer_to_pcc_dir(parsed_dir, txt_dir, out_dir):
    """
    Wrapper for transfer_to_pcc to work over directories.
    """

    fns = os.listdir(parsed_dir)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    for i, fn in enumerate(fns):
        if i % 5000 == 0:
            print(out_dir.split("/")[-1], ": ", i)
        parsed_path = os.path.join(parsed_dir, fn)
        txt_path = os.path.join(txt_dir, fn+".txt")
        out_path = os.path.join(out_dir, fn+".xml")

        transfer_to_pcc(parsed_path, txt_path, out_path)


#transfer_to_pcc_dir("/data/europarl/common/transferred/from_cs",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/pcc_labels/from_cs")
#transfer_to_pcc_dir("/data/europarl/common/transferred/from_en",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/pcc_labels/from_en")
#transfer_to_pcc_dir("/data/europarl/common/transferred/from_fr",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/pcc_labels/from_fr")

#transfer_to_pcc_dir("/data/europarl/common/parsed/cs_fr",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/pcc_labels/cs_fr")
#transfer_to_pcc_dir("/data/europarl/common/parsed/en_cs",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/pcc_labels/en_cs")
#transfer_to_pcc_dir("/data/europarl/common/parsed/en_fr",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/pcc_labels/en_fr")
#transfer_to_pcc_dir("/data/europarl/common/parsed/cs_fr_en",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/pcc_labels/cs_fr_en")

def parse_berkeley(inp_dir, out_dir):
    """
    Parse file using the berkely neural parser.

    Parameters
    ----------
    inp_dir : str
        Directory containing tokenized text files.
    out_dir : str
        Directory to save produced parses to.
    """
    
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    parser = benepar.Parser("benepar_de")

    for i, fn in enumerate(os.listdir(inp_dir)):
        if i == 10:
            print(i)
        if i % 5000 == 0:
            print(i)
        if fn[-4:] == "inds":
            continue
        txt_path = os.path.join(inp_dir,fn)
        out_path = os.path.join(out_dir, fn[:-4]+".ptree")
        if os.path.exists(out_path):
            continue

        with open(out_path, "w") as out_file:
            for line in open(txt_path):
                tree = parser.parse(line.split())
                tree.pprint(stream=out_file)
            
        
parse_berkeley("/data/europarl/common/txt/de_shortened", "/data/europarl/common/syntax/de/berkeley")
#parse_berkeley("/data/europarl/common/test", "/data/europarl/common/test2")
