#!/usr/bin/env python

import sys
from searcher import searcher

if __name__ == '__main__':
    if len(sys.argv) > 1:
        searchQuery = ' '.join(sys.argv[1:])
    else:
        print 'Please specify Search Query'
        exit()
    
    search = searcher(200)

    print searchQuery
    try:
        a,b = search.search(searchQuery, 20, 10)
    except:
        a,b = [],[]
    
    print len(a),len(b)
    clusters = open('/opt/bitnami/apache2/cgi-bin/clusters.csv','w')
    #clusters = open('../../data/clusters.csv','w')
    for i, cluster in enumerate(b):
        for s in cluster:
            try:
                clusters.write(s)
            except:
                pass
        if i < len(b)-1:
            clusters.write('\n')
    
    #topics.write('\n'.join(a))
    clusters.close()
    
    papers = open('/opt/bitnami/apache2/cgi-bin/papers.csv','w')
    #papers = open('../../data/papers.csv','w')
    for i, paper in enumerate(a):
        for s in paper:
            try:
                papers.write(s)
            except:
                pass
        if i < len(a)-1:
            papers.write('\n')
    #papers.write('\n'.join(b))
    papers.close()