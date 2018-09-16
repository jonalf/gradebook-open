"""
TABLES

classes
code, section, period, term, teacher, id

students
first, last, nick, id, hr, email

<class>_roster
class_id, student_id, row, col,

<class>_attendance
class_id, student_id,

<class>_assignment
class_id, student_id, grade,

"""

import sqlite3
