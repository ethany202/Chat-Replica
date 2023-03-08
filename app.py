from flask import Flask, redirect, url_for, render_template, request, session, g
from flask_socketio import SocketIO, emit
from datetime import timedelta
import retrieve_data as rd
import random

app = Flask(__name__)
app.config["SECRET_KEY"] = "chat"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
socketio = SocketIO(app, logger=True,
    engineio_logger=True, cors_allowed_origins="*")

random_users = []
lines = []
active_chats = {"Yanchovies":0}

# General Functions
def read_random_user():
    global random_users
    file="RandomUser.txt"
    if len(random_users)==0:
        random_users=open(file).read().splitlines()
    return random.choice(random_users)

def read_random_message():
    global lines
    file = "RandomText.txt"
    if len(lines)==0:
        lines = open(file).read().splitlines()
    return random.choice(lines)


# Path handlers
@app.route("/", methods=["POST", "GET"])
def home_page():
    if request.method=='GET':
        if "user" in session:
            return render_template("home.html", current_user=session['user'])
        else:
            return render_template("home.html", current_user="")
    else:
        streamer = request.form.get("username")

        conn = rd.connect()
        users = rd.check_records(streamer, conn)

        rd.close_connection(conn)
        if len(users)>=1:         
            return redirect(url_for('direct_to_stream', streamer=streamer))
        else:     
            if "user" in session:
                return render_template("home.html", current_user=session['user'])
            else:
                return render_template("home.html", current_user="")
    

@app.route("/<streamer>", methods=["POST", "GET"])
def direct_to_stream(streamer):
    if "user" in session:
        return render_template("chat.html", streamer=streamer)          
    return redirect(url_for('login'))  


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method=="GET":
        return render_template('login.html')
    else:
        username=request.form.get("username")
        password = request.form.get("password")
        conn = rd.connect()

        users = rd.verify_credentials(username, password, conn)
        rd.close_connection(conn)

        if len(users) == 0:
            return render_template('login.html')
        else:
            session['user'] = username
            session.permanent=True
            return redirect(url_for("home_page", current_user=username))


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method=='GET':
        return render_template('register.html')
    else:
        username=request.form.get('username')
        password=request.form.get('password')
        password_confirm = request.form.get('password-retype')

        if password != password_confirm:
            return render_template('register.html', warning="Please enter the same password twice")
        else:
            conn = rd.connect()
            existing_users = rd.check_records(username, conn)
            print(existing_users)
            if len(existing_users)>0:
                rd.close_connection(conn)
                return render_template('register.html', warning="This username already exists. Please select another one.")
            else:
                rd.add_user(username, password, conn)
                rd.close_connection(conn)

                session['user'] = username
                return redirect(url_for("home_page", current_user=username))

@app.route("/logout", methods=['POST'])
def logout():
    session.pop('user', None)

# Socket message handlers
@socketio.on('message')
def handle_message(message, streamer):
    global active_chats
    print(message)

    data = [session['user'], message]
    emit("new_message", data, broadcast=True)
    emit("random_message", "Yanchovies: LMAO", broadcast=True)


@socketio.on('random_message')
def handle_random_message(streamer):
    if active_chats[streamer] > 0:
        random_message = read_random_message()
        random_user = read_random_user()
        print(random_message)

        data=[random_user, random_message]
        emit("random_message", data, broadcast=True)


@socketio.on('delete_user')
def user_disconnected(streamer):
    global active_chats
    active_chats[streamer] -= 1
    if active_chats[streamer] < 0:
        active_chats[streamer]=0


@socketio.on('add_user')
def user_connected(streamer):
    global active_chats
    if streamer not in active_chats or active_chats[streamer]==0:
        active_chats[streamer] = 1
    else:
        active_chats[streamer]+=1
    emitted_value = [streamer,active_chats[streamer]]
    emit("set_connected_users", emitted_value, broadcast=True)


if __name__=="__main__":
    socketio.run(app, debug=True, host="mytwitch.onrender.com")
    #socketio.run(app, debug=True, host="172.27.176.1")
    #socketio.run(app, debug=True, host="10.123.112.31")
