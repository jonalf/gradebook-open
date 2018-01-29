from pymongo import Connection
from os import stat
import db

import json

T_ARRAY = 0
T_NUMBER = 1
T_STRING = 2
T_DICTIONARY = 3

TEST_CLASSES = [ 'FUNTIME', 'MKS65C' ]

def newstudent(last, first, stuyid, hr, id, email, c):
    return {'last':last,
            'first':first,
            'stuyid':stuyid,
            'hr':hr,
            'id':id,
            'email':email,
            'password':'',
            'classes':[c]
            }

class studentdb:
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

    
    def dropAllStudents(self):
        """
        Removes all the classes form the mongodb
        """
        self.db.students.drop()

    def initialLoad(self,filename):
        """
        one time load of data into the mongodb
        If you do this multiple times you will have multiple
        copies in the database (mongo gives a unique _ID field if you
        add the same data multiple times
        """

        # empty out the old stories
        self.db.students.drop()

        # code, sect, pd, teacher, last,first,id,email
        for line in open(filename).readlines():
            line=line.strip()
            (last,first,stuyid,hr,id,email)=line.split(',')[4:]

            self.addStudent(last, first, stuyid, hr, id, email)

    def loadStudents(self, filename):
        for line in open(filename).readlines():
            line=line.strip()
            (last,first,stuyid,hr,id,email)=line.split(',')[4:] 
            self.addStudent(last, first, stuyid, hr, id, email)

    def loadStudentsFromDB( self, term ):
        classdb = db.db()
        classList = classdb.getAllTermClasses( term )
        for c in classList:
            students = classdb.getStudents( c, term )
            for s in students:
                print s['first'] + ' ' + s['last']
                test = self.getStudent( s['id'] )
                if not test:
                    self.addStudent(s['last'], s['first'], s['stuyid'], s['hr'], s['id'], s['email'], c)
                else:
                    self.addClassToList( s['id'], c )

    def addStudent(self, last, first, stuyid, hr, id, email, c):
        if not self.db.students.find_one( {'id':id} ):
            self.db.students.insert(newstudent(last,first,stuyid,hr,id,email, c))

    def addClassToList(self, id, classname):
        self.db.students.update( {'id':id},
                                 {'$push' : {'classes':classname}})

    def removeStudent(self, id):
        self.db.students.remove( { 'id':id } ) 

    def getAllStudents(self):
        students = [ (x['last'],x['first'],x['stuyid'], x['id'], x['hr'], x['email'], x['classes']) for x in self.db.students.find()] 
        return students
    
    def getIDList(self):
        ids = [ x['id'] for x in self.db.students.find()] 
        return ids

    def getStudent( self, id):
        student = self.db.students.find_one({'id':id}, fields={'_id':False})
        return student

    def getGrades( self, id, term ):
        grades = {}
        classdb = db.db()
        student = self.getStudent( id )
        for c in student['classes']:
            #if c[0] in TEST_CLASSES:
            cname = '-'.join(c)
            temp_grades = {}
            stud = classdb.getStudent( c, term, id )
            if stud:
                stud = stud['students'][0]['assignments']
                for atype in stud:
                    temp_list = []                
                    for ass in stud[ atype ]:
                        if ass['public'] == 1:
                            temp_list += [ass]
                        if len(temp_list) > 0:
                            temp_grades[atype] = temp_list
                    
                if len(temp_grades) > 0:
                    grades[cname] = temp_grades
        return grades

    def setPassword( self, id, pw ):
        self.db.students.update( {'id':id}, 
                                 {'$set': {'password': pw}} )
    
    def clearPassword( self, id ):
        self.setPassword( id, '' )
    
        
    def isPasswordSet(self, id):
        student = self.getStudent(id)
        return not student['password'] == ''

    def authenticate(self, id, pw):
        student = self.getStudent(id)
        return student['password'] == pw

def menu():
    choiceCheck = False

    while not choiceCheck:
        menuText = '1: Import new term students\n'
        menuText+= '2: Reset a student password\n'

        print menuText
        selection = raw_input('Choice: ')
        try:
            s = int(selection)
            return s
        except:
            choiceCheck = False

def newTerm(m):
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
    m.loadStudentsFromDB(term)

def passwordReset(m):
    osis = 0
    while osis == 0:
        i = raw_input('Enter OSIS: ')

        if len(i) == 9 and i.isdigit():
            osis = i
        else:
            print 'Please enter a valid OSIS\n'
    m.clearPassword( osis )


if __name__ == '__main__':
    print '\n'
    mydb = studentdb()
    choice = menu()

    if choice == 1:
        newTerm(mydb)
    elif choice == 2:
        passwordReset(mydb)
    else:
        print 'Please make a valid choice'
