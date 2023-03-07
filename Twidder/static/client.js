let display_user = "";
let socket;

displayView = function(view){
    notification("",true);
    if(view == 0)
        document.getElementById("content").innerHTML = document.getElementById("welcomeview").innerHTML;
    else if(view == 1)
    {
        document.getElementById("content").innerHTML = document.getElementById("profileview").innerHTML;
        let curr_tab = localStorage.getItem("current_tab");
        if(curr_tab == null)
            changeTab('hometab');
        else
            changeTab(curr_tab);        
        getPersonalInfo();
        getMessages();
    }
    else if(view == 2)
    {
        document.getElementById("content").innerHTML = document.getElementById("resetpwview").innerHTML;
    }
        
    //Kod för att visa olika views
};

window.onload = function(){
    if(localStorage.getItem("token") != null)
    {
        establish_websocket();      //If we have token, connect websocket to see if sesion is valid
        displayView(1);
    }
        
    else
        displayView(0);
    //Kod som körs när en visst view visas

    
};

function validate_signup_input(formElement)
{

    let pw = formElement.signupPassword.value;
    let reppw = formElement.signupRepeatpassword.value;

    if(pw.length < 8)
    {
        notification("Password must be atleast 8 characters", true);
        return;
    }
    else if(pw != reppw)
    {
        notification("Passwords do not match", true);
        return;
    }

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if(this.readyState == 4)
        {
            if(this.status == 201)
            {
                notification("Signed upp successfully!", false);
            }
            else
            {
                notification("Server responded with status code: " + this.status, true);        
            }
        }
 
    };

    let dataobject = 
    {'email': formElement.signupEmail.value,
    'password': pw,
    'firstname': formElement.signupName.value,
    'familyname': formElement.signupSurname.value,
    'gender': document.getElementById("signup-gender").value,
    'city': formElement.signupCity.value,
    'country': formElement.signupCountry.value,
    }

    xhttp.open("POST", "http://127.0.0.1:5000/user/sign_up", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    let payload = JSON.stringify(dataobject);
    xhttp.send(payload);
    
}

let timeout;

function notification(message, is_error){
    if(is_error)
        document.getElementById("notification-box").style.color = "red";
    else
        document.getElementById("notification-box").style.color = "green";

    document.getElementById("notification-box").style.visibility = "visible";
    document.getElementById("notification-box").innerHTML = message;
    //Clear previous timeout if still pending
    clearTimeout(timeout);

    //Set notification do disappear after 5 seconds
    timeout = setTimeout(() => {
        document.getElementById("notification-box").style.visibility = "hidden";
    }, 5000);
}

function validate_login(formElement){
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if(this.readyState == 4)
        {
            if(this.status == 200)
            {
                localStorage.setItem("token", JSON.parse(xhttp.responseText).token);
                localStorage.setItem("email", formElement.loginEmail.value);
                establish_websocket();
                displayView(1);
            }
            else
            {
                notification("Server responded with status code: " + this.status, true);        
            }
        }
 
    };
    
    xhttp.open("POST", "http://127.0.0.1:5000/user/sign_in", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    let payload = {"email": formElement.loginEmail.value, "password": formElement.loginPassword.value };
    xhttp.send(JSON.stringify(payload));
    
}

function changeTab(tab_id){
    document.getElementById("hometab").style.display = "none";
    document.getElementById("browsetab").style.display = "none";
    document.getElementById("accounttab").style.display = "none";
    document.getElementById("notification-box").style.visibility = "hidden";
    document.getElementById(tab_id).style.display = "block";

    let buttons = document.getElementsByClassName("panel-choice");
    console.log(buttons);
    for(let x = 0; x < buttons.length; x++)
    {
        buttons[x].style.color = "white";
    }
    document.getElementById(tab_id+"-button").style.color = "orange";
    localStorage.setItem("current_tab", tab_id);                                        
}

function change_password(formElement){
    let newpw = formElement.changePasswordNew.value;
    let reppw = formElement.changePasswordRepeat.value;
    let oldpw = formElement.changePasswordOld.value;
    
    if(newpw.length < 8)
    {
        notification("Password must be atleast 8 characters", true);
        return;
    }
    else if(newpw != reppw)
    {
        notification("Passwords do not match", true);
        return;
    }

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if(this.readyState == 4)
        {
            if(this.status == 200)
            {
                notification("Password Changed Succesfully", false)
            }
            else
            {
                notification("Server responded with status code: " + this.status, true);        
            }
        }
    };

    xhttp.open("PUT", "http://127.0.0.1:5000/user/change_pw", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.setRequestHeader("Authorization", localStorage.getItem("token"));

    let payload = {"oldPW": oldpw, "newPW": newpw };
    xhttp.send(JSON.stringify(payload));
}

function logout(){
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if(this.readyState == 4)
        {
            if(this.status == 200)
            {
                socket.close()
                localStorage.removeItem("token");
                localStorage.removeItem("current_tab");
                localStorage.removeItem("email");
                displayView(0);
            }
            else
            {
                notification("Server responded with status code: " + this.status, true);        
            }
        }
    };

    xhttp.open("DELETE", "http://127.0.0.1:5000/user/sign_out", true);
    xhttp.setRequestHeader("Authorization", localStorage.getItem("token"));
    xhttp.send();
    
}

function getPersonalInfo(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if(this.readyState == 4)
        {
            if(this.status == 200)
            {
                let targetContainer = document.getElementById("personal-info-container");
                data = JSON.parse(xhttp.responseText);
                console.log(data)
                for(key in data)
                {
                    targetContainer.innerHTML += "<div><b>" +key[0].toUpperCase()+key.substring(1) + ": </b>"+ data[key]+ "<br></div>";
                }
            }
            else
            {
                notification("Server responded with status code: " + this.status, true);        
            }
        }
    };
    xhttp.open("GET", "http://127.0.0.1:5000/user/get_user_data_by_token", true);
    xhttp.setRequestHeader("Authorization", localStorage.getItem("token"));
    xhttp.send();
}

function postMessage(){
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if(this.readyState == 4)
        {
            if(this.status == 201)
            {
                notification("Message posted", false)
                document.getElementById(curr_tab+"-message").value = '';
            }
            else
            {
                notification("Server responded with status code: " + this.status, true);        
            }
        }
    };
    xhttp.open("POST", "http://127.0.0.1:5000/user/post_message", true);
    xhttp.setRequestHeader("Authorization", localStorage.getItem("token"));
    xhttp.setRequestHeader("Content-type", "application/json");
    let curr_tab = localStorage.getItem("current_tab");
    let msg = document.getElementById(curr_tab+"-message").value;
    
    let to_email = (curr_tab == "hometab" ? localStorage.getItem("email") : document.getElementById("search-email").value)
    let payload = {"to_email": to_email, "message": msg};
    xhttp.send(JSON.stringify(payload));
    
   // let response = serverstub.postMessage(localStorage.getItem("token"), msg, (curr_tab == "hometab" ? null : document.getElementById("search-email").value));
    
   // notification(response.message, !response.success);
    //document.getElementById(curr_tab+"-message").value = '';
}

function getMessages(){
    let curr_tab = localStorage.getItem("current_tab");
    if((curr_tab == "browsetab" && display_user == "") || curr_tab =="accounttab")
        return;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if(this.readyState == 4)
        {
            if(this.status == 200)
            {
                let count = 1;
                document.getElementById(curr_tab+"-message-wall").innerHTML = "";
                let data = JSON.parse(xhttp.responseText);
                
                for(key in data)
                {
                    
                    document.getElementById(curr_tab+"-message-wall").innerHTML += 
                    "<div class='message-container' id='"+toString(key)+"'"+"draggable='true' ondragstart='drag(event)'>"
                        +"<div class='message-author'>"+
                            "<b>"+ data[key].fromEmail  + ":"+"</b>"+
                        "</div>" +
                        "<div class='message-content'>" +
                            data[key].msg
                        + "</div>"
                    +"</div>";
                    
                }
            }
            else
            {
                notification("Server responded with status code: " + this.status, true);        
            }
        }
    };
    (
    curr_tab == "hometab" ? 
    xhttp.open("GET", "http://127.0.0.1:5000/user/get_messages_by_token", true) :
    xhttp.open("GET", "http://127.0.0.1:5000/user/get_messages_by_email/"+display_user)
    )
    xhttp.setRequestHeader("Authorization", localStorage.getItem("token"));
    xhttp.send();

}

function searchUser(){

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if(this.readyState == 4)
        {
            if(this.status == 200)
            {
                data = JSON.parse(xhttp.responseText)
                document.getElementById("user-message-wall").style.display="block";
                document.getElementById("browsetab-message-wall").style.display="block";
                document.getElementById("user-wall-name").innerHTML = data["firstname"] + "'s Message Wall";
                display_user = data["email"];
                let targetContainer = document.getElementById("user-info-container");
                document.getElementById("user-info-container").style.display="flex";
                targetContainer.innerHTML = "";
                targetContainer.innerHTML += "<h4>USER INFORMATION</h4>";
                getMessages()
                for(key in data)
                {
                    targetContainer.innerHTML += "<div class='info-attribute'><b>" +key[0].toUpperCase()+key.substring(1) + ": </b>"+ data[key]+ "<br></div>";
                }
            }
            else
            {
                notification("Server responded with status code: " + this.status, true);        
            }
        }
    };
   
    xhttp.open("GET", "http://127.0.0.1:5000/user/get_user_data_by_email/"+document.getElementById("search-email").value, true) 
    xhttp.setRequestHeader("Authorization", localStorage.getItem("token"));
    xhttp.send();
}

function establish_websocket(){
    socket = new WebSocket("ws://127.0.0.1:5000/ws");

    socket.onopen = function(e) {

        let payload = {"token": localStorage.getItem("token")};
        socket.send(JSON.stringify(payload));
    };
  
    socket.onmessage = function(event){
   
        if(event.data == "terminated"){
            localStorage.removeItem("token");
            localStorage.removeItem("email");
            localStorage.removeItem("current_tab");
            displayView(0);
        } 
    };
  
    socket.onclose = function(event) {
        if (event.wasClean) {
        
            if(event.reason == "Invalid token")
            {
                localStorage.removeItem("token");
                localStorage.removeItem("email");
                localStorage.removeItem("current_tab");
                displayView(0);
            }
            
        } else {
        // e.g. server process killed or network down
        // event.code is usually 1006 in this case
        }
    };
  
    socket.onerror = function(error) {
       
    };

}


function reset_password(formElement){
    let email = formElement.reset_email.value;
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if(this.readyState == 4)
        {
            if(this.status == 200)
            {
                notification("A new password has been sent to you")
            }
            else
            {
                notification("Server responded with status code: " + this.status, true);        
            }
        }
    };
    xhttp.open("POST", "http://127.0.0.1:5000/reset_password", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    let payload = {"email": email};
    xhttp.send(JSON.stringify(payload));
}

function allowDrop(ev) {
    ev.preventDefault();
  }
  
function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.children[1].innerHTML);
    //alert(ev.target.children[1].innerHTML);
}
  
function drop(ev) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text");
 
    ev.target.value = data;
  }
