from flask import Flask, request, json, jsonify
import random
import database_handler as db

LoggedInUsers = {}

app = Flask(__name__)

@app.route("/", methods=["GET"])
def root():
    return "Hello Filip", 200

def createUserToken(email):
    chars = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    token = ""
    for i in range(len(chars)):
        token += chars[random.randint(0, len(chars)-1)]
    LoggedInUsers[email] = token

    return token



@app.route("/user/sign_in", methods=["POST"])
def sign_in():
    data = request.get_json()
   
    if 'email' not in data or 'password' not in data:
        return '', 400
    else:
        try:
            resp = db.findUser(data['email'])
            if (data['password'] == resp['password']):
                token = createUserToken(data['email'])
                return '', 200 #oklart vilken status code. HÄr ska vi skapa en token eftersom löserordern matchade
            else:
                return '', 400    
        except:
            return '', 501
        
@app.route("/user/sign_up", methods=["POST"])
def sign_up():
    data = request.get_json()
    
    #Extremt ful if-sats hehehehe ska fixa bättre när jag har bättre koll - Kolla om all krävd data är given
    if 'email' in data and 'password' in data and 'firstname' in data and 'familyname' in data and 'gender' in data and 'country' in data and 'city' in data:
        if len(data['password']) > 7:
            response = db.findUser(data['email'])
            if response == False:
                user = db.createUser(data['email'], data['password'],data['firstname'], data['familyname'],data['gender'],data['country'], data['city'])
                if user:
                    #Om användaren ska loggas in direkt bör vi här skapa en token och returnera typ
                    print("user created")
                    return '', 200
            else:
                print("user not created, already exists")
                return '', 500 #User already exists
        else:
            return '', 301
    return '', 300

@app.route("/user/sign_out")
def sign_out():
    token = request.headers.get('Authorization')
    
    return

if __name__ == "__main__":
    app.debug = True
    app.run()


