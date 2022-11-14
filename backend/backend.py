from flask import Flask, request
from flask_cors import CORS, cross_origin
import pymongo # Mongo DB client
from hashlib import md5 # Encoder for password

# Set workspace values / app config
DEBUG = True # debug flag to print error information

app = Flask(__name__)
app.config.from_object(__name__) # loads workspace values

# Connects to MongoDB, creates database 'flask_db' and collection 'users'
client = pymongo.MongoClient("mongodb://username:password@cloud-profiles.cluster-cgeqr5welkvw.us-east-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false")
db = client.flask_db
users = db.users

# Global variable to keep logged in user information
global session
session = {'logged_in':False, 'username':''}

# Set session variable, used to record which user is currently signed in
def auth_user(user):
    session['logged_in'] = True
    session['username'] = user["username"]

# gets the user from the current session
def get_current_user():
    if session['logged_in']:
        return users.find_one({'username': session['username']})
    else:
        raise RuntimeError

# Resets session variable (for logout)
def reset_session():
    session['logged_in'] = False
    session['username'] = ''

# Handles Frontend GET or POST login
@app.route('/login', methods=["POST"])
def login():
    reset_session() # Login screen always resets session (assumes logout)
    payload = request.json
    # Checks if a POST request was made to Frontend Login, if not then it skips (this route handles both GET and POST for Frontend)
    if payload["method"] == "POST":
        try:
            # Checks if user exists and if password is correct
            try:
                pw_hash = md5(payload["data"]['inputPassword'].encode('utf-8')).hexdigest()
                user = users.find_one({'username': payload["data"]['inputUsername'], 'password': pw_hash})
                auth_user(user)
                return 'PROFILE'
            except:
                # Tries to add user to database (signup), if it fails then the user exists but the password is wrong
                try:
                    user = users.find_one({'username': payload["data"]['inputUsername']})
                    if user:
                        raise RuntimeError # Username is already taken
                    user_dict = {
                        "username": payload["data"]['inputUsername'],
                        "password": md5((payload["data"]['inputPassword']).encode('utf-8')).hexdigest(),
                        "profilepic": "https://d3ipks40p8ekbx.cloudfront.net/dam/jcr:3a4e5787-d665-4331-bfa2-76dd0c006c1b/user_icon.png",
                        "pronouns": "They/Them",
                        "description": "",
                        "email": "",
                        "firstName": "",
                        "lastName": "",
                        "country": "",
                        "birthday": "",
                        "occupation": "",
                        "mobile_number": "",
                        "phone_number": "",
                        "my_journal": "",
                        "my_experience": "",
                        "my_education": "",
                        "bg": "#f1f2f7"
                    }
                    users.insert_one(user_dict)
                    auth_user(user_dict)
                    return 'PROFILE'
                # User exists but password is incorrect
                except:
                    return 'TAKEN'
        except:
            return 'FAILURE'
    return 'LOGIN'

# Handles Frontend POST profile
@app.route('/profile', methods=["POST"])
def homepage():
    payload = request.json
    user = users.find_one({'username': payload["data"]["searchUsername"]})
    del user['_id'] # Added by mongoDB, unnecessary for this app
    # Checks if user is the current session user
    if user["username"] == session['username']:
        current = True
    else:
        current = False
    user["current"] = current
    return user

# Handles any Frontend route where it requires checking who the current logged in user is
@app.route('/currentUser')
def currentUser():
    try:
        user = get_current_user()
        del user['_id']
        return user
    except:
        return 'FAILURE'

# Handles Frotend POST edit
@app.route('/edit', methods=['POST'])
def edit():
    payload = request.json
    current_user = get_current_user()
    # profilepic is a url and often gives errors with the HTML, this value is not shown in the form so if it is left blank, it should not overwrite the previous url.
    if (payload["data"]['editProfilePic'] != ""):
        users.update_one({'username': current_user["username"]}, {"$set": {
            "profilepic": payload["data"]['editProfilePic'],
            "pronouns": payload["data"]['editpronouns'],
            "email": payload["data"]['editEmail'],
            "description": payload["data"]['editDescription'],
            "firstName": payload["data"]['editFirstName'],
            "lastName": payload["data"]['editLastName'],
            "country": payload["data"]['editCountry'],
            "birthday": payload["data"]['editBirthday'],
            "occupation": payload["data"]['editOccupation'],
            "mobile_number": payload["data"]['editMobileNumber'],
            "phone_number": payload["data"]['editPhoneNumber'],
            "my_journal": payload["data"]['editJournal'],
            "my_experience": payload["data"]['editExperience'],
            "my_education": payload["data"]['editEducation']
        }})
    else:
        users.update_one({'username': current_user["username"]}, {"$set": {
            "pronouns": payload["data"]['editpronouns'],
            "email": payload["data"]['editEmail'],
            "description": payload["data"]['editDescription'],
            "firstName": payload["data"]['editFirstName'],
            "lastName": payload["data"]['editLastName'],
            "country": payload["data"]['editCountry'],
            "birthday": payload["data"]['editBirthday'],
            "occupation": payload["data"]['editOccupation'],
            "mobile_number": payload["data"]['editMobileNumber'],
            "phone_number": payload["data"]['editPhoneNumber'],
            "my_journal": payload["data"]['editJournal'],
            "my_experience": payload["data"]['editExperience'],
            "my_education": payload["data"]['editEducation']
        }})
    return "SUCCESS"

# Handles Frotend POST editbg
@app.route('/editbg', methods=['POST'])
def editbg():
    payload = request.json
    current_user = get_current_user()
    users.update_one({'username': current_user["username"]}, {"$set": {
        "bg": payload["data"]['editBgprofile']
    }})
    return "SUCCESS"
    
# Handles Frontend delete
@app.route('/delete')
def delete():
    users.delete_one({'username': session["username"]})
    reset_session() # Resets the session just in case, still sends to Login so the user should be logged out anyway
    return 'SUCCESS'


if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0")