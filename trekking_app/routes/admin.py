from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from models import get_db

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrap

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    db = get_db()
    treks = db.execute("SELECT COUNT(*) as c FROM treks").fetchone()['c']
    users = db.execute("SELECT COUNT(*) as c FROM users WHERE role='user'").fetchone()['c']
    staff = db.execute("SELECT COUNT(*) as c FROM users WHERE role='staff'").fetchone()['c']
    bookings = db.execute("SELECT COUNT(*) as c FROM bookings").fetchone()['c']
    db.close()
    return render_template('admin/dashboard.html', treks=treks, users=users, staff=staff, bookings=bookings)

@admin_bp.route('/treks')
@admin_required
def treks():
    db = get_db()
    q = request.args.get('q', '')
    if q:
        rows = db.execute("SELECT * FROM treks WHERE name LIKE ? OR id=?", (f'%{q}%', q)).fetchall()
    else:
        rows = db.execute("SELECT * FROM treks").fetchall()
    staff_list = db.execute("SELECT id, name FROM users WHERE role='staff' AND status='active'").fetchall()
    db.close()
    return render_template('admin/treks.html', treks=rows, staff_list=staff_list, q=q)

@admin_bp.route('/treks/add', methods=['POST'])
@admin_required
def add_trek():
    db = get_db()
    db.execute("""INSERT INTO treks (name, location, difficulty, duration, slots, staff_id, status, start_date, end_date)
                 VALUES (?,?,?,?,?,?,?,?,?)""",
               (request.form['name'], request.form['location'], request.form['difficulty'],
                request.form['duration'], request.form['slots'], request.form.get('staff_id') or None,
                request.form.get('status', 'Pending'), request.form.get('start_date'), request.form.get('end_date')))
    db.commit()
    db.close()
    flash('Trek added.')
    return redirect(url_for('admin.treks'))

@admin_bp.route('/treks/<int:tid>/edit', methods=['POST'])
@admin_required
def edit_trek(tid):
    db = get_db()
    db.execute("""UPDATE treks SET name=?, location=?, difficulty=?, duration=?, slots=?, start_date=?, end_date=?
                 WHERE id=?""",
               (request.form['name'], request.form['location'], request.form['difficulty'],
                request.form['duration'], request.form['slots'], request.form.get('start_date'),
                request.form.get('end_date'), tid))
    db.commit()
    db.close()
    flash('Trek updated.')
    return redirect(url_for('admin.treks'))

@admin_bp.route('/treks/<int:tid>/delete', methods=['POST'])
@admin_required
def delete_trek(tid):
    db = get_db()
    db.execute("DELETE FROM treks WHERE id=?", (tid,))
    db.execute("DELETE FROM bookings WHERE trek_id=?", (tid,))
    db.commit()
    db.close()
    flash('Trek removed.')
    return redirect(url_for('admin.treks'))

@admin_bp.route('/treks/<int:tid>/assign', methods=['POST'])
@admin_required
def assign_staff(tid):
    db = get_db()
    db.execute("UPDATE treks SET staff_id=? WHERE id=?", (request.form.get('staff_id') or None, tid))
    db.commit()
    db.close()
    flash('Staff assigned.')
    return redirect(url_for('admin.treks'))

@admin_bp.route('/staff')
@admin_required
def staff():
    db = get_db()
    q = request.args.get('q', '')
    if q:
        rows = db.execute("SELECT * FROM users WHERE role='staff' AND (name LIKE ? OR id=?)", (f'%{q}%', q)).fetchall()
    else:
        rows = db.execute("SELECT * FROM users WHERE role='staff'").fetchall()
    db.close()
    return render_template('admin/staff.html', staff=rows, q=q)

@admin_bp.route('/staff/<int:sid>/approve', methods=['POST'])
@admin_required
def approve_staff(sid):
    db = get_db()
    db.execute("UPDATE users SET status='active' WHERE id=?", (sid,))
    db.commit()
    db.close()
    flash('Staff approved.')
    return redirect(url_for('admin.staff'))

@admin_bp.route('/staff/<int:sid>/blacklist', methods=['POST'])
@admin_required
def blacklist_staff(sid):
    db = get_db()
    db.execute("UPDATE users SET status='blacklisted' WHERE id=?", (sid,))
    db.commit()
    db.close()
    flash('Staff blacklisted.')
    return redirect(url_for('admin.staff'))

@admin_bp.route('/users')
@admin_required
def users():
    db = get_db()
    q = request.args.get('q', '')
    if q:
        rows = db.execute("SELECT * FROM users WHERE role='user' AND (name LIKE ? OR id=?)", (f'%{q}%', q)).fetchall()
    else:
        rows = db.execute("SELECT * FROM users WHERE role='user'").fetchall()
    db.close()
    return render_template('admin/users.html', users=rows, q=q)

@admin_bp.route('/users/<int:uid>/blacklist', methods=['POST'])
@admin_required
def blacklist_user(uid):
    db = get_db()
    db.execute("UPDATE users SET status='blacklisted' WHERE id=?", (uid,))
    db.commit()
    db.close()
    flash('User blacklisted.')
    return redirect(url_for('admin.users'))

@admin_bp.route('/bookings')
@admin_required
def bookings():
    db = get_db()
    rows = db.execute("""SELECT b.*, u.name as user_name, t.name as trek_name
                         FROM bookings b
                         JOIN users u ON b.user_id=u.id
                         JOIN treks t ON b.trek_id=t.id
                         ORDER BY b.booking_date DESC""").fetchall()
    db.close()
    return render_template('admin/bookings.html', bookings=rows)
