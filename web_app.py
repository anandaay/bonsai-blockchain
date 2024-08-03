from brownie import *
p = project.load('brownie-dir')
p.load_config()


from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"