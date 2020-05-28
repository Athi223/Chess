from flask import Flask, render_template, session
from flask_socketio import SocketIO, join_room, emit
from random import randint

app = Flask(__name__)
socketio = SocketIO(app)

rooms = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('chess.html')

@socketio.on('create')
def on_create():
    while True:
        room = randint(1,100)
        if room not in rooms:
            rooms[room] = { 'end': False, 'full': False }
            join_room(room)
            session['room'] = room
            emit('create_room', {'room': room})
            break

@socketio.on('join')
def on_join(data):
    room = int(data['room'])
    if room in rooms:
        if rooms[room]['full']:
            emit('join_room', {'room': False})
        else:
            rooms[room]['full'] = True
            join_room(room)
            session['room'] = room
            emit('join_room', {'room': True}, room=room)
    else:
        emit('join_room', {'room': False})
    

@socketio.on('move')
def on_move(data):
    room = session.get('room')
    emit('move_room', { 'move': data['move'] }, room=room)

@socketio.on('end')
def on_end(data):
    room = session.get('room')
    if data['opt'] == '1':
        if rooms[room]['end'] == False:
            rooms[room]['end'] = True
        else:
            rooms[room]['end'] = False
            emit('reset', room=room)
    else:
        emit('home', room=room)
        del rooms[room]

@socketio.on('chat')
def on_chat(data):
    emit('chat_room', { 'msg': data['msg'], 'player': data['player'] }, room=session.get('room'))

# Execution
if __name__ == "__main__":
    socketio.run(app, debug=True)
