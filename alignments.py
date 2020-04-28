import os
import xml.etree.ElementTree as ET
import re
from tqdm import tqdm


def split_align_file_docs(sent_align_path, word_align_path, split_dir):
    """
    Split the word alignment file into smaller files 
    each corresponding to one europarl file.

    Parameters
    ----------
    sent_align_path : str
        Xml file containing sentence alignments of the corpora.
    word_align_path : str
        File containing the word alignments for every sentence pair.
    split_dir : str
        Directory to save split files to.
    """

    tree = ET.parse(sent_align_path)
    docs = tree.iter(tag="linkGrp")
    with open(word_align_path) as word_align_file:
        #align_lines = word_align_file.readlines()
        for doc in tqdm(docs):
            fn = doc.attrib["fromDoc"][3:-7]
            links = list(doc.iter(tag="link"))
            num_sents = len(links)
            #curr_lines = align_lines[:num_sents]
            out_path = os.path.join(split_dir, fn)
            with open(out_path, "w") as out_file:
                for i, line in enumerate(word_align_file):
                    out_file.write(line)
                    if i == num_sents - 1:
                        break

split_align_file_docs("/home/johann/Studium/IM/data/Europarl/smt/de-en/bitext.xml",
                      "/home/johann/Studium/IM/data/Europarl/smt/de-en/model/aligned.intersection",
                      "/home/johann/Studium/IM/data/europarl/alignments/en_full_intersection")

def intersection_alignment(src2tgt_path, tgt2src_path, intersection_path):
    """
    Get intersection of word alignments for two directions.

    Parameters
    ----------
    src2tgt_path : str
        Alignment file in one direction.
    tgt2src_path : str
        Alignment file in other direction.
    intersection_path : str
        File to save intersection to.
    """

    with open(src2tgt_path) as s2t_file, \
            open(tgt2src_path) as t2s_file, \
            open(intersection_path, "w") as int_file:
        for s2t_line, t2s_line in zip(s2t_file, t2s_file):
            s2t = s2t_line.split()
            s2t = [a.split("-") for a in s2t]
            s2t = [(int(i),int(j)) for (i,j) in s2t]

            t2s = t2s_line.split()
            t2s = [a.split("-") for a in t2s]
            t2s = [(int(i),int(j)) for (i,j) in t2s]

            inter = [tup for tup in s2t if tup in t2s]
            inter = [str(i) + "-" + str(j) for (i,j) in inter]
            inter = " ".join(inter)
            int_file.write(inter)
            int_file.write("\n")


#intersection_alignment("/home/johann/Studium/IM/data/Europarl/smt/de-en/model/aligned.srctotgt", 
#        "/home/johann/Studium/IM/data/Europarl/smt/de-en/model/aligned.tgttosrc", 
#        "/home/johann/Studium/IM/data/Europarl/smt/de-en/model/aligned.intersection")
