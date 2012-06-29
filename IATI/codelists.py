# Tool for reading converting IATI Codelists into XML using XSLT available from https://github.com/aidinfolabs/IATI-XSLT/
# Author: tim@practicalparticipation.co.uk
# Created: January 7th 2012

from lxml import etree
import urllib
import os
from rdflib import Graph
from rdflib.parser import StringInputSource

#Set up codelist parameters
codelist_uri = "http://dev.yipl.com.np/iati/tools/public/api/codelists/"

codelist_baseuri, codelist_index = os.path.split(codelist_uri)

# Set up key variables
script_path = os.path.dirname(os.path.realpath(__file__))
exec_path = os.curdir

#Create the XSLT transformation function
xslt = etree.parse(script_path+'/../IATI-XSLT/templates/rdf/iati-codelists-rdf.xsl')
transform = etree.XSLT(xslt)


def fetch_codelists(dir):
    codelists_tree = etree.parse(codelist_uri)
    codelists = codelists_tree.getroot()
    
    for codelist in codelists:
        root, codelist_id = os.path.split(etree.tostring(codelist.find('url'),method='text'))
        try:
            codelist_data = urllib.urlopen(codelist_baseuri+'/'+codelist_id)
            try: 
                xml = etree.fromstring(codelist_data.read())
                rdf = transform(xml)
                g = Graph()
                g.parse(StringInputSource(rdf),"xml")
                g.serialize(dir + codelist_id + ".nt",format='nt')
            except Exception, e:
                print "Codelist " + codelist_id + " was not valid XML"
                print e
        except Exception, e:
            print "Error fetching codelist " + codelist_id

if __name__ == '__main__':
    dir = '/root/iati/data/codelists/'
    fetch_codelists(dir)