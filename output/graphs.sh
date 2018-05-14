#!/bin/sh
awk '{if ($NF ~ /Gbits/) print $3, $(NF-1)*1000;\
 else if ($NF ~ /Mbits/) print $3, $(NF-1);\
 else if ($NF ~/bits/) print $3, $(NF-1)/1000}' iperf-TCP-server-h2-h1.txt |sed s/-[0-9.]*/' '/|head -n -1 > server-TCP-bw.dat

#We add two seconds to x values since iperf started at second 2.
gnuplot -e "set terminal png; set output 'tcp-bw.png';\
  set xlabel 'time (seconds)';\
  set ylabel 'TCP bandwidth (Mbits/s)'; \
  set title 'Example of Link configuration modification';\
  plot 'server-TCP-bw.dat' using (\$1+2):2 with lines title 'TCP'"

