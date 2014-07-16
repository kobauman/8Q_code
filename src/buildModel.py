from gensim import corpora, models, similarities
import json
import logging
from copy import copy


class buidModel():
    def __init__(self,filename):
        self.abstracts = None
        try:
            infile = open(filename,"r")
            self.abstracts = json.loads(infile.read())
            infile.close()
            print 'Abstarcts loaded'
        except:
            return
        self.texts = list()
        
        self.indexLDA = dict()
        self.lda_corpus = list()
        
    
    
    def prepareCorpus(self):
        for i, abstract in enumerate(self.abstracts):
            if not i%100:
                print str(i)+" abstracts loaded"
    #        if i > 100:
    #            break
                
            self.texts.append(abstract['cleanText'])
            #print i, abstracts[abstract]
        
        print "Number of texts in collection: "+str(len(self.texts))
        
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%m-%d,%H:%M:%S', level=logging.INFO)
        
        self.dictionary = corpora.Dictionary(self.texts)
        self.dictionary.filter_extremes(no_below=10, no_above=0.8)
        self.dictionary.compactify()
        
        self.corpus_int = [self.dictionary.doc2bow(text) for text in self.texts]

    def builtTFIDF(self):
        self.tfidf = models.TfidfModel(self.corpus_int)
        features_num = len(self.dictionary.keys())
        self.index = similarities.SparseMatrixSimilarity(self.tfidf[self.corpus_int],features_num)


    def buildLDA(self,topic_number):
        self.lda_model = models.ldamodel.LdaModel(corpus=self.corpus_int, id2word=self.dictionary, num_topics=topic_number, update_every=1, chunksize=10000, passes=1)
        self.lda_model.print_topics(20)
            
        output = open('../../data/LDAtopics/'+'%d_LDA_topics.txt'%topic_number,"w")
        
        #self.save()
    #        self.dictionary.save(self.path+'%d_%d_words.dict'%(self.target_class,self.topics_num))
    #        self.lda_model.save(self.path+'%d_%d_ldamodel'%(self.target_class,self.topics_num))
    #        self.logger.info("Dictionary and LDA model saved to "+ self.path)
    
    
        for i, topic in enumerate(self.lda_model.show_topics(topics = 2000, topn=30, log=False, formatted=True)):
            #print str(i)+"\t"+topic.encode("utf8")
            try:
                output.write(str(i)+"\t"+topic.decode('utf8', 'ignore')+"\n\n")
            except:
                try:
                    output.write(str(i)+"\t"+topic[:30].decode('utf8', 'ignore')+"\n\n")
                except:
                    output.write(str(i)+"\t"+"\n\n")
        output.close()
    
    def makeNames(self):
        self.topics_names = list()
        lda_show = self.lda_model.show_topics(topics = self.lda_model.num_topics, topn=5, log=False, formatted=True)
        for topic in lda_show:
            words = topic.split("+")
            weights = [float(x.split("*")[0]) for x in words]
            i = 1
            if weights[i] > weights[0]/2:
                self.topics_names.append([x.split("*")[1].strip() for x in words[:2]])
            else:
                self.topics_names.append([x.split("*")[1].strip() for x in words[:1]])
                
    
    def applyLDA(self):
        for i, abstract in enumerate(self.corpus_int):
            topics = self.lda_model[abstract]
            cleanTopics = list()
            temp = [0]*self.lda_model.num_topics
            for topic in topics:
                if topic[1] > 0.05:
                    cleanTopics.append(topic)
                    temp[topic[0]] = topic[1]
                    if topic[1] > 0.2:
                        self.indexLDA[int(topic[0])] = self.indexLDA.get(int(topic[0]),[])
                        self.indexLDA[int(topic[0])].append(i)
            self.lda_corpus.append(copy(temp))
            self.abstracts[i]['lda'] = copy(cleanTopics)
        
    def save(self):
        #save dictionary
        self.dictionary.save('../../data/dictionary')
        
        #save Tfidf
        self.tfidf.save('../../data/tfidf_model')
        
        #save index
        self.index.save('../../data/index')
        
        #save LDA model
        self.lda_model.save('../../data/lda_model_%d'%self.lda_model.num_topics)
        
        #save indexLDA
        output = open('../../data/indexLDA.json','w')
        output.write(json.dumps(self.indexLDA))
        output.close()
        
        #save LDAcorpus
        output = open('../../data/LDAcorpus.json','w')
        output.write(json.dumps(self.lda_corpus))
        output.close()
        
        #save LDAcorpus
        output = open('../../data/LDAnames.json','w')
        output.write(json.dumps(self.topics_names))
        output.close()
        
        #save data
        output = open('../../data/abstracts_rich.json','w')
        output.write(json.dumps(self.abstracts))
        output.close()

        
if __name__ == '__main__':
    bm = buidModel('../../data/abstracts.json')
    bm.prepareCorpus()
    bm.builtTFIDF()
    bm.buildLDA(50)
    bm.makeNames()
    bm.applyLDA()
    bm.save()
