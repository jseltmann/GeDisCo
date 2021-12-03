# German Discourse Parsing Corpus

Course project I did under the supervision of Tatjana Scheffler.

## Intro
Discourse Parsing corpora for languages other than English are still small or nonexistent. Annotating them by hand would require many human-hours by people specifically trained for that task. This project attempts to build a German discours corpus. It uses the aligned translations from the Europarl corpus (i.e. containing political speeches). The idea is to parse the English language text and then transfer the relations onto the German text. This should work since the discourse structure of a speech doesn't change during translation. In addition, this project also translates Czech and French texts to English in an attempt to capture more relations, an idea taken from [this paper](https://www.aclweb.org/anthology/W19-2703).
This repository also includes my [course paper](https://raw.githubusercontent.com/jseltmann/GeDisCo/master/gedisco.pdf) (not peer-reviewed) and the [poster](https://raw.githubusercontent.com/jseltmann/GeDisCo/master/poster.pdf) I made.

## Warning
While the approach does basically work (see evaluation in the paper), the English Discourse parser I used, does not produce good enough relations to make a working corpus out of it. In order to get good data, you would have to redo it with a different parser. Alternatively, check out [this paper](https://aclanthology.org/2020.lrec-1.131/) by my fellow student Henny Sluyter-Gäthje, who used the smarter approach of using the PDTB (i.e. with human-annotated discourse relations) and translating its text into German. This should work better than my approach since machine translation is much more advanced than automatic Discourse parsing, although her paper does not test the dataset as much as I do in mine.

## How to create the corpus
### Getting and preparing the europarl text
The functions referenced in this section are all in the file `prepare_data.py`.
1. Download zipped files for the languages you want to use from [Opus](http://opus.nlpl.eu/Europarl.php).
   Unzip them.
2. Use `copy_common()` function to find, which texts the languages have in common and copy them to a new directory.
3. Use `xml_to_txt()` to turn the xml files into tokenized txt and to split them into one file per speech.
### Translate texts into English.
In order to use the Wang/Lan parser, the texts that aren't in English or German, need to be translated into English.
1. Use `append_files()` to join the txt files for one language into one file to be translated by moses.
2. Download [Moses](http://www.statmt.org/moses/RELEASE-4.0/binaries/ubuntu-16.04.tgz). Untar that file.
3. Download a [pretrained model](http://www.statmt.org/moses/RELEASE-4.0/models/). If there are no files there for the language you are using, you will have to train a model from scratch.
   For Czech and French I used:
   * europarl.binlm.1
   * moses.ini.1
   * phrase-table.1
   * reordering-table.1.wbe-msd-bidirectional-fe.gz
   Save these files into one directory (one per language, of course). Unzip reordering-...
   Update the file paths in moses.ini.1 to the locations of the other files.
4. Download the aligned europarl file between English and the language you're trying to translate. Go to [Opus](http://opus.nlpl.eu), select the languages and download the zip file under "Moses". Unzip it, which gives you one file for each language. Use lowercase.perl and tokenizer.perl from the `scripts/tokenizer` directory of the moses download.
5. Copy the file `shell_scripts/call_mert.sh` to the `scripts/training` directory of moses. Update the file paths in it for your setup. Then start it to finetune the model. This eventually creates a new `moses.ini`
6. Go to the `bin` directory of moses. Call moses with your config file and the combined text file you created earlier: `./moses -f path/to/moses.ini -i path/to/comb.txt > trans.txt`
7. Use the `split_translated()` function from `prepare_data.py` to split `trans.txt` into one file per speech again.
### Preprocess text for parsing
The Wang/Lan parser, which we are using to parse the English text, uses the conll-15 input format. So we'll have to transfer the texts first.
1. Clone the repository of the [UNITN Penn Discourse Treebank Discourse Parser](https://github.com/esrel/DP.git). We won't actually be using their parser, but their scripts to transform raw text to the conll json format.
2. Install the [Berkeley Parser](https://github.com/slavpetrov/berkeleyparser) and the [Stanford Parser](http://nlp.stanford.edu/software/lex-parser.shtml).
3. Copy the `txt2json_folder.sh` script into the DP directory. Change the file paths in it to your setup.
4. Call the script like this: `./txt2json_folder.sh inp_dir out_dir err_dir`. `inp_dir` contains the txt files, the json output is saved to `out_dir`. `err_dir` serves to hold txt files for which the scripts produced an error. Since there were very few of them, I ignored these files for the rest of the process.
### Parse the text
1. Clone the repository for the [Wang/Lan-Parser](https://github.com/lanmanok/conll2015_discourse) and follow the installation instructions there.
2. Copy the `call_parser.sh` script to the Wang/Lan-directory. Change the file paths in it according to your setup.
3. Install python2, if you don't have yet. Install the packages according to `requirements_p2.txt`.
4. Happy parsing.
### Get word alignments for the (translated) English and German text
1. Combine the files for the English and German speeches into one file per language, using the `append_files()` function from `prepare_data.py`. Set the `comp_dir` to the directory containing the speeches for the other languages, in order to ignore files that only occur in one language.
2. Clone the [GaChalign](https://github.com/alvations/gachalign.git) repository.
3. Switch into the repository and run the sentence alignment: `python2 gale-church.py /path/to/de_combined /path/to/en_combined gacha > /output/path`.
4. Split the resulting file again, in order to get one file per language (but now sentence-aligned!). Use the `spit_aligned()` function in `alignments.py`for that.
5. Clone the [mgiza](https://github.com/moses-smt/mgiza.git) repository.
6. Follow [these instructions](https://fabioticconi.wordpress.com/2011/01/17/how-to-do-a-word-alignment-with-giza-or-mgiza-from-parallel-corpus/) to get word alignments between the two language files. The files are already tokenized, so you can skip that step. I set the option `deficientdistortionforemptyword` to 1 in the configuration file.
7. Use the function `split_giza_results()` from `alignments.py` to split the results into one file per speech.
8. Do the last two steps also for the other direction, i.e. if you first set German as source and English as target language, then set Engleich as source and German as target now.
9. Use the function `intersection_alignment()` to get only alignments between two words if the alignment occured in both directions.
### "Translate" the found relations to German
1. Use the `transfer_rels()` function from `transfer_rels.py` to replace the English word indices in the parsed relations with word indices from the German text. This also takes care of translating between explicit relations that become implicit and vice versa.
### Combine relations found through different languages
1. Use the `unfiy_langs()` function from `combine_langs.py` to do that.
### Transform the found relations to different formats
Depending on what parser you are using, you might want to transfer the output to a different format.
1. Use `transfer_to_conll_dir()` from `transform_format.py` to transform the output to the conll15 json format. If you do that, you might also want to use the transformation scripts from the UNITN discourse parser on the German text, to get the same input format. You'll have to download the [German models](https://stanfordnlp.github.io/CoreNLP/history.html) for your version of the stanford parser and use the `txt2json_folder_german.sh`.
