import sys, os, fnmatch, math
import pytassium
from time import gmtime, strftime
import argparse

parser = argparse.ArgumentParser(description='Upload data to KASABI')
parser.add_argument('--dataset', dest='dataset', type=str, nargs=1, 
                   help='The dataset to upload to')
parser.add_argument('--apikey', dest='apikey', type=str, nargs=1, 
                   help='API Key')
args = parser.parse_args()


if not(args.dataset and args.apikey):
    print "Please provide both an --apikey and --dataset paramter at the command line"

else: 
    #Configure
    kasabi_dataset = args.dataset[0]
    api_key = args.apikey[0]

    dataset = pytassium.Dataset(kasabi_dataset,api_key) 
    response, job_uri = dataset.schedule_reset()
    print "Reset scheduled, URI is: %s" % job_uri
    print "Waiting for reset to complete"
    done = False
    while not done:
      response, data = dataset.job_status(job_uri)
      if response.status in range(200,300):
        if data['status'] == 'scheduled':
          print "Reset has not started yet"
        elif data['jobStatus'] == 'pending':
          print "Reset has not started yet"
        elif data['status'] == 'running':
          print "Reset is in progress"
        elif data['status'] == 'failed':
          print "Reset has failed"
          done = True
        elif data['status'] == 'succeeded':
          print "Reset has completed"
          done = True
        elif data['jobStatus'] == 'applied':
          print "Reset has completed"
          done = True
 
    #Establish variables
    script_path = os.path.dirname(os.path.realpath(__file__))
    exec_path = os.curdir

    def check_dir(dir):
        if not os.path.exists(dir):
            try:
                os.makedirs(dir)
            except Exception, e:
                print "Failed:", e
                print "Couldn't create directory"

    def upload(filename,type):
        dataset = pytassium.Dataset(kasabi_dataset,api_key)

        print "Processing "+type+" for "+os.path.splitext(filename)[0]
        chunk_size = 1000000

        #Chunk code taken from Pytassium, released under Public Domain License courtessy of Ian Davis (http://iandavis.com/)
        if os.path.getsize(filename) < chunk_size:
            response, joburi = dataset.store_file(filename,media_type='text/turtle')
            print joburi
        else:
            expected_chunks = math.ceil(os.path.getsize(filename) / chunk_size)
            chunk = 1
            linecount = 0
            data = ''
            f = open(filename, 'r')
            for line in f:
                linecount += 1
                data += line
                if len(data) >= chunk_size:
                    print "Storing chunk %s of %s (%s bytes), %s lines done, estimate %s remaining chunks" % (chunk, filename, len(data), linecount, expected_chunks - chunk + 1)
                    response, joburi = dataset.store_data(data, media_type='text/turtle')
                    print joburi
                    chunk += 1
                    data = ''
            f.close()    
            if len(data) >= 0:
                print "Storing final chunk %s of %s (%s bytes), %s total lines sent" % (chunk, filename, len(data), linecount)
                response, joburi = dataset.store_data(data, media_type='text/turtle')
                print joburi


    def archive(file,timestamp = True):
        root, filename = os.path.split(file)
        check_dir(root+"/archive")
        if timestamp:
            os.rename(file,root+"/archive/"+filename+"-"+strftime('%Y%m%d-%H%M%S',gmtime()))
        else:
            os.rename(file,root+"/archive/"+filename)

    #Loop through removals first, then additions, then completely new data
    for root, dirs, files in os.walk(exec_path):
        print root
        for filename in fnmatch.filter(files, '*.nt_csremove'):
            upload(os.path.join(root, filename),'removal')
        for filename in fnmatch.filter(files, '*.nt_csadd'):
            upload(os.path.join(root, filename),'addition')
        for filename in fnmatch.filter(files, '*.nt'):
            stem = os.path.splitext(os.path.join(root, filename))[0]
            # We don't want to upload archived files
            if not("archive" in stem):
                #We only want to do a full upload if we've not got removals or additions for this file
                if not(os.path.exists(stem+".nt_csremove") or os.path.exists(stem+".nt_csadd")):
                    upload(os.path.join(root, filename),' new data ')
                    # We don't want to archive the online n3 file - as the non-archive directory should always reflect what should be online right now
                    # archive(os.path.join(root, filename),False) 

        #Now do archival
        for filename in fnmatch.filter(files, '*.nt_csremove'):
            archive(os.path.join(root, filename))
        for filename in fnmatch.filter(files, '*.nt_csadd'):
            archive(os.path.join(root, filename))


