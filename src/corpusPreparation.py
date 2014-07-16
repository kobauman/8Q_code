import os
import re
import json
import sys
sys.path.append('../')

from gensim.utils import tokenize
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


def get_abstracts(path):
    if not path.endswith("/"):
        path += "/"
        
    abstracts = list()
    
    counter = 0
    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith(".txt"):
                counter += 1
                filename = root+'/'+name
                print counter,'\t',filename
                data = json.loads(open(filename,'r').read())
                #infile = open(filename,'r')
                rawText = data['abstract']
                parsedText = cleanText(rawText)
                data['cleanText'] = parsedText
                year = data['year']
                if year != 'None':
                    y = int(year)
                    if y < 2015 and y > 1950:
                        data['year'] = str(y)
                    else:
                        data['year'] = 'None'
                
                abstracts.append(data.copy()) 
                
    return abstracts


if __name__ == '__main__':
#    input_file = '../../data/8QLabs_Corpus/IEEEcnf/2013/19/6375864/06287017.pdf'
#    output = '../../data/8QLabs_Corpus/IEEEcnf/2013/19/6375864/06287017.txt'
#    out = open(output, 'w')
#    out.write(convert_pdf_to_txt(input_file))
    
    #path = '../../data/8QLabs_Corpus'
    #path = '../../data/8QLabs_Corpus/'
    #path = '../../data/8QLabs_Corpus/IEEEcnf'
    path = '/opt/bitnami/apache2/htdocs/data/Xfiles/'
    abstracts = get_abstracts(path)
    
    output = open('../../data/abstracts.json', 'w')
    output.write(json.dumps(abstracts).decode('utf8', 'ignore'))
    output.close()
        
