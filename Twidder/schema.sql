CREATE table IF NOT EXISTS Users(
    email varchar(30),
    pwd varchar(20),
    firstname varchar(20),
    familyname varchar(20),
    gender varchar(6),
    city varchar(20),
    country varchar(20),
    primary key(email));

CREATE TABLE loggedInUsers(
    email VARCHAR(30),
    token VARCHAR(30),
    PRIMARY KEY(token)
);

CREATE TABLE userMessages(
    id INTEGER primary key autoincrement,
    toEmail VARCHAR(30),
    fromEmail VARCHAR(30),
    msg VARCHAR(144),
    pos VARCHAR(100)
);


INSERT into Users (email, pwd, firstname, familyname, gender, city, country) VALUES('kalle@123.se', '12345678', 'kalle', 'johnny', 'male', 'gnbe', 'sweden');
