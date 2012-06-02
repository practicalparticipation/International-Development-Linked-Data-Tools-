#!/bin/bash

shopt -s nullglob
for f in *.xml
do
  basename=${f%.*}
  echo "Converting $basename"
  xsltproc ~/scripts/IATI-XSLT/templates/rdf/iati-activities-rdf.xsl $f > $basename.rdf
  echo "Formatting $basename as N-Triples"
  rdfcat -out N-TRIPLE $basename.rdf > $basename.nt
done

#
