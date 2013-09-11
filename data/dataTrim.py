#!/usr/bin/python
import sys

def dataTrim( filename ):
    f = open(filename)
    lines = f.read().strip()
    lines = lines.replace('\t', ',')
    lines = lines.split('\n')
    f.close()
    for i in range( len(lines) ):
        lines[i] = lines[i].split(',')[:10]
    return lines

def combine( data ):
    for i in range( len(data) ):
        data[i] = ','.join(data[i])
    return '\n'.join(data)


d = dataTrim(sys.argv[1])
print combine( d );
