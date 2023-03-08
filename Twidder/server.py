from flask import Flask, request, json, jsonify, make_response
import random
import database_handler as db
from flask_sock import Sock
import ssl, smtplib
import requests
from email.message import EmailMessage

app = Flask(__name__)
sockets = Sock(app)
#Connections stores emails with corresponding tokens and websocket
connections = {}
#email and application password. Used for sending reset emails.
email_sender =  "twidder.noreply1@gmail.com"
email_pw = "rtrxhfkprwqxklsw"



@sockets.route('/ws')
def echo_socket(ws):
    
    while True:
        message = ws.receive()
        data = json.loads(message)
        if "token" in data:
            token = data["token"]
            if not isLoggedIn(token):                  #If the website provides an old token, terminate the try to access
                ws.send("terminated")                  #Tells the websocket to close down. "Terminated" is just a keyword in our specific implementation
                ws.close()
                break
            email = tokenToEmail(token)
            if(email in connections):  #If the email already exists in an active session.
                if token != connections[email]['token']:    #Check so that the token is not the one from the same session that tries to establish connection
                    db.signOutUser(connections[email]['token']) #Signs out the other session
                    try:                                #Wrap in try block incase browser has been closed
                        connections[email]['socket'].send("terminated")  #Terminate the other session
                        connections[email]['socket'].close()
                    except Exception as e:
                        print(e)
                    connections.pop(email)  
            connections[email] = {'socket':ws,'token':token}       #Save socket and token because of signout logic
        

@app.teardown_request
def teardown(e):
    db.disconnect()

@app.route("/", methods=["GET"])
def root():
    return app.send_static_file("client.html"), 200

 #---------------HELPING FUNCTIONS------------------#
 #Self-describing. Creates a random token of numbers and letters.
def createUserToken(email): 
    chars = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    token = ""
    for i in range(len(chars)):
        token += chars[random.randint(0, len(chars)-1)]
    return token

#Used for reset_password function, creates a random password of length 10
def generatePassword(): 
    chars = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    new_pw = ""
    for i in range(10):
        new_pw += chars[random.randint(0, len(chars)-1)]
    return new_pw

#Creates a http response
def createRespons(s_code,data=None):
    if(data == None):
        return make_response('', s_code)
    else:
        return make_response(data, s_code)
#Checks if a user i logged in.
def isLoggedIn(token):
    user = db.getLoggedInUser(token)
    if user != False and user != None:
        return True
    return user
#Validates the user input for a sign up attempt
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
#Checks that @ exists, and that the remaining part qualifies as a domain.
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
#Converts token to password
def getPassword(token):
    return db.getPassword(token)
#Converts email to password
def emailToPassword(email):
    resp = db.findUser(email)
    if resp == False or resp == None:
       return resp
    return resp['password']
#Converts token to email
def tokenToEmail(token):
    resp = db.getLoggedInUser(token)
    if resp == False or resp == None:
       return resp
    return resp['email']
#Checks if a user exists based on email
def userExists(email):
    resp = db.findUser(email)
    if resp == False or resp == None:
        return resp
    return True
#Sends an email to the rec_email containing a new random password (called in reset_password function)
def sendNewPassword(rec_email, pw):
    subject = "Twidder Password Reset" #Sets the subject of the email to be sent
    
    #Creates the standard of the body part of the email, the main content.
    body = """  
        Below is your new password for Twidder
        We STRONGLY recommend you to change it when logged in.

 
        """
    body += pw #Concastinate the new random password to the body.

    em = EmailMessage() #Instantiating a new email-message  
    em['from'] = email_sender
    em['to'] = rec_email
    em['subject'] = subject
    em.set_content(body) 

    #Creates a ssl default context. Makes it possible for us to use SSL-transport
    #Context can be changed to different setting and protocols, but default is used for convenience.
    context = ssl.create_default_context()

    #Using the python module smtplib to send the email via our provider gmail
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_pw)
        smtp.sendmail(email_sender, rec_email, em.as_string())

#Used for gelocation. Sends a request to the geocode API, forwarding the provided coordinates (pos).
# 433505021179596109422x95061 is our API key
def getLocation(pos):
    url = "https://geocode.xyz/"+pos+"?json=1&auth=433505021179596109422x95061"
    resp = requests.get(url)
    #Response contains large amount of location data, we are only interesting in the city at the moment.
    city = json.loads(resp.text)['city']
    return city


#------------REQUESTS------------------
@app.route("/user/sign_in", methods=["POST"])
def sign_in():
    data = request.get_json()
    if 'email' not in data or 'password' not in data:
        return createRespons(400) #If no email or password was provided in the request body, response code 400-Bad request. 
    else:
        stored_password = emailToPassword(data['email'])
        user_exists = userExists(data['email'])
        if stored_password == False or user_exists == False:#A database failure will return False
            return createRespons(500)       #In case of a database failure, status code 500 -Internal Server Error
        if stored_password == None or user_exists == None: #If a requested data wasnt found in the database, the database will return None
            return createRespons(404)   #In case of data not found, 404- Resource not found
        if (data['password'] == stored_password): #Check if password matches the one in the database
            token = createUserToken(data['email']) #Succesfull login. Create a Token
            db.signInUser(data['email'], token) #Signs in the user to the database
            return createRespons(200, jsonify(token=token)) #Everything went well, 200-Ok and return the token

        return createRespons(401)  #User provided wrong password, 401- Unauthorized
        
@app.route("/user/sign_up", methods=["POST"])
def sign_up():
    data = request.get_json()
    #Checks if all data is provided in case of a sign-up attempt
    if 'email' in data and 'password' in data and 'firstname' in data and 'familyname' in data and 'gender' in data and 'country' in data and 'city' in data:
        if validateUserInput(data):
            if not userExists(data['email']):#If the user does not exists, create the user
                user = db.createUser(data['email'], data['password'],data['firstname'], data['familyname'],data['gender'],data['country'], data['city'])
                if user:
                    return createRespons(201)  #201 = Created
                else:
                    return createRespons(500)  #500 - internal server error: Database Failure
            else:
                return createRespons(409) #User already exists - 409 = Conflict with current resources
        
    return createRespons(400) #400- Bad Request: Correct data was not provided in request body or not valid information


@app.route("/user/sign_out", methods=["DELETE"])
def sign_out():
    if 'Authorization' in request.headers: #Check if token is provided in header
        token = request.headers.get('Authorization')
        if token is not None:
            logged_in = isLoggedIn(token)
            if logged_in == False:
                return createRespons(500) #Database Failure 500
            if logged_in == None: 
                return createRespons(401) #We are not signed in, cant sign out. 401
            if db.signOutUser(token):
                return createRespons(200) #Sign out successfull
            else:
                return createRespons(500)   #Database Failure 500
            
    return createRespons(400) #Bad Request - No Token Provided in the header  

@app.route("/user/change_pw", methods=['PUT'])
def change_password():
    if 'Authorization' not in request.headers:
        return createRespons(400) #No token provided, Bad Request
    token = request.headers['Authorization']
    logged_in = isLoggedIn(token)
    if logged_in == False:
        return createRespons(500) #Database Failure 500
    if logged_in == None:
        return createRespons(401) #Not logged in, cant change password. 401-Unauthorized
    data = request.get_json()
    if 'oldPW' in data and 'newPW' in data and len(data['newPW']) >= 8: #Checks if necessary data is provided in body, and new pw is > 8 chars.
        if data['oldPW'] != getPassword(token): 
            return createRespons(403) #403 Forbidden: We are logged in and authenticated, but provide wrong information about ourselves
        response = db.updatePassword(tokenToEmail(token), data['newPW']) #Updates the new password
        if response:
            return createRespons(200) #Password succesfully changed, 200 OK
        else:
            return createRespons(500) #500- Internal Server Error. Database Failure

    return createRespons(400) #Not correct data provided or password too short. Bad request

@app.route("/user/get_user_data_by_token", methods=['GET'])
def get_user_data_by_token():
    if 'Authorization' in request.headers:
        token = request.headers.get('Authorization')
        logged_in = isLoggedIn(token)
        if logged_in == False:
            return createRespons(500) #Database Failure
        if logged_in == None:
            return createRespons(401) #Unauthorized
        user_data = db.getUserData(tokenToEmail(token))
        if not user_data:
            return createRespons(500) #Database failure
        return createRespons(200, jsonify(user_data)) #200 OK - User data is returned
    return createRespons(400) #Bad request. no authorization header
        
@app.route("/user/get_user_data_by_email/<email>", methods=['GET'])
def get_user_data_by_email(email):
    if 'Authorization' in request.headers:
        token = request.headers.get('Authorization')
        if email is None:
            return createRespons(400) #Bad request - No email provided
        logged_in = isLoggedIn(token)
        if logged_in == False:
            return createRespons(500)   #Database failure - 500
        if logged_in == None:
            return createRespons(401)   #Not logged in - Unauthorized - 401
        user_data = db.getUserData(email)
        if user_data == False:
            return createRespons(500) #Database failure
        if user_data == None:
            return createRespons(404) #User could not be found, 404- Resource not found
        return createRespons(200, jsonify(user_data))   #All ok, 200, return the requested data
    return createRespons(400) #No token in header, 400 bad request

@app.route("/user/get_messages_by_token", methods=['GET'])
def get_messages_by_token():
    if 'Authorization' not in request.headers:
        return createRespons(400) #No token in header, 400 bad request
    token = request.headers.get('Authorization')

    logged_in = isLoggedIn(token)
    if logged_in == False:
        return createRespons(500) #Database failure
    if logged_in == None:
        return createRespons(401) #Not logged in - Unauthorized - 401
    messages = db.getMessages(tokenToEmail(token)) #Retrieve messages from database
    if messages == False:
        return createRespons(500) #Internal server error - Database failure
    else:
        return createRespons(200, jsonify(messages)) #MEssages found. 200 ok and returned to client
    return createRespons(401) #Unauthorized - 401 
    
@app.route("/user/get_messages_by_email/<email>", methods=['GET'])
def get_messages_by_email(email):
    if 'Authorization' not in request.headers:
        return createRespons(400) #No token in header, 400 bad request
    token = request.headers.get('Authorization')
    if email is None:
        return createRespons(400) #No email provided
    if userExists(email) == None:
        return createRespons(404) #USer does not exist in database, 404 - Resource not found

    logged_in = isLoggedIn(token)
    if logged_in == False:
        return createRespons(500) #Database failure - 500
    if logged_in == None:
        return createRespons(401)   #Unauthorized
    messages = db.getMessages(email) #Get messages from database
    if messages == False:
        return createRespons(500) #Database failure
    else:
        return createRespons(200, jsonify(messages)) #200 OK - return messages
   

@app.route("/user/post_message", methods=['POST'])
def post_message(): 
    data = request.get_json()
    if 'message' not in data or 'to_email' not in data or 'Authorization' not in request.headers:
        return createRespons(400)   #400 - bad request - not all required field are provided in request
    token = request.headers.get('Authorization')
    logged_in = isLoggedIn(token)
    if logged_in == False:
        return createRespons(500) #database failure
    if logged_in == None:
        return createRespons(401) #Unauthorized
    
    if userExists(data["to_email"]) == None:
        return createRespons(404) #USer does not exist - Resource not found
    if 'position' not in data: #If a position is not provided. The user denied to share his/her position, pos = None
        response = db.postMessage(tokenToEmail(token), data['message'],data['to_email'], pos=None)
    else:
        location = None
        if data['position'] != None: #If a location (coords) is provided in the request
            location = getLocation(data['position']) #Forward the request of coordinates -> location. 
        response = db.postMessage(tokenToEmail(token), data['message'],data['to_email'], pos=location) #pos = location. Adds the position to the message of where it was sent from
    if response:
        return createRespons(201) #Created - A message has been created and posted
    else:
        return createRespons(500) #Database failure
            
@app.route("/reset_password", methods=['POST']) #Maybe change this method put?
def reset_pw():
    data = request.get_json()
    if 'email' not in data:
        return createRespons(400) #Email not provided in request body - Bad request
    email = data['email']
    if validateEmail(email): #Checks is the email provided is valid
        if not userExists(email):
            return createRespons(404) #User connected to the email does not exist. 404 - Resource not found
        new_pw = generatePassword() #Generates a random pw
        response = db.updatePassword(email, new_pw) #Updates the db with the new random password.
        if response:
            sendNewPassword(email, new_pw) #If database change was successfull. Send an email to the user with his new password.
            return createRespons(200) #200 OK- Everything went well
        else:
            return createRespons(500) #500- Internal Server Error - database failrue.
    else:   
        createRespons(400)  #Email has wong format - bad request




if __name__ == "__main__":
    app.debug = True
    app.run()


