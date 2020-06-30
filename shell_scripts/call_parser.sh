#!/bin/bash

#dir_num="9"
json_dir="/home/users/jseltmann/data/europarl/common/conll/fr" #$dir_num
#json_dir="/home/users/jseltmann/data/europarl/common/test"
#json_dir="/home/users/jseltmann/data/europarl/common/parsed/en_err"
txt_dir="/home/users/jseltmann/data/europarl/common/txt/fr"
work_dir="/home/users/jseltmann/data/europarl/common/work" #$dir_num
#work_dir="/home/users/jseltmann/data/europarl/common/work"
out_dir="/home/users/jseltmann/data/europarl/common/parsed/fr"
#out_dir="/home/users/jseltmann/data/europarl/common/test2"
err_dir="/home/users/jseltmann/data/europarl/common/parsed/fr_err"
#err_dir="/home/users/jseltmann/data/europarl/common/test3"
mem_dir="/home/users/jseltmann/data/europarl/common/parsed/fr_mem"
#mem_dir="/home/users/jseltmann/data/europarl/common/test4"
log_dir="/home/users/jseltmann/data/europarl/common/parsed/fr_log"
#log_dir="/home/users/jseltmann/data/europarl/common/test4"
err_log_dir="/home/users/jseltmann/data/europarl/common/parsed/fr_err_log"
#err_log_dir="/home/users/jseltmann/data/europarl/common/test4"

mkdir $work_dir
mkdir $work_dir"/raw/"

ulimit -Sv 5000000
#. venv/bin/activate

i=0
num_files=`ls $json_dir | wc -l`

for fn in $(ls $json_dir) ; do
    json_path=$json_dir"/"$fn
    fn_txt=$(echo $fn | cut -d'.' -f 1)
    txt_path=$txt_dir"/"$fn_txt".txt"
    out_path=$out_dir"/"$fn_txt
    err_path=$err_dir"/"$fn_txt
    err_log_path=$err_log_dir"/"$fn_txt
    log_path=$log_dir"/"$fn_txt
    mem_path=$mem_dir"/"$fn_txt
    if [ -f $out_path ]; then
        continue
    fi
    if [ -f $err_path ]; then
        continue
    fi
    if [ -f $mem_path ]; then
        continue
    fi
    cp $json_path $work_dir"/pdtb-parses.json"
    cp $txt_path $work_dir"/raw/"

    python2 parser.py $work_dir none $work_dir 2> $work_dir"/err.log" > $work_dir"/out.log"
    #cat $work_dir"/err.log"
    #echo "######################"
    #cat $work_dir"/out.log"
    
    len_err=$(wc $work_dir"/err.log" | cut -d' ' -f 3)
    if [ "$len_err" == "0" ]; then
        num_out_err=$(grep Error $work_dir"/out.log" | wc -l)
        if [ "$num_out_err" == "0" ]; then
            mv $work_dir"/output.json" $out_path
            rm $work_dir"/out.log"
        else
            mv $work_dir"/output.json" $mem_path
            mv $work_dir"/out.log" $log_path
        fi
        rm $work_dir"/err.log"
    else
        cp $json_path $err_path
        mv $work_dir"/err.log" $err_log_path
        rm $work_dir"/out.log"
    fi
    
    #cat $work_dir"/err.log"
    #echo "#######################"
    #cat $work_dir"/out.log"
    #rm $work_dir"/err.log"
    #rm $work_dir"/out.log"
    #rm $work_dir"/raw/"*

    if (( i%100 == 0)); then
        echo $i"/"$num_files
    fi
    i=$(($i+1))
done
