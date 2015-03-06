from flask import Flask
from bluepy.btle import UUID, Peripheral, DefaultDelegate

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(port=8080)