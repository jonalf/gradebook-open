#!/usr/bin/python
import sys

#USE THIS VERSION FOR NON DEADALUS IMPORTS

CLASS = 5
SECTION = 6
FIRST = 2
LAST = 1
OSIS = 0
TEACHER = 7
HR = 3
PERIOD = 9

def dataConvert( filename ):
    f = open(filename)
    lines = f.read().strip()
    lines = lines.replace('* ', '')
    lines = lines.split('\n')
    f.close()
    for i in range( len(lines) ):
        l = lines[i].split(',')
        lines[i] = [ l[CLASS], l[SECTION], l[PERIOD], l[TEACHER], l[LAST].capitalize(), l[FIRST].capitalize(), l[OSIS], l[HR], l[OSIS], 'NA']
        #lines[i] = [ l[5], l[6], l[9], l[7], l[1].title(), l[2].title(), l[0], l[3], l[0], 'NA']
    return lines

def combine( data ):
    for i in range( len(data) ):
        data[i] = ','.join(data[i])
    return '\n'.join(data)


d = dataConvert(sys.argv[1])
print combine( d );
