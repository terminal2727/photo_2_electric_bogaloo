from flask import Flask
from server.api_setup import register_blueprints
from server.client_view import render_home
import os
import signal
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_home()

@app.route('/shutdown')
def close_app():
    print('Shutting down...')
    os.kill(os.getpid(), signal.SIGINT)

if __name__ == "__main__":
    register_blueprints(app)
    app.run(debug=True)