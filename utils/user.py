from functools import wraps
from flask import Flask, session, url_for, redirect, render_template
from socket import gethostname
import xmlrpclib
import md5
import getpass
import db

from pymongo import Connection
import hashlib

I_USERNAME = 0
I_DBUSERNAME = 1
I_PASSWORD = 2

def getUsers():
    connection = Connection()
    userCollection = connection.gradebook2.users
    users = [ (x['uname'], x['dbname'], x['password'], x['usage']) for x in userCollection.find()]
    return users

def getUserList():
    connection = Connection()
    userCollection = connection.gradebook2.users
    users = [ x['uname'] for x in userCollection.find()]
    return users

def addUser(user, dbuser, passw):
    connection = Connection()
    userCollection = connection.gradebook2.users
    pw = hashlib.sha1( passw ).hexdigest()
    userCollection.insert( { 'uname' : user, 'dbname' : dbuser, 'password' : pw, 'usage' : 0 } )

def removeUser( uname ):
    connection = Connection()
    userCollection = connection.gradebook2.users
    userCollection.remove( {'uname' : uname} )


def newUser( dbusers ):
    dbusercheck = False
    usercheck = False
    pwcheck = False

    connection = Connection()
    userCollection = connection.gradebook2.users

    while not dbusercheck:
        dbuser = raw_input('Enter name in database: ')
        if dbuser not in dbusers:
            print dbuser + ' is not in the database.\n'
        else:
            dbusercheck = True
    
    while not usercheck:
        user = raw_input('Enter username: ')
        if userCollection.find_one( {'uname': user} ):
            print user + ' is already in user, choose a new name.\n'
        else:
            usercheck = True

    while not pwcheck:
        passw1 = getpass.getpass()
        passw2 = getpass.getpass('Retype password:')
        
        if passw1 != passw2:
            print 'passwords do not match, try again\n'
        else:
            pwcheck = True

    pw = hashlib.sha1( passw1 ).hexdigest()
    addUser(user, dbuser, passw1)

def newPW():
    usercheck = False
    pwcheck = False

    connection = Connection()
    userCollection = connection.gradebook2.users

    while not usercheck:
        user = raw_input('Enter username: ')
        if userCollection.find_one( {'uname': user} ):
            usercheck = True
        else:
            print user + ' is not a valid user'

    while not pwcheck:
        passw1 = getpass.getpass()
        passw2 = getpass.getpass('Retype password:')
        
        if passw1 != passw2:
            print 'passwords do not match, try again\n'
        else:
            pwcheck = True

    pw = hashlib.sha1( passw1 ).hexdigest()
    userCollection.update( {'uname':user}, { '$set' : { 'password' : pw } })
    

def authenticate( uname, passw ):
    connection = Connection()
    userCollection = connection.gradebook2.users

    pw = hashlib.sha1( passw ).hexdigest()
    user = userCollection.find_one( {'uname' : uname} )
    if user and user['password'] == pw:
        return True
    return False

def markUsage( user ):
    connection = Connection()
    userCollection = connection.gradebook2.users
    user = userCollection.find_one( {'uname' : uname} )
    usage = user['usage']
    usage+= 1
    userCollection.update( {'uname':user}, { '$set' : { 'usage' : usage } })

def getDBUser( uname ):
    connection = Connection()
    userCollection = connection.gradebook2.users
    user = userCollection.find_one( {'uname' : uname} )
    return user['dbname']

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

def delUser():
    usercheck = False
    connection = Connection()
    userCollection = connection.gradebook2.users

    while not usercheck:
        uname = raw_input("Enter username: ")
        if userCollection.find_one( {'uname' : uname} ):
            usercheck = True
        else:
            print uname + ' is not a valid username.\n'

    removeUser(uname)
    
def showUsers():
    users = getUsers()
    print '\nCurrent Users:'
    for user in users:
        print user[0] + '\t' + user[1]

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
