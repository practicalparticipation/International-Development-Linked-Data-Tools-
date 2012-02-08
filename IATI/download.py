import sys
import ckan    
import urllib
from datetime import date
import os
import hashlib


def run(directory,groups):
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
                        if(check_file(pkg_name,dir + group + '/',resource.get('hash'))):
                            print "Saving file "+pkg_name
                            save_file(pkg_name, resource.get('url'), dir + group + '/')
                            print "File saved "+pkg_name
                    except Exception, e:
                        print "Failed:", e
                        print "Couldn't find directory"

def save_file(pkg_name, url, dir):
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

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Download data packages from the IATI Registry')
    parser.add_argument('--dir', type=str, nargs='?', default='~/iati/data/packages/',
                   help='A full path to where packages should be stored')
    parser.add_argument('--groups', dest='groups', type=str, nargs='*', 
                   help='One or more groups to use')
    args = parser.parse_args()
    print args
    import sys

    check_dir(args.dir)
    run(args.dir,args.groups)
