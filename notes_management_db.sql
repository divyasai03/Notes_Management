create database notes_management;
use notes_management;
CREATE TABLE user_data(
    username VARCHAR(30) PRIMARY KEY,
    password VARCHAR(300) NOT NULL,
    profile_name VARCHAR(30) UNIQUE NOT NULL
);

CREATE TABLE notes(
    sl_no INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(30) NOT NULL,
    title VARCHAR(30) NOT NULL,
    notes LONGTEXT,

    FOREIGN KEY(username)
    REFERENCES user_data(username)
);
SELECT * from user_data;
SELECT * from notes;