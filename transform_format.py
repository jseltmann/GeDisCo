import os
import json
from lxml import etree
import benepar
from tqdm import tqdm
import html
from nltk.tree import Tree, ParentedTree
import pickle


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
    Wrapper for transfer_to_conll to work over directories.
    """

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    fns = os.listdir(parsed_dir)

    for fn in tqdm(fns):
        parsed_path = os.path.join(parsed_dir, fn)
        txt_path = os.path.join(txt_dir, fn+".txt")
        out_path = os.path.join(out_dir, fn+".json")

        transfer_to_conll(parsed_path, txt_path, out_path)


#print("CoNLL En")
#transfer_to_conll_dir("/data/europarl/common/transferred/from_en",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/conll_labels/from_en")
#print("CoNLL En_Cs")
#transfer_to_conll_dir("/data/europarl/common/parsed/en_cs",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/conll_labels/en_cs")
#print("CoNLL En_Fr")
#transfer_to_conll_dir("/data/europarl/common/parsed/en_fr",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/conll_labels/en_fr")
#print("CoNLL Cs_Fr")
#transfer_to_conll_dir("/data/europarl/common/parsed/cs_fr",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/conll_labels/cs_fr")
#print("CoNLL Cs_Fr_En")
#transfer_to_conll_dir("/data/europarl/common/parsed/cs_fr_en",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/conll_labels/cs_fr_en")
#print("CoNLL Cs")
#transfer_to_conll_dir("/data/europarl/common/transferred/from_cs",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/conll_labels/from_cs")
#print("CoNLL Fr")
#transfer_to_conll_dir("/data/europarl/common/transferred/from_fr",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/conll_labels/from_fr")


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

    for fn in tqdm(fns):
        parsed_path = os.path.join(parsed_dir, fn)
        txt_path = os.path.join(txt_dir, fn+".txt")
        out_path = os.path.join(out_dir, fn+".xml")

        transfer_to_pcc(parsed_path, txt_path, out_path)

#print("PCC Cs")
#transfer_to_pcc_dir("/data/europarl/common/transferred/from_cs",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/pcc_labels/from_cs")
#print("PCC En")
#transfer_to_pcc_dir("/data/europarl/common/transferred/from_en",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/pcc_labels/from_en")
#print("PCC Fr")
#transfer_to_pcc_dir("/data/europarl/common/transferred/from_fr",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/pcc_labels/from_fr")
#
#print("PCC Cs_Fr")
#transfer_to_pcc_dir("/data/europarl/common/transferred/cs_fr",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/pcc_labels/cs_fr")
#print("PCC En_Cs")
#transfer_to_pcc_dir("/data/europarl/common/transferred/en_cs",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/pcc_labels/en_cs")
#print("PCC En_Fr")
#transfer_to_pcc_dir("/data/europarl/common/transferred/en_fr",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/pcc_labels/en_fr")
#print("PCC Cs_Fr_En")
#transfer_to_pcc_dir("/data/europarl/common/transferred/cs_fr_en",
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
            
        
#parse_berkeley("/data/europarl/common/txt/de_shortened", "/data/europarl/common/syntax/de/berkeley")
#parse_berkeley("/data/europarl/common/test", "/data/europarl/common/test2")


def remove_incomplete(tiger_dir, txt_dir):
    """
    Remove files from the tiger xml directory,
    that weren't completely translated into the tiger format.

    Parameters
    ----------
    tiger_dir : str
        Directory containing tiger xml files.
    txt_dir : str
        Directory containing corresponding tokenized text files.
    """

    fns = os.listdir(tiger_dir)
    fns = [fn.split(".")[0] for fn in fns]

    for fn in tqdm(fns):
        tiger_path = os.path.join(tiger_dir, fn+".xml")
        tree = etree.parse(tiger_path)
        toks = tree.findall(".//t")

        txt_path = os.path.join(txt_dir, fn+".txt")
        with open(txt_path) as txt_file:
            text = txt_file.read()
            words = text.split()
            #num = 0
            #for line in txt_file:
            #    words = line.split()
            #    num += len(words)

        if len(words) != len(toks):
            os.remove(tiger_path)

        for word, tok in zip(words, toks):
            tok = tok.attrib["word"]
            tok = html.unescape(tok)
            if word != tok:
                os.remove(tiger_path)
                break


#remove_incomplete("/data/europarl/common/syntax/de/tiger",
#                  "/data/europarl/common/txt/de") 


def remove_empty_lines(pcc_tok_dir, pcc_tok_new):
    """
    Remove empty lines from tokenized PCC files.
    This serves to be able to create character counts
    in the PCC-to-CoNLL transformation.

    Parameters
    ----------
    pcc_tok_dir : str
        Directory containing tokenized PCC files.
    pcc_tok_new : str
        Directory to write the resulting files to.
    """
    for fn in os.listdir(pcc_tok_dir):
        tok_path = os.path.join(pcc_tok_dir, fn)
        new_path = os.path.join(pcc_tok_new, fn)
        with open(tok_path) as tok_file:
            lines = tok_file.readlines()
        no_empty = [l for l in lines if l.strip() != ""]
        with open(new_path, "w") as new_file:
            for line in no_empty:
                new_file.write(line)

#remove_empty_lines("/data/PotsdamCommentaryCorpus/tokenized", "/data/PotsdamCommentaryCorpus/tokenized_no_emp_lines")


def pcc_to_conll(pcc_dir, conll_path):
    """
    Transfer PCC connectives file to conll 2015 format.

    Parameters
    ----------
    pcc_dir : str
        Directory containing parsed PCC connectives.
    conll_path : str
        Path to save resulting json format to.
    """

    rel_dicts = []
    for fn in os.listdir(pcc_dir):
        pcc_path = os.path.join(pcc_dir, fn)

        parsed = etree.parse(pcc_path)
        root = parsed.getroot()
        tokens = root.findall("tokens")[0].findall("token")
        tok_info = dict()
        char_count = 0
        for tok in tokens:
            ind = int(tok.attrib["id"])
            word = tok.text
            start = char_count
            end = char_count + len(word) + 1
            tok_info[ind] = (start, end)
            char_count = end + 1

        relations = root.findall("relations")[0].findall("relation")
        for relation in relations:
            rel = dict()
            if "pdtb3_sense" in relation.attrib:
                rel["Sense"] = [relation.attrib["pdtb3_sense"]]
            else:
                rel["Sense"] = [relation.attrib["type"]] # EntRel or NoRel
            if relation.attrib["type"] == "explicit":
                rel["Type"] = "Explicit"
            elif relation.attrib["type"] == "implicit":
                rel["Type"] = "Implicit"
            else:
                rel["Type"] = relation.attrib["type"]
            rel["ID"] = relation.attrib["relation_id"]
            rel["DocID"] = pcc_path.split("/")[-1].split(".")[0] # filename without .xml

            intarg_toks = relation.findall("int_arg_tokens")[0].findall("int_arg_token")
            intarg_toks = sorted([(int(t.attrib["id"]), t.attrib["token"]) for t in intarg_toks], key=lambda x:x[0])
            extarg_toks = relation.findall("int_arg_tokens")[0].findall("ext_arg_token")
            extarg_toks = sorted([(int(t.attrib["id"]), t.attrib["token"]) for t in extarg_toks], key=lambda x:x[0])
            conn_toks = relation.findall("connective_tokens")[0].findall("connective_token")
            conn_toks = sorted([(int(t.attrib["id"]), t.attrib["token"]) for t in conn_toks], key=lambda x:x[0])

            if len(intarg_toks) > 0 and len(extarg_toks) > 0:
                if min([i for i,_ in intarg_toks]) < min([i for i,_ in extarg_toks]):
                    arg1_toks = intarg_toks
                    arg2_toks = extarg_toks
                else:
                    arg1_toks = extarg_toks
                    arg2_toks = intarg_toks
            else:
                    arg1_toks = intarg_toks
                    arg2_toks = extarg_toks

            rel["Arg1"] = dict()
            rel["Arg1"]["TokenList"] = []
            rel["Arg1"]["RawText"] = ""
            for i, (num, tok) in enumerate(arg1_toks):
                start, end = tok_info[num]
                tok_ids = [start, end, num, 0, i]
                # putting 0 because sentences don't matter to evaluation
                rel["Arg1"]["TokenList"].append(tok_ids)
                rel["Arg1"]["RawText"] += tok + " "
            if len(rel["Arg1"]["TokenList"]) > 0:
                rel["Arg1"]["CharacterSpanList"] = [[rel["Arg1"]["TokenList"][0][0],
                                                     rel["Arg1"]["TokenList"][-1][1]]]
            else:
                rel["Arg2"]["CharacterSpanList"] = []

            rel["Arg2"] = dict()
            rel["Arg2"]["TokenList"] = []
            rel["Arg2"]["RawText"] = ""
            for i, (num, tok) in enumerate(arg2_toks):
                start, end = tok_info[num]
                tok_ids = [start, end, num, 0, i]
                # putting 0 because sentences don't matter to evaluation
                rel["Arg2"]["TokenList"].append(tok_ids)
                rel["Arg2"]["RawText"] += tok + " "
            if len(rel["Arg2"]["TokenList"]) > 0:
                rel["Arg2"]["CharacterSpanList"] = [[rel["Arg2"]["TokenList"][0][0],
                                                     rel["Arg2"]["TokenList"][-1][1]]]
            else:
                rel["Arg2"]["CharacterSpanList"] = []

            rel["Connective"] = dict()
            rel["Connective"]["TokenList"] = []
            rel["Connective"]["RawText"] = ""
            for i, (num, tok) in enumerate(arg1_toks):
                start, end = tok_info[num]
                tok_ids = [start, end, num, 0, i]
                # putting 0 because sentences don't matter to evaluation
                rel["Connective"]["TokenList"].append(tok_ids)
                rel["Connective"]["RawText"] += tok + " "
            if len(rel["Connective"]["TokenList"]) > 0:
                rel["Connective"]["CharacterSpanList"] = [[rel["Connective"]["TokenList"][0][0],
                                                       rel["Connective"]["TokenList"][-1][1]]]
            else:
                rel["Arg2"]["CharacterSpanList"] = []

            rel_dicts.append(rel)

    with open(conll_path, "w") as conll_file:
        for rel in rel_dicts:
            json.dump(rel, conll_file)
            conll_file.write("\n")


#def pcc_to_conll_dir(pcc_dir, conll_dir):
#    """
#    Wrap pcc_to_conll over directories.
#
#    Parameters:
#    -----------
#    pcc_dir : str
#        Directory containing PCC connectives in xml format.
#    conll_dir : str
#        Directory to save connectives in CoNLL format.
#    """
#
#    if not os.path.exists(conll_dir):
#        os.makedirs(conll_dir)
#
#    for fn in tqdm(os.listdir(pcc_dir)):
#        pcc_path = os.path.join(pcc_dir, fn)
#        conll_path = os.path.join(conll_dir, fn)
#        pcc_to_conll(pcc_path, conll_path)

pcc_to_conll("/data/PotsdamCommentaryCorpus/connectives",
             "/data/PotsdamCommentaryCorpus/conll_connectives.json")

def GSDP_to_conll(gsdp_dir, conll_path):
    """
    Transform relations found by the GermanShallowDiscourseParser
    to the format required by the CoNLL15 scorer.

    Parameters
    ----------
    gsdp_dir : str
        Directory containing original relations.
    conll_path : str
        File to save the transformed relations to.
    """

    new_rels = []
    for fn in os.listdir(gsdp_dir):
        gsdp_path = os.path.join(gsdp_dir, fn)
        with open(gsdp_path) as gsdp_file:
            rels = json.loads(gsdp_file.read())

        for rel in rels:
            nrel = dict()
            nrel["DocID"] = rel["DocID"].split(".")[0] # filename without .tok
            nrel["Arg1"] = dict()
            nrel["Arg1"]["TokenList"] = [quint[2] for quint in rel["Arg1"]["TokenList"]]

            nrel["Arg2"] = dict()
            nrel["Arg2"]["TokenList"] = [quint[2] for quint in rel["Arg2"]["TokenList"]]

            nrel["Connective"] = dict()
            nrel["Connective"]["TokenList"] = [quint[2] for quint in rel["Connective"]["TokenList"]]

            nrel["Sense"] = [rel["Sense"]]
            nrel["Type"] = rel["Type"]

            new_rels.append(nrel)

    with open(conll_path, "w") as conll_file:
        for rel in new_rels:
            json.dump(rel, conll_file)
            conll_file.write("\n")


GSDP_to_conll("/data/pcc_parsed/from_en",
              "/data/pcc_parsed/from_en.json")
