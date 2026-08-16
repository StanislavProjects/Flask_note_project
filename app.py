from flask import Flask, render_template, request, redirect, url_for
from models import db, Note

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

CATEGORIES = ['Общее', 'Учёба', 'Идеи', 'Работа', 'Личное']

@app.route('/')
def index():
    selectet_category = request.args.get('category')
    if selectet_category and selectet_category != 'Все':
        notes = Note.query.filter_by(category = selectet_category).order_by(Note.created_at.desc()).all()
    else:
        notes = Note.query.order_by(Note.created_at.desc()).all()

    return render_template(
        'index.html', 
        notes = notes,
        categories = CATEGORIES,
        selectet_category = selectet_category or 'Все'
    )

@app.route('/note/<int:note_id>')
def view_note(note_id):
    note = Note.query.get_or_404(note_id)

    return render_template(
        'note.html',
        note = note
    )

@app.route('/add', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'Общее')

        if title and content:
            new_note = Note(
                title = title,
                content = content,
                category = category
            )
            db.session.add(new_note)
            db.session.commit()

            return redirect(url_for('index'))

    return render_template(
        'add_note.html',
        categories = CATEGORIES
    )

@app.route('/delete/<int:delete_id>', methods=['POST'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)

    db.session.delete(note)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)

    if request.method == 'POST':
        note.title = request.form['title']
        note.content = request.form['content']
        db.session.commit()
        return redirect(url_for('index'))

    return render_template(
        'edit_note.html',
        note=note
        )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)