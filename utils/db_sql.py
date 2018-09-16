"""
TABLES

classes
code, section, period, term, teacher, id

students
first, last, nick, osis, hr, email, notes

<term>_roster_entries
class_id, student_id, row, col

<class>_attendance
student_id, date, category


<class>_assignment_types
class_id, type, options


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

def make_base_tables():
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()

    cur.execute('DROP TABLE IF EXISTS classes')
    db.commit()
    cur.execute('CREATE TABLE classes(id INTEGER PRIMARY KEY, code TEXT, section INTEGER, period INTEGER, term TEXT, teacher TEXT)')
    db.commit()

    db.close()

