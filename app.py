from flask import Flask, redirect, url_for, render_template, request, session
from flask_socketio import SocketIO, emit
import retrieve_data as rd
import random

app = Flask(__name__)
app.config["SECRET_KEY"] = "chat"
socketio = SocketIO(app, logger=True,
    engineio_logger=True, cors_allowed_origins="*")

random_users = []
lines = []
active_chats = {"Yanchovies":0}

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

@app.route("/", methods=["POST", "GET"])
def home_page():
    if request.method=='GET':
        return render_template("home.html")
    else:
        username = request.form.get("username")

        conn = rd.connect()
        users = rd.check_records(username, conn)

        if len(users)>=1:
            rd.close_connection(conn)
            return redirect(url_for('direct_to_stream', streamer=username))
        else:     
            rd.add_user(username, "Password", conn)   
            rd.close_connection(conn)
            return render_template("home.html")
    

@app.route("/<streamer>", methods=["POST", "GET"])
def direct_to_stream(streamer):
    return render_template("chat.html", streamer=streamer)            


@socketio.on('message')
def handle_message(message, streamer):
    global active_chats
    print(message)
    emit("new_message", message, broadcast=True)
    emit("random_message", "Yanchovies: LMAO", broadcast=True)


@socketio.on('random_message')
def handle_random_message(user, streamer):
    if active_chats[streamer] > 0:

        random_message = read_random_message()
        random_user = read_random_user()
        print(random_message)
        emit("random_message", random_user+": "+random_message, broadcast=True)


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
    #socketio.run(app, debug=True, host="192.168.1.166")
