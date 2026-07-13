from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        db.close()
        if user and check_password_hash(user['password'], password):
            if user['status'] == 'blacklisted':
                flash('Your account has been blacklisted.')
                return redirect(url_for('auth.login'))
            if user['role'] == 'staff' and user['status'] == 'pending':
                flash('Your account is pending admin approval.')
                return redirect(url_for('auth.login'))
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user['role'] == 'staff':
                return redirect(url_for('staff.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        flash('Invalid email or password.')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        if role not in ('staff', 'user'):
            flash('Invalid role.')
            return redirect(url_for('auth.register'))
        status = 'pending' if role == 'staff' else 'active'
        db = get_db()
        try:
            db.execute("INSERT INTO users (name, email, password, role, status) VALUES (?,?,?,?,?)",
                       (name, email, generate_password_hash(password), role, status))
            db.commit()
            flash('Registered successfully. Please log in.' if role == 'user' else 'Registered. Await admin approval.')
            return redirect(url_for('auth.login'))
        except Exception:
            flash('Email already exists.')
        finally:
            db.close()
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
