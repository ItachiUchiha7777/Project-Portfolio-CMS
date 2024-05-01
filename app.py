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



user=""



@app.route("/")
def index(str): 
   
    with sqlite3.connect("database.db") as connect:
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM posts")
            data = cursor.fetchall()
            # return (data)
            return render_template("index.html", data=data)
            

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/resume")
def resume():
    return render_template("resume.html")

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

@app.route("/admin")
def admin():
    try:
        if session["name"]:
             return render_template("admin.html")
    except:
        pass
    return redirect(url_for("login"))

    

@app.route("/upload")
def upload_form():
    if session.get('name'):
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
    dt = datetime.now()

   
    time = dt.strftime('%Y-%m-%d %H:%M')
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
                """INSERT INTO posts  
                (postID,media,title,caption,time) VALUES (?,?,?,?,?)""",
                (randommm,new_filename,title, text,time),
            )
            users.commit()

        return redirect(url_for("index"))


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
                    session["name"] = username
                    return redirect(url_for("index"))
                else:
                    return f"Wrong Password"
        return "Wrong Username"














@app.route("/view/<postid>")
def profile(postid):
    
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM posts WHERE postID=? ", (postid,))
    data_in1 = cursor.fetchall()  
    data_in=data_in1[0]
    data={
            "postid": data_in[0],
            "media": data_in[1],
            "title": data_in[2],
            "content": data_in[3],
            "date":data_in[4],
        }
    return render_template("view.html",data=data)




@app.route("/delete/<postid>")
def search_user(postid):
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM users WHERE postID=?", (postid,))
    data_in = cursor.fetchall()  
    return data_in




if __name__ == "__main__":
    app.run( debug=True)

