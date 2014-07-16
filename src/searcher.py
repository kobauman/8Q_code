from gensim import corpora, models, similarities
from gensim.utils import tokenize
import json
import re
import time
import sys
sys.path.append('../')
from sklearn.cluster import MiniBatchKMeans, KMeans


from utils.stopwords_lst import stopwords

stoplist = stopwords()

def cleanText(text):
    plain_text = text.lower().replace("\n"," ").replace('ieee transactions on magnetics','')
    plain_text = plain_text.replace('ieee','').replace('abstract','')
    result = list()
    for word in tokenize(plain_text):
        if word not in stoplist and re.search("[a-z]", word) and len(word) > 2:
            result.append(word.encode("utf8"))
    return result




class searcher():
    def __init__(self,topic_num):
        #load dictionary
        self.dictionary = corpora.Dictionary.load('../../data/dictionary')
        
        #load Tfidf
        self.tfidf = models.TfidfModel.load('../../data/tfidf_model')
        
        #load index
        self.index = similarities.SparseMatrixSimilarity.load('../../data/index')
        
        #load data
        infile = open('../../data/abstracts_rich.json','r')
        self.abstracts = json.loads(infile.read())
        infile.close()
        
        
        #============================
        #LDA
        
        #load LDA model
        self.lda_model = models.ldamodel.LdaModel.load('../../data/lda/lda_model_%d'%topic_num)
        
        #load indexLDA
        infile = open('../../data/lda/indexLDA_%d.json'%topic_num,'r')
        self.indexLDA = json.loads(infile.read())
        infile.close()
        
        #load LDA corpus
        infile = open('../../data/lda/LDAcorpus_%d.json'%topic_num,'r')
        self.lda_corpus = json.loads(infile.read())
        infile.close()
        
        #load LDA names
        infile = open('../../data/lda/LDAnames_%d.json'%topic_num,'r')
        self.topics_names = json.loads(infile.read())
        infile.close()
        
        
        
        
        print 'Searcher Loaded'
    
    
    def getRelevantPapers(self,search_query):
        text_list = cleanText(search_query)
        text_list_int = self.dictionary.doc2bow(text_list)
        sims = self.index[self.tfidf[text_list_int]]
        result_set = set()
        for doc, w in enumerate(sims):
            #print doc,w
            if w > 0.05:
                result_set.add(doc)
        print 'relevant_papers',len(result_set), '\t', result_set
        return result_set
    
    
    def getSetOfTopicsByPapers(self, paper_set, N = 1000):
        result = dict()
        for paperID in paper_set:
            for topic in self.abstracts[paperID]['lda']:
                result[topic[0]] = result.get(topic[0],0.0)
                result[topic[0]]+= topic[1]
        res = [[result[t],t] for t in result]
        res.sort(reverse=True)
        print [t[1] for t in res[:N]]
        return [t[1] for t in res[:N]]
        
    def getExtendedSetOfPapers(self, topic_set):
        result = set()
        for topic in topic_set:
            result = result.union(set(self.indexLDA[str(topic)]))
        print 'extended_list: ',len(result)
        return result
    
    
    def getClustersOfpapers(self,papers_set,cluster_num = 10):
        corpus = list()
        for paperID in papers_set:
            corpus.append(self.lda_corpus[paperID])
        
        clusterModel = MiniBatchKMeans(init='random', n_clusters=cluster_num, n_init=10)
        clusterModel.fit(corpus)
        
        clusterTopics = dict()
        clusterYear = dict()
        clusterSize = dict()
        
        paper_result = list()
        for paperID in papers_set:
            cluster = int(clusterModel.predict(self.lda_corpus[paperID])[0])
            paper_result.append('%d,%d,%s,%s,%d,%s'%(cluster,
                                            paperID,
                                            self.abstracts[paperID]['header'],
                                            str(self.abstracts[paperID]['year']),
                                            self.abstracts[paperID]['pages'],
                                            self.abstracts[paperID]['path']))
            
            clusterSize[cluster] = clusterSize.get(cluster,0)
            clusterSize[cluster] += 1
            
            clusterTopics[cluster] = clusterTopics.get(cluster,dict())
            for t in self.abstracts[paperID]['lda']:
                clusterTopics[cluster][t[0]] = clusterTopics[cluster].get(t[0],0)
                clusterTopics[cluster][t[0]] += t[1]
            
            clusterYear[cluster] = clusterYear.get(cluster,dict())
            year = self.abstracts[paperID]['year']
            if year:
                clusterYear[cluster][year] = clusterYear[cluster].get(year,0)
                clusterYear[cluster][year]+=1
                
        cluster_result = list()
        for cluster in clusterSize:
            topics = [[clusterTopics[cluster][t],t] for t in clusterTopics[cluster]]
            topics.sort(reverse=True)
            name = self.topics_names[topics[0][1]]
            
            years = [[clusterYear[cluster][y],y] for y in clusterYear[cluster]]
            if len(years) == 0:
                year = 'None'
            else:
                years.sort(reverse=True)
                year = years[0][1]
            
            cluster_result.append('%s,%d,%d,%d,%s'%(str(name),
                                          cluster,
                                          clusterSize[cluster],
                                          cluster,
                                          year))
    
        return paper_result, cluster_result
    
#    def getResultFromText(self, text, groups = 10):
#        
#        topic_dict = dict()
#        for doc in result_set:
#            for topic in self.abstracts[doc]['lda']:
#                topic_dict[topic[0]] = topic_dict.get(topic[0],{'center':[None,0.0],
#                                                                'closest':[None,0.0],'list':[]})
#                weightCenter = topic[1]
#                if weightCenter > topic_dict[topic[0]]['center'][1]:
#                    topic_dict[topic[0]]['center'][0] = self.abstracts[doc]['header']
#                    topic_dict[topic[0]]['center'][1] = weightCenter
#                
#                weightClosest = sims[doc]
#                if weightClosest > topic_dict[topic[0]]['closest'][1]:
#                    topic_dict[topic[0]]['closest'][0] = self.abstracts[doc]['header']
#                    topic_dict[topic[0]]['closest'][1] = weightClosest
#                
#                topic_dict[topic[0]]['list'].append(doc)
#        
#        topic_list = [[len(topic_dict[t]['list']),t] for t in topic_dict]
#        topic_list.sort(reverse=True)
#        
#        topic_result = list()
#        paper_result = list()
#        for topic in topic_list[:groups]:
#            topicID = topic[1]
#            topic_center = topic_dict[topicID]['center']
#            topic_closest = topic_dict[topicID]['closest']
#            #topicID,numberOfPapers,NameOfCenter,WeightOfCenter,NameOfClosest,WeightOfClosest
#            topic_line = '%d,%d,%s,%f,%s,%f'%(topicID,topic[0],
#                                        topic_center[0],topic_center[1],
#                                        topic_closest[0],topic_closest[1])
#            topic_result.append(topic_line)
#            
#            for paperID in topic_dict[topicID]['list']:
#                paperName = self.abstracts[paperID]['header']
#                paperPath = self.abstracts[paperID]['path']
#                #topicID,paperID,paperName,paperPath
#                paper_line = '%d,%d,%s,%s'%(topicID,paperID,paperName,paperPath)
#                paper_result.append(paper_line)
#        
#        return topic_result,paper_result
        
    def search(self,searchQuery,topics_num, cluster_num):
        relevantPapers = self.getRelevantPapers(searchQuery)
        topics = self.getSetOfTopicsByPapers(relevantPapers, topics_num)
        extendedSetOfPapers = self.getExtendedSetOfPapers(topics)
        paper_result, cluster_result = self.getClustersOfpapers(extendedSetOfPapers,cluster_num)
        return paper_result, cluster_result
        
if __name__ == '__main__':
    if len(sys.argv) > 1:
        topic_num = int(sys.argv[1])
    else:
        print 'Please specify Topic_num'
        exit()
    
    
    search = searcher(topic_num)
    t0 = time.time()
    #a,b = search.getResultFromText('Magnetoelastic Viscosity Sensor for On-Line Status Assessment of Lubricant Oils')
    a,b = search.search('A Data Fusion Technique for Wireless Ranging Performance Improvement',topics_num = 10,cluster_num = 10)
    print time.time()-t0
    for x in a:
        try:
            print x
        except:
            pass
    print '====================='
    for x in b:
        try:
            print x
        except:
            pass