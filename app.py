import os
import uuid
from flask import Flask, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import pymysql   # MySQL connector

app = Flask(__name__)

# InfinityFree MySQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://if0_41787435:OCzpJa0yjiF9id2@sql310.infinityfree.com:3306/if0_41787435_1233"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'twarvis-secret-key-2024'

# ✅ Uploads folder in root
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), "uploads")
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Notes table
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    original_name = db.Column(db.String(200), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    downloads = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.UTC))

# Initialize DB only once, after first request
@app.before_first_request
def init_db():
    db.create_all()
    print("✅ Database tables created successfully!")

# Example route
@app.route("/")
def index():
    return "Twarvis PDF Web is running with uploads in root!"
