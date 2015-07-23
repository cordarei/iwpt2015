#lang racket
(require plot)


(define (O2 x) (* x x))
(define (O3 x) (* x x x))
(define (Oavg x) (expt x 2.31))
(define (make-parser-time-complexity-plot)
  (parameterize ([plot-x-ticks no-ticks]
                 [plot-y-ticks no-ticks])
  (plot (list #;(axes)
              (function-interval O2 O3 )
              (function Oavg 0 10 #:style 'dot))
        #:x-label "" #:y-label ""
        #;(#:out-file "parser-time-complexity.pdf"
        #:out-kind 'pdf))))

(make-parser-time-complexity-plot)

(define features
  '(
    ( "p"  80.73  70.49 )
    ( "P0"  51.69  83.98 )
    ( "p,P0"  87.38  75.65 )
    ( "p,P1"  78.38  85.38 )
    ( "p,P2"  84.25  80.76 )
    ( "p,P3"  89.47  71.95 )
    ( "p,P0,P1"  88.95  76.16 )
    ( "p,P0,P2"  88.28  73.60 )
    ( "p,P0,P3"  88.81  70.99 )
    ( "p,P1,P2"  80.99  85.21 )
    ( "p,P1,P3"  89.05  75.74 )
    ( "p,P0,P1,P2,P3"  86.89  77.49 )
    ))

(define (feat-to-point-label ft)
  (point-label (apply vector (cdr ft)) (car ft)))

(define (make-feature-conf-plot)
  (parameterize ([plot-x-ticks (linear-ticks)])
   (plot (append (map feat-to-point-label features)
                 (list #;(x-axis 70 #:ticks? #t #:labels? #t)
                       (point-label (vector 89.05  75.74 ) "p,P1,P3" #:color "red")))
        #:x-min 50 #:x-max 100
        #:y-min 65 #:y-max 100
        #:x-label "Precision" #:y-label "Recall"
        #;(#:out-file "feature-conf-plot.pdf" #:out-kind 'pdf)
        )))

(make-feature-conf-plot)