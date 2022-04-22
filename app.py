"""
    Code adapted from Code Institute Course Material
    Task Manager Flask App mini Project
"""
import os
import datetime
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def index():
    """
    When user first landing on the home page is loaded
    """
    return render_template("welcome.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    """
    Get user's username from the form, and check if it already exists in
    the database. If user exists, flash a message and redirect to register
    page. Save user in the database, put user into a session cookie and
    redirect to profile page.
    """
    if request.method == "POST":
        # username already exists in db check
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash('Username already exists', 'error')
            return redirect(url_for("register"))

        register = {
            "fullname": request.form.get("fullname").lower(),
            "email": request.form.get("email").lower(),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash('Registration Successful!', 'success')
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Find user's saved account in database, check if password matches
    and if not flash a message. If does, welcome usename in the profile
    page.
    """

    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash(
                    'Welcome, {}'.format(request.form.get("username")), 'info')
                return redirect(url_for(
                    "trails", username=session["user"]))
            else:
                # invalid password match
                flash('Incorrect Username and/or Password', 'error')
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash('Incorrect Username and/or Password', 'error')
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """
    Log user out, remove them from session cookies and render login page.
    """
    flash('You have been logged out', 'info')
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/get_trails")
def trails():
    """
    Get the list of trails and render them on trails.page.
    Find the clicked trail_id, check if trail_id equalls with the favourite
    title_name and toggle the heart icon.
    """
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    trails = list(mongo.db.trails.find({}))
    favourites = list(mongo.db.favourites.find({"username": session['user']}))
    for trail in trails:
        trail["favourite"] = "far"
        for favourite in favourites:
            if trail["_id"] == favourite["title_name"]:
                trail["favourite"] = "fas"
                break

    return render_template("trails.html", username=username, trails=trails)


@app.route("/manage_trails")
def manage_trails():
    """
    Get trails and render them on manage-trails page.
    """
    trails = list(mongo.db.trails.find())
    return render_template("manage-trails.html", trails=trails)


@app.route("/search", methods=["GET", "POST"])
def search():
    """
    user can search for trails on The Collection page using keywords
    for 'title' and 'description'.
    """
    query = request.form.get("query")
    favourites = list(mongo.db.favourites.find({"username": session['user']}))
    trails = list(mongo.db.trails.find({"$text": {"$search": query}}))
    for trail in trails:
        trail["favourite"] = "far"
        for favourite in favourites:
            if trail["_id"] == favourite["title_name"]:
                trail["favourite"] = "fas"
                break
            
    return render_template("trails.html", trails=trails)


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    """
        Get username from db, get user's input for all fields and update in db.
        If user has selected favourite, get and render it on the corresponding
        field.
    """
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    trails = list(mongo.db.trails.find({"created_by": session["user"]}))
    # get user favourites
    favourites = list(mongo.db.favourites.find({"username": session['user']}))
    # make only a list of the favourite ids
    object_ids = [i["title_name"] for i in favourites]
    # get all trails if the contain the id in our list of favourite ids
    favs = mongo.db.trails.find({"_id": {"$in": object_ids}})

    return render_template(
        "profile.html", favs=favs, trails=trails, username=username)


@app.route("/add_trail", methods=["GET", "POST"])
def add_trail():
    """
        Get session user, get input from user in add trail page, store it in
        db and flash a message. Render new added trail on trails page.
    """
    if request.method == "POST":
        trail = {
            "title": request.form.get("title"),
            "type": request.form.get("type_name"),
            "location": request.form.get("location"),
            "difficulty": request.form.get("difficulty_level"),
            "miles": request.form.get("miles"),
            "image_url": request.form.get("image_url"),
            "description": request.form.get("description"),
            "created_by": session["user"],
            "post_date": datetime.datetime.utcnow().strftime(
                '%d %B %Y')

        }
        mongo.db.trails.insert_one(trail)
        flash('Trail Successfully Added', 'success')
        return redirect(url_for("trails"))

    types = mongo.db.types.find().sort("type_name", 1)
    difficulty = mongo.db.difficulty.find()
    return render_template(
        "add_trail.html", types=types, difficulty=difficulty)


@app.route("/edit_trail/<trail_id>", methods=["GET", "POST"])
def edit_trail(trail_id):
    """
    Get user's editted input and update db.Redirect to trail page
    upon successful flash message.
    """
    if request.method == "POST":
        submit = {
            "title": request.form.get("title"),
            "type": request.form.get("type_name"),
            "location": request.form.get("location"),
            "difficulty": request.form.get("difficulty_level"),
            "miles": request.form.get("miles"),
            "image_url": request.form.get("image_url"),
            "description": request.form.get("description"),
            "created_by": session["user"]
        }
        myquery = {"_id": ObjectId(trail_id)}
        new_values = {"$set": submit}
        mongo.db.trails.update_one(myquery, new_values)

        flash('Trail Successfully Updated', 'success')
        return redirect(url_for("trails"))

    trail = mongo.db.trails.find_one({"_id": ObjectId(trail_id)})
    types = mongo.db.types.find()
    difficulty = mongo.db.difficulty.find().sort("difficulty_level", 1)
    return render_template(
        "edit_trail.html", trail=trail, types=types, difficulty=difficulty)


@app.route("/delete_trail/<trail_id>")
def delete_trail(trail_id):

    """
    Delete trail id from the collection and flash message.
    """
    mongo.db.trails.delete_one({"_id": ObjectId(trail_id)})
    flash('Trail Successfully Deleted', 'success')
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return redirect(url_for("profile", username=username))


@app.route("/delete_managetrail/<trail_id>")
def delete_managetrail(trail_id):

    """
    Admin delete any trail from the collection and
    and render manage_trails page.
    """
    mongo.db.trails.delete_one({"_id": ObjectId(trail_id)})
    flash('Trail Successfully Deleted', 'success')
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return redirect(url_for("manage_trails", username=username))


@app.route("/add_favourite/<trail_id>", methods=["GET", "POST"])
def add_favourite(trail_id):
    """
    Add trail into favourites collection in DB and flash a message.
    """
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    fav = mongo.db.favourites.find_one(
        {"username": session["user"], "title_name": ObjectId(trail_id)})
    if fav:
        return redirect(url_for("trails", username=username))
    data = {
        "title_name": ObjectId(trail_id),
        "username": username
    }
    mongo.db.favourites.insert_one(data)
    flash("Trail saved to favourites", 'info')
    return redirect(url_for("trails", username=username))


@app.route("/remove_favourite/<trail_id>")
def remove_favourite(trail_id):
    """
    delete trails from favourites collection in DB and from profile.
    """
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    mongo.db.favourites.delete_one(
        {"title_name": ObjectId(trail_id), "username": username})
    return redirect(url_for("profile", username=session["user"]))
    

@app.errorhandler(404)
def not_found(e):
    """
        Render 404 page if errors occur
        Code credit to Geeks for Geeks for 404 error handling
        https://www.geeksforgeeks.org/python-404-error-handling-in-flask/
    """
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    """
        Render 500 page if errors occur
        Code credit to Digital Ocean for handling internal server errors
        https://www.digitalocean.com/community/tutorials/how-to-handle-errors-in-a-flask-application
    """
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)