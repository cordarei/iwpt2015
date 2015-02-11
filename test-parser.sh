#!/bin/sh

DIR=$(dirname $0)
MAIN=edu.stanford.nlp.parser.lexparser.LexicalizedParser
MEM=-mx3g
TB=$1
SENT_LENS='0 20 30 40 1000'
CONSTRAINTS='constraints.default constraints.precision constraints.recall constraints.maxprec test.boundaries'

parallel -j4 --results log java $MEM -cp $DIR/corenlp.jar $MAIN -test $TB -indConstMinSentLen {1} -independentConstraintsFile {2} -loadFromTextFile grammar.txt ::: $SENT_LENS ::: $CONSTRAINTS >/dev/null 2>/dev/null

print_total_rules() {
    awk '/Total rules/ {total += $4} END {print total}' < $1 | tr -d '\n'
}

print_total_traversals() {
    awk '/Total traversals/ {total += $4} END {print total}' < $1 | tr -d '\n'
}

print_total_time() {
    cat $1 | grep 'Testing on treebank done' | grep '[0-9][0-9.]\+' -o | tr -d '\n'
}

print_f1() {
    cat $1 | grep 'pcfg' | grep summary | grep 'F1: [0-9][0-9.]*' -o | sed 's/F1: //' | tr -d ' \n'
}

print_failed() {
  cat $1 | grep 'Parse failed' | wc -l | tr -d ' \n'
}

print_parser_results() {
    parser_output="log/1/$1/2/$2/stderr"
    echo -n '| '
    echo -n $1
    echo -n ' | '
    echo -n $2
    echo -n ' | '
    print_total_time $parser_output
    echo -n ' | '
    print_total_rules $parser_output
    echo -n ' | '
    print_total_traversals $parser_output
    echo -n ' | '
    print_f1 $parser_output
    echo -n ' | '
    print_failed $parser_output
    echo ' |'
}

for len in $SENT_LENS; do
    for con in $CONSTRAINTS; do
        print_parser_results $len $con
    done
done
