import io
import time
import threading
import picamera
# Create a pool of image processors
done = False
lock = threading.Lock()
pool = []

class ImageProcessor(threading.Thread):
    def __init__(self):
        super(ImageProcessor, self).__init__()
        self.terminated = False

    def run(self, cam):
        time.sleep(1)
        print("running")
        cam.capture("test.jpg")



if __name__ == '__main__':
    p = ImageProcessor()
    cam = picamera.PiCamera()
    p.run(cam)