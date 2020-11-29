import os
import random
from shutil import copyfile
from tqdm import tqdm


def find_common(dirs):
    """
    For a list of directories containing parsed files,
    find the common ones and return their names.

    Parameters
    ----------
    dirs : [str]
        List of directories.

    Return
    ------
    common_fns : [str]
        Names of common files.
    """

    common_fns = os.listdir(dirs[0])
    common_fns = [fn.split(".")[0] for fn in common_fns]

    for dir_name in dirs[1:]:
        fns = os.listdir(dir_name)
        fns = [fn.split(".")[0] for fn in fns]
        common_fns = [fn for fn in common_fns if fn in fns]

    return common_fns


def split(dirs, split_fn, split_fracs=[0.8,0.1,0.1], num_files=None):
    """
    For a list of directories, find the common files
    and split them into train/dev/test.
    Save the split into a file.

    Parameters
    ----------
    dirs : [str]
        List of directories.
    split_fn : str
        Path of a file to which the respective 
        filenames for train/dev/test are saved.
    split_fracs : [float]
        List of fractions to use for train/dev/test split.
    num_files : int or None
        Number of files to use. None for all files.
    """

    common_fns = find_common(dirs)

    random.shuffle(common_fns)
    if not num_files is None:
        common_fns = common_fns[:num_files]
    
    train_cut = int(split_fracs[0] * len(common_fns))
    train_fns = common_fns[:train_cut]

    dev_cut = train_cut + int(split_fracs[1] * len(common_fns))
    dev_fns = common_fns[train_cut:dev_cut]

    test_fns = common_fns[dev_cut:]

    with open(split_fn, "w") as split_file:
        split_file.write("train:\n")
        for fn in train_fns:
            split_file.write(fn + "\n")

        split_file.write("\n\n")
        split_file.write("dev:\n")
        for fn in dev_fns:
            split_file.write(fn + "\n")
        
        split_file.write("\n\n")
        split_file.write("test:\n")
        for fn in test_fns:
            split_file.write(fn + "\n")


dirs = ["/data/europarl/common/transferred/from_cs/",
        "/data/europarl/common/transferred/from_en/",
        "/data/europarl/common/transferred/from_fr/",
        "/data/europarl/common/parsed/en_cs",
        "/data/europarl/common/parsed/en_fr",
        "/data/europarl/common/parsed/cs_fr",
        "/data/europarl/common/parsed/cs_fr_en",
        "/data/europarl/common/txt/de_shortened",
        "/data/europarl/common/syntax/de/tiger"]

#split(dirs, 
#      "/data/europarl/common/split/split_5k.txt", 
#      split_fracs=[0.9,0,0.1],
#      num_files=5000)


def distribute_split(split_fn, dir_to_split, out_dir, file_ending):
    """
    Split a directory of files into train/dev/test parts
    according to the split file created by split().

    Parameters
    ----------
    split_fn : str
        Path to file containing split data.
    dir_to_split : str
        Path to directory containing the files
        which are supposed to be distributed.
    out_dir : str
        Files will be copied into that directory,
        into separate directories for train, dev, and test.
    file_ending : str
        File endings in dir_to_split (e.g. ".txt", ".xml",...)
    """

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    train_dir = os.path.join(out_dir, "train")
    if not os.path.exists(train_dir):
        os.mkdir(train_dir)
    dev_dir = os.path.join(out_dir, "dev")
    if not os.path.exists(dev_dir):
        os.mkdir(dev_dir)
    test_dir = os.path.join(out_dir, "test")
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)

    with open(split_fn) as split_file:
        curr_split = "train"
        cp_dir = train_dir
        for line in tqdm(split_file.readlines()):
            if len(line) < 2:
                continue
            if line[-2] == ":":
                curr_split = line[:-2]
                cp_dir = os.path.join(out_dir, curr_split)
                continue
            fn = line[:-1]
            orig_path = os.path.join(dir_to_split, fn+file_ending)
            cp_path = os.path.join(cp_dir, fn+file_ending)
            copyfile(orig_path, cp_path)
