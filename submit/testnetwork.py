#!/usr/bin/env python
import urllib
import urllib2
import time
import getopt
import sys
import os
import timeit
import platform
import subprocess
import re

REFERENCE_URL = 'http://stash.osgconnect.net/+sthapa/100MB_ref'
WSGI_URL = 'http://web-dev.ci-connect.net/~sthapa/record_network_test.wsgi'

def download_file():
    """
    Download file and then remove it
    """  
    webref = urllib2.urlopen(REFERENCE_URL)
    foo = webref.read()

def get_host_info():
    """
    GET host information
    """
    host_info = {}
    if 'OSG_SITE_NAME' in os.environ:
        host_info['site'] = os.environ['OSG_SITE_NAME']
    elif 'GLIDEIN_RESOURCE_NAME' in os.env:
        host_info['site'] = os.envron['GLIDEIN_RESOURCE_NAME']
    host_info['hostname']  =  platform.node()    
    return host_info

def send_record(test_record = None):
    """
    Send record to wsgi 
    """
    if test_record is None:
        return
    try:
        temp = test_record.copy()
        if 'latency' in temp:
            del temp['latency']
        bandwidth_req = WSGI_URL + '?' + urllib.urlencode(temp)
        req = urllib2.urlopen(bandwidth_req)
        temp = test_record.copy()
        if 'bandwidth' in temp:
            del temp['bandwidth']
        latency_req = WSGI_URL + '?' + urllib.urlencode(temp)
        req = urllib2.urlopen(latency_req)
    except Exception, e:
        pass

def get_latency():
    """
    Test ping time latency to stash
    """
    try:
        ping_output = subprocess.check_output(['/bin/ping', '-c', '10', 'stash.osgconnect.net'])
    except AttributeError:
        process = subprocess.Popen(['/bin/ping', '-c', '10', 'stash.osgconnect.net'], stdout=subprocess.PIPE)
        ping_output = process.communicate()[0]
    ping_regex = re.compile(r'rtt.*=\s+[\d.]+/([\d.]+)')
    match = ping_regex.search(ping_output)
    if match:
        return float(match.group(1))
    return 0.0

def main():
    test_record = get_host_info()
    test_record['date'] = time.time()
    download_times = timeit.Timer('download_file()', "from __main__ import download_file").repeat(repeat = 5, number = 1)
    avg_time = 0.0
    records = 0
    for x in download_times:
        if x < 0.005:
            continue
        avg_time += x
        records += 1
    test_record['bandwidth']  = float(100 * 2**20) / (avg_time / float(records))
    test_record['latency'] = get_latency()
    send_record(test_record)

if __name__ == "__main__":
    main()
