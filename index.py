from flask import Flask
from yeelightblue import YeeLightBlue
from random import randint
import time
import config

app = Flask(__name__)
yeelightblue = YeeLightBlue()

@app.route('/')
def color():
    red = randint(0, 255)
    green = randint(0, 255)
    blue = randint(0, 255)
    yeelightblue.setColor(red, green, blue)

    return 'red {0} green {1} blue {2} setted'.format(red, green, blue)

@app.route('/flow')
def colorFlow():
    yeelightblue.colorFlow()

    return 'color flow'

@app.route('/on')
def on():
    yeelightblue.turnOn()

    return 'on'

@app.route('/off')
def off():
    yeelightblue.turnOff()

    return 'off'


if __name__ == '__main__':
    app.run(host=config.SERVER_IP, port=config.SERVER_PORT)