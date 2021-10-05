from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'My First API !!'

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'You have reached the home route. The request to hit the gql endpoint is /graphql.'