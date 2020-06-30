import os
import json


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


transfer_to_conll_dir("/data/europarl/common/transferred/from_en",
                      "/data/europarl/common/txt/de",
                      "/data/europarl/common/conll_labels/from_en")
#transfer_to_conll_dir("/data/europarl/common/test",
#                      "/data/europarl/common/txt/de",
#                      "/data/europarl/common/test2")
