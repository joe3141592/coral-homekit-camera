from flask import Flask

import picamera


class Capture(object):

    def __init__(self):
        self.cam = picamera.PiCamera()

    def take(self):
        self.cam.capture("test.jpg")



app = Flask(__name__)

from imprint_app import routes
