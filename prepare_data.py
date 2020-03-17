import os
import shutil
import xml.etree.ElementTree as ET

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
        tree = ET.parse(file_path)
        sents = tree.iter(tag='s')
        sents = [s.iter(tag='w') for s in sents]
        sents = [" ".join(word.text) for s in sents for word in s]

        plain_path = os.path.join(txt_path, fn)
        with open(plain_path, "w") as plain_file:
            for sent in sents:
                plain_file.write(sent)
                plain_file.write("\n")


xml_to_txt("/home/users/jseltmann/data/europarl/common/xml/en", 
           "/home/users/jseltmann/data/europarl/common/txt/en")
