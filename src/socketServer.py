"""
URL redirection
"""

import BaseHTTPServer
from SocketServer import ThreadingMixIn
import time
#import threading
from searcher import searcher

search = searcher(50)


class searchHandler(BaseHTTPServer.BaseHTTPRequestHandler, searcher):
    def do_HEAD(self):
        searchQuery = self.path[1:]
        a,b = search.getResultFromText(searchQuery)
        
        topics = open('../../data/topics.csv','w')
        for t in a:
            try:
                topics.write(t+'\n')
            except:
                pass
        
        #topics.write('\n'.join(a))
        topics.close()
        
        papers = open('../../data/papers.csv','w')
        for t in b:
            try:
                papers.write(t+'\n')
            except:
                pass
        #papers.write('\n'.join(b))
        papers.close()
        
        link = 'http://www.google.com'
        self.send_response(301)
        self.send_header('Location',link)
        self.send_header('connection','close')
        self.end_headers()
        
        
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