# Progile Pages - Final Project - Part 1
#### David Corzo 20190432, Ian Jenatz 20190014, Anesveth Maatens 20190339

<br>

## Description
This project contains simple profile pages for users. Each user can fill out a 'form' with their details to fill out a profile page, which is stored in a database. After creating their profile, it is displayed and the user has an option to review and edit their information or search for the name of another user in a search engine. If the user exists, the user's profile page is loaded where you can review the information for this person. 

<br>

## How to run
Running this project is very simple, all you need to do is run `docker-compose up` in a terminal to bring up the frontend, backend, and mongo database simultaneously. 

1. Run `docker-compose up`
2. Access the frontend at: `http://127.0.0.1:8080/`

The frontend utilizes port 8080. The backend utilizes port 5000. Mongodb utilizes port 27017. 

All files relating to the frontend can be found in ./frontend, this includes the html templates and its static dependencies such as CSS and Javascript files, the python and requirements files, and the Dockerfile that docker-compose.yml.

All files relating to the backend can be found in ./backend, this includes the python and requirements files, and the Dockerfile that docker-compose.yml.