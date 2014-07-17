"""
URL redirection
"""

import BaseHTTPServer
from SocketServer import ThreadingMixIn
import time
#import threading
from searcher import searcher

search = searcher(200)


class searchHandler(BaseHTTPServer.BaseHTTPRequestHandler, searcher):
    def do_HEAD(self):
        searchQuery = self.path[1:]
        print searchQuery
        try:
            a,b = search.search(searchQuery, 20, 10)
        except:
            a,b = [],[]
        print a,b
        clusters = open('/opt/bitnami/apache2/cgi-bin/clusters.csv','w')
        for t in a:
            try:
                clusters.write(t+'\n')
            except:
                pass
        
        #topics.write('\n'.join(a))
        clusters.close()
        
        papers = open('/opt/bitnami/apache2/cgi-bin/papers.csv','w')
        for t in b:
            try:
                papers.write(t+'\n')
            except:
                pass
        #papers.write('\n'.join(b))
        papers.close()
        
#        link = 'http://www.google.com'
#        self.send_response(301)
#        self.send_header('Location',link)
#        self.send_header('connection','close')
#        self.end_headers()
        # just send back the same data, but upper-cased
        self.request.sendall("DONE")
        
        
    def do_GET(self):
        self.do_HEAD()


class ThreadedHTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass





if __name__ == '__main__':
    PORT_NUMBER = 8888
    server_class = ThreadedHTTPServer
    handler_class = searchHandler
    
    
    httpd = server_class(('', PORT_NUMBER), handler_class)    
    print time.asctime(), "Server Starts - %s" %str(httpd.server_address)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s" %str(httpd.server_address)