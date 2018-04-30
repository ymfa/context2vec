import sys
import numpy as np
import pandas as pd
from codecs import open
from collections import Counter, defaultdict
from context2vec.common.model_reader import ModelReader

if __name__ == '__main__':

    if len(sys.argv) < 4:
        sys.stderr.write("Usage: %s <csv-filename> <conversion-table> <model-params-filename> [gpu]\n" % sys.argv[0])
        sys.exit(1)

    csv_filename = sys.argv[1]
    model_f=sys.argv[3].split('/')[-1]
    out_filename = csv_filename.rsplit('.', 1)[0]+'-'+model_f
    print out_filename
    try:
        gpu = int(sys.argv[4])
    except:
        gpu = -1
    mr = ModelReader(sys.argv[3],gpu)



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
    def predict(simp_sentence, pos):
        tokens = [t.encode('utf-8') for t in simp_sentence]
        tokens = [t if t in mr.word2index1 else '<UNK>' for t in tokens]
        context_embed = mr.model.context2vec(tokens, pos)
        context_embed = context_embed / np.sqrt((context_embed * context_embed).sum())
        simp = simp_sentence[pos]
        bestTrad, bestScore = None, None
        for trad, trad_embed in simp2trad[simp]:
            score = np.dot(context_embed, trad_embed)  # both already normalized
            if score > bestScore:
                bestTrad, bestScore = trad, score
        return bestTrad

    csv = pd.read_csv(csv_filename, encoding='utf-8')
    trad_error_count, trad_count = Counter(), Counter()
    error_list = pd.DataFrame(columns=['char_res', 'orig_char', 'gold_char', 'char_index',
                                       'res', 'orig', 'gold', 'orig_line_num'])
    for i, row in csv.iterrows():
        pos = row['char_index']
        gold_char = normalize(row['gold_char'])
        pred_char_raw = predict(row['orig'], pos)
        pred_char = normalize(pred_char_raw)
        trad_count[gold_char] += 1
        print "%s%s" % (gold_char.encode('utf-8'), pred_char.encode('utf-8')),
        if gold_char != pred_char:
            orig_char = row['orig_char']
            error_list.loc[len(error_list)] = [pred_char, orig_char, gold_char, pos,
                                               pred_char_raw, row['orig'], row['gold'], row['orig_line_num']]
            trad_error_count[gold_char] += 1
    print
    error_list.to_csv(out_filename + '_c2v_errors.csv', index=False, encoding='utf-8')


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