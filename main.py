# main.py
from flask import Flask
from flask_socketio import SocketIO
from controllers import bp  # Importa o blueprint com as rotas
from models import DatabaseManager
import eventlet

app = Flask(__name__)
app.secret_key = "supersecretkey"
socketio = SocketIO(app, async_mode='eventlet')

# Inicializa o banco de dados com o schema atualizado
def init_db():
    DatabaseManager.init_db()

# Registra o blueprint dos controllers
app.register_blueprint(bp)

if __name__ == '__main__':
    init_db()
    socketio.run(app, host='0.0.0.0', port=5000)
