"""
TABLES

classes
code, section, period, term, teacher, id, name, rows, cols

students
first, last, nick, osis, hr, email, notes

teachers
name, login, password

<term>_roster_entries
class_id, student_id, row, col

<class>_attendance
student_id, date, category


<class>_assignment_types
type, options


<class>_assignments
class_id, type, max_grade, options, id

<class>_student_grades
class_id, student_id, assignment_id, grade, options

"""

import sqlite3
from os import path

TERM = '2018-fall'
DIR = path.dirname(__file__) or '.'
DIR += '/'
DBFILE = DIR + 'gradebook.db'

CSV_CODE = 0
CSV_SECTION = 1
CSV_PERIOD = 2
CSV_TEACHER = 3
CSV_LAST = 4
CSV_FIRST = 5
CSV_HR = 7
CSV_OSIS = 8
CSV_EMAIL = 9

def make_base_tables():
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()

    #Eventually will remove the drop table clause and change to CREATE TABLE IF NOT EXISTS
    cur.execute('DROP TABLE IF EXISTS classes')
    db.commit()
    cur.execute('CREATE TABLE classes(id INTEGER PRIMARY KEY, code TEXT, section INTEGER, period INTEGER, term TEXT, teacher TEXT, rows INTEGER, cols INTEGER, name TEXT)')
    db.commit()

    cur.execute('DROP TABLE IF EXISTS students')
    db.commit()
    cur.execute('CREATE TABLE students(osis INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, nick_name TEXT, hr TEXT, email TEXT, note TEXT)')
    db.commit()

    cur.execute('DROP TABLE IF EXISTS teachers')
    db.commit()
    cur.execute('CREATE TABLE teachers(id INTEGER PRIMARY KEY, name TEXT, login TEXT, password TEXT)')
    db.commit()

    cmd = 'DROP TABLE IF EXISTS "%s_rosters"'%TERM
    cur.execute(cmd)
    db.commit()
    cur.execute('CREATE TABLE "%s_rosters"(class_id INTEGER, student_osis INTEGER, row INTEGER, col INTEGER)'%TERM)
    db.commit()
    db.close()



def load_data(dfile):
    f = open(dfile)
    lines = f.readlines()
    f.close()

    db = sqlite3.connect( DBFILE )
    cur = db.cursor()

    for line in lines:
        line = line.strip()
        print 'adding entry: %s'%line

        data = line.split(',')
        cmd = 'SELECT id FROM classes WHERE code=? AND section=? AND term=?'
        cur.execute(cmd, (data[CSV_CODE], data[CSV_SECTION], TERM))
        class_id = cur.fetchone()
        if not class_id:
            class_id = new_class(data)
        else:
            class_id = class_id[0]

        cmd = 'SELECT osis FROM students WHERE osis=?'
        print int(data[CSV_OSIS])
        cur.execute(cmd, (int(data[CSV_OSIS]),))
        student_osis = cur.fetchone()
        if not student_osis:
            cmd = 'INSERT INTO students(osis, first_name, last_name, hr) VALUES(?, ?, ?, ?)'
            cur.execute(cmd, (data[CSV_OSIS], data[CSV_FIRST], data[CSV_LAST], data[CSV_HR]))
            student_osis = data[CSV_OSIS]
        else:
            student_osis = student_osis[0]

        cmd = 'INSERT INTO "%s_rosters"(class_id, student_osis, row, col) VALUES (?, ?, ?, ?)'%TERM
        cur.execute(cmd, (class_id, student_osis, -1, -1))
        db.commit()

    db.commit()
    db.close()



def new_class(data):
    print "class does not exist, creating now"

    db = sqlite3.connect( DBFILE )
    cur = db.cursor()

    cmd = 'INSERT INTO classes(code, section, period, term, teacher) VALUES(?, ?, ?, ?, ?)'
    cur.execute(cmd, (data[CSV_CODE], data[CSV_SECTION], data[CSV_PERIOD], TERM, data[CSV_TEACHER]))
    class_id = cur.lastrowid

    table_code = '%s_%d'%(data[CSV_CODE], class_id)

    cur.execute('CREATE TABLE "%s_attendance"(student_osis INTEGER, date DATETIME, category INTEGER)'%table_code)
    cur.execute('CREATE TABLE "%s_assignment_types"(id INTEGER PRIMARY KEY, type TEXT, options INTEGER)'%table_code)
    cur.execute('CREATE TABLE "%s_assignments"(id INTEGER PRIMARY KEY, name TEXT, type INTEGER, max_grade REAL, options INTEGER)'%table_code)
    cur.execute('CREATE TABLE "%s_student_grades"(student_osis INTEGER, assignment_id INTEGER, grade REAL, options INTEGER)'%table_code)

    db.commit()
    db.close()
    return class_id

# students
# first, last, nick, osis, hr, email, notes

# teachers
# name, login, password

# <term>_roster_entries
# class_id, student_id, row, col
