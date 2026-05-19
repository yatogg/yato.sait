from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yakutsk_cold_dev_secret_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─── Models ──────────────────────────────────────────────────────────────────

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(500))
    tech_stack = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# ─── Helpers ─────────────────────────────────────────────────────────────────

def is_logged_in():
    return session.get('admin_logged_in', False)

def validate_email(email):
    return re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email) is not None

# ─── Public routes ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/portfolio')
def portfolio():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('portfolio.html', projects=projects)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    errors = {}
    form_data = {}

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        form_data = {'name': name, 'email': email, 'message': message}

        # Server-side validation
        if not name or len(name) < 2:
            errors['name'] = 'Имя должно содержать минимум 2 символа.'
        if not email or not validate_email(email):
            errors['email'] = 'Введите корректный email-адрес.'
        if not message or len(message) < 10:
            errors['message'] = 'Сообщение должно содержать минимум 10 символов.'

        if not errors:
            msg = Message(name=name, email=email, message=message)
            db.session.add(msg)
            db.session.commit()
            flash('Сообщение отправлено! Отвечу в ближайшее время.', 'success')
            return redirect(url_for('contact'))

    return render_template('contact.html', errors=errors, form_data=form_data)

# ─── Auth routes ──────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('admin_dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_logged_in'] = True
            session['admin_name'] = admin.username
            return redirect(url_for('admin_dashboard'))
        error = 'Неверный логин или пароль.'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ─── Admin routes ─────────────────────────────────────────────────────────────

@app.route('/admin')
def admin_dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))
    projects_count = Project.query.count()
    messages_count = Message.query.count()
    unread_count = Message.query.filter_by(is_read=False).count()
    recent_messages = Message.query.order_by(Message.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                           projects_count=projects_count,
                           messages_count=messages_count,
                           unread_count=unread_count,
                           recent_messages=recent_messages)

@app.route('/admin/projects')
def admin_projects():
    if not is_logged_in():
        return redirect(url_for('login'))
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('admin/projects.html', projects=projects)

@app.route('/admin/projects/add', methods=['GET', 'POST'])
def admin_add_project():
    if not is_logged_in():
        return redirect(url_for('login'))
    errors = {}
    form_data = {}

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        url = request.form.get('url', '').strip()
        tech_stack = request.form.get('tech_stack', '').strip()
        form_data = {'title': title, 'description': description, 'url': url, 'tech_stack': tech_stack}

        if not title or len(title) < 3:
            errors['title'] = 'Название должно содержать минимум 3 символа.'
        if not description or len(description) < 10:
            errors['description'] = 'Описание должно содержать минимум 10 символов.'

        if not errors:
            project = Project(title=title, description=description, url=url, tech_stack=tech_stack)
            db.session.add(project)
            db.session.commit()
            flash('Проект успешно добавлен!', 'success')
            return redirect(url_for('admin_projects'))

    return render_template('admin/project_form.html', errors=errors, form_data=form_data, edit=False)

@app.route('/admin/projects/edit/<int:project_id>', methods=['GET', 'POST'])
def admin_edit_project(project_id):
    if not is_logged_in():
        return redirect(url_for('login'))
    project = Project.query.get_or_404(project_id)
    errors = {}

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        url = request.form.get('url', '').strip()
        tech_stack = request.form.get('tech_stack', '').strip()

        if not title or len(title) < 3:
            errors['title'] = 'Название должно содержать минимум 3 символа.'
        if not description or len(description) < 10:
            errors['description'] = 'Описание должно содержать минимум 10 символов.'

        if not errors:
            project.title = title
            project.description = description
            project.url = url
            project.tech_stack = tech_stack
            db.session.commit()
            flash('Проект обновлён!', 'success')
            return redirect(url_for('admin_projects'))

    form_data = {'title': project.title, 'description': project.description,
                 'url': project.url, 'tech_stack': project.tech_stack}
    return render_template('admin/project_form.html', errors=errors, form_data=form_data, edit=True, project=project)

@app.route('/admin/projects/delete/<int:project_id>', methods=['POST'])
def admin_delete_project(project_id):
    if not is_logged_in():
        return redirect(url_for('login'))
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Проект удалён.', 'info')
    return redirect(url_for('admin_projects'))

@app.route('/admin/messages')
def admin_messages():
    if not is_logged_in():
        return redirect(url_for('login'))
    messages = Message.query.order_by(Message.created_at.desc()).all()
    # Mark all as read
    Message.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/messages/delete/<int:msg_id>', methods=['POST'])
def admin_delete_message(msg_id):
    if not is_logged_in():
        return redirect(url_for('login'))
    msg = Message.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash('Сообщение удалено.', 'info')
    return redirect(url_for('admin_messages'))

# ─── Init DB ──────────────────────────────────────────────────────────────────

def init_db():
    with app.app_context():
        db.create_all()
        # Create admin if not exists
        if not Admin.query.filter_by(username='valera').first():
            admin = Admin(username='valera', password_hash=generate_password_hash('admin'))
            db.session.add(admin)

        # Seed projects if empty
        if Project.query.count() == 0:
            sample_projects = [
                Project(
                    title='Интернет-магазин на Django',
                    description='Полноценный e-commerce проект с корзиной, оплатой и личным кабинетом. Реализованы JWT-авторизация, REST API, интеграция с платёжной системой.',
                    url='https://github.com',
                    tech_stack='Python, Django, PostgreSQL, Redis, Celery'
                ),
                Project(
                    title='Telegram-бот для автоматизации',
                    description='Бот для автоматической обработки заказов, уведомлений и аналитики. Интегрирован с CRM и базой данных.',
                    url='https://t.me',
                    tech_stack='Python, aiogram, SQLite, Docker'
                ),
                Project(
                    title='Парсер данных и дашборд',
                    description='Система сбора данных с нескольких источников, обработки и визуализации в реальном времени. Расписание через cron.',
                    url='https://github.com',
                    tech_stack='Python, Scrapy, Pandas, Plotly, Flask'
                ),
                Project(
                    title='REST API для мобильного приложения',
                    description='Бэкенд для iOS/Android приложения: авторизация, push-уведомления, файловое хранилище, документация Swagger.',
                    url='https://github.com',
                    tech_stack='FastAPI, PostgreSQL, S3, Docker, Nginx'
                ),
            ]
            db.session.bulk_save_objects(sample_projects)
        db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
