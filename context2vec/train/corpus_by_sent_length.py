# -*- coding: utf-8 -*-

'''
Converts a single large corpus file into a directory, in which for every sentence length k there is a separate file containing all sentences of that length. 
'''

import sys
import os
from collections import Counter
from context2vec.common.defs import SENT_COUNTS_FILENAME, WORD_COUNTS_FILENAME, TOTAL_COUNTS_FILENAME
import re

import random

def get_file(sub_files, corpus_dir, num_filename):
    if num_filename not in sub_files:
        full_file_name = corpus_dir + '/' + num_filename
        sub_files[num_filename] = open(full_file_name, 'w')        
    return sub_files[num_filename]

def sent_seg_small(sent):
    sent_list=re.findall(ur'[^、，,；;！。？!?\n]+(?:[、,;，；！。？!?\n])*', sent)
    if len(sent_list)>1:
        sent_list.append(sent)
    return sent_list

def sent_permutate(sent):
    new_sents=[sent]
    sent=sent.split()
    itera=len(sent)/5
    if itera <2:
        return new_sents
    else:
        
        for i in range(itera):

            pos=random.randint(0,len(sent))
            win=random.randint(5,9)
            after=len(sent)-1-pos
            if after>=pos:
                end=pos+win+1
                if end>len(sent):
                    end=len(sent)
                
                new_sents.append(' '.join(sent[pos:end]))
            else:
                start=pos-win
                if start<0:
                    start=0
                new_sents.append(' '.join(sent[start:pos]))
    return new_sents
        
if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        print "usage: %s <corpus-file> [max-sent-len] [file total lines]"  % (sys.argv[0])
        sys.exit(1)
        
    corpus_file = open(sys.argv[1], 'r')
    if len(sys.argv) > 2:
        max_sent_len = int(sys.argv[2])
    else:
        max_sent_len = 128 
        
    print 'Using maximum sentence length: ' + str(max_sent_len)

    if len(sys.argv) > 3:
        
        total_lines=int(sys.argv[3])
        random.seed(1)
        test_lines_i=random.sample(list(range(total_lines)),int(total_lines*0.2))
        test_lines_i={i:1 for i in test_lines_i}
    else:
        test_lines_i={}
        
   
    corpus_dir = sys.argv[1]+'.DIR'
    os.makedirs(corpus_dir)
    sent_counts_file = open(corpus_dir+'/'+SENT_COUNTS_FILENAME, 'w')
    word_counts_file = open(corpus_dir+'/'+WORD_COUNTS_FILENAME, 'w')
    totals_file = open(corpus_dir+'/'+TOTAL_COUNTS_FILENAME, 'w')
    test_file=open(corpus_dir+'/'+'test_sents', 'w')
    
    sub_files = {}
    sent_counts = Counter()
    word_counts = Counter()
    print ('start..')
    line_num=0
    for line in corpus_file:
        if line_num%100000==0 and line_num>=100000:
            print '.',
        if line_num in test_lines_i:
            test_file.write(line)
            line_num+=1
            continue
        line_num+=1
#         if line_num%10000==0 and line_num>=10000:
#             print '.',
       
           
        line=line.replace('<unk>','<UNK>')
        #sent_list=sent_seg_small(line.decode('utf-8'))
        sent_list=[line.decode('utf-8')]
        for sents in sent_list:
            sents=[sents.strip()]
            #sents=sent_permutate(sents)
            for sent in sents:
                sent=sent.strip().encode('utf-8')
                words = sent.split()
                wordnum = len(words)
                if wordnum > 1 and wordnum <= max_sent_len:
                    num_filename = 'sent.' + str(wordnum)
                    sub_file = get_file(sub_files, corpus_dir, num_filename)
                    #sent=sent.decode('utf8')
                    sub_file.write(sent+'\n')
                    sent_counts[num_filename] += 1
                    for word in words:
                        word_counts[word] += 1
               
    for sub_file in sub_files.itervalues():
        sub_file.close()
        
    for num_filename, count in sent_counts.most_common():
        sent_counts_file.write(num_filename+'\t'+str(count)+'\n')
    
    for word, count in word_counts.most_common():
        word_counts_file.write(word+'\t'+str(count)+'\n')
    
    totals_file.write('total sents read: {}\n'.format(sum(sent_counts.itervalues())))
    totals_file.write('total words read: {}\n'.format(sum(word_counts.itervalues())))
    
    corpus_file.close()
    sent_counts_file.close()
    word_counts_file.close()
    totals_file.close()
    test_file.close()
    
    print 'Done'
