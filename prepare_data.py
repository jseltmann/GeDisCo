import os
import shutil
import xml.etree.ElementTree as ET
import re

def get_europarl_overlap(xml_path, langs):
    """
    Take europarl xml files for several languages from opus,
    and keep those which occur in all languages.

    Parameters
    ----------
    xml_path : str
        Path to the xml directory, containing sub-directories
        for the respective languages.
    langs : [str]
        Directory names of sub-directories for the languages.
    
    Return
    ------
    filenames : set(str)
        Filenames of the dates which the languages have in common.
    """

    lang_paths = [os.path.join(xml_path, lang) for lang in langs]
    filename_sets = [set(os.listdir(lang_path)) for lang_path in lang_paths]
    filenames = filename_sets[0].intersection(*filename_sets[1:])
        
    return filenames


def copy_common(filenames, common_save_path, langs, xml_path):
    """
    Copy xml files which the languages share in common into a new directory.

    Parameters
    ----------
    filenames : set(str)
        Set of common filenames found by get_europarl_overlap().
    common_save_path : str
        Path to save the common xml files to.
    langs : [str]
        Directory names of sub-directories for the languages.
    xml_path : str
        Path to the xml directory, containing sub-directories
        for the respective languages.
    """

    for lang in langs:
        lang_path = os.path.join(xml_path, lang)
        lang_orig_paths = [os.path.join(lang_path, fname) for fname in filenames]
        cp_lang_path = os.path.join(common_save_path, lang)
        if not os.path.exists(cp_lang_path):
            os.makedirs(cp_lang_path)
        for opath in lang_orig_paths:
            shutil.copy(opath, cp_lang_path)


#filenames = get_europarl_overlap("/home/users/jseltmann/data/europarl/Europarl/xml/",
#                                 ["cs", "en", "fr", "de"])
#
#copy_common(filenames, "/home/users/jseltmann/data/europarl/common/xml",
#            ["cs", "en", "fr", "de"], 
#            "/home/users/jseltmann/data/europarl/Europarl/xml/")


def xml_to_txt(xml_path, txt_path):
    """
    Turn xml europarl files into plain text files to use for discourse parsing.
    Create an own file for each speaker in the xml file, 
    but not for the president.
    Additionally, for each txt file, create a file which contains the indices,
    that the sentences in the txt file had in the xml file.
    This is important in order to not lose the information about sentence
    alignment between the various languages.

    Parameters
    ----------
    xml_path : str
        Directory containing the xml files.
    txt_path : str
        Directory to save the plain text files to.
    """

    if not os.path.exists(txt_path):
        os.makedirs(txt_path)

    for fn in os.listdir(xml_path):
        file_path = os.path.join(xml_path,fn)
        try:
            tree = ET.parse(file_path)
        except Exception as e:
            print(fn)
            raise e
        speakers = tree.iter(tag="SPEAKER")
        president_pattern = r"[P|p]räsident|[P|p]resident|[p|P]ředsed|[p|P]résiden"
        for i, speaker in enumerate(speakers):
            if re.search(president_pattern,speaker.attrib['NAME']):
                # exclude things said by the president, since these are not part of the debate
                continue
            sents = list(speaker.iter(tag='s'))
            sent_inds = [s.attrib['id'] for s in sents]
            sents = [s.iter(tag='w') for s in sents]
            sents = [[word.text.lower() for word in s] for s in sents]
            sents = [" ".join(s) for s in sents]

            text_fn = fn[:-4] + "_" + str(i) + ".txt"
            plain_path = os.path.join(txt_path, text_fn)
            with open(plain_path, "w") as plain_file:
                for sent in sents:
                    plain_file.write(sent)
                    plain_file.write("\n")
            inds_fn = fn[:-4] + "_" + str(i) + ".inds"
            inds_path = os.path.join(txt_path, inds_fn)
            with open(inds_path, "w") as inds_file:
                for ind in sent_inds:
                    inds_file.write(ind + "\n")


#for lang in ["en", "de", "fr", "cs"]:
#    xml_to_txt("/home/users/jseltmann/data/europarl/common/xml/" + lang, 
#               "/home/users/jseltmann/data/europarl/common/txt/" + lang)


def clean_txt(txt_dir):
    """
    Clean up small problems in the txt files.

    Parameters
    ----------
    txt_dir : str
        Directory containing the txt files.
    """
    for fn in os.listdir(txt_dir):
        if fn[-4:] == "inds":
            continue
        path = os.path.join(txt_dir, fn)
        with open(path) as txt_file:
            lines = txt_file.readlines()
        with open(path, "w") as txt_file:
            for line in lines:
                # remove whitespaces in numbers, e.g. 12 000 -> 12000
                num_reg = r"([0-9]+[\s|\n|\.])+"
                def num_repl(match):
                    ret_str = match[0]
                    if ret_str[-1] == "\n":
                        ret_str = ret_str[:-1]
                        line_break = True
                    else:
                        line_break = False
                    ret_str = "".join(ret_str.split())
                    if line_break:
                        ret_str += "\n"
                    else:
                        ret_str += " "
                    return ret_str
                
                new_line = re.sub(num_reg, num_repl, line)
                regs = [r"&#93;", r"&#91;", r"&quot;", r"&apos;", r"&amp;", r"@-@"]
                repls = ["]", "[", "„", "\'", "&", "-"]
                for reg, repl in zip(regs, repls):
                    #print(reg, repl)
                    new_line = re.sub(reg, lambda m: repl, new_line)
                txt_file.write(new_line)


clean_txt("/home/users/jseltmann/data/europarl/common/txt/cs_trans")
#clean_txt("/home/users/jseltmann/data/europarl/common/test")


def append_files(txt_dir, combined_path):
    """
    Append txt files into one combined file for better processing by moses.
    Delineate files with lines of "##########" and filenames, so that they
    can be split again.

    Parameters
    ----------
    txt_dir : str
        Directory containing text files to be appended.
    combined_path : str
        Path to save the combined file to.
    """

    with open(combined_path, "w") as comb_file:
        for fn in os.listdir(txt_dir):
            if fn[-4:] == "inds":
                continue
            file_path = os.path.join(txt_dir, fn)
            comb_file.write("##############################" + fn + "\n")
            with open(file_path) as txt_file:
                for line in txt_file:
                    #comb_file.write(line.lower())
                    comb_file.write(line)


#append_files("/home/users/jseltmann/data/europarl/common/txt/fr", "/home/users/jseltmann/data/europarl/common/comb/fr_test.txt")
#append_files("/home/users/jseltmann/data/europarl/common/txt/cs", "/home/users/jseltmann/data/europarl/common/comb/cs.txt")


def remove_long(txt_dir, long_dir=None):
    """
    Remove files that contain sentences with more than 200 words,
    since these can't be parsed by the stanford parser.
    Also remove the corresponding .inds files.

    Parameters
    ----------
    txt_dir : str
        Directory containing the text files.
    long_dir : str or None
        Directory to copy the files to, which contain a line that is too long.
        If None, the files are deleted.
    """

    for fn in os.listdir(txt_dir):
        if fn[-4:] == "inds":
            continue
        old_path = os.path.join(txt_dir, fn)
        with open(old_path) as f:
            lines = f.readlines()
        for line in lines:
            if len(line.split()) > 200:
                old_path_inds = os.path.join(txt_dir, fn[:-3]+"inds")
                if long_dir is not None:
                    new_path = os.path.join(long_dir, fn)
                    os.rename(old_path, new_path)
                    new_path_inds = os.path.join(long_dir, fn[:-3]+"inds")
                    os.rename(old_path_inds, new_path_inds)
                else:
                    os.remove(old_path)
                    os.remove(old_path_inds)
                break


#remove_long("/home/users/jseltmann/data/europarl/common/txt/en", 
#            "/home/users/jseltmann/data/europarl/common/too_long/en")

def split_translated(trans_file_path, trans_dir):
    """
    Split the file produced by the moses translation
    into the individual files for the speeches.

    Parameters
    ----------
    trans_file_path : str
        Path to file containing translations.
    trans_dir : str
        Directory to save the files to.
    """

    hashtag_re = r"########################"
    i = 0
    with open(trans_file_path) as trans_file:
        for line in trans_file:
            if re.match(hashtag_re, line):
                fn = line.split("#")[-1][:-2]
                split_path = os.path.join(trans_dir, fn)
                i += 1
                #if i == 3:
                #    break
            else:
                with open(split_path, "a") as split_file:
                    split_file.write(line)

#split_translated("/home/users/jseltmann/data/europarl/common/comb/cs2_trans.txt",
#                 "/home/users/jseltmann/data/europarl/common/txt/cs_trans/")
