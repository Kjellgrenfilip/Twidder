import sqlite3
from flask import g, json
import json

DATABASE_URL = 'dbtest.db'

def get_dB():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE_URL)
    return db

def findUser(email):
    cursor = get_dB().execute("SELECT * FROM Users where email=?;", [email])
    output = cursor.fetchone()
    cursor.close()

    if output:
        response = {'email': output[0], 'password': output[1]}  #Kanske ska vi skicka med all information om användaren, beror på lite vad som kommer behlövas senare.
        return response
    else:
        return False #Vad ska man returnera när användaren inte finns?

def createUser(email, pw, firstname, familyname, gender, country, city):
    try:
        get_dB().execute("insert into Users values(?,?,?,?,?,?,?);", [email,pw,firstname,familyname,gender,country,city])
        get_dB().commit()
    except:
        print("SQL query for creating user failed")
        return False
    return True #Om användaren lyckades skapas
    
 

    
