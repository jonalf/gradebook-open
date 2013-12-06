from functools import wraps
from flask import Flask, session, url_for, redirect, render_template
from socket import gethostname
import xmlrpclib
import md5
import getpass
import db

I_USERNAME = 0
I_DBUSERNAME = 1
I_PASSWORD = 2

if gethostname() == 'nibbler':
    ufile = '/var/www/gradebook/data/gbusers'
else:
    ufile = '../data/gbusers'

def authenticate(user, passw, userfile=ufile):
    passw = md5.new(passw).digest()
    users = getUserList(userfile)
    for u in users:
        if user == u[I_USERNAME] and passw == u[I_PASSWORD]:
            return True
    return False

def requireauth(page):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user' not in session:
                return redirect( url_for('login'))
            else:
                return f(*args, **kwargs)
        return wrapper
    return decorator

def markUsage( user ):
    f = open('utils/usage', 'r')
    s = f.read().strip().split('\n');
    f.close()

    d = {}
    if s[0] != '':
        for line in s:
            l = line.split(':')
            d[l[0]] = int(l[1])
            
    if user in d.keys():
        d[user] = d[user] + 1
    else:
        d[user] = 0
    s = ''
    for u in d:
        s+= u + ':' + str(d[u]) + '\n'
    
    f = open('utils/usage', 'w')
    f.write(s)
    f.close()


def getDBUser(user, userfile=ufile):
    users = getUserList(userfile)
    for u in users:
        if user == u[I_USERNAME]:
            return u[I_DBUSERNAME]
    return False

def getUsers(userfile = ufile):
    users = getUserList(userfile)
    uList = []
    for u in users:
        uList.append(u[I_USERNAME])
    return uList

def getUserList(userfile=ufile):
    f = open(userfile)
    users = f.read().strip().split('\n');
    f.close()
    i = 0
    while i < len(users):
        users[i] = users[i].split(',')
        i+=1
    return users
        
def addUser(user, dbuser, passw, userfile=ufile):
    pw = md5.new(passw).digest()
    line = ','.join([user, dbuser, pw])
    line+= '\n'
    f = open(userfile, 'a')
    f.write( line )
    f.close()

def newUser(dbusers, userfile=ufile):
    pwcheck = False
    dbusercheck = False
    usercheck = False
    
    f = open(userfile)
    s = f.read().strip().split('\n');
    f.close()
    users = getUsers()

    while not dbusercheck:
        dbuser = raw_input('Enter name in database: ')
        if dbuser not in dbusers:
            print dbuser + ' is not in the database.\n'
        else:
            dbusercheck = True
        
    while not usercheck:
        user = raw_input("Enter username: ")
        if user in users:
            print user + ' is already in use, choose a new name.\n'
        else:
            usercheck = True

    while not pwcheck:
        passw1 = getpass.getpass()
        passw2 = getpass.getpass('Retype password:')
        
        if passw1 != passw2:
            print 'passwords do not match, try again\n'
        else:
            pwcheck = True
    addUser(user, dbuser, passw1)

def newPW():
    usercheck = False
    pwcheck = False
    users = getUsers()

    while not usercheck:
        user = raw_input("Enter username: ")
        if user not in users:
            print user + ' is not a valid username.\n'
        else:
            usercheck = True

    while not pwcheck:
        passw1 = getpass.getpass()
        passw2 = getpass.getpass('Retype password:')
        
        if passw1 != passw2:
            print 'passwords do not match, try again\n'
        else:
            pwcheck = True
    passw1 = md5.new(passw1).digest()
    changePW(user, passw1)
    
def changePW(user, passw, userfile=ufile):
    lines = getUserList()
    i = 0
    while i < len(lines):
        if lines[i][I_USERNAME] == user:
            lines[i][I_PASSWORD] = passw
        i+=1

    f = open(userfile, 'w')
    for l in lines:
        line = ','.join(l)
        line+= '\n'
        f.write( line )
    f.close()

def delUser():
    usercheck = False
    users = getUsers()

    while not usercheck:
        user = raw_input("Enter username: ")
        if user not in users:
            print user + ' is not a valid username.\n'
        else:
            usercheck = True
    removeUser(user)
    
def removeUser(user, userfile=ufile):
    lines = getUserList()
    i = 0

    f = open(userfile, 'w')
    for l in lines:
        if l[I_USERNAME] != user:
            line = ','.join(l)
            line+= '\n'
            f.write( line )
    f.close()

def showUsers():
    users = getUserList()
    print '\nCurrent Users:'
    for user in users:
        print user[I_USERNAME] + '\t' + user[I_DBUSERNAME]

#Functions for interactive mode
def menu():
    choiceCheck = False

    while not choiceCheck:
        menuText = '1: Add a new user\n'
        menuText+= '2: Change a password\n'
        menuText+= '3: Remove a user\n'
        menuText+= '4: See full user list\n'
        print menuText
        selection = raw_input('Choice: ')        
        try:
            s = int(selection)
            return s
        except:
            choiceCheck = False

if __name__ == "__main__":
    mydb = db.db()
    dbusers = mydb.getTeachers()
    
    choice = menu()
    if choice == 1:
        newUser(dbusers)
    elif choice == 2:
        newPW()
    elif choice == 3:
        delUser()
    elif choice == 4:
        showUsers()
