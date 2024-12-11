#import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from Company_chat import get_response

#logging.basicConfig(filename='ChatBotApp.log', encoding='utf-8', level=logging.DEBUG)


app = Flask(__name__)
CORS(app)

@app.get("/")
def index_get():
    return render_template("base.html")


@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    # TODO: check if text is valid
    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)

if __name__ == "__main__":
    app.run(debug=True)
