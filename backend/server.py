from flask import Flask, request, json, jsonify, make_response
import random
import database_handler as db

LoggedInUsers = {}

app = Flask(__name__)

@app.route("/", methods=["GET"])
def root():
    return "Hello RalleBallz", 200
 #------------HJÄLPFUNKTIONER------------------
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
    
def isLoggedIn(token):
    user = db.getLoggedInUser(token)

    if user == False:
        return False
    return True

def validateUserInput(data):
    if len(data['email']) < 3 or len(data['email']) > 30:
        return False
    if len(data['password']) < 8:
        return False
    if len(data['firstname']) < 1 or len(data['firstname']) > 20:
        return False
    if len(data['familyname']) < 1 or len(data['familyname']) > 20:
        return False
    if len(data['gender']) < 1:
        return False
    if len(data['city']) < 1 or len(data['city']) > 20:
        return False
    if len(data['country']) < 1 or len(data['country']) > 20:
        return False
    return True

#Använde för att testa en db-helper funktion, kan tas bort
@app.route("/user/test_get", methods=["GET"])
def get_info():
    data = request.get_json()
    if 'email' in data:
        user = db.getUserData(email=data['email'])
        return createRespons(200, jsonify(user))
    elif 'token' in data:
        user = db.getUserData(data['token'])
        return createRespons(200, jsonify(user))
    
    return createRespons(503)


#------------REQUESTS------------------
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
                LoggedInUsers['email'] = token  #Lägger till Email + Token
                db.signInUser(data['email'], token)  #Tror det ska lagras i DB? Har för mig att man ska lägga till någon hashning senare
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
        if validateUserInput(data):
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

@app.route("/user/sign_out", methods=["DELETE"])
def sign_out():
    token = request.headers.get('Authorization')
    if isLoggedIn(token):
        if db.signOutUser(token):
            return createRespons(200)
        else:
            return createRespons(400)
        
    return createRespons(400)   
        
@app.route("/user/change_pw", methods=['PUT'])
def change_password(): #Får in Token i header, gamla + nya lösenordet i bodyn? 
    if 'Authorization' not in request.headers:
        return createRespons(401)
    token = request.headers['Authorization']
    data = request.get_json()
    if 'oldPW' in data and 'newPW' in data: #Kanske ska kolla på serversidan så att oldPW överensstämmer med det som finns i databas
        response = db.updatePassword(token, data['newPW'])
        print("kommer hit ay")
        if response:
            return createRespons(200)
    else:
        return createRespons(400)
    return createRespons(300)

        
@app.route("/user/get_user_data_by_email", methods=['GET'])
def get_user_data_by_email():
    data = request.get_json()
    token = request.headers.get('Authorization')
    if 'email' not in data or not token:
        return createRespons(400, jsonify('No email or/and token entered'))
    if isLoggedIn(data['email']):
        user_data = db.getUserData(email=data['email'])
    return createRespons(200, jsonify(user_data))

@app.route("/user/get_user_data_by_token", methods=['GET'])
def get_user_data_by_token():
    token = request.headers.get('Authorization') #Antar att man ska skicka token i header? 
    if not token:
        return createRespons(400, jsonify('No token entered'))
    
    user_data = db.getUserData(token=token)
    return createRespons(200, jsonify(user_data))
    
@app.route("/user/post_message", methods=['PUT'])
def post_message():
    data = request.get_json()
    token = request.headers.get('Authorization')
    if 'message' not in data or 'to_email' not in data or not token:
        return createRespons(400)
    if isLoggedIn(token) and db.findUser(data['email']):
        response = db.postMessage(token, data['message'],data['email'])
        if response:
            return createRespons(200)
        else:
            createRespons(402)
    else:
        return createRespons(401)
    
@app.route("/user/get_messages_by_email", methods=['GET'])
def get_messages_by_email():
    data = request.get_json()
    token = request.headers.get('Authorization')
    if 'email' in data and isLoggedIn(token):
        messages = db.getMessages(email=data['email'],token=token)
        if messages is not None:
            return createRespons(200, jsonify(messages))
        else:
            return createRespons(400)
    return

@app.route("/user/get_messages_by_token", methods=['GET'])
def get_messages_by_token():
    token = request.headers.get('Authorization')
    if token is None:
        return createRespons(400)
    if isLoggedIn(token): #Bör implementera en funktion som kollar så att användaren finns baserat på Token. Ska fixas
        messages = db.getMessages(token=token)
        if messages is not None:
            return createRespons(200, jsonify(messages))
        else:
            return createRespons(400)
    
if __name__ == "__main__":
    app.debug = True
    app.run()


