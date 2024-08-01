from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from flask_session import Session
from werkzeug.utils import secure_filename
import sqlite3
import secrets
import random

from datetime import datetime

app = Flask(__name__, static_folder="static")
app.config["SECRET_KEY"] = "chiaggadiigga"


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


connect = sqlite3.connect("database.db")


UPLOAD_FOLDER = "static/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER



# this is to make different file render by same url
user=""
@app.route("/")
def home():
    name = random.choice(["shubham", "geeta"])
    return redirect(url_for('index', name=name))
@app.route("/<string:name>")
def index(name):

    session["name"]=name.lower()
    global user
    user=session["name"]
    limit_count = 6
    if user=="geeta":
        limit_count =0
    with sqlite3.connect("database.db") as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM posts WHERE username = ? LIMIT ?", (session["name"], limit_count))
        data = cursor.fetchall()

        # Render the HTML template inside templates/<name>/name.html
        temp = name + "/index.html"

        return render_template(temp, data=data)


@app.route("/about")
def about():
    return render_template(f"{user}/about.html")


@app.route("/resume")
def resume():
    return render_template(f"{user}/resume.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/login")
def lofinform():
    return render_template("login.html")

@app.route("/logout")
def logout():
    user = session.pop("username", None)
    return redirect(url_for('index', name=session['name']))


# ye hamare team ke lie

@app.route("/advitiya")
def advitiya():
    return render_template("advitiya.html",)

# @app.route("/admin")
# def admin():
#     try:
#         if session["username"]:
#             return render_template("admin.html")
#     except:
#         pass
#     return redirect(url_for("login"))


@app.route("/upload")
def upload_form():
    if session.get("username"):
        return render_template("upload.html")
    else:
        return redirect(url_for("login"))
    # if session.get('username'):
    #      return render_template("upload.html")
    # else:
    #     return redirect(url_for("upload"))


@app.route("/upload", methods=["POST"])
def upload_file():
    if "photo" not in request.files:
        return "No file part"

    photo = request.files["photo"]
    text = request.form.get("text")
    title = request.form.get("title")
    selected_option = request.form.get('option')
    dt = datetime.now()
    if selected_option:
        pass
        
    else:
      # No option selected (handle as needed)
      message = "Please select an option"
      return message




    time = dt.strftime("%Y-%m-%d %H:%M")
    if photo.filename == "":
        return "No selected file"

    if photo:
        filename = secure_filename(photo.filename)
        extension = os.path.splitext(filename)[1]
        randommm = secrets.token_urlsafe(16)
        new_filename = randommm + extension
        photo.save(os.path.join(app.config["UPLOAD_FOLDER"], new_filename))

        # upload to database
        with sqlite3.connect("database.db") as users:
            cursor = users.cursor()
            cursor.execute(
                f"""INSERT INTO posts  
                (postID,media,title,caption,time,username,post_type) VALUES (?,?,?,?,?,?,?)""",
                (randommm, new_filename, title, text, time, session.get("username"),selected_option),
            )
            users.commit()

        return redirect(url_for("index",name=session.get("username")))


@app.route("/login", methods=["GET", "POST"])
def loginform():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        connect = sqlite3.connect("database.db")
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM users")
        data = cursor.fetchall()

        for all in data:
            if username in all:
                if password == all[1]:
                    session["username"] = username
                    return redirect(url_for("index",name=session["username"]))
                else:
                    return f"Wrong Password"
        return "Wrong Username"


@app.route("/view/<postid>")
def profile(postid):

    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM posts WHERE postID=? ", (postid,))
    data_in1 = cursor.fetchall()
    

    data_in = data_in1[0]
    data = {
        "postid": data_in[0],
        "media": data_in[1],
        "title": data_in[2],
        "content": data_in[3],
        "date": data_in[4],
    }
    return render_template("view.html", data=data)


@app.route("/delete/<postid>")
def delte(postid):
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()

    cursor.execute("Delete FROM users WHERE postID=?", (postid,))
    return redirect(url_for("index",name=session["username"]))

@app.route("/books")
def books():
    with sqlite3.connect("database.db") as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM posts WHERE post_type = ? and username = ?", ("book", session.get('name')))
        data = cursor.fetchall()
        # return data
        return render_template("books.html", data=data)
    


@app.route("/publications")
def publications():
        with sqlite3.connect("database.db") as connect:
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM posts WHERE post_type = ? and username = ?", ("publication", session.get('name')))

            data = cursor.fetchall()
            return render_template("publications.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)
