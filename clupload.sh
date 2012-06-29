#!/bin/bash
echo "Starting by resetting the store and adding the codelists"

python ~/scripts/resetandupload.py --apikey=$1 --dataset=$2 
echo
echo 
echo "Now uploading research data"
cd ~/r4d/data/
python ~/scripts/upload.py --apikey=$1 --dataset=$2 
echo 
echo
echo
echo "Now working on the IATI DFID data"
cd ~/iati/data/packages/dfid/
python ~/scripts/upload.py --apikey=$1 --dataset=$2 
