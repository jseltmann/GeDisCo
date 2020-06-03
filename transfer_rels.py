import os
import json


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
                if en in alignments:
                    alignments[en].append(de)
                else:
                    alignments[en] = [de]

    return alignments


def translate_parsed(parsed_dir, align_dir, txt_dir1, txt_dir2, out_dir):
    """
    Take output of English parser.
    Replace indices of words with corresponding word
    indices of the German text.

    Parameters
    ----------
    parsed_dir : str
        Path to directory containing parsed texts.
    align_dir : str
        Path to directory containing alignments.
    out_dir : str
        Path to save "translated" relations to.
    """

    parsed_fns = os.listdir(parsed_dir)
    for fn in os.listdir(align_dir):
        if not fn[:-4] in parsed_fns:
            continue
        parsed_path = os.path.join(parsed_dir, fn[:-4])
        align_path = os.path.join(align_dir, fn)
        out_path = os.path.join(out_dir, fn[:-4])

        alignments = read_alignments(align_path)

        with open(parsed_path) as parsed_f, open(out_path, "w") as out_f:
            for line in parsed_f:
                as_dict = json.loads(line)
                arg1_list = as_dict['Arg1']['TokenList']
                arg1_new = [alignments[n] for n in arg1_list if n in alignments]
                as_dict['Arg1']['TokenList'] = arg1_new
                arg2_list = as_dict['Arg2']['TokenList']
                arg2_new = [alignments[n] for n in arg2_list if n in alignments]
                arg2_new = [n for n_list in arg2_new for n in n_list]
                as_dict['Arg2']['TokenList'] = arg2_new
                connec_list = as_dict['Connective']['TokenList']
                connec_new = [alignments[n] for n in connec_list if n in alignments]
                as_dict['Connective']['TokenList'] = connec_new
                out_f.write(str(as_dict))
                out_f.write("\n")


translate_parsed("/data/europarl/common/parsed/en",
                 "/data/europarl/common/word_aligned/de_en_intersection",
                 "/data/europarl/common/transfered_rels/en")
