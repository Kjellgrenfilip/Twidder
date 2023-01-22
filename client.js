displayView = function(view){
    if(view == 0)
        document.getElementById("content").innerHTML = document.getElementById("welcomeview").innerHTML;
    else if(view == 1)
    {
        document.getElementById("content").innerHTML = document.getElementById("profileview").innerHTML;
        getPersonalInfo();
        getMessages();
    }
        
    //Kod för att visa olika views
};

window.onload = function(){
    if(localStorage.getItem("token") != null)
        displayView(1);
    else
        displayView(0);
    //Kod som körs när en visst view visas

    
};

function validate_signup_input()
{
    event.preventDefault();
    let pw = document.getElementById("signup-password").value;
    let reppw = document.getElementById("signup-repeatpassword").value;

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

    let dataobject = 
    {'email': document.getElementById("signup-email").value,
    'password': document.getElementById("signup-password").value,
    'firstname': document.getElementById("signup-name").value,
    'familyname': document.getElementById("signup-surname").value,
    'gender': document.getElementById("signup-gender").value,
    'city': document.getElementById("signup-city").value,
    'country': document.getElementById("signup-country").value,
    }

    let response = serverstub.signUp(dataobject);
    if(response.success)
        notification("Signup successful", false);
    else
        notification(response.message, true);

}

function notification(message, is_error){
    if(is_error)
        document.getElementById("notification-box").style.color = "red";
    else
        document.getElementById("notification-box").style.color = "green";

    
        document.getElementById("notification-box").innerHTML = message;
}

function validate_login(){
    event.preventDefault();

    let response = serverstub.signIn(document.getElementById("login-email").value, document.getElementById("login-password").value);
    if(response.success)
    {
        localStorage.setItem("token", response.data);
        displayView(1);
    }
       
    else
        notification(response.message, true);

    return false;
}

function changeTab(tab_id, button){
    document.getElementById("hometab").style.display = "none";
    document.getElementById("browsetab").style.display = "none";
    document.getElementById("accounttab").style.display = "none";
    notification("", false);
    document.getElementById(tab_id).style.display = "block";

    let buttons = document.getElementsByClassName("panel-choice");
    console.log(buttons);
    for(let x = 0; x < buttons.length; x++)
    {
        buttons[x].style.color = "white";
    }
    
    button.style.color = "orange";
    
}

function change_password(){
    event.preventDefault();
    let newpw = document.getElementById("account-newpassword").value;
    let reppw = document.getElementById("account-repeatpassword").value;
    let oldpw = document.getElementById("account-oldpassword").value;
    
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


    let response = serverstub.changePassword(localStorage.getItem("token"), oldpw, newpw);
    notification(response.message, !response.success);

}

function logout(){
    localStorage.removeItem("token");
    displayView(0);
}

function getPersonalInfo(){
    let response = serverstub.getUserDataByToken(localStorage.getItem("token"));
    if(!response.success)
        notification(response.message, true);
    console.log(response.data);

    let targetContainer = document.getElementById("personal-info-container");

    for(key in response.data)
    {
        targetContainer.innerHTML += "<b>" +key + ": </b>"+ response.data[key]+ "<br>";
    }
    

}

function postMessage(){
    
    let msg = document.getElementById("textarea-message").value;
    let response = serverstub.postMessage(localStorage.getItem("token"), msg, null);
    
    notification(response.message, !response.success);
    
}

function getMessages(){
    document.getElementById("message-wall-container").innerHTML = "";
    let response = serverstub.getUserMessagesByToken(localStorage.getItem("token"));

    console.log(response.data);


    for(let i = 0; i < response.data.length; i++)
    {
        document.getElementById("message-wall-container").innerHTML += "<div class='message-container'><div class='message-author'>"+
        response.data[i].writer  +
        "</div><div class='message-content'>" +
        response.data[i].content
        + "</div></div>";
    }
}

function searchUser(){
    event.preventDefault();
    let info = serverstub.getUserDataByEmail(localStorage.getItem("token"), document.getElementById("search-email").value);
    if(!info.success)
    {
        notification(info.message, true);
        return;
    }   
    let messages = serverstub.getUserMessagesByEmail(localStorage.getItem("token"), document.getElementById("search-email").value);
    
}