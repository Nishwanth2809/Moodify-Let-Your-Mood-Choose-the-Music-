from flask import Flask
from flask_session import Session
from dotenv import load_dotenv
import os
from routes import register_routes

load_dotenv()

app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET", "default_secret_key")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
