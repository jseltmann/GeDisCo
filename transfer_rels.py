import os

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
    txt_dir1 : str
        Directory containing texts for the first language.
    txt_dir2 : str
        Directory containing texts for the second language.
    out_dir : str
        Path to save "translated" relations to.
    """

    for fn in os.listdir(parsed_dir):
        parsed_path = os.path.join(parsed_dir, fn)
        align_path = os.path.join(align_dir, fn)
        out_path = os.path.join(out_dir, fn)
        txt1_path = os.path.join(txt_dir1, fn+".txt")
        txt2_path = os.path.join(txt_dir2, fn+".txt")

        alignments = read_alignments(align_path, txt1_path, txt2_path)



def read_alignments(align_path, txt1_path, txt2_path):
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
    txt1_path : str
        Path to file containing the text for language1.
    txt2_path : str
        Path to file containing the text for language2.

    Return
    ------
    alignments : dict(int)
        Dictionary assigning a list of German word indices
        words to each English word index.
    """

    align_tuples = []
    with open(txt1_path) as txt1:
        lines = txt1.readlines()
        sents1 = [line.split() for line in lines]
    with open(txt2_path) as txt2:
        lines = txt2.readlines()
        sents2 = [line.split() for line in lines]

    with open(align_path) as align_file:
        for line in align_file:
            algmts = line[:-1].split(" ")
            algmts = [al.split("-") for al in algmts]
            algmts = [(int(al[0]), int(al[1])) for al in algmts]
            align_tuples.append(algmts)

    word_counts = (0,0)
    tuples_doc_indices = []
    for i, sent_tuples in enumerate(align_tuples):
        for j in range(len(sent_tuples)):
            sent_tuples[j][0] += word_counts[0]
            sent_tuples[j][1] += word_counts[1]
        tuples_doc_indices += sent_tuples
        
        word_counts[0] += len(sents1[i])
        word_counts[1] += len(sents2[i])

    alignments = dict()
    for de, en in tuples_doc_indices:
        if en in alignments:
            alignments[en].append(de)
        else:
            alignments[en] = [de]

    return alignments
