#!/usr/bin/python

def getFile( fname ):
    f = open( fname )
    s = f.read().strip()
    f.close()
    return s

def fixPosts( s ):
    fixed = s.replace('post("/', 'post("/gradebook/')
    fixed = fixed.replace("post('/", "post('/gradebook/")
    fixed = fixed.replace('action="/backuprestore', 'action="/gradebook/backuprestore') 
    fixed = fixed.replace('/classview', '/gradebook/classview')    
    fixed = fixed.replace('/newpw', '/gradebook/newpw')    
    return fixed

def fixPicLinks( s ):
    fixed = s.replace('/static/studentpics/', '/gradebook/static/studentpics/')
    return fixed
                    
def fixLinks( s ):
    fixed = s.replace('/logout', '/gradebook/logout')
    fixed = fixed.replace('/selectclass', '/gradebook/selectclass')
    fixed = fixed.replace('/static/scripts.js', '/gradebook/static/scripts2.js')
    fixed = fixed.replace('/static/style.css', '/gradebook/static/style.css')
    fixed = fixed.replace('/static/bootstrap/js/bootstrap.min.js', '/gradebook/static/bootstrap/js/bootstrap.min.js')
    fixed = fixed.replace('/static/bootstrap/css/bootstrap.min.css', '/gradebook/static/bootstrap/css/bootstrap.min.css')
    fixed = fixed.replace('/login', '/gradebook/login')
    fixed = fixed.replace('/classview', '/gradebook/classview')    
    fixed = fixed.replace('/pwreset', '/gradebook/pwreset')    
    return fixed

regFile = getFile('static/scripts.js')
fixFile = fixPosts( regFile )
fixFile = fixPicLinks( fixFile )
f = open('static/scripts2.js', 'w')
f.write(fixFile)
f.close()

templates = ['base.html', 'classview.html', 'login.html', 'selectclass.html', 'pwreset.html']
for t in templates:
    s = getFile('templates/' + t)
    newF = fixLinks( s )
    f = open('templates/' + t, 'w')
    f.write( newF )
    f.close()
