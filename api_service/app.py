from flask import Flask
import os
import sys

# Ensure current folder is in Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@db:5432/metadata_db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Import routes
from routes.datasets import datasets_bp
from routes.lineage import lineage_bp
from routes.openlineage import openlineage_bp
from routes.runs import runs_bp

app.register_blueprint(datasets_bp)
app.register_blueprint(lineage_bp)
app.register_blueprint(openlineage_bp)
app.register_blueprint(runs_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)