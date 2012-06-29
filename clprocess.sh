#!/bin/bash

cd ~/r4d/data/
wget http://www.dfid.gov.uk/R4D/RDF/R4DOutputsData.zip
unzip R4DOutputsData.zip
mv R4DOutputsData.txt R4DOutputsData.rdf
mv online.nt archive/online.nt
echo "Converting R4D data into nTriples"
rdfcat -out N-TRIPLE R4DOutputsData.rdf > online.nt
echo "Removing zip file"
rm *.zip

echo 
echo
echo "Getting IATI Data"
echo
echo
cd ~/iati/data/
python ~/scripts/IATI/download.py --groups dfid
echo 
echo 
echo "Converting IATI Data"
echo
echo
cd ~/iati/data/packages/dfid/
shopt -s nullglob
for f in *.xml
do
  basename=${f%.*}
  echo "Converting $basename"
  xsltproc ~/scripts/IATI-XSLT/templates/rdf/iati-activities-rdf.xsl $f > $basename.rdf
  echo "Formatting $basename as N-Triples"
  ~/software/Jena/bin/rdfcat -out N-TRIPLE $basename.rdf > $basename.nt
done
echo 
echo
echo "Converting codelists"
python ~/scripts/IATI/codelists.py
echo
echo
echo "If you didn't see too many errors then everything is ready to upload"
echo
echo
echo "Now run clupload.sh to empty and refresh the store"
echo
echo "E.g. ./clupload.sh APIKEY STORENAME"
echo
echo