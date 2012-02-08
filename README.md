## IATI to RDF Conversion Scripts

These scripts fetch the latest IATI data from the IATI Registry and convert it to RDF before uploading to Kasabi platform

## Set up
These scripts are currently configured to run in the below directory configuration:

* /iati/scripts - The scripts in here. download.py must be run from here
* /iati/data/packages - Where we can place files fetched via the IATI Registry
* /iata/data/codelists - Where we can place codelists

### Dependencies

Pytassium, ckan, ckanclient, lxml

    easy_install pytassium
	easy_install ckan
	easy_install ckanclient
	easy_install lxml

## Synchronisation process

Run the download script. This read through the IATI Registry, checking the checksum of files against those of files already downloaded. 

    python download.py

Then change to /iati/data/packages/ and run

    python ~/iati/scripts/convert_to_rdf.py

And then

    python ~/iati/scripts/iati_upload.py



**If codelists have additions (see ToDo below):**

    python codelists.py

the change to /iati/codelists and run

    python ~/iati/scripts/iati_upload.py
    

## ToDo

* Codelist sync scripts do not currently hand for changes to codes / definitions. Need to implement proper revision control here. 