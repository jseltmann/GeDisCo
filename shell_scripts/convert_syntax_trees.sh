in_dir="/data/europarl/common/syntax/de/berkeley"
out_dir="/data/europarl/common/syntax/de/tiger"

i=0
num_files=`ls $in_dir | wc -l`

for fn in $(ls $in_dir) ; do
    if (( i%1000 == 0)); then
        echo $i"/"$num_files
    fi
    i=$(($i+1))

    in_path="${in_dir}/${fn}"
    fn=$(echo $fn | cut -d'.' -f 1)
    out_path="${out_dir}/${fn}.xml"
    convert_treebank $in_path berkeley tiger > $out_path
done
