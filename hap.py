import logging

from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_SENSOR
from edgetpu.classification.engine import ClassificationEngine
import io
from utils import retrain, get_labels,Camera, ApplicationState
import signal
import os

camera = Camera()
stream = io.BytesIO()
app_state = ApplicationState()
app_state.start()


class MotionSensor(Accessory):

    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        serv_motion = self.add_preload_service('MotionSensor')
        self.char_detected = serv_motion.configure_char('MotionDetected')
        self.engine = ClassificationEngine("./models/classify.tflite")
        self.is_trained = retrain()
        self.labels = get_labels()
        self.is_running = True
        logging.info(self.setup_message())

    def run(self):
        while self.is_running:

            if app_state.last_state == "shutdown":
                self.is_running = False
                os.system('kill $PPID')

            if (app_state.last_state == "run") and self.is_trained:
                detection=False
                img = camera.returnPIL()
                output = self.engine.ClassifyWithImage(img)
                if output[0][0] == int(self.labels["detection"]):
                    detection = True
                    logging.info("detection triggered")
                self._detected(detection)

            if app_state.last_state == "retrain":
                logging.info("imprinting weights")
                self.is_trained=retrain()
                self.labels = get_labels()

                if self.is_trained:
                    self.engine = ClassificationEngine("./models/classify.tflite")
                    app_state.last_state = "run"
                    logging.info("finished imprinting")

                else:
                    app_state.last_state = "collect"
                    logging.warning("could not imprint weights. Please provide enough pictures")

            if app_state.last_state == "collect_background":
                camera.collect("background")
                app_state.last_state = "collect"

            if app_state.last_state == "collect_detection":
                camera.collect("detection")
                app_state.last_state = "collect"

    def _detected(self, val=False):
        self.char_detected.set_value(val)

    def stop(self):
        logging.info("shut down")
        super().stop()


logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")



def get_accessory(driver):
    """Call this method to get a standalone Accessory."""
    return MotionSensor(driver, 'Coral')

# Start the accessory on port 51826
driver = AccessoryDriver(port=51826)

# Change `get_accessory` to `get_bridge` if you want to run a Bridge.
driver.add_accessory(accessory=get_accessory(driver))

# We want SIGTERM (terminate) to be handled by the driver itself,
# so that it can gracefully stop the accessory, server and advertising.
signal.signal(signal.SIGTERM, driver.signal_handler)

# Start it!

driver.start()