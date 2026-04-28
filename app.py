import os
import uuid
from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

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

# ============ HTML TEMPLATE EMBEDDED IN PYTHON ============
TWARVIS_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>TWARVIS | Notes & Past Papers Hub</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #1a1a2e;
        }

        #matrix-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            opacity: 0.15;
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
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }

        .logo {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -1px;
        }

        .tagline {
            color: #666;
            margin-top: 10px;
            font-size: 1rem;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            transition: transform 0.3s;
            cursor: pointer;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-number {
            font-size: 2rem;
            font-weight: 800;
            color: #667eea;
        }

        .stat-label {
            color: #666;
            font-size: 0.85rem;
            margin-top: 5px;
        }

        .upload-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
            box-shadow: 0 10px 30px rgba(102,126,234,0.4);
            transition: all 0.3s;
        }

        .upload-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 15px 40px rgba(102,126,234,0.6);
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            background: rgba(255,255,255,0.95);
            padding: 10px;
            border-radius: 60px;
            backdrop-filter: blur(10px);
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
            color: #666;
        }

        .tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .resource-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
        }

        .resource-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            transition: all 0.3s;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        }

        .resource-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }

        .resource-icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        .resource-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 8px;
        }

        .resource-desc {
            color: #666;
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
            border-top: 1px solid #eee;
            font-size: 0.75rem;
            color: #999;
        }

        .download-link {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        }

        .delete-link {
            color: #dc3545;
            font-size: 0.75rem;
            text-decoration: none;
        }

        .delete-link:hover {
            text-decoration: underline;
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
        }

        .modal-content {
            background: white;
            margin: 10% auto;
            padding: 30px;
            border-radius: 20px;
            width: 90%;
            max-width: 500px;
            position: relative;
            animation: slideIn 0.3s;
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
            color: #999;
        }

        .close:hover {
            color: #333;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }

        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1rem;
            transition: border 0.3s;
        }

        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .submit-btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }

        .submit-btn:hover {
            transform: scale(1.02);
        }

        .empty-state {
            text-align: center;
            padding: 60px;
            background: white;
            border-radius: 20px;
        }

        .empty-state i {
            font-size: 3rem;
            color: #667eea;
            margin-bottom: 15px;
        }

        .footer {
            text-align: center;
            padding: 30px;
            color: white;
            margin-top: 30px;
        }

        @media (max-width: 768px) {
            .container { padding: 15px; }
            .logo { font-size: 2rem; }
            .upload-btn { padding: 12px 20px; font-size: 0.85rem; }
            .resource-grid { grid-template-columns: 1fr; }
            .modal-content { margin: 20% auto; padding: 20px; }
        }

        /* Toast Notification */
        .toast {
            position: fixed;
            bottom: 100px;
            right: 30px;
            background: white;
            color: #333;
            padding: 12px 20px;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            z-index: 1000;
            animation: slideInRight 0.3s;
        }

        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    </style>
</head>
<body>
    <canvas id="matrix-canvas"></canvas>

    <div class="container">
        <div class="header">
            <h1 class="logo">⚡ TWARVIS</h1>
            <p class="tagline">Free Notes & Past Papers Library | Upload & Download Anytime</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="totalNotes">0</div>
                <div class="stat-label">Study Notes</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalPapers">0</div>
                <div class="stat-label">Past Papers</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalDownloads">0</div>
                <div class="stat-label">Total Downloads</div>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('notes')">📘 Notes</button>
            <button class="tab" onclick="switchTab('papers')">📄 Past Papers</button>
        </div>

        <div id="notesSection">
            <div class="resource-grid">
                {% for note in notes %}
                <div class="resource-card">
                    <div class="resource-icon">📘</div>
                    <div class="resource-title">{{ note.title }}</div>
                    <div class="resource-desc">{{ note.description or 'No description' }}</div>
                    <div class="resource-meta">
                        <span><i class="far fa-calendar"></i> {{ note.created_at.strftime('%b %d, %Y') if note.created_at else 'Recent' }}</span>
                        <span><i class="fas fa-download"></i> {{ note.downloads }}</span>
                        <a href="/download/{{ note.id }}" class="download-link"><i class="fas fa-download"></i> PDF</a>
                    </div>
                    <div style="margin-top: 8px; text-align: right;">
                        <a href="/delete/{{ note.id }}" class="delete-link" onclick="return confirm('Delete this note?')"><i class="fas fa-trash"></i> Delete</a>
                    </div>
                </div>
                {% else %}
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <h3>No notes yet</h3>
                    <p>Be the first to upload study notes!</p>
                </div>
                {% endfor %}
            </div>
        </div>

        <div id="papersSection" style="display: none;">
            <div class="resource-grid">
                {% for paper in pastpapers %}
                <div class="resource-card">
                    <div class="resource-icon">📄</div>
                    <div class="resource-title">{{ paper.title }}</div>
                    <div class="resource-desc">{{ paper.description or 'Past examination paper' }}</div>
                    <div class="resource-meta">
                        <span><i class="far fa-calendar"></i> {{ paper.created_at.strftime('%b %d, %Y') if paper.created_at else 'Recent' }}</span>
                        <span><i class="fas fa-download"></i> {{ paper.downloads }}</span>
                        <a href="/download/{{ paper.id }}" class="download-link"><i class="fas fa-download"></i> PDF</a>
                    </div>
                    <div style="margin-top: 8px; text-align: right;">
                        <a href="/delete/{{ paper.id }}" class="delete-link" onclick="return confirm('Delete this past paper?')"><i class="fas fa-trash"></i> Delete</a>
                    </div>
                </div>
                {% else %}
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <h3>No past papers yet</h3>
                    <p>Upload past papers to help others prepare!</p>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="footer">
            <p>📚 TWARVIS - Free Educational Resource Hub | Upload & Share Knowledge</p>
        </div>
    </div>

    <button class="upload-btn" onclick="openUploadModal()">
        <i class="fas fa-cloud-upload-alt"></i> Upload Notes / Past Paper
    </button>

    <div id="uploadModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeUploadModal()">&times;</span>
            <h2 style="margin-bottom: 20px;"><i class="fas fa-upload"></i> Share Your Resources</h2>
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
                    <label>PDF File</label>
                    <input type="file" name="file" accept=".pdf,.doc,.docx" required>
                </div>
                <button type="submit" class="submit-btn"><i class="fas fa-cloud-upload-alt"></i> Publish Resource</button>
            </form>
        </div>
    </div>

    <script>
        // Matrix Rain Effect
        const canvas = document.getElementById('matrix-canvas');
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        const chars = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
        const fontSize = 14;
        let drops = [];

        function initMatrix() {
            const columns = canvas.width / fontSize;
            drops = [];
            for (let i = 0; i < columns; i++) {
                drops[i] = Math.random() * -100;
            }
        }

        function drawMatrix() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#0f0';
            ctx.font = fontSize + 'px monospace';

            for (let i = 0; i < drops.length; i++) {
                const text = chars.charAt(Math.floor(Math.random() * chars.length));
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                    drops[i] = 0;
                }
                drops[i]++;
            }
        }

        initMatrix();
        setInterval(drawMatrix, 40);
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

        window.onclick = function(event) {
            if (event.target == document.getElementById('uploadModal')) {
                closeUploadModal();
            }
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
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.innerHTML = '<i class="fas fa-check-circle"></i> Upload successful!';
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
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

@app.route('/delete/<int:id>')
def delete_file(id):
    note = Note.query.get_or_404(id)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], note.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/statistics')
def statistics():
    total_notes = Note.query.filter_by(category='note').count()
    total_papers = Note.query.filter_by(category='pastpaper').count()
    total_downloads = db.session.query(db.func.sum(Note.downloads)).scalar() or 0
    return jsonify({'notes': total_notes, 'pastpapers': total_papers, 'downloads': total_downloads})

# Serve standalone HTML file if requested
@app.route('/standalone')
def standalone():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)