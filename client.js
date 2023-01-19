displayView = function(view){
    if(view == 0)
        document.getElementById("content").innerHTML = document.getElementById("welcomeview").innerHTML;
    else if(view == 1)
        document.getElementById("content").innerHTML = document.getElementById("profileview").innerHTML;
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
    let reppw = document.getElementById("signup-password").value;

    if(pw >= 8 && pw == reppw)
    {
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
    else
        notification("Validation failed", true);
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