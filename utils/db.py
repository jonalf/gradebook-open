from pymongo import Connection
import json

def newclass(code,sect,pd,teacher):
    rec = { 'code':code,
            'section':sect,
            'period':pd,
            'teacher':teacher,
            'rows':0,
            'cols':0,
            'seated':0,
            'students':[],
            'tests':[],
            'projects':[],
            'work':[],
            'weights': { 'work':.2, 'tests':.4, 'projects':.4 }
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
            'work':[],
            'tests':[],
            'projects':[]
            }

def newassignment(name, points, maxp):
    return { 'name': name,
             'points': points,
             'max' : maxp
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



    def getTeachers(self):
        teachers = [ x['teacher'] for x in self.db.classes.find()]
        t2=[]
        for t in teachers:
            if not t in t2:
                t2.append(t)
        return t2

    def getClasses(self,teacher):
        classes = [ (x['code'],x['section'],x['period']) for x in self.db.classes.find({'teacher':teacher})]
        return classes
                    

    def getClass( self,csp ):
        """
        csp is (code,section,period)
        maybe it should just be code and section
        """
        cls = [ x for x in self.db.classes.find({'code':csp[0],
                                                 'section':csp[1],
                                                 'period':csp[2]},
                                                fields={'_id':False})]
        
        return cls

    def resizeClass( self, csp, newRows, newCols ):
        self.db.classes.update( { 'code':csp[0], 
                                  'section':csp[1], 
                                  'period':csp[2] },
                                { "$set" : { "rows" : newRows,
                                             "cols" : newCols }})
    def setSeated(self, csp, b, rows, cols):
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2] },
                                { "$set" : { "seated" : b,
                                             "rows" : rows,
                                             "cols" : cols }})

    def setSeat(self, csp, sid, row, col):
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'students.id':sid },
                                {'$set' : { 'students.$.row' : row,
                                            'students.$.col' : col }})

    def setMassAttendance(self, csp, absent, late, excused, date):

        for s in absent:
            a = self.getAttendance(csp, s, 'A')
            l = self.getAttendance(csp, s, 'L')
            e = self.getAttendance(csp, s, 'E')            
            if date not in e and date not in a:                
                self.setAttendance(csp, s, 'A', date)
                if date in l:
                    self.removeAttendance(csp, s, 'L', date)         

        for s in late:
            a = self.getAttendance(csp, s, 'A')
            l = self.getAttendance(csp, s, 'L')
            e = self.getAttendance(csp, s, 'E')            
            if date not in e and date not in l:                
                self.setAttendance(csp, s, 'L', date)
                if date in a:
                    self.removeAttendance(csp, s, 'A', date)        

        for s in excused:
            a = self.getAttendance(csp, s, 'A')
            l = self.getAttendance(csp, s, 'L')
            e = self.getAttendance(csp, s, 'E')            
            self.setAttendance(csp, s, 'E', date)
            if date in a:
                self.removeAttendance(csp, s, 'A', date)
            if date in l:
                self.removeAttendance(csp, s, 'L', date)

    def getAttendance(self, csp, sid, mode):
        record = self.db.classes.find_one({'code':csp[0], 
                                      'section':csp[1],
                                      'period':csp[2],
                                      'students.id':sid}, 
                                     {'students.$':1})
        record = record['students'][0]
        if mode == 'A':
            return record['absent']
        elif mode == 'E':
            return record['excused']
        elif mode == 'L':
            return record['late']
        
    def removeAttendance(self, csp, sid, mode, date):
        if mode == 'A':
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'students.id':sid },
                                    {'$pull' : { 'students.$.absent':date}})
        elif mode == 'E':
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'students.id':sid },
                                    {'$pull' : { 'students.$.excused':date}})
        elif mode == 'L':
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'students.id':sid },
                                    {'$pull' : { 'students.$.late':date}})


    def setAttendance(self, csp, sid, mode, date):
        if mode == 'A':
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'students.id':sid },
                                    {'$push' : { 'students.$.absent':date}})
        elif mode == 'E':
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'students.id':sid },
                                    {'$push' : { 'students.$.excused':date}})
        elif mode == 'L':
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2],
                                     'students.id':sid },
                                    {'$push' : { 'students.$.late':date}})

    def changeAllAttendance(self, csp, sid, a, l, e):
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'students.id':sid },
                                {'$set' : { 'students.$.absent':a}})
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'students.id':sid },
                                {'$set' : { 'students.$.late':l}})
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'students.id':sid },
                                {'$set' : { 'students.$.excused':e}})
    
    def setMassGrades(self, csp, aname, atype, maxpoints, grades):
        found = False
        existing = self.db.classes.find_one( {'code':csp[0],
                                              'section':csp[1],
                                              'period':csp[2] },
                                             {atype: 1})
        existing = existing[atype]
        for e in existing:
            if aname in e.values():
                found = True
                break
        
        if not found:
            self.db.classes.update( {'code':csp[0],
                                     'section':csp[1],
                                     'period':csp[2] },
                                    {'$push': { atype: newassignment(aname,maxpoints, maxpoints)}})
            for i in grades.keys():
                self.db.classes.update( {'code':csp[0],
                                         'section':csp[1],
                                         'period':csp[2],
                                         'students.id':i},
                                        {'$push':{('students.$.'+atype):
                                                  newassignment(aname, grades[i], maxpoints)}})

    def changeGrade(self, csp, sid, atype, grades):
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'students.id':sid },
                                {'$set':{('students.$.'+atype):grades}})
        return self.db.classes.find_one( {'code':csp[0],
                                          'section':csp[1],
                                          'period':csp[2],
                                          'students.id':sid },
                                         {'students.$':1 } )        
    
    def getStudent(self, csp, sid):
        return self.db.classes.find_one( {'code':csp[0],
                                         'section':csp[1],
                                         'period':csp[2],
                                         'students.id':sid },
                                      {'students.$':1 } )

    def removeStudent(self, csp, sid):
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2] },
                                {'$pull' : { 'students' : { 'id' : sid }}})
                                 
    def addStudent(self, csp, first, last, nick, sid, email, row, col, stuyid, hr):
        s = newstudent2(first, last, nick, stuyid, hr, sid, email, row, col);
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2] },
                                {'$push' : { 'students' : s }})

    def changeWeights(self, csp, types, weights):
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2] },
                                {'$set':{'weights':newweights(types, weights)}})

    def saveInfo(self, csp, sid, nick, sid2, email, stuyid, hr):
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'students.id':sid },
                                {'$set':{('students.$.nick'):nick}})
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'students.id':sid },
                                {'$set':{('students.$.email'):email}})
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'students.id':sid },
                                {'$set':{('students.$.stuyid'):stuyid}})
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'students.id':sid },
                                {'$set':{('students.$.hr'):hr}})
        self.db.classes.update( {'code':csp[0],
                                 'section':csp[1],
                                 'period':csp[2],
                                 'students.id':sid },
                                {'$set':{('students.$.id'):sid2}})
        return self.db.classes.find_one( {'code':csp[0],
                                          'section':csp[1],
                                          'period':csp[2],
                                          'students.id':sid },
                                         {'students.$':1 } )        
        
    def getTodaysAttendance(self, csp, date, mode):
        studs = self.db.classes.find_one({'code':csp[0],
                                          'section':csp[1],
                                          'period':csp[2] },
                                         {'students':1})
        studs = studs['students']
        ids = []
        for s in studs:
            if date in s[mode]:
                ids.append( s['id'] )

        return ids


    def openSpot(self, csp):
        target = self.getClass( csp )
        rows = int(target[0]['rows'])
        cols = int(target[0]['cols'])
        size = len(target[0]['students'])
        return (rows * cols) > size
    
    def transfer(self, currentCSP, targetCSP, sid):
        student = self.db.classes.find_one({'code':currentCSP[0],
                                            'section':currentCSP[1],
                                            'period':currentCSP[2],
                                            'students.id':sid},
                                           {'students.$':1})
        self.db.classes.update( {'code':currentCSP[0],
                                 'section':currentCSP[1],
                                 'period':currentCSP[2] },
                                {'$pull' : { 'students' : { 'id' : sid }}})
        student = student['students'][0]
        seat = self.findOpenSpot(targetCSP)
        student['row'] = seat[0]
        student['col'] = seat[1]
        self.db.classes.update( {'code':targetCSP[0],
                                 'section':targetCSP[1],
                                 'period':targetCSP[2] },
                                {'$push' : { 'students' : student }})
                                           
    def findOpenSpot(self, csp):
        target = self.getClass( csp )
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
        
    def getBackup(self, csp):
        target = self.getClass( csp )
        target = target[0]
        return target

    def resetFromBackup(self, backup):
        self.db.classes.remove({'code':backup['code'], 
                                'section':backup['section'],
                                'period':backup['period']})
        self.db.classes.insert( backup )

    def getTeacher(self, csp):
        return self.db.classes.find_one( {'code':csp[0],
                                         'section':csp[1],
                                         'period':csp[2] },
                                      {'teacher':1 } )['teacher']

    def getBackupCSV(self, csp):
        target = self.getClass( csp )
        target = target[0]
        backup = csp[0] +'-'+ csp[1] +'-'+ csp[2] +' '+ target['teacher']+'\n'
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
        
        backup+= '\nWork Data\n'
        backup+= 'Last,First,ID,'
        lineparts = []
        for w in target['work']:
            lineparts.append( w['name'] )
        backup+= ','.join(lineparts) + '\n'
        backup+= 'Max,Points,,'
        lineparts = []
        for w in target['work']:
            lineparts.append(str(w['max']))
        backup+= ','.join(lineparts) + '\n'
        for s in students:
            lineparts = [ s['last'], s['first'], s['id'] ]
            for w in s['work']:
                lineparts.append( str(w['points']) )
            backup+= ','.join(lineparts) + '\n'

        backup+= '\nTest Data\n'
        backup+= 'Last,First,ID,'
        lineparts = []
        for t in target['tests']:
            lineparts.append( t['name'] )
        backup+= ','.join(lineparts) + '\n'
        backup+= 'Max,Points,,'
        lineparts = []
        for t in target['tests']:
            lineparts.append(str(t['max']))
        backup+= ','.join(lineparts) + '\n'
        for s in students:
            lineparts = [ s['last'], s['first'], s['id'] ]
            for t in s['tests']:
                lineparts.append( str(t['points']) )
            backup+= ','.join(lineparts) + '\n'

        backup+= '\nProject Data\n'
        backup+= 'Last,First,ID,'
        lineparts = []
        for p in target['projects']:
            lineparts.append( p['name'] )
        backup+= ','.join(lineparts) + '\n'
        backup+= 'Max,Points,,'
        lineparts = []
        for p in target['projects']:
            lineparts.append(str(p['max']))
        backup+= ','.join(lineparts) + '\n'
        for s in students:
            lineparts = [ s['last'], s['first'], s['id'] ]
            for p in s['projects']:
                lineparts.append( str(p['points']) )
            backup+= ','.join(lineparts) + '\n'

        return backup

if __name__=='__main__':
    mydb = db()    
    print mydb.getBackupCSV(('FUNTIME','01','1'))
#    mydb=db()
#    mydb.initialLoad("../data/students-base-9-2013.csv")

            

