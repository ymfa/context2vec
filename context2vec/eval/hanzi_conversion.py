# -*- coding: utf-8 -*-

import sys
import numpy as np
import pandas as pd
from codecs import open
from collections import Counter, defaultdict
from context2vec.common.model_reader import ModelReader
import cupy as cp
from chainer import cuda
import math


import re

def sent_seg(sent):
    sent_list=re.findall(ur'[^！。？!?\n]*(?:[！。？!?\n])*', sent)
    return sent_list

def extract_sent(input_sent,position):
    sent_lst=sent_seg(input_sent)
    
    start_i=0
    end_i=0
    for sent in sent_lst:
        end_i+=len(sent)
        if position >=start_i and position < end_i:
            if len(sent)<=1:
                return input_sent,position
            else:
                position=position-start_i
                return sent,position
        else:
            start_i+=len(sent)

class SentGenerator(defaultdict):
    def __init__ (self,item_type,batchsize):
        super(SentGenerator, self).__init__(item_type)
        self.batchsize=batchsize
        self.sent_ls=[]
    def sent_generator(self,a_list):
        
            for i in a_list:
                yield i
                
    def convert_to_generator(self,batchsize):
        self.sent_ls=[]
        for sent_l in self:
            repeat=int(math.ceil(float(len(self[sent_l]))/self.batchsize))
            self.sent_ls+=[sent_l]*repeat
            self[sent_l]=self.sent_generator(self[sent_l])
        np.random.seed(1034)
        np.random.shuffle(self.sent_ls) 
        
def batch_data(line_list,batchsize):
    sent_l2line_is=SentGenerator(list,batchsize)
    for line_i,line in enumerate(line_list):
#         print (list(line))
        sent_l=len(list(line))
        sent_l2line_is[sent_l].append(line_i)
#     print (sent_l2line_is.keys())
    sent_l2line_is.convert_to_generator(batchsize)
    return sent_l2line_is


def read_batch(f1, simp_lines,batchsize, word2index1):        
    batch = []
    line_inds=[]
    while len(batch) < batchsize:
        try:
            line_i=next(f1)
            line1 = simp_lines[line_i]
            
        except StopIteration:
            print ('{0} completed'.format(f1))
            return batch,line_inds
        if not line1: break
        sent_words1 = list(line1)
#         print (sent_words1)
        sent_inds1 = []
        for word in sent_words1:
#             print (word)
            word= word.encode('utf-8')
            if word in word2index1 :
                
                ind = word2index1[word]
            else:
                ind = word2index1['<UNK>']
            sent_inds1.append(ind)
        
        batch.append(sent_inds1)
        line_inds.append(line_i)
    return batch,line_inds

def next_batch(sent_l2line_is,simp_lines,batchsize):
    
    for sent_l in sent_l2line_is.sent_ls:
#         if model_f.endswith('s2tw'):                          
#             sent_arr,line_inds=read_batch(sent_l2line_is[sent_l],simp_lines,batchsize,None)
#         else:
        sent_arr,line_inds=read_batch(sent_l2line_is[sent_l],simp_lines,batchsize,mr.word2index1)
        if sent_arr==[]:
            continue
        else:
            yield xp.array(sent_arr),line_inds
# sent_ys = self._contexts_rep(sent_arr)


def replace_unk(orig):
    orig_out=[]
    for line in orig:
        line=line.replace('<UNK>','U')
        orig_out.append(line)
    return orig_out


if __name__ == '__main__':

    if len(sys.argv) < 5:
        sys.stderr.write("Usage: %s <csv-filename> <conversion-table> <model-params-filename> [gpu] [batchsize] \n" % sys.argv[0])
        sys.exit(1)

    csv_filename = sys.argv[1]
        
    model_f=sys.argv[3].split('/')[-1]
    out_filename = csv_filename.rsplit('.', 1)[0]+'-'+model_f
    
    print out_filename
    
    


    try:
        gpu = int(sys.argv[4])
    except:
        gpu = -1
    if gpu >= 0:
        cuda.check_cuda_available()
        cuda.get_device(gpu).use()
    xp = cp if gpu >= 0 else np
    if model_f.endswith('s2tw'):
        opencc_out=open(sys.argv[3],mode='r', encoding='utf-8')
    else:
        mr = ModelReader(sys.argv[3],gpu)

    
    #batchsize
    batchsize=int(sys.argv[5])

    # read conversion table
    trad2simp, var2norm = dict(), dict()
    with open(sys.argv[2], 'r', encoding='utf-8') as f:
        for line in f:
            simp, trad = line.strip().split('\t')
            variant_mode, prev_trad = False, None
            for char in trad:
                if char == '(': variant_mode = True
                elif char == ')': variant_mode = False
                elif variant_mode: var2norm[char] = prev_trad
                else:
                    trad2simp[char] = simp
                    prev_trad = char

    def normalize(c):
        return var2norm.get(c, c)

    simp2trad = defaultdict(set)
    for k, v in trad2simp.items(): simp2trad[v].add(k)
    for k, v in var2norm.items(): simp2trad[trad2simp[v]].add(k)
    
    if not model_f.endswith('s2tw'):
        simp2trad_new = defaultdict(list)
        for k, v in simp2trad.items():
            for trad in v:
                try:
                    trad_embed = mr.w[mr.word2index2[trad.encode('utf-8')]]
                except:
                    print "Traditional character {0} does not have an embedding." .format( trad.encode('utf-8'))
                    continue
                simp2trad_new[k].append((trad, trad_embed))
        simp2trad = simp2trad_new


    # run conversion test
    def predict(simp_sentence, pos,contexts,line_current_i):
#         simp_sentence,pos=extract_sent(simp_sentence,pos)
#         tokens = [t.encode('utf-8') for t in simp_sentence]
#         tokens = [t if t in mr.word2index1 else '<UNK>' for t in tokens]
#        context_embed = xp.array(mr.model.context2vec(tokens, pos))
#         print (simp_sentence.encode('utf-8'))
#         print (contexts)
        context_embed=contexts[pos].data[line_current_i]
        context_embed = context_embed / xp.sqrt((context_embed * context_embed).sum())
        simp = simp_sentence[pos]
        bestTrad, bestScore = None, None
        
        for trad, trad_embed in simp2trad[simp]:
            score = xp.dot(context_embed, xp.array(trad_embed))  # both already normalized
            
            if float(score) > bestScore:
                bestTrad, bestScore = trad, score

        return bestTrad

    csv = pd.read_csv(csv_filename, encoding='utf-8')
    trad_error_count, trad_count = Counter(), Counter()
    error_list = pd.DataFrame(columns=['char_res', 'orig_char', 'gold_char', 'char_index',
                                       'res', 'orig', 'gold', 'orig_line_num'])
    error_list.to_csv(out_filename + '_c2v_errors.csv', index=False, encoding='utf-8')

    
    #read in batches of sentences
    csv['orig']=replace_unk(csv['orig']) #replace <UNK> with U
    if model_f.endswith('s2tw'):
        print ('opencc')
        batch=[([],range(len(csv['orig'])))]
    else:
        batch_sent_generator=batch_data(csv['orig'],batchsize)
        batch=next_batch(batch_sent_generator,csv['orig'],batchsize)
    
    for sent_arr,line_inds in batch:
        if not model_f.endswith('s2tw'):
            mr.model.reset_state()
            contexts=mr.model._contexts_rep(sent_arr) #a batch of context representations
    
        for line_current_i,line_i in enumerate(line_inds):
    #     for i, row in csv.iterrows():
#             print (line_i),
            pos_lst = str(csv['char_index'][line_i]).split('-')
            pos_lst=[p for p in pos_lst if p!='']
            gold_chars=list(csv['gold_char'][line_i])
            orig=csv['orig'][line_i]
            
#             orig_line_nums=[i for i in str(csv['orig_line_num'][line_i]).split('-') if i !='']
           
            if model_f.endswith('s2tw'):
                  opencc_line=opencc_out.readline() 
            for i,pos in enumerate(pos_lst):
                pos=int(pos)
                if orig[pos] not in simp2trad:
                    print ('warning! {0} not in simp2trad'.format(orig[pos].encode('utf-8')))
                    continue
                gold_char = normalize(gold_chars[i])
                
                if not model_f.endswith('s2tw'):
                    pred_char_raw = predict(orig,pos,contexts,line_current_i)
                	#pred_char_raw=gold_char
                else:
                    pred_char_raw=opencc_line[pos]
                
                pred_char = normalize(pred_char_raw)
                trad_count[gold_char] += 1
                try:
                    print "%s%s%s" % (gold_char.encode('utf-8'), pred_char.encode('utf-8'),line_i),
                    if line_current_i%100==0 and line_current_i>100:
                        print ''
                except AttributeError:
                    print pos,gold_char.encode('utf-8'),pred_char_raw,pred_char,orig.encode('utf-8')
                    sys.exit(1)
                if gold_char != pred_char:
                    #print ('diff')
                    orig_char = orig[pos]
                    error_list.loc[1] = [pred_char, orig_char, gold_char, pos,
                                                       pred_char_raw, orig, csv['gold'][line_i], csv['orig_line_num'][line_i]]
                    error_list.to_csv(out_filename + '_c2v_errors.csv', index=False, encoding='utf-8',mode='a', header=False)
                    trad_error_count[gold_char] += 1
    print


    # make report
    report = pd.DataFrame(columns=['char_gold', 'char_orig', 'error_num', 'total', 'error_rate'])
    total_error, total_count = 0, 0
    for trad, simp in trad2simp.items():
        error, count = trad_error_count[trad], trad_count[trad]
        if count == 0: continue
        report.loc[len(report)] = [trad, simp, error, count, "%.3f" % (float(error) / count)]
        total_error += error
        total_count += count
    report.sort_values(['char_orig', 'error_rate', 'char_gold'], inplace=True)
    report.loc[len(report)] = ['Total', 'Total', total_error, total_count, "%.3f" % (total_error / total_count)]
    report.to_csv(out_filename + '_c2v_report.csv', index=False, encoding='utf-8')
