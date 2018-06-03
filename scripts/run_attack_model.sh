#! /bin/bash


## Graph name, and synthetic graph name as arguments
g=$1
mg=$2


attackModelDir="../attack_model"
dataDir="../dataset/${g}/${mg}"
overlap=0.2
overlap_choice=3
stage="stage"
depth=1
samples=100


mkdir -p ${dataDir}/${stage}/${overlap}/${overlap_choice}/pairs/

## Training Data Preparation
echo -e "\n$stage: recursive split..."
python ${attackModelDir}/RecursiveGraphSampling.py ${dataDir}/${mg}.txt ${dataDir}/${stage} ${overlap} ${overlap_choice} ${depth}
echo "stage: recursive split Done !!"


echo "waiting for scoop...."
python ${attackModelDir}/GenerateFeatures.py ${dataDir}/${stage}/${overlap}/${overlap_choice}/${mg}_1.txt ${dataDir}/${stage}/${overlap}/${overlap_choice}/${mg}_2.txt ${dataDir}/${stage}/${overlap}/${overlap_choice}/${mg}-overlap.txt ${samples} &
wait
echo "stage: node pairs generated. Done !!"




## Random Forest classification
echo -e "\nstage: classification with Random Forest..."


python ${attackModelDir}/RandomForest.py ${dataDir}/${stage}/${overlap}/${overlap_choice}/pairs
echo "stage: classification. Done !!"

echo "waiting for RF monster...."
wait
echo "Done !! RF monster...."