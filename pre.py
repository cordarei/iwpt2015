#!/usr/bin/env python

"""
pre.py: Preprocess script

Author: Joseph Irwin

To the extent possible under law, the person who associated CC0 with
this work has waived all copyright and related or neighboring rights
to this work.
http://creativecommons.org/publicdomain/zero/1.0/
"""


from __future__ import print_function

import ptb
import sys

ptb_file = sys.argv[1]
model_name = sys.argv[2]
do_train = '--train' in sys.argv

trees = lambda: ptb.parse(open(ptb_file))
sents = lambda: (ptb.make_parsed_sent(t) for t in trees())

def boundaries(s):
    return [s.tree.spans[i].end for i in s.tree.edges[1][1]]

def pos_level1(tag):
    if tag[0] in ('N', 'V'):
        return tag[0]
    elif tag == 'PRP':
        return 'N'
    else:
        return 'X'

def pos_level2(tag):
    l1 = pos_level1(tag)
    if l1 != 'X':
        return l1
    if tag[0] in ('I', 'T', ',', ':', '.'):
        return tag[0]
    if tag[0] == 'W' and tag[-1] != '$':
        return 'W'
    if tag == 'RP':
        return 'I'
    if tag == 'CC':
        return 'C'
    return 'X'

def pos_level3(tag):
    l2 = pos_level2(tag)
    if l2 != 'X':
        return l2
    if tag[:2] == 'RB':
        return 'R'
    if tag[0] == 'J':
        return 'J'
    if tag in ('DT', 'PDT', 'PRP$', 'WP$'):
        return 'D'
    if tag in ("''", "``"):
        return 'Q'
    if tag in ('CD', '$', '#'):
        return '#'
    if tag[0] == '-':
        return 'B'
    return 'X'


words = []
tags = []
bounds = []

for s in sents():
    words.append(list(s.words()))
    tags.append(list(s.tags()))
    bounds.append(boundaries(s))

def dump(filename, data):
    with open(filename, 'w') as f:
        for row in data:
            print(' '.join(str(c) for c in row), file=f)

dump(model_name + '.words', words)
dump(model_name + '.tags', tags)
dump(model_name + '.boundaries', bounds)

if do_train:
    postags = set(t for ts in tags for t in ts)
    postable = sorted([(t, pos_level1(t), pos_level2(t), pos_level3(t)) for t in postags], key=lambda x:x[1:])
    dump(model_name + '.postable', postable)

posmap = dict( (t[0],t) for line in open('train.postable') for t in [line.strip().split()] )

dump(model_name + '.tags1', ([posmap[t][1] for t in ts] for ts in tags))
dump(model_name + '.tags2', ([posmap[t][2] for t in ts] for ts in tags))
dump(model_name + '.tags3', ([posmap[t][3] for t in ts] for ts in tags))
