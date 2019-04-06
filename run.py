from imprint_app import app
import os
print("starting flask...")

#os.remove("./pics.json")

app.run(host="192.168.178.89", threaded=False)