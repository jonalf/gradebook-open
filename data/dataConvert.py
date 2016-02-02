#!/usr/bin/python
import sys

def dataConvert( filename ):
    f = open(filename)
    lines = f.read().strip()
    lines = lines.replace('* ', '')
    lines = lines.split('\n')
    f.close()
    for i in range( len(lines) ):
        l = lines[i].split(',')
        lines[i] = [ l[5], l[6], l[9], l[7], l[1].title(), l[2].title(), l[0], l[3], l[0], 'NA']
    return lines

def combine( data ):
    for i in range( len(data) ):
        data[i] = ','.join(data[i])
    return '\n'.join(data)


d = dataConvert(sys.argv[1])
print combine( d );
