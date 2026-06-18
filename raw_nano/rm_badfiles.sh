for file in files/* ; do
    flag=$( tail -c 26 $file )
    if [[ X$flag == X ]] ; then
        echo REMOVING $file
        rm $file
    fi
done
