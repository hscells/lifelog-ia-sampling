#!/usr/bin/python

import sys

if len(sys.argv) == 3:
    ifile = sys.argv[1]
    ofile = sys.argv[2]
else:
    print "process-fv.py <in file> <out file>"
    sys.exit(1)

fv = open(ifile, "rb")
print "Reading file..."
f = fv.read()

print "Processing data..."
f = ''.join(("{\n", f))
f = f.replace("\n", "")
f = f.replace("]", "],\n")
f = f.replace(";", ",")
f = f[:-2]
f = ''.join((f, "\n}"))

print "Writing data..."
out = open(ofile, "wb")
out.write(f)

print "Done!"
