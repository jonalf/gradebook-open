#!/usr/bin/python
from flask import Flask, request, render_template, url_for, redirect, session, make_response
import urllib2,json
import datetime
import json
from utils import db
from utils import user
from utils.user import requireauth

userdic = { 'jdyrlandweaver' : 'DYRLAND',
            'tester' : 'TESTER' }

app = Flask(__name__)
app.secret_key='2r\xe9w| \xcf\xb7f\xc8\x94p\xd0\xfb\xb6\x96VZ`\x14\x1c\x05X\xb7'

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
        if user.authenticate( u, p ):
            session['user'] = u
            session['teacher'] = userdic[u]
            print session
            return redirect( url_for('selectclass'))
        else:
            return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('teacher', None)
    return redirect( url_for('login'))

@app.route("/classview", methods = ["POST", "GET"])
@requireauth('classview')
def classview():
    cls = request.form["classname"]    
    return render_template("classview.html", clsname = cls)


@app.route("/loadclass", methods = ["POST"])
@requireauth('loadclass')
def loadclass():
    clsn = request.form["classname"]
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    cls = mydb.getClass( (nameParts[0], nameParts[1], nameParts[2] ) )
    try:
        mydb.resizeClass( (nameParts[0], nameParts[1], nameParts[2] ),
                          request.form["rows"], request.form["cols"])
    except KeyError:
        pass
    return json.dumps( cls[0] )

@app.route("/reseat", methods=["POST"])
@requireauth('reseat')
def reseat():
    clsn = request.form["classname"]
    nameParts = clsn.split("-")
    id1 = request.form["id1"]
    row1= request.form["row1"]
    col1 = request.form["col1"]
    id2 = request.form["id2"]
    row2= request.form["row2"]
    col2 = request.form["col2"]
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    mydb.setSeat( (nameParts[0], nameParts[1], nameParts[2] ), 
                  id1, row1, col1)
    mydb.setSeat( (nameParts[0], nameParts[1], nameParts[2] ), 
                  id2, row2, col2)
    return "done"

@app.route("/setseat", methods=["POST"])
@requireauth('setseat')
def setseat():
    clsn = request.form["classname"]
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    mydb.setSeat( (nameParts[0], nameParts[1], nameParts[2] ),
                  request.form['sid'], 
                  request.form['row'], request.form['col'])
    return "done"

@app.route("/saveattendance", methods=["POST"])
@requireauth('saveattendance')
def saveattendance():
    clsn = request.form["classname"]
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
    date = request.form['date']
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    mydb.setMassAttendance( (nameParts[0], nameParts[1], nameParts[2] ),
                    abss, lats, excs, date )
    return "done"

@app.route("/changeattendance", methods=["POST"])
@requireauth("changeattendance")
def changeAttendance():
    clsn = request.form["classname"]
    nameParts = clsn.split("-")
    a = request.form['absent'].split('_')
    l = request.form['late'].split('_')
    e = request.form['excused'].split('_')
    if a[0] == '':
        a = []
    if l[0] == '':
        l = []
    if e[0] == '':
        e = []
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    mydb.changeAllAttendance((nameParts[0], nameParts[1], nameParts[2]),
                             request.form['sid'], a, l, e)
    return "done"

@app.route("/gettoday", methods=["POST"])
@requireauth('gettoday')
def gettoday():
    clsn = request.form["classname"]
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    a = mydb.getTodaysAttendance((nameParts[0], nameParts[1], nameParts[2]), request.form['date'], 'absent')
    l = mydb.getTodaysAttendance((nameParts[0], nameParts[1], nameParts[2]), request.form['date'], 'late')
    e = mydb.getTodaysAttendance((nameParts[0], nameParts[1], nameParts[2]), request.form['date'], 'excused')
    d = {'absent':a, 'late':l, 'excused':e}
    return json.dumps(d)

@app.route("/seated", methods=["POST"])
@requireauth('seated')
def seated():
    clsn = request.form["classname"]
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    mydb.setSeated( (nameParts[0], nameParts[1], nameParts[2] ),
                  request.form["seated"],
                  request.form['rows'], request.form['cols'])
    return "seated set"

@app.route('/savegrades', methods=["POST"])
@requireauth('savegrades')
def savegrades():
    clsn = request.form["classname"]
    nameParts = clsn.split("-")
    g = json.loads(request.form['grades'])
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    mydb.setMassGrades( (nameParts[0], nameParts[1], nameParts[2] ),
                        request.form['aname'], request.form['atype'], 
                        float(request.form['points']), g);
    return "done"

@app.route('/changegrade', methods=["POST"])
@requireauth('changegrade')
def changegrade():
    clsn = request.form["classname"]
    nameParts = clsn.split("-")
    grades = json.loads(request.form['grades'])
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    student = mydb.changeGrade((nameParts[0], nameParts[1], nameParts[2] ), request.form['sid'], request.form['atype'], grades)
    return json.dumps(student['students'])

@app.route('/changeweights', methods=["POST"])
@requireauth('changeweights')
def changeweights():
    clsn = request.form["classname"]
    nameParts = clsn.split("-")
    types =  json.loads(request.form['types'])
    weights =  json.loads(request.form['weights'])
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    mydb.changeWeights( (nameParts[0], nameParts[1], nameParts[2] ),
                        types, weights)
    return "done";

@app.route('/saveinfo', methods=["POST"])
@requireauth('saveinfo')
def saveinfo():
    print request.form
    clsn = request.form["classname"]
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    student = mydb.saveInfo((nameParts[0], nameParts[1], nameParts[2] ), 
                            request.form['sid'], request.form['nick'],
                            request.form['id'], request.form['email'],
                            request.form['stuyid'], request.form['hr'])
    return json.dumps(student['students'])

@app.route('/getinfo', methods=["POST"])
@requireauth('getinfo')    
def getinfo(): 
    clsn = request.form["classname"]
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    student = mydb.getStudent((nameParts[0], nameParts[1], nameParts[2] ), request.form['sid'])
    return json.dumps(student['students'])

@app.route('/removestudent', methods=["POST"])
@requireauth('removestudent')
def removestudent():
    clsn = request.form["classname"]
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    mydb.removeStudent( (nameParts[0], nameParts[1], nameParts[2] ),
                        request.form['sid'])
    return "done"

@app.route('/addstudent', methods=["POST"])
@requireauth('addstudent')
def addstudent():
    clsn = request.form["classname"]
    nameParts = clsn.split("-")
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    mydb.addStudent( (nameParts[0], nameParts[1], nameParts[2] ),
                     request.form['first'], request.form['last'],
                     request.form['nick'], request.form['sid'], 
                     request.form['email'], int(request.form['row']),
                     int(request.form['col'] ), request.form['stuyid'],
                     request.form['hr']);
    return "done"
                                        
@app.route("/transferstudent", methods=["POST"])
@requireauth('transferstudent')
def transferstudent():
    clsn = request.form["classname"]
    nameParts = clsn.split("-")
    targetClsn = request.form['targetclass']
    targetParts = targetClsn.split('-')
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    spot = mydb.openSpot((targetParts[0],targetParts[1],targetParts[2]))
    if spot:
        mydb.transfer((nameParts[0],nameParts[1],nameParts[2]),
                      (targetParts[0],targetParts[1],targetParts[2]),
                      request.form['sid'])
        return "done"
    else:
        return "false"

@app.route('/getbackup', methods=['POST', 'GET'])
@requireauth('getbackup')
def getbackup():
    clsn = request.args.get('classname')
    nameParts = clsn.split("-")    
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    backup = mydb.getBackup((nameParts[0], nameParts[1], nameParts[2]))
    backup = json.dumps( backup )
    response = make_response( backup )
    response.headers['Content-Disposition'] = 'attachment; filename=' + clsn + '-' + str(datetime.date.today()) + '.bak'
    return response

@app.route('/backuprestore', methods=['POST'])
@requireauth('backuprestore')
def backupreset():
    backup = request.files['backupfile']
    backup = backup.read()
    backup = json.loads(backup)
    clsn = backup['code'] + "-" + backup['section'] + '-' + backup['period']
    nameParts = clsn.split("-")    
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    mydb.resetFromBackup(backup)
    return render_template("classview.html", clsname = clsn)

@app.route('/getbackupcsv', methods=['POST', 'GET'])
@requireauth('getbackupcsv')
def getbackupcsv():
    clsn = request.args.get('classname')
    nameParts = clsn.split("-")    
    mydb = db.db()
    if session['teacher'] != mydb.getTeacher( (nameParts[0], nameParts[1], nameParts[2] ) ):
        return 'false'
    backup = mydb.getBackupCSV((nameParts[0], nameParts[1], nameParts[2]))
    response = make_response( backup )
    response.headers['Content-Disposition'] = 'attachment; filename=' + clsn + '-' + str(datetime.date.today()) + '.csv'
    return response

@app.route("/validip", methods = ["POST"])
@requireauth('validip')
def validip():
    allowedIPs=['149.89.','10.32.','127.0.0.1','165.155.2']
    ip = request.remote_addr
    for i in  allowedIPs:
        if ip.startswith( i ):
            return 'true'
    return 'false'

@app.route("/selectclass")
@requireauth('selectclass')
def selectclass():
    return render_template("selectclass.html")

@app.route("/loadselect", methods = ["POST"])
@requireauth('loadselect')
def loadselect():
    teacher = session['teacher']
    mydb = db.db();
    return json.dumps( mydb.getClasses(teacher) )



if __name__=="__main__":
    app.debug=True
    app.run()
#    app.run(host='0.0.0.0')
