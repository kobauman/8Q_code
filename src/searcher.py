from gensim import corpora, models, similarities
from gensim.utils import tokenize
import json
import re
import time
import sys
sys.path.append('../')


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
        
        #load LDA model
        self.lda_model = models.ldamodel.LdaModel.load('../../data/lda_model_%d'%topic_num)
        
        #load data
        infile = open('../../data/abstracts_rich.json','r')
        self.abstracts = json.loads(infile.read())
        infile.close()
        
        
        print 'Searcher Loaded'
    
    def getResultFromText(self, text, groups = 10):
        text_list = cleanText(text)
        text_list_int = self.dictionary.doc2bow(text_list)
        sims = self.index[self.tfidf[text_list_int]]
        result_set = set()
        for doc, w in enumerate(sims):
            #print doc,w
            if w > 0.05:
                result_set.add(doc)
        
        topic_dict = dict()
        for doc in result_set:
            for topic in self.abstracts[doc]['lda']:
                topic_dict[topic[0]] = topic_dict.get(topic[0],{'center':[None,0.0],
                                                                'closest':[None,0.0],'list':[]})
                weightCenter = topic[1]
                if weightCenter > topic_dict[topic[0]]['center'][1]:
                    topic_dict[topic[0]]['center'][0] = self.abstracts[doc]['header']
                    topic_dict[topic[0]]['center'][1] = weightCenter
                
                weightClosest = sims[doc]
                if weightClosest > topic_dict[topic[0]]['closest'][1]:
                    topic_dict[topic[0]]['closest'][0] = self.abstracts[doc]['header']
                    topic_dict[topic[0]]['closest'][1] = weightClosest
                
                topic_dict[topic[0]]['list'].append(doc)
        
        topic_list = [[len(topic_dict[t]['list']),t] for t in topic_dict]
        topic_list.sort(reverse=True)
        
        topic_result = list()
        paper_result = list()
        for topic in topic_list[:groups]:
            topicID = topic[1]
            topic_center = topic_dict[topicID]['center']
            topic_closest = topic_dict[topicID]['closest']
            #topicID,numberOfPapers,NameOfCenter,WeightOfCenter,NameOfClosest,WeightOfClosest
            topic_line = '%d,%d,%s,%f,%s,%f'%(topicID,topic[0],
                                        topic_center[0],topic_center[1],
                                        topic_closest[0],topic_closest[1])
            topic_result.append(topic_line)
            
            for paperID in topic_dict[topicID]['list']:
                paperName = self.abstracts[paperID]['header']
                paperPath = self.abstracts[paperID]['path']
                #topicID,paperID,paperName,paperPath
                paper_line = '%d,%d,%s,%s'%(topicID,paperID,paperName,paperPath)
                paper_result.append(paper_line)
        
        return topic_result,paper_result
        
        
        
        
if __name__ == '__main__':
    search = searcher(50)
    t0 = time.time()
    #a,b = search.getResultFromText('Magnetoelastic Viscosity Sensor for On-Line Status Assessment of Lubricant Oils')
    a,b = search.getResultFromText('A Data Fusion Technique for Wireless Ranging Performance Improvement')
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