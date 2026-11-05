"""DHorizons educational Flask prototype (public demo edition)."""
import os
import re
import secrets
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
# Configure a fresh secret for each local demo. Set FLASK_SECRET_KEY to preserve sessions.
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or secrets.token_hex(32)
app.config.update(
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', f'sqlite:///{BASE_DIR / "database.db"}'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    UPLOAD_FOLDER=str(BASE_DIR / 'static' / 'uploads'),
    MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(100), nullable=False)
    contenuto = db.Column(db.Text, nullable=False)
    immagine = db.Column(db.String(200))

class Eventi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(100), nullable=False)
    contenuto = db.Column(db.Text, nullable=False)
    immagine = db.Column(db.String(200))
    data = db.Column(db.Date, nullable=False)

class Lezioni(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(300), nullable=False)

@app.context_processor
def csrf_context():
    def csrf_token():
        if '_csrf_token' not in session:
            session['_csrf_token'] = secrets.token_urlsafe(32)
        return session['_csrf_token']
    return {'csrf_token': csrf_token}

@app.before_request
def protect_post_requests():
    if request.method == 'POST':
        expected = session.get('_csrf_token', '')
        received = request.form.get('csrf_token', '')
        if not expected or not secrets.compare_digest(expected, received):
            abort(400, description='Invalid CSRF token')

def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapped

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
def save_image(field):
    f = request.files.get(field)
    if not f or not f.filename:
        return None
    original = secure_filename(f.filename)
    if '.' not in original or original.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
        abort(400, description='Only image files are allowed')
    ext = original.rsplit('.', 1)[1].lower()
    # Random file name avoids overwriting assets with a chosen filename.
    name = f'{secrets.token_hex(16)}.{ext}'
    f.save(str(Path(app.config['UPLOAD_FOLDER']) / name))
    return name

@app.route('/')
def home():
    # Preserve the original latest-content carousel, but avoid comparing IDs across different tables.
    post = Post.query.order_by(Post.id.desc()).limit(3).all()
    eventi = Eventi.query.order_by(Eventi.id.desc()).limit(3).all()
    lezioni = Lezioni.query.order_by(Lezioni.id.desc()).limit(3).all()
    ultimi_post = post + eventi + lezioni
    ultimi_post.sort(key=lambda x: x.id, reverse=True)
    return render_template('index.html', ultimi_post=ultimi_post)

@app.route('/post')
def post():
    return render_template('post.html', posts=Post.query.order_by(Post.id.desc()).all())

@app.route('/eventi')
def eventi():
    return render_template('eventi.html', eventi=Eventi.query.order_by(Eventi.data.desc()).all())

@app.route('/lezioni')
def lezioni():
    return render_template('lezioni.html', lezioni=Lezioni.query.all())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = os.environ.get('DHORIZONS_ADMIN_USERNAME', 'admin')
        password_hash = os.environ.get('DHORIZONS_ADMIN_PASSWORD_HASH', '')
        if (password_hash and secrets.compare_digest(request.form.get('username', ''), username)
                and check_password_hash(password_hash, request.form.get('password', ''))):
            session.clear()
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        flash('Credenziali errate o account demo non configurato')
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@admin_required
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin')
@admin_required
def admin():
    return render_template('admin.html', posts=Post.query.all(), eventi=Eventi.query.all(), lezioni=Lezioni.query.all())

@app.route('/admin/post', methods=['POST'])
@admin_required
def aggiungi_post():
    nuovo = Post(titolo=request.form['titolo'], contenuto=request.form['contenuto'], immagine=save_image('immagine'))
    db.session.add(nuovo)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/event', methods=['POST'])
@admin_required
def aggiungi_evento():
    date = datetime.strptime(request.form['data'], '%Y-%m-%d').date()
    nuovo = Eventi(titolo=request.form['titolo'], contenuto=request.form['contenuto'], data=date, immagine=save_image('immagine'))
    db.session.add(nuovo)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/lesson', methods=['POST'])
@admin_required
def aggiungi_lezione():
    db.session.add(Lezioni(titolo=request.form['titolo'], link=request.form['link']))
    db.session.commit()
    return redirect(url_for('admin'))

@app.template_filter('youtube_id')
def youtube_id(link):
    match = re.search(r'(?:v=|be/)([A-Za-z0-9_-]{11})', link or '')
    return match.group(1) if match else ''

@app.route('/admin/delete/post/<int:id>', methods=['POST'])
@admin_required
def elimina_post(id):
    item = db.session.get(Post, id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/delete/event/<int:id>', methods=['POST'])
@admin_required
def elimina_evento(id):
    item = db.session.get(Eventi, id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/delete/lesson/<int:id>', methods=['POST'])
@admin_required
def elimina_lezione(id):
    item = db.session.get(Lezioni, id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if not query:
        return redirect(request.referrer or url_for('home'))
    return render_template('search_results.html', query=query,
        post_risultati=Post.query.filter(Post.titolo.ilike(f'%{query}%') | Post.contenuto.ilike(f'%{query}%')).all(),
        eventi_risultati=Eventi.query.filter(Eventi.titolo.ilike(f'%{query}%') | Eventi.contenuto.ilike(f'%{query}%')).all(),
        lezioni_risultati=Lezioni.query.filter(Lezioni.titolo.ilike(f'%{query}%')).all())

if __name__ == '__main__':
    app.run(debug=False)
