
#!/usr/bin/env python

def uniq(lst):
    from itertools import groupby
    return [k for k,g in groupby(lst)]

def ngrams(seq, n=2):
    ret = []
    ngram=[]
    it = iter(seq)
    for i in it:
        ngram.append(i)
        if len(ngram) == n:
            ret.append(list(ngram))
            ngram = ngram[1:]
    return ret

def feature_format(name, value):
    return '{name}:<{value}>'.format(name=name, value=value)
def local_pos_features(tags, tags1, tags2, tags3, boundary, postable):
    WINDOW_SIZE = 3
    fs = set()
    mkname = lambda l: 'local_pos_{0}_{1}'.format(*l)
    mkval = lambda vs: '_'.join(vs)
    def mkfeats_helper(vals, lbl):
        return (feature_format(mkname(lbl), mkval(v)) for v in vals)
    left_tags = tags[:boundary]
    right_tags = tags[boundary:]
    for i in range(1, WINDOW_SIZE + 1):
        if len(left_tags) == i:
            fs.add(feature_format('local_pos_all_left', mkval(left_tags)))
        elif len(left_tags) > i:
            fs.add(feature_format('local_pos_suffix_left', mkval(left_tags[-i:])))
        if len(right_tags) == i:
            fs.add(feature_format('local_pos_all_right', mkval(right_tags)))
        elif len(right_tags) > i:
            fs.add(feature_format('local_pos_prefix_right', mkval(right_tags[:i])))
    return fs
def global_pos_features(tags, tags1, tags2, tags3, boundary, postable):
    fs = set()

    def mkfeats_helper(vals, lbl):
        mkname = lambda l: 'global_pos_{0}_{1}_{2}gram'.format(*l)
        mkval = lambda vs: '_'.join(vs)
        return (feature_format(mkname(lbl), mkval(v)) for v in vals)
    def mkfeats(seq, typ, side, N=3):
        return [
            f
            for n,gram in ((1, 'uni'),(2, 'bi'),(3,'tri'),(4, '4-'))[:N]
            for f in mkfeats_helper(ngrams(seq, n), (typ, side, gram))
        ]
    def slim(tags):
        return [t for t in tags if t != 'X']
    def full(tags):
        return tags

    left_tags = tags[:boundary]
    right_tags = tags[boundary:]
    #level 0 (raw POS tags)
    fs.update(mkfeats(left_tags, 'level0_raw', 'left'))
    fs.update(mkfeats(right_tags, 'level0_raw', 'right'))
    #level 1
    left_l1 = uniq(tags1[:boundary])
    right_l1 = uniq(tags1[boundary:])
    # slim
    fs.update(mkfeats(uniq(slim(left_l1)), 'level1_slim', 'left'))
    fs.update(mkfeats(uniq(slim(right_l1)), 'level1_slim', 'right'))
    # full
    fs.update(mkfeats(full(left_l1), 'level1_full', 'left'))
    fs.update(mkfeats(full(right_l1), 'level1_full', 'right'))
    #level 2
    left_l2 = uniq(tags2[:boundary])
    right_l2 = uniq(tags2[boundary:])
    # slim
    fs.update(mkfeats(uniq(slim(left_l2)), 'level2_slim', 'left'))
    fs.update(mkfeats(uniq(slim(right_l2)), 'level2_slim', 'right'))
    # full
    fs.update(mkfeats(full(left_l2), 'level2_full', 'left'))
    fs.update(mkfeats(full(right_l2), 'level2_full', 'right'))
    #level 3
    left_l3 = uniq(tags3[:boundary])
    right_l3 = uniq(tags3[boundary:])
    # slim
    fs.update(mkfeats(uniq(slim(left_l3)), 'level3_slim', 'left'))
    fs.update(mkfeats(uniq(slim(right_l3)), 'level3_slim', 'right'))
    # full
    fs.update(mkfeats(full(left_l3), 'level3_full', 'left'))
    fs.update(mkfeats(full(right_l3), 'level3_full', 'right'))

    return fs
def make_feature_dict():
    from collections import defaultdict
    from itertools import count
    ids = count(1)
    return defaultdict(lambda: next(ids))

def write_feature_dict(filename, feature_dict):
    with open(filename, 'w') as file:
        for f,i in sorted(feature_dict.items()):
            print('{}\t{}'.format(f,i), file=file)

def read_feature_dict(filename):
    return dict(
        (f,int(i))
        for f,i in (
                line.strip().split('\t')
                for line in open(filename)
        )
    )
def format_instance(feats, featdict, label):
    def get(fd,k):
        try:
            return fd[k]
        except KeyError:
            return -1

    return '{label} {feats}'.format(
        label=label,
        feats=' '.join(
            '{}:{}'.format(i,v)
            for i,v in sorted([(get(featdict, f), 1) for f in feats])
            if i > 0
        )
    )

import sys

model_name = sys.argv[1]
trained_model_name = None
if len(sys.argv) > 2:
    trained_model_name = sys.argv[2]
postable_name = (trained_model_name or model_name) + '.postable'


tags = [[t for t in line.strip().split()] for line in open(model_name + '.tags')]
tags1 = [[t for t in line.strip().split()] for line in open(model_name + '.tags1')]
tags2 = [[t for t in line.strip().split()] for line in open(model_name + '.tags2')]
tags3 = [[t for t in line.strip().split()] for line in open(model_name + '.tags3')]
boundaries = [[int(b) for b in line.strip().split()] for line in open(model_name + '.boundaries')]
postable = dict( (t[0], t) for line in open(postable_name) for t in [line.strip().split()] )

feature_ids = (
    read_feature_dict(trained_model_name + '.features')
    if trained_model_name
    else make_feature_dict()
)

datafile = open(model_name + '.dat', 'w')

snum = -1
for ts,t1s,t2s,t3s, bs in zip(tags, tags1, tags2, tags3, boundaries):
    snum += 1
    for i in range(1, len(ts)):
        fs = set()
        fs.update(global_pos_features(ts, t1s, t2s, t3s, i, postable))
        fs.update(local_pos_features(ts, t1s, t2s, t3s, i, postable))
        print(format_instance(fs, feature_ids, 1 if i in bs else -1), file=datafile)

datafile.close()

if not trained_model_name:
    write_feature_dict(model_name + '.features', feature_ids)
