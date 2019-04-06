from imprint_app import app
import os
print("starting flask...")

#os.remove("./pics.json")

app.run(host="0.0.0.0", threaded=False)