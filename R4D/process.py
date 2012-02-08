import sys, os, fnmatch, time
from time import strftime, gmtime
from rdflib.parser import StringInputSource
from rdflib.compare import to_isomorphic, graph_diff
from rdflib import Graph
from rdfchangesets import ChangeSet, BatchChangeSet

# Set up key variables
script_path = os.path.dirname(os.path.realpath(__file__))
exec_path = os.curdir

def check_dir(dir):
    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
        except Exception, e:
            print "Failed:", e
            print "Couldn't create directory"

def archive(fileName,timestamp = True, suffix = ''):
    root, filename = os.path.split(fileName)
    check_dir(root+"/archive")
    if timestamp:
        print "Archived to "+root+"/archive/"+filename+"-"+strftime('%Y%m%d-%H%M%S',gmtime())+suffix
        os.rename(fileName,root+"/archive/"+filename+"-"+strftime('%Y%m%d-%H%M%S',gmtime())+suffix)
    else:
        print "Archived to "+root+"/archive/"+filename+suffix
        os.rename(fileName,root+"/archive/"+filename+suffix)
    

def isRDF(s):
    if s.find(".rdf") == -1:
        return False
    else:
        return True


dirList=filter(isRDF,os.listdir(exec_path))
if len(dirList) > 1:
    print "More than one RDF file found. Please ensure only one file with .rdf extension in the current directory: " + exec_path
else: 
    try:
        print "Reading "+ dirList[0]
        print "(this may take some time...)"
        ng = Graph()
        ng.parse(dirList[0],format='xml')
        
        #If the old data has been uploaded then it will be in /archive/
        #If it has not yet been uploaded it will be in the main path. Prefer the main path version...
        rdf_path = exec_path + '/online.nt'

        #Now check if either really does exist, and make the changesets
        if os.path.exists(rdf_path):
            print "Comparing with old data"
            og = Graph()
            try:
                og.parse(rdf_path,format='nt')
            except Exception, e:
                print "Failed reading archived online data"
                print e

            print "Running graph diff - new data against archived data"
            both, old, new = graph_diff(og,ng)
            if(len(old)):
                cs = BatchChangeSet()
                cs.setCreatorName('R4D Update Scripts')
                cs.setChangeReason('Statements to remove from'+dirList[0])
                for (s,p,o) in old.triples((None, None, None)):
                    cs.remove(s,p,o)
                print "Saving triples for removal to changeset"
                cs.getGraph().serialize(rdf_path+'_csremove',format='nt')
            if(len(new)):
                cs = BatchChangeSet()
                cs.setCreatorName('IATI Update Scripts')
                cs.setChangeReason('Statements to add from '+dirList[0])
                for (s,p,o) in new.triples((None, None, None)):
                    cs.remove(s,p,o)
                print "Saving new triples to changeset"
                cs.getGraph().serialize(rdf_path+'_csadd',format='nt')  
        
        archive(exec_path+"/"+dirList[0],True)
        ng.serialize(rdf_path,format='nt')
        
    except Exception, e:
        print "Could not read RDFXML file: "
        print e


# Convert to turtle
# Compare to online.n3
# Create diffs
# Archive online.n3
# Save over online.n3
# Upload changes, or n3



