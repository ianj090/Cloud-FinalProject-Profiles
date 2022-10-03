from flask import Flask, redirect, request, flash, render_template
import requests # To make api requests to backend

# Set workspace values / app config
DEBUG = True # debug flag to print error information
SECRET_KEY = "a41014794565ebf9f22b99e2" # Used for Flask flash

app = Flask(__name__)
app.config.from_object(__name__) # loads workspace values

# Redirects to '/login' path
@app.route('/')
def initial():
    return redirect('/login')

# Start page for new connection, sign in with username and password (if user does not exists it gets created) and goes to '/profile' path through html form.
@app.route('/login', methods=['GET', 'POST'])
def login():
    payload = {"method": request.method}
    if request.method == 'POST':
        payload["data"] = request.form # Appends username and password to payload
    try:
        # Try to call backend (GET and POST work the same, backend handles this)
        try:
            r = requests.post('http://host.docker.internal:5000/login', json=payload)
            if r.text == 'PROFILE': # Successfully created user or logged in to existing
                return redirect('/profile')
            elif r.text == 'TAKEN': # Username exists and password is incorrect
                flash("That username is already taken") # Flask method to show messages to user (errors, other feedback)
                return render_template('login.html')
            else:
                raise RuntimeError
        except:
            return render_template('login.html') # Request failed, backend not online
    except:
        return 'FAIL'

# Main page for users, can either show your own profile or another user's profile (if POST)
@app.route('/profile', methods=['GET', 'POST'])
def homepage():
    payload = {"method": request.method}
    if request.method == 'POST': # POST method, returns searched user's profile
        payload["data"] = request.form
        try:
            user = requests.post('http://host.docker.internal:5000/profile', json=payload).json()
            current = user["current"]
        except:
            flash("User does not exist") # User not in DB
            return redirect("/profile")
    else: # GET Method, returns own user's profile
        try:
            user = requests.get('http://host.docker.internal:5000/currentUser').json()
            if user == 'FAILURE':
                raise RuntimeError
        except:
            return redirect('/login')
        current = True

    return render_template('profile.html',
        username = user["username"],
        profilepic = user["profilepic"],
        mood = user["mood"],
        description = user["description"],
        email = user["email"],
        firstName = user["firstName"],
        lastName = user["lastName"],
        country = user["country"],
        birthday = user["birthday"],
        occupation = user["occupation"],
        relationship_status = user["relationship_status"],
        mobile_number = user["mobile_number"],
        phone_number = user["phone_number"],
        my_journal = user["my_journal"],
        bg = user["bg"],
        current = current
    )

# Edits Profile information
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    payload = {"method": request.method}
    if request.method == 'POST': # Edits the information before getting the current user
        payload["data"] = request.form
        try:
            requests.post('http://host.docker.internal:5000/edit', json=payload)
            return redirect('/profile')
        except:
            return "FAIL" # Backend not online
    try:
        user = requests.get('http://host.docker.internal:5000/currentUser').json()
        if user == 'FAILURE':
            raise RuntimeError
    except:
        return redirect('/login') # User not logged in

    return render_template('editProfile.html',
        profilepic = user["profilepic"],
        mood = user["mood"],
        description = user["description"],
        email = user["email"],
        firstName = user["firstName"],
        lastName = user["lastName"],
        country = user["country"],
        birthday = user["birthday"],
        occupation = user["occupation"],
        relationship_status = user["relationship_status"],
        mobile_number = user["mobile_number"],
        phone_number = user["phone_number"],
        my_journal = user["my_journal"]
    )

# To Just change the background of the profile, functions the same as edit
@app.route('/editbg', methods=['GET', 'POST'])
def editbg():
    payload = {"method": request.method}
    if request.method == 'POST': # Edits background before retrieving user
        payload["data"] = request.form
        try:
            requests.post('http://host.docker.internal:5000/editbg', json=payload)
            return redirect('/profile')
        except:
            return "FAIL"
    try:
        user = requests.get('http://host.docker.internal:5000/currentUser').json()
        if user == 'FAILURE':
            raise RuntimeError
    except:
        return redirect('/login') # User not logged in

    return render_template('editBackground.html',
        bg = user["bg"]
    )

# Deletes current user from DB
@app.route('/delete')
def delete():
    try:
        user = requests.get('http://host.docker.internal:5000/currentUser').json()
        if user == 'FAILURE':
            raise RuntimeError
    except:
        return redirect('/login') # User not logged in
    
    # Tries to delete, if fails then the Backend is not online
    try:
        requests.get('http://host.docker.internal:5000/delete')
    except:
        flash('Could not remove user')
        return redirect('/profile')

    # If all passes go to login.
    flash("Deleted user")
    return redirect('/login')


if __name__ == '__main__':
    app.run(port=8080, host="0.0.0.0")