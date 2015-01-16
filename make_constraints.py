
#!/usr/bin/env python

"""
make_constraints.py: Turn the classifier's output into a constraints
file to use with a parser. Outputs three files with different
threshholds for positive/negative answers.

Author: Joseph Irwin

To the extent possible under law, the person who associated CC0 with
this work has waived all copyright and related or neighboring rights
to this work.
http://creativecommons.org/publicdomain/zero/1.0/
"""

import sys


PREC_THRESH = 0.75
REC_THRESH = 0.8

model_name = sys.argv[1]
output_name = sys.argv[2]

lengths = [int(line.strip().split()[-1]) for line in open(model_name + '.boundaries')]
answers = [int(line.strip().split()[0]) for line in open(model_name + '.dat')]
outputs = [(int(row[0]), float(row[1])) for line in open(output_name) for row in [line.strip().split()]]

def filter_prec(label, score):
    if label == 1 and score > PREC_THRESH:
        return 1
    else:
        return -1

def filter_rec(label, score):
    if label == -1 and score > REC_THRESH:
        return -1
    else:
        return 1

def evaluate(ans, out):
    tp, tn, fp, fn = 0,0,0,0
    for a,o in zip(ans, out):
        if a == 1 and o == 1:
            tp += 1
        elif a == -1 and o == -1:
            tn += 1
        elif a == 1 and o == -1:
            fn += 1
        else:
            fp += 1
    acc = float(tp + tn) / sum((tp,tn,fp,fn))
    prec = float(tp) / (tp + fp)
    rec = float(tp) / (tp + fn)
    f1 = 2 * prec * rec / (prec + rec)
    return (acc, prec, rec, f1)


print("System Output:")
print("Acc:{0:.2f} Prec:{1:.2f} Rec:{2:.2f} F1:{3:.2f}".format(*evaluate(answers, (o[0] for o in outputs))))
print("Higher Precision (score > {}):".format(PREC_THRESH))
print("Acc:{0:.2f} Prec:{1:.2f} Rec:{2:.2f} F1:{3:.2f}".format(*evaluate(answers, (filter_prec(*o) for o in outputs))))
print("Higher Recall (score > {}):".format(REC_THRESH))
print("Acc:{0:.2f} Prec:{1:.2f} Rec:{2:.2f} F1:{3:.2f}".format(*evaluate(answers, (filter_rec(*o) for o in outputs))))
