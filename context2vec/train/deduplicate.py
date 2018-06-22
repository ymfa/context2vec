import sys
import os

from collections import Counter
from context2vec.common.defs import SENT_COUNTS_FILENAME, WORD_COUNTS_FILENAME, TOTAL_COUNTS_FILENAME
import jieba

import jieba

def sents2segwords(sent_simp,sent_trad):
    w_simp_out=[]
    w_trad_out=[]
    w_simp=jieba.lcut(sent_simp)
    
    i=0
    for w in w_simp:
        
        w_trad_out+=list(sent_trad[i:(i+len(w))])
        
        w_simp_out+=list(w)
        if (i+len(w))!=len(sent_trad):
            w_trad_out.append('||')
            w_simp_out.append('||')
            i+=len(w)
    return ' '.join(w_simp_out).encode('utf-8'),' '.join(w_trad_out).encode('utf-8'),w_simp_out,w_trad_out

if __name__ == '__main__':
    
    corpus_dir=sys.argv[1]
    seg_flag=sys.argv[2]
    corpus_dir_en=corpus_dir+'.en.DIR'
    corpus_dir_de=corpus_dir+'.de.DIR'
    corpus_dir_en_de=corpus_dir+'.en-de.DIR'
    
    sent_counts=Counter()
    word_en_counts=Counter()
    word_de_counts=Counter()
    for root, dirs, files in os.walk(corpus_dir_en_de):
        
        for fname in files:
            
            if fname.startswith('sent.'):
                print ('processing', fname)
                with open (os.path.join(root,fname)) as f:
                    with open(os.path.join(corpus_dir_en,fname),'w') as f_en:
                              with open(os.path.join(corpus_dir_de,fname),'w') as f_de:
                                    for line in f:
                                        line=line.strip()
                                        
#                                         words=line.split()
                                        en_line,de_line=line.split('\t')
                                        if seg_flag=='seg':
                                         en_line,de_line,en_ws,de_ws=sents2segwords(''.join(en_line.split()).decode('utf-8'),''.join(de_line.split()).decode('utf-8'))
                                        else:
                                         en_ws=en_line.split()
                                         de_ws=de_line.split()
#                                         de_line=line[(len(line)-1)/2+1:]
                                        f_en.write(en_line+'\n'.encode('utf-8'))
                                        f_de.write(de_line +'\n'.encode('utf-8'))

                                        sent_counts[fname] += 1
                                        for word in en_ws:
                                            word_en_counts[word] += 1
                                        for word in de_ws:
                                            word_de_counts[word]+=1

    
    for corpus_d in [corpus_dir_en, corpus_dir_de]:
        word_counts=word_en_counts if corpus_d==corpus_dir_en else word_de_counts
      
        sent_counts_file = open(corpus_d+'/'+SENT_COUNTS_FILENAME, 'w')
        word_counts_file = open(corpus_d+'/'+WORD_COUNTS_FILENAME, 'w')
        totals_file = open(corpus_d+'/'+TOTAL_COUNTS_FILENAME, 'w')

        for num_filename, count in sent_counts.most_common():
            sent_counts_file.write(num_filename+'\t'+str(count)+'\n')

        for word, count in word_counts.most_common():
            if seg_flag=='seg':
                word_counts_file.write(word.encode('utf-8')+'\t'+str(count)+'\n')
            else:
                word_counts_file.write(word+'\t'+str(count)+'\n')

        totals_file.write('total sents read: {}\n'.format(sum(sent_counts.itervalues())))
        totals_file.write('total words read: {}\n'.format(sum(word_counts.itervalues())))

        sent_counts_file.close()
        word_counts_file.close()
        totals_file.close()
