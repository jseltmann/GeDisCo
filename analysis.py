import os
from lxml import etree
from tqdm import tqdm
import collections as col
import json
import random


def analyze_dir(to_analyze, txt_dir, res_path):
    """
    Analyze dataset in one directory.

    Parameters
    ----------
    to_analyze : str
        Path to directory for which to do the analysis.
    txt_dir : str
        Path to directory containing text files.
    res_path : str
        Path to write results to.
    """

    sense_counts = dict()
    num_relations = 0
    num_texts = 0
    num_explicit = 0
    num_implicit = 0
    num_other_types = 0
    one_sent = 0
    both_sents = 0
    conn_in_arg = 0
    num_words = 0
    doc_empt_arg = 0
    rel_empt_arg = 0
    rels_doc_with_empt = 0

    for fn in tqdm(os.listdir(to_analyze)):
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

        num_texts += 1
        num_words += word_count

        empt_in_doc = False
        json_path = os.path.join(to_analyze, fn)
        with open(json_path) as json_file:
            lines = json_file.readlines()
        for line in lines:
            relation = json.loads(line)
            num_relations += 1

            sense = relation["Sense"][0]
            if sense in sense_counts:
                sense_counts[sense] += 1
            else:
                sense_counts[sense] = 1

            c_inds = set(relation["Connective"]["TokenList"])
            i_inds = set(relation["Arg1"]["TokenList"])
            e_inds = set(relation["Arg2"]["TokenList"])

            if len(e_inds) == 0 or len(i_inds) == 0:
                rel_empt_arg += 1
                empt_in_doc = True

            def set_add(s1, s2):
                for el in s2:
                    s1.add(el)
                return s1

            if relation["Type"] == "Implicit":
                num_implicit += 1
                if i_inds in sent_inds and e_inds in sent_inds:
                    both_sents += 1
                elif set_add(i_inds, c_inds) in sent_inds and e_inds in sent_inds:
                    both_sents += 1
                elif i_inds in sent_inds and set_add(e_inds, c_inds) in sent_inds:
                    both_sents += 1
                else:
                    # one of the arguments could still be a sentence
                    if i_inds in sent_inds or set_add(i_inds, c_inds) in sent_inds:
                        one_sent += 1
                    elif e_inds in sent_inds or set_add(e_inds, c_inds) in sent_inds:
                        one_sent += 1
            elif relation["Type"] == "Explicit":
                num_explicit += 1
                arg_inds = set_add(i_inds, e_inds)
                if c_inds.issubset(arg_inds):
                    conn_in_arg += 1
            else:
                num_other_types += 1

        if empt_in_doc:
            rels_doc_with_empt += len(lines)
            doc_empt_arg += 1

    with open(res_path, "w") as res_file:
        res_file.write("analyzed directory: " + to_analyze + "\n")
        res_file.write("number of documents: " + str(num_texts) + "\n")
        res_file.write("number of words: " + str(num_words) + "\n")
        res_file.write("number of relations: "+ str(num_relations) + "\n")
        if num_texts > 0:
            frac_docs = float(num_relations) / float(num_texts)
            res_file.write("relations per document: " + str(frac_docs) + "\n")
        else:
            res_file.write("relations per document: \n")
        if num_words > 0:
            frac_words = float(num_relations) / float(num_words)
            res_file.write("relations per word: " + str(frac_words) + "\n")
        else:
            res_file.write("relations per word: \n")

        res_file.write("\n#### Senses ####\n")
        for sense in sorted(sense_counts.keys()):
            if num_relations > 0:
                frac = float(sense_counts[sense]) / float(num_relations)
                res_file.write(sense + ": " + str(frac) + "\n")
            else:
                res_file.write(sense + ": \n")
        res_file.write("\n")
        if num_relations > 0:
            frac_impl = float(num_implicit) / float(num_relations)
            res_file.write("fraction implicit: " + str(frac_impl) + "\n")
            frac_expl = float(num_explicit) / float(num_relations)
            res_file.write("fraction explicit: " + str(frac_expl) + "\n")
        else:
            res_file.write("fraction implicit: \n")
            res_file.write("fraction explicit: \n")

        res_file.write("\n#### Arguments ####\n")
        if num_implicit > 0:
            frac_one_sent = float(one_sent) / float(num_implicit)
            res_file.write("Fraction of implicit where one argument ")
            res_file.write("is a sentence: " + str(frac_one_sent) + "\n")
            frac_both_sent = float(both_sents) / float(num_implicit)
            res_file.write("Fraction of implicit where both arguments ")
            res_file.write("are sentences: " + str(frac_both_sent) + "\n")
        else:
            res_file.write("Fraction of implicit where one argument ")
            res_file.write("is a sentence: \n")
            res_file.write("Fraction of implicit where both arguments ")
            res_file.write("are sentences: \n")
        
        if num_explicit > 0:
            frac_conn_in_arg = float(conn_in_arg) / float(num_explicit)
            res_file.write("\nFraction of explicit where the connective")
            res_file.write(" is also part of one or both arguments: ")
            res_file.write(str(frac_conn_in_arg) + "\n")
        else:
            res_file.write("\nFraction of explicit where the connective")
            res_file.write(" is also part of one or both arguments: \n")

        res_file.write("\n#####Relations with empty arguments####\n")
        res_file.write("number: " + str(rel_empt_arg) + "\n")
        frac_of_rels = str(float(rel_empt_arg) / float(num_relations))
        res_file.write("fraction: " + frac_of_rels  + "\n")
        res_file.write("#docs with empty args: " + str(doc_empt_arg) + "\n")
        frac_of_docs = str(float(doc_empt_arg) / float(num_texts))
        res_file.write("fraction: " + frac_of_docs  + "\n")
        if rels_doc_with_empt > 0:
            frac_empt_in_empt_docs = str(float(rel_empt_arg) /
                                         float(rels_doc_with_empt))
        else:
            frac_empt_in_empt_docs = ""
        res_file.write("fraction of empty among rels in docs with empty: " + 
                frac_empt_in_empt_docs + "\n")


#analyze_dir("/data/europarl/common/transferred/from_en",
#            "/data/europarl/common/txt/de",
#            "/data/europarl/common/analysis/corpora/from_en.txt")
#analyze_dir("/data/europarl/common/transferred/from_cs",
#            "/data/europarl/common/txt/de",
#            "/data/europarl/common/analysis/corpora/from_cs.txt")
#analyze_dir("/data/europarl/common/transferred/from_fr",
#            "/data/europarl/common/txt/de",
#            "/data/europarl/common/analysis/corpora/from_fr.txt")
#analyze_dir("/data/europarl/common/transferred/en_cs",
#            "/data/europarl/common/txt/de",
#            "/data/europarl/common/analysis/corpora/en_cs.txt")
#analyze_dir("/data/europarl/common/transferred/en_fr",
#            "/data/europarl/common/txt/de",
#            "/data/europarl/common/analysis/corpora/en_fr.txt")
#analyze_dir("/data/europarl/common/transferred/cs_fr",
#            "/data/europarl/common/txt/de",
#            "/data/europarl/common/analysis/corpora/cs_fr.txt")
#analyze_dir("/data/europarl/common/transferred/cs_fr_en",
#            "/data/europarl/common/txt/de",
#            "/data/europarl/common/analysis/corpora/cs_fr_en.txt")


def analyze_dir_pcc(to_analyze, txt_dir, res_path):
    """
    Analyze dataset in one directory, but work on PCC xml files.

    Parameters
    ----------
    to_analyze : str
        Path to directory for which to do the analysis.
    txt_dir : str
        Path to directory containing text files.
    res_path : str
        Path to write results to.
    """

    sense_counts = dict()
    num_relations = 0
    num_texts = 0
    num_explicit = 0
    num_implicit = 0
    num_other_types = 0
    one_sent = 0
    both_sents = 0
    conn_in_arg = 0
    num_words = 0
    doc_empt_arg = 0
    rel_empt_arg = 0
    rels_doc_with_empt = 0

    for fn in tqdm(os.listdir(to_analyze)):
        txt_path = os.path.join(txt_dir, fn.split(".")[0] + ".tok")
        with open(txt_path) as txt_file:
            lines = txt_file.readlines()
            sents = [line.split() for line in lines]
            sent_inds = []
            word_count = 0
            for sent in sents:
                inds = set([i + word_count for i in range(len(sent))])
                sent_inds.append(inds)
                word_count += len(sent)

        num_texts += 1
        num_words += word_count

        xml_path = os.path.join(to_analyze, fn)
        tree = etree.parse(xml_path)
        relations = tree.findall(".//relation")
        empt_in_doc = False
        for relation in relations:
            num_relations += 1

            if "pdtb3_sense" in relation.attrib:
                sense = relation.attrib["pdtb3_sense"]
            else:
                sense = "None"
            sense_levels = sense.split(".")
            if len(sense_levels) > 2 and sense_levels[2].startswith("Arg"):
                sense = sense_levels[0] + "." + sense_levels[1]
            if sense in sense_counts:
                sense_counts[sense] += 1
            else:
                sense_counts[sense] = 1

            if relation.attrib["type"] == "explicit":
                ct = relation.find("connective_tokens")
                c_inds = set([t.attrib["id"] for t in ct])
            else:
                c_inds = set()
            it = relation.find("int_arg_tokens")
            i_inds = set([t.attrib["id"] for t in it])
            et = relation.find("ext_arg_tokens")
            e_inds = set([t.attrib["id"] for t in et])

            if len(e_inds) == 0 or len(i_inds) == 0:
                rel_empt_arg += 1
                empt_in_doc = True

            def set_add(s1, s2):
                for el in s2:
                    s1.add(el)
                return s1

            if relation.attrib["type"] == "implicit":
                num_implicit += 1
                if i_inds in sent_inds and e_inds in sent_inds:
                    both_sents += 1
                elif set_add(i_inds, c_inds) in sent_inds and e_inds in sent_inds:
                    both_sents += 1
                elif i_inds in sent_inds and set_add(e_inds, c_inds) in sent_inds:
                    both_sents += 1
                else:
                    # one of the arguments could still be a sentence
                    if i_inds in sent_inds or set_add(i_inds, c_inds) in sent_inds:
                        one_sent += 1
                    elif e_inds in sent_inds or set_add(e_inds, c_inds) in sent_inds:
                        one_sent += 1
            elif relation.attrib["type"] == "explicit":
                num_explicit += 1
                arg_inds = set_add(i_inds, e_inds)
                if c_inds.issubset(arg_inds):
                    conn_in_arg += 1
            else:
                num_other_types += 1

        if empt_in_doc:
            rels_doc_with_empt += len(lines)
            doc_empt_arg += 1

    with open(res_path, "w") as res_file:
        res_file.write("analyzed directory: " + to_analyze + "\n")
        res_file.write("number of documents: " + str(num_texts) + "\n")
        res_file.write("number of words: " + str(num_words) + "\n")
        res_file.write("number of relations: "+ str(num_relations) + "\n")
        if num_texts > 0:
            frac_docs = float(num_relations) / float(num_texts)
            res_file.write("relations per document: " + str(frac_docs) + "\n")
        else:
            res_file.write("relations per document: \n")
        if num_words > 0:
            frac_words = float(num_relations) / float(num_words)
            res_file.write("relations per word: " + str(frac_words) + "\n")
        else:
            res_file.write("relations per word: \n")

        res_file.write("\n#### Senses ####\n")
        for sense in sorted(sense_counts.keys()):
            if num_relations > 0:
                frac = float(sense_counts[sense]) / float(num_relations)
                res_file.write(sense + ": " + str(frac) + "\n")
            else:
                res_file.write(sense + ": \n")
        res_file.write("\n")
        if num_relations > 0:
            frac_impl = float(num_implicit) / float(num_relations)
            res_file.write("fraction implicit: " + str(frac_impl) + "\n")
            frac_expl = float(num_explicit) / float(num_relations)
            res_file.write("fraction explicit: " + str(frac_expl) + "\n")
        else:
            res_file.write("fraction implicit: \n")
            res_file.write("fraction explicit: \n")

        res_file.write("\n#### Arguments ####\n")
        if num_implicit > 0:
            frac_one_sent = float(one_sent) / float(num_implicit)
            res_file.write("Fraction of implicit where one argument ")
            res_file.write("is a sentence: " + str(frac_one_sent) + "\n")
            frac_both_sent = float(both_sents) / float(num_implicit)
            res_file.write("Fraction of implicit where both arguments ")
            res_file.write("are sentences: " + str(frac_both_sent) + "\n")
        else:
            res_file.write("Fraction of implicit where one argument ")
            res_file.write("is a sentence: \n")
            res_file.write("Fraction of implicit where both arguments ")
            res_file.write("are sentences: \n")
        
        if num_explicit > 0:
            frac_conn_in_arg = float(conn_in_arg) / float(num_explicit)
            res_file.write("\nFraction of explicit where the connective")
            res_file.write(" is also part of one or both arguments: ")
            res_file.write(str(frac_conn_in_arg) + "\n")
        else:
            res_file.write("\nFraction of explicit where the connective")
            res_file.write(" is also part of one or both arguments: \n")

        res_file.write("\n#####Relations with empty arguments####\n")
        res_file.write("number: " + str(rel_empt_arg) + "\n")
        frac_of_rels = str(float(rel_empt_arg) / float(num_relations))
        res_file.write("fraction: " + frac_of_rels  + "\n")
        res_file.write("#docs with empty args: " + str(doc_empt_arg) + "\n")
        frac_of_docs = str(float(doc_empt_arg) / float(num_texts))
        res_file.write("fraction: " + frac_of_docs  + "\n")
        if rels_doc_with_empt > 0:
            frac_empt_in_empt_docs = str(float(rel_empt_arg) /
                                         float(rels_doc_with_empt))
        else:
            frac_empt_in_empt_docs = ""
        res_file.write("fraction of empty among rels in docs with empty: " + 
                frac_empt_in_empt_docs + "\n")


#analyze_dir_pcc("/data/PotsdamCommentaryCorpus/connectives",
#                "/data/PotsdamCommentaryCorpus/tokenized",
#                "/data/europarl/common/analysis/corpora/pcc.txt")


def analyze_transfer(orig_dir, trans_dir, out_path):
    """
    Analyze differences produced by transferring to German text.

    Parameters
    ----------
    orig_dir : str
        Path to directory containing relations 
        parsed from English or translated text.
    trans_dir : str
        Path to directory containing transferred relations.
    out_path : str
        Path to write results to.
    """

    orig_fns = os.listdir(orig_dir)
    trans_fns = os.listdir(trans_dir)
    common_fns = [fn for fn in orig_fns if fn in trans_fns]

    e2e = col.defaultdict(int)
    e2i = col.defaultdict(int)
    i2i = col.defaultdict(int)
    i2e = col.defaultdict(int)

    losti = col.defaultdict(int)
    loste = col.defaultdict(int)

    for fn in tqdm(common_fns):
        orig_path = os.path.join(orig_dir, fn)
        rels_orig_ex = []
        rels_orig_im = []
        with open(orig_path) as orig_file:
            for line in orig_file:
                rel = json.loads(line)
                if rel["Type"] == "Explicit":
                    rels_orig_ex.append(rel)
                else:
                    rels_orig_im.append(rel)
        
        trans_path = os.path.join(trans_dir, fn)
        rels_trans_ex = dict()
        rels_trans_im = dict()
        with open(trans_path) as trans_file:
            for line in trans_file:
                rel = json.loads(line)
                i = rel["ID"]
                if rel["orig_type"] == "Explicit":
                    rels_trans_ex[i] = rel
                else:
                    rels_trans_im[i] = rel

        pairs = []
        for rel in rels_orig_ex:
            i = rel["ID"]
            if not i in rels_trans_ex:
                loste[rel["Sense"][0]] += 1
                continue
            rel_trans = rels_trans_ex[i]
            pairs.append((rel, rel_trans))
        for rel in rels_orig_im:
            i = rel["ID"]
            if not i in rels_trans_im:
                losti[rel["Sense"][0]] += 1
                continue
            rel_trans = rels_trans_im[i]
            pairs.append((rel, rel_trans))

        for ro, rt in pairs:
            sense = ro["Sense"][0]
            if ro["Type"] == rt["Type"] == "Explicit":
                e2e[sense] += 1
            elif ro["Type"] == "Explicit":
                e2i[sense] += 1
            elif ro["Type"] == rt["Type"] == "Implicit":
                i2i[sense] += 1
            else:
                i2e[sense] += 1
    
    total_all = sum(e2e.values()) + sum(e2i.values()) + sum(i2i.values()) + sum(i2e.values())

    outs = "Transfer relations analysis:\n"
    outs += "original files: " + orig_path + "\n"
    outs += "transferred files: " + trans_path + "\n\n\n"
    outs += "Explicit to Explicit: \n"
    total = sum(e2e.values())
    frac = total / total_all
    outs += "total: {:.4f} \t {:.4f} \n".format(total, frac)
    for sense in sorted(e2e.keys()):
        curr_num = e2e[sense]
        frac_e2e = curr_num / total
        frac_all = curr_num / total_all
        outs += sense + ":\t\t\t{0}\t{1:.4f}\t{2:.4f} \n".format(curr_num, frac_e2e, frac_all)
    outs += "\n\n"

    outs += "Explicit to Implicit: \n"
    total = sum(e2i.values())
    frac = total / total_all
    outs += "total: {:.4f} \t {:.4f} \n".format(total, frac)
    for sense in sorted(e2i.keys()):
        curr_num = e2i[sense]
        frac_e2i = curr_num / total
        frac_all = curr_num / total_all
        outs += sense + ":\t\t\t{0}\t{1:.4f}\t{2:.4f} \n".format(curr_num, frac_e2i, frac_all)
    outs += "\n\n"

    outs += "Implicit to Implicit: \n"
    total = sum(i2i.values())
    frac = total / total_all
    outs += "total: {:.4f} \t {:.4f} \n".format(total, frac)
    for sense in sorted(i2i.keys()):
        curr_num = i2i[sense]
        frac_i2i = curr_num / total
        frac_all = curr_num / total_all
        outs += sense + ":\t\t\t{0}\t{1:.4f}\t{2:.4f} \n".format(curr_num, frac_i2i, frac_all)
    outs += "\n\n"

    outs += "Implicit to Explicit: \n"
    total = sum(i2e.values())
    frac = total / total_all
    outs += "total: {:.4f} \t {:.4f} \n".format(total, frac)
    for sense in sorted(i2e.keys()):
        curr_num = i2e[sense]
        frac_i2e = curr_num / total
        frac_all = curr_num / total_all
        outs += sense + ":\t\t\t{0}\t{1:.4f}\t{2:.4f} \n".format(curr_num, frac_i2e, frac_all)
    outs += "\n\n"

    outs += "Implicit relations removed because an argument was empty:\n"
    outs += "total: " + str(sum(losti.values())) + "\n"
    for sense in sorted(losti.keys()):
        outs += sense + ": " + str(losti[sense]) + "\n"
    outs += "\n\n"

    outs += "Explicit relations removed because an argument was empty:\n"
    outs += "total: " + str(sum(loste.values())) + "\n"
    for sense in sorted(loste.keys()):
        outs += sense + ": " + str(loste[sense]) + "\n"
    outs += "\n\n"

    with open(out_path, "w") as out_file:
        out_file.write(outs)


#analyze_transfer("/data/europarl/common/parsed/en",
#                 "/data/europarl/common/transferred/from_en",
#                 "/data/europarl/common/analysis/transfer/en")
#analyze_transfer("/data/europarl/common/parsed/fr",
#                 "/data/europarl/common/transferred/from_fr",
#                 "/data/europarl/common/analysis/transfer/fr")
#analyze_transfer("/data/europarl/common/parsed/cs",
#                 "/data/europarl/common/transferred/from_cs",
#                 "/data/europarl/common/analysis/transfer/cs")


def choose_manual_files(split_fn, chosen_fn, n=100):
    """
    Randomly choose files for manual evaluation.

    Parameters
    ----------
    split_fn : str
        Path to file containing filenames in train/dev/test split.
    chosen_fn : str
        Path to save chosen filenames to.
    n : int
        Number of files to choose.
    """

    fns = []
    with open(split_fn) as split_file:
        for line in split_file:
            if len(line) < 2 or line[-2] == ":":
                continue
            fns.append(line.strip())

    chosen_fns = random.sample(fns, n)

    with open(chosen_fn, "w") as chosen_file:
        for fn in chosen_fns:
            chosen_file.write(fn + "\n")

choose_manual_files("/data/europarl/common/split/split_no_dev.txt",
                    "/data/europarl/common/split/manual_fns.txt")
