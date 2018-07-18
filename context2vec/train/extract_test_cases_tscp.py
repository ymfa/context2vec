
# coding: utf-8

# In[2]:


import sys
import pandas as pd
import csv

def load_conversion(conversion_f):
    conversion={}
    
    with open(conversion_f) as f:
        for line in f:
            simp_w,trad_w=line.split('\t')
#             if '(' not in conversion
            conversion[simp_w]=trad_w
    return conversion
import sys

def match_conversion(conversion,test_out_f,test_en_f,test_de_f):
        fieldnames = ['orig_char', 'gold_char','char_index','orig','gold','orig_line_num']
        writer = csv.DictWriter(open(test_out_f,'w'), fieldnames=fieldnames)
        writer.writeheader()
            
        test_de=open(test_de_f).readlines()

        with open (test_en_f) as test_en:
            
            line_num=0
            for line in test_en:
                trad_ws=''
                ws=''
                char_is=''
                line_nums=''
                line=line.strip()
                if line_num%10000==0 and line_num>10000:
                    print ('.'),
                for i,w in enumerate(line.split()):
                    if w in conversion:
                        trad_line=test_de[line_num].strip()
                        trad_w=test_de[line_num].strip().split()[i]
                        if trad_w in conversion[w]:
                            #store matched results
                            trad_ws+=trad_w
                            ws+=w
                            char_is+='-'+str(i)
                            line_nums+='-'+str(line_num)
                #output matched results per sentence to csv         
                if trad_ws!='':
                    writer.writerow({fieldnames[0]:ws, fieldnames[1]:trad_ws,fieldnames[2]:char_is,fieldnames[3]:line,fieldnames[4]:trad_line, fieldnames[5]:line_nums })
                line_num+=1


# In[ ]:


if __name__=='__main__':
    corpus_dir=sys.argv[1]
    test_en_f=corpus_dir+'.en.DIR/test_sents'
    test_de_f=corpus_dir+'.de.DIR/test_sents'
    test_out_f=corpus_dir+'_0.2_test_gold.csv'

    conversion_f=sys.argv[2]
    conversion=load_conversion(conversion_f)
    match_conversion(conversion,test_out_f,test_en_f,test_de_f)



