from functools import wraps
from flask import Flask, session, url_for, redirect, render_template
import xmlrpclib
import md5

passdic = { 'jdyrlandweaver' : '\x1e\xa5RdH\x8a\xa8\x9e\x8f\x9c\xb1>\xcaZy.',
            'tester' : '\x1e\xa5RdH\x8a\xa8\x9e\x8f\x9c\xb1>\xcaZy.' }

def authenticate(user, passw):
    return user in passdic.keys() and md5.new(passw).digest() == passdic[user]
        

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
