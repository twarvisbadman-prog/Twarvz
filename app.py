import os
import uuid
from flask import Flask, request, render_template_string, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

app = Flask(__name__)

# ============================================================
#  FIXED DATABASE CONFIGURATION - CRITICAL FIX!
# ============================================================
# Get database URL from environment or use default
database_url = os.environ.get('DATABASE_URL', 'mysql+pymysql://if0_41787435:OCzpJa0yjiF9id2@sql310.infinityfree.com:3306/if0_41787435_1233')

# IMPORTANT: Ensure it starts with mysql+pymysql:// not mysql://
if database_url.startswith('mysql://'):
    database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'twarvis-secret-key-2024')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Create uploads folder
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

# Create tables
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

# ============================================================
#  HTML TEMPLATE (YOUR STUDY HUB DESIGN)
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
        .toast { position: fixed; bottom: 100px; right: 30px; background: #1a1a1a; border: 1px solid #cc0033; color: #ffaaaa; padding: 12px 20px; border-radius: 10px; box-shadow: 0 5px 20px rgba(0,0,0,0.5); z-index: 1000; animation: slideInRight 0.3s; }
        @keyframes slideInRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        .loading { text-align: center; padding: 40px; color: #ff6688; }
        .footer { text-align: center; padding: 30px; color: #993333; margin-top: 30px; font-size: 0.8rem; }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @media (max-width: 768px) { 
            .hero h1 { font-size: 1.8rem; } 
            .header-content { flex-direction: column; text-align: center; } 
            .upload-btn { padding: 12px 20px; font-size: 0.85rem; } 
            .resource-grid { grid-template-columns: 1fr; } 
            .modal-content { margin: 20% auto; padding: 20px; }
            .stats { grid-template-columns: repeat(3, 1fr); }
            .admin-item { flex-direction: column; }
            .admin-item-actions { width: 100%; display: flex; justify-content: flex-end; }
        }
    </style>
</head>
<body>
    <canvas id="matrix-canvas"></canvas>
    <div class="glass-overlay">
        <div class="header">
            <div class="header-content">
                <div class="logo-group">
                    <span class="logo-main">⚡ STUDY HUB</span>
                    <span class="logo-lightning">⚡ powered by twarvis</span>
                </div>
                <div class="nav-links">
                    <div class="nav-icon" data-label="Home"><a href="/"><i class="fas fa-home"></i></a></div>
                    <div class="nav-icon" data-label="Browse"><a href="#" id="browseNav"><i class="fas fa-book-open"></i></a></div>
                    <div class="nav-icon" data-label="Upload"><a href="#" id="uploadNav"><i class="fas fa-cloud-upload-alt"></i></a></div>
                </div>
            </div>
        </div>
        <div class="hero">
            <h1>WELCOME TO STUDY HUB</h1>
            <p>Upload, browse, and dominate your studies — powered by the matrix.</p>
        </div>
        <div class="stats">
            <div class="stat-card"><div class="stat-number" id="totalNotes">0</div><div class="stat-label">📘 Study Notes</div></div>
            <div class="stat-card"><div class="stat-number" id="totalPapers">0</div><div class="stat-label">📄 Past Papers</div></div>
            <div class="stat-card"><div class="stat-number" id="totalDownloads">0</div><div class="stat-label">⬇️ Total Downloads</div></div>
        </div>
        <div class="resource-section">
            <div class="section-title">📚 RESOURCE LIBRARY</div>
            <div class="tabs">
                <button class="tab active" onclick="switchTab('notes')">📘 Notes</button>
                <button class="tab" onclick="switchTab('papers')">📄 Past Papers</button>
            </div>
            <div id="notesSection">
                <div class="resource-grid" id="notesGrid"><div class="loading"><i class="fas fa-spinner fa-spin"></i> Loading notes...</div></div>
            </div>
            <div id="papersSection" style="display: none;">
                <div class="resource-grid" id="papersGrid"><div class="loading"><i class="fas fa-spinner fa-spin"></i> Loading past papers...</div></div>
            </div>
        </div>
        <div class="footer"><p>⚡ Study Hub — powered by TWARVIS · Free Educational Resource Hub</p></div>
    </div>
    <button class="upload-btn" onclick="openUploadModal()"><i class="fas fa-cloud-upload-alt"></i> Upload Notes / Past Paper</button>
    <div id="adminSecretZone" class="admin-secret-area" title=""></div>
    <div id="uploadModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeUploadModal()">&times;</span>
            <h2 style="margin-bottom: 20px; color:#ff6688;"><i class="fas fa-upload"></i> Share Your Resources</h2>
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="form-group"><label>Resource Type</label><select name="type" id="resourceType" required><option value="note">📘 Study Note</option><option value="pastpaper">📄 Past Paper</option></select></div>
                <div class="form-group"><label>Title</label><input type="text" name="title" id="resourceTitle" placeholder="e.g., Calculus II Final Exam Notes" required></div>
                <div class="form-group"><label>Description (optional)</label><textarea name="description" id="resourceDesc" rows="3" placeholder="Brief description of this resource..."></textarea></div>
                <div class="form-group"><label>PDF/DOC/DOCX File (Max 50MB)</label><input type="file" name="file" id="resourceFile" accept=".pdf,.doc,.docx" required></div>
                <button type="submit" class="submit-btn"><i class="fas fa-cloud-upload-alt"></i> Publish Resource</button>
            </form>
        </div>
    </div>
    <div id="adminModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeAdminModal()">&times;</span>
            <h2 style="color:#ff6688;"><i class="fas fa-user-secret"></i> Admin Portal</h2>
            <div id="adminAuthPanel"><div class="form-group"><label>Master Passcode</label><input type="password" id="adminPass" placeholder="Enter passcode"></div><button onclick="verifyAdmin()" class="submit-btn">Authenticate</button></div>
            <div id="adminOverviewPanel" style="display:none;"><h3>📦 All Resources Overview</h3><div id="adminResourcesList" class="admin-overview-list"></div><button onclick="logoutAdmin()" class="submit-btn" style="background:#330000;">Close Panel</button></div>
        </div>
    </div>
    <div id="editModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeEditModal()">&times;</span>
            <h3 style="color:#ff6688;">✏️ Edit Resource</h3>
            <form id="editForm">
                <input type="hidden" id="editId">
                <div class="form-group"><label>Title</label><input type="text" id="editTitle" required></div>
                <div class="form-group"><label>Description</label><textarea id="editDesc" rows="2"></textarea></div>
                <div class="form-group"><label>Type</label><select id="editType"><option value="note">📘 Study Note</option><option value="pastpaper">📄 Past Paper</option></select></div>
                <button type="submit" class="submit-btn">Save Changes</button>
            </form>
        </div>
    </div>
    <script>
        const canvas = document.getElementById('matrix-canvas');
        const ctx = canvas.getContext('2d');
        function resizeCanvas() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
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

        function openUploadModal() { document.getElementById('uploadModal').style.display = 'block'; }
        function closeUploadModal() { document.getElementById('uploadModal').style.display = 'none'; document.getElementById('uploadForm').reset(); }
        function closeAdminModal() { document.getElementById('adminModal').style.display = 'none'; document.getElementById('adminAuthPanel').style.display = 'block'; document.getElementById('adminOverviewPanel').style.display = 'none'; document.getElementById('adminPass').value = ''; window.adminLogged = false; }
        function closeEditModal() { document.getElementById('editModal').style.display = 'none'; }
        window.onclick = function(event) {
            if (event.target == document.getElementById('uploadModal')) closeUploadModal();
            if (event.target == document.getElementById('adminModal')) closeAdminModal();
            if (event.target == document.getElementById('editModal')) closeEditModal();
        }

        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData();
            formData.append('type', document.getElementById('resourceType').value);
            formData.append('title', document.getElementById('resourceTitle').value);
            formData.append('description', document.getElementById('resourceDesc').value);
            formData.append('file', document.getElementById('resourceFile').files[0]);
            try {
                const response = await fetch('/upload', { method: 'POST', body: formData });
                if (response.ok) {
                    showToast('✅ Upload successful!');
                    closeUploadModal();
                    loadResources();
                    loadStats();
                } else {
                    showToast('❌ Upload failed');
                }
            } catch (error) {
                showToast('❌ Error uploading file');
            }
        });

        async function loadResources() {
            try {
                const response = await fetch('/api/resources');
                const data = await response.json();
                const notes = data.filter(r => r.category === 'note');
                const papers = data.filter(r => r.category === 'pastpaper');
                renderGrid('notesGrid', notes);
                renderGrid('papersGrid', papers);
            } catch (error) {
                console.error('Error loading resources:', error);
            }
        }

        function renderGrid(gridId, items) {
            const container = document.getElementById(gridId);
            if (!container) return;
            if (items.length === 0) {
                container.innerHTML = `<div class="empty-state"><i class="fas fa-dragon"></i><h3>No resources yet</h3><p>Be the first to upload!</p></div>`;
                return;
            }
            container.innerHTML = items.map(item => `
                <div class="resource-card">
                    <div class="resource-icon">${item.category === 'note' ? '📘' : '📄'}</div>
                    <div class="resource-title">${escapeHtml(item.title)}</div>
                    <div class="resource-desc">${escapeHtml(item.description || 'No description')}</div>
                    <div class="resource-meta">
                        <span><i class="far fa-calendar"></i> ${formatDate(item.created_at)}</span>
                        <span><i class="fas fa-download"></i> ${item.downloads}</span>
                        <a href="/download/${item.id}" class="download-link"><i class="fas fa-download"></i> Download</a>
                    </div>
                </div>
            `).join('');
        }

        async function loadStats() {
            try {
                const response = await fetch('/statistics');
                const data = await response.json();
                document.getElementById('totalNotes').textContent = data.notes;
                document.getElementById('totalPapers').textContent = data.pastpapers;
                document.getElementById('totalDownloads').textContent = data.downloads;
            } catch(e) { console.error('Stats error:', e); }
        }

        function formatDate(dateStr) {
            if (!dateStr) return 'Recent';
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        }
        function escapeHtml(str) {
            if (!str) return '';
            return str.replace(/[&<>]/g, function(m) {
                if (m === '&') return '&amp;';
                if (m === '<') return '&lt;';
                if (m === '>') return '&gt;';
                return m;
            });
        }
        function showToast(message) {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.innerHTML = '<i class="fas fa-check-circle"></i> ' + message;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }

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
                    loadResources();
                    loadStats();
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
                loadResources();
                loadStats();
            } else {
                alert('Update failed');
            }
        });

        loadResources();
        loadStats();
        setInterval(loadStats, 15000);
    </script>
</body>
</html>
'''

# ============================================================
#  ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template_string(STUDY_HUB_HTML)

@app.route('/api/resources')
def get_resources():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'description': n.description,
        'category': n.category,
        'downloads': n.downloads,
        'created_at': n.created_at.isoformat() if n.created_at else None,
        'file_size': n.file_size
    } for n in notes])

@app.route('/statistics')
def get_statistics():
    notes_count = Note.query.filter_by(category='note').count()
    papers_count = Note.query.filter_by(category='pastpaper').count()
    total_downloads = db.session.query(db.func.sum(Note.downloads)).scalar() or 0
    return jsonify({
        'notes': notes_count,
        'pastpapers': papers_count,
        'downloads': total_downloads
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        category = request.form.get('type')
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files.get('file')
        
        if not file:
            return jsonify({'error': 'No file provided'}), 400
        
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        unique_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        
        # Save file
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Save to database
        note = Note(
            title=title,
            description=description,
            category=category,
            filename=unique_name,
            original_name=file.filename,
            file_size=file_size,
            downloads=0
        )
        db.session.add(note)
        db.session.commit()
        
        return jsonify({
            'id': note.id,
            'title': note.title,
            'description': note.description,
            'category': note.category,
            'downloads': note.downloads,
            'created_at': note.created_at.isoformat() if note.created_at else None,
            'file_size': note.file_size
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<int:note_id>')
def download_file(note_id):
    note = Note.query.get_or_404(note_id)
    
    # Increment downloads
    note.downloads += 1
    db.session.commit()
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], note.filename)
    if os.path.exists(file_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], note.filename, as_attachment=True, download_name=note.original_name)
    else:
        return jsonify({'error': 'File not found'}), 404

# ============================================================
#  ADMIN ROUTES
# ============================================================

@app.route('/admin/resources')
def admin_resources():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'description': n.description,
        'category': n.category,
        'downloads': n.downloads,
        'created_at': n.created_at.isoformat() if n.created_at else None,
        'file_size': n.file_size
    } for n in notes])

@app.route('/admin/resource/<int:note_id>')
def admin_get_resource(note_id):
    note = Note.query.get_or_404(note_id)
    return jsonify({
        'id': note.id,
        'title': note.title,
        'description': note.description,
        'category': note.category
    })

@app.route('/admin/update/<int:note_id>', methods=['PUT'])
def admin_update_resource(note_id):
    note = Note.query.get_or_404(note_id)
    data = request.json
    
    note.title = data.get('title', note.title)
    note.description = data.get('description', note.description)
    note.category = data.get('category', note.category)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/delete/<int:note_id>', methods=['DELETE'])
def admin_delete_resource(note_id):
    note = Note.query.get_or_404(note_id)
    
    # Delete file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], note.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(note)
    db.session.commit()
    return jsonify({'success': True})

# ============================================================
#  SERVE UPLOADED FILES
# ============================================================
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ============================================================
#  START SERVER
# ============================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)