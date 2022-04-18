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
    return render_template("welcome.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
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

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash('Registration Successful!', 'success')
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash('Welcome, {}'.format(request.form.get("username")), 'info')
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
    flash('You have been logged out', 'info')
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/manage_trails")
def manage_trails():
    trails = list(mongo.db.trails.find())
    return render_template("manage-trails.html", trails=trails)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    trails = list(mongo.db.trails.find({"$text": {"$search": query}}))
    return render_template("trails.html", trails=trails)


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    trails = list(mongo.db.trails.find({"created_by": session["user"]}))
   

    # get user favourites
    favourites = list(mongo.db.favourites.find({"username": session['user']}))
    print(favourites)

    # make only a list of the favoute ids
    object_ids = [i["title_name"] for i in favourites]
    print(object_ids)

    # get all trails if the contain the id in our list of favourite ids
    # TODO
    favs = mongo.db.trails.find({"_id": {"$in": object_ids}})
    print(favs)

    return render_template("profile.html", favs=favs, trails=trails, username=username)


@app.route("/get_trails")
def trails():
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    trails = list(mongo.db.trails.find({}))
    favourites = list(mongo.db.favourites.find({"username": session['user']}))
    for i in trails:
        i["favourite"] = "far"
        for j in favourites:
            if i["_id"] == j["title_name"]:
                i["favourite"] = "fas"
                break
                 
    return render_template("trails.html", username=username, trails=trails)


@app.route("/add_trail", methods=["GET", "POST"])
def add_trail():
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
    difficulty = mongo.db.difficulty.find().sort("difficulty_level", 1)
    return render_template(
        "add_trail.html", types=types, difficulty=difficulty)


@app.route("/edit_trail/<trail_id>", methods=["GET", "POST"])
def edit_trail(trail_id):
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
    types = mongo.db.types.find().sort("type_name", 1)
    difficulty = mongo.db.difficulty.find().sort("difficulty_level", 1)
    return render_template(
        "edit_trail.html", trail=trail, types=types, difficulty=difficulty)


@app.route("/delete_trail/<trail_id>")
def delete_trail(trail_id):
    mongo.db.trails.delete_one({"_id": ObjectId(trail_id)})
    flash('Trail Successfully Deleted', 'success')
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return redirect(url_for("profile", username=username))


@app.route("/add_favourite/<trail_id>", methods=["GET", "POST"])
def add_favourite(trail_id):
    """
    add trail into favourites collection in DB.
    """
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    fav = mongo.db.favourites.find_one({"username": session["user"],"title_name": ObjectId(trail_id)})
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
    delete trails from favourites collection in DB and from profile

    """
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    mongo.db.favourites.delete_one({"title_name": ObjectId(trail_id),
                                     "username": username })

    return redirect(url_for("profile", username=session["user"]))
def not_found(e):
    """
        Render 404 page if errors occur
        Code credit to Geeks for Geeks for 404 error handling
        https://www.geeksforgeeks.org/python-404-error-handling-in-flask/
    """
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
