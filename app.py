from flask import Flask, render_template, request, redirect, url_for, flash, abort
from models import db, Note, User
import os
from werkzeug.utils import secure_filename
import uuid
from flask_login import (
        LoginManager, 
        login_user,
        logout_user,
        login_required,
        current_user
    )

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SECRET_KEY'] = 'q1w2e3r4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Извините, данная страница доступна только авторизованным пользователям'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'upload')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXSTENSTIONS = {'png', 'jpg', 'webp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CATEGORIES = ['Общее', 'Учёба', 'Идеи', 'Работа', 'Личное']

def allowed_files(file_name):
    return '.' in file_name and file_name.rsplit('.', 1)[1].lower() in ALLOWED_EXSTENSTIONS

def save_allowed_image(file):
    if not file or file.filename == '':
        print(1)
        return None
    if not allowed_files(file.filename):
        print(2)
        return None

    original_name = secure_filename(file.filename)
    extension = original_name.rsplit('.', 1)[1].lower()
    unik_name = f'{uuid.uuid4().hex}.{extension}'
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unik_name)
    file.save(file_path)

    return unik_name

def delete_allowed_image(file_name):
    if not file_name:
        return None

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

    if os.path.exists(file_path):
        os.remove(file_path)

@app.route('/')
@login_required
def index():
    selectet_category = request.args.get('category')
    query = Note.query.filter_by(id=current_user.id)
    if selectet_category and selectet_category != 'Все':
        query = Note.query.filter_by(category = selectet_category)
    
    notes = query.order_by(Note.created_at.desc()).all()

    return render_template(
        'index.html', 
        notes = notes,
        categories = CATEGORIES,
        selectet_category = selectet_category or 'Все'
    )

@app.route('/note/<int:note_id>')
@login_required
def view_note(note_id):
    note = Note.query.get_or_404(note_id)

    if note.user_id != current_user.id:
        abort(403)

    return render_template(
        'note.html',
        note = note
    )

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_note():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'Общее')
        image = request.files.get('image')
        

        if title and content:
            new_note = Note(
                title = title,
                content = content,
                category = category,
                user_id = current_user.id
            )
            new_note.image = save_allowed_image(image)
            print(new_note.image)
            db.session.add(new_note)
            db.session.commit()

            return redirect(url_for('index'))

    return render_template(
        'add_note.html',
        categories = CATEGORIES
    )

@app.route('/delete/<int:delete_id>', methods=['POST'])
@login_required
def delete_note(note_id):    ## Нужно сделать возможность удаления фото
    if note.user_id != current_user.id:
        abort(403)

    note = Note.query.get_or_404(note_id)

    db.session.delete(note)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):      ## Нужно сделать возможность изменения фото
    if note.user_id != current_user.id:
        abort(403)

    note = Note.query.get_or_404(note_id)

    if request.method == 'POST':
        note.title = request.form['title']
        note.content = request.form['content']
        note.category = request.form['category']
        db.session.commit()
        return redirect(url_for('index'))

    return render_template(
        'edit_note.html',
        note=note
        )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        password_confirm = request.form.get('password_confirm').strip()
        if not username or not password:
            flash('Введите имя пользователя или пароль.', 'error')
            print(1)            
            return render_template('register.html')
        if len(password) < 4:
            flash('Длина вашего пароля не должна быть менее 4-ех символов.', 'error')
            print(2)
            return render_template('register.html')
        if password != password_confirm:
            flash('Пароли не совпадают.', 'error')
            print(3)
            return render_template('register.html')
        ex_user = User.query.filter_by(username = username).first()
        if ex_user:
            flash('Такой username занят, попробуйте другой.', 'error')
            print(4)
            return render_template('register.html')
        if  not password.isascii():
            flash('Пароль должен содержать хотя бы одну английскую букву.', 'error')
            print(5)
            return render_template('register.html')
        if not any(char.isupper() for char in password):
            flash('Пароль должен содержать хотя бы одну заглавную букву.', 'error')
            print(6)
            return render_template('register.html')

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация прошла успешно.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Введены неверные учетные данные', 'error')
            return render_template('login.html')
        
        login_user(user)
        flash(f'Добро пожаловать, {user.username}.', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)