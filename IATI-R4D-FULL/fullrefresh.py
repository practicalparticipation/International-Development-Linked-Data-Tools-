# For running a full refresh of the KASABI-IATI Triple Store
import sys, os, fnmatch, math, argparse, zipfile, urllib, ckan, pytassium, hashlib
from time import gmtime, strftime
from datetime import date
from rdflib.parser import StringInputSource
from rdflib.compare import to_isomorphic, graph_diff
from rdflib import Graph
from rdfchangesets import ChangeSet, BatchChangeSet
from lxml import etree

# file_location = "http://www.dfid.gov.uk/R4D/RDF/R4DOutputsData.zip"
R4DLocation = "http://www.practicalparticipation.co.uk/tools/R4DOutputsData.zip"

parser = argparse.ArgumentParser(description='Upload data to KASABI')
parser.add_argument('--dataset', dest='dataset', type=str, nargs=1, 
                   help='The dataset to upload to')
parser.add_argument('--apikey', dest='apikey', type=str, nargs=1, 
                   help='API Key')
args = parser.parse_args()


def R4DdownloadFile(url):
	print "Downloading File"
	webFile = urllib.urlopen(url)
	localFileName = 'data/' + url.split('/')[-1]
	localFile = open(localFileName, 'w')
	localFile.write(webFile.read())
	webFile.close()
	localFile.close()

	print "Extracting file"
	zf = zipfile.ZipFile(localFileName)

	for i, name in enumerate(zf.namelist()):
		if not name.endswith('/'):
			outfile = open('data/latest.rdf', 'wb')
			outfile.write(zf.read(name))
			outfile.flush()
			outfile.close()
			print "File extracted"
	
	print "Reading file for conversion"
	ng = Graph()
	ng.parse("data/latest.rdf",format='xml')
	print "Serialising to Ntriples"
	ng.serialize("data/latest.nt",format='nt')


def iati_fetch(directory,groups):
    url = 'http://iatiregistry.org/api'
    import ckanclient
    registry = ckanclient.CkanClient(base_location=url)
    startnow = False
    for pkg_name in registry.package_register_get():
            try:
                 pkg = registry.package_entity_get(pkg_name)
            except Exception, e:
                 print "Error fetching package ",e

            try:
                group = pkg.get('groups').pop()
            except Exception, e:
                group = "Unknown"
            
            #Check if we were passed a list of groups, or if we're 
            if (not groups) or (group in groups):
                for resource in pkg.get('resources', []):
                    try:
                        if(check_file(pkg_name,directory + group + '/',resource.get('hash'))):
                            print "Saving file "+pkg_name
                            iati_save_file(pkg_name, resource.get('url'), directory + group + '/')
                            print "File saved "+pkg_name
                    except Exception, e:
                        print "Failed:", e
                        print "Couldn't find directory"

def iati_save_file(pkg_name, url, dir):
    check_dir(dir)
    webFile = urllib.urlopen(url)
    localFile = open(dir + '/' + pkg_name + '.xml', 'w')
    localFile.write(webFile.read())
    webFile.close()

def check_dir(dir):
    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
        except Exception, e:
            print "Failed:", e
            print "Couldn't create directory"

def check_file(pkg_name,dir,hash):
    try:
        checkfile = open(dir+'/'+pkg_name+'.xml')
        if(hashlib.sha1(checkfile.read()).hexdigest() == hash):
            print "No update to "+pkg_name
            return False
        else:
            print "File changed. Downloading update to " +pkg_name
            return True
    except Exception, e:
        print "New file - creating " + pkg_name
        return True

def rdf_clean_file(file):
    f = open(file,'r')
    data = f.read()
    f.close
    f = open(file,'w')
    f.write(data.replace('&#xD;','\\n'))
    f.close()

def rdf_process_file(file):        
    root, filename = os.path.split(file)
    rdf_file = os.path.splitext(filename)[0]+'.nt'
    rdf_path = root + '/' + rdf_file
    
    rdf_clean_file(file)
    
    try:
        xml = etree.parse(file)
        rdf = transform(xml)
        g = Graph()
        g.parse(StringInputSource(rdf),"xml")   
        g.serialize(rdf_path,format='nt')
        
    except Exception, e:
        print "Error processing file "+ file
        print e


# Set up variables and work through scripts

xslt = etree.parse('/root/scripts/IATI-XSLT/templates/rdf/iati-activities-rdf.xsl')
transform = etree.XSLT(xslt)

# R4DdownloadFile(R4DLocation)
# iati_fetch('data/','dfid')

for root, dirs, files in os.walk('data/dfid/'):
  for filename in fnmatch.filter(files, '*.xml'):
      print(os.path.join(root, filename))
      rdf_process_file(os.path.join(root, filename))