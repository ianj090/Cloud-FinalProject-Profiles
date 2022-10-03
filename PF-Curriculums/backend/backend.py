from flask import Flask, redirect, g, request, flash, render_template
from peewee import * # ORM for Sqlite
from hashlib import md5 # Encoder for password
# import os # random string method
import random

from psutil import users

# Set workspace values / app config
DATABASE = 'profiles.db' # Database name for sqlite3
DEBUG = True # debug flag to print error information

app = Flask(__name__)
app.config.from_object(__name__) # loads workspace values

# Sqlite connection (using peewee ORM from now on, not Sqlite directly)
# Peewee queries docs: https://docs.peewee-orm.com/en/latest/peewee/querying.html 
database = SqliteDatabase(DATABASE)

global session 
session = {'logged_in':False, 'username':''}

# Parent Class containing metadata (in case other classes are used)
class BaseModel(Model):
    class Meta:
        database = database

# Class for users with profiles, contains all values to be displayed
class User(BaseModel):
    username = CharField(unique=True) # primary key
    password = CharField() 
    profilepic = CharField()
    mood = CharField()
    description = CharField()
    email = CharField()
    firstName = CharField()
    lastName = CharField()
    country = CharField()
    birthday = CharField()
    occupation = CharField()
    relationship_status = CharField()
    mobile_number = CharField()
    phone_number = CharField()
    my_journal = CharField()
    bg = CharField()

# Creates table in database, ignored if it exists
def create_table():
    with database:
        database.create_tables([User])

# Set session variable, used to record which user is currently signed in
def auth_user(user):
    session['logged_in'] = True
    session['username'] = user.username

# gets the user from the current session
def get_current_user():
    if session['logged_in']:
        return User.get(User.username == session['username'])
    else:
        raise RuntimeError

def create_user(user):
    with database.atomic(): # Peewee best practice
        test = User.create(
            username = ''.join(random.sample(user['username'], len(user['username']))),
            password = md5((user['password']).encode('utf-8')).hexdigest(),
            profilepic = user['profilepic'],
            mood = user['mood'],
            description = user['description'],
            email = user['email'],
            firstName = user['firstName'],
            lastName = user['lastName'],
            country = user['country'],
            birthday = user['birthday'],
            occupation = user['occupation'],
            relationship_status = user['relationship_status'],
            mobile_number = user['mobile_number'],
            phone_number = user['phone_number'],
            my_journal = user['my_journal'],
            bg = user['bg']
        )

#### From route /
def reset_session():
    session['logged_in'] = False
    session['username'] = ''

# Open and close database connection with every request (peewee best practices)
@app.before_request
def before_request():
    g.db = database
    g.db.connect()

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route('/reset_session/')
def reset():
    reset_session()
    return 'SUCCESS'

# Redirects to '/login' path
@app.route('/login', methods=["POST"])
def login():
    reset_session()
    payload = request.json
    if payload["method"] == "POST":
        try:
            try:
                pw_hash = md5(payload["data"]['inputPassword'].encode('utf-8')).hexdigest()
                user = User.get(
                    (User.username == payload["data"]['inputUsername']) &
                    (User.password == pw_hash))
                auth_user(user)
                return 'PROFILE'
            except:
                try:
                    with database.atomic(): # Peewee best practice
                        # Create user with empty fields
                        user = User.create(
                            username = payload["data"]['inputUsername'],
                            password = md5((payload["data"]['inputPassword']).encode('utf-8')).hexdigest(),
                            profilepic = "https://d3ipks40p8ekbx.cloudfront.net/dam/jcr:3a4e5787-d665-4331-bfa2-76dd0c006c1b/user_icon.png",
                            mood = "Relaxed",
                            description = "",
                            email = "",
                            firstName = "",
                            lastName = "",
                            country = "",
                            birthday = "",
                            occupation = "",
                            relationship_status = "",
                            mobile_number = "",
                            phone_number = "",
                            my_journal = "",
                            bg = "#f1f2f7"
                        )
                    auth_user(user)
                    return 'PROFILE'
                except:
                    return 'TAKEN'
        except:
            return 'FAILURE'
    return 'LOGIN'

@app.route('/profile', methods=["POST"])
def homepage():
    payload = request.json
    print(payload)
    user = User.get(User.username == payload["data"]["searchUsername"])
    print(user)
    # Checks if user is the current session user
    if user.username == session['username']:
        current = True
    else:
        current = False
    user_dict = { 
        "username" : user.username,
        "profilepic" : user.profilepic,
        "mood" : user.mood,
        "description" : user.description,
        "email" : user.email,
        "firstName" : user.firstName,
        "lastName" : user.lastName,
        "country" : user.country,
        "birthday" : user.birthday,
        "occupation" : user.occupation,
        "relationship_status" : user.relationship_status,
        "mobile_number" : user.mobile_number,
        "phone_number" : user.phone_number,
        "my_journal" : user.my_journal,
        "bg" : user.bg,
        "current": current
    }
    print(user_dict)
    return user_dict

@app.route('/currentUser')
def currentUser():
    try:
        user = get_current_user()
        user_dict = { 
            "username" : user.username,
            "profilepic" : user.profilepic,
            "mood" : user.mood,
            "description" : user.description,
            "email" : user.email,
            "firstName" : user.firstName,
            "lastName" : user.lastName,
            "country" : user.country,
            "birthday" : user.birthday,
            "occupation" : user.occupation,
            "relationship_status" : user.relationship_status,
            "mobile_number" : user.mobile_number,
            "phone_number" : user.phone_number,
            "my_journal" : user.my_journal,
            "bg" : user.bg
        }
        return user_dict
    except:
        return 'FAILURE'

@app.route('/edit', methods=['POST'])
def edit():
    payload = request.json
    current_user = get_current_user()
    print(payload)
    if (payload["data"]['editProfilePic'] != ""):
        query = User.update(
            profilepic = payload["data"]['editProfilePic'],
            mood = payload["data"]['editMood'],
            email = payload["data"]['editEmail'],
            description = payload["data"]['editDescription'],
            firstName = payload["data"]['editFirstName'],
            lastName = payload["data"]['editLastName'],
            country = payload["data"]['editCountry'],
            birthday = payload["data"]['editBirthday'],
            occupation = payload["data"]['editOccupation'],
            relationship_status = payload["data"]['editRelationship_status'],
            mobile_number = payload["data"]['editMobileNumber'],
            phone_number = payload["data"]['editPhoneNumber'],
            my_journal = payload["data"]['editJournal']
        ).where(User.username == current_user.username).execute()
    else:
        query = User.update(
            mood = payload["data"]['editMood'],
            email = payload["data"]['editEmail'],
            description = payload["data"]['editDescription'],
            firstName = payload["data"]['editFirstName'],
            lastName = payload["data"]['editLastName'],
            country = payload["data"]['editCountry'],
            birthday = payload["data"]['editBirthday'],
            occupation = payload["data"]['editOccupation'],
            relationship_status = payload["data"]['editRelationship_status'],
            mobile_number = payload["data"]['editMobileNumber'],
            phone_number = payload["data"]['editPhoneNumber'],
            my_journal = payload["data"]['editJournal']
        ).where(User.username == current_user.username).execute() 
    return "SUCCESS"

@app.route('/editbg', methods=['POST'])
def editbg():
    payload = request.json
    current_user = get_current_user()
    query = User.update(
        bg = payload["data"]['editBgprofile'],
    ).where(User.username == current_user.username).execute()
    return "SUCCESS"
    

@app.route('/delete')
def delete():
    user = get_current_user()
    user.delete_instance()
    session['logged_in'] = False
    session['username'] = ''
    return 'SUCCESS'


if __name__ == '__main__':
    create_table() # Creates table in DB if it does not exist
    app.run()