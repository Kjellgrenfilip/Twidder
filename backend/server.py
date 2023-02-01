from flask import Flask, request, json, jsonify, make_response
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

#Fattar inte om bara själva datan ska returneras i Json eller hela responsen? Oklart i lab-PM
def createRespons(s_code,data=None): #Kan lägga till fler medlemmar sen som authorization och sånt
    if(data == None):
        return make_response('', s_code)
    else:
        return make_response(data, s_code)



@app.route("/user/sign_in", methods=["POST"])
def sign_in():
    data = request.get_json()
   
    if 'email' not in data or 'password' not in data:
        return createRespons(400)
    else:
        try:
            resp = db.findUser(data['email'])
            if (data['password'] == resp['password']):
                token = createUserToken(data['email']) #Lyckad inloggning, skapar en token som ska returneras
                return createRespons(200, jsonify(token=token))
            else:
                return createRespons(401) #Lösenordet matchar inte 401=Unauthorized
        except:
            return createRespons(404)  #Användaren finns ej 404=Server could not find the requested ressource
        
@app.route("/user/sign_up", methods=["POST"])
def sign_up():
    data = request.get_json()
    #Extremt ful if-sats hehehehe ska fixa bättre när jag har bättre koll - Kolla om all krävd data är given
    if 'email' in data and 'password' in data and 'firstname' in data and 'familyname' in data and 'gender' in data and 'country' in data and 'city' in data:
        if len(data['password']) > 7:
            #response = db.findUser(data['email'])
            if db.findUser(data['email']) == False:
                user = db.createUser(data['email'], data['password'],data['firstname'], data['familyname'],data['gender'],data['country'], data['city'])
                if user:
                    #Om användaren ska loggas in direkt bör vi här skapa en token och returnera typ
                    return createRespons(200, jsonify(message="User Succesfully Created"))
            else:
                print("user not created, already exists")
                return createRespons(409, jsonify(message="User Already Exists")) #User already exists - 409 = Conflict with current resources?
        else:
            return createRespons(400, jsonify("Password entered is too Short"))
    return createRespons(400, jsonify("Wrong data submitted"))

@app.route("/user/sign_out")
def sign_out():
    token = request.headers.get('Authorization')

    return

if __name__ == "__main__":
    app.debug = True
    app.run()


