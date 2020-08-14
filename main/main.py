from flask_ngrok import run_with_ngrok
from flask import Flask, render_template, request
from dialogue_manager import *
    
app = Flask(__name__)
run_with_ngrok(app)
dialogue_manager = DialogueManager()
print("comlpeted")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(dialogue_manager.generate_answer(userText))
 

if __name__ == "__main__":
    app.run()
