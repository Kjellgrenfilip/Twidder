from flask import Flask, request, json, jsonify, make_response
import random
import database_handler as db
from flask_sock import Sock
import ssl, smtplib
import requests
from email.message import EmailMessage
app = Flask(__name__)
sockets = Sock(app)

connections = {}

email_sender =  "twidder.noreply1@gmail.com"
email_pw = "rtrxhfkprwqxklsw"


@sockets.route('/ws')
def echo_socket(ws):
    print("New websocket connection")
    while True:
        message = ws.receive()
        data = json.loads(message)
        if "token" in data:
            token = data["token"]
            print("Websocket provided token: " + token)
            if not isLoggedIn(token):                   #Om webbläsaren har gammal token och försöker visa sidan
                print("User is not logged in!")
                ws.send("terminated")
                ws.close()
                break
            email = tokenToEmail(token)
            print("     This token has email: "+email)
            if(email in connections):
                print(connections[email]['token'])
                if token != connections[email]['token']:
                    print("     Found another token for this user: ")
                    db.signOutUser(connections[email]['token'])
                    try:
                        connections[email]['socket'].send("terminated")  #Wrap in try block incase browser has been closed
                        connections[email]['socket'].close()
                    except Exception as e:
                        print(e)
                    print("     This token has now been invalidated")
                    connections.pop(email)
            connections[email] = {'socket':ws,'token':token}       #Decided to save socket and token because of current signout logic
        

@app.teardown_request
def teardown(e):
    db.disconnect()

@app.route("/", methods=["GET"])
def root():
    return app.send_static_file("client.html"), 200

 #---------------HJÄLPFUNKTIONER------------------#
def createUserToken(email):
    chars = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    token = ""
    for i in range(len(chars)):
        token += chars[random.randint(0, len(chars)-1)]
    return token

def generatePassword():
    chars = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    new_pw = ""
    for i in range(10):
        new_pw += chars[random.randint(0, len(chars)-1)]
    return new_pw


def createRespons(s_code,data=None): #Kan lägga till fler medlemmar sen som authorization och sånt
    if(data == None):
        return make_response('', s_code)
    else:
        return make_response(data, s_code)
    
def isLoggedIn(token):
    user = db.getLoggedInUser(token)

    if user != False and user != None:
        return True
    return user

def validateUserInput(data):
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

def validateEmail(email):
    at = email.find('@')
    if at == -1 or at == 0:
        return False
    dot = email.find('.', at)
    if dot == -1:
        return False
    if (dot - at) == 1:
        return False
    if dot == (len(email) - 1):
        return False
    return True

def getPassword(token):
    return db.getPassword(token)

def emailToPassword(email):
    resp = db.findUser(email)
    if resp == False or resp == None:
       return resp
    return resp['password']

def tokenToEmail(token):
    resp = db.getLoggedInUser(token)
    if resp == False or resp == None:
       return resp
    return resp['email']

def userExists(email):
    resp = db.findUser(email)
    if resp == False or resp == None:
        return resp
    return True

def sendNewPassword(rec_email, pw):
    subject = "Twidder Password Reset"
    body = """
        Below is your new password for Twidder
        We STRONGLY recommend you to change it when logged in.

 
        """
    body += pw

    em = EmailMessage()
    em['from'] = email_sender
    em['to'] = rec_email
    em['subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_pw)
        smtp.sendmail(email_sender, rec_email, em.as_string())

def getLocation(pos):
    url = "https://geocode.xyz/"+pos+"?json=1&auth=433505021179596109422x95061"
    resp = requests.get(url)
    city = json.loads(resp.text)['city']
    return city


#------------REQUESTS------------------
@app.route("/user/sign_in", methods=["POST"])
def sign_in():
    data = request.get_json()
    if 'email' not in data or 'password' not in data:
        return createRespons(400, "Hej")
    else:
        stored_password = emailToPassword(data['email'])
        user_exists = userExists(data['email'])
        if stored_password == False or user_exists == False:
            return createRespons(500)
        if stored_password == None or user_exists == None:
            return createRespons(404)
        if (data['password'] == stored_password): #Kolla så lösenord matchar det i databasen
            token = createUserToken(data['email']) #Lyckad inloggning, skapar en token som ska returneras
            db.signInUser(data['email'], token)
            return createRespons(200, jsonify(token=token))

        return createRespons(401)  #Användaren har angett fel lösenord alternativt finns ej registrerad, kanske 404
        
@app.route("/user/sign_up", methods=["POST"])
def sign_up():
    data = request.get_json()
    #Extremt ful if-sats  Kolla om all krävd data är given
    if 'email' in data and 'password' in data and 'firstname' in data and 'familyname' in data and 'gender' in data and 'country' in data and 'city' in data:
        if validateUserInput(data):
            if not userExists(data['email']):
                user = db.createUser(data['email'], data['password'],data['firstname'], data['familyname'],data['gender'],data['country'], data['city'])
                if user:
                    return createRespons(201)  #201 = Created
                else:
                    return createRespons(500)  #500 - internal server error: Av någon anledning kunde användare inte skapas
            else:
                return createRespons(409) #User already exists - 409 = Conflict with current resources?
        
    return createRespons(400) #400- Bad Request: Datan som angivits uppfyller inte alla krav alterativt har inte all data angivits


@app.route("/user/sign_out", methods=["DELETE"])
def sign_out():
    if 'Authorization' in request.headers:
        token = request.headers.get('Authorization')
        if token is not None:
            logged_in = isLoggedIn(token)
            if logged_in == False:
                return createRespons(500)
            if logged_in == None:
                return createRespons(401)
            if db.signOutUser(token):
                return createRespons(200)
            else:
                return createRespons(500)   #Felaktig token - Unauthorized
            
    return createRespons(400) #Bad Request - No Token Provided in the header  

@app.route("/user/change_pw", methods=['PUT'])
def change_password(): #Får in Token i header, gamla + nya lösenordet i bodyn? 
    if 'Authorization' not in request.headers:
        return createRespons(400)
    token = request.headers['Authorization']
    logged_in = isLoggedIn(token)
    if logged_in == False:
        return createRespons(500)
    if logged_in == None:
        return createRespons(401)
    data = request.get_json()
    if 'oldPW' in data and 'newPW' in data and len(data['newPW']) >= 8:
        if data['oldPW'] != getPassword(token):
            return createRespons(403) #403 Forbidden: We are logged in and authenticated, but provide wrong information about ourselves
        response = db.updatePassword(tokenToEmail(token), data['newPW'])
        if response:
            return createRespons(200)
        else:
            return createRespons(500) #500- Internal Server Error.

    return createRespons(400) # 400 oldPW eller newPW finns inte med i payload eller så är lösenordet för kort

@app.route("/user/get_user_data_by_token", methods=['GET'])
def get_user_data_by_token():
    if 'Authorization' in request.headers:
        token = request.headers.get('Authorization')
        logged_in = isLoggedIn(token)
        if logged_in == False:
            return createRespons(500)
        if logged_in == None:
            return createRespons(401)
        user_data = db.getUserData(tokenToEmail(token))
        if not user_data:
            return createRespons(500)
        return createRespons(200, jsonify(user_data)) 
    return createRespons(400) #Bad request
        
@app.route("/user/get_user_data_by_email/<email>", methods=['GET'])
def get_user_data_by_email(email):
    if 'Authorization' in request.headers:
        token = request.headers.get('Authorization')
        if email is None:
            return createRespons(400)
        logged_in = isLoggedIn(token)
        if logged_in == False:
            return createRespons(500)
        if logged_in == None:
            return createRespons(401)
        user_data = db.getUserData(email)
        if user_data == False:
            return createRespons(500)
        if user_data == None:
            return createRespons(404)
        return createRespons(200, jsonify(user_data))
    return createRespons(400)

@app.route("/user/get_messages_by_token", methods=['GET'])
def get_messages_by_token():
    if 'Authorization' not in request.headers:
        return createRespons(400)
    token = request.headers.get('Authorization')

    logged_in = isLoggedIn(token)
    if logged_in == False:
        return createRespons(500)
    if logged_in == None:
        return createRespons(401)
    messages = db.getMessages(tokenToEmail(token))
    if messages == False:
        return createRespons(500) #Internal server error
    else:
        return createRespons(200, jsonify(messages))
    return createRespons(401)
    
@app.route("/user/get_messages_by_email/<email>", methods=['GET'])
def get_messages_by_email(email):
    if 'Authorization' not in request.headers:
        return createRespons(400)
    token = request.headers.get('Authorization')
    if email is None:
        return createRespons(400)
    if userExists(email) == None:
        return createRespons(404)

    logged_in = isLoggedIn(token)
    if logged_in == False:
        return createRespons(500)
    if logged_in == None:
        return createRespons(401)
    messages = db.getMessages(email)
    if messages == False:
        return createRespons(500) #INTERNAL server error, nånting går fel på Databassidan
    else:
        return createRespons(200, jsonify(messages))
   

@app.route("/user/post_message", methods=['POST'])
def post_message(): #Lämna epost tom om vi postar på egen vägg
    data = request.get_json()
    if 'message' not in data or 'to_email' not in data or 'Authorization' not in request.headers:
        return createRespons(400)   #400 - alla fält finns inte i payload
    token = request.headers.get('Authorization')
    logged_in = isLoggedIn(token)
    if logged_in == False:
        return createRespons(500)
    if logged_in == None:
        return createRespons(401)
    
    if userExists(data["to_email"]) == None:
        return createRespons(404)
    if 'position' not in data:
        response = db.postMessage(tokenToEmail(token), data['message'],data['to_email'], pos=None)
    else:
        location = None
        if data['position'] != None:
            location = getLocation(data['position'])
        response = db.postMessage(tokenToEmail(token), data['message'],data['to_email'], pos=location)
    if response:
        return createRespons(201)
    else:
        return createRespons(500)
    return createRespons(400) #Bad request. Svårt att säga vilken felkod
            
@app.route("/reset_password", methods=['POST'])
def reset_pw():
    data = request.get_json()
    if 'email' not in data:
        return createRespons(400)
    email = data['email']
    if validateEmail(email):
        if not userExists(email):
            return createRespons(404)
        new_pw = generatePassword()
        response = db.updatePassword(email, new_pw)
        if response:
            sendNewPassword(email, new_pw)
            return createRespons(200)
        else:
            return createRespons(500) #500- Internal Server Error.
    else:   
        createRespons(400)




if __name__ == "__main__":
    app.debug = True
    app.run()


