#!/bin/sh

echo "Creating training data..."
python ~/Git/nlp2015/pre.py ~/Data/parsing/wsj/wsj02-21.mrg train --train
python ~/Git/nlp2015/make_data.py train
echo "Creating testing data..."
python ~/Git/nlp2015/pre.py ~/Data/parsing/wsj/wsj22.mrg test
python ~/Git/nlp2015/make_data.py test train
echo "Training and testing classifier..."
opal -O 4 -P train.dat model test.dat >out
python ~/Git/nlp2015/make_constraints.py test out | tee results-classifier
