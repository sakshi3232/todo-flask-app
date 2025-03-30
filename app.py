from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import datetime
import requests
from azure.messaging.notificationhubs import NotificationHubClient
from config import Config
from models import db, User, Task

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    if current_user.is_authenticated:
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        return render_template("index.html", tasks=tasks)
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/add_task", methods=["POST"])
@login_required
def add_task():
    title = request.form["title"]
    due_date = request.form["due_date"]
    due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d")
    task = Task(user_id=current_user.id, title=title, due_date=due_date)
    db.session.add(task)
    db.session.commit()

    # Send push notification
    send_push_notification(title, due_date)

    return redirect(url_for("index"))

@app.route("/delete_task/<int:task_id>")
@login_required
def delete_task(task_id):
    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("index"))

def send_push_notification(task_title, due_date):
    hub_client = NotificationHubClient.from_connection_string(Config.AZURE_CONNECTION_STRING, Config.AZURE_NOTIFICATION_HUB)
    message = f"Reminder: {task_title} is due on {due_date.strftime('%Y-%m-%d')}"
    hub_client.send_direct_notification(message, user_id=str(current_user.id))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
