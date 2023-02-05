import sqlite3
from flask import g, json
import json

DATABASE_URL = 'dbtest.db'
#-----------------------HELP FUNCTIONS--------------------------------
def get_dB():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE_URL)
    return db


#Kanske en funktion som initierar databasen?
#Kanske en funktion som "stänger/disconnectar"


#-----------------------QUERY-functions--------------------------------
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

def signInUser(email, token):
    try:
        get_dB().execute("insert into loggedInUsers values(?,?);", [email,token])
        get_dB().commit()
    except:
        print("SQL query for signing in user failed")
        return False
    return True #Om användaren lyckades skapas

def getLoggedInUser(token):
    cursor = get_dB().execute("SELECT * FROM loggedInUsers where token=?;", [token])
    output = cursor.fetchall()[0]
    cursor.close()

    if output:
        response = {'email': output[0], 'token': token}  #Returnerar email b.la. så att man kan komma åt userinfo sen
        return response
    else:
        return False #Vad ska man returnera när användaren inte finns?
    
def updatePassword(token, newpw):
    try:
        email = getLoggedInUser(token)['email']
        get_dB().execute("UPDATE Users SET pw=? WHERE email=?", [newpw,email])
        get_dB().commit()
    except:
        print("SQL query updatePassword failed")
        return False
    return True 

def getUserData(email=None, token=None): #Använder samma funktion för email/token. Man kan välja
    cursor = get_dB().cursor()
    try:
        if email:
            cursor.execute("SELECT * from Users where email=?;", [email])
        elif token:
            user = getLoggedInUser(token)
            cursor.execute("SELECT * from Users where email=?;", [user['email']])
        user_data = cursor.fetchall()[0]
        response = {
            'email': user_data[0],
            'firstname': user_data[2],
            'familyname': user_data[3],
            'gender': user_data[4],
            'country': user_data[5],
            'city': user_data[6]
        }
        cursor.close()
        print(response)
        return response #Kan lika gärna returna direkt men gjorde såhär för min egna läsbarhet
    except:
        cursor.close()
        return False
    

def signOutUser(token):
    try:
        get_dB().execute("DELETE from loggedInUsers WHERE token=?", [token])
        get_dB().commit()
        return True
    except:
        print("failed to delete logged in user")
        return False
    
def post_message(token, msg, to_email):
    user = getLoggedInUser(token)
    try:
        get_dB().execute("insert into userMessages values(?,?,?);", [to_email, user['email'], msg])
        get_dB().commit()
        return True
    except:
        return False
    
    
 

    
