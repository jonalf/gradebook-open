#!/usr/bin/python
from flask import Flask, request, render_template, url_for, redirect, session, make_response, flash
import urllib2,json
import datetime
import json
from socket import gethostname
from utils import db
from utils import user
from utils import studentdb
from utils.user import requireauth, markUsage
from random import randint

if gethostname() == 'gradebook':
    userfile = '/var/www/gradebook/data/gbusers'
else:
    userfile = 'data/gbusers'

CURRENT_TERM = '2018-spring'

app = Flask(__name__)
app.secret_key = open('/dev/urandom', 'rb').read(32)

#LOGIN LOGOUT SELECTION FUNCTIONS
@app.route("/")
def index():
    if 'user' not in session:
        return redirect(url_for("login"))
    else:
        return redirect( url_for('selectclass'))

@app.route("/login", methods = ["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        if 'user' in request.form:
            u = request.form['user'].strip()
            p = request.form['pass'].strip()
        else:
            u = 'anon'
        if u not in user.getUserList(): #userdic.keys():
            print u
            print 'no esta aqui'
            return redirect(url_for('login'))
        elif user.authenticate( u, p ):
            session['user'] = u
            session['teacher'] = user.getDBUser(u) #userdic[u]
            print session
            return redirect( url_for('selectclass'))
        else:
            return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('teacher', None)
    return redirect( url_for('login'))

@app.route("/selectclass")
@requireauth('selectclass')
def selectclass():
    return render_template("selectclass.html", trm = CURRENT_TERM)

@app.route("/loadselect", methods = ["POST"])
@requireauth('loadselect')
def loadselect():
    teacher = session['teacher']
    mydb = db.db();
    return json.dumps( mydb.getAllClasses(teacher) )

@app.route("/pwreset")
@requireauth('/pwreset')
def pwreset():
    print "RESET!"
    if 'user' not in session:
        return redirect(url_for("login"))
    else:
        return render_template("pwreset.html", usr = session['user'])

@app.route("/help")
def help():
    if 'user' not in session:
        return redirect(url_for("login"))
    else:
        return render_template("help.html")

#=============================================

@app.route("/newpw", methods = ["POST", "GET"])
@requireauth('/newpw')
def newpw():
    message = '<div class="redalert"><center>'
    if request.method == "GET":
        return redirect(url_for("login"))
    else:
        u = request.form['user'].strip()
        op = request.form['oldpass'].strip()
        np1 = request.form['newpass1'].strip()
        np2 = request.form['newpass2'].strip()

        if np1 != np2:
            flash('New Passwords do not match, Please Try Again')
            return redirect( url_for("pwreset", usr = u) )

        elif len(np1) < 6:
            flash('Passwords must have at least 6 characters, Please Try Again')
            return redirect( url_for("pwreset", usr = u) )
            
        elif user.authenticate( u, op ):
            user.web_pw_reset( u, np1 )
            return redirect( url_for("logout") )
 
        else:
            flash('Incorrect Password, Please Try Again')
            return redirect( url_for("pwreset", usr = u) )


#STUDENT LOGIN FUNCTIONS
@app.route("/studentlogin", methods = ["POST", "GET"])
def studentlogin():
    if request.method == "GET":
        return render_template("studentlogin.html")
    else:
        if 'user' in request.form:
            u = request.form['user'].strip()
            p = request.form['pass'].strip()
        else:
            u = 'anon'
        
        students = studentdb.studentdb()        
        if u not in students.getIDList():
            print u
            print 'no esta aqui'
            return redirect(url_for('studentlogin'))

        elif not students.isPasswordSet( u ):
            return render_template("studentpwset.html", user = u)
            
        elif students.authenticate( u, p ):
            session['user'] = u
            print session
            return redirect( url_for('studentview'))
        
        else:
            return redirect(url_for('studentlogin'))

@app.route('/studentpwset', methods = ["POST", "GET"])
def studentpwset():
    if request.method == 'GET':
        return render_template("studentpwset.html")
    else:
        u = request.form['user'].strip()
        p = request.form['pass'].strip()
        p2 = request.form['pass2'].strip()

        if p == '' or p2 == '':
            return render_template("studentpwset.html", user = u, message = 'Please enter a password into both boxes below')
        elif p != p2:
            return render_template("studentpwset.html", user = u, message = 'Both passwords did not match, please try again.')
        else:
            students = studentdb.studentdb()
            students.setPassword( u, p )
            return render_template("studentlogin.html", user = u, message = 'Your password has been set, please login below.')

@app.route('/studentview')
@requireauth( 'studentview' )
def studentview():
    return render_template("studentview.html", user=session['user'])
    

@app.route('/studentlogout')
def studentlogout():
    session.pop('user', None)
    return redirect( url_for('studentlogin'))

@app.route('/studentload', methods = ['POST'])
def studentload():
    sdb = studentdb.studentdb()
    cdb = db.db()
    student = sdb.getStudent( session['user'] )
    #sdb.getGrades( session['user'], CURRENT_TERM )
    return json.dumps(student)

@app.route('/studentgradeload', methods = ['POST'])
def studentgradeload():
    sdb = studentdb.studentdb()
    grades = sdb.getGrades( session['user'], CURRENT_TERM )
    return json.dumps(grades)


@app.route("/studentpwreset")
@requireauth('/studentpwreset')
def studentpwreset():
    print "RESET!"
    if 'user' not in session:
        return redirect(url_for("login"))
    else:
        return render_template("studentpwreset.html", usr = session['user'])

@app.route("/studentnewpw", methods = ["POST", "GET"])
@requireauth('/studentnewpw')
def studentnewpw():
    message = '<div class="redalert"><center>'
    if request.method == "GET":
        return redirect(url_for("login"))
    else:
        u = request.form['user'].strip()
        op = request.form['oldpass'].strip()
        np1 = request.form['newpass1'].strip()
        np2 = request.form['newpass2'].strip()

        students = studentdb.studentdb()

        if np1 != np2:
            flash('New Passwords do not match, Please Try Again')
            return redirect( url_for("studentpwreset", usr = u) )

        elif len(np1) < 6:
            flash('Passwords must have at least 6 characters, Please Try Again')
            return redirect( url_for("studentpwreset", usr = u) )
            
        elif students.authenticate( u, op ):
            students.setPassword( u, np1 )
            return redirect( url_for("studentlogout") )
 
        else:
            flash('Incorrect Password, Please Try Again')
            return redirect( url_for("studentpwreset", usr = u) )


#=============================================


# GENERAL CLASS VIEWING FUNCTIONS
@app.route("/classview", methods = ["POST", "GET"])
@requireauth('classview')
def classview():
    if request.method == 'POST':
        term = request.form['term'].strip()
    else:
        term = request.args.get('term')
    if term == 'other':
        try:
            c = request.form["classname"].strip()
            c = c.split(' ')
            cls = c[1]
            term = c[0]
        except:
            return redirect( url_for('selectclass'))
    else:
        if request.method == 'POST':
            cls = request.form["classname"].strip()
        else:
            cls = request.args.get('classname')
        print cls
        print term
    if cls == None or term == None:
        return redirect(url_for('selectclass'))
    return render_template("classview.html", clsname = cls, trm=term)


@app.route("/loadclass", methods = ["POST"])
@requireauth('loadclass')
def loadclass():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    
    markUsage( session['teacher'] )
    cls = mydb.getClass( (nameParts[0], nameParts[1], nameParts[2] ), term )
    try:
        mydb.resizeClass( (nameParts[0], nameParts[1], nameParts[2] ),
                          term, request.form["rows"].strip(), request.form["cols"].strip())
    except KeyError:
        pass
    return json.dumps( cls[0] )

@app.route("/seated", methods=["POST"])
@requireauth('seated')
def seated():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.setSeated( (nameParts[0], nameParts[1], nameParts[2]), term,
                  request.form["seated"].strip(),
                  request.form['rows'].strip(), request.form['cols'].strip())
    return "seated set"

@app.route("/validip", methods = ["POST"])
@requireauth('validip')
def validip():
    # allowedIPs=['149.89.','10.32.','127.0.0.1','165.155.2', '10.55.', '69.55.54.210']
    # ip = request.remote_addr
    # for i in  allowedIPs:
    #     if ip.startswith( i ):
    #         return 'true'
    # return 'false'
    return 'true'

#=============================================

# BACKUP VIEW FUNCTIONS
@app.route('/getbackup', methods=['POST', 'GET'])
@requireauth('getbackup')
def getbackup():
    clsn = request.args.get('classname')
    term = request.args.get('term')
    nameParts = clsn.split("-")    
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    backup = mydb.getBackup((nameParts[0], nameParts[1], nameParts[2]), term)
    backup = json.dumps( backup )
    response = make_response( backup )
    response.headers['Content-Disposition'] = 'attachment; filename=' + clsn + '-' + term + '-' + str(datetime.date.today()) + '.bak'
    return response

@app.route('/backuprestore', methods=['POST'])
@requireauth('backuprestore')
def backupreset():
    backup = request.files['backupfile']
    backup = backup.read()
    backup = json.loads(backup)
    clsn = backup['code'] + "-" + backup['section'] + '-' + backup['period']
    nameParts = clsn.split("-")    
    term = backup['term']
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.resetFromBackup(backup)
    return render_template("classview.html", clsname = clsn,trm = term )

@app.route('/getbackupcsv', methods=['POST', 'GET'])
@requireauth('getbackupcsv')
def getbackupcsv():
    clsn = request.args.get('classname')
    term = request.args.get('term')
    nameParts = clsn.split("-")    
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    backup = mydb.getBackupCSV((nameParts[0], nameParts[1], nameParts[2]), term)
    response = make_response( backup )
    response.headers['Content-Disposition'] = 'attachment; filename=' + clsn + '-' + term + '-' + str(datetime.date.today()) + '.csv'
    return response

@app.route('/getallbackupcsv', methods=['POST', 'GET'])
@requireauth('getallbackupcsv')
def getallbackupcsv():
    teacher = session['teacher']
    term = request.args.get('term')
    mydb = db.db();
    classes = mydb.getClasses(teacher, term)
    backup = ''
    for c in classes:
        backup+= mydb.getBackupCSV(c, term) + '\n\n'

    response = make_response( backup )
    response.headers['Content-Disposition'] = 'attachment; filename=' + teacher + '-' + term + '-' + str(datetime.date.today()) + '.csv'
    return response

@app.route('/getallbackup', methods=['POST', 'GET'])
@requireauth('getallbackup')
def getallbackup():
    teacher = session['teacher']
    term = request.args.get('term')
    mydb = db.db();
    classes = mydb.getClasses(teacher, term)
    backup = ''
    for c in classes:
        b = mydb.getBackup(c, term)
        backup+= json.dumps( b ) + '\n'

    response = make_response( backup )
    response.headers['Content-Disposition'] = 'attachment; filename=' + teacher + '-' + term + '-' + str(datetime.date.today()) + '.bak'
    return response

@app.route('/backupallrestore', methods=['POST'])
@requireauth('backupallrestore')
def backupallreset():
    backups = request.files['backupfile']
    backups = backups.read().strip().split('\n')    
    mydb = db.db()
    for b in backups:
        backup = json.loads(b)
        clsn = backup['code'] + "-" + backup['section'] + '-' + backup['period']
        nameParts = clsn.split("-")    
        term = backup['term']
        if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
            return 'false'
        mydb.resetFromBackup(backup)
    return render_template("selectclass.html", term = CURRENT_TERM)
#=============================================

# ATTENDANCE VIEW FUNCTIONS
@app.route("/saveattendance", methods=["POST"])
@requireauth('saveattendance')
def saveattendance():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    if request.form['absent'] != '':
        abss = request.form['absent'].strip().split('_')
    else:
        abss = []
    if request.form['late'] != '':
        lats = request.form['late'].strip().split('_')
    else:
        lats = []
    if request.form['excused'] != '':
        excs = request.form['excused'].strip().split('_')
    else:
        excs = []
    if request.form['exlates'] != '':
        exlates = request.form['exlates'].strip().split('_')
    else:
        exlates = []
    date = request.form['date'].strip()
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.setMassAttendance( (nameParts[0], nameParts[1], nameParts[2] ),
                    term, abss, lats, excs, exlates, date )
    return "done"

@app.route("/gettoday", methods=["POST"])
@requireauth('gettoday')
def gettoday():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    a = mydb.getTodaysAttendance((nameParts[0], nameParts[1], nameParts[2]), term, request.form['date'].strip(), 'absent')
    l = mydb.getTodaysAttendance((nameParts[0], nameParts[1], nameParts[2]), term, request.form['date'].strip(), 'late')
    e = mydb.getTodaysAttendance((nameParts[0], nameParts[1], nameParts[2]), term, request.form['date'].strip(), 'excused')
    el = mydb.getTodaysAttendance((nameParts[0], nameParts[1], nameParts[2]), term, request.form['date'].strip(), 'exlate')
    d = {'absent':a, 'late':l, 'excused':e, 'exlate':el}
    return json.dumps(d)
#=============================================

# ARRANGE VIEW FUNCTIONS
@app.route("/reseat", methods=["POST"])
@requireauth('reseat')
def reseat():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    id1 = request.form["id1"].strip()
    row1= request.form["row1"].strip()
    col1 = request.form["col1"].strip()
    id2 = request.form["id2"].strip()
    row2= request.form["row2"].strip()
    col2 = request.form["col2"].strip()
    mydb = db.db()
    
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    
    mydb.setSeat( (nameParts[0], nameParts[1], nameParts[2] ), term, 
                  id1, row1, col1)
    mydb.setSeat( (nameParts[0], nameParts[1], nameParts[2] ), term, 
                  id2, row2, col2)
    return "done"

@app.route("/setseat", methods=["POST"])
@requireauth('setseat')
def setseat():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.setSeat( (nameParts[0], nameParts[1], nameParts[2] ), term,
                  request.form['sid'].strip(), 
                  request.form['row'].strip(), request.form['col'].strip())
    return "done"

@app.route("/arrangeRandom", methods = ["POST"])
@requireauth('arrangeRandom')
def arrangeRandom():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'

    cls = mydb.getClass( (nameParts[0], nameParts[1], nameParts[2] ), term )
    students = cls[0]['students']
    for i in range(100):
        s1 = students[randint(0, len(students)-1)]
        s2 = students[randint(0, len(students)-1)]
        r = s1['row']
        c = s1['col']
        s1['row'] = s2['row']
        s1['col'] = s2['col']
        s2['row'] = r
        s2['col'] = c
        mydb.setSeat( (nameParts[0], nameParts[1], nameParts[2]), term,
                      s1['id'], s1['row'], s1['col'])
        mydb.setSeat( (nameParts[0], nameParts[1], nameParts[2]), term,
                      s2['id'], s2['row'], s2['col'])
    return json.dumps( cls[0] )

#=============================================

# STUDENT VIEW FUNCTIONS
@app.route('/addstudent', methods=["POST"])
@requireauth('addstudent')
def addstudent():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.addStudent( (nameParts[0], nameParts[1], nameParts[2] ),term,
                     request.form['first'].strip(), request.form['last'].strip(),
                     request.form['nick'].strip(), request.form['sid'].strip(), 
                     request.form['email'].strip(), int(request.form['row'].strip()),
                     int(request.form['col'].strip() ), request.form['stuyid'].strip(),
                     request.form['hr'].strip());
    return "done"

@app.route('/getinfo', methods=["POST"])
@requireauth('getinfo')    
def getinfo(): 
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    student = mydb.getStudent((nameParts[0], nameParts[1], nameParts[2] ), term, request.form['sid'])
    return json.dumps(student['students'])

@app.route('/removestudent', methods=["POST"])
@requireauth('removestudent')
def removestudent():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.removeStudent((nameParts[0], nameParts[1], nameParts[2]),term,
                        request.form['sid'].strip())
    return "done"
                                        
@app.route("/transferstudent", methods=["POST"])
@requireauth('transferstudent')
def transferstudent():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    targetClsn = request.form['targetclass'].strip()
    targetParts = targetClsn.split('-')
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    spot = mydb.openSpot((targetParts[0],targetParts[1],targetParts[2]), term)
    if spot:
        mydb.transfer((nameParts[0],nameParts[1],nameParts[2]),
                      (targetParts[0],targetParts[1],targetParts[2]),
                      term, request.form['sid'].strip())
        return "done"
    else:
        return "false"

#INFO MODE
@app.route('/saveinfo', methods=["POST"])
@requireauth('saveinfo')
def saveinfo():
    print request.form
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    student = mydb.saveInfo((nameParts[0], nameParts[1], nameParts[2]),
                            term,
                            request.form['sid'].strip(), request.form['nick'].strip(),
                            request.form['id'].strip(), request.form['email'].strip(),
                            request.form['stuyid'].strip(), request.form['hr'].strip())
    return json.dumps(student['students'])

# ATTENDANCE VIEW
@app.route("/changeattendance", methods=["POST"])
@requireauth("changeattendance")
def changeAttendance():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    a = request.form['absent'].strip().split('_')
    l = request.form['late'].strip().split('_')
    e = request.form['excused'].strip().split('_')
    el = request.form['exlate'].strip().split('_')
    if a[0] == '':
        a = []
    if l[0] == '':
        l = []
    if e[0] == '':
        e = []
    if el[0] == '':
        el = []
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.changeAllAttendance((nameParts[0], nameParts[1], nameParts[2]),
                             term, request.form['sid'].strip(), a, l, e, el)
    return "done"

#WORK VIEW
@app.route('/changegrade', methods=["POST"])
@requireauth('changegrade')
def changegrade():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    grades = json.loads(request.form['grades'].strip())
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    student = mydb.changeGrade((nameParts[0], nameParts[1], nameParts[2] ), term, request.form['sid'].strip(), request.form['atype'].strip(), grades)
    return json.dumps(student['students'])
#=============================================


# ASSIGNMENT VIEW FUNCTIONS
@app.route('/savegrades', methods=["POST"])
@requireauth('savegrades')
def savegrades():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    g = json.loads(request.form['grades'].strip())
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'

    mydb.setMassGrades( (nameParts[0], nameParts[1], nameParts[2] ),
                        term,
                        request.form['aname'].strip(), request.form['atype'].strip(), 
                        request.form['apublic'].strip(),
                        float(request.form['points'].strip()), g);
    return "done"

@app.route('/getassignments', methods=["POST"])
@requireauth('getassignments')
def getassignments():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    assignments = mydb.getAssignments((nameParts[0],nameParts[1],nameParts[2]), term)
    return json.dumps( assignments )

@app.route('/getassignment', methods=["POST"])
@requireauth('getassignment')
def getassignment():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    try:
        assignment = mydb.getAssignment((nameParts[0],nameParts[1],nameParts[2]), term,
                                     request.form['aname'].strip())
        return json.dumps( assignment )
    except:
        return '{"grades":[]}'

@app.route('/deletegrades', methods=["POST"])
@requireauth('deletegrades')
def deletegrades():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    ids = json.loads(request.form['ids'])
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    print ids
    mydb.deleteAssignment( (nameParts[0], nameParts[1], nameParts[2] ),
                           term, ids,
                           request.form['aname'].strip(), request.form['atype'].strip()); 
    return "done"

#=============================================


# GRADE MODE FUNCTIONS
@app.route('/changeweights', methods=["POST"])
@requireauth('changeweights')
def changeweights():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    weights =  json.loads(request.form['weights'].strip())
    mydb = db.db()

    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.changeWeights((nameParts[0], nameParts[1], nameParts[2]),term,
                        weights)
    return "done"

@app.route('/createassignmenttype', methods=["POST"])
@requireauth('createassignmenttype')
def createassignmenttypr():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    atname = request.form['atname'].strip()
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.addAssignmentType((nameParts[0], nameParts[1], nameParts[2]),term,
                           atname)
    return 'done'

@app.route('/removeassignmenttype', methods=["POST"])
@requireauth('removeassignmenttype')
def removeassignmenttypr():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    atname = request.form['atname'].strip()
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.removeAssignmentType((nameParts[0], nameParts[1], nameParts[2]),term,
                           atname)
    print atname
    return 'done'

@app.route('/savegradeoptions', methods=["POST"])
@requireauth('savegradeoptions')
def savegradeoptions():
    clsn = request.form["classname"].strip()
    term = request.form['term'].strip()
    nameParts = clsn.split("-")
    option = request.form['option'].strip()
    mydb = db.db()

    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    
    mydb.saveGradeOptions((nameParts[0], nameParts[1], nameParts[2]),term, option)
    return "done";

#=============================================

if __name__=="__main__":
#    app.debug=True
    app.run()
#    app.run(host='0.0.0.0')
