import os
import uuid
from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

# Add this import for MySQL
import pymysql

app = Flask(__name__)

# InfinityFree MySQL connection
# Make sure your database name is exactly as created in InfinityFree
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://if0_41787435:OCzpJa0yjiF9id2@sql310.infinityfree.com:3306/if0_41787435_1233"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'twarvis-secret-key-2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Create uploads folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

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

# Create tables
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

# Rest of your code continues here...
# (The HTML template and routes remain the same)
