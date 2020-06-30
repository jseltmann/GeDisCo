#!/bin/bash

# raw text to json for discourse parsing

###
# PATHS:
# Berkeley Parser command
BP='java -jar ../berkeleyparser/BerkeleyParser-1.7.jar -gr ../berkeleyparser/eng_sm6.gr'
# Stanford constituency to dependency conversion command
SC='java -cp ../stanfordparser/stanford-parser-full-2018-10-17/stanford-parser.jar:../stanfordparser/stanford-english-corenlp-2018-10-05-models.jar edu.stanford.nlp.trees.EnglishGrammaticalStructure -basic -treeFile'
# Tokenization command
TK='java -cp ../stanfordparser/stanford-parser-full-2018-10-17/stanford-parser.jar edu.stanford.nlp.process.DocumentPreprocessor'

sdir='scripts'

#raw=$1 #raw text file
out=tmp
in_dir=$1
out_dir=$2
err_dir=$3

i=0
num_files=`ls $in_dir | wc -l`
for raw in $(ls $in_dir) ; do
    filetype=$(echo $raw | cut -d'.' -f 2)
    if [[ $filetype == "inds" ]]; then
        continue
    fi
    
    if (( i%1000 == 0)); then
        echo $i"/"$num_files
    fi
    i=$(($i+1))

    full_path="${in_dir}/${raw}"
    filename=$(echo $raw | cut -d'.' -f 1)
    out_path="${out_dir}/${filename}.json"
    if [ -f $out_path ]; then
        continue
    fi
    err_path="${err_dir}/${filename}.json"
    if [ -f $err_path ]; then
        continue
    fi

    rm $out.tok
    rm $out.err
    while IFS= read -r line; do
            echo $line > $out.line
            $TK $out.line >> $out.tok 2>/dev/null
    done < $full_path
    $BP < $out.tok > $out.ptree
    $SC $out.ptree > $out.dep
    break
    
    php $sdir/txt2json.php -r $full_path -t $out.tok -p $out.ptree -d $out.dep > $out.json 2> $out.err
    len_err=$(wc $out.err | cut -d' ' -f 3)
    if [ $len_err == 0 ]; then
        mv $out.json $out_path
    else
        mv $out.json $err_path
        #cat $out.err
    fi
    touch $out.err
    
done
