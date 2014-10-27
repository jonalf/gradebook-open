from pymongo import Connection
from os import stat

import json

T_ARRAY = 0
T_NUMBER = 1
T_STRING = 2
T_DICTIONARY = 3

def newclass(code,sect,pd,teacher):
    rec = { 'code':code,
            'section':sect,
            'period':pd,
            'teacher':teacher,
            'rows':0,
            'cols':0,
            'seated':0,
            'term':'',
            'students':[],
            'assignments':{ 'work':[], 'tests':[], 'projects':[] },
            'tests':[],
            'projects':[],
            'work':[],
            'weights': { 'work':.2, 'tests':.4, 'projects':.4 },
            'options':[]
            }
    return rec

def newstudent(last,first,stuyid,hr,id,email):
    return {'last':last,
            'first':first,
            'nick':'',
            'stuyid':stuyid,
            'hr':hr,
            'id':id,
            'email':email,
            'row':0,
            'col':0,
            'absent':[],
            'late':[],
            'excused':[],
            'exlate':[],
            'assignments':{ 'work':[], 'tests':[], 'projects':[] },
            'work':[],
            'tests':[],
            'projects':[]
            }

def newstudent2(first, last, nick, stuyid, hr, id, email, row, col):
    return {'last':last,
            'first':first,
            'nick':nick,
            'stuyid':stuyid,
            'hr':hr,
            'id':id,
            'email':email,
            'row':row,
            'col':col,
            'absent':[],
            'late':[],
            'excused':[],
            'exlate':[],
            'assignments':{ 'work':[], 'tests':[], 'projects':[] },
            'work':[],
            'tests':[],
            'projects':[]
            }

def newassignment(name, points, maxp):
    return { 'name': name,
             'points': points,
             'max' : maxp,
             #new
             'public' : 0
             }

def newassignment2(name, points, maxp, apublic):
    if apublic == 'true':
        apublic = 1
    else:
        apublic = 0
    return { 'name': name,
             'points': points,
             'max' : maxp,
             #new
             'public' : apublic
             }

def newweights(types, weights):
    d = {}
    i = 0
    while i < len(types):
        d[ types[i] ] = weights[i]
        i+= 1
    return d
        
class db:
    """ 
    Connects to a mongodb

    the base unit is a class which contains 
    base level info and a list of students

    Each student contains student info and lists for tests,
    hw's attendance, etc.
    """

    def __init__(self):
        self.connection=Connection()
        self.db = self.connection.gradebook2

    
    def dropAllClasses(self):
        """
        Removes all the classes form the mongodb
        """
        self.db.classes.drop()

    def initialLoad(self,filename="../data/students-base-9-2013.csv"):
        """
        one time load of data into the mongodb
        If you do this multiple times you will have multiple
        copies in the database (mongo gives a unique _ID field if you
        add the same data multiple times
        """

        # empty out the old stories
        self.db.classes.drop()
        
        classes={}
        # code, sect, pd, teacher, last,first,id,email
        for line in open(filename).readlines():
            line=line.strip()
            (code,sect,pd,teacher,last,first,stuyid,hr,id,email)=line.split(',')
            classes.setdefault((code,sect),newclass(code,sect,pd,teacher))
            s=classes[(code,sect)]
            s['students'].append(newstudent(last,first,stuyid,hr,id,email))

        for k in classes:
            self.db.classes.insert(classes[k])

    def loadNewClass(self, filename):    
        classes = {}
        for line in open(filename).readlines():
            line=line.strip()
            (code,sect,pd,teacher,last,first,stuyid,hr,id,email)=line.split(',')
            classes.setdefault((code,sect),newclass(code,sect,pd,teacher))
            s=classes[(code,sect)]
            s['students'].append(newstudent(last,first,stuyid,hr,id,email))
        for k in classes:
            self.db.classes.insert(classes[k])

    def removeClass(self, csp, term):
        self.db.classes.remove( { 'code':csp[0], 
                                  'section':csp[1], 
                                  'period':csp[2],
                                  'term':term} )


    def transferAllWork(self):
        teachers = self.getTeachers()
        for t in teachers:
            classes = self.getAllClasses(t)
            terms = classes['terms']            
            for t in terms:
                if t != 'terms':
                    for c in classes[t]:
                        self.transferWork(c, t)

    def transferWork(self, csp, term):
        cls = self.getClass(csp, term)[0]
        for atype1 in cls['assignments'].keys():
            alist1 = cls[atype1]
            cls['assignments'][atype1] = alist1
        self.db.classes.update({'code':csp[0],
                                'section':csp[1],
                                'period':csp[2],
                                'term':term},
                                {'$set' : {'assignments':cls['assignments']}})      

        students = self.getStudents(csp, term)
        for s in students:
            for atype in s['assignments'].keys():
                alist = s[atype]
                s['assignments'][atype] = alist
            self.db.classes.update({'code':csp[0],
                                    'section':csp[1],
                                    'period':csp[2],
                                    'term':term,
                                    'students.id':s['id']},
                                   {'$set' : {'students.$.assignments':s['assignments']}})

    def getTeachers(self):
        teachers = [ x['teacher'] for x in self.db.classes.find()]
        t2=[]
        for t in teachers:
            if not t in t2:
                t2.append(t)
        return t2

    def getClasses(self,teacher, term):
        classes = [ (x['code'],x['section'],x['period']) for x in self.db.classes.find({'teacher':teacher, 'term':term})]
        return classes

    def getAllTermClasses(self, term):
        classes = [ (x['code'],x['section'],x['period']) for x in self.db.classes.find({'term':term})]
        return classes

    def getClasses2(self, teacher):
        classes = [ (x['code'],x['section'],x['period'],x['term']) for x in self.db.classes.find({'teacher':teacher})]
        return classes

    def getAllClasses(self, teacher):
        allClasses = {}
        classes = [ (x['code'],x['section'],x['period'], x['term']) for x in self.db.classes.find({'teacher':teacher})]        
        for c in classes:
            if c[3] not in allClasses.keys():
                allClasses[c[3]] = [c[:3]]
            else:
                allClasses[c[3]].append(c[:3])
            allClasses['terms'] = allClasses.keys()
        return allClasses

    def getClass( self, csp, term ):
        """
        csp is (code,section,period)
        maybe it should just be code and section
        """
        cls = [ x for x in self.db.classes.find({'code':csp[0],
                                                 'section':csp[1],
                                                 'period':csp[2],
                                                 'term':term},
                                                fields={'_id':False})]
        
        return cls

    def resizeClass( self, csp, term, newRows, newCols ):
        self.db.classes.update( { 'code':csp[0], 
                                  'section':csp[1], 
                                  'period':csp[2],
                                  'term':term},
                                { "$set" : { "rows" : newRows,
                                             "cols" : newCols }})
    def setSeated(self, csp, term,  b, rows, cols):
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term':term},
                                { "$set" : { "seated" : b,
                                             "rows" : rows,
                                             "cols" : cols }})

    def setSeat(self, csp, term, sid, row, col):
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term':term,
                                 'students.id':sid },
                                {'$set' : { 'students.$.row' : row,
                                            'students.$.col' : col }})

    def setMassAttendance(self, csp, term, absent, late, excused,exlate,date):

        for s in absent:
            a = self.getAttendance(csp, term, s, 'A')
            l = self.getAttendance(csp, term, s, 'L')
            e = self.getAttendance(csp, term, s, 'E')            
            el = self.getAttendance(csp,term, s, 'X')            
            if date not in e and date not in a:                
                self.setAttendance(csp, term, s, 'A', date)
                if date in l:
                    self.removeAttendance(csp, term, s, 'L', date)
                if date in el:
                    self.removeAttendance(csp, term, s, 'X', date)

        for s in late:
            a = self.getAttendance(csp, term, s, 'A')
            l = self.getAttendance(csp, term, s, 'L')
            e = self.getAttendance(csp, term, s, 'E')            
            el = self.getAttendance(csp,term, s, 'X')            
            if date not in e and date not in l and date not in el:
                self.setAttendance(csp, term, s, 'L', date)
                if date in a:
                    self.removeAttendance(csp, term, s, 'A', date)

        for s in exlate:
            a = self.getAttendance(csp, term, s, 'A')
            l = self.getAttendance(csp, term, s, 'L')
            e = self.getAttendance(csp, term, s, 'E')            
            el = self.getAttendance(csp, term, s, 'X')            
            if date not in el:                
                self.setAttendance(csp, term, s, 'X', date)
                if date in a:
                    self.removeAttendance(csp, term, s, 'A', date)
                if date in e:
                    self.removeAttendance(csp, term, s, 'E', date)
                if date in l:
                    self.removeAttendance(csp, term, s, 'L', date)

        for s in excused:
            a = self.getAttendance(csp, term, s, 'A')
            l = self.getAttendance(csp, term, s, 'L')
            e = self.getAttendance(csp, term, s, 'E')            
            self.setAttendance(csp, term, s, 'E', date)
            if date in a:
                self.removeAttendance(csp, term, s, 'A', date)
            if date in l:
                self.removeAttendance(csp, term, s, 'L', date)

    def getAttendance(self, csp, term, sid, mode):
        record = self.db.classes.find_one({'code':csp[0], 
                                           'section':csp[1],
                                           'period':csp[2],
                                           'term':term,
                                           'students.id':sid}, 
                                          {'students.$':1})
        record = record['students'][0]
        if mode == 'A':
            return record['absent']
        elif mode == 'E':
            return record['excused']
        elif mode == 'L':
            return record['late']
        elif mode == 'X':
            return record['exlate']
        
    def removeAttendance(self, csp, term, sid, mode, date):
        if mode == 'A':
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'term':term,
                                     'students.id':sid },
                                    {'$pull' : { 'students.$.absent':date}})
        elif mode == 'E':
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'term' : term,
                                     'students.id':sid },
                                    {'$pull' : { 'students.$.excused':date}})
        elif mode == 'L':
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'term' : term,
                                     'students.id':sid },
                                    {'$pull' : { 'students.$.late':date}})
        elif mode == 'X':
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'term' : term,
                                     'students.id':sid },
                                    {'$pull' : { 'students.$.exlate':date}})


    def setAttendance(self, csp, term, sid, mode, date):
        if mode == 'A':
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'term' : term,
                                     'students.id':sid },
                                    {'$push' : { 'students.$.absent':date}})
        elif mode == 'E':
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'term' : term,
                                     'students.id':sid },
                                    {'$push' : { 'students.$.excused':date}})
        elif mode == 'L':
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'term' : term,
                                     'students.id':sid },
                                    {'$push' : { 'students.$.late':date}})
        elif mode == 'X':
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'term' : term,
                                     'students.id':sid },
                                    {'$push' : { 'students.$.exlate':date}})

    def changeAllAttendance(self, csp, term, sid, a, l, e, el):
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term':term,
                                 'students.id':sid },
                                {'$set' : { 'students.$.absent':a}})
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term':term,
                                 'students.id':sid },
                                {'$set' : { 'students.$.late':l}})
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term':term,
                                 'students.id':sid },
                                {'$set' : { 'students.$.excused':e}})
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term':term,
                                 'students.id':sid },
                                {'$set' : { 'students.$.exlate':el}})
    
    def setMassGrades(self, csp, term, aname, atype, apublic, maxpoints, grades):
        found = False
        existing = self.db.classes.find_one( {'code':csp[0],
                                              'section':csp[1],
                                              'period':csp[2],
                                              'term':term},
                                             {'assignments': 1})
        existing = existing['assignments'][atype]
        for e in existing:
            if aname in e.values():
                found = True
                break
        
        if found:
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'term':term},
                                    {'$pull' : { 'assignments.'+atype : { 'name' : aname }}})

            for i in grades.keys():
                self.db.classes.update( {'code':csp[0],
                                         'section':csp[1],
                                         'period':csp[2],
                                         'term':term,
                                         'students.id':i},
                                        {'$pull':{('students.$.assignments.'+atype): {'name' : aname}}})

        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term':term},
                                {'$push': { 'assignments.'+atype: newassignment2(aname,maxpoints, maxpoints, apublic)}})
        for i in grades.keys():
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'term':term,
                                     'students.id':i},
                                    {'$push':{('students.$.assignments.'+atype):
                                              newassignment(aname, grades[i], maxpoints)}})

    def deleteAssignment(self, csp, term, ids, aname, atype):
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term':term},
                                {'$pull' : { 'assignments.'+atype : { 'name' : aname }}})

        for i in ids:
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'term':term,
                                     'students.id':i},
                                    {'$pull':{('students.$.assignments.'+atype): {'name' : aname}}})


    def changeGrade(self, csp, term, sid, atype, grades):
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term':term,
                                 'students.id':sid },
                                {'$set':{('students.$.assignments.'+atype):grades}})
        return self.db.classes.find_one( {'code':csp[0],
                                          'section':csp[1],
                                          'period':csp[2],
                                          'term':term,
                                          'students.id':sid },
                                         {'students.$':1 } )        
    
    def getAssignments(self, csp, term):
        cls = self.getClass( csp, term )
        cls = cls[0]
        assignments = []
        for atype in cls['assignments'].keys():
            for a in cls['assignments'][atype]:
                assignments.append( a['name'] )
        return assignments

    def getAssignment(self, csp, term, aname):
        cls = self.getClass( csp, term )
        cls = cls[0]
        assignment = { 'name' : aname }
        grades = []
        for atype in cls['assignments']:
            for a in cls['assignments'][atype]:
                if a['name'] == aname:
                    assignment['max'] = a['max']
                    assignment['type'] = atype
                    assignment['public'] = a['public']
                    break
                    
        for s in cls['students']:
            grades.append( {'id' : s['id'],
                            'grade' : self.getGrade(s, aname, assignment['type'])})
        
        assignment['grades'] = grades
        return assignment

    def getGrade(self, student, aname, atype):
        for g in student['assignments'][ atype ]:
            if g['name'] == aname:
                return g['points']
        return -2

    def getStudent2(self, csp, term, sid):
        return self.db.classes.find_one({'code':csp[0],
                                         'section':csp[1],
                                         'period':csp[2],
                                         'term':term,
                                         'students.id': sid },
                                        { "students.id": 1, "_id" : 0 } )

    def getStudent(self, csp, term, sid):
        return self.db.classes.find_one( {'code':csp[0],
                                          'section':csp[1],
                                          'period':csp[2],
                                          'term' : term,
                                          'students.id':sid },
                                         {'students.$':1 } )

    def removeStudent(self, csp, term, sid):
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term' : term},
                                {'$pull' : { 'students' : { 'id' : sid }}})
                                 
    def addStudent(self, csp, term, first, last, nick, sid, email, row, col, stuyid, hr):
        s = newstudent2(first, last, nick, stuyid, hr, sid, email, row, col);
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term' : term},
                                {'$push' : { 'students' : s }})

    def changeWeights(self, csp, term, weights):
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term':term},
                                {'$set':{'weights':weights}})

    def saveGradeOptions(self, csp, term, option):
        currentOptions =  self.db.classes.find_one({'code':csp[0],
                                                    'section':csp[1],
                                                    'period':csp[2],
                                                    'term':term},
                                                   { 'options':1})['options']
        if option == 'drop-avg':
            if 'drop-total' in currentOptions:
                currentOptions.remove( 'drop-total' )
                currentOptions.append( option )
            elif 'drop-avg' in currentOptions:
                currentOptions.remove( 'drop-avg' )
            else:
                currentOptions.append( option )

        if option == 'drop-total':
            if 'drop-avg' in currentOptions:
                currentOptions.remove( 'drop-avg' )
                currentOptions.append( option )
            elif 'drop-total' in currentOptions:
                currentOptions.remove( 'drop-total' )
            else:
                currentOptions.append( option )

        self.db.classes.update({'code':csp[0],
                                'section':csp[1],
                                'period':csp[2],
                                'term':term},
                               {'$set':{'options':currentOptions}})

    def saveInfo(self, csp, term, sid, nick, sid2, email, stuyid, hr):
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term':term,
                                 'students.id':sid },
                                {'$set':{('students.$.nick'):nick}})
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term':term,
                                 'students.id':sid },
                                {'$set':{('students.$.email'):email}})
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term':term,
                                 'students.id':sid },
                                {'$set':{('students.$.stuyid'):stuyid}})
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term':term,
                                 'students.id':sid },
                                {'$set':{('students.$.hr'):hr}})
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'term':term,
                                 'students.id':sid },
                                {'$set':{('students.$.id'):sid2}})
        return self.db.classes.find_one( {'code':csp[0],
                                          'section':csp[1],
                                          'period':csp[2],
                                          'term':term,
                                          'students.id':sid },
                                         {'students.$':1 } )        

    def getStudents(self, csp, term):
        return self.db.classes.find_one({'code':csp[0],
                                         'section':csp[1],
                                         'period':csp[2],
                                         'term':term},
                                        {'students':1})['students']

    def setCurrentTerm(self, term):
        teachers = self.getTeachers()
        for t in teachers:
            classes = self.getClasses(t, '')
            for c in classes:
                self.db.classes.update({'code':c[0],
                                        'section':c[1],
                                        'period':c[2],
                                        'term':''},
                                       {'$set' : { 'term' : term }})
        
    def addAssignmentType(self, csp, term, atname ):
        assignments =  self.db.classes.find_one({'code':csp[0],
                                                 'section':csp[1],
                                                 'period':csp[2],
                                                 'term':term},
                                                {'assignments':1})['assignments']
        weights =  self.db.classes.find_one({'code':csp[0],
                                             'section':csp[1],
                                             'period':csp[2],
                                             'term':term},
                                            {'weights':1})['weights']
        students = self.getStudents( csp, term )

        for s in students:
            s[ 'assignments' ][ atname ] = []
        assignments[ atname ] = []
        weights[ atname ] = 0

        self.db.classes.update({'code':csp[0],
                                'section':csp[1],
                                'period':csp[2],
                                'term':term},
                               {'$set' : { 'assignments' : assignments } })
        self.db.classes.update({'code':csp[0],
                                'section':csp[1],
                                'period':csp[2],
                                'term':term},
                               {'$set' : { 'weights' : weights } })
        self.db.classes.update({'code':csp[0],
                                'section':csp[1],
                                'period':csp[2],
                                'term':term},
                               {'$set' : { 'students' : students } })

    def removeAssignmentType(self, csp, term, atname ):
        assignments =  self.db.classes.find_one({'code':csp[0],
                                                 'section':csp[1],
                                                 'period':csp[2],
                                                 'term':term},
                                                {'assignments':1})['assignments']
        weights =  self.db.classes.find_one({'code':csp[0],
                                             'section':csp[1],
                                             'period':csp[2],
                                             'term':term},
                                            {'weights':1})['weights']
        students = self.getStudents( csp, term )

        for s in students:
            s[ 'assignments' ].pop( atname )
        assignments.pop( atname )
        weights.pop( atname )

        self.db.classes.update({'code':csp[0],
                                'section':csp[1],
                                'period':csp[2],
                                'term':term},
                               {'$set' : { 'assignments' : assignments } })
        self.db.classes.update({'code':csp[0],
                                'section':csp[1],
                                'period':csp[2],
                                'term':term},
                               {'$set' : { 'weights' : weights } })
        self.db.classes.update({'code':csp[0],
                                'section':csp[1],
                                'period':csp[2],
                                'term':term},
                               {'$set' : { 'students' : students } })


    def addClassField(self, fname, ftype, dKeyNames=[], dVal=0):

        if ftype == T_ARRAY:
            field = []
        elif ftype == T_STRING:
            field = ''
        elif ftype == T_DICTIONARY:
            field = {}
            for n in dKeyNames:
                field[n] = dVal
        else:
            field = 0
        teachers = self.getTeachers()
        for t in teachers:
            classes = self.getClasses2(t)
            for c in classes:                
                self.db.classes.update({'code':c[0],
                                        'section':c[1],
                                        'period':c[2],
                                        'term':c[3]},
                                       {'$set' : { fname : field }})

    def addStudentField(self, fname, ftype, dKeyNames=[], dVal=0):
        teachers = self.getTeachers()
        for t in teachers:
            classes = self.getAllClasses(t)
            terms = classes['terms']            
            for t in terms:
                if t != 'terms':
                    for c in classes[t]:
                        self.addFieldToStudents(c, t, fname, ftype, dKeyNames, dVal)

    def addFieldToStudents(self, csp, term, fname, ftype,dKeyNames=[],dVal=0):
        students = self.getStudents(csp, term)
        if ftype == T_ARRAY:
            field = []
        elif ftype == T_STRING:
            field = ''
        elif ftype == T_DICTIONARY:
            field = {}
            for n in dKeyNames:
                field[n] = dVal
        else:
            field = 0
        for s in students:
            self.db.classes.update({'code':csp[0],
                                    'section':csp[1],
                                    'period':csp[2],
                                    'term':term,
                                    'students.id':s['id']},
                                   {'$set' : {'students.$.'+fname:field}})


    #WORK IN PROGRESS
    def addAssignmentField(self):
        teachers = self.getTeachers()
        for t in teachers:
            classes = self.getAllClasses(t)
            terms = classes['terms']            
            for t in terms:
                if t != 'terms':
                    for c in classes[t]:
                        self.addFieldToAssignments(c, t)


    def addFieldToAssignments(self, csp, term ):
            
        print `csp`
        #Get the class
        cls = self.db.classes.find_one({'code':csp[0],
                                        'section':csp[1],
                                        'period':csp[2],
                                        'term':term } )
        
        ass = cls['assignments']
        #add public to each assignment
        for atype in ass:

            for a in ass[atype]:
                a['public'] = 0;

        #update the class
        cls['assignments'] = ass
        
        #add field to each students' assignment dictionary
        students = cls['students']
        for s in students:

            #add the field to each entry
            ass = s['assignments']
            for atype in ass:

                for a in ass[atype]:
                    a['public'] = 0;

            s['assignments'] = ass

        cls['students'] = students
        
        #update the database
        self.db.classes.update({'code':csp[0],
                                'section':csp[1],
                                'period':csp[2],
                                'term':term },
                               { "$set" : {  "assignments" : cls['assignments'] } })
        self.db.classes.update({'code':csp[0],
                                'section':csp[1],
                                'period':csp[2],
                                'term':term },
                               { "$set" : {  "students" : cls['students'] } })
            
    #END WORK IN PROGRESS
        

    def getTodaysAttendance(self, csp, term, date, mode):
        studs = self.db.classes.find_one({'code':csp[0],
                                          'section':csp[1],
                                          'period':csp[2],
                                          'term' : term},
                                         {'students':1})
        studs = studs['students']
        ids = []
        for s in studs:
            if date in s[mode]:
                ids.append( s['id'] )
        return ids


    def openSpot(self, csp, term):
        target = self.getClass( csp, term )
        rows = int(target[0]['rows'])
        cols = int(target[0]['cols'])
        size = len(target[0]['students'])
        return (rows * cols) > size
    
    def transfer(self, currentCSP, targetCSP, term, sid):
        student = self.db.classes.find_one({'code':currentCSP[0],
                                            'section':currentCSP[1],
                                            'period':currentCSP[2],
                                            'term' : term,
                                            'students.id':sid},
                                           {'students.$':1})
        self.db.classes.update( {'code':currentCSP[0],
                                 'section':currentCSP[1],
                                 'period':currentCSP[2],
                                 'term' : term},
                                {'$pull' : { 'students' : { 'id' : sid }}})
        student = student['students'][0]
        seat = self.findOpenSpot(targetCSP, term)
        student['row'] = seat[0]
        student['col'] = seat[1]
        self.db.classes.update( {'code':targetCSP[0],
                                 'section':targetCSP[1],
                                 'period':targetCSP[2],
                                 'term':term},
                                {'$push' : { 'students' : student }})
                                           
    def findOpenSpot(self, csp, term):
        target = self.getClass( csp, term )
        target = target[0]
        
        for r in range(int(target['rows'])):
            for c in range(int(target['cols'])):                
             if self.isSpotOpen(target['students'], str(r), str(c)):
                return (str(r), str(c))
            
    def isSpotOpen(self, students, row, col):
        i = 0
        while (i < len(students) ):
            if students[i]['row'] == row and students[i]['col'] == col:
                return False
            i+= 1
        return True
        
    def getBackup(self, csp, term):
        target = self.getClass( csp, term )
        target = target[0]
        return target

    def resetFromBackup(self, backup):
        self.db.classes.remove({'code':backup['code'], 
                                'section':backup['section'],
                                'period':backup['period'],
                                'term':backup['term']})
        self.db.classes.insert( backup )

    def getTeacher(self, csp, term):
        return self.db.classes.find_one( {'code':csp[0],
                                          'section':csp[1],
                                          'period':csp[2],
                                          'term':term},
                                         {'teacher':1 } )['teacher']

    def getBackupCSV(self, csp, term):
        target = self.getClass( csp, term )
        target = target[0]
        backup = csp[0] +'-'+ csp[1] +'-'+ csp[2] +' '+ target['teacher']+' ' + term + '\n'
        students = target['students']
        backup+= '\nAttendance Data: Absent\n'
        backup+= 'Last,First,ID\n'
        for s in students:
            lineparts = [ s['last'], s['first'], s['id'] ] + s['absent']
            backup+= ','.join(lineparts) + '\n'
        backup+= '\nAttendance Data: Late\n'
        backup+= 'Last,First,ID\n'
        for s in students:
            lineparts = [ s['last'], s['first'], s['id'] ] + s['late']
            backup+= ','.join(lineparts) + '\n'
        backup+= '\nAttendance Data: Excused\n'
        backup+= 'Last,First,ID\n'
        for s in students:
            lineparts = [ s['last'], s['first'], s['id'] ] + s['excused']
            backup+= ','.join(lineparts) + '\n'
        backup+= '\nAttendance Data: Excused Late\n'
        backup+= 'Last,First,ID\n'
        for s in students:
            lineparts = [ s['last'], s['first'], s['id'] ] + s['exlate']
            backup+= ','.join(lineparts) + '\n'
        
        for atype in target['assignments']:
            lineparts = []
            backup+= '\n' + atype + ' Data\n'
            backup+= 'Last,First,ID,'

            for a in target['assignments'][atype]:
                lineparts.append( a['name'] )
            backup+= ','.join(lineparts) + '\n'
            backup+= 'Max,Points,,'
            lineparts = []
            for a in target['assignments'][atype]:
                lineparts.append(str(a['max']))
            backup+= ','.join(lineparts) + '\n'

            for s in students:
                lineparts = [ s['last'], s['first'], s['id'] ]
                for a in s['assignments'][atype]:
                    lineparts.append( str(a['points']) )
                backup+= ','.join(lineparts) + '\n'
        return backup

#Functions for interactive mode
def menu():
    choiceCheck = False

    while not choiceCheck:
        menuText = '1: Add new class(es) from a data file\n'
        menuText+= '2: Set the current term\n'
        menuText+= '3: Remove a class\n'
        menuText+= '4: See full class list\n'
        print menuText
        selection = raw_input('Choice: ')        
        try:
            s = int(selection)
            return s
        except:
            choiceCheck = False

def addClass(m):
    fileCheck = False
    filename = ''
    while not fileCheck:
        filename = raw_input('Enter csv file to import: ')
        try:
            stat(filename)
            fileCheck = True
        except:
            print 'File not found'
            fileCheck = False
    m.loadNewClass( filename )

def setTerm(m):
    termCheck = False
    term = ''
    t = 0
    year = raw_input('Enter year: ')
    while not termCheck:
        i = raw_input('Enter 1 for fall, 2 for spring: ')
        if i.isdigit():
            t = int(i)
            if t != 1 and t != 2:
                print 'Please enter 1 or 2.\n'
            else:
                termCheck = True
        else:
            print 'Please enter 1 or 2.\n'                    
    if t == 1:
        term = 'fall'
    else:
        term = 'spring'
    term = year + '-' + term
    m.setCurrentTerm(term)

def loopSelection( dataList, picking=True ):
    loopCheck = False
    data = ''
    while not loopCheck:
        stext = '\nSelect one of the following by number\n'
        i = 0
        for d in dataList:
            stext+= `i` + ' ' + str(d) + '\n'
            i+= 1
        print stext
        
        if not picking:
            break

        ds = raw_input('Choice: ')
        if ds.isdigit():
            choice = int(ds)
            if choice < 0 or choice >= len(dataList):
                print 'Please use an appropriate number.\n'
            else:
                data = dataList[choice]
                loopCheck = True
        else:
            print 'Please use an appropriate number.\n'
    if picking:
        return data

def showClasses(mydb, picking = True):
    teachers = mydb.getTeachers()    
    print 'Choose a teacher.\n'
    teacher = loopSelection( teachers )
    
    classes = mydb.getClasses2( teacher )
    print '\nClasses for ' + teacher + ':'
    class1 = loopSelection( classes, picking )
    return class1

def remClass(mydb):
    class1 = showClasses(mydb)
    mydb.removeClass( class1[:3], class1[3] )

if __name__ == '__main__':
    print '\n'
    mydb=db()
    choice = menu()

    if choice == 1:
        addClass(mydb)
    elif choice == 2:
        setTerm(mydb)
    elif choice == 3:
        remClass(mydb)
    elif choice == 4:
        showClasses(mydb, False)
#    mydb.initialLoad("../data/students-base-9-9-2013.csv")
#    mydb.setCurrentTerm('2013-fall')

            

