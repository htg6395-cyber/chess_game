from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import chess

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# This board object will be the "Master" version of the game
game = chess.Board()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('move')
def handle_move(data):
    try:
        # Convert move to UCI format (e.g., 'e2e4')
        move = chess.Move.from_uci(data['from'] + data['to'])
        
        # Check if the move is legal on the "Master" board
        if move in game.legal_moves:
            game.push(move)
            # Broadcast to the other player
            emit('move', data, broadcast=True, include_self=False)
        else:
            # If illegal, force the sender to sync back to the real game state
            emit('sync', {'fen': game.fen()})
    except:
        # If there's an error, force sync
        emit('sync', {'fen': game.fen()})

if __name__ == '__main__':
    socketio.run(app)