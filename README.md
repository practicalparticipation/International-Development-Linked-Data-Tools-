# IATI and R4D Conversion Scripts

## Set up

These scripts have been developed and tested as root on a Turnkey Linux Core server image (Ubuntu 10.04 LTS). 

They should be cloned to /root/scripts/

### Dependencies

Pytassium, ckan, ckanclient, lxml, argparse

    easy_install pytassium
	easy_install ckan
	easy_install ckanclient
	easy_install lxml
	easy_install argparse


## IATI to RDF Conversion Scripts

These scripts fetch the latest IATI data from the IATI Registry and convert it to RDF before uploading to Kasabi platform. When re-run they check for changes to the data, and upload a changeset rather than original file, managing additions and removals. Changeset are archived. 

### Synchronisation process

Run the download script. This read through the IATI Registry, checking the checksum of files against those of files already downloaded. 

    python ~/scripts/IATI/download.py

To just download a particular donors files add **--groups groupname** as a parameter. E.g. 

    python download.py --groups dfid wb

To just fetch packages from DFID and the World Bank.

Then change to ~/iati/data/packages/ and run

    python ~/scripts/IATI/convert_to_rdf.py

And then

    python ~/iati/scripts/upload.py --apikey=APIKEY --dataset=DATASET

Where APIKEY is your API Key from Kasabi.com and DATASET is the slug of the store you want to add data to. 

**If codelists have additions (see ToDo below):**

    python ~/scripts/IATI/codelists.py

the change to /iati/codelists and run

    python ~/scripts/IATI/iati_upload.py


## R4D scripts

These scripts convert the RDFXML RDF Dump from Research for Development to N3 and manage the creation of changesets to upload to Kasabi. 

### To use

Place the latest RDF dump into the ~/r4d/data/ folder with a .xml extension 

Run 

    python ~/scripts/R4D/process.py

This should convert the file and generate changesets. You can then run:

    python ~/scripts/upload.py --apikey=APIKEY --dataset=DATASET

From the ~/r4d/data/ directory where APIKEY is your API Key from Kasabi.com and DATASET is the slug of the store you want to add data to. 


# ToDo

* Updated the RDF model (possibly to convert direct to N3 so we can avoid conversion in the script to speed things up)
* Update so this does not rely on running as root
* IATI Codelist sync scripts do not currently hand for changes to codes / definitions. Need to implement proper revision control here. 
* Update the upload script to perform better logging, and to note when a .nt has not changed since last upload in order to not duplicate uploads
* Provide this all as a Turnkey Backup image anyone can grab a copy of (or similar)
* Work out how to schedule this to run weekly/monthly firing up a server and shutting it off when done
