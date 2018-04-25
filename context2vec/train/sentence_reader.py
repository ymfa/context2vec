import math
import collections
import numpy as np

from context2vec.common.defs import Toks, SENT_COUNTS_FILENAME, WORD_COUNTS_FILENAME, LANG1, LANG2


def read_batch(f1, f2, batchsize, word2index1, word2index2):        
    batch = []
    while len(batch) < batchsize:
        line1 = f1.readline()
        line2 = f2.readline()
        if not line1: break
        sent_words1 = line1.strip().split()
        sent_words2 = line2.strip().split()
        assert(len(sent_words1) > 1 and len(sent_words2) == len(sent_words1))
        sent_inds1 = []
        for word in sent_words1:
            if word in word2index1:
                ind = word2index1[word]
            else:
                ind = word2index1['<UNK>']
            sent_inds1.append(ind)
        sent_inds2 = []
        for word in sent_words2:
            if word in word2index2:
                ind = word2index2[word]
            else:
                ind = word2index2['<UNK>']
            sent_inds2.append(ind)
        batch.append((sent_inds1, sent_inds2))
    return batch


class SentenceReaderDir(object):
    '''
    Reads a batch of sentences at a time from a corpus directory in random order.
    Assumes that the sentences are split into different files in the directory according to their word lengths.
    '''
    
    sent_counts_filename = SENT_COUNTS_FILENAME
    word_counts_filename = WORD_COUNTS_FILENAME

    def __init__(self, path, trimfreq, batchsize):
        '''
        Initialize reader.
        :param path: input directory
        :param trimfreq: treat all words with lower frequency than trimfreq as unknown words
        :param batchsize: the size of the minibatch that will be read in every iteration
        '''
        self.path_prefix = path
        self.path1 = "%s.%s.DIR" % (path, LANG1)
        self.path2 = "%s.%s.DIR" % (path, LANG2)
        self.batchsize = batchsize
        self.trimmed_word2count1, self.word2index1, self.index2word1 = self.read_and_trim_vocab(self.path1, trimfreq)
        self.trimmed_word2count2, self.word2index2, self.index2word2 = self.read_and_trim_vocab(self.path2, trimfreq)
        self.total_words = sum(self.trimmed_word2count1.itervalues()) + sum(self.trimmed_word2count2.itervalues())
        self.fds = []
        
    def open(self):
        self.fds = []
        with open(self.path1+'/'+self.sent_counts_filename) as f:
            for line in f:
                [filename, count] = line.strip().split()
                batches = int(math.ceil(float(count) / self.batchsize))
                fd = open(self.path1+'/'+filename, 'r'), open(self.path2+'/'+filename, 'r')
                self.fds = self.fds + [fd]*batches
        np.random.seed(1034)
        np.random.shuffle(self.fds)
    

    def close(self):
        fds_set = set(self.fds)
        for f1, f2 in fds_set:
            f1.close()
            f2.close()
                        
            
    def read_and_trim_vocab(self, path, trimfreq):
        word2count = collections.Counter()
        with open(path+'/'+self.word_counts_filename) as f:
            for line in f:
                [word, count] = line.strip().lower().split()
                word2count[word] = int(count)
    
        trimmed_word2count = collections.Counter()
        index2word = {Toks.UNK:'<UNK>', Toks.BOS:'<BOS>', Toks.EOS:'<EOS>'}
        word2index = {'<UNK>':Toks.UNK, '<BOS>':Toks.BOS, '<EOS>':Toks.EOS}
        unknown_counts = 0
        for word, count in word2count.iteritems():
            if count >= trimfreq and word.lower() != '<unk>' and word.lower() != '<rw>':    
                ind = len(word2index)
                word2index[word] = ind
                index2word[ind] = word
                trimmed_word2count[ind] = count
            else:
                unknown_counts += count
        trimmed_word2count[word2index['<BOS>']] = 0
        trimmed_word2count[word2index['<EOS>']] = 0
        trimmed_word2count[word2index['<UNK>']] = unknown_counts
        
        return trimmed_word2count, word2index, index2word

       
    def next_batch(self):                
        for fd1, fd2 in self.fds:
            batch = read_batch(fd1, fd2, self.batchsize, self.word2index1, self.word2index2)
            yield batch
 
 
 
if __name__ == '__main__':
    import sys   
    reader = SentenceReaderDir(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]))
    
    for i in range(2):
        print 'epoc', i
        reader.open()
        i = 0
        j = 0
        for batch in reader.next_batch():
            if i < 3:
                print batch
                print
            i += 1
            j += len(batch)
        print 'batches', i
        print 'sents', j
        reader.close()
                     
