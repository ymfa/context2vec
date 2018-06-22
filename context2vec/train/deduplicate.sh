#!/bin/bash

dir=$1
seg_flag=$2
echo $dir


dir_en=$dir.en.DIR
dir_de=$dir.de.DIR
en_de_dir=${dir}.en-de.DIR

if [ ! -d "${en_de_dir}" ]; then
    echo ${en_de_dir}
    mkdir ${en_de_dir}
fi


for filename_en in $dir_en/sent.*

do
    bs=${filename_en##*/}
    echo $bs
    en_de_f=${en_de_dir}/$bs
    paste $filename_en $dir_de/$bs > ${en_de_f}
    #echo $en-de-f
    cat ${en_de_f} | uniq > ${en_de_f}-new
    cat ${en_de_f}-new > $en_de_f
    rm ${en_de_f}-new


done

echo create stats
python deduplicate.py $dir $seg_flag
rm -rf ${en_de_dir}