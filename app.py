#!/usr/bin/python
from flask import Flask, request, render_template, url_for, redirect, session, make_response
import urllib2,json
import datetime
import json
from socket import gethostname
from utils import db
from utils import user
from utils.user import requireauth

if gethostname() == 'nibbler':
    userfile = '/var/www/gradebook/data/gbusers'
else:
    userfile = 'data/gbusers'

CURRENT_TERM = '2013-fall'

app = Flask(__name__)
app.secret_key='2r\xe9w| \xcf\xb7f\xc8\x94p\xd0\xfb\xb6\x96VZ`\x14\x1c\x05X\xb7'


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
            u = request.form['user']
            p = request.form['pass']
        else:
            u = 'anon'
        if u not in user.getUsers(userfile): #userdic.keys():
            print u
            print 'no esta aqui'
            return redirect(url_for('login'))
        elif user.authenticate( u, p, userfile ):
            session['user'] = u
            session['teacher'] = user.getDBUser(u, userfile) #userdic[u]
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

#=============================================


# GENERAL CLASS VIEWING FUNCTIONS
@app.route("/classview", methods = ["POST", "GET"])
@requireauth('classview')
def classview():
    if request.method == 'POST':
        term = request.form['term']
    else:
        term = request.args.get('term')
    if term == 'other':
        try:
            c = request.form["classname"]
            c = c.split(' ')
            cls = c[1]
            term = c[0]
        except:
            return redirect( url_for('selectclass'))
    else:
        if request.method == 'POST':
            cls = request.form["classname"]
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
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    cls = mydb.getClass( (nameParts[0], nameParts[1], nameParts[2] ), term )
    try:
        mydb.resizeClass( (nameParts[0], nameParts[1], nameParts[2] ),
                          term, request.form["rows"], request.form["cols"])
    except KeyError:
        pass
    return json.dumps( cls[0] )

@app.route("/seated", methods=["POST"])
@requireauth('seated')
def seated():
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.setSeated( (nameParts[0], nameParts[1], nameParts[2]), term,
                  request.form["seated"],
                  request.form['rows'], request.form['cols'])
    return "seated set"

@app.route("/validip", methods = ["POST"])
@requireauth('validip')
def validip():
    allowedIPs=['149.89.','10.32.','127.0.0.1','165.155.2', '10.55.', '69.55.54.210']
    ip = request.remote_addr
    for i in  allowedIPs:
        if ip.startswith( i ):
            return 'true'
    return 'false'
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
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    if request.form['absent'] != '':
        abss = request.form['absent'].split('_')
    else:
        abss = []
    if request.form['late'] != '':
        lats = request.form['late'].split('_')
    else:
        lats = []
    if request.form['excused'] != '':
        excs = request.form['excused'].split('_')
    else:
        excs = []
    if request.form['exlates'] != '':
        exlates = request.form['exlates'].split('_')
    else:
        exlates = []
    date = request.form['date']
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.setMassAttendance( (nameParts[0], nameParts[1], nameParts[2] ),
                    term, abss, lats, excs, exlates, date )
    return "done"

@app.route("/gettoday", methods=["POST"])
@requireauth('gettoday')
def gettoday():
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    a = mydb.getTodaysAttendance((nameParts[0], nameParts[1], nameParts[2]), term, request.form['date'], 'absent')
    l = mydb.getTodaysAttendance((nameParts[0], nameParts[1], nameParts[2]), term, request.form['date'], 'late')
    e = mydb.getTodaysAttendance((nameParts[0], nameParts[1], nameParts[2]), term, request.form['date'], 'excused')
    el = mydb.getTodaysAttendance((nameParts[0], nameParts[1], nameParts[2]), term, request.form['date'], 'exlate')
    d = {'absent':a, 'late':l, 'excused':e, 'exlate':el}
    return json.dumps(d)
#=============================================

# ARRANGE VIEW FUNCTIONS
@app.route("/reseat", methods=["POST"])
@requireauth('reseat')
def reseat():
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    id1 = request.form["id1"]
    row1= request.form["row1"]
    col1 = request.form["col1"]
    id2 = request.form["id2"]
    row2= request.form["row2"]
    col2 = request.form["col2"]
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
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.setSeat( (nameParts[0], nameParts[1], nameParts[2] ), term,
                  request.form['sid'], 
                  request.form['row'], request.form['col'])
    return "done"
#=============================================

# STUDENT VIEW FUNCTIONS
@app.route('/addstudent', methods=["POST"])
@requireauth('addstudent')
def addstudent():
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.addStudent( (nameParts[0], nameParts[1], nameParts[2] ),term,
                     request.form['first'], request.form['last'],
                     request.form['nick'], request.form['sid'], 
                     request.form['email'], int(request.form['row']),
                     int(request.form['col'] ), request.form['stuyid'],
                     request.form['hr']);
    return "done"

@app.route('/getinfo', methods=["POST"])
@requireauth('getinfo')    
def getinfo(): 
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    student = mydb.getStudent((nameParts[0], nameParts[1], nameParts[2] ), term, request.form['sid'])
    return json.dumps(student['students'])

@app.route('/removestudent', methods=["POST"])
@requireauth('removestudent')
def removestudent():
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.removeStudent((nameParts[0], nameParts[1], nameParts[2]),term,
                        request.form['sid'])
    return "done"
                                        
@app.route("/transferstudent", methods=["POST"])
@requireauth('transferstudent')
def transferstudent():
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    targetClsn = request.form['targetclass']
    targetParts = targetClsn.split('-')
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    spot = mydb.openSpot((targetParts[0],targetParts[1],targetParts[2]), term)
    if spot:
        mydb.transfer((nameParts[0],nameParts[1],nameParts[2]),
                      (targetParts[0],targetParts[1],targetParts[2]),
                      term, request.form['sid'])
        return "done"
    else:
        return "false"

#INFO MODE
@app.route('/saveinfo', methods=["POST"])
@requireauth('saveinfo')
def saveinfo():
    print request.form
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    student = mydb.saveInfo((nameParts[0], nameParts[1], nameParts[2]),
                            term,
                            request.form['sid'], request.form['nick'],
                            request.form['id'], request.form['email'],
                            request.form['stuyid'], request.form['hr'])
    return json.dumps(student['students'])

# ATTENDANCE VIEW
@app.route("/changeattendance", methods=["POST"])
@requireauth("changeattendance")
def changeAttendance():
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    a = request.form['absent'].split('_')
    l = request.form['late'].split('_')
    e = request.form['excused'].split('_')
    el = request.form['exlate'].split('_')
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
                             term, request.form['sid'], a, l, e, el)
    return "done"

#WORK VIEW
@app.route('/changegrade', methods=["POST"])
@requireauth('changegrade')
def changegrade():
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    grades = json.loads(request.form['grades'])
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    student = mydb.changeGrade((nameParts[0], nameParts[1], nameParts[2] ), term, request.form['sid'], request.form['atype'], grades)
    return json.dumps(student['students'])
#=============================================


# ASSIGNMENT VIEW FUNCTIONS
@app.route('/savegrades', methods=["POST"])
@requireauth('savegrades')
def savegrades():
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    g = json.loads(request.form['grades'])
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.setMassGrades( (nameParts[0], nameParts[1], nameParts[2] ),
                        term,
                        request.form['aname'], request.form['atype'], 
                        float(request.form['points']), g);
    return "done"

@app.route('/getassignments', methods=["POST"])
@requireauth('getassignments')
def getassignments():
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    assignments = mydb.getAssignments((nameParts[0],nameParts[1],nameParts[2]), term)
    return json.dumps( assignments )

@app.route('/getassignment', methods=["POST"])
@requireauth('getassignment')
def getassignment():
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    try:
        assignment = mydb.getAssignment((nameParts[0],nameParts[1],nameParts[2]), term,
                                     request.form['aname'])
        return json.dumps( assignment )
    except:
        return '{"grades":[]}'
#=============================================


# GRADE MODE FUNCTIONS
@app.route('/changeweights', methods=["POST"])
@requireauth('changeweights')
def changeweights():
    clsn = request.form["classname"]
    term = request.form['term']
    nameParts = clsn.split("-")
    weights =  json.loads(request.form['weights'])
    mydb = db.db()

    print 'weights:'
    print weights

    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ), term ):
        return 'false'
    mydb.changeWeights((nameParts[0], nameParts[1], nameParts[2]),term,
                        weights)
    return "done";
#=============================================

if __name__=="__main__":
    app.debug=True
    app.run()
#    app.run(host='0.0.0.0')
