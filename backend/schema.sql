CREATE table IF NOT EXISTS Users(email varchar(30), pwd varchar(20), firstname varchar(20), familyname varchar(20),
gender varchar(6), city varchar(20), country varchar(20), primary key(email));

INSERT into Users (email, pwd, firstname, familyname, gender, city, country) VALUES('kalle@123.se', '123', 'kalle', 'johnny', 'male', 'gnbe', 'sweden');