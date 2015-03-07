from flask import Flask
from bluepy.btle import UUID, Peripheral, DefaultDelegate
from yeelightblue import YeeLightBlue

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

yeelightblue = YeeLightBlue()

if __name__ == '__main__':
    app.run(port=8080)