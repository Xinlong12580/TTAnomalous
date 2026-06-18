input_file=$1
year=$2
output_file=$3
n_files=$4
extra=$5

echo $input_file
ntotal_files=$(wc -l < $input_file)
echo $ntotal_files
i=0
#if [[ $input_file == *"QCD"* && $input_file != *"skimmed"* ]]; then
#    ((ntotal_files = ntotal_files / 3 )) #storage space limited, can't handle all, and QCD is not important 
#fi
while ((( i * n_files ) <  ntotal_files )); do
    echo -d $input_file -y $year -n $n_files -i $i $extra >> $output_file
    (( i++ ))
    #echo $i
done
