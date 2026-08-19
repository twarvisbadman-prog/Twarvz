import os
import uuid
from flask import Flask, request, render_template_string, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

app = Flask(__name__)

# ============================================================
#  FIXED DATABASE CONFIGURATION
# ============================================================
# The port is now a query parameter, not part of the host
database_url = os.environ.get('DATABASE_URL', 'mysql+pymysql://if0_41787435:OCzpJa0yjiF9id2@sql310.infinityfree.com/if0_41787435_1233?port=3306')

# If Render provides a different DATABASE_URL format, use it
if os.environ.get('DATABASE_URL'):
    database_url = os.environ.get('DATABASE_URL')
    # Ensure it uses the correct driver
    if database_url.startswith('mysql://'):
        database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'twarvis-secret-key-2024')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Create uploads folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# ============================================================
#  REST OF YOUR CODE (models, routes, HTML template)
#  Keep everything else exactly the same
# ============================================================