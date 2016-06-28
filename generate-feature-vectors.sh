#!/bin/bash
#./run.sh /data/ntcir2015_lifelogging/NTCIR_Lifelog_Dryrun_Dataset/NTCIR-Lifelog_Dryrun_images/ dryrun-images.txt dryrun-feature-vectors.txt 100 1000 dryrun_clusters
#./run.sh /data/ntcir2015_lifelogging/NTCIR_Lifelog_formal_run_Dataset/NTCIR-Lifelog_formal_run_images/ formal-images.txt formal-feature-vectors.txt 100 1000 formal_clusters
p="processed-"
python feature-vectors/generate-filelist.py $1 $2
./feature-vectors/extractfeatures $2 $3
python feature-vectors/process-fv.py $3 $p$3
