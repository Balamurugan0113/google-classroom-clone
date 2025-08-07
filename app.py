from flask import Flask, render_template, redirect, url_for, request, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os, uuid

from config import Config
from models import db, User, Classroom, Enrollment, Assignment

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        role = request.form['role']
        user = User(username=username, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'teacher':
        classes = Classroom.query.filter_by(teacher_id=current_user.id).all()
        return render_template('dashboard_teacher.html', classes=classes)
    else:
        enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
        student_classes = [Classroom.query.get(e.class_id) for e in enrollments]
        assignments = []
        for c in student_classes:
            assignments.extend(Assignment.query.filter_by(classroom_id=c.id).all())
        return render_template('dashboard_student.html', classes=student_classes, assignments=assignments)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/create_class', methods=['POST'])
@login_required
def create_class():
    name = request.form['classname']
    join_code = str(uuid.uuid4())[:8]
    new_class = Classroom(name=name, join_code=join_code, teacher_id=current_user.id)
    db.session.add(new_class)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/join_class', methods=['POST'])
@login_required
def join_class():
    code = request.form['code']
    classroom = Classroom.query.filter_by(join_code=code).first()
    if classroom:
        already = Enrollment.query.filter_by(student_id=current_user.id, class_id=classroom.id).first()
        if not already:
            enrollment = Enrollment(student_id=current_user.id, class_id=classroom.id)
            db.session.add(enrollment)
            db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/upload/<int:class_id>', methods=['POST'])
@login_required
def upload(class_id):
    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    assignment = Assignment(filename=filename, classroom_id=class_id)
    db.session.add(assignment)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
