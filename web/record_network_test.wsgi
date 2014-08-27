#!/usr/bin/env python

from cgi import parse_qs, escape
import sys
import datetime

import elasticsearch

DEBUG = 1

def get_db_client():
    """ Instantiate DB client and pass connection back """

    client = elasticsearch.Elasticsearch(host='student01.ci-connect.net')
    return client

def insert_record(client = None, record = None):
    """
    Record network bandwidth/latency measurements to elastic search
    """
    if record is None or record == {} or  client is None:
        return

    if 'bandwidth' in record and record['bandwidth'] != 0:
        bandwidth_rec = record.copy()
        if 'latency' in bandwidth_rec:
            del bandwidth_rec['latency']
        client.index(index='network-probe', doc_type='bandwidth', body=bandwidth_rec)
    if 'latency' in record and record['latency'] != 0:
        latency_rec = record.copy()
        if 'bandwidth' in latency_rec:
            del latency_rec['bandwidth']
        client.index(index='network-probe', doc_type='latency', body=latency_rec)
    

def application(environ, start_response):
    """ Get GET parameters and put into mongoDB"""

    query_dict = parse_qs(environ['QUERY_STRING'])
    record = {}
    if 'host' in query_dict:
        record['host'] = escape(query_dict['host'][0])
    else:
        record['host'] = ''
    if 'bandwidth' in query_dict:
        record['bandwidth'] = float(escape(query_dict['bandwidth'][0]))
    else:
        record['bandwidth'] = 0.0
    if 'latency' in query_dict:
        record['latency'] = float(escape(query_dict['latency'][0]))
    else:
        record['latency'] = 0.0
    if 'site' in query_dict:
        record['site'] = escape(query_dict['site'][0])
    else:
        record['site'] = ''
    if 'date' in query_dict:
        try:
            record['date'] = datetime.datetime.fromtimestamp(float(escape(query_dict['date'][0])))
        except:
            record['date'] = datetime.datetime.now()
    else:
        record['date'] = datetime.datetime.now()
    if (record['site'] == ''):
        status = '200 OK'
        response_body = 'No record to insert!'
        response_headers = [('Content-Type', 'text/html'),
                            ('Content-Length', str(len(response_body)))]
        start_response(status, response_headers)
        return [response_body]
    response_body = 'Record inserted'
    client = get_db_client()        
    try:
        if DEBUG:
            print record
        insert_record(client, record)
    except Exception, e:
        response_body = "Error %s while recording %s" % (e, record)
        sys.stderr.write(response_body)
    status = '200 OK'
    response_headers = [('Content-Type', 'text/html'),
                     ('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)
    print response_body
    return [response_body]

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('login.osgconnect.net', 8080, application)
    srv.serve_forever()
