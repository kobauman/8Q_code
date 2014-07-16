from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
import os
import json
import sys
import re
import dateutil.parser as dparser
sys.path.append('../')

from utils.stopwords_lst import stopwords
stoplist = stopwords()



def convert_all_files(path):
    if not path.endswith("/"):
        path += "/"
    counter = 0
    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith(".pdf"):
                counter += 1
                print counter,'\t',root+'/'+name
                input_file = root+'/'+name
                output = input_file.replace('.pdf','.txt')
                abstract = convert_pdf_to_txt(input_file)
                if abstract:
                    out = open(output, 'w')
                    abstract['ID'] = name.split('/')[-1].split('.')[0]
                    abstract['path'] = input_file
                    out.write(json.dumps(abstract))
                    out.close()
                else:
                    try:
                        os.remove(output)
                    except:
                        pass
                    print 'pass'
                



def convert_pdf_to_txt(path):
    p = re.compile('\d{4}')
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for j, page in enumerate(PDFPage.get_pages(fp, pagenos, 
                                               maxpages=maxpages, 
                                               password=password,
                                               caching=caching, 
                                               check_extractable=True)):
        if j == 0:
            interpreter.process_page(page)
        else:
            continue
        #break
    
    fp.close()
    device.close()
    string = retstr.getvalue()
    retstr.close()
    
    years = p.findall(string)
    if years:
        year = years[0]
    else:
        year = None
    lines = string.split('\n')
    header = list()
    header_flag = False
    
    abstract = ''
    abstr_flag = False
    for i, line in enumerate(lines):
        if line.strip() == '' or line.isdigit():
            continue
        
        if header_flag == True or 'ieee' in line.lower() or 'abstract' in line.lower():
            pass
        else:
            header.append(line)
        
        if 'abstract ' in line.lower():
            abstr_flag = True
            header_flag = True
        if 'index terms' in line.lower() or 'introduction' in line.lower():
            if not len(abstract):
                abstract = ' '.join(lines[:i])
            abstr_flag = False
        if abstr_flag:
            abstract += line
    
    #print header
    header_text = ' '.join(header[:2])
    
    if len(abstract):
        #print header_text
        return {'header':header_text.decode('utf-8', 'ignore'), 
                'abstract':abstract,
                'year':year,
                'pages':j+1}
    else:
        return False


if __name__ == '__main__':
#    input_file = '../../data/8QLabs_Corpus/IEEEcnf/2013/19/6375864/06287017.pdf'
#    output = '../../data/8QLabs_Corpus/IEEEcnf/2013/19/6375864/06287017.txt'
#    out = open(output, 'w')
#    out.write(convert_pdf_to_txt(input_file))
    
    #convert_all_files('../../data/8QLabs_Corpus/IEEEcnf/')
    
    #convert_all_files('../../data/8QLabs_Corpus/')
    convert_all_files('/opt/bitnami/apache2/htdocs/data/Xfiles/')
        
            
                
    