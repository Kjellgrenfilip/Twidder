let display_user = "";

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
    
    setTimeout(() => {
        document.getElementById("notification-box").innerHTML = "";
    }, 5000);
}

function validate_login(formElement){

    let response = serverstub.signIn(formElement.loginEmail.value, formElement.loginPassword.value);
    if(response.success)
    {
        localStorage.setItem("token", response.data);
        displayView(1);
    } 
    else
        notification(response.message, true);

    return false;
}

function changeTab(tab_id){
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


    let response = serverstub.changePassword(localStorage.getItem("token"), oldpw, newpw);
    notification(response.message, !response.success);

}

function logout(){
    localStorage.removeItem("token");
    localStorage.removeItem("current_tab");
    displayView(0);
}

function getPersonalInfo(){
    let response = serverstub.getUserDataByToken(localStorage.getItem("token"));
    if(!response.success)
        notification(response.message, true);

    let targetContainer = document.getElementById("personal-info-container");

    for(key in response.data)
    {
        targetContainer.innerHTML += "<b>" +key[0].toUpperCase()+key.substring(1) + ": </b>"+ response.data[key]+ "<br>";
    }
    

}

function postMessage(){
    let curr_tab = localStorage.getItem("current_tab");
    let msg = document.getElementById(curr_tab+"-message").value;
    let response = serverstub.postMessage(localStorage.getItem("token"), msg, (curr_tab == "hometab" ? null : document.getElementById("search-email").value));
    
    notification(response.message, !response.success);
    
}

function getMessages(){
    let curr_tab = localStorage.getItem("current_tab");
    if(curr_tab == "browsetab" && display_user == "")
        return;
    document.getElementById(curr_tab+"-message-wall").innerHTML = "";
    

    let response = ( curr_tab == "hometab" ? 
    serverstub.getUserMessagesByToken(localStorage.getItem("token")) : 
    serverstub.getUserMessagesByEmail(localStorage.getItem("token"), display_user));
    


    for(let i = 0; i < response.data.length; i++)
    {
        document.getElementById(curr_tab+"-message-wall").innerHTML += "<div class='message-container'><div class='message-author'>"+
       "<b>"+ response.data[i].writer  + ":"+"</b>"+
        "</div><div class='message-content'>" +
        response.data[i].content
        + "</div></div>";
    }
}

function searchUser(){
   //event.preventDefault();
    let info = serverstub.getUserDataByEmail(localStorage.getItem("token"), document.getElementById("search-email").value);
    if(!info.success)
    {
        notification(info.message, true);
        return;
    }   
    //Activate the post-message textarea and showcase the message-wall when a user is found.
    document.getElementById("user-message-wall").style.display="block";
    document.getElementById("browsetab-message-wall").style.display="block";
    display_user = info.data.email;
    
    let targetContainer = document.getElementById("user-info-container");
    targetContainer.innerHTML = "";
    targetContainer.innerHTML += "<h3><u>USER INFORMATION</u></h3>";

    for(key in info.data)
    {
        targetContainer.innerHTML += "<b>" +key[0].toUpperCase()+key.substring(1) + ": </b>"+ info.data[key]+ "<br>";
    }

    document.getElementById("browsetab-message-wall").innerHTML = "";
    let messages = serverstub.getUserMessagesByEmail(localStorage.getItem("token"), document.getElementById("search-email").value);
    
    for(let i = 0; i < messages.data.length; i++)
    {
        document.getElementById("browsetab-message-wall").innerHTML += "<div class='message-container'><div class='message-author'>"+
        "<b>"+ messages.data[i].writer  + ":</b>"+
        "</div><div class='message-content'>" +
        messages.data[i].content
        + "</div></div>";
    }
}