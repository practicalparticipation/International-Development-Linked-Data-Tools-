import sys, os, fnmatch
from lxml import etree
from rdflib.parser import StringInputSource
from rdflib.compare import to_isomorphic, graph_diff
from rdflib import Graph
from rdfchangesets import ChangeSet, BatchChangeSet

# Set up key variables
script_path = os.path.dirname(os.path.realpath(__file__))
exec_path = os.curdir

#Create the XSLT transformation function
xslt = etree.parse(script_path+'/IATI-XSLT/templates/rdf/iati-activities-rdf.xsl')
transform = etree.XSLT(xslt)


def clean_file(file):
    f = open(file,'r')
    data = f.read()
    f.close
    f = open(file,'w')
    f.write(data.replace('&#xD;','\\n'))
    f.close()

def process_file(file):        
    root, filename = os.path.split(file)
    rdf_file = os.path.splitext(filename)[0]+'.nt'
    rdf_path = root + '/' + rdf_file
    
    clean_file(file)
    
    try:
        xml = etree.parse(file)
        rdf = transform(xml)
    
        g = Graph()
        g.parse(StringInputSource(rdf),"xml")   
    
    
        # If the graph already exists then we want to generate some diffs before overwriting it: these can be used generating changesets when uploading to a datastore
        existing = False
        if os.path.exists(rdf_path):
            print "Comparing graphs"
            go = Graph()
            go.parse(rdf_path,format='nt')
            existing = True
        elif os.path.exists(root+'/archive/'+rdf_file):
            print "Comparing with archived graph"
            go = Graph()
            go.parse(root+'/archive/'+rdf_file,format='nt')
            existing = True
        
        if existing:
            both, old, new = graph_diff(go,g)
            if(len(old)):
                # old.serialize(rdf_path+'_old',format='nt') #Uncomment if you want a non-reified version of the statements
                cs = BatchChangeSet()
                cs.setCreatorName('IATI Update Scripts')
                cs.setChangeReason('Statements to remove from'+file)
                for (s,p,o) in old.triples((None, None, None)):
                    cs.remove(s,p,o)
                cs.getGraph().serialize(rdf_path+'_csremove',format='nt')
            if(len(new)):
                # new.serialize(rdf_path+'_new',format='nt') #Uncomment if you want a non-reified version of the statements
                cs = BatchChangeSet()
                cs.setCreatorName('IATI Update Scripts')
                cs.setChangeReason('Statements to add from '+file)
                for (s,p,o) in new.triples((None, None, None)):
                    cs.remove(s,p,o)
                cs.getGraph().serialize(rdf_path+'_csadd',format='nt')
            			
        g.serialize(rdf_path,format='nt')
        
    except Exception, e:
        print "Error processing file "+ file
        print e

for root, dirs, files in os.walk(exec_path):
  for filename in fnmatch.filter(files, '*.xml'):
      print(os.path.join(root, filename))
      process_file(os.path.join(root, filename))
