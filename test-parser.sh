
#!/bin/sh

DIR=$(dirname $0)
MAIN=edu.stanford.nlp.parser.lexparser.LexicalizedParser
MEM=-mx3g
TB=$1

parallel -j4 --results log "java $MEM -cp $DIR/corenlp.jar $MAIN -test $TB -indConstMinSentLen {1} -independentConstraintsFile {2} -loadFromTextFile grammar.txt" ::: 0 20 30 40 1000 ::: constraints.default constraints.precision constraints.recall test.boundaries
