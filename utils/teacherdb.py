from pymongo import Connection
from os import stat
import db

import json

T_ARRAY = 0
T_NUMBER = 1
T_STRING = 2
T_DICTIONARY = 3


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
                                 {'$push' : {'$.classes':classname}})

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
            grades['-'.join(c)] = classdb.getStudent( c, term, id )['students'][0]['assignments']
        return grades

    def setPassword( self, id, pw ):
        self.db.students.update( {'id':id}, 
                                 {'$set': {'password': pw}} )
    
    def isPasswordSet(self, id):
        student = self.getStudent(id)
        return not student['password'] == ''

    def authenticate(self, id, pw):
        student = self.getStudent(id)
        return student['password'] == pw

if __name__ == '__main__':
    print '\n'
    mydb=studentdb.studentdb()

            

