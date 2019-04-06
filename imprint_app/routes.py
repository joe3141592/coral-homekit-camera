from flask import Flask, render_template, redirect, request, send_file
from tinydb import TinyDB, Query, where
import json
from PIL import Image
from io import BytesIO
from utils import StateManager
from imprint_app import app

state_manager = None
q = Query()


@app.before_first_request
def test():
    global state_manager
    state_manager = StateManager()


def load_pic(file):
    img_io = BytesIO()
    dummy_img = Image.open("./pics/{}.jpg".format(file))#.resize((224,224))
    dummy_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return img_io


classes = TinyDB("./classes.json")
pics = TinyDB("./pics.json")


@app.route("/samples/", methods=["POST", "GET"])
def add_sample():
    if request.method == "POST":
        if request.form["class"] == "background":
            state_manager.collect_background()
        else:
            state_manager.collect_detection()

    if request.method == "GET":
        res=pics.all()
        print(res)
        return json.dumps({"ids": [{"id":r["img"], "class":r["class"]} for r in res]})

    return "ok"


@app.route("/state/", methods=["POST", "GET"])
def handle_state():
    if request.method == "POST":
        new_state = request.form["state"]
        if new_state == "retrain":
            state_manager.retrain()
        return "ok"


@app.route("/samples/<cid>", methods=["POST", "GET", "DELETE"])
def get_pic(cid):
    if request.method == "GET":
        print(cid)
        res=pics.get(q["img"] == cid)
        print(res)
        img_io = load_pic(res["img"])
        return send_file(img_io, mimetype='image/jpeg')

    if request.method == "DELETE":
        pics.remove(where('img') == cid)
        return "deleted"


@app.route('/')
def hello_world():
    return redirect("/static/index.html")


