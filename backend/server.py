from flask import Flask, request, json, jsonify, make_response
import random
import database_handler as db

LoggedInUsers = {}

app = Flask(__name__)

@app.teardown_request
def teardown(e):
    db.disconnect()

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

def getPassword(token):
    return db.getPassword(token)

def emailToPassword(email):
    return db.findUser(email)['password']

def tokenToEmail(token):
    return db.getLoggedInUser(token)['email']

def userExists(email):
    resp = db.findUser(email)
    if resp == False:
        return False
    return True





#------------REQUESTS------------------
@app.route("/user/sign_in", methods=["POST"])
def sign_in():
    data = request.get_json()
    if 'email' not in data or 'password' not in data:
        return createRespons(400)
    else:
        try:
            if (data['password'] == emailToPassword(data['email']) and userExists(data['email'])):
                token = createUserToken(data['email']) #Lyckad inloggning, skapar en token som ska returneras
                LoggedInUsers['email'] = token  #Lägger till Email + Token
                db.signInUser(data['email'], token)  #Tror det ska lag is not None401=Unauthorized
                return createRespons(200, token)
        except:
            return createRespons(404)  #Användaren finns ej 404=Server could not find the requested ressource
        
@app.route("/user/sign_up", methods=["POST"])
def sign_up():
    data = request.get_json()
    #Extremt ful if-sats hehehehe ska fixa bättre när jag har bättre koll - Kolla om all krävd data är given
    if 'email' in data and 'password' in data and 'firstname' in data and 'familyname' in data and 'gender' in data and 'country' in data and 'city' in data:
        if validateUserInput(data):
            if not userExists(data['email']):
                user = db.createUser(data['email'], data['password'],data['firstname'], data['familyname'],data['gender'],data['country'], data['city'])
                if user:
                    return createRespons(200, jsonify(user))
            else:
                print("user not created, already exists")
                return createRespons(409, jsonify(message="User Already Exists")) #User already exists - 409 = Conflict with current resources?
        else:
            return createRespons(400, jsonify("Wrong User Input for signup"))
    return createRespons(400, jsonify("Not all data provided"))

@app.route("/user/sign_out", methods=["DELETE"])
def sign_out():
    token = request.headers.get('Authorization')
    if isLoggedIn(token):
        if db.signOutUser(token):
            return createRespons(200)
        else:
            return createRespons(400)
        
    return createRespons(400)   

#Fixa lite mer kontroller här
@app.route("/user/change_pw", methods=['PUT'])
def change_password(): #Får in Token i header, gamla + nya lösenordet i bodyn? 
    if 'Authorization' not in request.headers:
        return createRespons(401)
    token = request.headers['Authorization']
    if not isLoggedIn(token):
        return createRespons(401)
    data = request.get_json()
    if 'oldPW' in data and 'newPW' in data: #Kanske ska kolla på serversidan så att oldPW överensstämmer med det som finns i databas
        if data['oldPW'] != getPassword(token):
            return createRespons(401, "Old password is incorrect")
        if len(data['newPW']) < 8:
            return createRespons(406)
        response = db.updatePassword(token, data['newPW'])
        
        if response:
            return createRespons(200)
    else:
        return createRespons(400)
    return createRespons(300)

        
@app.route("/user/get_user_data_by_email/<email>", methods=['GET'])
def get_user_data_by_email(email):
   # data = request.get_json()
    token = request.headers.get('Authorization')
    if email is None or token is None:
        return createRespons(400, jsonify('No email or/and token entered'))
    if isLoggedIn(token) == False:
        return createRespons(401)
    user_data = db.getUserData(email=email)
    if not user_data:
        return createRespons(404)
    return createRespons(200, jsonify(user_data))

@app.route("/user/get_user_data_by_token", methods=['GET'])
def get_user_data_by_token():
    token = request.headers.get('Authorization') #Antar att man ska skicka token i header? 
    if not token:
        return createRespons(400, jsonify('No token entered'))
    if not isLoggedIn(token):
        return createRespons(401)
    user_data = db.getUserData(token=token)
    if not user_data:
        return createRespons(404)
    return createRespons(200, jsonify(user_data))
    
@app.route("/user/post_message", methods=['PUT'])
def post_message(): #Lämna epost tom om vi postar på egen vägg
    data = request.get_json()
    token = request.headers.get('Authorization')
    if 'message' not in data or 'to_email' not in data or not token:
        return createRespons(400)
    if isLoggedIn(token) and db.findUser(data['to_email']):
        response = db.postMessage(token, data['message'],data['to_email'])
        if response:
            return createRespons(200)
        else:
            return createRespons(402)
    else:
        return createRespons(401)
    
@app.route("/user/get_messages_by_email/<email>", methods=['GET'])
def get_messages_by_email(email):
    token = request.headers.get('Authorization')
    if email is None:
        return createRespons(400)
    if isLoggedIn(token):
        messages = db.getMessages(email)
        if messages:
            return createRespons(200, jsonify(messages))
        else:
            return createRespons(404)
    else:
        return createRespons(401)

@app.route("/user/get_messages_by_token", methods=['GET'])
def get_messages_by_token():
    token = request.headers.get('Authorization')
    if token is None:
        return createRespons(400)
    if isLoggedIn(token): 
        email = tokenToEmail(token)
        messages = db.getMessages(email)
        if messages == False:
            return createRespons(400)
        else:
            return createRespons(200, jsonify(messages))
            
    
if __name__ == "__main__":
    app.debug = True
    app.run()


