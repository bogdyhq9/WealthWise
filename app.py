import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from domain.errors.usererror import UserError

from domain.tables import UserTable, PostTable, LikesTable, CommentTable, GroupTable, MembersTable

from sqlalchemy import create_engine, and_, select
from sqlalchemy.orm import sessionmaker

from repository.repositoryGroup import RepositoryGroup
from repository.repositoryPost import RepositoryPost
from repository.repositoryUser import RepositoryUser
from service.service import Service

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine = create_engine('sqlite:///blog.db')
Session = sessionmaker(bind=engine)
sessiondata = Session()

repoUser = RepositoryUser()
repoPost = RepositoryPost()
repoGroup = RepositoryGroup()
service = Service(repoUser, repoPost, repoGroup)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def home():
    if "user_id" in session:
        likes = sessiondata.query(LikesTable).filter(LikesTable.user_id == session["user_id"]).all()
        likes = {like.post_id: 1 for like in likes}
    else:
        likes = {}
    posts = sessiondata.query(PostTable).all()
    dates = []

    for post in posts:
        date = post.date
        formatted_date = date.strftime("%Y-%m-%d")
        dates.append(formatted_date)

    return render_template("index.html", posts=posts, dates=dates, len=len(posts), likes=likes)


@app.route("/login", methods=["POST", "GET"])
def login():
    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        try:
            name = request.form.get("username")
            password = request.form.get("password")
            user = service.loginUser(name, password)
            session["user_id"] = user[0].id
        except UserError as e:
            flash(e)
            return render_template("login.html")

        return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        try:
            email = request.form.get("email")
            username = request.form.get("username")
            password = request.form.get("password")
            realname = request.form.get("realname")
            hash = generate_password_hash(password)
            service.addUser(email, username, hash, realname)
        except UserError as e:
            flash(e)
            return render_template("register.html")

        return redirect("/login")


@app.route("/changepassword", methods=["GET", "POST"])
def change():
    if request.method == "GET":
        return render_template("change.html")
    if request.method == "POST":
        try:
            username = request.form.get("username")
            email = request.form.get("email")
            newpass = request.form.get("newpass")
            confirmpass = request.form.get("confirmpass")
            service.changePassword(username,email,session['user_id'],newpass,confirmpass)
        except UserError as e:
            flash(e)
            return render_template("change.html")
        return redirect("/")


@app.route("/editprofile", methods=["GET", "POST"])
def edifprofile():
    if request.method == "GET":
        user_id = session["user_id"]
        user = service.getUserByID(user_id)
        return render_template("editprofile.html", user=user)
    if request.method == "POST":
        newusername = request.form.get("username")
        newrealname = request.form.get("realname")
        newdescription = request.form.get("description")
        user_id = session["user_id"]
        service.editprofile(newusername, newrealname, newdescription, user_id)
        return redirect("/profile")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/post", methods=["GET", "POST"])
def post():
    if request.method == "GET":
        return render_template("post.html")
    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category")
        content = request.form.get("content")
        user = service.getUserByID(session['user_id'])
        username = user.username
        service.addPost(title,category,content,username)
        return redirect("/")


@app.route("/like", methods=["POST"])
def like():
    if "user_id" not in session:
        flash("You have to log in")
        return render_template("login.html")
    else:
        idpost = request.form.get("post_id")
        userid = session["user_id"]

        post = sessiondata.query(PostTable).filter(PostTable.id == idpost).all()
        post[0].no_likes += 1

        like = LikesTable(user_id=userid, post_id=idpost)
        sessiondata.add(like)
        sessiondata.commit()
        return redirect("/")


@app.route("/comment", methods=["GET", "POST"])
def comment():
    if request.method == "GET":
        # Retrieve post_id from query parameters
        post_id = request.args.get("post_id")
        # Query the database to retrieve the post
        post = sessiondata.query(PostTable).filter(PostTable.id == post_id).first()
        if post:
            # Assuming post has a date attribute
            formatted_date = post.date.strftime("%Y-%m-%d")
            results = sessiondata.query(CommentTable).filter(CommentTable.post_id == post_id).all()
            dates = []
            users = []
            for result in results:
                date = result.created_at
                formatted_date = date.strftime("%Y-%m-%d")
                dates.append(formatted_date)
                user = sessiondata.query(UserTable).filter(UserTable.id == result.user_id).all()
                users.append(user[0].username)

            return render_template("comment.html", post=post, date=formatted_date, results=results, len=len(results),
                                   dates=dates, users=users)
        else:
            # Handle case where post_id does not exist
            return "Post not found"
    if request.method == "POST":
        if "user_id" in session:
            content = request.form.get("content")
            idpost = request.form.get("post_id")
            iduser = session["user_id"]
            comment = CommentTable(post_id=idpost, user_id=iduser, content=content)
            sessiondata.add(comment)
            sessiondata.commit()
            return redirect("/comment?post_id=" + idpost)
        else:
            flash("You have to log in")
            return render_template("login.html")


@app.route("/profile", methods=["GET"])
def profile():
    iduser = session["user_id"]
    user = service.getUserByID(iduser)
    posts = service.getAllPost()
    dates = []
    for post in posts:
        date = post.date
        formatted_date = date.strftime("%Y-%m-%d")
        dates.append(formatted_date)
    return render_template("profile.html", user=user, posts=posts, dates=dates, len=len(posts))


@app.route("/deletepost", methods=["GET", "POST"])
def deletepost():
    if request.method == "POST":
        id_post = request.form.get("post_id")
        post = sessiondata.query(PostTable).filter(PostTable.id == id_post).first()
        comments = sessiondata.query(CommentTable).filter(CommentTable.post_id == id_post).all()
        likes = sessiondata.query(CommentTable).filter(LikesTable.post_id == id_post).all()
        for like in likes:
            sessiondata.delete(like)
        for comment in comments:
            sessiondata.delete(comment)
        sessiondata.delete(post)
        sessiondata.commit()
        return redirect("/profile")


@app.route("/group", methods=["GET", "POST"])
def group():
    if request.method == "GET":
        groups = service.getAllGroups()
        members = sessiondata.query(MembersTable).filter(MembersTable.user_id == session['user_id']).all()

        members = {member.group_id for member in members}
        return render_template("group.html", groups=groups, len=len(groups), members=members)
    if request.method == "POST":
        group_id = request.form.get("group_id")
        group = service.getGroupById(group_id)
        group.number_of_members += 1
        member = MembersTable(user_id=session['user_id'], group_id=group_id)
        sessiondata.add(member)
        sessiondata.commit()
        return redirect("/group")


@app.route("/creategroup", methods=["GET", "POST"])
def creategroup():
    if request.method == "GET":
        return render_template("creategroup.html")
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        permission = request.form.get("permission")
        number_of_members = 1
        user_id = session['user_id']
        if permission == "Y":
            permission = True
        else:
            permission = False

        group = GroupTable(name=name, description=description, number_of_members=number_of_members, creator_id=user_id,
                           permission=permission)
        sessiondata.add(group)
        sessiondata.commit()
        member = MembersTable(user_id=session['user_id'], group_id=group.id)
        sessiondata.add(member)
        sessiondata.commit()
        return redirect("/group")


@app.route("/leavegroup", methods=["POST"])
def leavegroup():
    if request.method == "POST":
        group_id = request.form.get("group_id")
        member = sessiondata.query(MembersTable).filter(
            (MembersTable.user_id == session['user_id']) & (MembersTable.group_id == group_id)).first()
        sessiondata.delete(member)
        sessiondata.commit()

        group = sessiondata.query(GroupTable).filter(GroupTable.id == group_id).first()
        if group.creator_id == session['user_id']:
            members = sessiondata.query(MembersTable).filter(MembersTable.group_id == group_id).all()
            for member in members:
                sessiondata.delete(member)
            sessiondata.delete(group)
            sessiondata.commit()
    return redirect("/group")


sessiondata.close()
