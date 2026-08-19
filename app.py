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
# Clean database URL without port in the string
database_url = os.environ.get('DATABASE_URL', 'mysql+pymysql://if0_41787435:OCzpJa0yjiF9id2@sql310.infinityfree.com/if0_41787435_1233')

if os.environ.get('DATABASE_URL'):
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('mysql://'):
        database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)
    # Remove any port from the URL string
    if '?port=' in database_url:
        database_url = database_url.split('?')[0]
    if ':3306/' in database_url:
        database_url = database_url.replace(':3306/', '/')

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'port': 3306  # Port as integer, not in URL
    }
}
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'twarvis-secret-key-2024')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# ============================================================
#  DATABASE MODEL
# ============================================================
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

with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

# ============================================================
#  HTML TEMPLATE - PUT YOUR HTML HERE
# ============================================================
STUDY_HUB_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>Study Hub · powered by TWARVIS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,600;14..32,700;14..32,800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #000; min-height: 100vh; overflow-x: hidden; color: #e0e0e0; }
        #matrix-canvas { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; background: #000000; pointer-events: none; }
        .glass-overlay { position: relative; z-index: 2; background: transparent; min-height: 100vh; width: 100%; padding: 0 20px 40px; }
        .header { background: rgba(0, 0, 0, 0.5); border-bottom: 1px solid rgba(255, 45, 45, 0.5); position: sticky; top: 0; z-index: 100; padding: 8px 0; backdrop-filter: blur(2px); }
        .header-content { max-width: 1400px; margin: 0 auto; padding: 8px 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
        .logo-group { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
        .logo-main { font-size: 1.6rem; font-weight: 800; background: linear-gradient(135deg, #ff1a1a, #00cc33); -webkit-background-clip: text; background-clip: text; color: transparent; letter-spacing: -0.5px; }
        .logo-lightning { font-size: 0.75rem; font-weight: 300; color: #ff4d4d; letter-spacing: 1px; text-transform: uppercase; background: rgba(255, 0, 0, 0.1); padding: 2px 12px; border-radius: 40px; border: 1px solid rgba(255, 45, 45, 0.3); }
        .nav-links { display: flex; gap: 12px; flex-wrap: wrap; }
        .nav-icon { background: rgba(0, 0, 0, 0.6); border: 1px solid rgba(255, 45, 45, 0.5); border-radius: 50%; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; transition: all 0.2s ease; cursor: pointer; position: relative; }
        .nav-icon::before { content: attr(data-label); position: absolute; bottom: -30px; left: 50%; transform: translateX(-50%); background: rgba(0, 0, 0, 0.8); color: #00ff41; font-size: 0.7rem; padding: 4px 10px; border-radius: 20px; white-space: nowrap; opacity: 0; visibility: hidden; transition: all 0.2s; pointer-events: none; border: 1px solid #ff2d2d; font-weight: 500; }
        .nav-icon:hover::before { opacity: 1; visibility: visible; bottom: -35px; }
        .nav-icon:hover { transform: translateY(-2px) scale(1.05); background: rgba(255, 45, 45, 0.3); border-color: #ff1a1a; box-shadow: 0 0 12px rgba(255, 26, 26, 0.4); }
        .nav-icon a { text-decoration: none; color: #ff4d4d; font-size: 1.3rem; transition: all 0.2s; }
        .nav-icon:hover a { color: #fff; }
        .hero { text-align: center; padding: 50px 20px 30px; animation: fadeInUp 0.5s ease; }
        .hero h1 { font-size: 2.6rem; font-weight: 800; background: linear-gradient(135deg, #fff, #ff3333, #00ff44); -webkit-background-clip: text; background-clip: text; color: transparent; margin-bottom: 15px; }
        .hero p { color: #ddd; font-size: 1.1rem; max-width: 600px; margin: 0 auto; font-weight: 400; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; max-width: 1000px; margin: 30px auto 40px; padding: 0 12px; }
        .stat-card { background: rgba(0, 0, 0, 0.6); border: 1px solid rgba(255, 45, 45, 0.35); border-radius: 40px; padding: 20px; text-align: center; transition: all 0.2s; box-shadow: 0 4px 12px rgba(0,0,0,0.4); cursor: pointer; }
        .stat-card:hover { border-color: #ff3366; transform: translateY(-3px); box-shadow: 0 0 15px rgba(255, 51, 102, 0.2); }
        .stat-number { font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, #ff3366, #00ff55); -webkit-background-clip: text; background-clip: text; color: transparent; font-family: 'Inter', sans-serif; }
        .stat-label { color: #cc8888; font-size: 0.85rem; margin-top: 5px; font-weight: 500; }
        .tabs { display: flex; gap: 10px; margin-bottom: 25px; background: rgba(0,0,0,0.7); padding: 10px; border-radius: 60px; backdrop-filter: blur(4px); border: 1px solid #330000; max-width: 500px; margin-left: auto; margin-right: auto; }
        .tab { flex: 1; padding: 12px 20px; border: none; background: transparent; font-size: 1rem; font-weight: 600; cursor: pointer; border-radius: 50px; transition: all 0.3s; color: #aa8888; }
        .tab.active { background: linear-gradient(135deg, #cc0033 0%, #990022 100%); color: white; box-shadow: 0 0 10px rgba(204,0,51,0.6); }
        .resource-section { max-width: 1300px; margin: 40px auto; padding: 0 16px; }
        .section-title { font-size: 1.8rem; font-weight: 800; text-align: center; margin-bottom: 30px; background: linear-gradient(135deg, #ff4444, #00ff55); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .resource-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px; }
        .resource-card { background: rgba(10, 10, 10, 0.8); border-radius: 28px; padding: 20px; transition: all 0.3s; border: 1px solid #2a1a1a; box-shadow: 0 8px 20px rgba(0,0,0,0.5); }
        .resource-card:hover { transform: translateY(-5px); border-color: #cc0033; box-shadow: 0 0 20px rgba(204,0,51,0.2); }
        .resource-icon { font-size: 2.5rem; margin-bottom: 10px; color: #ff3366; }
        .resource-title { font-size: 1.2rem; font-weight: 700; color: #ffaaaa; margin-bottom: 8px; }
        .resource-desc { color: #aa8888; font-size: 0.85rem; margin-bottom: 12px; line-height: 1.4; }
        .resource-meta { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; padding-top: 12px; border-top: 1px solid #2a1a1a; font-size: 0.75rem; color: #885555; flex-wrap: wrap; gap: 8px; }
        .download-link { background: linear-gradient(135deg, #cc0033 0%, #990022 100%); color: white; padding: 6px 14px; border-radius: 25px; text-decoration: none; font-size: 0.8rem; font-weight: 600; transition: all 0.3s; display: inline-flex; align-items: center; gap: 5px; }
        .download-link:hover { transform: scale(1.05); background: #ff3366; }
        .empty-state { text-align: center; padding: 60px; background: rgba(0,0,0,0.5); border-radius: 30px; border: 1px dashed #cc0033; }
        .empty-state i { font-size: 3rem; color: #cc0033; margin-bottom: 15px; }
        .empty-state h3 { color: #ffaaaa; margin-bottom: 10px; }
        .empty-state p { color: #aa8888; }
        .upload-btn { position: fixed; bottom: 30px; right: 30px; background: linear-gradient(135deg, #cc0033 0%, #990022 100%); color: white; border: none; padding: 18px 28px; border-radius: 50px; font-size: 1rem; font-weight: 600; cursor: pointer; z-index: 100; display: flex; align-items: center; gap: 10px; box-shadow: 0 10px 30px rgba(204,0,51,0.5); transition: all 0.3s; }
        .upload-btn:hover { transform: scale(1.05); box-shadow: 0 0 20px #ff3366; }
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); backdrop-filter: blur(8px); }
        .modal-content { background: #111111; margin: 8% auto; padding: 30px; border-radius: 24px; width: 90%; max-width: 550px; position: relative; animation: slideIn 0.3s; border: 1px solid #cc0033; box-shadow: 0 0 30px rgba(204,0,51,0.3); }
        @keyframes slideIn { from { transform: translateY(-50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        .close { position: absolute; right: 20px; top: 20px; font-size: 28px; cursor: pointer; color: #aa5555; transition: 0.2s; }
        .close:hover { color: #ff6688; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #ffaaaa; }
        .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 12px; background: #1a1a1a; border: 1px solid #440022; border-radius: 12px; font-size: 1rem; color: #fff; transition: border 0.3s; }
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: #ff3366; }
        .submit-btn { width: 100%; padding: 14px; background: linear-gradient(135deg, #cc0033 0%, #990022 100%); color: white; border: none; border-radius: 12px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.3s; }
        .submit-btn:hover { transform: scale(1.02); box-shadow: 0 0 12px #ff3366; }
        .admin-secret-area { position: fixed; bottom: 10px; left: 10px; width: 50px; height: 50px; opacity: 0; cursor: pointer; z-index: 200; background: transparent; }
        .admin-overview-list { max-height: 400px; overflow-y: auto; margin: 15px 0; }
        .admin-item { background: #1f1f1f; margin: 8px 0; padding: 12px; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; border-left: 3px solid #cc0033; flex-wrap: wrap; gap: 8px; }
        .admin-item-info { flex: 1; }
        .admin-item-info strong { color: #ff8888; }
        .admin-item-info small { color: #886666; display: block; font-size: 0.7rem; }
        .admin-item-actions button { background: #330000; border: none; color: #ff7777; padding: 6px 12px; margin-left: 8px; border-radius: 20px; cursor: pointer; transition: 0.2s; }
        .admin-item-actions button:hover { background: #cc0033; color: white; }
        .badge-admin { font-size: 0.7rem; background: #330000; padding: 2px 8px; border-radius: 20px; margin-left: 8px; color: #ff8888; }
        .toast { position: fixed; bottom: 100px; right: 30px; background: #1a1a1a; border: 1px solid #cc0033; color: #ffaaaa; padding: 12px 20px; border-radius: 10px; box-shadow: 0 5px 20px rgba(0,0,0,0.5); z-index: