import os
import uuid
from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

# Django settings configuration
from django.conf import settings

settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'if0_41787435_1233',   # create this in InfinityFree panel
            'USER': 'if0_41787435',              # your InfinityFree username
            'PASSWORD': 'OCzpJa0yjiF9id2',       # your InfinityFree password
            'HOST': 'sql310.infinityfree.com',   # your InfinityFree MySQL host
            'PORT': '3306',
        }
    },
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'notes',  # your notes app
    ],
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'twarvis-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///twarvis.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

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

with app.app_context():
    db.create_all()

# ============ MATRIX THEME HTML TEMPLATE ============
TWARVIS_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>TWARVIS | Matrix Notes & Past Papers Hub</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', 'Share Tech Mono', monospace;
            background: #000000;
            min-height: 100vh;
            color: #e0e0e0;
        }

        #matrix-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            opacity: 0.3;
            pointer-events: none;
        }

        .container {
            position: relative;
            z-index: 1;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: rgba(10, 10, 10, 0.92);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(220, 20, 60, 0.4);
            border-radius: 24px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 40px rgba(0,0,0,0.6), 0 0 15px rgba(255, 0, 0, 0.2);
        }

        .logo {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #ff3366 0%, #cc0033 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -1px;
            text-shadow: 0 0 5px rgba(255,0,0,0.3);
        }

        .tagline {
            color: #ff4444;
            margin-top: 10px;
            font-size: 1rem;
            font-family: 'Share Tech Mono', monospace;
            letter-spacing: 1px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(8px);
            border: 1px solid #cc0033;
            padding: 20px;
            border-radius: 16px;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(204,0,51,0.2);
        }

        .stat-card:hover {
            transform: translateY(-5px);
            border-color: #ff3366;
            box-shadow: 0 0 15px rgba(255,51,102,0.4);
        }

        .stat-number {
            font-size: 2rem;
            font-weight: 800;
            color: #ff3366;
            font-family: 'Share Tech Mono', monospace;
        }

        .stat-label {
            color: #cc8888;
            font-size: 0.85rem;
            margin-top: 5px;
        }

        .upload-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(135deg, #cc0033 0%, #990022 100%);
            color: white;
            border: none;
            padding: 18px 28px;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            z-index: 100;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 10px 30px rgba(204,0,51,0.5);
            transition: all 0.3s;
        }

        .upload-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px #ff3366;
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            background: rgba(0,0,0,0.85);
            padding: 10px;
            border-radius: 60px;
            backdrop-filter: blur(10px);
            border: 1px solid #330000;
        }

        .tab {
            flex: 1;
            padding: 12px 20px;
            border: none;
            background: transparent;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            border-radius: 50px;
            transition: all 0.3s;
            color: #aa8888;
        }

        .tab.active {
            background: linear-gradient(135deg, #cc0033 0%, #990022 100%);
            color: white;
            box-shadow: 0 0 10px rgba(204,0,51,0.6);
        }

        .resource-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 20px;
        }

        .resource-card {
            background: #0a0a0a;
            border-radius: 18px;
            padding: 20px;
            transition: all 0.3s;
            border: 1px solid #2a1a1a;
            box-shadow: 0 8px 20px rgba(0,0,0,0.5);
        }

        .resource-card:hover {
            transform: translateY(-5px);
            border-color: #cc0033;
            box-shadow: 0 0 20px rgba(204,0,51,0.3);
        }

        .resource-icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
            color: #ff3366;
        }

        .resource-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #ffaaaa;
            margin-bottom: 8px;
        }

        .resource-desc {
            color: #aa8888;
            font-size: 0.85rem;
            margin-bottom: 12px;
            line-height: 1.4;
        }

        .resource-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #2a1a1a;
            font-size: 0.75rem;
            color: #885555;
        }

        .download-link {
            background: linear-gradient(135deg, #cc0033 0%, #990022 100%);
            color: white;
            padding: 6px 14px;
            border-radius: 25px;
            text-decoration: none;
            font-size: 0.8rem;
            font-weight: 600;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }

        .download-link:hover {
            transform: scale(1.05);
            background: #ff3366;
        }

        .admin-badge {
            display: none;
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            backdrop-filter: blur(8px);
        }

        .modal-content {
            background: #111111;
            margin: 8% auto;
            padding: 30px;
            border-radius: 24px;
            width: 90%;
            max-width: 550px;
            position: relative;
            animation: slideIn 0.3s;
            border: 1px solid #cc0033;
            box-shadow: 0 0 30px rgba(204,0,51,0.3);
        }

        @keyframes slideIn {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .close {
            position: absolute;
            right: 20px;
            top: 20px;
            font-size: 28px;
            cursor: pointer;
            color: #aa5555;
        }

        .close:hover {
            color: #ff6688;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #ffaaaa;
        }

        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 12px;
            background: #1a1a1a;
            border: 1px solid #440022;
            border-radius: 12px;
            font-size: 1rem;
            color: #fff;
            transition: border 0.3s;
        }

        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none;
            border-color: #ff3366;
        }

        .submit-btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #cc0033 0%, #990022 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }

        .submit-btn:hover {
            transform: scale(1.02);
            box-shadow: 0 0 12px #ff3366;
        }

        .empty-state {
            text-align: center;
            padding: 60px;
            background: #0a0a0a;
            border-radius: 24px;
            border: 1px dashed #cc0033;
        }

        .empty-state i {
            font-size: 3rem;
            color: #cc0033;
            margin-bottom: 15px;
        }

        .footer {
            text-align: center;
            padding: 30px;
            color: #993333;
            margin-top: 30px;
            font-size: 0.8rem;
        }

        .admin-secret-area {
            position: fixed;
            bottom: 10px;
            left: 10px;
            width: 50px;
            height: 50px;
            opacity: 0;
            cursor: pointer;
            z-index: 200;
            background: transparent;
        }

        .admin-overview-list {
            max-height: 400px;
            overflow-y: auto;
            margin: 15px 0;
        }

        .admin-item {
            background: #1f1f1f;
            margin: 8px 0;
            padding: 12px;
            border-radius: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-left: 3px solid #cc0033;
        }

        .admin-item-info {
            flex: 1;
        }

        .admin-item-info strong {
            color: #ff8888;
        }

        .admin-item-info small {
            color: #886666;
            display: block;
            font-size: 0.7rem;
        }

        .admin-item-actions button {
            background: #330000;
            border: none;
            color: #ff7777;
            padding: 6px 12px;
            margin-left: 8px;
            border-radius: 20px;
            cursor: pointer;
            transition: 0.2s;
        }

        .admin-item-actions button:hover {
            background: #cc0033;
            color: white;
        }

        .badge-admin {
            font-size: 0.7rem;
            background: #330000;
            padding: 2px 8px;
            border-radius: 20px;
            margin-left: 8px;
            color: #ff8888;
        }

        .toast {
            position: fixed;
            bottom: 100px;
            right: 30px;
            background: #1a1a1a;
            border: 1px solid #cc0033;
            color: #ffaaaa;
            padding: 12px 20px;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.5);
            z-index: 1000;
            animation: slideInRight 0.3s;
        }

        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        @media (max-width: 768px) {
            .container { padding: 15px; }
            .logo { font-size: 2rem; }
            .upload-btn { padding: 12px 20px; font-size: 0.85rem; }
            .resource-grid { grid-template-columns: 1fr; }
            .modal-content { margin: 20% auto; padding: 20px; }
        }
    </style>
</head>
<body>
    <canvas id="matrix-canvas"></canvas>

    <div class="container">
        <div class="header">
            <h1 class="logo">⚡ TWARVIS | MATRIX</h1>
            <p class="tagline">〈 RED RAIN 〉 Free Notes & Past Papers | Upload & Share Anonymously</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="totalNotes">0</div>
                <div class="stat-label">📘 Study Notes</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalPapers">0</div>
                <div class="stat-label">📄 Past Papers</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalDownloads">0</div>
                <div class="stat-label">⬇️ Total Downloads</div>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('notes')">📘 Notes</button>
            <button class="tab" onclick="switchTab('papers')">📄 Past Papers</button>
        </div>

        <div id="notesSection">
            <div class="resource-grid" id="notesGrid">
                {% for note in notes %}
                <div class="resource-card" data-id="{{ note.id }}">
                    <div class="resource-icon">📘</div>
                    <div class="resource-title">{{ note.title }}</div>
                    <div class="resource-desc">{{ note.description or 'No description' }}</div>
                    <div class="resource-meta">
                        <span><i class="far fa-calendar"></i> {{ note.created_at.strftime('%b %d, %Y') if note.created_at else 'Recent' }}</span>
                        <span><i class="fas fa-download"></i> {{ note.downloads }}</span>
                        <a href="/download/{{ note.id }}" class="download-link"><i class="fas fa-download"></i> Download</a>
                    </div>
                </div>
                {% else %}
                <div class="empty-state">
                    <i class="fas fa-dragon"></i>
                    <h3>No notes yet</h3>
                    <p>Be the first to upload study notes!</p>
                </div>
                {% endfor %}
            </div>
        </div>

        <div id="papersSection" style="display: none;">
            <div class="resource-grid" id="papersGrid">
                {% for paper in pastpapers %}
                <div class="resource-card" data-id="{{ paper.id }}">
                    <div class="resource-icon">📄</div>
                    <div class="resource-title">{{ paper.title }}</div>
                    <div class="resource-desc">{{ paper.description or 'Past examination paper' }}</div>
                    <div class="resource-meta">
                        <span><i class="far fa-calendar"></i> {{ paper.created_at.strftime('%b %d, %Y') if paper.created_at else 'Recent' }}</span>
                        <span><i class="fas fa-download"></i> {{ paper.downloads }}</span>
                        <a href="/download/{{ paper.id }}" class="download-link"><i class="fas fa-download"></i> Download</a>
                    </div>
                </div>
                {% else %}
                <div class="empty-state">
                    <i class="fas fa-dragon"></i>
                    <h3>No past papers yet</h3>
                    <p>Upload past papers to help others prepare!</p>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="footer">
            <p>⚡ TWARVIS — Free Educational Resource Hub | Anonymous Upload | Knowledge is Power</p>
        </div>
    </div>

    <button class="upload-btn" onclick="openUploadModal()">
        <i class="fas fa-cloud-upload-alt"></i> Upload Notes / Past Paper
    </button>

    <!-- Hidden Admin Portal Trigger -->
    <div id="adminSecretZone" class="admin-secret-area" title=""></div>

    <!-- Upload Modal -->
    <div id="uploadModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeUploadModal()">&times;</span>
            <h2 style="margin-bottom: 20px; color:#ff6688;"><i class="fas fa-upload"></i> Share Your Resources</h2>
            <form method="POST" action="/upload" enctype="multipart/form-data" onsubmit="return validateForm()">
                <div class="form-group">
                    <label>Resource Type</label>
                    <select name="type" required>
                        <option value="note">📘 Study Note</option>
                        <option value="pastpaper">📄 Past Paper</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Title</label>
                    <input type="text" name="title" placeholder="e.g., Calculus II Final Exam Notes" required>
                </div>
                <div class="form-group">
                    <label>Description (optional)</label>
                    <textarea name="description" rows="3" placeholder="Brief description of this resource..."></textarea>
                </div>
                <div class="form-group">
                    <label>PDF/DOC/DOCX File (Max 50MB)</label>
                    <input type="file" name="file" accept=".pdf,.doc,.docx" required>
                </div>
                <button type="submit" class="submit-btn"><i class="fas fa-cloud-upload-alt"></i> Publish Resource</button>
            </form>
        </div>
    </div>

    <!-- Admin Modal -->
    <div id="adminModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeAdminModal()">&times;</span>
            <h2 style="color:#ff6688;"><i class="fas fa-user-secret"></i> Admin Portal</h2>
            <div id="adminAuthPanel">
                <div class="form-group">
                    <label>Master Passcode</label>
                    <input type="password" id="adminPass" placeholder="Enter passcode">
                </div>
                <button onclick="verifyAdmin()" class="submit-btn">Authenticate</button>
            </div>
            <div id="adminOverviewPanel" style="display:none;">
                <h3>📦 All Resources Overview</h3>
                <div id="adminResourcesList" class="admin-overview-list"></div>
                <button onclick="logoutAdmin()" class="submit-btn" style="background:#330000;">Close Panel</button>
            </div>
        </div>
    </div>

    <!-- Edit Modal -->
    <div id="editModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeEditModal()">&times;</span>
            <h3 style="color:#ff6688;">✏️ Edit Resource</h3>
            <form id="editForm">
                <input type="hidden" id="editId">
                <div class="form-group">
                    <label>Title</label>
                    <input type="text" id="editTitle" required>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea id="editDesc" rows="2"></textarea>
                </div>
                <div class="form-group">
                    <label>Type</label>
                    <select id="editType">
                        <option value="note">📘 Study Note</option>
                        <option value="pastpaper">📄 Past Paper</option>
                    </select>
                </div>
                <button type="submit" class="submit-btn">Save Changes</button>
            </form>
        </div>
    </div>

    <script>
        // Matrix Rain Effect - RED VERSION
        const canvas = document.getElementById('matrix-canvas');
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        const chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン";
        const fontSize = 16;
        let drops = [];

        function initMatrix() {
            const columns = Math.ceil(canvas.width / fontSize);
            drops = Array(columns).fill(1).map(() => Math.random() * -100);
        }

        function drawMatrix() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.07)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#ff1a4f';
            ctx.font = `bold ${fontSize}px 'Share Tech Mono'`;
            for (let i = 0; i < drops.length; i++) {
                const text = chars.charAt(Math.floor(Math.random() * chars.length));
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }
        }

        initMatrix();
        setInterval(drawMatrix, 45);
        window.addEventListener('resize', initMatrix);

        // Tab Switching
        function switchTab(tab) {
            const notesSection = document.getElementById('notesSection');
            const papersSection = document.getElementById('papersSection');
            const tabs = document.querySelectorAll('.tab');
            
            if (tab === 'notes') {
                notesSection.style.display = 'block';
                papersSection.style.display = 'none';
                tabs[0].classList.add('active');
                tabs[1].classList.remove('active');
            } else {
                notesSection.style.display = 'none';
                papersSection.style.display = 'block';
                tabs[0].classList.remove('active');
                tabs[1].classList.add('active');
            }
        }

        // Modal Functions
        function openUploadModal() {
            document.getElementById('uploadModal').style.display = 'block';
        }

        function closeUploadModal() {
            document.getElementById('uploadModal').style.display = 'none';
        }

        function closeAdminModal() {
            document.getElementById('adminModal').style.display = 'none';
            document.getElementById('adminAuthPanel').style.display = 'block';
            document.getElementById('adminOverviewPanel').style.display = 'none';
            document.getElementById('adminPass').value = '';
            window.adminLogged = false;
        }

        function closeEditModal() {
            document.getElementById('editModal').style.display = 'none';
        }

        window.onclick = function(event) {
            if (event.target == document.getElementById('uploadModal')) closeUploadModal();
            if (event.target == document.getElementById('adminModal')) closeAdminModal();
            if (event.target == document.getElementById('editModal')) closeEditModal();
        }

        // Form Validation
        function validateForm() {
            const title = document.querySelector('input[name="title"]').value;
            const file = document.querySelector('input[name="file"]').value;
            if (!title || !file) {
                alert('Please fill in title and select a file');
                return false;
            }
            return true;
        }

        // Load Statistics
        async function loadStats() {
            try {
                const response = await fetch('/statistics');
                const data = await response.json();
                document.getElementById('totalNotes').textContent = data.notes;
                document.getElementById('totalPapers').textContent = data.pastpapers;
                document.getElementById('totalDownloads').textContent = data.downloads;
            } catch(e) {
                console.error('Stats error:', e);
            }
        }

        loadStats();
        setInterval(loadStats, 15000);

        // Show success message
        if (window.location.search.includes('success')) {
            showToast('✅ Upload successful!');
        }

        function showToast(message) {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.innerHTML = '<i class="fas fa-check-circle"></i> ' + message;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }

        // ============ ADMIN PORTAL (Hidden - 5 clicks on secret area) ============
        let clickCount = 0;
        let clickTimer;
        const secretZone = document.getElementById('adminSecretZone');
        const ADMIN_PASS = "MatrixAdmin2025";
        let adminLogged = false;
        window.adminLogged = false;

        secretZone.addEventListener('click', () => {
            clickCount++;
            if (clickTimer) clearTimeout(clickTimer);
            clickTimer = setTimeout(() => { clickCount = 0; }, 800);
            if (clickCount >= 5) {
                document.getElementById('adminModal').style.display = 'block';
                clickCount = 0;
            }
        });

        function verifyAdmin() {
            const entered = document.getElementById('adminPass').value;
            if (entered === ADMIN_PASS) {
                adminLogged = true;
                window.adminLogged = true;
                document.getElementById('adminAuthPanel').style.display = 'none';
                document.getElementById('adminOverviewPanel').style.display = 'block';
                loadAdminOverview();
            } else {
                alert("❌ Invalid passcode. Access denied.");
            }
        }

        function logoutAdmin() {
            adminLogged = false;
            window.adminLogged = false;
            closeAdminModal();
        }

        async function loadAdminOverview() {
            const response = await fetch('/admin/resources');
            const resources = await response.json();
            const listDiv = document.getElementById('adminResourcesList');
            
            if (resources.length === 0) {
                listDiv.innerHTML = '<div class="empty-state">No resources found</div>';
                return;
            }
            
            listDiv.innerHTML = resources.map(r => `
                <div class="admin-item">
                    <div class="admin-item-info">
                        <strong>${escapeHtml(r.title)}</strong>
                        <span class="badge-admin">${r.category === 'note' ? '📘 Note' : '📄 Paper'}</span>
                        <small>⬇️ ${r.downloads} downloads | ${r.file_size ? (r.file_size/1024).toFixed(1) : 0} KB | ID: ${r.id}</small>
                        <small style="color:#886666;">${escapeHtml(r.description || 'No description')}</small>
                    </div>
                    <div class="admin-item-actions">
                        <button onclick="editResource(${r.id})"><i class="fas fa-edit"></i> Edit</button>
                        <button onclick="deleteResource(${r.id})"><i class="fas fa-trash"></i> Delete</button>
                    </div>
                </div>
            `).join('');
        }

        async function deleteResource(id) {
            if (confirm('⚠️ PERMANENT DELETE: This action cannot be undone. Delete this resource?')) {
                const response = await fetch(`/admin/delete/${id}`, { method: 'DELETE' });
                if (response.ok) {
                    showToast('🗑️ Resource deleted successfully');
                    loadAdminOverview();
                    location.reload();
                } else {
                    alert('Delete failed');
                }
            }
        }

        async function editResource(id) {
            const response = await fetch(`/admin/resource/${id}`);
            const resource = await response.json();
            document.getElementById('editId').value = resource.id;
            document.getElementById('editTitle').value = resource.title;
            document.getElementById('editDesc').value = resource.description || '';
            document.getElementById('editType').value = resource.category;
            document.getElementById('editModal').style.display = 'block';
        }

        document.getElementById('editForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('editId').value;
            const data = {
                title: document.getElementById('editTitle').value,
                description: document.getElementById('editDesc').value,
                category: document.getElementById('editType').value
            };
            const response = await fetch(`/admin/update/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (response.ok) {
                showToast('✏️ Resource updated successfully');
                closeEditModal();
                loadAdminOverview();
                location.reload();
            } else {
                alert('Update failed');
            }
        });

        function escapeHtml(str) {
            if (!str) return '';
            return str.replace(/[&<>]/g, function(m) {
                if (m === '&') return '&amp;';
                if (m === '<') return '&lt;';
                if (m === '>') return '&gt;';
                return m;
            });
        }
    </script>
</body>
</html>
'''

# ============ ROUTES ============
@app.route('/')
def index():
    notes = Note.query.filter_by(category='note').order_by(Note.created_at.desc()).all()
    pastpapers = Note.query.filter_by(category='pastpaper').order_by(Note.created_at.desc()).all()
    return render_template_string(TWARVIS_HTML, notes=notes, pastpapers=pastpapers)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return "No file", 400
        
        file = request.files['file']
        if file.filename == '':
            return "No file selected", 400
        
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        category = request.form.get('type', 'note')
        
        if title == '':
            return "Title required", 400
        
        original_name = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{original_name}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(file_path)
        
        file_size = os.path.getsize(file_path)
        
        note = Note(
            title=title,
            description=description,
            category=category,
            filename=unique_name,
            original_name=original_name,
            file_size=file_size
        )
        db.session.add(note)
        db.session.commit()
        
        return redirect(url_for('index') + '?success=1')
    except Exception as e:
        return f"Upload failed: {str(e)}", 500

@app.route('/download/<int:id>')
def download_file(id):
    note = Note.query.get_or_404(id)
    note.downloads += 1
    db.session.commit()
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        note.filename,
        as_attachment=True,
        download_name=note.original_name
    )

# Admin routes (protected with secret key, but frontend handles passcode)
@app.route('/admin/resources')
def admin_resources():
    resources = Note.query.order_by(Note.created_at.desc()).all()
    return jsonify([{
        'id': r.id,
        'title': r.title,
        'description': r.description,
        'category': r.category,
        'downloads': r.downloads,
        'file_size': r.file_size,
        'created_at': r.created_at.isoformat() if r.created_at else None
    } for r in resources])

@app.route('/admin/resource/<int:id>')
def admin_get_resource(id):
    note = Note.query.get_or_404(id)
    return jsonify({
        'id': note.id,
        'title': note.title,
        'description': note.description,
        'category': note.category
    })

@app.route('/admin/update/<int:id>', methods=['PUT'])
def admin_update_resource(id):
    note = Note.query.get_or_404(id)
    data = request.get_json()
    note.title = data.get('title', note.title)
    note.description = data.get('description', note.description)
    note.category = data.get('category', note.category)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/delete/<int:id>', methods=['DELETE'])
def admin_delete_resource(id):
    note = Note.query.get_or_404(id)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], note.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(note)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/statistics')
def statistics():
    total_notes = Note.query.filter_by(category='note').count()
    total_papers = Note.query.filter_by(category='pastpaper').count()
    total_downloads = db.session.query(db.func.sum(Note.downloads)).scalar() or 0
    return jsonify({'notes': total_notes, 'pastpapers': total_papers, 'downloads': total_downloads})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
