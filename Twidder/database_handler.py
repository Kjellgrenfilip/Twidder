import sqlite3
from flask import g, json
import json

DATABASE_URL = 'database.db'
#-----------------------HELP FUNCTIONS--------------------------------
def get_dB():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE_URL)
    return db


#Kanske en funktion som initierar databasen?

def disconnect():
    db = getattr(g,'db', None)
    if db is not None:
        g.db.close()
        g.db = None

#Logik: Returnera False = exception -> server skickar statuskod 500
#       Returnera None = ingen rad matchade query
#-----------------------QUERY-functions--------------------------------

def findUser(email):
    try:
        cursor = get_dB().execute("SELECT * FROM Users where email=?;", [email])
        output = cursor.fetchone()
        cursor.close()
        
        if output == None:
            return None

        response = {'email': output[0], 'password': output[1]}  #Kanske ska vi skicka med all information om användaren, beror på lite vad som kommer behlövas senare.
        return response
        
    except:
        return False

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
    try:
        cursor = get_dB().execute("SELECT * FROM loggedInUsers where token=?;", [token])
        output = cursor.fetchone()
        cursor.close()
        if output == None:
            return None
        
        response = {'email': output[0], 'token': token} 
        return response
    except:
        return False #Returnerar False om något fel inträffar i databasen

def getPassword(token):
    try:
        email = getLoggedInUser(token)['email']
        cursor = get_dB().execute("SELECT pwd FROM Users where email=?;", [email])
        output = cursor.fetchone()
        cursor.close()
        return output[0]
    except:
        return None

def updatePassword(token, newpw):
    try:
        email = getLoggedInUser(token)['email']
        get_dB().execute("UPDATE Users SET pwd=? WHERE email=?", [newpw,email])
        get_dB().commit()
    except:
        print("SQL query updatePassword failed")
        return False
    return True 

def getUserData(email): #Använder samma funktion för email/token. Man kan välja
    cursor = get_dB().cursor()
    try:
        cursor.execute("SELECT * from Users where email=?;", [email])
        user_data = cursor.fetchone()
        cursor.close()
        if user_data == None:
            return None
        response = {
            'email': user_data[0],
            'firstname': user_data[2],
            'familyname': user_data[3],
            'gender': user_data[4],
            'country': user_data[5],
            'city': user_data[6]
        }
        
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
    
def postMessage(from_email, msg, to_email):
    try:
        get_dB().execute("insert into userMessages (toEmail, fromEmail, msg) values(?,?,?);", [to_email,from_email, msg])
        get_dB().commit()
        return True
    except:
        return False
    

def getMessages(email):
    try:
        if email is not None:
            cursor= get_dB().execute("SELECT * from userMessages where toEmail=?;", [email])
        response = {}
        
        if cursor == None:
            return response
        
        msg_id = 0
        for row in cursor.fetchall():
            response[msg_id] = {'toEmail':   row[1],
                                'fromEmail': row[2],
                                'msg':       row[3]
                               }
            msg_id += 1

        cursor.close()
        return response 
    except:
        cursor.close()
        return False
    
    
    
 

    
