from flask import Flask, redirect, url_for, render_template, request, session, g
from datetime import timedelta
import retrieve_data as rd
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config["SECRET_KEY"] = "chat"
socketio = SocketIO(app, logger=True,
    engineio_logger=True, cors_allowed_origins="*")

available_chats_dict={"yanchovies"}

@app.route("/", methods=["POST", "GET"])
def home_page():
    if request.method=='GET':
        #return render_template("home.html")
        return render_template("chat.html", streamer="Yanchovies")
    else:
        username = request.form.get("username")

        #conn = rd.connect()
        #users = rd.check_records(streamer, conn)

        #rd.close_connection(conn)

        #if len(users)>=1:
        session["chat"]=username
        return redirect(url_for('direct_to_stream', streamer=username))
    
@app.route("/<streamer>", methods=["POST", "GET"])
async def direct_to_stream(streamer):
    if request.method=="GET":
        available_chats_dict.add(streamer)
        return render_template("chat.html", streamer=streamer)
    if request.method=="POST":
        if streamer in available_chats_dict:
            message=request.form.get("message")
            print(message)
            
            # if message=="!end":
            #     print("ENDING STREAM")
            #     available_chats_dict.remove(streamer)              
    

@socketio.on('message')
def handle_message(message):
    print(message)
    if message != "USER CONNECTED":
        send(message, broadcast=True)
    #if message == "!end":
     #   print("ENDING STREAM")
        #session.pop(streamer)
        #available_chats_dict.remove(streamer)

if __name__=="__main__":
    #app.run(debug=True)
    socketio.run(app, debug=True, host="mytwitch.herokuapp.com")
# Instead of Python reading from file, JavaScript reads from file and sends random message (POST request) to Python backend

